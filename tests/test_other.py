"""Test miscelaneous functions in the project."""

from src.overturetoosm import objects
from src.overturetoosm import utils


def test_util_source() -> None:
    """Test the source statement function"""
    source_1 = objects.Sources(
        **{"property": "property1", "dataset": "dataset1", "confidence": 0.8}
    )
    source_2 = objects.Sources(
        **{"property": "property2", "dataset": "dataset2", "confidence": 0.8}
    )

    assert (
        utils.source_statement([source_1, source_2])
        == "dataset1, dataset2 via overturetoosm"
    )
