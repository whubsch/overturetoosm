"""Test the places.py module."""

from copy import deepcopy
from typing import Any

import pydantic
import pytest

from src.overturetoosm.objects import ConfidenceError, UnmatchedError
from src.overturetoosm.places import process_place
from src.overturetoosm.utils import process_geojson


@pytest.fixture(name="clean_dict")
def clean_fix() -> dict[str, Any]:
    """Fixture with the clean place properties."""
    return {
        "name": "Primary Name",
        "brand": "Brand Name",
        "brand:wikidata": "Q123",
        "addr:street_address": "123 Main St",
        "addr:city": "City",
        "addr:postcode": "12345",
        "addr:state": "CA",
        "addr:country": "US",
        "phone": "+1234567890",
        "website": "https://example.com/",
        "source": "dataset1 via overturetoosm",
        "office": "lawyer",
        "lawyer": "notary",
        "contact:facebook": "https://www.facebook.com/example/",
    }


@pytest.fixture(name="geojson_dict")
def geojson_fix() -> dict[str, Any]:
    """Fixture with a mock place geojson."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-1, 1]},
                "properties": {
                    "id": "123",
                    "version": 1,
                    "update_time": "2022-01-01T00:00:00Z",
                    "sources": [
                        {
                            "property": "property1",
                            "dataset": "dataset1",
                            "record_id": "record1",
                            "confidence": 0.8,
                        }
                    ],
                    "names": {
                        "primary": "Primary Name",
                        "common": {"ex": "Example common name"},
                        "rules": [{"variant": "short", "value": "EX"}],
                    },
                    "brand": {
                        "wikidata": "Q123",
                        "names": {
                            "primary": "Brand Name",
                            "common": {"ex": "Example common name"},
                            "rules": [{"variant": "short", "value": "EX"}],
                        },
                    },
                    "categories": {
                        "main": "notary_public",
                        "alternate": ["alternate_category1", "alternate_category2"],
                    },
                    "confidence": 0.8,
                    "websites": ["https://example.com/"],
                    "socials": ["https://www.facebook.com/example/"],
                    "phones": ["+1234567890"],
                    "addresses": [
                        {
                            "freeform": "123 Main St",
                            "locality": "City",
                            "postcode": "12345",
                            "region": "CA",
                            "country": "US",
                        }
                    ],
                },
            }
        ],
    }


@pytest.fixture(name="props_dict")
def props_fix() -> dict[str, Any]:
    """Fixture with the raw place properties."""
    return {
        "id": "123",
        "version": 1,
        "update_time": "2022-01-01T00:00:00Z",
        "sources": [
            {
                "property": "property1",
                "dataset": "dataset1",
                "record_id": "record1",
                "confidence": 0.8,
            }
        ],
        "names": {
            "primary": "Primary Name",
            "common": {"ex": "Example common name"},
            "rules": [{"variant": "short", "value": "EX"}],
        },
        "brand": {
            "wikidata": "Q123",
            "names": {
                "primary": "Brand Name",
                "common": {"ex": "Example common name"},
                "rules": [{"variant": "short", "value": "EX"}],
            },
        },
        "categories": {
            "main": "notary_public",
            "alternate": ["alternate_category1", "alternate_category2"],
        },
        "confidence": 0.8,
        "websites": ["https://example.com/"],
        "socials": ["https://www.facebook.com/example/"],
        "phones": ["+1234567890"],
        "addresses": [
            {
                "freeform": "123 Main St",
                "locality": "City",
                "postcode": "12345",
                "region": "CA",
                "country": "US",
            }
        ],
    }


def test_place_props(props_dict: dict, clean_dict: dict) -> None:
    """Test that all properties are processed correctly."""
    new_props = process_place(props_dict)
    assert new_props == clean_dict


def test_place_props_no_brand(props_dict: dict, clean_dict: dict) -> None:
    """Test that all properties are processed correctly."""
    props_dict.pop("brand", None)
    new_props = process_place(props_dict)
    for i in ["brand", "brand:wikidata"]:
        clean_dict.pop(i, None)
    assert new_props == clean_dict


def test_place_props_no_category(props_dict: dict, clean_dict: dict) -> None:
    """Test that all properties are processed correctly."""
    props_dict.pop("categories", None)
    new_props = process_place(props_dict)
    for i in ["office", "lawyer"]:
        clean_dict.pop(i, None)
    assert new_props == clean_dict


def test_place_props_twitter(props_dict: dict, clean_dict: dict) -> None:
    """Test that all properties are processed correctly."""
    props_dict["socials"].append("https://twitter.com/example/")
    new_props = process_place(props_dict)
    clean_dict["contact:twitter"] = "https://twitter.com/example/"
    assert new_props == clean_dict


def test_low_confidence(props_dict) -> None:
    """Test that properties with low confidence are not processed."""
    with pytest.raises(ConfidenceError):
        process_place(props_dict, confidence=0.9)


def test_confidence(props_dict) -> None:
    """Test that invalid properties are not processed."""
    props_dict["confidence"] = -0.1
    with pytest.raises(pydantic.ValidationError):
        process_place(props_dict)


def test_unmatched_error(props_dict) -> None:
    """Test that invalid properties are not processed."""
    props_dict["categories"]["main"] = "invalid_category"
    with pytest.raises(UnmatchedError):
        process_place(props_dict, unmatched="error")


def test_unmatched_ignore(props_dict, clean_dict: dict) -> None:
    """Test that invalid properties are not processed."""
    props_dict["categories"]["main"] = "invalid_category"
    for i in ["office", "lawyer"]:
        clean_dict.pop(i, None)
    assert process_place(props_dict, unmatched="ignore") == clean_dict


def test_unmatched_force(props_dict, clean_dict: dict) -> None:
    """Test that invalid properties are not processed."""
    cat = "invalid_category"
    props_dict["categories"]["main"] = cat
    for i in ["office", "lawyer"]:
        clean_dict.pop(i, None)
    clean_dict["type"] = cat
    assert process_place(props_dict, unmatched="force") == clean_dict


def test_place_geojson(geojson_dict, clean_dict: dict) -> None:
    """Test that all properties are processed correctly."""
    assert process_geojson(geojson=geojson_dict, fx=process_place) == {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-1, 1]},
                "properties": clean_dict,
            }
        ],
    }


def test_place_geojson_error(geojson_dict) -> None:
    """Test that all properties are processed correctly when error flag is set."""
    copy = deepcopy(geojson_dict)
    copy["features"][0]["properties"]["categories"]["main"] = "invalid_category"
    assert process_geojson(
        geojson=copy, fx=process_place, options={"unmatched": "error"}
    ) == {"type": "FeatureCollection", "features": []}


def test_place_geojson_force(geojson_dict, clean_dict: dict) -> None:
    """Test that all properties are processed correctly when force flag is set."""
    copy = deepcopy(geojson_dict)
    copy["features"][0]["properties"]["categories"]["main"] = "invalid_category"
    clean_dict["type"] = "invalid_category"
    for i in ["office", "lawyer"]:
        clean_dict.pop(i, None)
    assert process_geojson(
        geojson=copy, fx=process_place, options={"unmatched": "force"}
    ) == {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-1, 1]},
                "properties": clean_dict,
            }
        ],
    }


def test_place_geojson_ignore(geojson_dict, clean_dict: dict) -> None:
    """Test that all properties are processed correctly when ignore flag is set."""
    copy = deepcopy(geojson_dict)
    copy["features"][0]["properties"]["categories"]["main"] = "invalid_category"
    for i in ["office", "lawyer"]:
        clean_dict.pop(i, None)
    assert process_geojson(
        geojson=copy, fx=process_place, options={"unmatched": "ignore"}
    ) == {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-1, 1]},
                "properties": clean_dict,
            }
        ],
    }
