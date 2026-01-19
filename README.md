# Shopify Taxonomy Weights & LCA Data

Community-maintained extension to [Shopify's Standard Product Taxonomy](https://github.com/Shopify/product-taxonomy) adding estimated product weights and Life Cycle Assessment (LCA) carbon footprint data.

> **Note**: This is an independent community project, not affiliated with or endorsed by Shopify. We use Shopify's taxonomy IDs to enable easy integration with Shopify stores and any system using their product classification.

## Purpose

Enable climate impact calculations for e-commerce products without requiring detailed product specifications. When you know a product's category but not its exact weight or materials, this dataset provides reasonable estimates for:

- **Weight estimation** - Shipping calculations, packaging decisions
- **Carbon footprint** - kg CO2e per product for climate impact reporting
- **Material composition** - Default material breakdowns per category

## Data Structure

```
data/
├── apparel-accessories.yml   # aa-* categories
├── electronics.yml           # el-* categories
├── home-garden.yml           # hg-* categories (coming soon)
├── ...
schemas/
└── category-data.schema.json # JSON Schema for validation
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

### Calculate product carbon footprint

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

| Vertical | Status | Categories |
|----------|--------|------------|
| Apparel & Accessories (aa) | Partial | ~25 categories |
| Electronics (el) | Partial | ~15 categories |
| Home & Garden (hg) | Partial | ~40 categories |
| Furniture (fr) | Partial | ~35 categories |
| Sporting Goods (sg) | Partial | ~50 categories |
| Food & Beverages (fb) | Planned | - |
| Health & Beauty (hb) | Planned | - |
| Toys & Games (tg) | Planned | - |

## Contributing

Contributions welcome! We need help with:

1. **Adding weight estimates** - Real product weights from manufacturers or measurements
2. **Adding LCA data** - Carbon footprint data with sources
3. **Expanding coverage** - New product verticals

### How to contribute

1. Fork the repository
2. Add or update data in YAML files under `data/`
3. Include sources for your data
4. Validate against the schema: `npm run validate` (coming soon)
5. Submit a pull request

### Data quality guidelines

- **Always cite sources** - No unsourced data
- **Prefer primary data** - Manufacturer reports > industry averages > estimates
- **Note methodology** - How was the number derived?
- **Indicate confidence** - Be honest about data quality
- **Use SI units** - Grams for weight, kg CO2e for carbon

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
