import json

with open("scripts/tags.json", "r+", encoding="utf-8") as f:
    tags = json.load(f)

tags_filled = {k: v for k, v in tags.items() if v}

with open("src/overturetoosm/resources.py", "w+", encoding="utf-8") as f:
    f.write(
        f'''"""A mapping of Overture tags to OSM tags."""

tags: dict[str, dict[str, str]] = {json.dumps(tags_filled, indent=4)}
"""dict[str, dict[str, str]]: A mapping of Overture to OSM tags, 
excluding blank values. This is downstream from the `scripts/tag.json` 
file."""
'''
    )
