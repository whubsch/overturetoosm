"""Command line interface for the overturetoosm package."""

import argparse
import json
from typing import Dict

from . import process_address, process_building, process_geojson, process_place


def parse_kwargs(pairs) -> Dict[str, str]:
    """Parse key-value pairs into a dictionary."""
    kwargs = {}
    for pair in pairs:
        key, value = pair.split("=")
        kwargs[key] = value
    return kwargs


def main():
    """Configure the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Convert Overture data to the OSM schema in the GeoJSON format."
    )

    parser.add_argument(
        "-i", "--input", required=True, help="Path to the input GeoJSON file"
    )
    out = parser.add_argument_group("Output options")
    output_group = out.add_mutually_exclusive_group(required=True)
    output_group.add_argument("-o", "--output", help="Path to the output GeoJSON file")
    output_group.add_argument(
        "--in-place",
        action="store_true",
        help="Convert the input file in place (overwrites the original file)",
    )

    parser.add_argument(
        "-t",
        "--type",
        choices=["place", "building", "address"],
        type=str,
        required=True,
        help="Type of feature to convert (place, building, or address)",
    )
    parser.add_argument("kwargs", nargs="*", help="Additional arguments")

    args = parser.parse_args()

    kwargs = parse_kwargs(args.kwargs)

    fx_dict = {
        "place": process_place,
        "building": process_building,
        "address": process_address,
    }

    with open(args.input, "r", encoding="utf-8") as f:
        contents: dict = json.load(f)
        conf = float(kwargs.get("confidence", 0))
        kwargs.pop("confidence", None)
        geojson = process_geojson(
            contents, fx=fx_dict.get(args.type, None), confidence=conf, options=kwargs
        )

    if args.in_place:
        with open(args.input, "w+", encoding="utf-8") as f:
            json.dump(geojson, f, indent=4)
    else:
        with open(args.output, "w+", encoding="utf-8") as f:
            json.dump(geojson, f, indent=4)
