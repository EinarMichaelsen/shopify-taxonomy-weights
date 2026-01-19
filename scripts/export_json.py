#!/usr/bin/env python3
"""
Export all YAML data files to a single consolidated JSON file.
Useful for API integrations and programmatic access.
"""

import yaml
import json
import os
from pathlib import Path
from datetime import datetime


def load_yaml_files(data_dir):
    """Load all YAML files and merge into single structure."""
    all_data = {
        "schema_version": "0.1.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "verticals": {},
        "categories": {},
        "metadata": {
            "total_categories": 0,
            "categories_with_lca": 0,
            "categories_missing_lca": 0,
            "verticals": []
        }
    }

    for yaml_file in sorted(data_dir.glob('*.yml')):
        vertical_name = yaml_file.stem

        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        if not data or 'categories' not in data:
            continue

        # Add vertical info
        all_data["verticals"][vertical_name] = {
            "file": yaml_file.name,
            "category_count": len(data['categories']),
            "schema_version": data.get('schema_version', '0.1.0'),
            "last_updated": data.get('last_updated', 'unknown')
        }
        all_data["metadata"]["verticals"].append(vertical_name)

        # Add categories with vertical prefix
        for cat_id, cat_data in data['categories'].items():
            if not isinstance(cat_data, dict):
                continue

            # Add vertical reference to each category
            cat_data['vertical'] = vertical_name
            all_data["categories"][cat_id] = cat_data

            # Update stats
            all_data["metadata"]["total_categories"] += 1
            if 'lca' in cat_data and 'sources' in cat_data:
                all_data["metadata"]["categories_with_lca"] += 1
            elif cat_data.get('lca_data_missing', False):
                all_data["metadata"]["categories_missing_lca"] += 1

    # Calculate coverage
    total = all_data["metadata"]["total_categories"]
    with_lca = all_data["metadata"]["categories_with_lca"]
    all_data["metadata"]["coverage_percentage"] = round(with_lca / total * 100, 1) if total > 0 else 0

    return all_data


def main():
    data_dir = Path(__file__).parent.parent / 'data'
    output_dir = data_dir.parent / 'dist'
    output_dir.mkdir(exist_ok=True)

    print("Exporting YAML to JSON...")

    # Export consolidated JSON
    all_data = load_yaml_files(data_dir)

    # Full export
    output_file = output_dir / 'shopify-taxonomy-weights.json'
    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2)
    print(f"  Full export: {output_file}")

    # Minified export
    output_file_min = output_dir / 'shopify-taxonomy-weights.min.json'
    with open(output_file_min, 'w') as f:
        json.dump(all_data, f, separators=(',', ':'))
    print(f"  Minified: {output_file_min}")

    # Categories-only export (lighter weight)
    categories_only = {
        "schema_version": "0.1.0",
        "generated_at": all_data["generated_at"],
        "categories": all_data["categories"]
    }
    output_categories = output_dir / 'categories.json'
    with open(output_categories, 'w') as f:
        json.dump(categories_only, f, indent=2)
    print(f"  Categories only: {output_categories}")

    print(f"\nStats:")
    print(f"  Total categories: {all_data['metadata']['total_categories']}")
    print(f"  With sourced LCA: {all_data['metadata']['categories_with_lca']}")
    print(f"  Coverage: {all_data['metadata']['coverage_percentage']}%")
    print(f"  Verticals: {len(all_data['verticals'])}")


if __name__ == '__main__':
    main()
