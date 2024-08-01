from typing import Dict, Literal
from .objects import AddressProps


def process_address(
    props: dict,
    style: Literal["US"] = "US",
) -> Dict[str, str]:
    """Convert Overture's address properties to OSM tags.

    Args:
        props (dict): The feature properties from the Overture GeoJSON.
        style (str, optional): How to handle the `address_levels` field. Open a pull request or issue to add support for other regions. Defaults to "US".

    Returns:
        Dict[str, str]: The reshaped and converted properties in OSM's flat str:str schema.
    """
    bad_tags = ["version", "theme", "type", "address_levels"]
    print(props)
    prop = AddressProps(**props)
    obj_dict = prop.model_dump(exclude_none=True, by_alias=True)
    if prop.address_levels:
        if style == "US":
            obj_dict["addr:state"] = prop.address_levels[0]["value"]

    for tag in bad_tags:
        obj_dict.pop(tag, None)

    return obj_dict
