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


import bpy
from ..lib import scenes
from ..lib.tracker import tracker
from bpy.types import PropertyGroup
from bpy.props import (
    CollectionProperty,
    IntProperty,
    BoolProperty,
    StringProperty,
    PointerProperty,
)


class CUSTOM_UL_List(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        scene = data
        ob = item
        # print(data, item, active_data, active_propname)

        if self.layout_type in {"DEFAULT", "COMPACT"}:

            layout.prop(ob, "name", text="", emboss=False, icon_value=layout.icon(ob))


class CreateSceneOperator(bpy.types.Operator):
    """Create a new scene with a new preset"""

    bl_idname = "acon3d.create_scene"
    bl_label = "New Scene"
    bl_options = {"REGISTER", "UNDO"}

    name: bpy.props.StringProperty(name="Name")

    preset: bpy.props.EnumProperty(
        name="Preset",
        description="Scene preset",
        items=[
            ("None", "Use Current Scene Settings", ""),
            ("Indoor Daytime", "Indoor Daytime", ""),
            ("Indoor Sunset", "Indoor Sunset", ""),
            ("Indoor Nighttime", "Indoor Nighttime", ""),
            ("Outdoor Daytime", "Outdoor Daytime", ""),
            ("Outdoor Sunset", "Outdoor Sunset", ""),
            ("Outdoor Nighttime", "Outdoor Nighttime", ""),
        ],
    )

    def execute(self, context):
        tracker.scene_add()

        old_scene = context.scene
        new_scene = scenes.create_scene(old_scene, self.preset, self.name)
        context.window_manager.ACON_prop.scene = new_scene.name
        return {"FINISHED"}

    def invoke(self, context, event):
        self.name = scenes.gen_scene_name("ACON_Scene_")
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.separator()
        layout.prop(self, "name")
        layout.prop(self, "preset")
        layout.separator()


class DeleteSceneOperator(bpy.types.Operator):
    """Remove current scene from this file"""

    bl_idname = "acon3d.delete_scene"
    bl_label = "Remove Scene"
    bl_translation_context = "*"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        return len(bpy.data.scenes) > 1

    def execute(self, context):

        scene = context.scene
        scenesList = [*bpy.data.scenes]

        i = scenesList.index(scene)
        scenesList.remove(scene)
        length = len(scenesList)
        nextScene = scenesList[min(i, length - 1)]

        # Updating `scene` value invoke `load_scene` function which compares current
        # scene and target scene. So it should happen before removing scene.
        context.window_manager.ACON_prop.scene = nextScene.name

        bpy.data.scenes.remove(scene)

        # Why set `scene` value again? Because `remove(scene)` occurs funny bug
        # that sets `scene` value to 1 when `nextScene` is the first element of
        # `bpy.data.scenes` collection. This ends up having `scene` value invalid
        # and displaying empty value in the ui panel.
        context.window_manager.ACON_prop.scene = nextScene.name

        return {"FINISHED"}


class Acon3dScenesPanel(bpy.types.Panel):
    bl_idname = "ACON3D_PT_scenes"
    bl_label = "Scenes"
    bl_category = "Scene"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="SCENE_DATA")

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.prop(context.window_manager.ACON_prop, "scene", text="")
        row.operator("acon3d.create_scene", text="", icon="ADD")
        row.operator("acon3d.delete_scene", text="", icon="REMOVE")

        # MATERIAL_UL_List을 그려주는 부분
        # row = layout.row()
        # scene = context.scene
        # obj = context.object
        scn = context.scene
        layout = self.layout
        col = layout.column()
        col.template_list(
            "CUSTOM_UL_List",
            "",
            scn,
            "objects",
            scn,
            "active_object_index",
        )
        # col.template_list(
        #     "CUSTOM_UL_List",
        #     "",
        #     context.window_manager.ACON_prop,
        #     "scene",
        #     context.window_manager.ACON_prop,
        #     "active_object_index",
        # )
        # col.template_list(
        #     "CUSTOM_UL_List",
        #     "",
        #     bpy.data,
        #     "scene",
        #     bpy.data,
        #     "1",
        # )
        scene = context.scene
        col.template_list("CUSTOM_UL_List", "", scene, "my_list", scene, "list_index")


class ListItem(PropertyGroup):
    name: StringProperty(name="Set Name", override={"LIBRARY_OVERRIDABLE"})


classes = (
    CreateSceneOperator,
    DeleteSceneOperator,
    Acon3dScenesPanel,
    CUSTOM_UL_List,
    ListItem,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.Scene.active_object_index = IntProperty()
    bpy.types.WindowManager.active_object_index = IntProperty()
    bpy.types.Scene.my_list = bpy.props.CollectionProperty(type=ListItem)
    bpy.types.Scene.list_index = IntProperty(
        name="Active Selection Set",
        description="Index of the currently active selection set",
        default=0,
        override={"LIBRARY_OVERRIDABLE"},
    )


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
