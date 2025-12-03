#!/usr/bin/env python3
"""
Script to check for mismatches between Overture categories CSV and resources.py dict.
Also checks for missing top-level OSM tags in Overture categories.
"""

import argparse
import re
import csv
import sys
import ast
from io import StringIO

import time

import requests
from tqdm import tqdm


# OSM top-level tags as per https://wiki.openstreetmap.org/wiki/Map_features
TOP_LEVEL_TAGS = {
    "advertising",
    "aerialway",
    "aeroway",
    "amenity",
    "barrier",
    "boundary",
    "building",
    "club",
    "craft",
    "departures_board",
    "education",
    "emergency",
    "geological",
    "healthcare",
    "highway",
    "historic",
    "landcover",
    "landuse",
    "leisure",
    "man_made",
    "military",
    "natural",
    "office",
    "piste:type",
    "place",
    "power",
    "public_transport",
    "railway",
    "route",
    "shop",
    "telecom",
    "tourism",
    "waterway",
}


# Import the places_tags dict from resources
# Read it directly to avoid package import issues
def load_places_tags() -> dict:
    """Load places_tags dict from resources.py by parsing the AST."""
    with open("src/overturetoosm/resources.py", "r") as f:
        content = f.read()

    places_string = re.search(
        r"places_tags: dict\[str, dict\[str, str\]\] = (\{.+\})", content, re.M | re.S
    )
    if places_string:
        return ast.literal_eval(places_string.group(1))
    raise ValueError("Could not find places_tags in resources.py")


places_tags = load_places_tags()

# TagInfo API base URL
TAGINFO_API_URL = "https://taginfo.openstreetmap.org/api/4/tag/stats"

# URL to the Overture categories CSV
CSV_URL = "https://raw.githubusercontent.com/OvertureMaps/schema/refs/heads/dev/docs/schema/concepts/by-theme/places/overture_categories.csv"


def fetch_csv_categories():
    """Fetch and parse the Overture categories CSV."""
    print(f"Fetching CSV from: {CSV_URL}")
    response = requests.get(CSV_URL)
    response.raise_for_status()
    content = response.text

    # Parse CSV (semicolon-separated)
    csv_reader = csv.DictReader(StringIO(content), delimiter=";")
    categories = set()

    for row in csv_reader:
        # The first column contains the category code
        # Get the first value in the row
        first_col = list(row.keys())[0]
        category_code = row[first_col].strip()
        if category_code:
            categories.add(category_code)

    return categories


def get_resources_keys():
    """Get all keys from the places_tags dict."""
    return set(places_tags.keys())


def format_output(
    csv_categories, resources_keys, in_csv_not_in_resources, in_resources_not_in_csv
):
    """Format the comparison output."""
    lines = []
    lines.append("=" * 80)
    lines.append("Overture Categories Comparison")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Categories in CSV: {len(csv_categories)}")
    lines.append(f"Keys in resources.py: {len(resources_keys)}")
    lines.append("")

    # Report results
    lines.append("=" * 80)
    lines.append("RESULTS")
    lines.append("=" * 80)
    lines.append("")

    if in_csv_not_in_resources:
        lines.append(
            f"❌ Categories in CSV but NOT in resources.py ({len(in_csv_not_in_resources)}):"
        )
        lines.append("-" * 80)
        for category in sorted(in_csv_not_in_resources):
            lines.append(f"  - {category}")
        lines.append("")
    else:
        lines.append("✅ All CSV categories are present in resources.py")
        lines.append("")

    if in_resources_not_in_csv:
        lines.append(
            f"❌ Keys in resources.py but NOT in CSV ({len(in_resources_not_in_csv)}):"
        )
        lines.append("-" * 80)
        for key in sorted(in_resources_not_in_csv):
            lines.append(f"  - {key}")
        lines.append("")
    else:
        lines.append("✅ All resources.py keys are present in CSV")
        lines.append("")

    # Summary
    lines.append("=" * 80)
    lines.append("SUMMARY")
    lines.append("=" * 80)
    if not in_csv_not_in_resources and not in_resources_not_in_csv:
        lines.append("✅ Perfect match! All categories are synchronized.")
    else:
        lines.append("⚠️  Mismatches found:")
        lines.append(f"   - Missing from resources.py: {len(in_csv_not_in_resources)}")
        lines.append(f"   - Extra in resources.py: {len(in_resources_not_in_csv)}")

    return "\n".join(lines)


def check_missing_top_level_tags():
    """Identify Overture categories without a top-level OSM tag."""
    missing_top_level = []

    for overture_category, osm_tags in places_tags.items():
        # Check if any of the OSM tags are top-level tags
        has_top_level = any(tag in TOP_LEVEL_TAGS for tag in osm_tags.keys())

        if not has_top_level:
            missing_top_level.append({"category": overture_category, "tags": osm_tags})

    return missing_top_level


def format_top_level_output(missing_top_level):
    """Format the top-level tags check output."""
    lines = []
    lines.append("=" * 80)
    lines.append("Top-Level OSM Tags Check")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Total categories in resources.py: {len(places_tags)}")
    lines.append(f"Categories without top-level tags: {len(missing_top_level)}")
    lines.append("")

    if not missing_top_level:
        lines.append("✅ All Overture categories have at least one top-level OSM tag!")
        lines.append("")
    else:
        lines.append("=" * 80)
        lines.append("CATEGORIES WITHOUT TOP-LEVEL TAGS")
        lines.append("=" * 80)
        lines.append("")

        for item in missing_top_level:
            lines.append(f"❌ {item['category']}")
            lines.append(f"   Tags: {item['tags']}")
            lines.append("")

        lines.append("=" * 80)
        lines.append("SUMMARY")
        lines.append("=" * 80)
        percentage = len(missing_top_level) / len(places_tags) * 100
        lines.append(
            f"⚠️  {len(missing_top_level)} categories ({percentage:.1f}%) lack top-level tags"
        )
        lines.append("")

    return "\n".join(lines)


def get_taginfo_stats(key, value):
    """Query TagInfo API for usage statistics of a tag combination.

    Returns the count of 'all' type usage, or None if the query fails.
    """
    try:
        params = {"key": key, "value": value}
        response = requests.get(TAGINFO_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Find the 'all' type count
        for item in data.get("data", []):
            if item.get("type") == "all":
                return item.get("count", 0)
        return 0
    except Exception as e:
        print(f"  ⚠️  Error fetching stats for {key}={value}: {e}", file=sys.stderr)
        return None


def check_taginfo_usage(threshold=1000):
    """Check TagInfo usage counts for all tag combinations with top-level tags.

    Returns list of categories whose top-level tag combinations have fewer than
    threshold uses.
    """
    low_usage_categories = []

    # First, count how many top-level tags we need to check
    total_to_check = 0
    for osm_tags in places_tags.values():
        top_level_tags = {k: v for k, v in osm_tags.items() if k in TOP_LEVEL_TAGS}
        total_to_check += len(top_level_tags)

    print(f"Checking TagInfo API for tag usage (threshold: {threshold})...")
    print(f"Querying {total_to_check} top-level tag combinations...\n")

    with tqdm(total=total_to_check, desc="Checking tags", unit="tag") as pbar:
        for overture_category, osm_tags in places_tags.items():
            # Find top-level tags
            top_level_tags = {k: v for k, v in osm_tags.items() if k in TOP_LEVEL_TAGS}

            if not top_level_tags:
                continue

            # Check each top-level tag combination
            for key, value in top_level_tags.items():
                # Rate limiting - be nice to TagInfo API
                time.sleep(0.1)

                count = get_taginfo_stats(key, value)

                if count is not None and count < threshold:
                    low_usage_categories.append(
                        {
                            "category": overture_category,
                            "key": key,
                            "value": value,
                            "count": count,
                            "all_tags": osm_tags,
                        }
                    )
                    tqdm.write(
                        f"  Found: {overture_category} -> {key}={value} (count: {count})"
                    )

                pbar.update(1)

    print(f"\nChecked {total_to_check} top-level tag combinations")
    return low_usage_categories


def format_taginfo_output(low_usage_categories, threshold=1000):
    """Format the TagInfo usage check output."""
    lines = []
    lines.append("=" * 80)
    lines.append(f"TagInfo API Usage Check (threshold: < {threshold} uses)")
    lines.append("=" * 80)
    lines.append("")

    if not low_usage_categories:
        lines.append(
            f"✅ All categories with top-level tags have at least {threshold} uses in OSM!"
        )
        lines.append("")
    else:
        lines.append(
            f"Found {len(low_usage_categories)} tag combinations with low usage:"
        )
        lines.append("")
        lines.append("=" * 80)
        lines.append("LOW USAGE TAG COMBINATIONS")
        lines.append("=" * 80)
        lines.append("")

        # Sort by count (lowest first)
        sorted_categories = sorted(low_usage_categories, key=lambda x: x["count"])

        for item in sorted_categories:
            lines.append(f"❌ {item['category']}")
            lines.append(f"   Top-level tag: {item['key']}={item['value']}")
            lines.append(f"   Usage count: {item['count']:,}")
            lines.append(f"   All tags: {item['all_tags']}")
            lines.append("")

        lines.append("=" * 80)
        lines.append("SUMMARY")
        lines.append("=" * 80)
        lines.append(
            f"⚠️  {len(low_usage_categories)} tag combinations have < {threshold} uses in OSM"
        )
        lines.append("")
        lines.append("These tags may be:")
        lines.append("  - Newly proposed tags not yet widely adopted")
        lines.append("  - Incorrect or non-standard tag combinations")
        lines.append("  - Regional tags with limited global usage")
        lines.append("")
        lines.append("Consider reviewing these mappings against:")
        lines.append("  - https://wiki.openstreetmap.org/wiki/Map_features")
        lines.append("  - https://taginfo.openstreetmap.org/")

    return "\n".join(lines)


def main():
    """Compare CSV categories with resources.py keys and check for top-level tags."""
    parser = argparse.ArgumentParser(
        description="Compare Overture categories CSV with resources.py and check for top-level OSM tags"
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Save output to file instead of printing to console",
        metavar="FILE",
    )
    parser.add_argument(
        "--check-top-level",
        action="store_true",
        help="Check which Overture categories don't have a top-level OSM tag",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all checks (CSV comparison and top-level tags)",
    )
    parser.add_argument(
        "--check-taginfo",
        action="store_true",
        help="Check TagInfo API for usage counts of top-level tags",
    )
    parser.add_argument(
        "--taginfo-threshold",
        type=int,
        default=1000,
        help="Minimum usage count threshold for TagInfo check (default: 1000)",
    )
    args = parser.parse_args()

    # If no specific check is requested, default to CSV comparison
    if not args.check_top_level and not args.all and not args.check_taginfo:
        args.check_top_level = False
        run_csv_check = True
    else:
        run_csv_check = args.all

    output_parts = []

    # CSV comparison check
    if run_csv_check:
        csv_categories = fetch_csv_categories()
        resources_keys = get_resources_keys()
        in_csv_not_in_resources = csv_categories - resources_keys
        in_resources_not_in_csv = resources_keys - csv_categories
        csv_output = format_output(
            csv_categories,
            resources_keys,
            in_csv_not_in_resources,
            in_resources_not_in_csv,
        )
        output_parts.append(csv_output)

    # Top-level tags check
    if args.check_top_level or args.all:
        missing_top_level = check_missing_top_level_tags()
        top_level_output = format_top_level_output(missing_top_level)
        output_parts.append(top_level_output)

    # TagInfo usage check
    if args.check_taginfo or args.all:
        low_usage = check_taginfo_usage(threshold=args.taginfo_threshold)
        taginfo_output = format_taginfo_output(
            low_usage, threshold=args.taginfo_threshold
        )
        output_parts.append(taginfo_output)

    # Combine outputs

    output = "\n\n".join(output_parts)

    # Print or save output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"✅ Results saved to: {args.output}")
        if run_csv_check:
            print(f"   - Missing from resources.py: {len(in_csv_not_in_resources)}")
            print(f"   - Extra in resources.py: {len(in_resources_not_in_csv)}")
        if args.check_top_level or args.all:
            print(f"   - Categories without top-level tags: {len(missing_top_level)}")
        if args.check_taginfo or args.all:
            print(f"   - Low usage tag combinations: {len(low_usage)}")
    else:
        print(output)

    # Return exit code
    exit_code = 0
    if run_csv_check and (in_csv_not_in_resources or in_resources_not_in_csv):
        exit_code = 1
    if (args.check_top_level or args.all) and missing_top_level:
        exit_code = 1
    if (args.check_taginfo or args.all) and low_usage:
        exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
