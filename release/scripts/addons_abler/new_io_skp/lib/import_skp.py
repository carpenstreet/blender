import bpy
import sys
import os
import time
from dataclasses import asdict
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty
from .scene_importer import SceneImporter, ImportProgress
from .skp_log import progress_bar


if sys.platform == "win32":
    lib = bpy.app.binary_path.split("\\")[:-1]
    lib[0] += "\\"
    lib = os.path.join(*lib, "2.96", "scripts", "startup", "abler")
elif sys.platform == "darwin":
    lib = bpy.app.binary_path.split("/")[:-6]
    lib = "/" + os.path.join(*lib,"blender", "release", "scripts", "startup", "abler")
else:
    lib = None

sys.path.append(lib)
from lib.tracker import tracker
from lib.import_file import AconImportHelper, AconExportHelper
from lib.file_view import file_view_title



# 변환 진행도 및 단위 개수별 변환 시간 출력 옵션 확인
print_progress = False
print_time = False

regions = None
keywords = None
iter_time = None
skp_tracking_props = None

def generator_runner(target_func):
    gen = None

    def runner():
        global regions, keywords, iter_time
        nonlocal gen
        try:
            if not gen:
                gen = target_func()

            next(gen)
            for region in regions:
                region.tag_redraw()
        except StopIteration:
            regions = []
            keywords = None
            iter_time = None
            return None
        except:
            prop = bpy.context.window_manager.SKP_prop
            prop.is_crashed = True
            prop.end_date = time.time()

            regions = []
            keywords = None
            iter_time = None
            return None
        return 0

    return runner


def iter_func():
    global keywords, iter_time

    # Generator를 통해서 SceneImporter > load() 내부의 SketchUp 변환 진행 과정 확인하기
    load_iter = (
        SceneImporter().set_filename(keywords["filepath"]).load(bpy.context, **keywords)
    )

    prop = bpy.context.window_manager.SKP_prop

    # Cython 실행하기  (ImportProgress.IMPORT_START)
    progress_type, _ = next(load_iter)
    yield
    # Model Info 가져오기 (ImportProgress.READ_FILE)
    progress_type, statistics, import_lookatme = next(load_iter)

    global skp_tracking_props
    skp_tracking_props = asdict(statistics)
    skp_tracking_props["import_lookatme"] = import_lookatme

    yield
    statistics.objects = statistics.instances + statistics.groups

    scene_count = len(bpy.data.scenes)
    # 각 단계별 가중치 계산
    # 처리 순서 대로
    # (Import Start, Material, Object, Update Skip Layer, Update View Layer,
    # Always Face Camera, Apply Toon Style, Select ALl Objects)
    # TODO dataclass / dictionary 등 가독성 좋은 구조 사용
    weights = (1, 0.001, 0.001, 0.2 / scene_count, 0.1, 0.001, 5)

    weight_sum = (
        weights[0]
        + weights[1] * statistics.materials
        + weights[2] * statistics.objects
        + weights[3] * statistics.hidden_layer_count
        + weights[4]
        + weights[5] * statistics.afc_instances
        + weights[6]
    )
    normalize_factor = 1 / weight_sum
    weights = tuple(elem * normalize_factor for elem in weights)

    prop.total_progress += weights[0]

    # write_materials, write_entities의 진행도 파악
    materials = 0
    objects = 0
    instances = 0
    groups = 0
    time_instances = 0
    time_groups = 0
    always_face_camera_instances = 0
    skip_layer_and_scene = 0

    for progress_type, data in load_iter:
        if progress_type == ImportProgress.MATERIAL:
            materials += 1
            prop.total_progress += weights[1]
            if print_progress:
                progress_bar("Materials", materials, statistics.materials)

        # Materials가 없으면 ImportProgress.MATERIAL이 발생하지 않아서 materials progress를 넘어감
        elif progress_type == ImportProgress.MATERIALS_DONE:
            prop.total_progress += weights[1] * (statistics.materials - materials)
            if print_progress:
                progress_bar("Materials", materials, statistics.materials)

        elif progress_type == ImportProgress.OBJECT:
            objects += 1
            prop.total_progress += weights[2]
            if print_progress and (objects != statistics.objects):
                progress_bar("Entities ", objects, statistics.objects)

        elif progress_type == ImportProgress.OBJECTS_DONE:
            prop.total_progress += weights[2] * (statistics.objects - objects)
            if print_progress:
                progress_bar("Entities ", objects, statistics.objects)

        elif progress_type == ImportProgress.TIME_INSTANCE:
            instances += 1
            time_instances += data
            if print_time and (instances >= 1000) and (instances % 1000 == 0):
                print(
                    f"\nInstances: {instances}/{statistics.instances} | {time_instances:.4f} s"
                )
                time_instances = 0

        elif progress_type == ImportProgress.TIME_GROUP:
            groups += 1
            time_groups += data
            if print_time and (groups >= 1000) and (groups % 1000 == 0):
                print(
                    f"\nGroups   : {groups}/{statistics.groups} | {time_groups:.4f} s"
                )
                time_groups = 0

        elif progress_type == ImportProgress.UPDATE_SKIP_LAYER:
            skip_layer_and_scene += 1
            total_num = scene_count * statistics.hidden_layer_count
            prop.total_progress += weights[3]
            if print_progress and (skip_layer_and_scene != total_num):
                progress_bar(
                    "Skip Layers ",
                    skip_layer_and_scene,
                    total_num,
                )

        elif progress_type == ImportProgress.UPDATE_SKIP_LAYER_DONE:
            total_num = scene_count * statistics.hidden_layer_count
            prop.total_progress += weights[3] * (total_num - skip_layer_and_scene)

        elif progress_type == ImportProgress.UPDATE_VIEW_LAYER:
            prop.total_progress += weights[4]

        elif progress_type == ImportProgress.ALWAYS_FACE_CAMERA:
            prop.total_progress += weights[5]
            if print_progress and (
                always_face_camera_instances != statistics.afc_instances
            ):
                progress_bar(
                    "Always Face Cameras ",
                    always_face_camera_instances,
                    statistics.afc_instances,
                )

        elif progress_type == ImportProgress.ALWAYS_FACE_CAMERA_DONE:
            prop.total_progress += weights[5] * (
                statistics.afc_instances - always_face_camera_instances
            )

        elif progress_type == ImportProgress.APPLY_TOON_STYLE:
            prop.total_progress += weights[6]


        cur_time = time.time()
        if cur_time - iter_time > 1:
            iter_time = cur_time
            yield

    if print_time:
        print("=" * 40)
        print(
            f"Instances (< 1000): %3i | time: {time_instances:.4f} s"
            % (instances % 1000)
        )
        print(f"Groups    (< 1000): %3i | time: {time_groups:.4f} s" % (groups % 1000))
        print("=" * 40)

    prop.end_date = time.time()
    prop.total_progress = 1
    bpy.context.window.cursor_set("DEFAULT")

    return


class ImportSKPPro(Operator):
    """Load a Trimble Sketchup SKP file"""

    bl_idname = "acon3d.import_skp_pro"
    bl_label = "Import SKP"
    bl_options = {"PRESET", "UNDO"}

    filepath: StringProperty(default="")

    import_camera: BoolProperty(
        name="Last View In SketchUp As Camera View",
        description="Import last saved view in SketchUp as a Blender Camera.",
        default=False,
    )

    reuse_material: BoolProperty(
        name="Use Existing Materials",
        description="Doesn't copy material IDs already in the Blender Scene.",
        default=True,
    )

    max_instance: IntProperty(name="Threshold :", default=50)

    dedub_type: EnumProperty(
        name="Instancing Type :",
        items=(
            ("FACE", "Faces", ""),
            ("VERTEX", "Verts", ""),
        ),
        default="VERTEX",
    )

    dedub_only: BoolProperty(
        name="Groups Only",
        description="Import instanciated groups only.",
        default=False,
    )

    scenes_as_camera: BoolProperty(
        name="Scene(s) As Camera(s)",
        description="Import SketchUp Scenes As Blender Camera.",
        default=True,
    )

    import_scene: StringProperty(
        name="Import A Scene :",
        description="Import a specific Sketchup Scene",
        default="",
    )

    reuse_existing_groups: BoolProperty(
        name="Reuse Groups",
        description="Use existing Blender groups to instance componenets with.",
        default=True,
    )

    remove_existing_objects: BoolProperty(
        name="Remove Existing Objects When Importing", default=True
    )

    import_lookatme: BoolProperty(default=False)

    def execute(self, context):
        global regions, keywords, iter_time

        keywords = self.as_keywords(
            ignore=("axis_forward", "axis_up", "filter_glob", "split_mode")
        )
        if "--background" in sys.argv or "-b" in sys.argv:
            load_iter = (
                SceneImporter()
                .set_filename(keywords["filepath"])
                .load(bpy.context, **keywords)
            )
            for progress_type, *_ in load_iter:
                if not progress_type:
                    pass
        else:
            regions = []
            for region in context.area.regions:
                if region.type == "UI":
                    regions.append(region)

            iter_time = time.time()

            bpy.ops.acon3d.get_skp_progress_new("INVOKE_DEFAULT")
        return {"FINISHED"}


class ImportSKPProPanel(bpy.types.Panel):
    bl_parent_id = "ACON3D_PT_general"
    bl_idname = "ACON3D_PT_import_skp_pro"
    bl_label = "General"
    bl_category = "General"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.scale_y = 1.0
        row.operator("acon3d.import_pro", text="Import SKP pro")


class ImportProOperator(bpy.types.Operator, AconImportHelper):
    """Import file according to the current settings (.skp, .fbx, .blend)"""

    bl_idname = "acon3d.import_pro"
    bl_label = "Import"
    bl_options = {"UNDO"}
    bl_translation_context = "*"

    filter_glob: bpy.props.StringProperty(
        default="*.skp", options={"HIDDEN"}
    )
    import_lookatme: bpy.props.BoolProperty(
        default=False,
    )
    filepath: bpy.props.StringProperty(default="")
    use_filter = True

    def draw(self, context):
        super().draw(context)

        layout = self.layout
        row = layout.row()
        row.label(text="Import files onto the viewport.")
        row = layout.row()
        row.label(text="Sketchup File (.skp)", icon="DOT")
        self.path_ext = self.filepath.rsplit(".")[-1]
        if self.path_ext == "skp":
            row = layout.row()
            row.prop(self, "import_lookatme", text="Import Look at me")

    def invoke(self, context, event):
        with file_view_title("IMPORT"):
            return super().invoke(context, event)

    def execute(self, context):
        if not self.check_path(accepted=["skp"]):
            return {"FINISHED"}

        if self.path_ext == "skp":
            # skp importer 관련하여 감싸는 skp operator를 만들어서 트래킹과 exception 핸들링을 더 잘 할 수 있도록 함.
            # TODO: 다른 유관 프로젝트들과의 dependency와 legacy가 청산되면 위와 같은 네이밍 컨벤션으로 갈 수 있도록 리팩토링 할 것.
            # 관련 논의 : https://github.com/ACON3D/blender/pull/204#discussion_r101510407

            bpy.ops.acon3d.import_skp_pro_op(
                filepath=self.filepath, import_lookatme=self.import_lookatme
            )

        return {"FINISHED"}


class ImportSKPProOperator(bpy.types.Operator, AconImportHelper):
    """Import SKP file according to the current settings"""

    bl_idname = "acon3d.import_skp_pro_op"
    bl_label = "Import SKP"
    bl_options = {"UNDO"}
    bl_translation_context = "abler"

    filter_glob: bpy.props.StringProperty(default="*.skp", options={"HIDDEN"})
    import_lookatme: bpy.props.BoolProperty(default=False)
    use_filter = True

    def invoke(self, context, event):
        with file_view_title("IMPORT"):
            return super().invoke(context, event)

    def execute(self, context):
        if not self.check_path(accepted=["skp"]):
            return {"FINISHED"}
        bpy.ops.acon3d.close_skp_progress_new()
        bpy.ops.acon3d.import_skp_pro(
            "INVOKE_DEFAULT",
            filepath=self.filepath,
            import_lookatme=self.import_lookatme,
        )

        return {"FINISHED"}

class NewGetSKPProgress(Operator):
    bl_label = "Get Progress"
    bl_idname = "acon3d.get_skp_progress_new"

    def invoke(self, context, event):
        context.window_manager.SKP_prop.start_date = time.time()
        context.window.cursor_set("WAIT")
        bpy.app.timers.register(generator_runner(iter_func), first_interval=0)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        prop = context.window_manager.SKP_prop
        global skp_tracking_props

        if prop.end_date:
            spent_time = time.strftime("%H:%M:%S", time.gmtime(prop.end_date - prop.start_date))
            if not skp_tracking_props:
                skp_tracking_props = {}
            skp_tracking_props["Spent Time"] = spent_time
            if prop.is_crashed:
                # tracker.import_skp_fail(skp_tracking_props)
                bpy.ops.acon3d.alert(
                    "INVOKE_DEFAULT",
                    title="Import Failure",
                    message_1="Cannot import selected file.",
                )
            else:
                # tracker.import_skp_success(skp_tracking_props)
                pass
            skp_tracking_props = None
            return {"FINISHED"}

        return {"RUNNING_MODAL"}


class NewCloseSKPProgress(Operator):
    """Finish importing file"""

    bl_label = "Close Progress"
    bl_idname = "acon3d.close_skp_progress_new"

    def execute(self, context):
        prop = context.window_manager.SKP_prop
        # SKP_prop 초기화
        prop.total_progress = 0
        prop.start_date = 0
        prop.end_date = 0
        prop.is_crashed = False

        return {"FINISHED"}



