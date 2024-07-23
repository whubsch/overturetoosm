"""Convert Overture's `buildings` features to OSM tags."""

from .objects import BuildingProps, ConfidenceError


def process_props(
    props: dict,
    confidence: float = 0.0,
) -> dict[str, str]:
    """Convert Overture's properties properties to OSM tags."""
    new_props = {}
    prop_obj = BuildingProps(**props)
    confidences = [source.confidence for source in prop_obj.sources]
    if any(conf < confidence for conf in confidences):
        raise ConfidenceError(confidence, max(confidences))

    if prop_obj.class_:
        new_props["building"] = prop_obj.class_

    if prop_obj.sources:
        new_props["source"] = (
            ", ".join(i.dataset.strip(", ") for i in prop_obj.sources)
            + " via overturetoosm"
        )

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