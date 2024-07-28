"""`overturetoosm` is a Python package to convert objects tagged in the 
Overture schema for use in OSM. Only Overture's `places` and `buildings` 
layers are currently supported.

Links:
* [Project GitHub](https://github.com/whubsch/overturetoosm)
* [Documentation](https://whubsch.github.io/overturetoosm/)
* [PyPI](https://pypi.org/project/overturetoosm/)
"""

from .places import process_place
from .buildings import process_building
from .utils import process_geojson
from . import places
from . import buildings
from . import objects
from . import utils
from . import resources

__all__ = [
    "process_place",
    "process_building",
    "process_geojson",
    "places",
    "buildings",
    "objects",
    "utils",
    "resources",
]
