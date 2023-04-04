# <pep8-80 compliant>
__author__ = "Martijn Berger"
__license__ = "GPL"

"""
This program is free software; you can redistribute it and
or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 3
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see http://www.gnu.org/licenses
"""

import bpy
from .lib.import_skp import ImportSKPPro, ImportSKPProPanel, ImportProOperator, ImportSKPProOperator, ImportSKPProOperator, NewGetSKPProgress, NewCloseSKPProgress
from .lib.sketchup_addon_prefs import NewSketchupAddonPreferences

bl_info = {
    "name": "ACON3D SketchUp Converter PRO",
    "author": "Martijn Berger, Sanjay Mehta, Arindam Mondal, Seonggu Kim",
    "version": (0, 21),
    "blender": (2, 93, 0),
    "description": "Import of native SketchUp (.skp) files",
    "wiki_url": "https://github.com/martijnberger/pyslapi",
    "doc_url": "https://github.com/arindam-m/pyslapi/wiki",
    "tracker_url": "https://github.com/arindam-m/pyslapi/wiki/Bug-Report",
    "category": "ACON3D",
}

classes = (
    ImportSKPPro,
    ImportProOperator,
    ImportSKPProPanel,
    ImportSKPProOperator,
    NewGetSKPProgress,
    NewCloseSKPProgress,
    NewSketchupAddonPreferences,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()
