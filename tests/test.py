from copy import deepcopy
import pytest
import pydantic
from src.overturetoosm.places import (
    ConfidenceError,
    UnmatchedError,
    process_geojson,
    process_props,
)

clean = {
    "name": "Primary Name",
    "brand": "Brand Name",
    "brand:wikidata": "Q123",
    "addr:street_address": "123 Main St",
    "addr:city": "City",
    "addr:postcode": "12345",
    "addr:state": "State",
    "addr:country": "Country",
    "phone": "+1234567890",
    "website": "https://example.com",
    "source": "dataset1 via overturetoosm",
    "office": "lawyer",
    "lawyer": "notary",
    "contact:facebook": "www.facebook.com/example",
}


@pytest.fixture
def geojson_dict():
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
                        "common": "Common Name",
                        "rules": "Rules Name",
                    },
                    "brand": {
                        "wikidata": "Q123",
                        "names": {
                            "primary": "Brand Name",
                            "common": "Common Name",
                            "rules": "Rules Name",
                        },
                    },
                    "categories": {
                        "main": "notary_public",
                        "alternate": ["alternate_category1", "alternate_category2"],
                    },
                    "confidence": 0.8,
                    "websites": ["https://example.com"],
                    "socials": ["www.facebook.com/example"],
                    "phones": ["+1234567890"],
                    "addresses": [
                        {
                            "freeform": "123 Main St",
                            "locality": "City",
                            "postcode": "12345",
                            "region": "State",
                            "country": "Country",
                        }
                    ],
                },
            }
        ],
    }


@pytest.fixture
def props_dict():
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
            "common": "Common Name",
            "rules": "Rules Name",
        },
        "brand": {
            "wikidata": "Q123",
            "names": {
                "primary": "Brand Name",
                "common": "Common Name",
                "rules": "Rules Name",
            },
        },
        "categories": {
            "main": "notary_public",
            "alternate": ["alternate_category1", "alternate_category2"],
        },
        "confidence": 0.8,
        "websites": ["https://example.com"],
        "socials": ["www.facebook.com/example"],
        "phones": ["+1234567890"],
        "addresses": [
            {
                "freeform": "123 Main St",
                "locality": "City",
                "postcode": "12345",
                "region": "State",
                "country": "Country",
            }
        ],
    }


def test_place_props(props_dict: dict):
    """Test that all properties are processed correctly"""
    new_props = process_props(props_dict)
    assert new_props == clean


def test_low_confidence(props_dict):
    """Test that properties with low confidence are not processed"""
    with pytest.raises(ConfidenceError):
        process_props(props_dict, confidence=0.9)


def test_confidence(props_dict):
    """Test that invalid properties are not processed"""
    props_dict["confidence"] = -0.1
    with pytest.raises(pydantic.ValidationError):
        process_props(props_dict)


def test_unmatched_error(props_dict):
    """Test that invalid properties are not processed"""
    props_dict["categories"]["main"] = "invalid_category"
    with pytest.raises(UnmatchedError):
        process_props(props_dict, unmatched="error")


def test_unmatched_ignore(props_dict):
    """Test that invalid properties are not processed"""
    props_dict["categories"]["main"] = "invalid_category"
    cl = deepcopy(clean)
    del cl["office"]
    del cl["lawyer"]
    assert process_props(props_dict, unmatched="ignore") == cl


def test_unmatched_force(props_dict):
    """Test that invalid properties are not processed"""
    cat = "invalid_category"
    props_dict["categories"]["main"] = cat
    cl = deepcopy(clean)
    del cl["office"]
    del cl["lawyer"]
    cl["type"] = cat
    assert process_props(props_dict, unmatched="force") == cl


def test_place_geojson(geojson_dict):
    """Test that all properties are processed correctly"""
    assert process_geojson(geojson_dict) == {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-1, 1]},
                "properties": clean,
            }
        ],
    }


def test_place_geojson_error(geojson_dict):
    """Test that all properties are processed correctly when error flag is set"""
    copy = deepcopy(geojson_dict)
    copy["features"][0]["properties"]["categories"]["main"] = "invalid_category"
    print(copy)
    assert process_geojson(geojson_dict, unmatched="error") == {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-1, 1]},
                "properties": clean,
            }
        ],
    }
