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


import bpy, platform, os, subprocess, datetime
from ..lib import render, cameras
from ..lib.file_view import file_view_title
from ..lib.materials import materials_handler
from ..lib.tracker import tracker
from time import time
from ..warning_modal import BlockingModalOperator
from ..lib.import_file import AconImportHelper, AconExportHelper


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


def open_directory(path):

    if platform.system() == "Windows":

        FILEBROWSER_PATH = os.path.join(os.getenv("WINDIR"), "explorer.exe")
        path = os.path.normpath(path)

        if os.path.isdir(path):
            subprocess.run([FILEBROWSER_PATH, path])
        elif os.path.isfile(path):
            subprocess.run([FILEBROWSER_PATH, "/select,", os.path.normpath(path)])

    elif platform.system() == "Darwin":
        subprocess.call(["open", "-R", path])

    elif platform.system() == "Linux":
        print("Linux")


def check_file_numbering(self, context):
    base_filepath = os.path.join(self.dirname, self.basename)
    file_format = self.filename_ext
    numbered_filepath = base_filepath
    number = 2

    while os.path.isfile(f"{numbered_filepath}{file_format}"):
        numbered_filepath = f"{base_filepath} ({number})"
        number += 1

    context.scene.render.filepath = numbered_filepath
    self.filepath = f"{numbered_filepath}{file_format}"


class Acon3dCameraViewOperator(bpy.types.Operator):
    """Fit render region to viewport"""

    bl_idname = "acon3d.camera_view"
    bl_label = "Camera View"
    bl_translation_context = "abler"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        cameras.turn_on_camera_view()

        return {"FINISHED"}


class Acon3dRenderWarningOperator(BlockingModalOperator):
    bl_idname = "acon3d.render_warning"
    bl_label = "Render Selected Scenes"
    bl_description = "Render with high quality according to the set pixel"
    bl_translation_context = "abler"
    scene_count: bpy.props.IntProperty(name="Scene count", default=0)

    def draw_modal(self, layout):
        tr = bpy.app.translations.pgettext
        padding_size = 0.01
        content_size = 1.0 - 2 * padding_size
        box = layout.box()
        main = box.column()

        main.label(text="")

        row = main.split(factor=padding_size)
        row.label(text="")
        row = row.split(factor=content_size)
        col = row.column()
        col.label(text="Render Selected Scenes?")
        col.label(text="High quality render may take a long time to be finished.")
        col.label(
            text=tr("Selected Scenes: $(sceneCount)").replace(
                "$(sceneCount)", str(self.scene_count)
            )
        )
        if bpy.data.is_dirty:
            col.operator("acon3d.render_save", text="Save and Render")
        else:
            col.operator("acon3d.render_high_quality", text="Render", text_ctxt="abler")
        col.operator("acon3d.close_blocking_modal", text="Cancel", text_ctxt="abler")
        row.label(text="")

        main.label(text="")

    @classmethod
    def poll(self, context):
        render_prop = context.window_manager.ACON_prop

        is_method_selected = (
            render_prop.hq_render_full
            or render_prop.hq_render_line
            or render_prop.hq_render_texture
            or render_prop.hq_render_shadow
        )
        # 이 부분은 뺐다가 poll 실행 당시에 scene_count가 등록이 안되어있는 타이밍 문제때문에 에러메시지가 계속 떠서 그냥 다시 살림.
        is_scene_selected = any(s.is_render_selected for s in render_prop.scene_col)
        return is_method_selected and is_scene_selected


def render_save_handler(dummy):
    bpy.ops.acon3d.render_high_quality("INVOKE_DEFAULT")
    bpy.app.handlers.save_post.remove(render_save_handler)


class Acon3dRenderSaveOpertor(bpy.types.Operator):
    bl_idname = "acon3d.render_save"
    bl_label = "Save and Render"
    bl_description = "Save and render with high quality according to the set pixel"
    bl_translation_context = "abler"

    def execute(self, context):
        bpy.ops.acon3d.close_blocking_modal("INVOKE_DEFAULT")
        bpy.app.handlers.save_post.append(render_save_handler)
        return bpy.ops.acon3d.save("INVOKE_DEFAULT", is_render=True)


class Acon3dRenderOperator(bpy.types.Operator):

    show_on_completion: bpy.props.BoolProperty(
        name="Show in folder on completion", default=True
    )
    write_still = True
    render_queue = []
    rendering = False
    render_canceled = False
    timer_event = None
    initial_scene = None
    initial_display_type = None
    render_start_time = None

    def pre_render(self, dummy, dum):
        self.rendering = True

    def post_render(self, dummy, dum):
        if self.render_queue:
            self.render_queue.pop(0)
            self.rendering = False

    def on_render_cancel(self, dummy, dum):
        self.render_canceled = True

    def on_render_finish(self, context):
        # set initial_scene
        bpy.data.window_managers["WinMan"].ACON_prop.scene = self.initial_scene.name
        return {"FINISHED"}

    def prepare_queue(self, context):

        for scene in bpy.data.scenes:
            self.render_queue.append((None, scene))

        return {"RUNNING_MODAL"}

    def prepare_render(self):
        render.setup_background_images_compositor()
        render.match_object_visibility()

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        self.render_canceled = False
        self.rendering = False
        self.render_queue = []
        self.initial_scene = context.scene
        self.initial_display_type = context.preferences.view.render_display_type
        self.timer_event = context.window_manager.event_timer_add(
            0.2, window=context.window
        )

        context.preferences.view.render_display_type = "NONE"
        context.window_manager.modal_handler_add(self)

        bpy.app.handlers.render_pre.append(self.pre_render)
        bpy.app.handlers.render_post.append(self.post_render)
        bpy.app.handlers.render_cancel.append(self.on_render_cancel)

        return self.prepare_queue(context)

    def modal(self, context, event):
        return {"PASS_THROUGH"}


class Acon3dRenderQuickOperator(Acon3dRenderOperator, AconExportHelper):
    """Take a snapshot of the active viewport"""

    bl_idname = "acon3d.render_quick"
    bl_label = "Quick Render"
    bl_description = "Take a snapshot of the active viewport"
    bl_translation_context = "abler"

    filename_ext = ".png"
    filter_glob: bpy.props.StringProperty(default="*.png", options={"HIDDEN"})

    def __init__(self):
        AconExportHelper.__init__(self)
        scene = bpy.context.scene
        self.filepath = f"{scene.name}{self.filename_ext}"

    def invoke(self, context, event):
        with file_view_title("RENDER"):
            return super().invoke(context, event)

    def execute(self, context):
        self.check_path(
            save_check=False,
            default_name=f"{context.scene.name}{self.filename_ext}",
        )

        # Get basename without file extension
        self.dirname, self.basename = os.path.split(os.path.normpath(self.filepath))

        if "." in self.basename:
            self.basename = ".".join(self.basename.split(".")[:-1]).rstrip()

        return super().execute(context)

    def prepare_queue(self, context):
        # File name duplicate check

        check_file_numbering(self, context)

        for obj in context.selected_objects:
            obj.select_set(False)

        bpy.ops.render.opengl("INVOKE_DEFAULT", write_still=True)

        return {"RUNNING_MODAL"}

    def modal(self, context, event):

        if event.type == "TIMER":

            if not self.render_queue or self.render_canceled is True:

                bpy.app.handlers.render_pre.remove(self.pre_render)
                bpy.app.handlers.render_post.remove(self.post_render)
                bpy.app.handlers.render_cancel.remove(self.on_render_cancel)

                context.window_manager.event_timer_remove(self.timer_event)
                context.window.scene = self.initial_scene
                context.preferences.view.render_display_type = self.initial_display_type

                self.report({"INFO"}, "RENDER QUEUE FINISHED")

                bpy.ops.acon3d.alert(
                    "INVOKE_DEFAULT",
                    title="Render Queue Finished",
                    message_1="Rendered images are saved in:",
                    message_2=self.filepath,
                )

                if self.show_on_completion:
                    open_directory(self.filepath)

                return self.on_render_finish(context)

            elif self.rendering is False:

                check_file_numbering(self, context)

                self.prepare_render()

                bpy.ops.render.render("INVOKE_DEFAULT", write_still=self.write_still)

        return {"PASS_THROUGH"}

    def on_render_finish(self, context):
        tracker.render_quick()
        return super().on_render_finish(context)


class Acon3dRenderDirOperator(Acon3dRenderOperator, AconImportHelper):
    # Render Type : High Quality, Snip

    filter_glob: bpy.props.StringProperty(default="Folders", options={"HIDDEN"})

    def __init__(self):
        AconImportHelper.__init__(self)

        # Get basename without file extension
        self.filepath = bpy.context.blend_data.filepath

        if not self.filepath:
            self.filepath = "untitled"

        else:
            self.dirname, self.basename = os.path.split(os.path.normpath(self.filepath))

            if "." in self.basename:
                self.basename = ".".join(self.basename.split(".")[:-1]).rstrip()

            self.filepath = self.basename

    def execute(self, context):
        if not os.path.isdir(self.filepath) and os.path.isfile(self.filepath):
            bpy.ops.acon3d.alert(
                "INVOKE_DEFAULT",
                title="File Select Error",
                message_1="No selected file.",
            )
            return {"FINISHED"}
        return super().execute(context)

    def render_handler(self):
        progress_prop = bpy.context.window_manager.progress_prop
        progress_prop.is_loaded = False

        bpy.ops.render.render("INVOKE_DEFAULT", write_still=self.write_still)

        return None

    def modal(self, context, event):
        if event.type == "TIMER":

            if not self.render_queue or self.render_canceled is True:

                bpy.app.handlers.render_pre.remove(self.pre_render)
                bpy.app.handlers.render_post.remove(self.post_render)
                bpy.app.handlers.render_cancel.remove(self.on_render_cancel)

                context.window_manager.event_timer_remove(self.timer_event)
                context.window.scene = self.initial_scene
                context.preferences.view.render_display_type = self.initial_display_type

                self.report({"INFO"}, "RENDER QUEUE FINISHED")

                bpy.ops.acon3d.alert(
                    "INVOKE_DEFAULT",
                    title="Render Queue Finished",
                    message_1="Rendered images are saved in:",
                    message_2=self.filepath,
                )

                if self.show_on_completion:
                    open_directory(self.filepath)

                return self.on_render_finish(context)

            elif self.rendering is False:

                name_item, qitem, *_ = self.render_queue[0]
                if name_item:
                    dirname_temp = os.path.join(self.filepath, name_item)
                    if not os.path.exists(dirname_temp):
                        try:
                            os.makedirs(dirname_temp)
                        except FileNotFoundError:
                            bpy.ops.acon3d.alert(
                                "INVOKE_DEFAULT",
                                title="This file path does not exist",
                                message_1="Please select valid file path",
                            )
                        except OSError:
                            bpy.ops.acon3d.alert(
                                "INVOKE_DEFAULT",
                                title="Invalid Directory Name",
                                message_1="Please rewrite your directory name",
                            )
                else:
                    dirname_temp = self.filepath

                base_filepath = os.path.join(dirname_temp, qitem.name)
                file_format = qitem.render.image_settings.file_format
                numbered_filepath = base_filepath
                number = 2
                while os.path.isfile(f"{numbered_filepath}.{file_format}"):
                    numbered_filepath = f"{base_filepath} ({number})"
                    number += 1

                qitem.render.filepath = numbered_filepath
                context.window_manager.ACON_prop.scene = qitem.name

                self.prepare_render()

                """
                렌더 씬이 결정된 직후 ~ 렌더를 처음 시작했을 때 사이에 is_loaded = True 로 설정,
                is_loaded = True 일 때 스켈레톤 UI 를 그립니다.
                is_loaded 값이 순간적으로 변경되기 때문에 timers 에 등록하여 다른 큐에서 draw 를 실행하도록 하였습니다.
                (0초로 두면 draw 도중 잘리는 이슈가 있어서, 0.01초로 변경)
                """
                if context.window_manager.progress_prop.is_loaded:
                    bpy.app.timers.register(self.render_handler, first_interval=0.01)
                else:
                    bpy.ops.render.render(
                        "INVOKE_DEFAULT", write_still=self.write_still
                    )

        return {"PASS_THROUGH"}


class Acon3dRenderSnipOperator(Acon3dRenderDirOperator):
    """Render selected objects isolatedly from background"""

    bl_idname = "acon3d.render_snip"
    bl_label = "Snip Render"
    bl_translation_context = "abler"

    temp_scenes = []
    temp_layer = None
    temp_col = None
    temp_image = None

    @classmethod
    def poll(self, context):
        return len(context.selected_objects)

    def invoke(self, context, event):
        with file_view_title("RENDER"):
            return super().invoke(context, event)

    def prepare_render(self):
        if len(self.render_queue) == 3:
            render.clear_compositor()

        elif len(self.render_queue) == 2:
            shade_scene = self.temp_scenes[0]
            filename = (
                f"{shade_scene.name}.{shade_scene.render.image_settings.file_format}"
            )

            image_path = os.path.join(self.filepath, filename)
            self.temp_image = bpy.data.images.load(image_path)

            for mat in bpy.data.materials:
                materials_handler.set_material_parameters_by_type(mat)

            compNodes = render.clear_compositor()
            render.setup_background_images_compositor(*compNodes)
            render.setup_snip_compositor(
                *compNodes, snip_layer=self.temp_layer, shade_image=self.temp_image
            )

            os.remove(image_path)

        else:
            bpy.data.collections.remove(self.temp_col)
            bpy.data.images.remove(self.temp_image)
            render.setup_background_images_compositor()

        render.match_object_visibility()

    def prepare_queue(self, context):
        scene = context.scene.copy()
        self.render_queue.append((None, scene))
        self.temp_scenes.append(scene)

        scene.eevee.use_bloom = False
        scene.render.use_lock_interface = True

        for mat in bpy.data.materials:
            mat.blend_method = "OPAQUE"
            mat.shadow_method = "OPAQUE"
            if toonNode := mat.node_tree.nodes.get("ACON_nodeGroup_combinedToon"):
                toonNode.inputs[1].default_value = 0
                toonNode.inputs[3].default_value = 1

        scene = context.scene.copy()
        scene.name = f"{context.scene.name}_snipped"
        self.render_queue.append((None, scene))
        self.temp_scenes.append(scene)

        layer = scene.view_layers.new("ACON_layer_snip")
        self.temp_layer = layer
        for col in layer.layer_collection.children:
            col.exclude = True

        col_group = bpy.data.collections.new("ACON_group_snip")
        self.temp_col = col_group
        scene.collection.children.link(col_group)
        for obj in context.selected_objects:
            col_group.objects.link(obj)

        scene = context.scene.copy()
        scene.name = f"{context.scene.name}_full"
        self.render_queue.append((None, scene))
        self.temp_scenes.append(scene)

        return {"RUNNING_MODAL"}

    def on_render_finish(self, context):
        tracker.render_snip()

        for mat in bpy.data.materials:
            materials_handler.set_material_parameters_by_type(mat)

        for scene in self.temp_scenes:
            bpy.data.scenes.remove(scene)

        self.temp_scenes.clear()

        return super().on_render_finish(context)


class Acon3dRenderHighQualityOperator(Acon3dRenderDirOperator):
    """Render with high quality according to the set pixel"""

    bl_idname = "acon3d.render_high_quality"
    bl_label = "Render Selected Scenes"
    bl_translation_context = "abler"

    # 렌더를 위해 임시로 만들어진 scene list
    temp_scenes = []

    def __init__(self):
        super().__init__()

    def draw(self, context):
        super().draw(context)

        layout = self.layout
        box = layout.box()
        box.scale_y = 0.5
        box.use_property_split = True
        box.use_property_decorate = False
        box.label(
            icon="ERROR",
            text="Please select the path in",
        )
        box.label(
            text="which the rendered images",
        )
        box.label(
            text="will be saved.",
        )

    def invoke(self, context, event):
        bpy.ops.acon3d.close_blocking_modal("INVOKE_DEFAULT")
        with file_view_title("RENDER"):
            return super().invoke(context, event)

    def pre_render(self, dummy, dum):
        self.render_start_time = time()

        super().pre_render(dummy, dum)
        _, scene, render_type = self.render_queue[0]
        info = find_target_render_scene_info(
            scene.name, bpy.context.window_manager.progress_prop.render_scene_infos
        )
        if info:
            info.status = "in progress"

        # bpy.data.materials가 전체 씬에 대해 적용되기 때문에
        # 렌더 씬마다 적용하기 위해 재질의 상태를 렌더하기 전 pre_render에서 적용
        if render_type == "full":
            for mat in bpy.data.materials:  # scene
                materials_handler.set_material_parameters_by_type(mat)
        elif render_type == "line":
            for mat in bpy.data.materials:  # scene
                mat.blend_method = "OPAQUE"
                mat.shadow_method = "OPAQUE"
                if toonNode := mat.node_tree.nodes.get("ACON_nodeGroup_combinedToon"):
                    try:
                        toonNode.inputs[1].default_value = 0
                        toonNode.inputs[3].default_value = 1
                    except AttributeError:
                        bpy.ops.acon3d.alert(
                            "INVOKE_DEFAULT",
                            title="Please do not edit this node",
                            message_1="It may cause unexpected errors.",
                        )
        else:  # Shadow / Texture
            for mat in bpy.data.materials:  # scene
                if mat.ACON_prop.type == "Mirror":
                    mat.blend_method = "OPAQUE"
                    mat.shadow_method = "OPAQUE"
                    if toonNode := mat.node_tree.nodes.get(
                        "ACON_nodeGroup_combinedToon"
                    ):
                        toonNode.inputs[1].default_value = 0
                        toonNode.inputs[3].default_value = 1
                else:
                    materials_handler.set_material_parameters_by_type(mat)

    def post_render(self, dummy, dum):
        base_scene_name, scene, render_type = self.render_queue[0]
        render_time = str(
            datetime.timedelta(seconds=round(time() - self.render_start_time))
        )
        render_data = {
            "Scene": base_scene_name,
            "Filepath": bpy.data.filepath,
            "Render time": render_time,
        }

        if render_type == "full":
            tracker.render_full(render_data)

        elif render_type == "line":
            tracker.render_line(render_data)

        elif render_type == "shadow":
            tracker.render_shadow(render_data)

        elif render_type == "texture":
            tracker.render_texture(render_data)

        progress_prop = bpy.context.window_manager.progress_prop
        info = find_target_render_scene_info(
            scene.name, bpy.context.window_manager.progress_prop.render_scene_infos
        )
        if info:
            info.status = "finished"
        progress_prop.complete_num += 1
        super().post_render(dummy, dum)

    def prepare_render(self):
        _, _, render_type = self.render_queue[0]
        compNodes = render.clear_compositor()
        if render_type == "full":
            render.setup_background_images_compositor(*compNodes)
        render.match_object_visibility()

    # render_type - line, shadow, texture
    def prepare_temp_scene(self, base_scene, render_type: str):
        scene = base_scene.copy()
        # 현재 씬을 복사한 씬으로 적용
        bpy.data.window_managers["WinMan"].ACON_prop.scene = scene.name

        # 렌더를 위한 씬 이름을 폴더명으로 설정하기 위한 queue에 추가
        self.render_queue.append((base_scene.name, scene, render_type))

        self.temp_scenes.append(scene)

        bpy.context.window_manager.progress_prop.total_render_num += 1

        scene.name = f"{base_scene.name}_{render_type}"
        if render_type != "full":
            scene.eevee.use_bloom = False
        scene.render.use_lock_interface = True

        # scene_info - UI 에 이름과 진행 상황을 보여주기 위한 데이터
        # FIXME scnee_info 에 scene 을 담고, temp_scenes 를 없애면 더 깔끔하지 않을까?
        scene_info = bpy.context.window_manager.progress_prop.render_scene_infos.add()
        scene_info.render_scene_name = scene.name
        scene_info.status = "waiting"

        prop = scene.ACON_prop
        if render_type == "line":
            prop.toggle_texture = False
            prop.toggle_shading = False
            prop.toggle_toon_edge = True
        elif render_type == "shadow":
            prop.toggle_texture = False
            prop.toggle_shading = True
            prop.toggle_toon_edge = False
        elif render_type == "texture":
            prop.toggle_texture = True
            prop.toggle_shading = False
            prop.toggle_toon_edge = False

    def prepare_queue(self, context):
        # 렌더 초기화
        progress_prop = context.window_manager.progress_prop
        progress_prop.total_render_num = 0
        progress_prop.complete_num = 0
        progress_prop.is_progress_shown = True
        progress_prop.start_date = time()
        progress_prop.end_date = 0
        progress_prop.render_scene_infos.clear()
        progress_prop.is_loaded = False

        render_prop = context.window_manager.ACON_prop
        for s_col in render_prop.scene_col:
            if s_col.is_render_selected and s_col.name in bpy.data.scenes:
                scene = bpy.data.scenes[s_col.name]

                if render_prop.hq_render_full:
                    self.prepare_temp_scene(scene, render_type="full")

                if render_prop.hq_render_line:
                    self.prepare_temp_scene(scene, render_type="line")

                if render_prop.hq_render_shadow:
                    self.prepare_temp_scene(scene, render_type="shadow")

                if render_prop.hq_render_texture:
                    self.prepare_temp_scene(scene, render_type="texture")

        progress_prop.is_loaded = True

        return {"RUNNING_MODAL"}

    def on_render_finish(self, context):
        context.window_manager.progress_prop.end_date = time()

        for mat in bpy.data.materials:
            materials_handler.set_material_parameters_by_type(mat)

        for scene in self.temp_scenes:
            bpy.data.scenes.remove(scene)

        self.temp_scenes.clear()

        return super().on_render_finish(context)

    @classmethod
    def poll(self, context):
        render_prop = context.window_manager.ACON_prop

        is_method_selected = (
            render_prop.hq_render_full
            or render_prop.hq_render_line
            or render_prop.hq_render_texture
            or render_prop.hq_render_shadow
        )

        is_scene_selected = any(s.is_render_selected for s in render_prop.scene_col)

        return is_method_selected and is_scene_selected


class Acon3dCloseProgressOperator(bpy.types.Operator):
    bl_idname = "acon3d.close_progress"
    bl_label = "OK"
    bl_description = "Finish render and close render progress module"
    bl_translation_context = "abler"

    @classmethod
    def poll(cls, context):
        prop = context.window_manager.progress_prop

        return prop.total_render_num == prop.complete_num

    def execute(self, context):
        progress_prop = context.window_manager.progress_prop
        progress_prop.total_render_num = 0
        progress_prop.complete_num = 0
        progress_prop.start_date = 0
        progress_prop.end_date = 0
        progress_prop.render_scene_infos.clear()
        progress_prop.is_progress_shown = False

        return {"FINISHED"}


def find_target_render_scene_info(render_scene_name, infos):
    for info in infos:
        if render_scene_name == info.render_scene_name:
            return info
    return None


class RenderSceneInfoProperty(bpy.types.PropertyGroup):
    # line, texture 등이 뒤에 붙은 render 할 때만 생성되는 scene 의 이름
    render_scene_name: bpy.props.StringProperty()
    # waiting, finished, in progress
    status: bpy.props.StringProperty(default="waiting")


class RenderProperty(bpy.types.PropertyGroup):
    start_date: bpy.props.IntProperty(default=0)
    end_date: bpy.props.IntProperty(default=0)
    complete_num: bpy.props.IntProperty(default=0)
    total_render_num: bpy.props.IntProperty(default=0)
    is_progress_shown: bpy.props.BoolProperty(default=False)
    render_scene_infos: bpy.props.CollectionProperty(type=RenderSceneInfoProperty)
    is_loaded: bpy.props.BoolProperty(default=False)


classes = (
    RenderSceneInfoProperty,
    RenderProperty,
    Acon3dRenderWarningOperator,
    Acon3dRenderSaveOpertor,
    Acon3dCameraViewOperator,
    Acon3dRenderHighQualityOperator,
    Acon3dRenderSnipOperator,
    Acon3dRenderQuickOperator,
    Acon3dCloseProgressOperator,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.WindowManager.progress_prop = bpy.props.PointerProperty(
        type=RenderProperty
    )


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.WindowManager.progress_prop
