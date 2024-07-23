"""Pydantic models needed throughout the project."""

import pydantic


class Sources(pydantic.BaseModel):
    """Overture sources model."""

    property: str
    dataset: str
    record_id: str | None = None
    confidence: float = pydantic.Field(default=0.0)


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
    ):
        """@private"""
        self.category = category
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"{self.message} {{category={self.category}}}"


class BuildingProps(pydantic.BaseModel):
    """Overture building properties."""

    version: int
    class_: str = pydantic.Field(alias="class")
    subtype: str
    sources: list[Sources]
    height: float | None = None
    is_underground: bool | None = None
    num_floors: int | None = None
    num_floors_underground: int | None = None
    min_height: float | None = None
    min_floor: int | None = None
    facade_color: str | None = None
    facade_material: str | None = None
    roof_material: str | None = None
    roof_shape: str | None = None
    roof_direction: str | None = None
    roof_orientation: str | None = None
    roof_color: str | None = None
    roof_height: float | None = None
