"""Convert Overture's `places` features to OSM tags."""

from typing import Literal

from .objects import PlaceProps


def process_place(
    props: dict,
    confidence: float = 0.0,
    region_tag: str = "addr:state",
    unmatched: Literal["error", "force", "ignore"] = "ignore",
) -> dict[str, str]:
    """Convert Overture's places properties to OSM tags.

    Example usage:
    ```python
    import json
    from overturetoosm import process_place

    with open("overture.geojson", "r", encoding="utf-8") as f:
        contents: dict = json.load(f)

        for feature in contents["features"]:
            feature["properties"] = process_place(feature["properties"], confidence=0.5)

    with open("overture_out.geojson", "w+", encoding="utf-8") as x:
        json.dump(contents, x, indent=4)
    ```
    Args:
        props (dict): The feature properties from the Overture GeoJSON.
        region_tag (str, optional): What tag to convert Overture's `region` tag to.
            Defaults to `addr:state`.
        confidence (float, optional): The minimum confidence level. Defaults to 0.0.
        unmatched (Literal["error", "force", "ignore"], optional): How to handle
            unmatched Overture categories. The "error" option raises an UnmatchedError
            exception, "force" puts the category into the `type` key, and "ignore"
            only returns other properties. Defaults to "ignore".

    Returns:
        dict[str, str]: The reshaped and converted properties in OSM's flat str:str
            schema.

    Raises:
        `overturetoosm.objects.UnmatchedError`: Raised if `unmatched` is set to `error`
            and the Overture category has no OSM definition.
        `overturetoosm.objects.ConfidenceError`: Raised if the confidence level is set
            above a feature's confidence.
    """
    return PlaceProps(**props).to_osm(confidence, region_tag, unmatched)
