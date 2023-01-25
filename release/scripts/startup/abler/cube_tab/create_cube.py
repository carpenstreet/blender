import random

import bpy


class AconAddCubeOperator(bpy.types.Operator):
    bl_idname = "acon3d.add_cube"
    bl_label = "Add Cube"
    bl_translation_context = "abler"

    name: bpy.props.StringProperty(name="Name", description="Write scene name")
    location_x: bpy.props.IntProperty(name="x")
    location_y: bpy.props.IntProperty(name="y")
    location_z: bpy.props.IntProperty(name="z")

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.separator()
        layout.prop(self, "name")
        layout.separator()
        layout.prop(self, "location_x")
        layout.separator()
        layout.prop(self, "location_y")
        layout.separator()
        layout.prop(self, "location_z")
        layout.separator()

    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add(
            location=(self.location_x, self.location_y, self.location_z), size=2.0
        )

        hue = random.uniform(0.0, 1.0)
        saturation = random.uniform(0.0, 1.0)
        value = random.uniform(0.0, 1.0)
        alpha = 1

        color_mat = bpy.data.materials.new("Color Mat")
        id = color_mat.name
        bpy.data.materials[id].diffuse_color = (hue, saturation, value, alpha)

        ob = bpy.context.active_object
        ob.name = self.name
        mesh = bpy.context.active_object.data
        mesh.materials.append(color_mat)

        return {"FINISHED"}


class AconDeleteAllOperator(bpy.types.Operator):
    bl_idname = "acon3d.delete_all"
    bl_label = "Delete All"
    bl_translation_context = "abler"

    def execute(self, context):
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()

        return {"FINISHED"}


class Acon3dCubePanel(bpy.types.Panel):
    bl_idname = "ACON3D_PT_cube"
    bl_label = "Cube"
    bl_category = "Cube"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"
    bl_order = 1

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="EVENT_A")

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.scale_y = 1.0
        row.operator("acon3d.add_cube", text="add cube")

        row = layout.row()
        row.scale_y = 1.0
        row.operator("acon3d.delete_all", text="delete all")


class ACON3dMovePanel(bpy.types.Panel):
    bl_idname = "ACON3D_PT_MoveCube"
    bl_label = "Move"
    bl_category = "Cube"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"
    bl_order = 2

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="EVENT_B")

    def draw(self, context):
        layout = self.layout
        obj = bpy.context.active_object
        prop = obj.ACON_prop
        layout.prop(prop, "location_x", text="x")
        layout.prop(prop, "location_y", text="y")
        layout.prop(prop, "location_z", text="z")


class ACON3dScalePanel(bpy.types.Panel):
    bl_idname = "ACON3D_PT_ScaleCube"
    bl_label = "Scale"
    bl_category = "Cube"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"
    bl_order = 3

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="EVENT_C")

    def draw(self, context):
        layout = self.layout
        obj = context.object
        prop = obj.ACON_prop
        layout.prop(prop, "scale_x", text="x")
        layout.prop(prop, "scale_y", text="y")
        layout.prop(prop, "scale_z", text="z")


class ACON3dRotatePanel(bpy.types.Panel):
    bl_idname = "ACON3D_PT_RotateCube"
    bl_label = "Rotate"
    bl_category = "Cube"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"
    bl_order = 4

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="EVENT_D")

    def draw(self, context):
        layout = self.layout
        obj = context.object
        prop = obj.ACON_prop
        layout.prop(prop, "rotate_x", text="x")
        layout.prop(prop, "rotate_y", text="y")
        layout.prop(prop, "rotate_z", text="z")


classes = (
    Acon3dCubePanel,
    AconAddCubeOperator,
    AconDeleteAllOperator,
    ACON3dMovePanel,
    ACON3dScalePanel,
    ACON3dRotatePanel,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
