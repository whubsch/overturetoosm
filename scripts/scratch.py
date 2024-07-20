from overture_to_osm.resources import tags

text = []
for k, v in tags.items():
    sec = " ".join([f"{{{{tag|{k1}|{v1}}}}}" for k1, v1 in v.items()])
    text.append(f"|-\n|{k}||{sec}")

with open("wiki.txt", "w+", encoding="utf-8") as f:
    f.write("\n".join(text))
