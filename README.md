# Overture to OSM

![GitHub License](https://img.shields.io/github/license/whubsch/overturetoosm)
![GitHub last commit](https://img.shields.io/github/last-commit/whubsch/overturetoosm)
![PyPI - Version](https://img.shields.io/pypi/v/overturetoosm)
![Pepy Total Downlods](https://img.shields.io/pepy/dt/overturetoosm)

This Python project translates objects from the Overture maps schema to the OpenStreetMap (OSM) tagging scheme. The goal is to provide a seamless way to convert map data from Overture's format to a format that can be utilized within the OSM ecosystem. The package currently only supports Overture's `places`, `buildings`, and `addresses` layers. You can improve the Overture categorization that this package uses by editing [the Overture categories page](https://wiki.openstreetmap.org/wiki/Overture_categories) on the OSM Wiki or submitting a pull request to the [tags.json](https://github.com/whubsch/overturetoosm/blob/main/scripts/tags.json) file.

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

## Docs

The documentation for our package is available online at our [documentation page](https://whubsch.github.io/overturetoosm/index.html). We would greatly appreciate your contributions to help improve the auto-generated docs; please submit any updates or corrections via pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/whubsch/overturetoosm/blob/main/LICENSE.txt) file for details.

## See also

- [Overture Maps](https://docs.overturemaps.org/schema/)
- [OpenStreetMap](https://www.openstreetmap.org/)
- [Overture categories wiki page](https://wiki.openstreetmap.org/wiki/Overture_categories)
