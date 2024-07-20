from typing import Any, Optional
from resources import tags
import pydantic

bad_tags = ["id", "version", "update_time", "sources", "user", "uid"]


class Sources(pydantic.BaseModel):
    property: str
    dataset: str
    record_id: str
    confidence: float | None


class Names(pydantic.BaseModel):
    primary: str
    common: str | None
    rules: str | None


class Addresses(pydantic.BaseModel):
    freeform: str | None
    locality: str | None
    postcode: str | None
    region: str | None
    country: str | None


class Categories(pydantic.BaseModel):
    main: str
    alternate: list[str] | None


class Brand(pydantic.BaseModel):
    wikidata: str | None
    names: Names


class PlaceProps(pydantic.BaseModel):
    id: str
    version: int
    update_time: str
    sources: list[Sources]
    names: Names
    brand: Brand | None = None
    categories: Categories | None = None
    confidence: float
    websites: list[str] | None = None
    socials: list[str] | None = None
    phones: list[str] | None = None
    addresses: list[Addresses]


def process_geojson_props(
    props: dict,
    region_tag: str = "addr:state",
    confidence: float = 0.0,
) -> dict[str, str]:
    """Process GeoJSON properties from Overture."""
    new_props = {}
    prop_obj = PlaceProps(**props)
    if prop_obj.confidence < confidence:
        return {}

    try:
        if prop_obj.categories:
            prim = tags.get(prop_obj.categories.main)
            if prim:
                new_props |= prim
            else:
                print(prop_obj.categories.main)
    except KeyError:
        pass

    try:
        name = prop_obj.names.primary
        if name:
            new_props |= {"name": name}
    except KeyError:
        pass

    if "phones" in props:
        new_props["phone"] = prop_obj.phones[0]

    if "websites" in props:
        if prop_obj.websites:
            new_props["website"] = prop_obj.websites[0]

    if "addresses" in props:
        add = props["addresses"][0]
        if "freeform" in add:
            new_props["addr:street_address"] = prop_obj.addresses[0].freeform
        if "country" in add:
            new_props["addr:country"] = prop_obj.addresses[0].country
        if "postcode" in add:
            new_props["addr:postcode"] = prop_obj.addresses[0].postcode
        if "region" in add:
            new_props[region_tag] = prop_obj.addresses[0].region

    if "sources" in props:
        new_props["source"] = (
            ", ".join({i["dataset"] for i in props["sources"]}) + " via overture_to_osm"
        )

    if "brand" in props:
        if prop_obj.brand:
            new_props["brand"] = prop_obj.brand.names.primary
            new_props["brand:wikidata"] = prop_obj.brand.wikidata

    print(new_props)
    return new_props
