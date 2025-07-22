"""Tests for the address module."""

from typing import Any

import pytest

from src.overturetoosm.addresses import process_address


@pytest.fixture(name="clean_dict")
def clean_fix() -> dict[str, Any]:
    """Fixture with the clean address properties."""
    return {
        "addr:country": "US",
        "addr:postcode": "02459",
        "addr:street": "COMMONWEALTH AVE",
        "addr:housenumber": "1000",
        "addr:state": "MA",
        "source": "NAD via overturetoosm",
    }


@pytest.fixture(name="props_dict")
def props_fix() -> dict[str, Any]:
    """Fixture with the raw address properties."""
    return {
        "theme": "addresses",
        "type": "address",
        "version": 0,
        "country": "US",
        "address_levels": [{"value": "MA"}, {"value": "NEWTON CENTRE"}],
        "postcode": "02459",
        "street": "COMMONWEALTH AVE",
        "number": "1000",
        "sources": [
            {
                "property": "",
                "dataset": "NAD",
                "record_id": None,
                "update_time": None,
                "confidence": None,
            }
        ],
    }


def test_process_address(props_dict, clean_dict) -> None:
    """Test that address properties are processed correctly."""
    assert process_address(props_dict) == clean_dict


def test_process_address_no_levels(props_dict, clean_dict) -> None:
    """Test that address properties are processed correctly."""
    props_dict.pop("address_levels", None)
    clean_dict.pop("addr:state", None)
    assert process_address(props_dict) == clean_dict


def test_process_address_not_us(props_dict, clean_dict) -> None:
    """Test that address properties are processed correctly."""
    clean_dict.pop("addr:state", None)
    assert process_address(props_dict, style="CA") == clean_dict
