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
from .lib import cameras
from bpy_extras.io_utils import ImportHelper


class CreateCameraOperator(bpy.types.Operator):
    """Creates New Camera"""

    bl_idname = "acon3d.create_camera"
    bl_label = "Create Camera"
    bl_options = {"REGISTER", "UNDO"}

    name: bpy.props.StringProperty(name="Name")

    def execute(self, context):
        cameras.make_sure_camera_exists()

        # duplicate camera
        viewCameraObject = context.scene.camera
        camera_object = viewCameraObject.copy()
        camera_object.name = self.name
        camera_object.hide_viewport = True

        # add camera to designated collection (create one if not exists)
        collection = bpy.data.collections.get("ACON_col_cameras")
        if not collection:
            collection = bpy.data.collections.new("ACON_col_cameras")
            context.scene.collection.children.link(collection)
            layer_collection = context.view_layer.layer_collection
            layer_collection.children.get("ACON_col_cameras").exclude = True
        collection.objects.link(camera_object)

        # select created camera in custom view ui
        context.scene.ACON_prop.view = camera_object.name
        return {"FINISHED"}

    def invoke(self, context, event):
        self.name = cameras.gen_camera_name("ACON_Camera_")
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.separator()
        layout.prop(self, "name")
        layout.separator()


class DeleteCameraOperator(bpy.types.Operator):
    """Deletes Current Camera"""

    bl_idname = "acon3d.delete_camera"
    bl_label = "Delete Camera"
    bl_translation_context = "*"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        collection = bpy.data.collections.get("ACON_col_cameras")
        return collection and len(collection.objects) > 1

    def execute(self, context):
        if currentCameraName := context.scene.ACON_prop.view:
            bpy.data.objects.remove(bpy.data.objects[currentCameraName])

        return {"FINISHED"}


class Acon3dViewPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""

    bl_idname = "ACON3D_PT_view"
    bl_label = "Camera Control"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="CAMERA_DATA")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        layout.operator("acon3d.fly_mode")

        cam = context.scene.camera
        if cam is not None:
            row = layout.row()
            col = row.column()
            col.scale_x = 3
            col.separator()
            col = row.column()
            row = col.row()
            row.prop(cam.data, "lens")

        return


class Acon3dCameraPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""

    bl_parent_id = "ACON3D_PT_view"
    bl_idname = "ACON3D_PT_camera"
    bl_label = "Cameras"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene
        row = layout.row(align=True)
        row.prop(scene.ACON_prop, "view", text="")
        row.operator("acon3d.create_camera", text="", icon="ADD")
        row.operator("acon3d.delete_camera", text="", icon="REMOVE")


def scene_mychosenobject_poll(self, object):
    return object.type == "CAMERA"


class Acon3dDOFPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""

    bl_parent_id = "ACON3D_PT_view"
    bl_idname = "ACON3D_PT_dof"
    bl_label = "Depth of Field"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}
    COMPAT_ENGINES = {"BLENDER_EEVEE", "BLENDER_WORKBENCH"}

    def draw_header(self, context):
        if bpy.context.scene.camera is not None:
            scene = context.scene
            self.layout.prop(scene.ACON_prop, "use_dof", text="")
        else:
            self.layout.active = False

    def draw(self, context):
        if bpy.context.scene.camera is not None:
            layout = self.layout
            layout.use_property_split = True
            layout.use_property_decorate = False  # No animation.

            cam = bpy.context.scene.camera.data
            dof = cam.dof
            layout.active = dof.use_dof

            col = layout.column()
            col.prop(dof, "focus_object", text="Focus on Object")
            sub = col.column()
            sub.active = dof.focus_object is None
            sub.prop(dof, "focus_distance", text="Focus Distance")
            sub = col.column()
            sub.active = True
            sub.prop(dof, "aperture_fstop", text="F-stop")


class RemoveBackgroundOperator(bpy.types.Operator):
    """Removes Current Background Image"""

    bl_idname = "acon3d.background_image_remove"
    bl_label = "Remove Background Image"
    bl_translation_context = "*"
    bl_options = {"REGISTER", "UNDO"}

    index: bpy.props.IntProperty(name="Index", default=0)

    def execute(self, context):
        # self.index를 유저가 마음대로 바꿀 수 있는 패널로 인해 try/except로 감쌈
        try:
            image = context.scene.camera.data.background_images[self.index]
            image.image = None
            bpy.context.scene.camera.data.background_images.remove(image)
        except:
            pass
        return {"FINISHED"}


class FindBackgroundOperator(bpy.types.Operator, ImportHelper):
    """Open Image"""

    bl_idname = "acon3d.background_image_find"
    bl_label = "Open Image"
    bl_translation_context = "*"
    bl_options = {"REGISTER", "UNDO"}

    index: bpy.props.IntProperty(name="Index", default=0, options={"HIDDEN"})
    filter_glob: bpy.props.StringProperty(default="*.png", options={"HIDDEN"})
    filepath: bpy.props.StringProperty()

    def execute(self, context):
        new_image = bpy.data.images.load(self.filepath)
        image = context.scene.camera.data.background_images[self.index]
        image.image = new_image
        return {"FINISHED"}

    def invoke(self, context, event):
        path_abler = bpy.utils.preset_paths("abler")[0]
        self.filepath = path_abler + "/Background_Image/"
        wm = context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        space = context.space_data
        params = space.params
        params.display_type = "THUMBNAIL"
        space.show_region_tool_props = False
        space.show_region_ui = False
        space.show_region_toolbar = False


class Acon3dBackgroundPanel(bpy.types.Panel):
    bl_parent_id = "ACON3D_PT_view"
    bl_idname = "ACON3D_PT_background"
    bl_label = "Background Images"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        toggle_texture = context.scene.ACON_prop.toggle_texture

        if context.scene.camera is not None and toggle_texture:
            scene = context.scene
            self.layout.prop(scene.ACON_prop, "show_background_images", text="")
        else:
            self.layout.active = False

    def draw(self, context):
        layout = self.layout
        layout.operator("view3d.background_image_add", text="Add Image", text_ctxt="*")

        camObj = context.scene.camera
        active = camObj and camObj.data.show_background_images

        layout.active = active
        layout.use_property_split = True
        layout.use_property_decorate = False

        toggle_texture = context.scene.ACON_prop.toggle_texture

        if context.scene.camera is not None and toggle_texture:
            cam = context.scene.camera.data

            for i, bg in enumerate(cam.background_images):
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
                    row.label(text="Not Set")

                row.operator(
                    "acon3d.background_image_remove", text="", emboss=False, icon="X"
                ).index = i

                if bg.show_expanded:
                    row = box.row()
                    row.operator("acon3d.background_image_find", text="New").index = i
                    # row.template_ID(bg, "image", new="image.open")
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
                    row.prop(bg, "scale")
                    row = box.row(heading="Flip")
                    row.prop(bg, "use_flip_x", text="X")
                    row.prop(bg, "use_flip_y", text="Y")


classes = (
    Acon3dViewPanel,
    Acon3dCameraPanel,
    CreateCameraOperator,
    DeleteCameraOperator,
    Acon3dDOFPanel,
    RemoveBackgroundOperator,
    FindBackgroundOperator,
    Acon3dBackgroundPanel,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
