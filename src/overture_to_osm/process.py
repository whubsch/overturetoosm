from typing import Literal
import pydantic

from .resources import tags


def place_props(
    props: dict,
    region_tag: str = "addr:state",
    confidence: float = 0.0,
    unmatched: Literal["error", "force", "ignore"] = "ignore",
) -> dict[str, str]:
    """Convert Overture's properties to OSM tags.

    Args:
        props (dict): The feature properties from the Overture GeoJSON.
        region_tag (str, optional): What tag to convert Overture's `region` tag to.
            Defaults to `addr:state`.
        confidence (float, optional): The minimum confidence level. Defaults to 0.0.
        unmatched (Literal["error", "force", "ignore"], optional): How to handle unmatched Overture categories.
            The "error" option raises an UnmatchedError exception, "force" puts the
            category into the `type` key, and "ignore" only returns other properties.
            Defaults to "ignore".

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
        prim = tags.get(prop_obj.categories.main)
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
            ", ".join({i.dataset for i in prop_obj.sources}) + " via overture_to_osm"
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


def place_geojson(
    geojson: dict,
    region_tag: str = "addr:state",
    confidence: float = 0.0,
    unmatched: Literal["error", "force", "ignore"] = "ignore",
) -> dict:
    """Convert an Overture `place` GeoJSON to one that follows OSM's schema.

    Args:
        geojson (dict): The dictionary representation of the Overture GeoJSON.
        region_tag (str, optional): What tag to convert Overture's `region` tag to.
            Defaults to `addr:state`.
        confidence (float, optional): The minimum confidence level. Defaults to 0.0.
        unmatched (Literal["error", "force", "ignore"], optional): How to handle unmatched Overture categories.
            The "error" option raises an UnmatchedError exception, "force" puts the
            category into the `type` key, and "ignore" only returns other properties.
            Defaults to "ignore".

    Returns:
        dict: The dictionary representation of the GeoJSON that follows OSM's schema.
    """
    new_features = []
    for feature in geojson["features"]:
        try:
            feature["properties"] = place_props(
                feature["properties"], region_tag, confidence, unmatched
            )
            new_features.append(feature)
        except ConfidenceError:
            pass

    geojson["features"] = new_features
    return geojson


class Sources(pydantic.BaseModel):
    """Overture sources model."""

    property: str
    dataset: str
    record_id: str
    confidence: float | None


class Names(pydantic.BaseModel):
    """Overture names model."""

    primary: str
    common: str | None
    rules: str | None


class Addresses(pydantic.BaseModel):
    """Overture addresses model."""

    freeform: str | None
    locality: str | None
    postcode: str | None
    region: str | None
    country: str | None


class Categories(pydantic.BaseModel):
    """Overture categories model."""

    main: str
    alternate: list[str] | None


class Brand(pydantic.BaseModel):
    """Overture brand model."""

    wikidata: str | None
    names: Names


class PlaceProps(pydantic.BaseModel):
    """Overture properties model."""

    id: str
    version: int
    update_time: str
    sources: list[Sources]
    names: Names
    brand: Brand | None = None
    categories: Categories | None = None
    confidence: float = pydantic.Field(ge=0.0, le=1.0)
    websites: list[str] | None = None
    socials: list[str] | None = None
    phones: list[str] | None = None
    addresses: list[Addresses]


class ConfidenceError(Exception):
    """
    Confidence error exception.

    This exception is raised when the confidence level of an item is too low.
    It contains the original confidence level and the confidence level of the item.

    Attributes:
        confidence_level (float): The set confidence level.
        confidence_item (float): The confidence of the item.
        message (str): The error message.
    """

    def __init__(
        self,
        confidence_level: float,
        confidence_item: float,
        message: str = "Confidence in this item is too low.",
    ):
        """@private"""
        self.confidence_level = confidence_level
        self.confidence_item = confidence_item
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"{self.message} {{confidence_level={self.confidence_level}, item={self.confidence_item}}}"


class UnmatchedError(Exception):
    """
    Unmatched category error.

    This exception is raised when an item's Overture category does not have a
    corresponding OSM definition. Edit
    [the OSM Wiki page](https://wiki.openstreetmap.org/wiki/Overture_categories)
    to add a definition to this category.

    Attributes:
        category (str): The Overture category that is unmatched.
        message (str): The error message.
    """

    def __init__(
        self,
        category: str,
        message: str = "Overture category is unmatched.",
    ):
        """@private"""
        self.category = category
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"{self.message} {{category={self.category}}}"
