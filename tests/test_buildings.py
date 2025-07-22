"""Test the buildings.py module."""

from typing import Any

import pytest

from src.overturetoosm.buildings import process_building
from src.overturetoosm.objects import ConfidenceError


@pytest.fixture(name="clean_dict")
def clean_fix() -> dict[str, Any]:
    """Fixture with the clean building properties."""
    return {
        "building": "parking",
        "building:levels": 4,
        "building:levels:underground": 1,
        "height": 21.34,
        "source": "metaLidarExtractions, microsoftMLBuildings via overturetoosm",
        "name": "Clarendon Family Dentistry",
    }


@pytest.fixture(name="props_dict")
def props_fix() -> dict[str, Any]:
    """Fixture with the raw building properties."""
    return {
        "theme": "buildings",
        "type": "building",
        "version": 1,
        "level": 1,
        "height": 21.34,
        "has_parts": False,
        "num_floors": 4,
        "names": {
            "primary": "Clarendon Family Dentistry",
            "common": None,
            "rules": None,
        },
        "num_floors_underground": 1,
        "subtype": "transportation",
        "class": "parking",
        "is_underground": False,
        "sources": [
            {"property": "", "dataset": "microsoftMLBuildings,", "confidence": 0.7},
            {
                "property": "/properties/height",
                "dataset": "metaLidarExtractions,",
                "confidence": 0.45,
            },
        ],
    }


def test_process_building(props_dict: dict, clean_dict: dict) -> None:
    """Test the process_building function."""
    props = process_building(props_dict)
    assert props == clean_dict


def test_process_building_confidence(props_dict: dict) -> None:
    """Test the process_building function."""
    with pytest.raises(ConfidenceError):
        process_building(props_dict, confidence=0.9)


def test_process_building_underground(props_dict: dict, clean_dict: dict) -> None:
    """Test the process_building function."""
    props_dict["is_underground"] = True
    props = process_building(props_dict)
    clean_dict["location"] = "underground"
    assert props == clean_dict


def test_process_building_no_floors(props_dict: dict, clean_dict: dict) -> None:
    """Test the process_building function."""
    props_dict.pop("num_floors", None)
    props = process_building(props_dict)
    clean_dict.pop("building:levels", None)
    assert props == clean_dict


def test_process_building_underfloors(props_dict: dict, clean_dict: dict) -> None:
    """Test the process_building function."""
    props_dict.pop("num_floors_underground", None)
    props = process_building(props_dict)
    clean_dict.pop("building:levels:underground", None)
    assert props == clean_dict


def test_process_building_min_level(props_dict: dict, clean_dict: dict) -> None:
    """Test the process_building function."""
    props_dict["min_floor"] = 2
    props = process_building(props_dict)
    clean_dict["building:min_level"] = 2
    assert props == clean_dict
