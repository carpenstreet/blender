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

from typing import Any, Dict, List, Union, Tuple, Optional
from math import radians
import bpy
from bpy.types import Collection, Object, Camera


def gen_camera_name(name: str, i: int = 1) -> str:
    found: Optional[bool] = None
    collection: Optional[Collection] = bpy.data.collections.get("ACON_col_cameras")

    if collection:
        combinedName: str = name + str(i)

        for object in collection.objects:
            if object.name == combinedName:
                found = True
                break

    return gen_camera_name(name, i + 1) if found else name + str(i)


# items should be a global variable due to a bug in EnumProperty
items: List[Tuple[str, str, str]] = []


def add_view_items_from_collection(self, context) -> List[Tuple[str, str, str]]:
    items.clear()
    if collection := bpy.data.collections.get("ACON_col_cameras"):
        for item in collection.objects:
            items.append((item.name, item.name, ""))

    return items


def go_to_custom_camera(self, context) -> None:
    make_sure_camera_exists()
    viewCamera: Camera = context.scene.camera
    targetCamera: Camera = bpy.data.objects[context.scene.ACON_prop.view]
    viewCamera.location[0] = targetCamera.location[0]
    viewCamera.location[1] = targetCamera.location[1]
    viewCamera.location[2] = targetCamera.location[2]
    viewCamera.rotation_mode = targetCamera.rotation_mode
    viewCamera.rotation_euler[0] = targetCamera.rotation_euler[0]
    viewCamera.rotation_euler[1] = targetCamera.rotation_euler[1]
    viewCamera.rotation_euler[2] = targetCamera.rotation_euler[2]
    viewCamera.scale[0] = targetCamera.scale[0]
    viewCamera.scale[1] = targetCamera.scale[1]
    viewCamera.scale[2] = targetCamera.scale[2]
    turn_on_camera_view()


def make_sure_camera_exists() -> None:
    # early out if scene camera exists
    if bpy.context.scene.camera:
        bpy.context.scene.camera.data.show_passepartout = False
        return

    # create camera if View_Camera does not exist
    cam = bpy.data.cameras.new("View_Camera")
    cam.lens = 30
    cam.show_passepartout = False
    obj = bpy.data.objects.new("View_Camera", cam)
    obj.location = (4.7063, 7.6888, 1.9738)
    obj.rotation_euler = (radians(90), radians(0), radians(-212))
    obj.hide_select = True
    bpy.context.scene.collection.objects.link(obj)

    # set context camera
    bpy.context.scene.camera = obj

    # View_Camera 오브젝트 활성화
    bpy.context.view_layer.objects.active = obj


def make_sure_camera_unselectable(self, context) -> None:
    # 씬을 로드할 때 camera 오브젝트들이 선택되지 않도록 설정
    if camera := context.scene.camera:
        camera.hide_select = True


# turn on camera view (set viewport to the current selected camera's view)
def turn_on_camera_view(center_camera: bool = True) -> None:
    make_sure_camera_exists()
    # turn on camera view in the selected context(view pane)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces[0].region_3d.view_perspective = "CAMERA"
                area.spaces[0].lock_camera = True
                if center_camera:
                    override: Dict[str, Any] = {"area": area}
                    bpy.ops.view3d.view_center_camera(override)
                break


def turn_off_camera_view() -> None:
    # turn off camera view in the selected context(view pane)
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            area.spaces[0].region_3d.view_perspective = "PERSP"
            break


def switch_to_rendered_view() -> None:
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.shading.type = "RENDERED"
