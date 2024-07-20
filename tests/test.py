import pytest
import pydantic
from ..src.overture_to_osm.process import place_props, PlaceProps


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
            "main": "main_category",
            "alternate": ["alternate_category1", "alternate_category2"],
        },
        "confidence": 0.8,
        "websites": ["https://example.com"],
        "socials": ["@example"],
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


def test_process_place_props(props_dict: dict):
    """Test that all properties are processed correctly"""
    new_props = place_props(props_dict)
    assert new_props == {
        "name": "Primary Name",
        "brand": "Brand Name",
        "addr:street_address": "123 Main St",
        "addr:city": "City",
        "addr:postcode": "12345",
        "addr:state": "State",
        "addr:country": "Country",
        "phone": "+1234567890",
        "website": "https://example.com",
        "source": "property1, dataset1 via overture_to_osm",
    }


def test_process_place_props_low_confidence(props_dict):
    """Test that properties with low confidence are not processed"""
    props_dict["confidence"] = 0.5
    new_props = place_props(props_dict)
    assert new_props == {}


def test_process_place_props_invalid_id(props_dict):
    """Test that invalid properties are not processed"""
    del props_dict["id"]
    with pytest.raises(pydantic.ValidationError):
        place_props(props_dict)


def test_process_place_props_invalid_confidence(props_dict):
    props_dict["confidence"] = -0.1
    with pytest.raises(pydantic.ValidationError):
        place_props(props_dict)


def test_process_place_props_invalid_address(props_dict):
    del props_dict["addresses"][0]["freeform"]
    new_props = place_props(props_dict)
    assert "addr:street_address" not in new_props


def test_process_place_props_invalid_phones(props_dict):
    """Test that phones are not added if not present in props"""
    del props_dict["phones"]
    new_props = place_props(props_dict)
    assert "phone" not in new_props


def test_process_place_props_invalid_websites(props_dict):
    """Test that websites are not added if not present in props"""
    del props_dict["websites"]
    new_props = place_props(props_dict)
    assert "website" not in new_props


def test_process_place_props_invalid_socials(props_dict):
    """Test that socials are not added if not present in props"""
    del props_dict["socials"]
    new_props = place_props(props_dict)
    assert "socials" not in new_props
