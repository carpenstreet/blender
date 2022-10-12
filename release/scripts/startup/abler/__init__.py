# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "ACON3D Panel",
    "description": "",
    "author": "sdk@acon3d.com, hoie@acon3d.com",
    "version": (0, 0, 1),
    "blender": (2, 93, 0),
    "location": "",
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "ACON3D",
}


# Main imports
import bpy
import sys
from types import ModuleType

from . import custom_properties
from .general_tab import general
from .camera_tab import camera_control
from .camera_tab import background_control
from .scene_tab import scene_control
from .scene_tab import layer_control
from .style_tab import styles_control
from .style_tab import object_control
from .export_tab import render_control
from . import pref
from . import operators
from . import warning_modal
from .lib.tracker import tracker

# =========================================================================
# Registration:
# =========================================================================

importedLibrary = [
    custom_properties,
    general,
    camera_control,
    background_control,
    scene_control,
    layer_control,
    styles_control,
    object_control,
    render_control,
    pref,
    operators,
    warning_modal,
]
if "--background" not in sys.argv and "-b" not in sys.argv:
    from . import startup_flow

    importedLibrary.append(startup_flow)


def register():
    for item in importedLibrary:
        if not isinstance(item, ModuleType):
            continue
        try:
            item.register()
        except Exception as e:
            print(f"ABLER: Failed to register {item.__name__}\n" + str(e))


# unregister가 사용되지 않아서 아래와 같이 pass 처리함
def unregister():
    pass


if __name__ == "__main__":
    register()
