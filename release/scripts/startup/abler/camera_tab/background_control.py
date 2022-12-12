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
import os

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
    "category": "CAMERA",
}

import bpy
from ..lib import cameras
from ..lib.file_view import file_view_title
from ..lib.import_file import AconImportHelper


class RemoveBackgroundOperator(bpy.types.Operator):
    """Remove current background image"""

    bl_idname = "acon3d.background_image_remove"
    bl_label = "Remove background image"
    bl_translation_context = "abler"
    bl_options = {"REGISTER", "UNDO"}

    index: bpy.props.IntProperty(name="Index", default=0)

    def execute(self, context):
        # self.index를 유저가 마음대로 바꿀 수 있는 패널로 인해 try/except로 감쌈
        try:
            image = context.scene.camera.data.background_images[self.index]
            if image.image:
                bpy.data.images.remove(image.image)
            image.image = None
            bpy.context.scene.camera.data.background_images.remove(image)
        except:
            pass
        return {"FINISHED"}


class OpenDefaultBackgroundOperator(bpy.types.Operator, AconImportHelper):
    """Open default background image"""

    bl_idname = "acon3d.default_background_image_open"
    bl_label = "Default Image"
    bl_translation_context = "abler"
    bl_options = {"REGISTER", "UNDO"}

    index: bpy.props.IntProperty(name="Index", default=0, options={"HIDDEN"})
    filter_glob: bpy.props.StringProperty(default="*.png", options={"HIDDEN"})
    filepath: bpy.props.StringProperty()
    use_filter = True

    def invoke(self, context, event):
        with file_view_title("BACKGROUND"):
            path_abler = bpy.utils.preset_paths("abler")[0]
            self.filepath = path_abler + "/Background_Image/"
            return super().invoke(context, event)

    def execute(self, context):
        if not self.check_path(accepted=["png", "jpg"]):
            return {"FINISHED"}

        new_image = bpy.data.images.load(self.filepath)
        image = context.scene.camera.data.background_images[self.index]
        if image.image:
            bpy.data.images.remove(image.image)
        image.image = new_image
        return {"FINISHED"}

    def draw(self, context):
        super().draw(context)
        space = context.space_data
        space.show_region_tool_props = False
        space.show_region_ui = False
        space.show_region_toolbar = False


class OpenCustomBackgroundOperator(bpy.types.Operator, AconImportHelper):
    """Open custom background image"""

    bl_idname = "acon3d.custom_background_image_open"
    bl_label = "Custom Image"
    bl_translation_context = "abler"
    bl_options = {"REGISTER", "UNDO"}

    image_extension = "*.png;*.jpg;"
    index: bpy.props.IntProperty(name="Index", default=0, options={"HIDDEN"})
    filter_glob: bpy.props.StringProperty(default=image_extension, options={"HIDDEN"})
    use_filter = True

    def invoke(self, context, event):
        with file_view_title("BACKGROUND"):
            return super().invoke(context, event)

    def execute(self, context):
        if not self.check_path(accepted=["png", "jpg"]):
            return {"FINISHED"}

        new_image = bpy.data.images.load(self.filepath)
        image = context.scene.camera.data.background_images[self.index]
        if image.image:
            bpy.data.images.remove(image.image)
        image.image = new_image
        return {"FINISHED"}

    def draw(self, context):
        super().draw(context)
        context.space_data.show_region_tool_props = False


class Acon3dBackgroundPanel(bpy.types.Panel):
    bl_idname = "ACON3D_PT_background"
    bl_label = "Background"
    bl_category = "Camera"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"
    bl_order = 11
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Background", icon="IMAGE_BACKGROUND")


class Acon3dBackgroundImagesPanel(bpy.types.Panel):
    bl_parent_id = "ACON3D_PT_background"
    bl_idname = "ACON3D_PT_background_images"
    bl_label = "Background Images"
    bl_category = "Camera"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"

    def draw(self, context):
        layout = self.layout
        layout.operator("view3d.background_image_add", text="Add Image", text_ctxt="*")

        camObj = context.scene.camera

        layout.use_property_split = True
        layout.use_property_decorate = False

        if camObj is not None:
            background_images = camObj.data.background_images

            l = len(background_images)
            for i, bg in enumerate(reversed(background_images)):
                count = l - i - 1

                box = layout.box()
                row = box.row(align=True)
                row.prop(bg, "show_expanded", text="", emboss=False)

                if bg.source == "IMAGE" and bg.image:
                    row.prop(bg.image, "name", text="", emboss=False)
                elif bg.source == "MOVIE_CLIP" and bg.clip:
                    row.prop(bg.clip, "name", text="", emboss=False)
                elif bg.source and bg.use_camera_clip:
                    row.label(text="Active Clip")
                else:
                    row.label(text="Not Set", text_ctxt="abler")

                row.operator(
                    "acon3d.background_image_remove", text="", emboss=False, icon="X"
                ).index = count

                if bg.show_expanded:
                    row = box.row()
                    row.operator(
                        "acon3d.default_background_image_open", text="Default Image"
                    ).index = count
                    row.operator(
                        "acon3d.custom_background_image_open", text="Custom Image"
                    ).index = count
                    row = box.row()
                    row.prop(bg, "alpha")
                    row = box.row()
                    row.prop(bg, "display_depth", text="Placement", expand=True)
                    row = box.row()
                    row.prop(bg, "frame_method", expand=True)
                    row = box.row()
                    row.prop(bg, "offset")
                    row = box.row()
                    row.prop(bg, "rotation")
                    row = box.row()
                    row.prop(bg, "scale", text="Scale", text_ctxt="abler")
                    row = box.row(heading="Flip")
                    row.prop(bg, "use_flip_x", text="Flip X-axis")
                    row.prop(bg, "use_flip_y", text="Flip Y-axis")


classes = (
    RemoveBackgroundOperator,
    OpenDefaultBackgroundOperator,
    OpenCustomBackgroundOperator,
    Acon3dBackgroundPanel,
    Acon3dBackgroundImagesPanel,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
