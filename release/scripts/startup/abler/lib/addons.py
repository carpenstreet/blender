import bpy


addons = [
    "io_anim_bvh",
    "io_curve_svg",
    "io_mesh_ply",
    "io_mesh_stl",
    "io_scene_gltf2",
    "io_scene_obj",
    "io_scene_x3d",
]


def disable_preference_addons():
    prefs_context = bpy.context.preferences
    prefs_ops = bpy.ops.preferences

    for addon in addons:
        if prefs_context.addons.find(addon) != -1:
            prefs_ops.addon_disable(module=addon)
