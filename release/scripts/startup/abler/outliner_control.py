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


import contextlib
bl_info = {
    "name": "Outliner Panel",
    "description": "",
    "author": "sdk@acon3d.com",
    "version": (0, 0, 1),
    "blender": (3, 00, 0),
    "location": "",
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "ACON3D",
}
import bpy


class Acon3dOutlinerPanel(bpy.types.Panel):
    bl_idname = "ACON3D_PT_outliner"
    bl_label = "Outliner"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def recursive_collection(self, layout, collection, indent=0):
        indent_basis = "   "
        for child in collection.children:
            row = layout.row()
            row.alignment = "LEFT"
            row.label(text=indent_basis * indent + child.name, icon="GROUP")
            self.recursive_collection(layout, child, indent=indent + 1)
        with contextlib.suppress(AttributeError):
            for child in collection.objects:
                row = layout.row()
                row.alignment = "LEFT"
                row.label(text=indent_basis * indent + child.name, icon="OBJECT_DATA")
                self.recursive_collection(layout, child, indent=indent + 1)

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="OUTLINER")

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        self.recursive_collection(box, bpy.context.scene.collection)


classes = (
    Acon3dOutlinerPanel,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
