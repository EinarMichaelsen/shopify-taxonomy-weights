# Shopify Taxonomy Weights & LCA Data

Community-maintained extension to [Shopify's Standard Product Taxonomy](https://github.com/Shopify/product-taxonomy) adding estimated product weights and Life Cycle Assessment (LCA) carbon footprint data.

> **Note**: This is an independent community project, not affiliated with or endorsed by Shopify. We use Shopify's taxonomy IDs to enable easy integration with Shopify stores and any system using their product classification.

> **Disclaimer**: Weight estimates in this dataset are AI-generated approximations, not sourced from verified measurements. They are intended as rough defaults for shipping and carbon calculations when actual product weights are unavailable. LCA carbon data (66 categories) cites specific sources — all other weight data should be treated as unverified estimates. **Do not use for regulatory reporting or precise claims.** Contributions of real, measured weights are welcome.

**[Try the Demo](https://shopify-taxonomy-weights.vercel.app)** | **[API Docs](#rest-api)**

## Purpose

Enable climate impact calculations for e-commerce products without requiring detailed product specifications. When you know a product's category but not its exact weight or materials, this dataset provides reasonable estimates for:

- **Weight estimation** - Shipping calculations, packaging decisions
- **Carbon footprint** - kg CO2e per product for climate impact reporting
- **Material composition** - Default material breakdowns per category

## Data Structure

```
data/                                  # 26 YAML files (one per Shopify vertical)
├── animals-pet-supplies.yml           # ap-* (418)
├── apparel-accessories.yml            # aa-* (464)
├── arts-entertainment.yml             # ae-* (1,220)
├── baby-toddler.yml                   # bt-* (252)
├── business-industrial.yml            # bi-* (593)
├── cameras-optics.yml                 # co-* (212)
├── electronics.yml                    # el-* (1,175)
├── food-beverages-tobacco.yml         # fb-* (441)
├── furniture.yml                      # fr-* (355)
├── hardware.yml                       # ha-* (1,122)
├── health-beauty.yml                  # hb-* (898)
├── home-garden.yml                    # hg-* (2,301)
├── luggage-bags.yml                   # lb-* (36)
├── media.yml                          # me-* (33)
├── office-supplies.yml                # os-* (243)
├── sporting-goods.yml                 # sg-* (1,596)
├── toys-games.yml                     # tg-* (247)
├── vehicles-parts.yml                 # vp-* (605)
├── ...and 8 smaller verticals
dist/
├── shopify-taxonomy-weights.json      # Full JSON export
├── shopify-taxonomy-weights.min.json  # Minified JSON
└── categories.json                    # Categories only
schemas/
└── category-data.schema.json          # JSON Schema for validation
scripts/
├── query.py                           # Query tool for category lookup
├── export_json.py                     # Export YAML to JSON
└── audit_lca_data.py                  # Audit LCA data sources
api/
└── weight.ts                          # Vercel API endpoint
public/
└── index.html                         # Demo web app
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

**Weight estimates** are AI-generated approximations based on general product knowledge. They have not been individually verified against real-world measurements. Confidence levels (`low`, `medium`, `high`) reflect relative certainty, not measurement precision. Treat all weight data as rough estimates.

**LCA data** (66 categories) cites specific sources:
- [Higg Materials Sustainability Index](https://howtohigg.org/)
- [WRAP UK](https://wrap.org.uk/) textile research
- Manufacturer sustainability reports (Apple, Dell, HP, etc.)
- Academic LCA studies
- [Ecoinvent](https://ecoinvent.org/) database (where available)

## Coverage

**Total: 12,372 categories** (full Shopify taxonomy) | **100% have weight estimates** | **66 with sourced LCA data (0.5%)**

All 26 Shopify taxonomy verticals are covered. Weight estimates for ~818 categories were individually set; the remaining ~11,554 categories inherit estimates from their nearest parent category.

| Vertical | Categories | With LCA |
|----------|------------|----------|
| Home & Garden (hg) | 2,301 | 8 |
| Sporting Goods (sg) | 1,596 | 8 |
| Arts & Entertainment (ae) | 1,220 | 26 |
| Electronics (el) | 1,175 | 5 |
| Hardware (ha) | 1,122 | - |
| Health & Beauty (hb) | 898 | 6 |
| Vehicles & Parts (vp) | 605 | - |
| Business & Industrial (bi) | 593 | - |
| Apparel & Accessories (aa) | 464 | 6 |
| Food, Beverages & Tobacco (fb) | 441 | - |
| Animals & Pet Supplies (ap) | 418 | 2 |
| Furniture (fr) | 355 | 6 |
| Baby & Toddler (bt) | 252 | 3 |
| Toys & Games (tg) | 247 | 6 |
| Office Supplies (os) | 243 | - |
| Cameras & Optics (co) | 212 | - |
| Services (se) | 55 | - |
| Software (so) | 45 | - |
| Mature (ma) | 37 | - |
| Luggage & Bags (lb) | 36 | - |
| Media (me) | 33 | - |
| Religious & Ceremonial (rc) | 13 | - |
| Product Add-Ons (pa) | 8 | - |
| Bundles (bu) | 1 | - |
| Gift Cards (gc) | 1 | - |
| Uncategorized (na) | 1 | - |

Categories marked with `lca_data_missing: true` need LCA data contributions. See [docs/lca_data_needed.md](docs/lca_data_needed.md) for the full list.

## Contributing

Contributions welcome! We need help with:

1. **Verified weight data** - Replace AI-generated estimates with real measured weights from manufacturers or shipping data
2. **Adding LCA data** - Carbon footprint data with sources (12,306 categories need data!)
3. **Improving estimates** - Better weight ranges and confidence levels based on real products

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
