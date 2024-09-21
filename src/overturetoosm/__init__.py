r"""Convert Overture's `places`, `buildings`, and `addresses` features to OSM tags.

`overturetoosm` is a Python package to convert objects tagged in the
Overture schema for use in OSM. Only Overture's `places`, `buildings`,
and `addresses` layers are currently supported.

Links:
* [Project GitHub](https://github.com/whubsch/overturetoosm)
* [Documentation](https://whubsch.github.io/overturetoosm/)
* [PyPI](https://pypi.org/project/overturetoosm/)

The package also allows you to use the module directly from the command line.
With the `overturemaps` Python package installed, you can download and convert
Overture data to OSM in two lines of code.

```bash
$ python -m overturemaps download --bbox=-71.068,42.353,-71.058,42.363 \\
  -f geojson --type=place -o boston.geojson
$ python -m overturetoosm place -i boston.geojson --in-place --confidence 0.9
```
"""

from . import addresses, buildings, objects, places, resources, segments, utils
from .addresses import process_address
from .buildings import process_building
from .places import process_place
from .utils import process_geojson

__all__ = [
    "process_place",
    "process_building",
    "process_address",
    "process_geojson",
    "places",
    "buildings",
    "addresses",
    "objects",
    "segments",
    "utils",
    "resources",
]
