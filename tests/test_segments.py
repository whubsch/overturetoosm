"""Test the segments.py module."""

from typing import Any

import pytest
from pydantic import ValidationError

from src.overturetoosm.segments import SegmentProperties
# from src.overturetoosm.objects import ConfidenceError


@pytest.fixture(name="props_dict")
def props_fix() -> dict[str, Any]:
    """Fixture with the clean segment properties."""
    return {
        "id": "0892aa87b057ffff043ffa50b0c799df",
        "version": 0,
        "sources": [
            {
                "property": "",
                "dataset": "OpenStreetMap",
                "record_id": "w590831817",
                "update_time": None,
                "confidence": None,
            }
        ],
        "subtype": "road",
        "class": "secondary",
        "names": {
            "primary": "South Arlington Ridge Road",
            "common": None,
            "rules": None,
        },
        "level": 3,
        "connector_ids": [
            "08f2aa87b042d070047f7e4ae29f3ddf",
            "08f2aa87b0553085043f7b50915fc2f9",
            "08f2aa87b0550799043f5e54b6721dab",
            "08f2aa87b055042c043d5f567e660ef3",
        ],
        "road_surface": [{"value": "paved", "between": None}],
        "speed_limits": [
            {
                "min_speed": None,
                "max_speed": {"value": 25, "unit": "mph"},
                "is_max_speed_variable": None,
                "when": None,
                "between": None,
            }
        ],
    }


def test_segment_props(props_dict: dict) -> None:
    """Test that all properties are processed correctly."""
    new_props = SegmentProperties(**props_dict)
    assert isinstance(new_props, SegmentProperties)


@pytest.mark.parametrize(
    "remove_key", ["road_surface", "speed_limits", "sources", "level", "names"]
)
def test_segment_props_no_tags(props_dict: dict, remove_key: str) -> None:
    """Test that all properties are processed correctly."""
    props_dict.pop(remove_key, None)
    new_props = SegmentProperties(**props_dict)
    assert isinstance(new_props, SegmentProperties)


@pytest.mark.parametrize("remove_key", ["id", "version", "subtype"])
def test_segment_props_no_id(props_dict: dict, remove_key: str) -> None:
    """Test that all properties are processed correctly."""
    props_dict.pop(remove_key, None)
    with pytest.raises(ValidationError):
        SegmentProperties(**props_dict)


# def test_segment_props_no_class(props_dict: dict) -> None:
#     """Test that all properties are processed correctly."""
#     props_dict.pop("class", None)
#     new_props = SegmentProperties(**props_dict).model_dump(exclude_none=True)
#     assert isinstance(new_props, dict)
