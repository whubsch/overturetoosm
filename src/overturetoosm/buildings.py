"""Convert Overture's `buildings` features to OSM tags."""

from .objects import BuildingProps


def process_building(
    props: dict, confidence: float = 0.0, required_license: str | None = "CDLA"
) -> dict[str, str]:
    """Convert Overture's building properties to OSM tags.

    Args:
        props (dict): The feature properties from the Overture GeoJSON.
        confidence (float, optional): The minimum confidence level. Defaults to 0.0.
        required_license (str | None, optional): Required license string that must
            be present in at least one source (e.g., "CDLA"). Features with no
            matching license will raise a LicenseError. If None, no license
            validation is performed. Defaults to "CDLA".

    Returns:
        dict[str, str]: The reshaped and converted properties in OSM's flat
            str:str schema.

    Raises:
        `overturetoosm.objects.ConfidenceError`: Raised if the confidence level is set
            above a feature's confidence.
        `overturetoosm.objects.LicenseError`: Raised if `required_license` is set
            and no sources contain the required license.
    """
    return BuildingProps(**props).to_osm(confidence, required_license)
