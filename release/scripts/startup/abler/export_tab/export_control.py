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


class RENDER_UL_List(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            layout.separator()
            layout.prop(item, "is_render_selected", text="")
            layout.prop(item, "name", text="", emboss=False)


class Acon3dHighQualityRenderPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""

    bl_idname = "ACON3D_PT_high_quality_render"
    bl_label = "High Quality Render"
    bl_category = "Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    COMPAT_ENGINES = {"BLENDER_RENDER", "BLENDER_EEVEE", "BLENDER_WORKBENCH"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="RENDERLAYERS")

    def draw(self, context):
        if bpy.context.scene.camera:
            scene = context.scene

            layout = self.layout

            row = layout.row(align=True)
            row.use_property_split = True
            row.use_property_decorate = False
            row.operator("acon3d.camera_view", text="", icon="RESTRICT_VIEW_OFF")
            row.prop(scene.render, "resolution_x", text="")
            row.prop(scene.render, "resolution_y", text="")
            render_prop = context.window_manager.ACON_prop
            row = layout.row()
            col = row.column()
            row = col.row()
            row.prop(render_prop, "hq_render_full", text="Full Render")
            row = col.row()
            row.prop(render_prop, "hq_render_texture", text="Texture Render")
            row = col.row()
            row.prop(render_prop, "hq_render_line", text="Line Render")
            row = col.row()
            row.prop(render_prop, "hq_render_shadow", text="Shadow Render")
            col.template_list(
                "RENDER_UL_List",
                "",
                render_prop,
                "scene_col",
                render_prop,
                "active_scene_index",
            )
            row = layout.row()
            count = 0
            render_prop = context.window_manager.ACON_prop
            for s_col in render_prop.scene_col:
                if s_col.is_render_selected and s_col.name in bpy.data.scenes:
                    count += 1
            opr = row.operator("acon3d.render_warning")
            opr.scene_count = count

            # 변경한 뷰포트 색이 같이 렌더되는 기능과 함께 들어가기로 논의되었습니다.
            # 그 전까지 주석처리 해두겠습니다.
            # 해당 이슈 링크: https://www.notion.so/acon3d/Issue-37_-af9ca441b3c44e858097418fb6dc811c
            # row = layout.row()
            # prop = context.scene.ACON_prop
            # row.prop(prop, "background_color", text="Background Color")


class Acon3dQuickRenderPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""

    bl_idname = "ACON3D_PT_quick_render"
    bl_label = "Quick Render"
    bl_category = "Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    COMPAT_ENGINES = {"BLENDER_RENDER", "BLENDER_EEVEE", "BLENDER_WORKBENCH"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="RESTRICT_RENDER_OFF")

    def draw(self, context):
        scene = context.scene

        layout = self.layout
        row = layout.row(align=True)
        row.use_property_split = True
        row.use_property_decorate = False
        row.operator("acon3d.camera_view", text="", icon="RESTRICT_VIEW_OFF")
        row.prop(scene.render, "resolution_x", text="")
        row.prop(scene.render, "resolution_y", text="")
        row = layout.row()
        row.operator("acon3d.render_quick", text="Render Viewport", text_ctxt="*")


class Acon3dSnipRenderPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""

    bl_idname = "ACON3D_PT_snip_render"
    bl_label = "Snip Render"
    bl_category = "Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    COMPAT_ENGINES = {"BLENDER_RENDER", "BLENDER_EEVEE", "BLENDER_WORKBENCH"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="XRAY")

    def draw(self, context):
        scene = context.scene

        layout = self.layout
        row = layout.row(align=True)
        row.use_property_split = True
        row.use_property_decorate = False
        row.operator("acon3d.camera_view", text="", icon="RESTRICT_VIEW_OFF")
        row.prop(scene.render, "resolution_x", text="")
        row.prop(scene.render, "resolution_y", text="")
        row = layout.row()
        row.operator("acon3d.render_snip", text="Render Viewport", text_ctxt="*")


classes = (
    Acon3dHighQualityRenderPanel,
    Acon3dQuickRenderPanel,
    Acon3dSnipRenderPanel,
    RENDER_UL_List,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
