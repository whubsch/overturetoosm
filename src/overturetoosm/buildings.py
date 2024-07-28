"""Convert Overture's `buildings` features to OSM tags."""

from typing import Dict
from .utils import source_statement
from .objects import BuildingProps, ConfidenceError


def process_building(
    props: dict,
    confidence: float = 0.0,
) -> Dict[str, str]:
    """Convert Overture's building properties to OSM tags.

    Args:
        props (dict): The feature properties from the Overture GeoJSON.
        confidence (float, optional): The minimum confidence level. Defaults to 0.0.

    Returns:
        Dict[str, str]: The reshaped and converted properties in OSM's flat str:str schema.

    Raises:
        `overturetoosm.objects.ConfidenceError`: Raised if the confidence level is set
            above a feature's confidence.
    """
    new_props = {}
    prop_obj = BuildingProps(**props)
    confidences = [source.confidence for source in prop_obj.sources]
    if any(conf < confidence for conf in confidences):
        raise ConfidenceError(confidence, max(confidences))

    new_props["building"] = prop_obj.class_

    new_props["source"] = source_statement(prop_obj.sources)

    obj_dict = prop_obj.model_dump(exclude_none=True).items()
    new_props.update(
        {
            k.replace("facade", "building")
            .replace("_", ":")
            .replace("color", "colour"): v
            for k, v in obj_dict
            if k.startswith(("roof", "facade"))
        }
    )
    new_props.update({k: v for k, v in obj_dict if k.endswith("height")})

    if prop_obj.is_underground:
        new_props["location"] = "underground"
    if prop_obj.num_floors:
        new_props["building:levels"] = prop_obj.num_floors
    if prop_obj.num_floors_underground:
        new_props["building:levels:underground"] = prop_obj.num_floors_underground
    if prop_obj.min_floor:
        new_props["building:min_level"] = prop_obj.min_floor
    return new_props
