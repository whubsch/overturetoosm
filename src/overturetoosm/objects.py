"""Pydantic models needed throughout the project."""

from typing import Dict, List, Optional
import pydantic


class Sources(pydantic.BaseModel):
    """Overture sources model."""

    property: str
    dataset: str
    record_id: Optional[str] = None
    confidence: float = pydantic.Field(default=0.0)


class Names(pydantic.BaseModel):
    """Overture names model."""

    primary: str
    common: Optional[Dict[str, str]]
    rules: Optional[List[Dict[str, str]]]


class Addresses(pydantic.BaseModel):
    """Overture addresses model."""

    freeform: Optional[str]
    locality: Optional[str]
    postcode: Optional[str]
    region: Optional[str]
    country: Optional[str]


class Categories(pydantic.BaseModel):
    """Overture categories model."""

    main: str
    alternate: Optional[List[str]]


class Brand(pydantic.BaseModel):
    """Overture brand model."""

    wikidata: Optional[str]
    names: Names


class PlaceProps(pydantic.BaseModel):
    """Overture properties model.

    Use this model directly if you want to manipulate the `place` properties yourself.
    """

    id: str
    version: int
    update_time: str
    sources: List[Sources]
    names: Names
    brand: Optional[Brand] = None
    categories: Optional[Categories] = None
    confidence: float = pydantic.Field(ge=0.0, le=1.0)
    websites: Optional[List[str]] = None
    socials: Optional[List[str]] = None
    phones: Optional[List[str]] = None
    addresses: List[Addresses]


class ConfidenceError(Exception):
    """
    Confidence error exception.

    This exception is raised when the confidence level of an item is below the
    user-defined level. It contains the original confidence level and the confidence
    level of the item.

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
    ) -> None:
        """@private"""
        self.confidence_level = confidence_level
        self.confidence_item = confidence_item
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        """@private"""
        conf = f"confidence_level={self.confidence_level}, confidence_item={self.confidence_item}"
        return f"""{self.message} {conf}"""


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
    ) -> None:
        """@private"""
        self.category = category
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        """@private"""
        return f"{self.message} {{category={self.category}}}"


class BuildingProps(pydantic.BaseModel):
    """Overture building properties.

    Use this model directly if you want to manipulate the `building` properties yourself.
    """

    version: int
    class_: str = pydantic.Field(alias="class")
    subtype: str
    sources: List[Sources]
    height: Optional[float] = None
    is_underground: Optional[bool] = None
    num_floors: Optional[int] = None
    num_floors_underground: Optional[int] = None
    min_height: Optional[float] = None
    min_floor: Optional[int] = None
    facade_color: Optional[str] = None
    facade_material: Optional[str] = None
    roof_material: Optional[str] = None
    roof_shape: Optional[str] = None
    roof_direction: Optional[str] = None
    roof_orientation: Optional[str] = None
    roof_color: Optional[str] = None
    roof_height: Optional[float] = None
