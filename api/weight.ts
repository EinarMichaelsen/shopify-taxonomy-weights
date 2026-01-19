import type { VercelRequest, VercelResponse } from '@vercel/node';
import data from './data.json';

const categories = data.categories as Record<string, Category>;

interface Category {
  name: string;
  vertical: string;
  weight: {
    estimate_g: number;
    min_g: number;
    max_g: number;
    confidence: 'low' | 'medium' | 'high';
  };
  lca?: {
    carbon_kg_co2e_per_kg: number;
    carbon_kg_co2e_per_unit: number;
    scope: string;
    data_quality: string;
  };
  lca_data_missing?: boolean;
  materials?: {
    primary_material: string;
    breakdown: Array<{ material: string; percentage: number }>;
  };
  sources?: string[];
}

interface WeightResponse {
  id: string;
  name: string;
  vertical: string;
  weight: Category['weight'];
  lca?: Category['lca'];
  lca_data_missing?: boolean;
}

function getById(id: string): WeightResponse | null {
  const category = categories[id];
  if (category) {
    return {
      id,
      name: category.name,
      vertical: category.vertical,
      weight: category.weight,
      ...(category.lca && { lca: category.lca }),
      ...(category.lca_data_missing && { lca_data_missing: true }),
    };
  }

  // Try parent category (remove last segment)
  if (id.includes('-')) {
    const parts = id.split('-');
    if (parts.length > 2) {
      const parentId = parts.slice(0, -1).join('-');
      return getById(parentId);
    }
  }

  return null;
}

function search(query: string, limit = 10): WeightResponse[] {
  const queryLower = query.toLowerCase().trim();
  const results: Array<{ data: WeightResponse; score: number }> = [];

  for (const [id, category] of Object.entries(categories)) {
    const name = category.name.toLowerCase();

    // Exact name match
    if (name === queryLower) {
      results.push({
        data: {
          id,
          name: category.name,
          vertical: category.vertical,
          weight: category.weight,
          ...(category.lca && { lca: category.lca }),
          ...(category.lca_data_missing && { lca_data_missing: true }),
        },
        score: 0,
      });
    }
    // Name contains query
    else if (name.includes(queryLower)) {
      results.push({
        data: {
          id,
          name: category.name,
          vertical: category.vertical,
          weight: category.weight,
          ...(category.lca && { lca: category.lca }),
          ...(category.lca_data_missing && { lca_data_missing: true }),
        },
        score: 1,
      });
    }
    // ID contains query
    else if (id.toLowerCase().includes(queryLower)) {
      results.push({
        data: {
          id,
          name: category.name,
          vertical: category.vertical,
          weight: category.weight,
          ...(category.lca && { lca: category.lca }),
          ...(category.lca_data_missing && { lca_data_missing: true }),
        },
        score: 2,
      });
    }
  }

  // Sort by score (lower is better), then by ID length (shorter is more general)
  results.sort((a, b) => {
    if (a.score !== b.score) return a.score - b.score;
    return a.data.id.length - b.data.id.length;
  });

  return results.slice(0, limit).map(r => r.data);
}

export default function handler(req: VercelRequest, res: VercelResponse) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { id, search: searchQuery, limit } = req.query;

  // Lookup by ID
  if (id && typeof id === 'string') {
    const result = getById(id);
    if (result) {
      return res.status(200).json(result);
    }
    return res.status(404).json({ error: 'Category not found', id });
  }

  // Search
  if (searchQuery && typeof searchQuery === 'string') {
    const limitNum = typeof limit === 'string' ? parseInt(limit, 10) : 10;
    const results = search(searchQuery, Math.min(limitNum, 100));
    return res.status(200).json({
      query: searchQuery,
      count: results.length,
      results,
    });
  }

  // No params - return usage info
  return res.status(200).json({
    usage: {
      lookup: 'GET /api/weight?id=aa-1-13-8',
      search: 'GET /api/weight?search=t-shirts&limit=10',
    },
    stats: {
      total_categories: Object.keys(categories).length,
      coverage: '100% weight estimates',
    },
  });
}
