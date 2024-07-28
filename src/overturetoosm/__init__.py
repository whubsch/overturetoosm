"""`overturetoosm` is a Python package to convert objects tagged in the 
Overture schema for use in OSM. Only Overture's `places` and `buildings` 
layers are currently supported.
"""

# SPDX-FileCopyrightText: 2024-present Will <wahubsch@gmail.com>
#
# SPDX-License-Identifier: MIT

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
