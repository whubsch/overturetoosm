"""Command line interface for the overturetoosm package."""

import argparse
import json

from . import process_address, process_building, process_geojson, process_place


def main():
    """Configure the argument parser for the CLI."""
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument(
        "-i", "--input", required=True, help="Path to the input GeoJSON file"
    )
    out = parent.add_argument_group("output options")
    output_group = out.add_mutually_exclusive_group(required=True)
    output_group.add_argument("-o", "--output", help="Path to the output GeoJSON file")
    output_group.add_argument(
        "--in-place",
        action="store_true",
        help="Convert the input file in place (overwrites the input file)",
    )

    parser = argparse.ArgumentParser(
        description="Convert Overture data to the OSM schema in the GeoJSON format."
    )
    subs = parser.add_subparsers(dest="fx_type", help="types")
    place_parser = subs.add_parser("place", help="Convert place data", parents=[parent])
    place_parser.add_argument(
        "-c",
        "--confidence",
        type=float,
        default=0.0,
        help="The minimum confidence level. Default: 0.0",
    )
    place_parser.add_argument(
        "-r",
        "--region-tag",
        default="addr:state",
        help="What tag to convert Overture's `region` tag to. Default: `addr:state`",
    )
    place_parser.add_argument(
        "-u",
        "--unmatched",
        choices=["force", "ignore"],
        default="ignore",
        help="How to handle unmatched Overture categories. Default: ignore",
    )

    building_parser = subs.add_parser(
        "building", help="Convert building data", parents=[parent]
    )
    building_parser.add_argument(
        "-c",
        "--confidence",
        type=float,
        default=0.0,
        help="The minimum confidence level. Default: 0.0",
    )

    address_parser = subs.add_parser(
        "address", help="Convert address data", parents=[parent]
    )
    address_parser.add_argument(
        "-s",
        "--style",
        default="US",
        help="How to handle the `address_levels` field. Default: US",
    )

    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        contents: dict = json.load(f)
        geojson = {}
        if args.fx_type == "place":
            geojson = process_geojson(
                contents,
                process_place,
                confidence=args.confidence,
                options={"region_tag": args.region_tag, "unmatched": args.unmatched},
            )
        elif args.fx_type == "building":
            geojson = process_geojson(
                contents, process_building, confidence=args.confidence
            )
        elif args.fx_type == "address":
            geojson = process_geojson(
                contents, process_address, options={"style": args.style}
            )

    if not geojson:
        raise ValueError("No features found in the input file.")

    if args.in_place:
        with open(args.input, "w+", encoding="utf-8") as f:
            json.dump(geojson, f, indent=4)
    else:
        with open(args.output, "w+", encoding="utf-8") as f:
            json.dump(geojson, f, indent=4)
