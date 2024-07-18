from collections import Counter
import json
from process import process_geojson_feature
from resources import tags

with open("arlington_over.geojson", "r", encoding="utf-8") as f:
    contents: dict = json.load(f)
    count = []

    for each in contents["features"]:
        # process_geojson_feature(each)
        try:
            prim = tags.get(each["properties"]["categories"]["main"])
            if not prim:
                # print(each["properties"]["categories"]["main"])
                count.append(each["properties"]["categories"]["main"])

        except KeyError:
            pass

    print(Counter(count))
