import bpy


enable_addons = ["io_skp"]
disable_addons = [
    "io_anim_bvh",
    "io_curve_svg",
    "io_mesh_ply",
    "io_mesh_stl",
    "io_scene_gltf2",
    "io_scene_obj",
    "io_scene_x3d",
]


def manage_preferences_addons():
    prefs_context = bpy.context.preferences
    prefs_ops = bpy.ops.preferences

    # 활성 addons
    for addon in enable_addons:
        if addon not in prefs_context.addons:
            prefs_ops.addon_enable(module=addon)

    # 비활성 addons
    for addon in disable_addons:
        if addon in prefs_context.addons:
            prefs_ops.addon_disable(module=addon)
