"""Write the tags to a wiki formatted table."""

import json


def write_wiki(table: str) -> str:
    """Write the table to a wiki formatted string."""
    return f"""[[Overture Maps|Overture]] categories are described [https://github.com/OvertureMaps/schema/blob/main/task-force-docs/places/overture_categories.csv here], unfortunately there are no descriptions. We can however infer some details from the hierarchy. The following are "root"/"top level tags" in Overture.
* eat_and_drink
* accommodation
* automotive
* arts_and_entertainment
* attractions_and_activities
* active_life
* beauty_and_spa
* education
* financial_service
* private_establishments_and_corporates
* retail
* health_and_medical
* pets
* business_to_business
* public_service_and_government
* religious_organization
* real_estate
* travel
* mass_media
* home_service
* professional_services
* structure_and_geography

== Mapping ==

{{| class="wikitable" id="mapping_table"
!Overture!!OSM
{table}
|}}

[[Category:Overture Maps]]
    """


def main() -> None:
    text = []
    with open("scripts/tags.json", "r", encoding="utf-8") as f:
        tags = json.load(f)

    for k, v in tags.items():
        sec = " ".join([f"{{{{tag|{k1}|{v1}}}}}" for k1, v1 in v.items()])
        text.append(f"|-\n|{k}||{sec}")

    with open("scripts/wiki.txt", "w+", encoding="utf-8") as f:
        f.write(write_wiki("\n".join(text)))


if __name__ == "__main__":
    main()
