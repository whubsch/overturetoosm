"""Convert Overture's `addresses` features to OSM tags."""

from .objects import AddressProps


def process_address(
    props: dict, style: str = "US", required_license: str | None = "CDLA"
) -> dict[str, str]:
    """Convert Overture's address properties to OSM tags.

    Args:
        props (dict): The feature properties from the Overture GeoJSON.
        style (str, optional): How to handle the `address_levels` field. Open
            a pull request or issue to add support for other regions. Defaults to "US".
        required_license (str | None, optional): Required license string that must
            be present in at least one source (e.g., "CDLA"). Features with no
            matching license will raise a LicenseError. If None, no license
            validation is performed. Defaults to "CDLA".

    Returns:
        dict[str, str]: The reshaped and converted properties in OSM's flat
            str:str schema.

    Raises:
        `overturetoosm.objects.LicenseError`: Raised if `required_license` is set
            and no sources contain the required license.
    """
    return AddressProps(**props).to_osm(style, required_license)
