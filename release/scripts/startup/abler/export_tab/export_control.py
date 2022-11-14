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
from time import time, strftime, localtime, gmtime


class RENDER_UL_List(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            layout.separator()
            layout.prop(item, "is_render_selected", text="")
            layout.prop(item, "name", text="", emboss=False)


# TODO Util 함수 어디에 넣어야 할지 확인
def timestamp_to_string(timestamp, is_date=True):
    if not timestamp:
        return "- - -"
    if is_date:
        return strftime("%Y-%m-%d %H:%M:%S", localtime(timestamp))
    return strftime("%H:%M:%S", gmtime(timestamp))


class Acon3dHighQualityRenderPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""

    bl_idname = "ACON3D_PT_high_quality_render"
    bl_label = "High-Quality Render"
    bl_category = "Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"
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
            row.prop(
                render_prop, "hq_render_full", text="Full Render", text_ctxt="abler"
            )
            row = col.row()
            row.prop(
                render_prop,
                "hq_render_texture",
                text="Texture Render",
                text_ctxt="abler",
            )
            row = col.row()
            row.prop(
                render_prop, "hq_render_line", text="Line Render", text_ctxt="abler"
            )
            row = col.row()
            row.prop(
                render_prop, "hq_render_shadow", text="Shadow Render", text_ctxt="abler"
            )
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

            self.draw_progress(context, layout)

    def draw_progress_skeleton(self, infos, layout):
        box = layout.box()
        box.label(text="Total Rendering")
        sub = box.split(align=True, factor=0.20)
        col = sub.column(align=True)
        col.label(text=f"0 / 0")
        col = sub.column(align=True)
        col.template_progress_bar(progress=0.0)

        for info in infos:
            box.label(text=info.render_scene_name)
            box.template_progress_bar(progress=0.0)

        sub = box.split(align=True, factor=0.25)

        col = sub.column(align=True)
        col.label(text="Start", icon="DOT")
        col.label(text="Finish", icon="DOT")
        col.label(text="Time Span", icon="DOT")

        col = sub.column(align=True)
        col.label(text=": - - -")
        col.label(text=": - - -")
        col.label(text=": - - -")

        layout.operator("acon3d.close_progress", text="OK")

    def draw_progress(self, context, layout):
        progress_prop = context.window_manager.progress_prop
        if progress_prop.is_loaded:
            self.draw_progress_skeleton(progress_prop.render_scene_infos, layout)
            return

        if not progress_prop.start_date:
            return

        box = layout.box()

        cur_progress = context.window_manager.get_progress()

        render_progress = 0
        if progress_prop.total_render_num:
            render_progress = (
                progress_prop.complete_num + cur_progress
            ) / progress_prop.total_render_num

        box.label(text="Total Rendering")
        sub = box.split(align=True, factor=0.20)
        col = sub.column(align=True)
        col.label(
            text=f"{min(progress_prop.complete_num + 1, progress_prop.total_render_num)} / {progress_prop.total_render_num} "
        )
        col = sub.column(align=True)
        col.template_progress_bar(progress=render_progress)

        for info in progress_prop.render_scene_infos:
            col = box.column()
            col.scale_y = 0.8
            col.label(text=info.render_scene_name)
            if info.status == "waiting":
                col.template_progress_bar(progress=0.0)
            elif info.status == "in progress":
                col.template_progress_bar(progress=cur_progress)
            else:
                col.template_progress_bar(progress=1.0)

        sub = box.split(align=True, factor=0.25)

        col = sub.column(align=True)
        col.label(text="Start", icon="DOT")
        col.label(text="Finish", icon="DOT")
        col.label(text="Time Span", icon="DOT")

        start_string = timestamp_to_string(progress_prop.start_date)
        end_string = timestamp_to_string(progress_prop.end_date)

        if not progress_prop.start_date:
            span = 0
        elif not progress_prop.end_date:
            span = time() - progress_prop.start_date
        else:
            span = progress_prop.end_date - progress_prop.start_date
        span_string = timestamp_to_string(span, is_date=False)

        col = sub.column(align=True)
        col.label(text=": " + start_string)
        col.label(text=": " + end_string)
        col.label(text=": " + span_string)

        layout.operator("acon3d.close_progress", text="OK")


class Acon3dQuickRenderPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""

    bl_idname = "ACON3D_PT_quick_render"
    bl_label = "Quick Render"
    bl_category = "Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"
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
        row.operator("acon3d.render_quick", text="Render Viewport")


class Acon3dSnipRenderPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""

    bl_idname = "ACON3D_PT_snip_render"
    bl_label = "Snip Render"
    bl_category = "Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"
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
        row.operator("acon3d.render_snip", text="Render Viewport")


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
