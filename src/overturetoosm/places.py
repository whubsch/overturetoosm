"""Convert Overture's `places` features to OSM tags."""

from typing import Literal

from .objects import PlaceProps, UnmatchedError, ConfidenceError
from .resources import places_tags


def process_props(
    props: dict,
    region_tag: str = "addr:state",
    confidence: float = 0.0,
    unmatched: Literal["error", "force", "ignore"] = "ignore",
) -> dict[str, str]:
    """Convert Overture's places properties to OSM tags.

    Example usage:
    ```python
    import json
    from overturetoosm.places import process_props

    with open("overture.geojson", "r", encoding="utf-8") as f:
        contents: dict = json.load(f)

        for feature in contents["features"]:
            feature["properties"] = process_props(feature["properties"])

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
        dict[str, str]: The reshaped and converted properties in OSM's flat str:str schema.

    Raises:
        `UnmatchedError`: Raised if `unmatched` is set to `error` and the Overture category
            has no OSM definition.
        `ConfidenceError`: Raised if the confidence level is set above a feature's confidence.
    """
    new_props = {}
    prop_obj = PlaceProps(**props)
    if prop_obj.confidence < confidence:
        raise ConfidenceError(confidence, prop_obj.confidence)

    if prop_obj.categories:
        prim = places_tags.get(prop_obj.categories.main)
        if prim:
            new_props |= prim
        elif unmatched == "force":
            new_props |= {"type": prop_obj.categories.main}
        elif unmatched == "error":
            raise UnmatchedError(prop_obj.categories.main)

    if prop_obj.names.primary:
        new_props |= {"name": prop_obj.names.primary}

    if prop_obj.phones is not None:
        new_props["phone"] = prop_obj.phones[0]

    if prop_obj.websites is not None:
        new_props["website"] = prop_obj.websites[0]

    if add := prop_obj.addresses[0]:
        if add.freeform:
            new_props["addr:street_address"] = add.freeform
        if add.country:
            new_props["addr:country"] = add.country
        if add.postcode:
            new_props["addr:postcode"] = add.postcode
        if add.locality:
            new_props["addr:city"] = add.locality
        if add.region:
            new_props[region_tag] = add.region

    if prop_obj.sources:
        new_props["source"] = (
            ", ".join({i.dataset for i in prop_obj.sources}) + " via overturetoosm"
        )

    if prop_obj.socials is not None:
        for social in prop_obj.socials:
            if "facebook" in social:
                new_props["contact:facebook"] = social
            elif "twitter" in social:
                new_props["contact:twitter"] = social

    if prop_obj.brand:
        new_props["brand"] = prop_obj.brand.names.primary
        new_props["brand:wikidata"] = prop_obj.brand.wikidata

    return new_props


def process_geojson(
    geojson: dict,
    region_tag: str = "addr:state",
    confidence: float = 0.0,
    unmatched: Literal["error", "force", "ignore"] = "ignore",
) -> dict:
    """Convert an Overture `place` GeoJSON to one that follows OSM's schema.

    Example usage:
    ```python
    import json
    from overturetoosm.places import process_geojson

    with open("overture.geojson", "r", encoding="utf-8") as f:
        contents: dict = json.load(f)
        geojson = process_geojson(contents)

    with open("overture_out.geojson", "w+", encoding="utf-8") as x:
        json.dump(geojson, x, indent=4)
    ```
    Args:
        geojson (dict): The dictionary representation of the Overture GeoJSON.
        region_tag (str, optional): What tag to convert Overture's `region` tag to.
            Defaults to `addr:state`.
        confidence (float, optional): The minimum confidence level. Defaults to 0.0.
        unmatched (Literal["error", "force", "ignore"], optional): How to handle unmatched Overture
            categories. The "error" option skips unmatched places, "force" puts the
            category into the `type` key, and "ignore" only returns other properties.
            Defaults to "ignore".

    Returns:
        dict: The dictionary representation of the GeoJSON that follows OSM's schema.
    """
    new_features = []
    for feature in geojson["features"]:
        try:
            feature["properties"] = process_props(
                feature["properties"], region_tag, confidence, unmatched
            )
            new_features.append(feature)
        except (ConfidenceError, UnmatchedError):
            pass

    geojson["features"] = new_features
    return geojson
