"""Test the cli.py module."""

import json
import sys
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from src.overturetoosm.cli import main


@pytest.fixture(name="sample_place_geojson")
def sample_place_geojson_fix() -> dict[str, Any]:
    """Fixture with a sample place GeoJSON for testing."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-77.0274, 38.8881]},
                "properties": {
                    "id": "a3899a03-54b5-4693-a700-2fbc93a091b4",
                    "version": 1,
                    "sources": [
                        {
                            "property": "",
                            "dataset": "meta",
                            "record_id": "112232885458679",
                            "confidence": 0.75,
                            "update_time": "2025-06-02T07:00:00.000Z",
                            "between": None,
                        }
                    ],
                    "names": {"primary": "Test Museum", "common": None, "rules": None},
                    "categories": {"primary": "art_museum", "alternate": ["museum"]},
                    "confidence": 0.75,
                    "websites": ["https://www.example.com"],
                    "phones": ["+12026331000"],
                    "addresses": [
                        {
                            "freeform": "1050 Independence Ave SW",
                            "locality": "Washington",
                            "postcode": "20024",
                            "region": "DC",
                            "country": "US",
                        }
                    ],
                },
            }
        ],
    }


@pytest.fixture(name="sample_building_geojson")
def sample_building_geojson_fix() -> dict[str, Any]:
    """Fixture with a sample building GeoJSON for testing."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-77.027, 38.888],
                            [-77.026, 38.888],
                            [-77.026, 38.889],
                            [-77.027, 38.889],
                            [-77.027, 38.888],
                        ]
                    ],
                },
                "properties": {
                    "id": "test-building-id",
                    "version": 1,
                    "sources": [
                        {
                            "property": "",
                            "dataset": "OpenStreetMap",
                            "record_id": "w123456",
                            "confidence": 0.9,
                            "update_time": None,
                            "between": None,
                        }
                    ],
                    "names": {
                        "primary": "Test Building",
                        "common": None,
                        "rules": None,
                    },
                    "height": 15.0,
                    "num_floors": 3,
                    "has_parts": False,
                },
            }
        ],
    }


@pytest.fixture(name="sample_address_geojson")
def sample_address_geojson_fix() -> dict[str, Any]:
    """Fixture with a sample address GeoJSON for testing."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-77.027, 38.888]},
                "properties": {
                    "id": "test-address-id",
                    "version": 1,
                    "sources": [
                        {
                            "property": "",
                            "dataset": "Microsoft",
                            "record_id": "123456",
                            "confidence": 0.8,
                            "update_time": None,
                            "between": None,
                        }
                    ],
                    "address_levels": [{"value": "DC"}, {"value": "Washington"}],
                    "number": "100",
                    "street": "Main St",
                    "postcode": "20001",
                    "country": "US",
                },
            }
        ],
    }


def test_place_conversion_with_output_file(
    sample_place_geojson: dict[str, Any],
) -> None:
    """Test place conversion with separate output file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.geojson"
        output_path = Path(tmpdir) / "output.geojson"

        # Write input file
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(sample_place_geojson, f)

        # Mock sys.argv
        test_args = [
            "overturetoosm",
            "place",
            "-i",
            str(input_path),
            "-o",
            str(output_path),
        ]

        with patch.object(sys, "argv", test_args):
            main()

        # Check output file exists and has content
        assert output_path.exists()
        with open(output_path, encoding="utf-8") as f:
            result = json.load(f)
            assert result["type"] == "FeatureCollection"
            assert len(result["features"]) > 0
            assert "properties" in result["features"][0]


def test_place_conversion_in_place(sample_place_geojson: dict[str, Any]) -> None:
    """Test place conversion with in-place modification."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.geojson"

        # Write input file
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(sample_place_geojson, f)

        # Mock sys.argv
        test_args = ["overturetoosm", "place", "-i", str(input_path), "--in-place"]

        with patch.object(sys, "argv", test_args):
            main()

        # Check input file was modified
        with open(input_path, encoding="utf-8") as f:
            result = json.load(f)
            assert result["type"] == "FeatureCollection"
            assert len(result["features"]) > 0


def test_place_with_confidence_filter(sample_place_geojson: dict[str, Any]) -> None:
    """Test place conversion with confidence threshold."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.geojson"
        output_path = Path(tmpdir) / "output.geojson"

        # Write input file
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(sample_place_geojson, f)

        # Mock sys.argv with high confidence requirement
        test_args = [
            "overturetoosm",
            "place",
            "-i",
            str(input_path),
            "-o",
            str(output_path),
            "-c",
            "0.9",
        ]

        with patch.object(sys, "argv", test_args):
            # Should raise ValueError when all features are filtered out
            with pytest.raises(ValueError, match="No features found"):
                main()


def test_place_with_region_tag(sample_place_geojson: dict[str, Any]) -> None:
    """Test place conversion with custom region tag."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.geojson"
        output_path = Path(tmpdir) / "output.geojson"

        # Write input file
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(sample_place_geojson, f)

        # Mock sys.argv with custom region tag
        test_args = [
            "overturetoosm",
            "place",
            "-i",
            str(input_path),
            "-o",
            str(output_path),
            "-r",
            "addr:province",
        ]

        with patch.object(sys, "argv", test_args):
            main()

        # Check output exists
        assert output_path.exists()
        with open(output_path, encoding="utf-8") as f:
            result = json.load(f)
            assert result["type"] == "FeatureCollection"


def test_place_with_unmatched_option(sample_place_geojson: dict[str, Any]) -> None:
    """Test place conversion with unmatched categories handling."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.geojson"
        output_path = Path(tmpdir) / "output.geojson"

        # Write input file
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(sample_place_geojson, f)

        # Mock sys.argv with unmatched option
        test_args = [
            "overturetoosm",
            "place",
            "-i",
            str(input_path),
            "-o",
            str(output_path),
            "-u",
            "force",
        ]

        with patch.object(sys, "argv", test_args):
            main()

        # Check output exists
        assert output_path.exists()


def test_building_conversion(sample_building_geojson: dict[str, Any]) -> None:
    """Test building conversion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.geojson"
        output_path = Path(tmpdir) / "output.geojson"

        # Write input file
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(sample_building_geojson, f)

        # Mock sys.argv
        test_args = [
            "overturetoosm",
            "building",
            "-i",
            str(input_path),
            "-o",
            str(output_path),
        ]

        with patch.object(sys, "argv", test_args):
            main()

        # Check output file exists and has content
        assert output_path.exists()
        with open(output_path, encoding="utf-8") as f:
            result = json.load(f)
            assert result["type"] == "FeatureCollection"
            assert len(result["features"]) > 0


def test_building_with_confidence_filter(
    sample_building_geojson: dict[str, Any],
) -> None:
    """Test building conversion with confidence threshold."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.geojson"
        output_path = Path(tmpdir) / "output.geojson"

        # Write input file
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(sample_building_geojson, f)

        # Mock sys.argv with confidence filter
        test_args = [
            "overturetoosm",
            "building",
            "-i",
            str(input_path),
            "-o",
            str(output_path),
            "-c",
            "0.85",
        ]

        with patch.object(sys, "argv", test_args):
            main()

        # Check output
        assert output_path.exists()
        with open(output_path, encoding="utf-8") as f:
            result = json.load(f)
            assert result["type"] == "FeatureCollection"


def test_address_conversion(sample_address_geojson: dict[str, Any]) -> None:
    """Test address conversion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.geojson"
        output_path = Path(tmpdir) / "output.geojson"

        # Write input file
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(sample_address_geojson, f)

        # Mock sys.argv
        test_args = [
            "overturetoosm",
            "address",
            "-i",
            str(input_path),
            "-o",
            str(output_path),
        ]

        with patch.object(sys, "argv", test_args):
            main()

        # Check output file exists and has content
        assert output_path.exists()
        with open(output_path, encoding="utf-8") as f:
            result = json.load(f)
            assert result["type"] == "FeatureCollection"
            assert len(result["features"]) > 0


def test_address_with_style_option(sample_address_geojson: dict[str, Any]) -> None:
    """Test address conversion with custom style."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.geojson"
        output_path = Path(tmpdir) / "output.geojson"

        # Write input file
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(sample_address_geojson, f)

        # Mock sys.argv with custom style
        test_args = [
            "overturetoosm",
            "address",
            "-i",
            str(input_path),
            "-o",
            str(output_path),
            "-s",
            "UK",
        ]

        with patch.object(sys, "argv", test_args):
            main()

        # Check output exists
        assert output_path.exists()
        with open(output_path, encoding="utf-8") as f:
            result = json.load(f)
            assert result["type"] == "FeatureCollection"


def test_high_confidence_filters_all_features(
    sample_place_geojson: dict[str, Any],
) -> None:
    """Test that high confidence threshold filters out all features and raises error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.geojson"
        output_path = Path(tmpdir) / "output.geojson"

        # Write feature collection where all features are filtered out by high confidence
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(sample_place_geojson, f)

        # Mock sys.argv with very high confidence that will filter out all features
        test_args = [
            "overturetoosm",
            "place",
            "-i",
            str(input_path),
            "-o",
            str(output_path),
            "-c",
            "0.99",
        ]

        with patch.object(sys, "argv", test_args):
            # Should raise ValueError when all features are filtered out
            with pytest.raises(ValueError, match="No features found"):
                main()


def test_missing_input_file() -> None:
    """Test handling of missing input file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "nonexistent.geojson"
        output_path = Path(tmpdir) / "output.geojson"

        # Mock sys.argv
        test_args = [
            "overturetoosm",
            "place",
            "-i",
            str(input_path),
            "-o",
            str(output_path),
        ]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(FileNotFoundError):
                main()


def test_json_output_formatting(sample_place_geojson: dict[str, Any]) -> None:
    """Test that output JSON is properly formatted with indentation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.geojson"
        output_path = Path(tmpdir) / "output.geojson"

        # Write input file
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(sample_place_geojson, f)

        # Mock sys.argv
        test_args = [
            "overturetoosm",
            "place",
            "-i",
            str(input_path),
            "-o",
            str(output_path),
        ]

        with patch.object(sys, "argv", test_args):
            main()

        # Check output is formatted (contains newlines from indentation)
        with open(output_path, encoding="utf-8") as f:
            content = f.read()
            # Indented JSON should have multiple lines
            assert content.count("\n") > 1
            # Should be valid JSON
            json.loads(content)


def test_in_place_preserves_filename(sample_place_geojson: dict[str, Any]) -> None:
    """Test that in-place conversion preserves the original filename."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "my_data.geojson"

        # Write input file
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(sample_place_geojson, f)

        # Mock sys.argv
        test_args = ["overturetoosm", "place", "-i", str(input_path), "--in-place"]

        with patch.object(sys, "argv", test_args):
            main()

        # Check file still exists with same name
        assert input_path.exists()
        assert input_path.name == "my_data.geojson"


def test_all_place_options_together(sample_place_geojson: dict[str, Any]) -> None:
    """Test place conversion with all options combined."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.geojson"
        output_path = Path(tmpdir) / "output.geojson"

        # Write input file
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(sample_place_geojson, f)

        # Mock sys.argv with all options
        test_args = [
            "overturetoosm",
            "place",
            "-i",
            str(input_path),
            "-o",
            str(output_path),
            "-c",
            "0.5",
            "-r",
            "addr:province",
            "-u",
            "ignore",
        ]

        with patch.object(sys, "argv", test_args):
            main()

        # Check output exists
        assert output_path.exists()
        with open(output_path, encoding="utf-8") as f:
            result = json.load(f)
            assert result["type"] == "FeatureCollection"


def test_missing_subcommand_raises_error(sample_place_geojson: dict[str, Any]) -> None:
    """Test that missing subcommand (place/building/address) raises error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.geojson"
        output_path = Path(tmpdir) / "output.geojson"

        # Write input file
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(sample_place_geojson, f)

        # Mock sys.argv without subcommand
        test_args = ["overturetoosm", "-i", str(input_path), "-o", str(output_path)]

        with patch.object(sys, "argv", test_args):
            # Should raise SystemExit because required subcommand is missing
            with pytest.raises(SystemExit):
                main()
