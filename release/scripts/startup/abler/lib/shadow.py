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


from typing import Optional
import bpy, math
from bpy.types import Object, Light, Context


def change_sun_rotation(self, context: Context) -> None:
    acon_sun: Optional[Object] = bpy.data.objects.get("ACON_sun")
    if not acon_sun:
        acon_sun = create_ACON_sun()

    prop = context.scene.ACON_prop

    acon_sun.rotation_euler.x = math.radians(90) - prop.sun_rotation_x
    acon_sun.rotation_euler.y = 0
    acon_sun.rotation_euler.z = prop.sun_rotation_z


def toggle_sun(self, context: Context) -> None:
    acon_sun: Optional[Object] = bpy.data.objects.get("ACON_sun")
    if not acon_sun:
        acon_sun = create_ACON_sun()

    prop = context.scene.ACON_prop

    acon_sun.hide_viewport = not prop.toggle_sun
    acon_sun.hide_render = not prop.toggle_sun


def change_sun_strength(self, context: Context) -> None:
    acon_sun: Optional[Object] = bpy.data.objects.get("ACON_sun")
    if not acon_sun:
        acon_sun = create_ACON_sun()

    prop = context.scene.ACON_prop
    if acon_sun.data.type == "SUN":
        acon_sun.data.energy = prop.sun_strength


def toggle_shadow_shading(self, context: Context) -> None:
    prop = context.scene.ACON_prop

    # Shadow
    acon_sun: Optional[Object] = bpy.data.objects.get("ACON_sun")
    if not acon_sun:
        acon_sun = create_ACON_sun()

    if acon_sun.data.type == "SUN":
        acon_sun.data.use_shadow = prop.toggle_shadow_shading

    # Shading
    # obj: Optional[Object] = context.object
    # if obj is None:
    #     return
    #
    # mat: Optional[Material] = obj.active_material
    # if not mat:
    #     return
    #
    # shadingFactorValue: int = int(prop.toggle_shadow_shading)
    # toonNode: Optional[Node] = mat.node_tree.nodes.get("ACON_nodeGroup_combinedToon")
    # if not toonNode:
    #     return
    # toonNode.inputs[4].default_value = shadingFactorValue


def toggle_shadow(self, context: Context) -> None:
    acon_sun: Optional[Object] = bpy.data.objects.get("ACON_sun")
    if not acon_sun:
        acon_sun = create_ACON_sun()

    prop = context.scene.ACON_prop
    if acon_sun.data.type == "SUN":
        acon_sun.data.use_shadow = prop.toggle_shadow


def setup_clear_shadow():
    bpy.context.scene.eevee.shadow_cube_size = "4096"
    bpy.context.scene.eevee.shadow_cascade_size = "4096"
    bpy.context.scene.eevee.use_soft_shadows = True

    acon_sun: Optional[Object] = bpy.data.objects.get("ACON_sun")

    if not acon_sun:
        acon_sun = create_ACON_sun()
    if acon_sun.data.type == "SUN":
        acon_sun.data.angle = 0

    # 오브젝트의 그림자가 아닌 옵션에 의한 그림자는 "불량 그림자"로 판단하고 해당 옵션 off
    # 그림자가 생기는 면과 붙어 있지 않고 떠있는 느낌을 지우기 위해 bias를 오류가 나지 않을 정도로 조정
    # create_ACON_sun(), startup.blend에도 같은 작업 수행
    acon_sun.data.use_contact_shadow = False
    acon_sun.data.shadow_buffer_bias = 0.1


def create_ACON_sun() -> Object:
    acon_sun_data: Light = bpy.data.lights.new("ACON_sun", type="SUN")
    acon_sun_data.energy = 1

    acon_sun: Object = bpy.data.objects.new("ACON_sun", acon_sun_data)
    acon_sun.rotation_euler.x = math.radians(90 - 35)
    acon_sun.rotation_euler.y = 0
    acon_sun.rotation_euler.z = math.radians(65)
    acon_sun.data.use_contact_shadow = False
    acon_sun.data.shadow_buffer_bias = 0.1

    bpy.context.scene.collection.objects.link(acon_sun)

    return acon_sun
