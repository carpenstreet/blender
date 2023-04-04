from bpy.types import AddonPreferences
from bpy.props import FloatProperty, IntProperty


class NewSketchupAddonPreferences(AddonPreferences):
    bl_idname = __name__.split(".")[0]

    camera_far_plane: FloatProperty(
        name="Camera Clip Ends At :", default=250, unit="LENGTH"
    )

    draw_bounds: IntProperty(
        name="Draw Similar Objects As Bounds When It's Over :", default=1000
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="- Basic Import Options -")
        row = self.draw_ui(layout, "camera_far_plane")
        layout = self.layout
        row = self.draw_ui(layout, "draw_bounds")

    def draw_ui(self, layout, text):
        ret_row = layout.row()
        ret_row.use_property_split = True
        ret_row.prop(self, text)
        return ret_row
