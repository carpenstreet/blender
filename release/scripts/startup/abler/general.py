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
    "author": "hoie@acon3d.com",
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
from .lib import scenes
from .lib.materials import materials_setup
from .lib.tracker import tracker


class ImportOperator(bpy.types.Operator, ImportHelper):
    """Import file according to the current settings"""

    bl_idname = "acon3d.import_blend"
    bl_label = "Import"
    bl_translation_context = "*"

    filter_glob: bpy.props.StringProperty(default="*.blend", options={"HIDDEN"})

    def execute(self, context):
        tracker.import_blend()

        for obj in bpy.data.objects:
            obj.select_set(False)

        FILEPATH = self.filepath

        col_layers = bpy.data.collections.get("Layers")
        if not col_layers:
            col_layers = bpy.data.collections.new("Layers")
            context.scene.collection.children.link(col_layers)

        with bpy.data.libraries.load(FILEPATH) as (data_from, data_to):
            data_to.collections = data_from.collections
            data_to.objects = list(data_from.objects)

        children_names = {}

        for coll in data_to.collections:
            for child in coll.children.keys():
                children_names[child] = True

        for coll in data_to.collections:

            if "ACON_col" in coll.name:
                data_to.collections.remove(coll)
                break

            found = any(coll.name == child for child in children_names)
            if coll.name == "Layers" or (
                "Layers." in coll.name and len(coll.name) == 10
            ):
                for coll_2 in coll.children:
                    added_l_exclude = context.scene.l_exclude.add()
                    added_l_exclude.name = coll_2.name
                    added_l_exclude.value = True
                    col_layers.children.link(coll_2)

        for obj in data_to.objects:
            if obj.type == "MESH":
                obj.select_set(True)
            else:
                data_to.objects.remove(obj)

        materials_setup.applyAconToonStyle()

        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                ctx = bpy.context.copy()
                ctx["area"] = area
                ctx["region"] = area.regions[-1]
                bpy.ops.view3d.view_selected(ctx)

        return {"FINISHED"}


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


class ToggleToolbarOperator(bpy.types.Operator):
    """Toggle toolbar visibility"""

    bl_idname = "acon3d.context_toggle"
    bl_label = "Toggle Toolbar"
    bl_translation_context = "*"

    def execute(self, context):
        tracker.toggle_toolbar()

        context.scene.render.engine = "BLENDER_EEVEE"
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        value = space.show_region_toolbar
                        space.show_region_toolbar = not value

        return {"FINISHED"}


class FileOpenOperator(bpy.types.Operator, ImportHelper):
    """Open new file"""

    bl_idname = "acon3d.file_open"
    bl_label = "File Open"
    bl_translation_context = "*"

    filter_glob: bpy.props.StringProperty(default="*.blend", options={"HIDDEN"})

    def execute(self, context):
        FILEPATH = self.filepath
        bpy.ops.wm.open_mainfile(filepath=FILEPATH)

        return {"FINISHED"}


class FlyOperator(bpy.types.Operator):
    """Move around the scene using WASD, QE, and mouse like FPS game"""

    bl_idname = "acon3d.fly_mode"
    bl_label = "Fly Mode (shift + `)"
    bl_translation_context = "*"

    def execute(self, context):
        tracker.fly_mode()

        if context.space_data.type == "VIEW_3D":
            bpy.ops.view3d.walk("INVOKE_DEFAULT")

        return {"FINISHED"}


class Acon3dImportPanel(bpy.types.Panel):
    bl_idname = "ACON3D_PT_import"
    bl_label = "General"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="EVENT_A")

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.scale_y = 1.0
        row.operator("acon3d.file_open")
        row.operator("acon3d.import_blend", text="Import")

        layout.separator()
        row = layout.row()
        row.operator("acon3d.import_fbx", text="Import FBX")

        row = layout.row()

        prefs = context.preferences
        view = prefs.view

        row.prop(view, "language")
        row = layout.row()
        row.operator("acon3d.context_toggle")
        row = layout.row()
        row.operator("acon3d.fly_mode")


class ApplyToonStyleOperator(bpy.types.Operator):
    """Apply Toon Style"""

    bl_idname = "acon3d.apply_toon_style"
    bl_label = "Apply Toon Style"
    bl_translation_context = "*"

    def execute(self, context):
        materials_setup.applyAconToonStyle()
        scenes.loadScene(None, None)

        return {"FINISHED"}


classes = (
    Acon3dImportPanel,
    ToggleToolbarOperator,
    ImportOperator,
    ApplyToonStyleOperator,
    FileOpenOperator,
    FlyOperator,
    ImportFBXOperator,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
