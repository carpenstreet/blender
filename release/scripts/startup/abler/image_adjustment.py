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
    "author": "sdk@acon3d.com",
    "version": (0, 0, 1),
    "blender": (2, 93, 0),
    "location": "",
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "ACON3D",
}


import bpy


class Acon3dImageAdjustmentPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""

    bl_idname = "ACON3D_PT_image_adjustment"
    bl_label = "Image Adjustment"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}
    COMPAT_ENGINES = {"BLENDER_RENDER", "BLENDER_EEVEE", "BLENDER_WORKBENCH"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="IMAGE_DATA")

    def draw(self, context):
        return


class Acon3dBrightnessContrastPanel(bpy.types.Panel):
    bl_label = "Brightness / Contrast"
    bl_idname = "ACON3D_PT_image_sub_bright"
    bl_parent_id = "ACON3D_PT_image_adjustment"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}
    COMPAT_ENGINES = {"BLENDER_RENDER", "BLENDER_EEVEE", "BLENDER_WORKBENCH"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        prop = context.scene.ACON_prop

        layout.prop(prop, "image_adjust_brightness", text="Brightness", slider=True)
        layout.prop(prop, "image_adjust_contrast", text="Contrast", slider=True)


class Acon3dColorBalancePanel(bpy.types.Panel):
    bl_label = "Color Balance"
    bl_idname = "ACON3D_PT_image_sub_color"
    bl_parent_id = "ACON3D_PT_image_adjustment"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}
    COMPAT_ENGINES = {"BLENDER_RENDER", "BLENDER_EEVEE", "BLENDER_WORKBENCH"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        prop = context.scene.ACON_prop

        layout.prop(prop, "image_adjust_color_r", text="Red", slider=True)
        layout.prop(prop, "image_adjust_color_g", text="Green", slider=True)
        layout.prop(prop, "image_adjust_color_b", text="Blue", slider=True)


class Acon3dHueSaturationPanel(bpy.types.Panel):
    bl_label = "Hue / Saturation"
    bl_idname = "ACON3D_PT_image_sub_hue"
    bl_parent_id = "ACON3D_PT_image_adjustment"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}
    COMPAT_ENGINES = {"BLENDER_RENDER", "BLENDER_EEVEE", "BLENDER_WORKBENCH"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        prop = context.scene.ACON_prop

        layout.prop(prop, "image_adjust_hue", text="Hue", slider=True)
        layout.prop(prop, "image_adjust_saturation", text="Saturation", slider=True)


class Acon3dExposurePanel(bpy.types.Panel):
    bl_label = "Exposure"
    bl_idname = "ACON3D_PT_image_sub_exposure"
    bl_parent_id = "ACON3D_PT_image_adjustment"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}
    COMPAT_ENGINES = {"BLENDER_RENDER", "BLENDER_EEVEE", "BLENDER_WORKBENCH"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        prop = context.scene.ACON_prop

        layout.prop(prop, "exposure", text="Exposure", slider=True)
        layout.prop(prop, "gamma", text="Gamma", slider=True)


classes = (
    Acon3dImageAdjustmentPanel,
    Acon3dBrightnessContrastPanel,
    Acon3dColorBalancePanel,
    Acon3dHueSaturationPanel,
    Acon3dExposurePanel,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
