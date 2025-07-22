"""Convert Overture's `addresses` features to OSM tags."""

from .objects import AddressProps


def process_address(props: dict, style: str = "US") -> dict[str, str]:
    """Convert Overture's address properties to OSM tags.

    Args:
        props (dict): The feature properties from the Overture GeoJSON.
        style (str, optional): How to handle the `address_levels` field. Open
            a pull request or issue to add support for other regions. Defaults to "US".

    Returns:
        dict[str, str]: The reshaped and converted properties in OSM's flat
            str:str schema.
    """
    return AddressProps(**props).to_osm(style)
