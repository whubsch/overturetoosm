import json
import re

with open("scripts/tags.json", "r+", encoding="utf-8") as f:
    tags = json.load(f)

tags_filled = {k: v for k, v in tags.items() if v}

new_dict_str = json.dumps(tags_filled, indent=4).replace(":", ": ")
pattern = r"places_tags: dict\[str, dict\[str, str\]\]\s*=\s*\{.*\}"
replacement = f"places_tags: dict[str, dict[str, str]] = {new_dict_str}"

with open("src/overturetoosm/resources.py", "r", encoding="utf-8") as f:
    contents = f.read()

replace = re.sub(pattern, replacement, contents, flags=re.DOTALL)

with open("src/overturetoosm/resources.py", "w+", encoding="utf-8") as f:
    f.write(replace)

print("Done!")
