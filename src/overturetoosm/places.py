"""Convert Overture's `places` features to OSM tags."""

from typing import Literal, Dict

from .objects import PlaceProps, UnmatchedError, ConfidenceError
from .resources import places_tags


def process_place(
    props: dict,
    confidence: float = 0.0,
    region_tag: str = "addr:state",
    unmatched: Literal["error", "force", "ignore"] = "ignore",
) -> Dict[str, str]:
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
        dict[str, str]: The reshaped and converted properties in OSM's flat str:str schema.

    Raises:
        `overturetoosm.objects.UnmatchedError`: Raised if `unmatched` is set to `error` and
            the Overture category has no OSM definition.
        `overturetoosm.objects.ConfidenceError`: Raised if the confidence level is set
            above a feature's confidence.
    """
    new_props = {}
    prop_obj = PlaceProps(**props)
    if prop_obj.confidence < confidence:
        raise ConfidenceError(confidence, prop_obj.confidence)

    if prop_obj.categories:
        prim = places_tags.get(prop_obj.categories.main)
        if prim:
            new_props = {**new_props, **prim}
        elif unmatched == "force":
            new_props["type"] = prop_obj.categories.main
        elif unmatched == "error":
            raise UnmatchedError(prop_obj.categories.main)

    if prop_obj.names.primary:
        new_props["name"] = prop_obj.names.primary

    if prop_obj.phones is not None:
        new_props["phone"] = prop_obj.phones[0]

    if prop_obj.websites is not None:
        new_props["website"] = str(prop_obj.websites[0])

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
            social_str = str(social)
            if "facebook" in social_str:
                new_props["contact:facebook"] = social_str
            elif "twitter" in str(social):
                new_props["contact:twitter"] = social_str

    if prop_obj.brand:
        new_props["brand"] = prop_obj.brand.names.primary
        new_props["brand:wikidata"] = prop_obj.brand.wikidata

    return new_props
