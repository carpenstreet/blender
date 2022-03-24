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
    "author": "youjin@acon3d.com",
    "version": (0, 0, 1),
    "blender": (2, 93, 0),
    "location": "",
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "ACON3D",
}


import os
import bpy
from bpy_extras.io_utils import ImportHelper
from .lib.materials import materials_setup
from .lib.tracker import tracker


class ImportFBXOperator(bpy.types.Operator, ImportHelper):
    """Import FBX file according to the current settings"""

    bl_idname = "acon3d.import_fbx"
    bl_label = "Import FBX"
    bl_translation_context = "*"

    filter_glob: bpy.props.StringProperty(default="*.fbx", options={"HIDDEN"})

    def execute(self, context):

        for obj in bpy.data.objects:
            obj.select_set(False)

        FILEPATH = self.filepath

        filename = os.path.basename(FILEPATH)
        col_imported = bpy.data.collections.new("[FBX] " + filename.replace(".fbx", ""))

        col_layers = bpy.data.collections.get("Layers")
        if not col_layers:
            col_layers = bpy.data.collections.new("Layers")
            context.scene.collection.children.link(col_layers)

        bpy.ops.import_scene.fbx(filepath=FILEPATH)
        for obj in bpy.context.selected_objects:
            if obj.name in bpy.context.scene.collection.objects:
                bpy.context.scene.collection.objects.unlink(obj)
            for c in bpy.data.collections:
                if obj.name in c.objects:
                    c.objects.unlink(obj)
            col_imported.objects.link(obj)

        # put col_imported in l_exclude
        col_layers.children.link(col_imported)
        added_l_exclude = context.scene.l_exclude.add()
        added_l_exclude.name = col_imported.name
        added_l_exclude.value = True

        # create group
        bpy.ops.acon3d.create_group()
        # apply AconToonStyle
        materials_setup.applyAconToonStyle()

        return {"FINISHED"}


class Acon3dImportExternalFilesPanel(bpy.types.Panel):
    bl_idname = "ACON3D_PT_import_external_files"
    bl_label = "Import External Files"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="IMPORT")

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.scale_y = 1.0
        row.operator("acon3d.import_fbx", text="Import FBX")


classes = (ImportFBXOperator, Acon3dImportExternalFilesPanel)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
