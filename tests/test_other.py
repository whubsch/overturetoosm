"""Test miscelaneous functions in the project."""

import json
import pytest
from src.overturetoosm import objects, segments


@pytest.fixture(name="props_dict")
def props_fix() -> dict:
    """Fixture with the clean segment properties."""
    return {
        "property": "",
        "dataset": "OpenStreetMap",
        "record_id": "w590831817",
        "update_time": None,
        "confidence": None,
    }


def test_util_source() -> None:
    """Test the source statement function."""
    source_1 = objects.Sources(
        **{"property": "property1", "dataset": "dataset1", "confidence": 0.8}
    )
    source_2 = objects.Sources(
        **{"property": "property2", "dataset": "dataset2", "confidence": 0.8}
    )

    assert (
        objects.source_statement([source_1, source_2])
        == "dataset1, dataset2 via overturetoosm"
    )


def test_segment_sources(props_dict: dict) -> None:
    """Test that source URL is processed correctly."""
    source = objects.Sources(**props_dict)
    assert source.get_osm_link() == "https://www.openstreetmap.org/way/590831817"


def test_segment_sources_not_osm(props_dict: dict) -> None:
    """Test that source URL is processed correctly."""
    props_dict.update({"dataset": "dataset1"})
    source = objects.Sources(**props_dict)
    assert source.get_osm_link() == None


@pytest.mark.parametrize(
    "type",
    [
        ("place", objects.PlaceProps),
        ("building", objects.BuildingProps),
        ("address", objects.AddressProps),
        ("segment", segments.SegmentProperties),
    ],
)
def test_objects(type) -> None:
    """Test that all properties are processed correctly."""
    with open(f"scripts/test_{type[0]}.geojson", encoding="utf-8") as f:
        data = json.load(f)

        for feature in data["features"]:
            type[1](**feature["properties"])
