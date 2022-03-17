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
from .lib import layers


class Acon3dCreateGroupOperator(bpy.types.Operator):
    """Create Group"""

    bl_idname = "acon3d.create_group"
    bl_label = "Create Group"
    bl_translation_context = "*"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        collection = bpy.data.collections.get("Groups")
        if not collection:
            collection = bpy.data.collections.new("Groups")
            context.scene.collection.children.link(collection)
            layer_collection = context.view_layer.layer_collection
            layer_collection.children.get("Groups").exclude = True

        col_group = bpy.data.collections.new("ACON_group")
        collection.children.link(col_group)

        for obj in context.selected_objects:
            group_props = obj.ACON_prop.group
            last_group = None
            if len(group_props):
                last_group_prop = group_props[-1]
                last_group = bpy.data.collections.get(last_group_prop.name)

            if last_group:
                if last_group.name in collection.children.keys():
                    collection.children.unlink(last_group)
                if last_group.name not in col_group.children.keys():
                    col_group.children.link(last_group)
            else:
                col_group.objects.link(obj)

            new_group_prop = obj.ACON_prop.group.add()
            new_group_prop.name = col_group.name

        return {"FINISHED"}


class Acon3dExplodeGroupOperator(bpy.types.Operator):
    """Explode Group"""

    bl_idname = "acon3d.explode_group"
    bl_label = "Explode Group"
    bl_translation_context = "*"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        for selected_object in context.selected_objects:

            group_props = selected_object.ACON_prop.group

            if not len(group_props):
                continue

            last_group_prop = group_props[-1]

            root_group = bpy.data.collections.get("Groups")
            if not root_group:
                root_group = bpy.data.collections.new("Groups")
                context.scene.collection.children.link(root_group)
                layer_collection = context.view_layer.layer_collection
                layer_collection.children.get("Groups").exclude = True

            if selected_group := bpy.data.collections.get(last_group_prop.name):
                for child in selected_group.children:
                    root_group.children.link(child)
                bpy.data.collections.remove(selected_group)

            group_props.remove(len(group_props) - 1)

        return {"FINISHED"}


class Acon3dLayerPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""

    bl_idname = "ACON3D_PT_Layer"
    bl_label = "Layer"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="OUTLINER")

    def _draw_collection(
        self, layout, view_layer, use_local_collections, collection, index
    ):
        findex = 0
        for child in collection.children:
            index += 1

            if child.name == "Layer0":
                findex += 1
                continue

            l_exclude = bpy.context.scene.l_exclude

            if findex > len(l_exclude) - 1:
                break

            target = l_exclude[findex]

            icon = "OUTLINER_COLLECTION"
            icon_vis = "HIDE_OFF" if target.value else "HIDE_ON"
            icon_lock = "UNLOCKED" if not target.lock else "LOCKED"
            row = layout.row()
            row.use_property_decorate = False
            sub = row.split(factor=0.98)
            subrow = sub.row()
            subrow.alignment = "LEFT"
            subrow.label(text=child.name, icon=icon)

            sub = row.split()
            subrow = sub.row(align=True)
            subrow.alignment = "RIGHT"
            subrow.prop(
                target,
                "value",
                text="",
                icon=icon_vis,
                emboss=False,
                invert_checkbox=True,
            )
            subrow.prop(target, "lock", text="", icon=icon_lock, emboss=False)
            findex += 1

        return index

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        box = layout.box()

        view = context.space_data
        view_layer = context.view_layer

        if "Layers" in view_layer.layer_collection.children:

            self._draw_collection(
                box,
                view_layer,
                view.use_local_collections,
                view_layer.layer_collection.children["Layers"],
                1,
            )


classes = (
    Acon3dCreateGroupOperator,
    Acon3dExplodeGroupOperator,
    Acon3dLayerPanel,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    # layers.subscribeToGroupedObjects()


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    # layers.clearSubscribers()
