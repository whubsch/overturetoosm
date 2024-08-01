"""Convert Overture's `addresses` features to OSM tags."""

from typing import Dict
from .objects import AddressProps


def process_address(
    props: dict,
    style: str = "US",
) -> Dict[str, str]:
    """Convert Overture's address properties to OSM tags.

    Args:
        props (dict): The feature properties from the Overture GeoJSON.
        style (str, optional): How to handle the `address_levels` field. Open
            a pull request or issue to add support for other regions. Defaults to "US".

    Returns:
        Dict[str, str]: The reshaped and converted properties in OSM's flat str:str schema.
    """
    bad_tags = ["version", "theme", "type", "address_levels"]
    prop = AddressProps(**props)

    obj_dict = prop.model_dump(exclude_none=True, by_alias=True)

    if obj_dict["address_levels"] and len(obj_dict["address_levels"]) > 0:
        if style == "US":
            obj_dict["addr:state"] = str(obj_dict["address_levels"][0]["value"])

    for tag in bad_tags:
        obj_dict.pop(tag, None)

    return obj_dict
