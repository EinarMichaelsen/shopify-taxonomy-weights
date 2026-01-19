#!/usr/bin/env python3
"""
Query tool for Shopify taxonomy weights.
Lookup categories by ID, name, or search terms.

Usage:
    python query.py "t-shirts"
    python query.py aa-1-13-8
    python query.py --id aa-1-13-8
    python query.py --name "T-Shirts"
    python query.py --search "laptop"
    python query.py --vertical apparel-accessories
    python query.py --json "t-shirts"
"""

import yaml
import json
import argparse
import sys
from pathlib import Path
from typing import Optional, Dict, List


def load_all_categories(data_dir: Path) -> Dict:
    """Load all categories from YAML files."""
    categories = {}

    for yaml_file in sorted(data_dir.glob('*.yml')):
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        if not data or 'categories' not in data:
            continue

        vertical = yaml_file.stem
        for cat_id, cat_data in data['categories'].items():
            if isinstance(cat_data, dict):
                cat_data['_vertical'] = vertical
                cat_data['_id'] = cat_id
                categories[cat_id] = cat_data

    return categories


def search_categories(categories: Dict, query: str) -> List[Dict]:
    """Search categories by name or ID (fuzzy match)."""
    query_lower = query.lower().strip()
    results = []

    for cat_id, cat_data in categories.items():
        # Exact ID match
        if cat_id.lower() == query_lower:
            return [cat_data]

        # Name contains query
        name = cat_data.get('name', '').lower()
        if query_lower in name or query_lower in cat_id.lower():
            results.append(cat_data)

    # Sort by relevance (exact name match first, then by ID length)
    results.sort(key=lambda x: (
        x.get('name', '').lower() != query_lower,
        len(x.get('_id', ''))
    ))

    return results


def get_by_id(categories: Dict, cat_id: str) -> Optional[Dict]:
    """Get category by exact ID."""
    return categories.get(cat_id)


def get_by_vertical(categories: Dict, vertical: str) -> List[Dict]:
    """Get all categories in a vertical."""
    return [c for c in categories.values() if c.get('_vertical') == vertical]


def format_category(cat: Dict, verbose: bool = False) -> str:
    """Format category for display."""
    lines = []
    cat_id = cat.get('_id', 'unknown')
    name = cat.get('name', 'Unknown')
    vertical = cat.get('_vertical', 'unknown')

    lines.append(f"ID: {cat_id}")
    lines.append(f"Name: {name}")
    lines.append(f"Vertical: {vertical}")

    # Weight info
    weight = cat.get('weight', {})
    if weight:
        estimate = weight.get('estimate_g', 'N/A')
        min_g = weight.get('min_g', 'N/A')
        max_g = weight.get('max_g', 'N/A')
        confidence = weight.get('confidence', 'N/A')
        lines.append(f"Weight: {estimate}g (range: {min_g}-{max_g}g, confidence: {confidence})")

    # LCA info
    if cat.get('lca_data_missing'):
        lines.append("LCA: Data missing - contributions welcome!")
    elif 'lca' in cat:
        lca = cat['lca']
        co2_kg = lca.get('carbon_kg_co2e_per_kg', 'N/A')
        co2_unit = lca.get('carbon_kg_co2e_per_unit', 'N/A')
        scope = lca.get('scope', 'N/A')
        lines.append(f"LCA: {co2_kg} kg CO2e/kg, {co2_unit} kg CO2e/unit ({scope})")

        if verbose and 'sources' in cat:
            lines.append(f"Sources: {', '.join(cat['sources'])}")

    # Materials
    if verbose and 'materials' in cat:
        mat = cat['materials']
        primary = mat.get('primary_material', 'N/A')
        lines.append(f"Primary Material: {primary}")
        if 'breakdown' in mat:
            lines.append("Material Breakdown:")
            for item in mat['breakdown']:
                lines.append(f"  - {item.get('material', 'unknown')}: {item.get('percentage', 0)}%")

    # Notes
    if verbose and 'notes' in cat:
        lines.append(f"Notes: {cat['notes']}")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Query Shopify taxonomy weight data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    python query.py "t-shirts"           # Search for t-shirts
    python query.py aa-1-13-8            # Get by ID
    python query.py --search "laptop"    # Search all fields
    python query.py --vertical apparel-accessories  # List vertical
    python query.py --json aa-1-13-8     # Output as JSON
        '''
    )
    parser.add_argument('query', nargs='?', help='Search query or category ID')
    parser.add_argument('--id', help='Get category by exact ID')
    parser.add_argument('--name', help='Search by name')
    parser.add_argument('--search', help='Search all categories')
    parser.add_argument('--vertical', help='List all categories in vertical')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    parser.add_argument('--limit', '-n', type=int, default=10, help='Limit results (default: 10)')

    args = parser.parse_args()

    # Find data directory
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data'

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}", file=sys.stderr)
        sys.exit(1)

    # Load categories
    categories = load_all_categories(data_dir)

    # Handle queries
    results = []

    if args.id:
        cat = get_by_id(categories, args.id)
        if cat:
            results = [cat]
    elif args.vertical:
        results = get_by_vertical(categories, args.vertical)
    elif args.search or args.name or args.query:
        query = args.search or args.name or args.query
        results = search_categories(categories, query)

    if not results:
        print("No matching categories found.")
        sys.exit(1)

    # Limit results
    if args.limit and len(results) > args.limit:
        print(f"Showing {args.limit} of {len(results)} results:\n")
        results = results[:args.limit]

    # Output
    if args.json:
        # Clean internal fields for JSON output
        clean_results = []
        for r in results:
            clean = {k: v for k, v in r.items() if not k.startswith('_')}
            clean['id'] = r.get('_id')
            clean['vertical'] = r.get('_vertical')
            clean_results.append(clean)

        if len(clean_results) == 1:
            print(json.dumps(clean_results[0], indent=2))
        else:
            print(json.dumps(clean_results, indent=2))
    else:
        for i, cat in enumerate(results):
            if i > 0:
                print("\n" + "-" * 40 + "\n")
            print(format_category(cat, verbose=args.verbose))


if __name__ == '__main__':
    main()
