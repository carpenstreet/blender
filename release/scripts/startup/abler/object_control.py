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
from .lib import layers
from .lib.tracker import tracker


class GroupNavigateTopOperator(bpy.types.Operator):
    """Select Top Group"""

    bl_idname = "acon3d.group_navigate_top"
    bl_label = "Group Navigate Top"
    bl_translation_context = "*"

    @classmethod
    def poll(cls, context):
        return context.object

    def execute(self, context):
        tracker.group_navigate_top()
        layers.selectByGroup("TOP")
        return {"FINISHED"}


class GroupNavigateUpOperator(bpy.types.Operator):
    """Select Upper Group"""

    bl_idname = "acon3d.group_navigate_up"
    bl_label = "Group Navigate Up"
    bl_translation_context = "*"

    @classmethod
    def poll(cls, context):
        return context.object

    def execute(self, context):
        tracker.group_navigate_up()
        layers.selectByGroup("UP")
        return {"FINISHED"}


class GroupNavigateDownOperator(bpy.types.Operator):
    """Select Lower Group"""

    bl_idname = "acon3d.group_navigate_down"
    bl_label = "Group Navigate Down"
    bl_translation_context = "*"

    @classmethod
    def poll(cls, context):
        return context.object

    def execute(self, context):
        tracker.group_navigate_down()
        layers.selectByGroup("DOWN")
        return {"FINISHED"}


class GroupNavigateBottomOperator(bpy.types.Operator):
    """Select Bottom Group"""

    bl_idname = "acon3d.group_navigate_bottom"
    bl_label = "Group Navigate Bottom"
    bl_translation_context = "*"

    @classmethod
    def poll(cls, context):
        return context.object

    def execute(self, context):
        tracker.group_navigate_bottom()
        layers.selectByGroup("BOTTOM")
        return {"FINISHED"}


class Acon3dStateUpdateOperator(bpy.types.Operator):
    """Save newly adjusted state data of the object"""

    bl_idname = "acon3d.state_update"
    bl_label = "Update State"
    bl_translation_context = "*"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):

        for obj in context.selected_objects:

            prop = obj.ACON_prop

            if not prop.use_state:
                continue

            for att in ["location", "rotation_euler", "scale"]:

                vector = getattr(obj, att)
                setattr(prop.state_end, att, vector)

        context.object.ACON_prop.state_slider = 1

        return {"FINISHED"}


class Acon3dStateActionOperator(bpy.types.Operator):
    """Move object state"""

    bl_idname = "acon3d.state_action"
    bl_label = "Move State"
    bl_translation_context = "*"
    bl_options = {"REGISTER", "UNDO"}

    step: bpy.props.FloatProperty(name="Toggle Mode", default=0.25)

    def execute(self, context):

        for obj in context.selected_objects:

            prop = obj.ACON_prop
            x = prop.state_slider

            if x == 1:
                x = 0
            else:
                x += self.step

            x = min(x, 1)
            prop.state_slider = x

        return {"FINISHED"}


class Acon3dObjectPanel(bpy.types.Panel):
    bl_idname = "ACON_PT_Object_Main"
    bl_label = "Object Control"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="FILE_3D")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        col = row.column()
        col.scale_x = 3
        col.separator()
        col = row.column()

        if context.object:
            row = col.row()
            row.prop(
                context.object.ACON_prop,
                "constraint_to_camera_rotation_z",
                text="Look at me",
            )


class ObjectSubPanel(bpy.types.Panel):
    bl_parent_id = "ACON_PT_Object_Main"
    bl_idname = "ACON_PT_Object_Sub"
    bl_label = "Use State"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.object

    def draw_header(self, context):
        if obj := context.object:
            layout = self.layout
            layout.active = bool(len(context.selected_objects))
            layout.enabled = layout.active
            layout.prop(obj.ACON_prop, "use_state", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = True

        obj = context.object
        prop = obj.ACON_prop

        layout.active = prop.use_state and bool(len(context.selected_objects))
        layout.enabled = layout.active
        row = layout.row(align=True)
        row.prop(prop, "state_slider", slider=True)
        row.operator("acon3d.state_update", text="", icon="FILE_REFRESH")


class Acon3dGroupNavigaionPanel(bpy.types.Panel):
    bl_parent_id = "ACON_PT_Object_Main"
    bl_idname = "ACON_PT_Group_Navigation"
    bl_label = "Group Navigation"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        obj = context.active_object
        prop = obj.ACON_prop
        layout = self.layout

        row = layout.row(align=True)
        row.enabled = "Groups" in context.collection.children.keys()
        row.prop(prop, "group_list", text="")
        row.operator("acon3d.group_navigate_top", text="", icon="TRIA_UP_BAR")
        row.operator("acon3d.group_navigate_up", text="", icon="TRIA_UP")
        row.operator("acon3d.group_navigate_down", text="", icon="TRIA_DOWN")
        row.operator("acon3d.group_navigate_bottom", text="", icon="TRIA_DOWN_BAR")


classes = (
    GroupNavigateUpOperator,
    GroupNavigateTopOperator,
    GroupNavigateDownOperator,
    GroupNavigateBottomOperator,
    Acon3dStateActionOperator,
    Acon3dStateUpdateOperator,
    Acon3dObjectPanel,
    ObjectSubPanel,
    Acon3dGroupNavigaionPanel,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
