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


class Acon3dStylePanel(bpy.types.Panel):
    bl_idname = "ACON_PT_Styles"
    bl_label = "Styles"
    bl_category = "Style"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="MATERIAL")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        col = row.column()
        col.scale_x = 3
        col.separator()
        col = row.column()
        row = col.row()
        row.prop(context.scene.ACON_prop, "toggle_texture", text="Texture")
        return


class LinePanel(bpy.types.Panel):
    bl_parent_id = "ACON_PT_Styles"
    bl_idname = "ACON_PT_Edge_Sub"
    bl_label = "Line"
    bl_category = "Style"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

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


classes = (Acon3dStylePanel, LinePanel)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
