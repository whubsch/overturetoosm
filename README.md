# Overture to OSM

![GitHub License](https://img.shields.io/github/license/whubsch/overturetoosm)
![GitHub last commit](https://img.shields.io/github/last-commit/whubsch/overturetoosm)
![PyPI - Version](https://img.shields.io/pypi/v/overturetoosm)
![Pepy Total Downlods](https://img.shields.io/pepy/dt/overturetoosm)

This Python project translates objects from the Overture maps schema to the OpenStreetMap (OSM) tagging scheme. The goal is to provide a seamless way to convert map data from Overture's format to a format that can be utilized within the OSM ecosystem. The package currently only supports Overture's `places`, `buildings`, and `addresses` layers. You can improve the Overture categorization that this package uses for the `places` layer by editing [the Overture categories page](https://wiki.openstreetmap.org/wiki/Overture_categories) on the OSM Wiki or submitting a pull request to the [tags.json](https://github.com/whubsch/overturetoosm/blob/main/scripts/tags.json) file.

There is also a Pydantic model for the `transportation` layer's `segment` object via `overturetoosm.segments.SegmentProperties`, but the conversion to OSM tags is not yet supported because of the Overture schema's complexity.

The package also allows you to use the module directly from the command line.
With the `overturemaps` Python package installed, you can download and convert
Overture data to OSM in two lines of code.

```bash
$ python -m overturemaps download --bbox=-71.068,42.353,-71.058,42.363 \\
  -f geojson --type=place -o boston.geojson
$ python -m overturetoosm place -i boston.geojson --in-place --confidence 0.9
```

> [!NOTE]
> Use of this package does not absolve you from following OSM's [import guidelines](https://wiki.openstreetmap.org/wiki/Import/Guidelines).

## Table of Contents

- [Features](#features)
- [Usage](#usage)
- [Docs](#docs)
- [License](#license)

## Features

- Translate Overture map places to OSM tags.
- Handle various map object types, including buildings and points of interest.
- Ensure compatibility with OSM data structures and conventions.

## Usage

This package is meant to work with GeoJSON files containing Overture maps data, including those produced by the [overturemaps](https://pypi.org/project/overturemaps/) Python package.

```console
pip install overturetoosm
```

You will probably for the most part be handling features from a GeoJSON or other file, but for demonstration purposes I'll define it inline:

```python
>>> import overturetoosm
>>> overture = {
        "id": "123",
        "version": 1,
        "update_time": "2022-01-01T00:00:00Z",
        "sources": [
            {
                "property": "property1",
                "dataset": "dataset1",
                "confidence": 0.8,
            }
        ],
        "names": {
            "primary": "Primary Name",
        },
        "categories": {"main": "restaurant"},
        "confidence": 0.8,
        "addresses": [
            {
                "freeform": "123 E Main Blvd",
                "locality": "City",
                "postcode": "12345",
                "region": "CA",
                "country": "US",
            }
        ],
    }
>>> output = overturetoosm.process_place(overture)
{
        "name": "Primary Name",
        "addr:street_address": "123 E Main Blvd",
        "addr:city": "City",
        "addr:postcode": "12345",
        "addr:state": "CA",
        "addr:country": "US",
        "source": "dataset1 via overturetoosm",
        "amenity": "restaurant",
}
```

Note that the `addr:street_address` tag is not suitable for import into OSM, and thus will have to be parsed further. If you are working on `places` in the US, you can automatically parse the `addr:street_address` tag using the [atlus](https://pypi.org/project/atlus/) package, a separate project I've worked on.

```python
>>> import atlus
>>> atlus.get_address(output["addr:street_address"])[0]
{"addr:housenumber": "123", "addr:street": "East Main Boulevard"}
```

## Docs

The documentation for our package is available online at our [documentation page](https://whubsch.github.io/overturetoosm/index.html). We would greatly appreciate your contributions to help improve the auto-generated docs; please submit any updates or corrections via pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/whubsch/overturetoosm/blob/main/LICENSE.txt) file for details.

## See also

- [Overture Maps](https://docs.overturemaps.org/schema/)
- [OpenStreetMap](https://www.openstreetmap.org/)
- [Overture categories wiki page](https://wiki.openstreetmap.org/wiki/Overture_categories)
