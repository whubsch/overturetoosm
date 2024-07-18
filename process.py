from resources import tags

bad_tags = ["id", "version", "update_time", "sources", "user", "uid"]


def process_geojson_feature(
    feature: dict[str, str | dict | list],
    region_tag: str = "addr:state",
    confidence: float = 0.0,
) -> None:
    new_props = {}
    props: dict = feature["properties"]

    try:
        prim = tags.get(props["categories"]["main"])
        if prim:
            new_props |= prim
        else:
            print(props["categories"]["main"])
    except KeyError:
        pass

    try:
        name = props["names"]["primary"]
        if name:
            new_props |= {"name": name}
    except KeyError:
        pass

    if "phones" in props:
        new_props["phone"] = props["phones"][0]

    if "websites" in props:
        new_props["website"] = props["websites"][0]

    if "addresses" in props:
        add = props["addresses"][0]
        if "freeform" in add:
            new_props["addr:street_address"] = add["freeform"]
        if "country" in add:
            new_props["addr:country"] = add["country"]
        if "postcode" in add:
            new_props["addr:postcode"] = add["postcode"]
        if "region" in add:
            new_props[region_tag] = add["region"]

    # print(new_props)
