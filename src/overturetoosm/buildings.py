"""Convert Overture's `buildings` features to OSM tags."""

from .objects import BuildingProps


def process_building(props: dict, confidence: float = 0.0) -> dict[str, str]:
    """Convert Overture's building properties to OSM tags.

    Args:
        props (dict): The feature properties from the Overture GeoJSON.
        confidence (float, optional): The minimum confidence level. Defaults to 0.0.

    Returns:
        dict[str, str]: The reshaped and converted properties in OSM's flat
            str:str schema.

    Raises:
        `overturetoosm.objects.ConfidenceError`: Raised if the confidence level is set
            above a feature's confidence.
    """
    return BuildingProps(**props).to_osm(confidence)
