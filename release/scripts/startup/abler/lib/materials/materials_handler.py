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


import bpy
from typing import List, Optional
from bpy.types import (
    Context,
    NodeTree,
    Node,
    Object,
    Material,
    BoolProperty,
    EnumProperty,
    FloatProperty,
    MaterialSlot,
    NodeSocket,
    PropertyGroup,
)


def toggleToonEdge(self, context: Context) -> None:
    if not context:
        context = bpy.context

    if not self:
        self = context.scene.ACON_prop
    toonEdgeFactorValue: int = int(context.scene.ACON_prop.toggle_toon_edge)

    node_group: Optional[NodeTree] = bpy.data.node_groups.get(
        "ACON_nodeGroup_combinedToon"
    )
    if not node_group:
        return

    node: Optional[Node] = node_group.nodes.get("ACON_node_toonEdgeFactor")
    if not node:
        return

    node.outputs[0].default_value = toonEdgeFactorValue


def toggleEachEdge(self, context: Context) -> None:
    if not context:
        context = bpy.context
    if "object" not in dir(context):
        return

    obj: Optional[Object] = context.object
    if obj is None:
        return

    mat: Optional[Material] = obj.active_material

    if not mat:
        return

    toonEdgeFactorValue: int = int(mat.ACON_prop.toggle_edge)
    toonNode: Optional[Node] = mat.node_tree.nodes.get("ACON_nodeGroup_combinedToon")
    if toonNode:
        toonNode.inputs[9].default_value = toonEdgeFactorValue


def toggleToonFace(self, context: Context) -> None:
    if not context:
        context = bpy.context

    if not self:
        self = context.scene.ACON_prop

    toonFaceFactorValue: int = int(context.scene.ACON_prop.toggle_toon_face)

    node_group: Optional[NodeTree] = bpy.data.node_groups.get(
        "ACON_nodeGroup_combinedToon"
    )
    if not node_group:
        return

    node: Optional[Node] = node_group.nodes.get("ACON_nodeGroup_toonFace")
    if node:
        node.inputs[4].default_value = toonFaceFactorValue


def toggleTexture(self, context: Context) -> None:
    if not context:
        context = bpy.context

    if not self:
        self = context.scene.ACON_prop

    toggle_texture: BoolProperty = context.scene.ACON_prop.toggle_texture
    textureFactorValue: int = int(not toggle_texture)

    if context.scene.camera:
        for image in context.scene.camera.data.background_images:
            image.show_background_image = toggle_texture

    node_group: Optional[NodeTree] = bpy.data.node_groups.get(
        "ACON_nodeGroup_combinedToon"
    )
    if not node_group:
        return

    node: Optional[Node] = node_group.nodes.get("ACON_node_textureMixFactor")
    if not node:
        return
    node.inputs[0].default_value = textureFactorValue


def toggleShading(self, context: Context) -> None:
    if not context:
        context = bpy.context

    if not self:
        self = context.scene.ACON_prop

    toggle_shading: BoolProperty = context.scene.ACON_prop.toggle_shading
    shadingFactorValue: int = int(toggle_shading)

    node_group: Optional[NodeTree] = bpy.data.node_groups.get(
        "ACON_nodeGroup_combinedToon"
    )
    if not node_group:
        return

    node: Optional[Node] = node_group.nodes.get("ACON_node_shadeMixFactor")
    if not node:
        return
    node.outputs[0].default_value = shadingFactorValue


def toggleEachShading(self, context: Context) -> None:

    if not context:
        context = bpy.context

    if not context:
        context = bpy.context

    if "object" not in dir(context):
        return

    obj: Optional[Object] = context.object
    if obj is None:
        return

    mat: Optional[Material] = obj.active_material

    if not mat:
        return

    shadingFactorValue: int = int(mat.ACON_prop.toggle_shading)
    toonNode: Optional[Node] = mat.node_tree.nodes.get("ACON_nodeGroup_combinedToon")
    if not toonNode:
        return
    toonNode.inputs[4].default_value = shadingFactorValue


def toggleEachShadow(self, context: Context) -> None:

    if not context:
        context = bpy.context

    if not context:
        context = bpy.context

    if "object" not in dir(context):
        return

    obj: Optional[Object] = context.object
    if obj is None:
        return

    mat: Optional[Material] = obj.active_material

    if not mat:
        return

    mat.shadow_method = "CLIP" if mat.ACON_prop.toggle_shadow else "NONE"


def changeToonDepth(self, context: Context) -> None:
    if not context:
        context = bpy.context

    if not self:
        self = context.scene.ACON_prop

    node_group: Optional[NodeTree] = bpy.data.node_groups.get(
        "ACON_nodeGroup_combinedToon"
    )
    if not node_group:
        return

    toonFaceFactorValue: int = int(context.scene.ACON_prop.toon_shading_depth == "3")

    node: Optional[Node] = node_group.nodes.get("ACON_nodeGroup_toonFace")
    if not node:
        return
    node.inputs[1].default_value = toonFaceFactorValue


def setMaterialParametersByType(mat: Material) -> None:

    type: EnumProperty = mat.ACON_prop.type

    toonNode: Optional[Node] = mat.node_tree.nodes.get("ACON_nodeGroup_combinedToon")
    if not toonNode:
        return

    if type == "Clear":
        mat.blend_method = "BLEND"
        mat.ACON_prop.toggle_shadow = False
        # WORKAROUND:
        # 렌더 시 필요에 따라 mat.shadow_method = "OPAQUE" 대입을 하는 경우가 있는데,
        # 렌더가 끝난 후 머티리얼 관련 뒷처리를 할 때
        # toggle_shadow = False 을 통해 shadow_method 가 원상복구 되기를 기대했으나,
        # 기대대로 동작하지 않고 "OPAQUE" 상태로 남아서 직접 "NONE" 대입해서 처리
        mat.shadow_method = "NONE"
        toonNode.inputs[1].default_value = 1
        toonNode.inputs[3].default_value = 1
    elif type == "Diffuse":
        mat.blend_method = "CLIP"
        mat.ACON_prop.toggle_shadow = True
        toonNode.inputs[1].default_value = 0
        toonNode.inputs[3].default_value = 1
    elif type == "Glow":
        mat.blend_method = "CLIP"
        mat.ACON_prop.toggle_shadow = True
        toonNode.inputs[1].default_value = 0
        toonNode.inputs[2].default_value = 0
        toonNode.inputs[3].default_value = 0
    elif type == "Mirror":
        bpy.context.scene.eevee.use_ssr = True
        mat.blend_method = "CLIP"
        mat.ACON_prop.toggle_shadow = True
        toonNode.inputs[1].default_value = 0
        toonNode.inputs[2].default_value = 1
        toonNode.inputs[3].default_value = 0.5


def changeMaterialType(self, context: Context) -> None:
    try:
        if not context:
            context = bpy.context

        material_slots: List[MaterialSlot] = context.active_object.material_slots

        for mat_slot in material_slots:
            mat: Material = mat_slot.material
            setMaterialParametersByType(mat)

    except:
        print("ACON Material Type change handler could not complete.")


def changeImageAdjustBrightness(self, context: Context) -> None:
    if not context:
        context = bpy.context

    if not self:
        self = context.scene.ACON_prop

    node_group: Optional[NodeTree] = bpy.data.node_groups.get(
        "ACON_nodeGroup_combinedToon"
    )

    if not node_group:
        return

    bright: Optional[Node] = node_group.nodes.get("ACON_node_bright")
    if not bright:
        return
    inputs: List[NodeSocket] = bright.inputs

    prop: PropertyGroup = context.scene.ACON_prop
    value: FloatProperty = prop.image_adjust_brightness

    inputs[1].default_value = value
    inputs[2].default_value = value


def changeImageAdjustContrast(self, context: Context) -> None:
    if not context:
        context = bpy.context

    node_group: Optional[NodeTree] = bpy.data.node_groups.get(
        "ACON_nodeGroup_combinedToon"
    )

    if not node_group:
        return

    contrast: Optional[Node] = node_group.nodes.get("ACON_node_contrast")
    if not contrast:
        return
    inputs: List[NodeSocket] = contrast.inputs

    prop: PropertyGroup = context.scene.ACON_prop
    value: FloatProperty = prop.image_adjust_contrast

    inputs[1].default_value = -0.1 * value
    inputs[2].default_value = value


def changeImageAdjustColor(self, context: Context) -> None:
    if not context:
        context = bpy.context

    if not self:
        self = context.scene.ACON_prop

    node_group: Optional[NodeTree] = bpy.data.node_groups.get(
        "ACON_nodeGroup_combinedToon"
    )

    if not node_group:
        return

    brightContrast: Optional[Node] = node_group.nodes.get("ACON_node_colorBalance")
    if not brightContrast:
        return
    inputs: List[NodeSocket] = brightContrast.inputs

    prop: PropertyGroup = context.scene.ACON_prop
    r: FloatProperty = prop.image_adjust_color_r
    g: FloatProperty = prop.image_adjust_color_g
    b: FloatProperty = prop.image_adjust_color_b
    color = (r, g, b, 1)

    inputs[2].default_value = color


def changeImageAdjustHue(self, context: Context) -> None:
    if not context:
        context = bpy.context

    if not self:
        self = context.scene.ACON_prop

    node_group: Optional[NodeTree] = bpy.data.node_groups.get(
        "ACON_nodeGroup_combinedToon"
    )

    if not node_group:
        return

    hueSaturation: Optional[Node] = node_group.nodes.get("ACON_node_hueSaturation")
    if not hueSaturation:
        return
    inputs: List[NodeSocket] = hueSaturation.inputs

    prop: PropertyGroup = context.scene.ACON_prop
    value: FloatProperty = prop.image_adjust_hue

    inputs[0].default_value = value


def changeImageAdjustSaturation(self, context: Context) -> None:
    if not context:
        context = bpy.context

    if not self:
        self = context.scene.ACON_prop

    node_group: Optional[NodeTree] = bpy.data.node_groups.get(
        "ACON_nodeGroup_combinedToon"
    )

    if not node_group:
        return

    hueSaturation: Optional[Node] = node_group.nodes.get("ACON_node_hueSaturation")
    if not hueSaturation:
        return
    inputs: List[NodeSocket] = hueSaturation.inputs

    prop: PropertyGroup = context.scene.ACON_prop
    value: FloatProperty = prop.image_adjust_saturation

    inputs[1].default_value = value


def changeLineProps(self, context: Context) -> None:
    if not context:
        context = bpy.context

    if not self:
        self = context.scene.ACON_prop

    node_group: Optional[NodeTree] = bpy.data.node_groups.get(
        "ACON_nodeGroup_combinedToon"
    )

    if not node_group:
        return

    node_outline: Optional[Node] = node_group.nodes.get("ACON_nodeGroup_outline")
    if not node_outline:
        return
    inputs: List[NodeSocket] = node_outline.inputs

    prop: PropertyGroup = context.scene.ACON_prop
    min_value: FloatProperty = prop.edge_min_line_width
    max_value: FloatProperty = prop.edge_max_line_width
    line_detail: FloatProperty = prop.edge_line_detail

    inputs[0].default_value = min_value
    inputs[1].default_value = max_value
    inputs[3].default_value = line_detail


def changeToonShadingBrightness(self, context: Context) -> None:
    if not context:
        context = bpy.context

    if not self:
        self = context.scene.ACON_prop

    node_group: Optional[NodeTree] = bpy.data.node_groups.get(
        "ACON_nodeGroup_combinedToon"
    )

    if not node_group:
        return
    node_outline = node_group.nodes.get("ACON_nodeGroup_toonFace")
    inputs = node_outline.inputs

    prop: PropertyGroup = context.scene.ACON_prop
    value_1: FloatProperty = prop.toon_shading_brightness_1
    value_2: FloatProperty = prop.toon_shading_brightness_2

    inputs[2].default_value = value_1
    inputs[3].default_value = value_2
