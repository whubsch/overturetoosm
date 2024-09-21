"""Write the tags to a wiki formatted table."""

import json
import requests
import re


def get_wikitext(page_title: str = "Overture categories") -> str:
    # Define the API endpoint and parameters
    url = "https://wiki.openstreetmap.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": page_title,
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
    }

    # Send the request to the MediaWiki API
    response = requests.get(url, params=params)
    data = response.json()

    # Extract the page id (keys are page ids)
    page = next(iter(data["query"]["pages"].values()))

    # Get the wikitext content
    wikitext = page["revisions"][0]["slots"]["main"]["*"]

    return wikitext


def main() -> None:
    text = []
    with open("scripts/tags.json", "r", encoding="utf-8") as f:
        tags = json.load(f)

    for k, v in tags.items():
        sec = " ".join([f"{{{{tag|{k1}|{v1}}}}}" for k1, v1 in v.items()])
        text.append(f"|-\n|{k}||{sec}")

    pattern = r"{\| class=\"wikitable\" .*\|}"
    replacement = f'{{| class="wikitable" id="mapping_table"\n!Overture!!OSM\n{"\n".join(text)}\n|}}'

    with open("scripts/wiki.txt", "w+", encoding="utf-8") as f:
        new = re.sub(pattern, replacement, get_wikitext(), flags=re.DOTALL)
        f.write(new)

    print("Done!")


if __name__ == "__main__":
    main()
