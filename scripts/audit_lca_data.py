#!/usr/bin/env python3
"""
Audit LCA data across all YAML files.
- Removes LCA data where no sources are cited
- Adds lca_data_missing: true for categories without sourced LCA data
- Generates report of changes and categories needing LCA data
"""

import yaml
import os
import re
from pathlib import Path
from collections import defaultdict

# Custom YAML representer to preserve formatting
class LiteralStr(str):
    pass

def literal_str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(LiteralStr, literal_str_representer)

def audit_yaml_file(filepath):
    """Audit a single YAML file and return statistics."""
    with open(filepath, 'r') as f:
        content = f.read()

    data = yaml.safe_load(content)
    if not data or 'categories' not in data:
        return None, {}

    stats = {
        'total_categories': 0,
        'categories_with_sourced_lca': 0,
        'categories_lca_removed': 0,
        'categories_missing_lca': 0,
        'lca_removed_list': [],
        'categories_needing_lca': []
    }

    categories = data['categories']

    for cat_id, cat_data in categories.items():
        if not isinstance(cat_data, dict):
            continue

        stats['total_categories'] += 1
        has_lca = 'lca' in cat_data
        has_sources = 'sources' in cat_data and cat_data['sources']
        already_marked_missing = cat_data.get('lca_data_missing', False)

        if has_lca and has_sources:
            # Keep LCA data - it has sources
            stats['categories_with_sourced_lca'] += 1
        elif has_lca and not has_sources:
            # Remove LCA data - no sources
            del cat_data['lca']
            cat_data['lca_data_missing'] = True
            stats['categories_lca_removed'] += 1
            stats['lca_removed_list'].append({
                'id': cat_id,
                'name': cat_data.get('name', 'Unknown')
            })
            stats['categories_needing_lca'].append({
                'id': cat_id,
                'name': cat_data.get('name', 'Unknown'),
                'materials': cat_data.get('materials', {}).get('primary_material', 'unknown')
            })
        elif not has_lca and not already_marked_missing:
            # No LCA data and not marked - add flag
            cat_data['lca_data_missing'] = True
            stats['categories_missing_lca'] += 1
            stats['categories_needing_lca'].append({
                'id': cat_id,
                'name': cat_data.get('name', 'Unknown'),
                'materials': cat_data.get('materials', {}).get('primary_material', 'unknown')
            })
        elif already_marked_missing:
            # Already properly marked as missing
            stats['categories_missing_lca'] += 1
            stats['categories_needing_lca'].append({
                'id': cat_id,
                'name': cat_data.get('name', 'Unknown'),
                'materials': cat_data.get('materials', {}).get('primary_material', 'unknown')
            })

    return data, stats


def write_yaml_file(filepath, data):
    """Write YAML file with custom formatting."""
    # Custom dumper to handle special cases
    class CustomDumper(yaml.SafeDumper):
        pass

    def str_representer(dumper, data):
        if '\n' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)

    CustomDumper.add_representer(str, str_representer)

    with open(filepath, 'w') as f:
        yaml.dump(data, f, Dumper=CustomDumper, default_flow_style=False,
                  sort_keys=False, allow_unicode=True, width=120)


def main():
    data_dir = Path(__file__).parent.parent / 'data'

    all_stats = {}
    all_needing_lca = []
    total_removed = 0

    print("=" * 60)
    print("LCA Data Audit Report")
    print("=" * 60)
    print()

    for yaml_file in sorted(data_dir.glob('*.yml')):
        print(f"Processing: {yaml_file.name}")

        data, stats = audit_yaml_file(yaml_file)
        if data is None:
            print(f"  Skipped (no categories)")
            continue

        all_stats[yaml_file.name] = stats
        total_removed += stats['categories_lca_removed']

        # Add file context to needing LCA list
        for cat in stats['categories_needing_lca']:
            cat['file'] = yaml_file.name
            all_needing_lca.append(cat)

        print(f"  Total categories: {stats['total_categories']}")
        print(f"  With sourced LCA: {stats['categories_with_sourced_lca']}")
        print(f"  LCA removed (no source): {stats['categories_lca_removed']}")
        print(f"  Missing LCA data: {stats['categories_missing_lca']}")

        if stats['lca_removed_list']:
            print(f"  Removed LCA from:")
            for item in stats['lca_removed_list'][:5]:
                print(f"    - {item['id']}: {item['name']}")
            if len(stats['lca_removed_list']) > 5:
                print(f"    ... and {len(stats['lca_removed_list']) - 5} more")

        # Write updated file
        write_yaml_file(yaml_file, data)
        print(f"  Updated: {yaml_file.name}")
        print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    total_categories = sum(s['total_categories'] for s in all_stats.values())
    total_sourced = sum(s['categories_with_sourced_lca'] for s in all_stats.values())
    total_missing = sum(s['categories_missing_lca'] for s in all_stats.values()) + total_removed

    print(f"Total categories: {total_categories}")
    print(f"Categories with sourced LCA: {total_sourced}")
    print(f"Categories needing LCA data: {total_missing}")
    print(f"LCA data removed (unsourced): {total_removed}")
    print(f"Coverage: {total_sourced/total_categories*100:.1f}%")

    # Write report for GitHub issues
    report_path = data_dir.parent / 'docs' / 'lca_data_needed.md'
    report_path.parent.mkdir(exist_ok=True)

    with open(report_path, 'w') as f:
        f.write("# Categories Needing LCA Data\n\n")
        f.write(f"Total categories needing LCA data: {len(all_needing_lca)}\n\n")

        # Group by file
        by_file = defaultdict(list)
        for cat in all_needing_lca:
            by_file[cat['file']].append(cat)

        for filename, cats in sorted(by_file.items()):
            f.write(f"## {filename}\n\n")
            f.write(f"Categories needing LCA data: {len(cats)}\n\n")
            f.write("| ID | Name | Primary Material |\n")
            f.write("|---|---|---|\n")
            for cat in cats:
                f.write(f"| {cat['id']} | {cat['name']} | {cat['materials']} |\n")
            f.write("\n")

    print(f"\nReport written to: {report_path}")

    return all_stats, all_needing_lca


if __name__ == '__main__':
    main()
