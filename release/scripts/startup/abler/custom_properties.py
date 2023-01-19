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


import bpy
from math import radians
from .lib import scenes, cameras, shadow, objects, bloom, version
from .lib.layers import get_first_layer_name_of_object
from .lib.materials import materials_handler
from .lib.read_cookies import *
from .scene_tab import object_control


class AconSceneColGroupProperty(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Scenes",
        description="Click to apply and double click to rename.",
        default="",
        update=scenes.change_scene_name,
    )

    index: bpy.props.IntProperty()

    is_render_selected: bpy.props.BoolProperty(
        name="Scene List",
        description="Select scene to render",
    )


class AconWindowManagerProperty(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.WindowManager.ACON_prop = bpy.props.PointerProperty(
            type=AconWindowManagerProperty
        )

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.ACON_prop

    scene: bpy.props.EnumProperty(
        name="Scene",
        description="Change scene",
        items=scenes.add_scene_items,
        update=scenes.load_scene,
    )

    hide_low_version_warning: bpy.props.BoolProperty(
        # name="Hide Low Version Warning",
        name="",
        description="Don't show this message again",
        default=False,
        update=version.remember_low_version_warning_hidden,
    )

    scene_col: bpy.props.CollectionProperty(type=AconSceneColGroupProperty)

    active_scene_index: bpy.props.IntProperty(
        update=scenes.load_scene_by_index, name="Scene"
    )

    hq_render_full: bpy.props.BoolProperty(
        name="Full Render",
        description="Render according to the set pixel",
        default=True,
    )
    hq_render_line: bpy.props.BoolProperty(
        name="Line Render",
        description="Render only lines according to the set pixel",
        default=True,
    )
    hq_render_texture: bpy.props.BoolProperty(
        name="Texture Render",
        description="Render only textures according to the set pixel",
        default=True,
    )
    hq_render_shadow: bpy.props.BoolProperty(
        name="Shadow Render",
        description="Render only shadow according to the set pixel",
        default=True,
    )


class CollectionLayerExcludeProperties(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Scene.l_exclude = bpy.props.CollectionProperty(
            type=CollectionLayerExcludeProperties
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.l_exclude

    def update_layer_visibility(self, context):
        l_exclude = bpy.context.scene.l_exclude
        target_layer = bpy.data.collections[self.name]

        visited = set()

        # 시작 오브젝트의 부모 오브젝트의 상태
        def get_parent_value(obj):
            cur = obj.parent
            while cur:
                if cur.hide_viewport:
                    return False
                cur = cur.parent
            return True

        # 부모 오브젝트 off => 항상 off,  부모 오브젝트 on => 현재 값으로 결정
        def update_objects(obj, value: bool):
            if obj.name in visited:
                return
            visited.add(obj.name)

            if value:
                for l in l_exclude:
                    if l.name == get_first_layer_name_of_object(obj) and not l.value:
                        value = False
                        break

            obj.hide_viewport = not value
            obj.hide_render = not value

            for o in obj.children:
                update_objects(o, value)

        for obj in target_layer.objects:
            value = get_parent_value(obj) and self.value
            update_objects(obj, value)

    def update_layer_lock(self, context):
        l_exclude = bpy.context.scene.l_exclude
        target_layer = bpy.data.collections[self.name]

        visited = set()

        # 시작 오브젝트의 부모 오브젝트의 상태
        def get_parent_lock(obj):
            cur = obj.parent
            while cur:
                if cur.hide_select:
                    return True
                cur = cur.parent
            return False

        # 부모 오브젝트 off => 항상 off,  부모 오브젝트 on => 현재 값으로 결정
        def update_objects(obj, lock: bool):
            if obj.name in visited:
                return
            visited.add(obj.name)

            if not lock:
                for l in l_exclude:
                    if l.name == get_first_layer_name_of_object(obj) and l.lock:
                        lock = True
                        break

            obj.hide_select = lock

            for o in obj.children:
                update_objects(o, lock)

        for obj in target_layer.objects:
            lock = get_parent_lock(obj) or self.lock
            update_objects(obj, lock)

    name: bpy.props.StringProperty(name="Layer Name", default="")

    value: bpy.props.BoolProperty(
        name="Layer Exclude",
        description="Choose if the objects in the current layer visible in the viewport or not",
        default=True,
        update=update_layer_visibility,
    )

    lock: bpy.props.BoolProperty(
        name="Layer Lock",
        description="Choose if the objects in the current layer lock in the viewport or not",
        default=False,
        update=update_layer_lock,
    )


class AconSceneSelectedGroupProperty(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Scene.ACON_selected_group = bpy.props.PointerProperty(
            type=AconSceneSelectedGroupProperty
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.ACON_selected_group

    current_root_group: bpy.props.StringProperty(
        name="Current Selected Root Group", default=""
    )
    current_group: bpy.props.StringProperty(name="Current Selected Group", default="")
    direction: bpy.props.EnumProperty(
        name="Level Direction",
        description="Change order of collection level",
        items=[
            ("UP", "up", "Level Up"),
            ("DOWN", "down", "Level Down"),
            ("TOP", "top", "Level Top"),
            ("BOTTOM", "bottom", "Level bottom"),
        ],
    )


class AconSceneProperty(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Scene.ACON_prop = bpy.props.PointerProperty(type=AconSceneProperty)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.ACON_prop

    toggle_toon_edge: bpy.props.BoolProperty(
        # name="Toon Style Edge",
        name="",
        description="Express toon style line profile",
        default=True,
        update=materials_handler.toggle_toon_edge,
    )

    edge_min_line_width: bpy.props.FloatProperty(
        # name="Min Line Width",
        name="",
        description="Adjust the thickness of minimum depth edges (Range: 0 ~ 5)",
        subtype="PIXEL",
        default=1,
        min=0,
        max=5,
        step=1,
        update=materials_handler.change_line_props,
    )

    edge_max_line_width: bpy.props.FloatProperty(
        # name="Max Line Width",
        name="",
        description="Adjust the thickness of maximum depth edges (Range: 0 ~ 5)",
        subtype="PIXEL",
        default=1,
        min=0,
        max=5,
        step=1,
        update=materials_handler.change_line_props,
    )

    edge_line_detail: bpy.props.FloatProperty(
        # name="Line Detail",
        name="",
        description="Adjust amount of edges to be shown (Range: 0 ~ 20, Recommended: 1.2)",
        subtype="FACTOR",
        default=1,
        min=0,
        max=20,
        step=10,
        update=materials_handler.change_line_props,
    )

    toggle_toon_face: bpy.props.BoolProperty(
        # name="Toon Style Face",
        name="",
        description="Express toon style face",
        default=True,
        update=materials_handler.toggle_toon_face,
    )

    toggle_texture: bpy.props.BoolProperty(
        # name="Texture",
        name="",
        description="Express material texture",
        default=True,
        update=materials_handler.toggle_texture,
    )

    toggle_shading: bpy.props.BoolProperty(
        # name="Shading",
        name="",
        description="Express shading",
        default=True,
        update=materials_handler.toggle_shading,
    )

    toon_shading_depth: bpy.props.EnumProperty(
        name="Toon Color Depth",
        description="Change number of colors used for shading",
        items=[("2", "2 depth", ""), ("3", "3 depth", "")],
        default="3",
        update=materials_handler.change_toon_depth,
    )

    toon_shading_brightness_1: bpy.props.FloatProperty(
        # name="Brightness 1",
        name="",
        description="Change shading brightness (Range: 0 ~ 10)",
        subtype="FACTOR",
        default=3,
        min=0,
        max=10,
        step=1,
        update=materials_handler.change_toon_shading_brightness,
    )

    toon_shading_brightness_2: bpy.props.FloatProperty(
        # name="Brightness 2",
        name="",
        description="Change shading brightness (Range: 0 ~ 10)",
        subtype="FACTOR",
        default=5,
        min=0,
        max=10,
        step=1,
        update=materials_handler.change_toon_shading_brightness,
    )

    view: bpy.props.EnumProperty(
        name="View",
        items=cameras.add_view_items_from_collection,
        update=cameras.go_to_custom_camera,
    )

    toggle_sun: bpy.props.BoolProperty(
        # name="Sun Light",
        name="",
        description="Express sunlight",
        default=True,
        update=shadow.toggle_sun,
    )

    sun_strength: bpy.props.FloatProperty(
        # name="Strength",
        name="",
        description="Control the strength of sunlight (Range: 0 ~ 10)",
        subtype="FACTOR",
        default=1.5,
        min=0,
        max=10,
        step=1,
        update=shadow.change_sun_strength,
    )

    toggle_shadow_shading: bpy.props.BoolProperty(
        name="",
        description="Express shadow and shading",
        default=True,
        update=shadow.toggle_shadow_shading,
    )

    toggle_shadow: bpy.props.BoolProperty(
        # name="Shadow",
        name="",
        description="Express shadow",
        default=True,
        update=shadow.toggle_shadow,
    )

    sun_rotation_x: bpy.props.FloatProperty(
        # name="Altitude",
        name="",
        description="Adjust sun altitude",
        subtype="ANGLE",
        unit="ROTATION",
        step=100,
        default=radians(20),
        update=shadow.change_sun_rotation,
    )

    sun_rotation_z: bpy.props.FloatProperty(
        # name="Azimuth",
        name="",
        description="Adjust sun azimuth",
        subtype="ANGLE",
        unit="ROTATION",
        step=100,
        default=radians(130),
        update=shadow.change_sun_rotation,
    )

    image_adjust_brightness: bpy.props.FloatProperty(
        # name="Brightness",
        name="",
        description="Adjust the overall brightness (Range: -1 ~ 1)",
        subtype="FACTOR",
        default=0,
        min=-1,
        max=1,
        step=1,
        update=materials_handler.change_image_adjust_brightness,
    )

    image_adjust_contrast: bpy.props.FloatProperty(
        # name="Contrast",
        name="",
        description="Adjust the overall contrast (Range: -1 ~ 1)",
        subtype="FACTOR",
        default=0,
        min=-1,
        max=1,
        step=1,
        update=materials_handler.change_image_adjust_contrast,
    )

    image_adjust_color_r: bpy.props.FloatProperty(
        # name="Red",
        name="",
        description="Adjust color balance (Range: 0 ~ 2)",
        subtype="FACTOR",
        default=1,
        min=0,
        max=2,
        step=1,
        update=materials_handler.change_image_adjust_color,
    )

    image_adjust_color_g: bpy.props.FloatProperty(
        # name="Green",
        name="",
        description="Adjust color balance (Range: 0 ~ 2)",
        subtype="FACTOR",
        default=1,
        min=0,
        max=2,
        step=1,
        update=materials_handler.change_image_adjust_color,
    )

    image_adjust_color_b: bpy.props.FloatProperty(
        # name="Blue",
        name="",
        description="Adjust color balance (Range: 0 ~ 2)",
        subtype="FACTOR",
        default=1,
        min=0,
        max=2,
        step=1,
        update=materials_handler.change_image_adjust_color,
    )

    image_adjust_hue: bpy.props.FloatProperty(
        # name="Hue",
        name="",
        description="Adjust hue (Range: 0 ~ 1)",
        subtype="FACTOR",
        default=0.5,
        min=0,
        max=1,
        step=1,
        update=materials_handler.change_image_adjust_hue,
    )

    image_adjust_saturation: bpy.props.FloatProperty(
        # name="Saturation",
        name="",
        description="Adjust saturation (Range: 0 ~ 2)",
        subtype="FACTOR",
        default=1,
        min=0,
        max=2,
        step=1,
        update=materials_handler.change_image_adjust_saturation,
    )

    exposure: bpy.props.FloatProperty(
        # name="Exposure",
        name="",
        description="Adjust the overall exposure and light up indoor space along with gamma (range: -10 ~ 10)",
        subtype="FACTOR",
        default=0.0,
        min=-10,
        max=10,
        update=materials_handler.change_exposure,
    )

    gamma: bpy.props.FloatProperty(
        # name="Gamma",
        name="",
        description="Adjust the overall gamma value and light up indoor space along with exposure (range: 0 ~ 5)",
        subtype="FACTOR",
        default=1.0,
        min=0,
        max=5,
        update=materials_handler.change_gamma,
    )

    selected_objects_str: bpy.props.StringProperty(name="Selected Objects")

    use_dof: bpy.props.BoolProperty(
        # name="Depth of Field",
        name="",
        description="Blur objects at a certain distance using the values set below",
        default=False,
        update=scenes.change_dof,
    )

    show_background_images: bpy.props.BoolProperty(
        # name="Background Images",
        name="",
        description="Add images to the front and rear of the model",
        default=False,
        update=scenes.change_background_images,
    )

    use_bloom: bpy.props.BoolProperty(
        # name="Bloom",
        name="",
        description="Create a shining effect with high luminance pixels",
        default=True,
        update=scenes.change_bloom,
    )

    bloom_threshold: bpy.props.FloatProperty(
        name="",
        description="Filter out pixels under this level of brightness (Range: 0 ~ 10)",
        default=1.0,
        min=0,
        max=10.0,
        update=bloom.change_bloom_threshold,
    )

    bloom_knee: bpy.props.FloatProperty(
        name="",
        description="Make transition between under/over-threshold (Range: 0 ~ 1)",
        default=0.5,
        min=0,
        max=1.0,
        update=bloom.change_bloom_knee,
    )

    bloom_radius: bpy.props.FloatProperty(
        name="",
        description="Adjust spreading distance of bloom effect (Range: 0 ~ 10)",
        default=4.0,
        min=0,
        max=10.0,
        update=bloom.change_bloom_radius,
    )

    bloom_color: bpy.props.FloatVectorProperty(
        name="",
        description="Select color of bloom effect",
        subtype="COLOR",
        default=(1.0, 1.0, 1.0),
        min=0,
        max=1.0,
        update=bloom.change_bloom_color,
    )

    bloom_intensity: bpy.props.FloatProperty(
        name="",
        description="Change bloom intensity (Range: 0 ~ 1)",
        default=0.5,
        min=0,
        max=1.0,
        update=bloom.change_bloom_intensity,
    )

    bloom_clamp: bpy.props.FloatProperty(
        name="",
        description="Adjust maximum intensity of bloom effect that each pixel can have (0 to disable) (Range: 0 ~ 1000)",
        default=0,
        min=0,
        max=1000.0,
        update=bloom.change_bloom_clamp,
    )

    background_color: bpy.props.FloatVectorProperty(
        name="",
        description="Change background color",
        subtype="COLOR",
        default=(1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        update=scenes.change_background_color,
    )


class AconMaterialProperty(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Material.ACON_prop = bpy.props.PointerProperty(
            type=AconMaterialProperty
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Material.ACON_prop

    type: bpy.props.EnumProperty(
        name="Type",
        description="Select material type",
        items=[
            ("Diffuse", "Diffuse", ""),
            ("Mirror", "Reflection", ""),
            ("Glow", "Emission", ""),
            ("Clear", "Transparent", ""),
        ],
        update=materials_handler.change_material_type,
    )

    toggle_shadow: bpy.props.BoolProperty(
        name="Shadow",
        description="Exclude shadow of selected object",
        default=True,
        update=materials_handler.toggle_each_shadow,
    )

    toggle_shading: bpy.props.BoolProperty(
        name="Shading",
        description="Exclude shading of selected object",
        default=True,
        update=materials_handler.toggle_each_shading,
    )

    toggle_edge: bpy.props.BoolProperty(
        name="Line",
        description="Exclude line of selected object",
        default=True,
        update=materials_handler.toggle_each_edge,
    )


class AconMetadataProperty(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        # TODO: 만약 text 안 쓰고 다른 걸 쓸거라면 fake user 체크 필요
        bpy.types.Text.ACON_metadata = bpy.props.PointerProperty(
            type=AconMetadataProperty
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Text.ACON_metadata

    file_version: bpy.props.StringProperty(name="File Version")


class AconMeshProperty(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Mesh.ACON_prop = bpy.props.PointerProperty(type=AconMeshProperty)

    @classmethod
    def unregister(cls):
        del bpy.types.Mesh.ACON_prop

    def toggle_show_password(self, context):
        if self.show_password:
            self.password_shown = self.password
        else:
            self.password = self.password_shown

    username: bpy.props.StringProperty(name="Username", description="Insert username")

    password: bpy.props.StringProperty(
        name="Password", description="Insert password", subtype="PASSWORD"
    )

    password_shown: bpy.props.StringProperty(
        name="Password", description="Password", subtype="NONE"
    )

    show_password: bpy.props.BoolProperty(
        name="Show Password",
        description="Show password (Use only in private environment)",
        default=False,
        update=toggle_show_password,
    )

    # TODO: description 달기
    remember_username: bpy.props.BoolProperty(
        name="Remember Username",
        description="Autofill this username next time",
        default=True,
    )

    login_status: bpy.props.StringProperty(
        name="Login Status",
        description="Login Status",
    )

    show_guide: bpy.props.BoolProperty(
        name="",
        description="Always show tutorial guide when starting ABLER",
        default=True,
        update=remember_show_guide,
    )


class AconObjectGroupProperty(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Group", description="Group", default="")


class AconObjectStateProperty(bpy.types.PropertyGroup):

    location: bpy.props.FloatVectorProperty(
        name="location", description="location", subtype="TRANSLATION", unit="LENGTH"
    )
    rotation_euler: bpy.props.FloatVectorProperty(
        name="rotation", description="rotation", subtype="EULER", unit="ROTATION"
    )
    scale: bpy.props.FloatVectorProperty(name="scale", description="scale")


class AconObjectProperty(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Object.ACON_prop = bpy.props.PointerProperty(type=AconObjectProperty)

    @classmethod
    def unregister(cls):
        del bpy.types.Object.ACON_prop

    def get_location_x(self, context):
        return context.selected_objects[0].location[0]

    group: bpy.props.CollectionProperty(type=AconObjectGroupProperty)

    group_list: bpy.props.EnumProperty(
        name="",
        items=object_control.add_group_list_from_collection,
    )

    constraint_to_camera_rotation_z: bpy.props.BoolProperty(
        # name="Look at me",
        name="",
        description="Set object to look camera",
        default=False,
        update=objects.toggle_constraint_to_camera,
    )

    use_state: bpy.props.BoolProperty(
        # name="Use State",
        name="",
        description="Move object using the preset state information and the slider below",
        default=False,
        update=objects.toggle_use_state,
    )

    state_exists: bpy.props.BoolProperty(
        name="Determine if state is created", default=False
    )

    state_slider: bpy.props.FloatProperty(
        name="State Slider",
        description="",
        default=0,
        min=0,
        max=1,
        step=1,
        update=objects.move_state,
    )

    state_begin: bpy.props.PointerProperty(type=AconObjectStateProperty)

    state_end: bpy.props.PointerProperty(type=AconObjectStateProperty)

    location_x: bpy.props.FloatProperty(
        name="x",
        update=objects.edit_state,
        get=get_location_x,
    )

    location_y: bpy.props.FloatProperty(
        name="y",
        update=objects.edit_state,
    )

    location_z: bpy.props.FloatProperty(
        name="z",
        update=objects.edit_state,
    )

    scale_x: bpy.props.FloatProperty(
        name="x",
        update=objects.edit_state,
    )

    scale_y: bpy.props.FloatProperty(
        name="y",
        update=objects.edit_state,
    )

    scale_z: bpy.props.FloatProperty(
        name="z",
        update=objects.edit_state,
    )

    rotate_x: bpy.props.FloatProperty(
        name="x",
        update=objects.edit_state,
    )

    rotate_y: bpy.props.FloatProperty(
        name="y",
        update=objects.edit_state,
    )

    rotate_z: bpy.props.FloatProperty(
        name="z",
        update=objects.edit_state,
    )


classes = (
    AconSceneColGroupProperty,
    AconWindowManagerProperty,
    CollectionLayerExcludeProperties,
    AconSceneSelectedGroupProperty,
    AconSceneProperty,
    AconMaterialProperty,
    AconMeshProperty,
    AconObjectGroupProperty,
    AconObjectStateProperty,
    AconObjectProperty,
    AconMetadataProperty,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
