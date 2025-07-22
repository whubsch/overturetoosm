"""Pydantic models needed throughout the project."""

# ruff: noqa: D415

from enum import Enum

try:
    from typing import Annotated
except ImportError:
    from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator

from .resources import places_tags


class OvertureBaseModel(BaseModel):
    """Base model for Overture features."""

    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=0)
    theme: str | None = None
    type: str | None = None
    id: str | None = Field(None, pattern=r"^(\S.*)?\S$")


class Wikidata(RootModel):
    """Model for transportation segment wikidata."""

    root: str = Field(description="Wikidata ID.", pattern=r"^Q\d+")


class Sources(BaseModel):
    """Overture sources model."""

    property: str
    dataset: str
    record_id: str | None = None
    confidence: float | None = Field(ge=0.0, le=1.0)
    update_time: str | None = None

    @field_validator("confidence")
    @classmethod
    def set_default_if_none(cls, v: float) -> float:
        """@private"""
        return v if v is not None else 0.0

    def get_osm_link(self) -> str | None:
        """Return the OSM link for the source."""
        if (
            self.record_id
            and self.record_id.startswith(("n", "w", "r"))
            and self.dataset == "OpenStreetMap"
        ):
            type_dict = {"n": "node", "w": "way", "r": "relation"}
            return f"https://www.openstreetmap.org/{type_dict[self.record_id[0]]}/{self.record_id[1:]}"


class RulesVariant(str, Enum):
    """Overture name rules variant model."""

    alternate = "alternate"
    common = "common"
    official = "official"
    short = "short"


class Between(RootModel):
    """Model for transportation segment between."""

    root: Annotated[list, Field(float, min_length=2, max_length=2)]


class Rules(BaseModel):
    """Overture name rules model."""

    variant: RulesVariant
    language: str | None = None
    value: str
    between: Between | None = None
    side: str | None = None


class Names(BaseModel):
    """Overture names model."""

    primary: str
    common: dict[str, str] | None
    rules: list[Rules] | None


class PlaceAddress(BaseModel):
    """Overture addresses model."""

    freeform: str | None
    locality: str | None
    postcode: str | None
    region: str | None
    country: str | None = Field(pattern=r"^[A-Z]{2}$")


class Categories(BaseModel):
    """Overture categories model."""

    main: str
    alternate: list[str] | None


class Brand(BaseModel):
    """Overture brand model."""

    wikidata: Wikidata | None = None
    names: Names

    def to_osm(self) -> dict[str, str]:
        """Convert brand properties to OSM tags."""
        osm = {"brand": self.names.primary}
        if self.wikidata:
            osm.update({"brand:wikidata": str(self.wikidata.root)})
        return osm


class Socials(RootModel):
    """Overture socials model."""

    root: list[str]

    def to_osm(self) -> dict[str, str]:
        """Convert socials properties to OSM tags."""
        new_props = {}
        for social in self.root:
            if "facebook" in social:
                new_props["contact:facebook"] = social
            elif "twitter" in str(social):
                new_props["contact:twitter"] = social
        return new_props


class PlaceProps(OvertureBaseModel):
    """Overture properties model.

    Use this model directly if you want to manipulate the `place` properties yourself.
    """

    update_time: str
    sources: list[Sources]
    names: Names
    brand: Brand | None = None
    categories: Categories | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    websites: list[str] | None = None
    socials: Socials | None = None
    emails: list[str] | None = None
    phones: list[str] | None = None
    addresses: list[PlaceAddress]

    def to_osm(
        self, confidence: float, region_tag: str, unmatched: str
    ) -> dict[str, str]:
        """Convert Overture's place properties to OSM tags.

        Used internally by the `overturetoosm.process_place` function.
        """
        new_props = {}
        if self.confidence < confidence:
            raise ConfidenceError(confidence, self.confidence)

        if self.categories:
            prim = places_tags.get(self.categories.main)
            if prim:
                new_props = {**new_props, **prim}
            elif unmatched == "force":
                new_props["type"] = self.categories.main
            elif unmatched == "error":
                raise UnmatchedError(self.categories.main)

        if self.names.primary:
            new_props["name"] = self.names.primary

        if self.phones is not None:
            new_props["phone"] = self.phones[0]

        if self.websites is not None and self.websites[0]:
            new_props["website"] = str(self.websites[0])

        if add := self.addresses[0]:
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

        if self.sources:
            new_props["source"] = source_statement(self.sources)

        if self.socials:
            new_props.update(self.socials.to_osm())

        if self.brand:
            new_props.update(self.brand.to_osm())

        return new_props


class ConfidenceError(Exception):
    """Confidence error exception.

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
        lev = f"confidence_level={self.confidence_level}"
        item = f"confidence_item={self.confidence_item}"
        return f"""{self.message} {lev}, {item}"""


class UnmatchedError(Exception):
    """Unmatched category error.

    This exception is raised when an item's Overture category does not have a
    corresponding OSM definition. Edit
    [the OSM Wiki page](https://wiki.openstreetmap.org/wiki/Overture_categories)
    to add a definition to this category.

    Attributes:
        category (str): The Overture category that is unmatched.
        message (str): The error message.
    """

    def __init__(
        self, category: str, message: str = "Overture category is unmatched."
    ) -> None:
        """@private"""
        self.category = category
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        """@private"""
        return f"{self.message} {{category={self.category}}}"


class BuildingProps(OvertureBaseModel):
    """Overture building properties.

    Use this model if you want to manipulate the `building` properties yourself.
    """

    has_parts: bool
    sources: list[Sources]
    class_: str | None = Field(alias="class", default=None)
    subtype: str | None = None
    names: Names | None = None
    level: int | None = None
    height: float | None = None
    is_underground: bool | None = None
    num_floors: int | None = Field(serialization_alias="building:levels", default=None)
    num_floors_underground: int | None = Field(
        serialization_alias="building:levels:underground", default=None
    )
    min_height: float | None = None
    min_floor: int | None = Field(
        serialization_alias="building:min_level", default=None
    )
    facade_color: str | None = Field(
        serialization_alias="building:colour", default=None
    )
    facade_material: str | None = Field(
        serialization_alias="building:material", default=None
    )
    roof_material: str | None = Field(serialization_alias="roof:material", default=None)
    roof_shape: str | None = Field(serialization_alias="roof:shape", default=None)
    roof_direction: str | None = Field(
        serialization_alias="roof:direction", default=None
    )
    roof_orientation: str | None = Field(
        serialization_alias="roof:orientation", default=None
    )
    roof_color: str | None = Field(serialization_alias="roof:colour", default=None)
    roof_height: float | None = Field(serialization_alias="roof:height", default=None)

    def to_osm(self, confidence: float) -> dict[str, str]:
        """Convert properties to OSM tags.

        Used internally by`overturetoosm.process_building` function.
        """
        new_props = {}
        confidences = {source.confidence for source in self.sources}
        if any(conf and conf < confidence for conf in confidences):
            raise ConfidenceError(confidence, max({i for i in confidences if i}))

        new_props["building"] = self.class_ if self.class_ else "yes"

        new_props["source"] = source_statement(self.sources)

        prop_obj = self.model_dump(exclude_none=True, by_alias=True).items()
        new_props.update(
            {k: v for k, v in prop_obj if k.startswith(("roof", "building"))}
        )
        new_props.update({k: round(v, 2) for k, v in prop_obj if k.endswith("height")})

        if self.is_underground:
            new_props["location"] = "underground"
        if self.names:
            new_props["name"] = self.names.primary
        return new_props


class AddressLevel(BaseModel):
    """Overture address level model."""

    value: str


class AddressProps(OvertureBaseModel):
    """Overture address properties.

    Use this model directly if you want to manipulate the `address` properties yourself.
    """

    number: str | None = Field(serialization_alias="addr:housenumber")
    street: str | None = Field(serialization_alias="addr:street")
    postcode: str | None = Field(serialization_alias="addr:postcode")
    country: str | None = Field(serialization_alias="addr:country")
    address_levels: (
        None | (Annotated[list[AddressLevel], Field(min_length=1, max_length=5)])
    ) = Field(default_factory=list)
    sources: list[Sources]

    def to_osm(self, style: str) -> dict[str, str]:
        """Convert properties to OSM tags.

        Used internally by `overturetoosm.process_address`.
        """
        obj_dict = {
            k: v
            for k, v in self.model_dump(exclude_none=True, by_alias=True).items()
            if k.startswith("addr:")
        }
        obj_dict["source"] = source_statement(self.sources)

        if self.address_levels and len(self.address_levels) > 0 and style == "US":
            obj_dict["addr:state"] = str(self.address_levels[0].value)

        return obj_dict


def source_statement(source: list[Sources]) -> str:
    """Return a source statement from a list of sources."""
    return (
        ", ".join(sorted({i.dataset.strip(", ") for i in source}))
        + " via overturetoosm"
    )
