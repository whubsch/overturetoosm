import json
import os


with open("scripts/tags.json", "r+", encoding="utf-8") as f:
    tags = json.load(f)

tags_filled = {k: v for k, v in tags.items() if v}

with open("src/overture_to_osm/resources.py", "w+", encoding="utf-8") as f:
    f.write(f"tags = {json.dumps(tags_filled, indent=4)}\n")
