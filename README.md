# Shopify Taxonomy Weights & LCA Data

Community-maintained extension to [Shopify's Standard Product Taxonomy](https://github.com/Shopify/product-taxonomy) adding estimated product weights and Life Cycle Assessment (LCA) carbon footprint data.

> **Note**: This is an independent community project, not affiliated with or endorsed by Shopify. We use Shopify's taxonomy IDs to enable easy integration with Shopify stores and any system using their product classification.

**[Try the Demo](https://shopify-taxonomy-weights.vercel.app)** | **[API Docs](#rest-api)**

## Purpose

Enable climate impact calculations for e-commerce products without requiring detailed product specifications. When you know a product's category but not its exact weight or materials, this dataset provides reasonable estimates for:

- **Weight estimation** - Shipping calculations, packaging decisions
- **Carbon footprint** - kg CO2e per product for climate impact reporting
- **Material composition** - Default material breakdowns per category

## Data Structure

```
data/
├── apparel-accessories.yml   # aa-* categories (106)
├── electronics.yml           # el-* categories (11)
├── home-garden.yml           # hg-* categories (156)
├── furniture.yml             # fr-* categories (109)
├── sporting-goods.yml        # sg-* categories (149)
├── health-beauty.yml         # hb-* categories (61)
├── toys-games.yml            # tg-* categories (123)
├── baby-toddler.yml          # bt-* categories (120)
├── animals-pet-supplies.yml  # ap-* categories (65)
├── luggage-bags.yml          # lb-* categories (78)
├── arts-entertainment.yml    # ae-* categories (141)
dist/
├── shopify-taxonomy-weights.json     # Full JSON export
├── shopify-taxonomy-weights.min.json # Minified JSON
└── categories.json                   # Categories only
schemas/
└── category-data.schema.json # JSON Schema for validation
scripts/
├── query.py          # Query tool for category lookup
├── export_json.py    # Export YAML to JSON
└── audit_lca_data.py # Audit LCA data sources
api/
└── weight.ts         # Vercel API endpoint
public/
└── index.html        # Demo web app
```

### Category IDs

We use Shopify's taxonomy category IDs directly:
- `aa-1-13-8` = Apparel & Accessories > Clothing > Tops > T-Shirts
- `el-1-2` = Electronics > Computers & Tablets > Laptops
- `sg-4-17-2-17` = Sporting Goods > Outdoor Recreation > Winter Sports > Snowboards

Find category IDs at: https://shopify.github.io/product-taxonomy/

### Data Fields

```yaml
aa-1-13-8:
  name: "T-Shirts"
  weight:
    estimate_g: 180        # Best estimate in grams
    min_g: 120             # Minimum typical weight
    max_g: 280             # Maximum typical weight
    confidence: high       # low | medium | high
  lca:
    carbon_kg_co2e_per_kg: 8.0      # Embodied carbon per kg
    carbon_kg_co2e_per_unit: 1.44   # Per typical unit
    scope: cradle-to-gate          # LCA boundary
    data_quality: secondary        # primary | secondary | estimated
  materials:
    primary_material: cotton
    breakdown:
      - material: cotton
        percentage: 100
  sources:
    - "Carbon Trust Clothing Footprint Study"
```

## Usage

### Quick Query (CLI)

```bash
# Search by name
python scripts/query.py "t-shirts"

# Get by exact ID
python scripts/query.py aa-1-13-8

# Output as JSON
python scripts/query.py --json aa-1-13-8

# Verbose output with sources
python scripts/query.py "laptop" --verbose

# List all categories in a vertical
python scripts/query.py --vertical electronics
```

### REST API

Live API at `https://shopify-taxonomy-weights.vercel.app`

```bash
# Lookup by Shopify category ID
curl "https://shopify-taxonomy-weights.vercel.app/api/weight?id=aa-1-13-8"

# Search by name
curl "https://shopify-taxonomy-weights.vercel.app/api/weight?search=laptop&limit=5"
```

**Response:**
```json
{
  "id": "aa-1-13-8",
  "name": "T-Shirts",
  "vertical": "apparel-accessories",
  "weight": {
    "estimate_g": 180,
    "min_g": 120,
    "max_g": 280,
    "confidence": "high"
  }
}
```

### JSON Export

Use the pre-built JSON exports in `dist/`:

```javascript
// Full data with all metadata
const data = require('./dist/shopify-taxonomy-weights.json');

// Get a specific category
const tshirt = data.categories['aa-1-13-8'];
console.log(tshirt.weight.estimate_g); // 180
console.log(tshirt.lca.carbon_kg_co2e_per_unit); // 1.44
```

### Python Usage

```python
import yaml

# Load category data
with open('data/apparel-accessories.yml') as f:
    data = yaml.safe_load(f)

# Get footprint for a T-shirt
tshirt = data['categories']['aa-1-13-8']
weight_kg = tshirt['weight']['estimate_g'] / 1000
carbon_per_kg = tshirt['lca']['carbon_kg_co2e_per_kg']

footprint = weight_kg * carbon_per_kg
print(f"Estimated footprint: {footprint:.2f} kg CO2e")
# Output: Estimated footprint: 1.44 kg CO2e
```

### Find category by Shopify taxonomy ID

```python
def get_category_data(category_id, data_files):
    """Look up category data, falling back to parent categories."""
    for data in data_files:
        if category_id in data['categories']:
            return data['categories'][category_id]

    # Try parent category (remove last segment)
    if '-' in category_id:
        parent_id = '-'.join(category_id.split('-')[:-1])
        return get_category_data(parent_id, data_files)

    return None
```

## Data Sources

Weight estimates are derived from:
- Manufacturer specifications
- Shipping industry data
- Retail product databases

LCA data is sourced from:
- [Higg Materials Sustainability Index](https://howtohigg.org/)
- [WRAP UK](https://wrap.org.uk/) textile research
- Manufacturer sustainability reports (Apple, Dell, HP, etc.)
- Academic LCA studies
- [Ecoinvent](https://ecoinvent.org/) database (where available)

## Coverage

**Total: 1,119 categories** | **100% have weight estimates** | **79 with sourced LCA data (7.1%)**

| Vertical | Categories | With LCA | Notes |
|----------|------------|----------|-------|
| Home & Garden (hg) | 156 | 8 | Kitchen, bedding, decor, outdoor |
| Sporting Goods (sg) | 149 | 8 | Fitness, outdoor, team sports |
| Arts & Entertainment (ae) | 141 | 26 | Art supplies, instruments, books |
| Toys & Games (tg) | 123 | 6 | Building toys, games, outdoor play |
| Baby & Toddler (bt) | 120 | 3 | Strollers, gear, nursery |
| Furniture (fr) | 109 | 6 | Living, bedroom, office furniture |
| Apparel & Accessories (aa) | 106 | 6 | Clothing, shoes, jewelry |
| Luggage & Bags (lb) | 78 | 3 | Luggage, backpacks, bags |
| Animals & Pet Supplies (ap) | 65 | 2 | Pet food, supplies, accessories |
| Health & Beauty (hb) | 61 | 6 | Skincare, hair, personal care |
| Electronics (el) | 11 | 5 | Computers, phones, audio |
| Food & Beverages (fb) | - | - | Planned |
| Vehicles & Parts (vp) | - | - | Planned |
| Hardware (ha) | - | - | Planned |

Categories marked with `lca_data_missing: true` need LCA data contributions. See [docs/lca_data_needed.md](docs/lca_data_needed.md) for the full list.

## Contributing

Contributions welcome! We need help with:

1. **Adding LCA data** - Carbon footprint data with sources (1,040 categories need data!)
2. **Adding weight estimates** - Real product weights from manufacturers or measurements
3. **Expanding coverage** - New product verticals

### Priority: LCA Data Needed

We removed all unsourced LCA data to ensure data integrity. Categories needing LCA data are marked with `lca_data_missing: true`. See the full list at [docs/lca_data_needed.md](docs/lca_data_needed.md).

Good sources for LCA data:
- [Higg Materials Sustainability Index](https://howtohigg.org/)
- [Ecoinvent Database](https://ecoinvent.org/)
- Manufacturer sustainability reports
- Academic LCA studies (peer-reviewed)
- Industry association environmental reports

### How to contribute

1. Fork the repository
2. Find a category with `lca_data_missing: true`
3. Research and add LCA data with proper sources
4. Run `python scripts/audit_lca_data.py` to validate
5. Submit a pull request

### Data quality guidelines

- **Always cite sources** - No unsourced data accepted
- **Prefer primary data** - Manufacturer reports > industry averages > estimates
- **Note methodology** - How was the number derived?
- **Indicate confidence** - Be honest about data quality
- **Use SI units** - Grams for weight, kg CO2e for carbon
- **Include scope** - cradle-to-gate or cradle-to-grave

## Limitations

- **Estimates only** - Actual products vary significantly
- **Averages** - Data represents typical products, not specific items
- **Cradle-to-gate focus** - Use phase and end-of-life data is incomplete
- **Geographic variance** - Manufacturing location significantly affects footprint

This data is suitable for:
- Rough estimates and screening
- Consumer-facing approximations
- Research and comparison

Not suitable for:
- Regulatory reporting
- Carbon credits/offsets
- Precise product-level claims

## License

[MIT License](LICENSE) - Use freely, attribution appreciated.

## Related Projects

- [Shopify Product Taxonomy](https://github.com/Shopify/product-taxonomy) - The taxonomy we map to
- [Open Food Facts](https://world.openfoodfacts.org/) - Similar approach for food products
- [Higg Index](https://howtohigg.org/) - Industry standard for apparel sustainability
