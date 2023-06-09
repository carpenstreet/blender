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
    "version": (0, 3, 0),
    "blender": (3, 0, 0),
    "location": "",
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Style",
}

import bpy


class Acon3dStylesPanel(bpy.types.Panel):
    bl_idname = "ACON_PT_Styles"
    bl_label = "Styles"
    bl_category = "Style"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"
    bl_order = 20
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Styles", icon="MATERIAL")

        row = layout.row()
        col = row.column()
        col.scale_x = 3
        col.separator()
        col = row.column()
        row = col.row()
        row.prop(
            context.scene.ACON_prop, "toggle_texture", text="Texture", text_ctxt="abler"
        )
        return


class LinePanel(bpy.types.Panel):
    bl_parent_id = "ACON_PT_Styles"
    bl_idname = "ACON_PT_Line"
    bl_label = "Line"
    bl_category = "Style"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.ACON_prop, "toggle_toon_edge", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        prop = context.scene.ACON_prop

        if prop.toggle_toon_edge:
            layout.prop(prop, "edge_min_line_width", text="Min Line Width", slider=True)
            layout.prop(prop, "edge_max_line_width", text="Max Line Width", slider=True)
            layout.prop(prop, "edge_line_detail", text="Line Detail", slider=True)


class SunlightPanel(bpy.types.Panel):
    bl_parent_id = "ACON_PT_Styles"
    bl_idname = "ACON3D_PT_Sunlight"
    bl_label = "Sunlight"
    bl_category = "Style"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.ACON_prop, "toggle_sun", text="")

    def draw(self, context):
        if context.scene.ACON_prop.toggle_sun:
            layout = self.layout
            layout.use_property_decorate = False  # No animation.
            layout.use_property_split = True
            row = layout.row(align=True)
            row.prop(
                context.scene.ACON_prop,
                "sun_strength",
                text="Strength",
                text_ctxt="abler",
            )
            row = layout.row(align=True)
            row.prop(
                context.scene.ACON_prop,
                "sun_rotation_x",
                text="Altitude",
                text_ctxt="abler",
            )
            row = layout.row(align=True)
            row.prop(
                context.scene.ACON_prop,
                "sun_rotation_z",
                text="Azimuth",
                text_ctxt="abler",
            )


class LIGHT_UL_List(bpy.types.UIList):
    bl_idname = "LIGHT_UL_List"
    bl_description = "Click to select a light"
    def __init__(self):
        super().__init__()
        self.use_filter_sort_reverse = True

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            if not item.obj.data:
                return
            light_type = item.obj.data.type
            row = layout.row(align=True)
            if light_type == "POINT":
                row.prop(item.obj, "name", icon="LIGHT_POINT", emboss=False, text="")
            elif light_type == "SPOT":
                row.prop(item.obj, "name", icon="LIGHT_SPOT", emboss=False, text="")
            elif light_type == "AREA":
                row.prop(item.obj, "name", icon="LIGHT_AREA", emboss=False, text="")
            row.prop(
                item,
                "is_hidden",
                text="",
                icon="HIDE_ON" if item.is_hidden else "HIDE_OFF",
            )


class LightPanel(bpy.types.Panel):
    bl_parent_id = "ACON_PT_Styles"
    bl_idname = "ACON3D_PT_Lights"
    bl_label = "Lights"
    bl_category = "Style"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"

    def draw(self, context):
        # update scene
        scene = context.scene

        if scene.ACON_prop.toggle_lights:
            layout = self.layout
            scene_prop = scene.ACON_prop
            layout.use_property_decorate = False  # No animation.
            layout.use_property_split = True
            row = layout.row(align=True)
            # Add Light
            row.label(text="Add Light")

            row = layout.row(align=True)

            # PointLight 생성버튼
            col = row.column()
            col.operator(AddPointLightOperator.bl_idname, text="Point", text_ctxt="abler", icon="LIGHT_POINT")

            # SpotLight 생성버튼
            col = row.column()
            col.operator(AddSpotLightOperator.bl_idname, text="Spot", text_ctxt="abler", icon="LIGHT_SPOT")

            # AreaLight 생성버튼
            col = row.column()
            col.operator(AddAreaLightOperator.bl_idname, text="Area", text_ctxt="abler", icon="LIGHT_AREA")

            row = layout.row(align=True)
            col = row.column()
            col.template_list(
                "LIGHT_UL_List",
                "LightsInSceneList",
                scene_prop,
                "lights",
                scene_prop,
                "light_index",
            )
            col = row.column()
            col.operator(RemoveLightOperator.bl_idname, text="", icon="REMOVE")

            if scene_prop.lights:
                index = scene_prop.light_index

                if index not in range(0, len(scene_prop.lights)):
                    return

                light = scene_prop.lights[index]
                row = layout.row(align=True)
                row.prop(light, "color", text="Color", slider=True)
                row = layout.row(align=True)
                row.prop(light, "energy", text="Energy", slider=True)
                row = layout.row(align=True)
                row.prop(light, "diffuse_factor", text="Diffuse", slider=True)
                row = layout.row(align=True)
                row.prop(light, "specular_factor", text="Specular", slider=True)
                row = layout.row(align=True)
                row.prop(light, "volume_factor", text="Volume", slider=True)


class AddLightOperatorBase(bpy.types.Operator):
    bl_options = {"REGISTER"}
    bl_translation_context = "abler"
    light_type = "LIGHT_BASE"
    scene: bpy.types.Scene

    def invoke(self, context, event):
        if not bpy.context.scene:
            return {"FINISHED"}

        self.scene = bpy.context.scene
        return self.execute(context)

    def _create_light_on_scene(self):
        acon_light_data: Light = bpy.data.lights.new(
            name="ACON_light", type=self.light_type
        )
        acon_light_data.energy = 10

        # object 생성
        acon_light: Object = bpy.data.objects.new(acon_light_data.name, acon_light_data)
        return acon_light

    def execute(self, context):
        light = self._create_light_on_scene()
        self.scene.collection.objects.link(light)
        item = self.scene.ACON_prop.lights.add()
        item.obj = light
        return {"FINISHED"}


class AddPointLightOperator(AddLightOperatorBase):
    bl_idname = "acon3d.add_light_point"
    bl_label = "Add Point Light"
    bl_description = "Add Point Light"
    light_type = "POINT"


class AddSpotLightOperator(AddLightOperatorBase):
    bl_idname = "acon3d.add_light_spot"
    bl_label = "Add Spot Light"
    bl_description = "Add Spot Light"
    light_type = "SPOT"


class AddAreaLightOperator(AddLightOperatorBase):
    bl_idname = "acon3d.add_light_area"
    bl_label = "Add Area Light"
    bl_description = "Add Area Light"
    light_type = "AREA"


class RemoveLightOperator(bpy.types.Operator):
    bl_idname = "acon3d.remove_light"
    bl_translation_context = "abler"
    bl_label = ""
    bl_description = "Remove Selected Light"
    bl_options = {"REGISTER"}

    def execute(self, context):
        scene = context.scene
        index = scene.ACON_prop.light_index
        lights = scene.ACON_prop.lights

        if index >= len(lights):
            return {"FINISHED"}

        light_obj = scene.ACON_prop.lights[index].obj

        # 실제 오브젝트 제거 (data block 정리는 블렌더가 함)
        bpy.data.objects.remove(light_obj)

        # ACON_prop.lights 데이터 제거
        scene.ACON_prop.lights.remove(index)

        if index > 0:
            index = index - 1

        return {"FINISHED"}


class ShadowShadingPanel(bpy.types.Panel):
    bl_parent_id = "ACON_PT_Styles"
    bl_idname = "ACON3D_PT_ShadowShading"
    bl_label = "Shadow / Shading"
    bl_category = "Style"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.ACON_prop, "toggle_shadow_shading", text="")

    def draw(self, context):
        if context.scene.ACON_prop.toggle_shadow_shading:
            layout = self.layout
            row = layout.row()
            col = row.column()
            col.scale_x = 3
            col.separator()
            col = row.column()
            row = col.row()
            row.prop(context.scene.ACON_prop, "toggle_shadow", text="Shadow")


class ShadingPanel(bpy.types.Panel):
    bl_parent_id = "ACON3D_PT_ShadowShading"
    bl_idname = "ACON_PT_Shading"
    bl_label = "Toon Style Shading"
    bl_category = "Style"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"

    @classmethod
    def poll(cls, context):
        return context.scene.ACON_prop.toggle_shadow_shading

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.ACON_prop, "toggle_toon_face", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        if context.scene.ACON_prop.toggle_toon_face:
            prop = context.scene.ACON_prop

            col = layout.column()
            col.prop(prop, "toon_shading_depth")

            if prop.toon_shading_depth == "2":
                col.prop(
                    prop, "toon_shading_brightness_1", text="Brightness", slider=True
                )
            else:
                col.prop(
                    prop, "toon_shading_brightness_1", text="Brightness 1", slider=True
                )
                col.prop(
                    prop, "toon_shading_brightness_2", text="Brightness 2", slider=True
                )


class MATERIAL_UL_List(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        layout.use_property_split = True
        layout.use_property_decorate = False
        ob = data
        slot = item
        if ma := slot.material:
            layout.prop(ma, "name", text="", emboss=False, icon_value=icon)
            layout.prop(ma.ACON_prop, "type", text="")

            # exception handling code added due to error from link below
            # https://carpenstreet-np.sentry.io/issues/3974831978/?project=4504597190803456&referrer=slack
            if not ma.node_tree:
                return
            toonNode = ma.node_tree.nodes.get("ACON_nodeGroup_combinedToon")

            if not toonNode:
                return

            if ma.ACON_prop.type == "Diffuse":
                layout.label(text="", translate=False)

            if ma.ACON_prop.type == "Mirror":
                layout.prop(toonNode.inputs[6], "default_value", text="")

            if ma.ACON_prop.type == "Glow":
                layout.prop(toonNode.inputs[5], "default_value", text="")

            if ma.ACON_prop.type == "Clear":
                layout.prop(toonNode.inputs[7], "default_value", text="")


class CloneMaterialOperator(bpy.types.Operator):
    """Clone selected material"""

    bl_idname = "acon3d.clone_material"
    bl_label = "Clone Material"
    bl_options = {"REGISTER", "UNDO"}
    bl_translation_context = "abler"

    @classmethod
    def poll(cls, context):
        try:
            return bool(context.object.active_material)
        except:
            return False

    def execute(self, context):
        mat = context.object.active_material.copy()
        context.object.active_material = mat

        return {"FINISHED"}


class ObjectPropertiesPanel(bpy.types.Panel):
    bl_parent_id = "ACON_PT_Styles"
    bl_idname = "ACON_PT_ObjectProperties"
    bl_label = "Object Properties"
    bl_category = "Style"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        if obj and context.selected_objects:
            # Breadcrumb을 그려줌
            row = layout.row()
            col = row.column()
            col.scale_x = 3
            col.separator()
            col = row.column()
            col.label(text=obj.name, icon="OBJECT_DATA")
            col = row.column()
            col.label(text="", icon="RIGHTARROW")
            if obj.active_material:
                col = row.column()
                col.label(text=obj.active_material.name, icon="MATERIAL")
            # MATERIAL_UL_List을 그려주는 부분
            row = layout.row()
            col = row.column()
            col.scale_x = 3
            col.separator()
            col = row.column()
            col.template_list(
                "MATERIAL_UL_List",
                "",
                obj,
                "material_slots",
                obj,
                "active_material_index",
                rows=2,
            )
            if mat := obj.active_material:
                box = col.box()
                row = box.row()
                row.template_ID(
                    obj, "active_material", new="acon3d.clone_material", unlink=""
                )
                row = box.row()
                row.prop(mat.ACON_prop, "toggle_shadow")
                row = box.row()
                row.prop(mat.ACON_prop, "toggle_shading")
                row = box.row()
                row.prop(mat.ACON_prop, "toggle_edge")
        else:
            row = layout.row()
            col = row.column()
            col.scale_x = 3
            col.separator()
            col = row.column()
            col.label(text="No selected object")


class BloomPanel(bpy.types.Panel):
    bl_parent_id = "ACON_PT_Styles"
    bl_idname = "ACON_PT_BLOOM"
    bl_label = "Bloom"
    bl_category = "Style"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"
    COMPAT_ENGINES = {"BLENDER_EEVEE"}

    def draw_header(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene.ACON_prop, "use_bloom", text="")

    def draw(self, context):
        if context.scene.ACON_prop.use_bloom:
            layout = self.layout
            layout.use_property_split = True
            layout.use_property_decorate = False  # No animation.

            scene = context.scene
            eevee_prop = scene.eevee
            prop = scene.ACON_prop

            layout.active = eevee_prop.use_bloom
            col = layout.column()
            col.prop(prop, "bloom_threshold", text="Threshold", slider=True)
            col.prop(prop, "bloom_knee", text="Knee", slider=True)
            col.prop(prop, "bloom_radius", text="Radius", slider=True)
            col.prop(prop, "bloom_color", text="Color")
            col.prop(prop, "bloom_intensity", text="Intensity", slider=True)
            col.prop(prop, "bloom_clamp", text="Clamp", slider=True)


class ColorAdjustmentPanel(bpy.types.Panel):
    bl_parent_id = "ACON_PT_Styles"
    bl_idname = "ACON3D_PT_ColorAdjustment"
    bl_label = "Color Adjustment"
    bl_category = "Style"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"
    COMPAT_ENGINES = {"BLENDER_RENDER", "BLENDER_EEVEE", "BLENDER_WORKBENCH"}

    def draw(self, context):
        return


class BrightnessContrastPanel(bpy.types.Panel):
    bl_label = "Brightness / Contrast"
    bl_idname = "ACON3D_PT_BrightnessContrast"
    bl_parent_id = "ACON3D_PT_ColorAdjustment"
    bl_category = "Style"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"
    COMPAT_ENGINES = {"BLENDER_RENDER", "BLENDER_EEVEE", "BLENDER_WORKBENCH"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        prop = context.scene.ACON_prop

        layout.prop(prop, "image_adjust_brightness", text="Brightness", slider=True)
        layout.prop(prop, "image_adjust_contrast", text="Contrast", slider=True)


class ColorBalancePanel(bpy.types.Panel):
    bl_label = "Color Balance"
    bl_idname = "ACON3D_PT_ColorBalance"
    bl_parent_id = "ACON3D_PT_ColorAdjustment"
    bl_category = "Style"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"
    COMPAT_ENGINES = {"BLENDER_RENDER", "BLENDER_EEVEE", "BLENDER_WORKBENCH"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        prop = context.scene.ACON_prop

        layout.prop(prop, "image_adjust_color_r", text="Red", slider=True)
        layout.prop(prop, "image_adjust_color_g", text="Green", slider=True)
        layout.prop(prop, "image_adjust_color_b", text="Blue", slider=True)


class HueSaturationPanel(bpy.types.Panel):
    bl_label = "Hue / Saturation"
    bl_idname = "ACON3D_PT_HueSaturation"
    bl_parent_id = "ACON3D_PT_ColorAdjustment"
    bl_category = "Style"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"
    COMPAT_ENGINES = {"BLENDER_RENDER", "BLENDER_EEVEE", "BLENDER_WORKBENCH"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        prop = context.scene.ACON_prop

        layout.prop(prop, "image_adjust_hue", text="Hue", slider=True)
        layout.prop(prop, "image_adjust_saturation", text="Saturation", slider=True)


class ExposurePanel(bpy.types.Panel):
    bl_label = "Exposure"
    bl_idname = "ACON3D_PT_Exposure"
    bl_parent_id = "ACON3D_PT_ColorAdjustment"
    bl_category = "Style"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"
    COMPAT_ENGINES = {"BLENDER_RENDER", "BLENDER_EEVEE", "BLENDER_WORKBENCH"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        prop = context.scene.ACON_prop

        layout.prop(prop, "exposure", text="Exposure", slider=True)
        layout.prop(prop, "gamma", text="Gamma", slider=True)


classes = (
    Acon3dStylesPanel,
    LinePanel,
    SunlightPanel,
    LIGHT_UL_List,
    LightPanel,
    AddPointLightOperator,
    AddSpotLightOperator,
    AddAreaLightOperator,
    RemoveLightOperator,
    ShadowShadingPanel,
    ShadingPanel,
    MATERIAL_UL_List,
    CloneMaterialOperator,
    ObjectPropertiesPanel,
    BloomPanel,
    ColorAdjustmentPanel,
    BrightnessContrastPanel,
    ColorBalancePanel,
    HueSaturationPanel,
    ExposurePanel,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
