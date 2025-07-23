import json
import logging
import re

import requests
from bs4 import BeautifulSoup


def equals_to_dict(pairs: list[str]) -> dict[str, str]:
    """Convert a string in the format "key=value" into a dictionary."""
    return {
        key.strip(): value.strip(" \n")
        for key, value in (pair.split("=") for pair in pairs)
    }


def main() -> None:
    """Parse the OSM wiki and return a mapping of Overture categories to OSM tags."""
    tag_mapping = parse_wiki()

    print("Writing tags to scripts/tags.json...")
    with open("scripts/tags.json", mode="w", encoding="utf-8") as f:
        f.write(json.dumps(tag_mapping, indent=4))


def parse_wiki() -> dict:
    """Parse the OSM wiki and return a mapping of Overture categories to OSM tags."""
    table = {}
    print("Getting tags from OSM wiki...")
    data = requests.get(
        "https://wiki.openstreetmap.org/w/api.php",
        {"action": "parse", "page": "Overture_categories", "format": "json"},
        timeout=10,
    ).json()
    soup = BeautifulSoup(data["parse"]["text"]["*"], "html.parser")
    print("Parsing tags from OSM wiki...")
    a = soup.find("table")
    if a:
        for row in list(a.find_all("tr")):
            columns = row.find_all("td")
            if len(columns) != 2:
                continue

            overture = columns[0]
            overture_tag = ""
            if overture:
                overture_tag = overture.text

            osm = columns[1]
            osm_tags = {}

            if osm and osm.text not in ["", "\n"]:
                try:
                    osm_tags = equals_to_dict(
                        [i for i in osm.text.split(" ") if not i.endswith("*")]
                    )
                except ValueError:
                    print(f"Failed to parse '{osm.text}' from '{overture_tag}'")
                    continue

            if overture_tag:
                table[overture_tag] = osm_tags

    return table


def parse_tags(wiki_str: str) -> dict:
    """Parse OSM tags from the wiki."""
    tags = {}
    print(wiki_str)
    for tag in wiki_str.split(" and "):
        if m := re.match(r"^\s*([-_:\w]+)=([-_:\w]+)\s*$", tag):
            tags[m.group(1)] = m.group(2)
        else:
            logging.error(f"Failed to parse '{tag}' from '{wiki_str}'")

    return tags


if __name__ == "__main__":
    main()
