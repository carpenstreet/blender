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


class SCENE_UL_List(bpy.types.UIList):
    def __init__(self):
        super().__init__()
        self.use_filter_sort_reverse = True

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row()
            row.prop(item, "name", text="", emboss=False)


class CreateSceneOperator(bpy.types.Operator):
    """Create a new scene with current viewport"""

    bl_idname = "acon3d.create_scene"
    bl_label = "Add New Scene"
    bl_translation_context = "abler"
    bl_options = {"REGISTER", "UNDO"}

    name: bpy.props.StringProperty(name="Name", description="Write scene name")

    preset: bpy.props.EnumProperty(
        name="Preset",
        description="Select scene preset",
        items=[
            ("None", "Use Current Scene Settings", ""),
            ("Default", "Default", ""),
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

        prop = context.window_manager.ACON_prop
        # self.name이 씬 이름 목록에 있을 땐 번호 추가
        while self.name in prop.scene_col:
            scene_name = self.name.rsplit(".")[0]
            post_fix = self.name.rsplit(".")[-1]
            if post_fix.isnumeric():
                post_fix = str(int(post_fix) + 1).zfill(3)
            else:
                post_fix = "001"
            self.name = scene_name + "." + post_fix

        old_scene = context.scene
        new_scene = scenes.create_scene(old_scene, self.preset, self.name)
        prop.scene = new_scene.name

        # scene_col 추가
        new_scene_col = prop.scene_col.add()
        new_scene_col.name = new_scene.name
        new_scene_col.index = len(prop.scene_col) - 1

        prop.active_scene_index = new_scene_col.index

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
    bl_translation_context = "abler"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        return len(bpy.data.scenes) > 1

    def execute(self, context):
        prop = context.window_manager.ACON_prop

        scene = prop.scene_col[prop.active_scene_index]
        scenesList = [*bpy.data.scenes]

        # bpy.data.scenes은 이름순으로 자동정렬돼 생성순인 scene_col와 순서가 달라
        # scene.name을 대조해 삭제
        for item in scenesList:
            if item.name == scene.name:
                scene = item

        i = scenesList.index(scene)
        scenesList.remove(scene)
        length = len(scenesList)
        nextScene = scenesList[min(i, length - 1)]

        # Updating `scene` value invoke `load_scene` function which compares current
        # scene and target scene. So it should happen before removing scene.
        prop.scene = nextScene.name

        bpy.data.scenes.remove(scene)
        prop.scene_col.remove(prop.active_scene_index)

        # active_scene_index 처리
        if prop.active_scene_index == 0:
            # 맨 아래 씬 삭제 시 가장 위의 씬으로 이동
            next_scene_index = len(prop.scene_col) - 1
        else:
            # 씬을 삭제 시 바로 다음 순서의 씬(생성순 내림차순)으로 전환
            next_scene_index = prop.active_scene_index - 1
        prop.active_scene_index = next_scene_index

        return {"FINISHED"}


class Acon3dScenesPanel(bpy.types.Panel):
    bl_idname = "ACON3D_PT_scenes"
    bl_label = "Scenes"
    bl_category = "Scene"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    # 블렌더에선 bl_order가 앞이어도 bl_options = {"HIDE_HEADER"}인 패널부터 먼저 배치돼 기획안과 다르게 나옴
    # camera -> scene -> style 순으로 배치하도록
    # Acon3dCameraControlPanel의 bl_order 값과 맞춰 하위 패널로 인식하게끔 만듦
    bl_order = 10
    bl_translation_context = "abler"

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="SCENE_DATA")

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        prop = context.window_manager.ACON_prop

        # SCENE_UL_List을 그려주는 부분
        col = row.column()
        col.template_list(
            "SCENE_UL_List", "", prop, "scene_col", prop, "active_scene_index"
        )
        col = row.column(align=True)
        col.operator("acon3d.create_scene", text="", icon="ADD")
        col.operator("acon3d.delete_scene", text="", icon="REMOVE")


classes = (
    CreateSceneOperator,
    DeleteSceneOperator,
    Acon3dScenesPanel,
    SCENE_UL_List,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
