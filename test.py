from collections import Counter
import json
from process import process_geojson_props
from resources import tags

with open("arlington_over1.geojson", "r", encoding="utf-8") as f:
    contents: dict = json.load(f)
    count = []

    for each in contents["features"]:
        each["properties"] = process_geojson_props(each["properties"], confidence=0.8)
        # try:
        #     prim = tags.get(each["properties"]["categories"]["main"])
        #     if not prim:
        #         # print(each["properties"]["categories"]["main"])
        #         count.append(each["properties"]["categories"]["main"])

        # except KeyError:
        #     pass

    contents["features"] = [each for each in contents["features"] if each["properties"]]

    with open("arlington_over2.geojson", "w+", encoding="utf-8") as f:
        json.dump(contents, f, indent=4)

    # print(len(count), len(contents["features"]))
    # print(Counter(count))
