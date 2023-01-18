import random

import bpy


class AconAddCubeOperator(bpy.types.Operator):
    bl_idname = "acon3d.add_cube"
    bl_label = "Add Cube"
    bl_translation_context = "abler"

    name: bpy.props.StringProperty(name="Name", description="Write scene name")
    x: bpy.props.IntProperty(name="x")
    y: bpy.props.IntProperty(name="y")
    z: bpy.props.IntProperty(name="z")

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.separator()
        layout.prop(self, "name")
        layout.separator()
        layout.prop(self, "x")
        layout.separator()
        layout.prop(self, "y")
        layout.separator()
        layout.prop(self, "z")
        layout.separator()

    def execute(self, context):

        mesh = bpy.ops.mesh.primitive_cube_add(
            location=(self.x, self.y, self.z), size=2.0
        )
        ob = bpy.context.object
        me = ob.data
        ob.name = self.name
        me.name = "CUBEMESH"

        return {"FINISHED"}


class AconDeleteAllCubesOperator(bpy.types.Operator):
    bl_idname = "acon3d.delete_all_cubes"
    bl_label = "Delete All Cubes"
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
        row.operator("acon3d.delete_all_cubes", text="delete all")


class ACON3dNameCubePanel(bpy.types.Panel):
    bl_idname = "ACON3D_PT_NameCube"
    bl_label = "Cube Name"
    bl_category = "Cube"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"
    bl_order = 1

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="EVENT_B")

    def draw(self, context):
        layout = self.layout
        prop = context.scene.ACON_prop
        layout.prop(prop, "cube_name", text="name")


classes = (
    Acon3dCubePanel,
    AconAddCubeOperator,
    AconDeleteAllCubesOperator,
    ACON3dNameCubePanel,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
