"""Useful functions for the project."""

from collections.abc import Callable

from .objects import ConfidenceError, UnmatchedError


def process_geojson(
    geojson: dict,
    fx: Callable,
    confidence: float | None = None,
    options: dict | None = None,
) -> dict:
    """Convert an Overture `place` GeoJSON to one that follows OSM's schema.

    Example usage:
    ```python
    import json
    from overturetoosm import process_geojson

    with open("overture.geojson", "r", encoding="utf-8") as f:
        contents: dict = json.load(f)
        geojson = process_geojson(contents, fx=process_building)

    with open("overture_out.geojson", "w+", encoding="utf-8") as x:
        json.dump(geojson, x, indent=4)
    ```
    Args:
        geojson (dict): The dictionary representation of the Overture GeoJSON.
        fx (Callable): The function to apply to each feature.
        confidence (float, optional): The minimum confidence level. Defaults to 0.0.
        options (dict, optional): Function-specific options to pass as arguments to
            the `fx` function.

    Returns:
        dict: The dictionary representation of the GeoJSON that follows OSM's schema.
    """
    options = options or {}
    new_features = []
    for feature in geojson["features"]:
        try:
            if confidence:
                feature["properties"] = fx(feature["properties"], confidence, **options)
            else:
                feature["properties"] = fx(feature["properties"], **options)
            new_features.append(feature)
        except (ConfidenceError, UnmatchedError):
            pass

    geojson["features"] = new_features
    return geojson
