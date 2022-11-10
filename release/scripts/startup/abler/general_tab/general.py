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
import os

from datetime import datetime, timedelta
import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper
from ..lib import scenes
from ..lib.file_view import file_view_title
from ..lib.materials import materials_setup
from ..lib.tracker import tracker
from ..lib.read_cookies import read_remembered_show_guide
from ..lib.import_file import AconImportHelper


def split_filepath(filepath):
    # Get basename without file extension
    dirname, basename = os.path.split(os.path.normpath(filepath))

    if "." in basename:
        basename = ".".join(basename.split(".")[:-1])

    return dirname, basename


def numbering_filepath(filepath, ext):
    dirname, basename = split_filepath(filepath)
    basepath = os.path.join(dirname, basename)

    num_path = basepath
    num_name = basename
    number = 2

    while os.path.isfile(f"{num_path}{ext}"):
        num_path = f"{basepath} ({number})"
        num_name = f"{basename} ({number})"
        number += 1

    return num_path, num_name


class AconTutorialGuidePopUpOperator(bpy.types.Operator):
    """Show tutorial guide"""

    bl_idname = "acon3d.tutorial_guide_popup"
    bl_label = "Quick Start Guide"
    bl_translation_context = "abler"

    def execute(self, context):
        tracker.tutorial_guide_on()

        userInfo = bpy.data.meshes.get("ACON_userInfo")
        prop = userInfo.ACON_prop
        prop.show_guide = read_remembered_show_guide()

        bpy.ops.wm.splash_tutorial_1("INVOKE_DEFAULT")
        return {"FINISHED"}


class AconTutorialGuideCloseOperator(bpy.types.Operator):
    """Close Tutorial Guide"""

    bl_idname = "acon3d.tutorial_guide_close"
    bl_label = "OK"

    def execute(self, context):
        bpy.ops.wm.splash_tutorial_close("INVOKE_DEFAULT")
        return {"CANCELLED"}


class AconTutorialGuide1Operator(bpy.types.Operator):
    """Mouse Mode"""

    bl_idname = "acon3d.tutorial_guide_1"
    bl_label = "Mouse Mode"
    bl_translation_context = "abler"

    def execute(self, context):
        bpy.ops.acon3d.tutorial_guide_close()
        bpy.ops.wm.splash_tutorial_1("INVOKE_DEFAULT")
        return {"FINISHED"}


class AconTutorialGuide2Operator(bpy.types.Operator):
    """Fly Mode"""

    bl_idname = "acon3d.tutorial_guide_2"
    bl_label = "Fly Mode"
    bl_translation_context = "abler"

    def execute(self, context):
        bpy.ops.acon3d.tutorial_guide_close()
        bpy.ops.wm.splash_tutorial_2("INVOKE_DEFAULT")
        return {"FINISHED"}


class AconTutorialGuide3Operator(bpy.types.Operator):
    """Scene Control"""

    bl_idname = "acon3d.tutorial_guide_3"
    bl_label = "Scene Control"
    bl_translation_context = "abler"

    def execute(self, context):
        bpy.ops.acon3d.tutorial_guide_close()
        bpy.ops.wm.splash_tutorial_3("INVOKE_DEFAULT")
        return {"FINISHED"}


class ToggleToolbarOperator(bpy.types.Operator):
    """
    Toggle toolbar visibility

    Toogle Toolbar를 General 패널에서 삭제하기로 기획됨.
    그러나, 관련 내용을 다른 위치 혹은 다른 기능으로 재사용 할 수 있어 코드를 삭제하지 않음.
    관련 Notion 문서:
    https://www.notion.so/acon3d/DEFAULT-Show-78cd7fd6d13742ed9f36d9ae423e15cf
    """

    bl_idname = "acon3d.context_toggle"
    bl_label = "Toggle Toolbar"
    bl_translation_context = "abler"

    def execute(self, context):
        tracker.toggle_toolbar()

        context.scene.render.engine = "BLENDER_EEVEE"
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        value = space.show_region_toolbar
                        space.show_region_toolbar = not value

        return {"FINISHED"}


def update_recent_files(target_path, is_add=False):
    """
    Update Recent Files in User Resources

    target_path: path to update
    is_add: if True, add target_path to first of the recent files list
    """

    history_path = bpy.utils.user_resource("CONFIG") + "/recent-files.txt"

    try:
        # create history_path if not exists
        open(history_path, "a").close()

        with open(history_path) as fin:
            recent_filepaths_except_target = [
                path for path in fin.read().splitlines() if path != target_path
            ]

        if is_add:
            recent_filepaths_except_target.insert(0, target_path)
            recent_filepaths_except_target = recent_filepaths_except_target[:10]

        with open(history_path, "wt") as fout:
            fout.write("\n".join(recent_filepaths_except_target))

    except Exception as e:
        print(e)
        return


class BaseFileOpenOperator:
    filepath: bpy.props.StringProperty(name="text", default="")

    def open_file(self):
        try:
            path = self.filepath

            bpy.ops.wm.open_mainfile(
                "INVOKE_DEFAULT", filepath=path, display_file_selector=False
            )
            update_recent_files(path, is_add=True)

        except Exception as e:
            update_recent_files(path)
            tracker.file_open_fail()

            self.report({"ERROR"}, message=str(e))
        else:
            tracker.file_open()


class FileOpenOperator(bpy.types.Operator, AconImportHelper, BaseFileOpenOperator):
    """Open new file"""

    bl_idname = "acon3d.file_open"
    bl_label = "Open"
    bl_translation_context = "abler"

    filter_glob: bpy.props.StringProperty(default="*.blend", options={"HIDDEN"})

    def invoke(self, context, event):
        with file_view_title("OPEN"):
            return super().invoke(context, event)

    def execute(self, context):
        if not self.check_path(accepted=["blend"]):
            return {"FINISHED"}
        self.open_file()
        return {"FINISHED"}


class FileRecentOpenOperator(bpy.types.Operator, BaseFileOpenOperator):
    bl_idname = "acon3d.recent_file_open"
    bl_label = ""
    bl_translation_context = "abler"

    @classmethod
    def description(cls, context, properties):
        filepath = properties.filepath

        if not os.path.isfile(filepath):
            return f"{filepath}\n\nFile Not Found"

        modified_datetime = datetime.fromtimestamp(os.path.getmtime(filepath))
        time_distance = datetime.today().date() - modified_datetime.date()

        if time_distance == timedelta():
            modified_time = modified_datetime.strftime("Today %H:%M")
        elif time_distance == timedelta(days=1):
            modified_time = modified_datetime.strftime("Yesterday %H:%M")
        else:
            modified_time = modified_datetime.strftime("%d %b %Y %H:%M")

        modified_time = f"Modified: {modified_time}"

        size = round(os.path.getsize(filepath) / 1000000.0, 1)
        size = f"Size: {size} MB"

        return f"{filepath}\n\n{modified_time}\n{size}"

    def execute(self, context):
        self.open_file()
        return {"FINISHED"}


class FlyOperator(bpy.types.Operator):
    """Move around the scene using WASD, QE, and mouse like FPS games"""

    bl_idname = "acon3d.fly_mode"
    bl_label = "Fly with WASD (shift + `)"
    bl_translation_context = "abler"

    def execute(self, context):
        tracker.fly_mode()

        if context.space_data.type == "VIEW_3D":
            bpy.ops.view3d.walk("INVOKE_DEFAULT")

        return {"FINISHED"}


class SaveOperator(bpy.types.Operator, ExportHelper):
    """Save the current Blender file"""

    bl_idname = "acon3d.save"
    bl_label = "Save"
    bl_translation_context = "abler"

    filename_ext = ".blend"

    # invoke() 사용을 하지 않고 execute() 분리 시도 방법은 현재 어렵습니다.
    # Helper 함수에서는 invoke()가 호출되어서 파일 브라우저 관리를 하는데,
    # 파일이 최초 저장될 때는 invoke()를 활용해서 파일 브라우저에서 파일명을 관리를 해야하지만,
    # 파일이 이미 저장된 상태일 때는 invoke()를 넘어가고 바로 execute()를 실행해야 합니다.
    def invoke(self, context, event):
        with file_view_title("SAVE"):
            if bpy.data.is_saved:
                return self.execute(context)

            else:
                return ExportHelper.invoke(self, context, event)

    def execute(self, context):
        try:
            if bpy.data.is_saved:
                self.filepath = context.blend_data.filepath
                dirname, basename = split_filepath(self.filepath)

                bpy.ops.wm.save_mainfile({"dict": "override"}, filepath=self.filepath)
                update_recent_files(self.filepath, is_add=True)
                self.report({"INFO"}, f'Saved "{basename}{self.filename_ext}"')

            else:
                numbered_filepath, numbered_filename = numbering_filepath(
                    self.filepath, self.filename_ext
                )

                self.filepath = f"{numbered_filepath}{self.filename_ext}"

                bpy.ops.wm.save_mainfile({"dict": "override"}, filepath=self.filepath)
                update_recent_files(self.filepath, is_add=True)
                self.report({"INFO"}, f'Saved "{numbered_filename}{self.filename_ext}"')

        except Exception as e:
            tracker.save_fail()
            raise e
        else:
            tracker.save()

        return {"FINISHED"}


class SaveAsOperator(bpy.types.Operator, ExportHelper):
    """Save the current file in the desired location"""

    bl_idname = "acon3d.save_as"
    bl_label = "Save As..."
    bl_translation_context = "abler"

    filename_ext = ".blend"

    def invoke(self, context, event):
        with file_view_title("SAVE_AS"):
            return super().invoke(context, event)

    def execute(self, context):
        try:
            numbered_filepath, numbered_filename = numbering_filepath(
                self.filepath, self.filename_ext
            )

            self.filepath = f"{numbered_filepath}{self.filename_ext}"

            bpy.ops.wm.save_as_mainfile({"dict": "override"}, filepath=self.filepath)
            update_recent_files(self.filepath, is_add=True)
            self.report({"INFO"}, f'Saved "{numbered_filename}{self.filename_ext}"')

        except Exception as e:
            tracker.save_as_fail()
            raise e
        else:
            tracker.save_as()

        return {"FINISHED"}


class ImportOperator(bpy.types.Operator, AconImportHelper):
    """Import file according to the current settings (.skp, .fbx, .blend)"""

    bl_idname = "acon3d.import"
    bl_label = "Import"
    bl_translation_context = "*"

    filter_glob: bpy.props.StringProperty(
        default="*.blend;*.fbx;*.skp", options={"HIDDEN"}
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Import files onto the viewport.")
        row = layout.row()
        row.label(text="ㅁ Sketchup File (.skp)")
        row = layout.row()
        row.label(text="ㅁ FBX File (.fbx)")
        row = layout.row()
        row.label(text="ㅁ Blender File (.blend)")

    def invoke(self, context, event):
        with file_view_title("IMPORT"):
            return super().invoke(context, event)

    def execute(self, context):
        if not self.check_path(accepted=["blend", "fbx", "skp"]):
            return {"FINISHED"}

        path = self.filepath
        path_ext = path.rsplit(".")[-1]

        if path_ext == "blend":
            bpy.ops.acon3d.import_blend(filepath=path)
        elif path_ext == "fbx":
            bpy.ops.acon3d.import_fbx(filepath=path)
        elif path_ext == "skp":
            # skp importer 관련하여 감싸는 skp operator를 만들어서 트래킹과 exception 핸들링을 더 잘 할 수 있도록 함.
            # TODO: 다른 유관 프로젝트들과의 dependency와 legacy가 청산되면 위와 같은 네이밍 컨벤션으로 갈 수 있도록 리팩토링 할 것.
            # 관련 논의 : https://github.com/ACON3D/blender/pull/204#discussion_r1015104073
            bpy.ops.acon3d.import_skp_op(filepath=path)

        return {"FINISHED"}


class ImportBlenderOperator(bpy.types.Operator, AconImportHelper):
    """Import Blender file according to the current settings"""

    bl_idname = "acon3d.import_blend"
    bl_label = "Import Blender"
    bl_translation_context = "*"

    filter_glob: bpy.props.StringProperty(default="*.blend", options={"HIDDEN"})

    class SameFileImportError(Exception):
        def __init__(self):
            super().__init__()

    def invoke(self, context, event):
        with file_view_title("IMPORT"):
            return super().invoke(context, event)

    def execute(self, context):
        try:
            if not self.check_path(accepted=["blend"]):
                return {"FINISHED"}

            # Blender에서 File Open과 같은 파일을 import하면 Collection과 Mesh Object 이름에 ".001"이 넘버링 하지 않음
            # 그래서 중복 처리를 하지 않고 있어, 예외 경우로 구분하고 메세지 알림 띄워주기
            filepath_curr = bpy.data.filepath
            FILEPATH = self.filepath

            if filepath_curr == FILEPATH:
                raise self.SameFileImportError

            for obj in bpy.data.objects:
                obj.select_set(False)

            col_layers = bpy.data.collections.get("Layers")
            if not col_layers:
                col_layers = bpy.data.collections.new("Layers")
                context.scene.collection.children.link(col_layers)

            with bpy.data.libraries.load(FILEPATH) as (data_from, data_to):
                data_to.collections = data_from.collections
                data_to.objects = list(data_from.objects)

            for coll in data_to.collections:

                if "ACON_col" in coll.name:
                    data_to.collections.remove(coll)
                    break

                if coll.name == "Layers" or (
                    "Layers." in coll.name and len(coll.name) == 10
                ):
                    for coll_2 in coll.children:
                        # File Open과 다른 파일을 import 할 때, Collection과 Mesh Object 이름이 중복되면 ".001"부터 넘버링됨
                        # Layer0.001의 오브젝트를 Layer0으로 이동하고 Layer0.001을 Outliner에서 제거
                        if "Layer0." in coll_2.name:
                            for coll_obj in bpy.data.collections[coll_2.name].objects:
                                bpy.data.collections[coll_2.name].objects.unlink(
                                    coll_obj
                                )
                                bpy.data.collections["Layer0"].objects.link(coll_obj)

                        else:
                            # 모든 씬의 l_exclude에 col_imported를 추가
                            for scene in bpy.data.scenes:
                                added_l_exclude = scene.l_exclude.add()
                                added_l_exclude.name = coll_2.name
                                added_l_exclude.value = True
                            col_layers.children.link(coll_2)

            # 레이어 이름에 Layer0.이 포함된 중복 레이어 제거
            for coll in data_to.collections:
                if "Layer0." in coll.name:
                    bpy.data.collections.remove(coll)

            # View Layer에 없는 Mesh Object들의 select_set(True) 에러가 나고 있었음
            # 이런 오브젝트들은 선택되지 않아도 무방하여 해당 작업을 제거함
            for obj in data_to.objects:
                if obj.type != "MESH":
                    data_to.objects.remove(obj)

            materials_setup.apply_ACON_toon_style()

            for area in context.screen.areas:
                if area.type == "VIEW_3D":
                    ctx = bpy.context.copy()
                    ctx["area"] = area
                    ctx["region"] = area.regions[-1]
                    bpy.ops.view3d.view_selected(ctx)

        # TODO: 에러 세분화 필요
        except self.SameFileImportError:
            tracker.import_same_blend_fail()
            bpy.ops.acon3d.alert(
                "INVOKE_DEFAULT",
                title="Import Failure",
                message_1="Cannot import exact same file from same directory.",
            )
        except Exception as e:
            tracker.import_blend_fail()
            self.report({"ERROR"}, f"Fail to import blend file. Check filepath.")
        else:
            tracker.import_blend()

        return {"FINISHED"}


class ImportFBXOperator(bpy.types.Operator, AconImportHelper):
    """Import FBX file according to the current settings"""

    bl_idname = "acon3d.import_fbx"
    bl_label = "Import FBX"
    bl_translation_context = "abler"

    filter_glob: bpy.props.StringProperty(default="*.fbx", options={"HIDDEN"})

    def invoke(self, context, event):
        with file_view_title("IMPORT"):
            return super().invoke(context, event)

    def execute(self, context):
        if not self.check_path(accepted=["fbx"]):
            return {"FINISHED"}
        try:
            for obj in bpy.data.objects:
                obj.select_set(False)

            FILEPATH = self.filepath

            filename = os.path.basename(FILEPATH)
            col_imported = bpy.data.collections.new(
                "[FBX] " + filename.replace(".fbx", "")
            )

            col_layers = bpy.data.collections.get("Layers")
            if not col_layers:
                col_layers = bpy.data.collections.new("Layers")
                context.scene.collection.children.link(col_layers)

            bpy.ops.import_scene.fbx(filepath=FILEPATH)
            for obj in bpy.context.selected_objects:
                if obj.name in bpy.context.scene.collection.objects:
                    bpy.context.scene.collection.objects.unlink(obj)
                for c in bpy.data.collections:
                    if obj.name in c.objects:
                        c.objects.unlink(obj)
                col_imported.objects.link(obj)

            # 모든 씬의 l_exclude에 col_imported를 추가
            col_layers.children.link(col_imported)
            for scene in bpy.data.scenes:
                added_l_exclude = scene.l_exclude.add()
                added_l_exclude.name = col_imported.name
                added_l_exclude.value = True

            # create group
            bpy.ops.acon3d.create_group()
            # apply AconToonStyle
            materials_setup.apply_ACON_toon_style()

        except Exception as e:
            tracker.import_fbx_fail()
            raise e
        else:
            tracker.import_fbx()

        return {"FINISHED"}


class ImportSKPOperator(bpy.types.Operator, AconImportHelper):
    """Import SKP file according to the current settings"""

    bl_idname = "acon3d.import_skp_op"
    bl_label = "Import SKP"
    bl_translation_context = "abler"

    filter_glob: bpy.props.StringProperty(default="*.skp", options={"HIDDEN"})

    def invoke(self, context, event):
        with file_view_title("IMPORT"):
            return super().invoke(context, event)

    def execute(self, context):
        if not self.check_path(accepted=["skp"]):
            return {"FINISHED"}
        try:
            # TODO: 이곳에 완성된 skp importer 관련 함수가 들어갈 예정
            pass
        except Exception as e:
            tracker.import_skp_fail()
            raise e
        else:
            tracker.import_skp()

        return {"FINISHED"}


class Acon3dGeneralPanel(bpy.types.Panel):
    bl_idname = "ACON3D_PT_general"
    bl_label = "General"
    bl_category = "General"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_translation_context = "abler"
    bl_options = {"HIDE_HEADER"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="EVENT_A")

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.scale_y = 1.0
        row.operator("acon3d.tutorial_guide_popup")

        row = layout.row()
        row.scale_y = 1.0
        row.operator("acon3d.file_open")
        row.operator("acon3d.import", text="Import")

        row = layout.row()
        row.scale_y = 1.0
        row.operator("acon3d.save", text="Save")
        row.operator("acon3d.save_as", text="Save As...")

        row = layout.row()
        prefs = context.preferences
        view = prefs.view

        row.prop(view, "language")
        row = layout.row()
        row.operator("acon3d.fly_mode")


class ApplyToonStyleOperator(bpy.types.Operator):
    """Apply Toon Style"""

    bl_idname = "acon3d.apply_toon_style"
    bl_label = "Apply Toon Style"
    bl_translation_context = "abler"

    def execute(self, context):
        materials_setup.apply_ACON_toon_style()
        scenes.load_scene(None, None)

        return {"FINISHED"}


classes = (
    AconTutorialGuidePopUpOperator,
    AconTutorialGuideCloseOperator,
    AconTutorialGuide1Operator,
    AconTutorialGuide2Operator,
    AconTutorialGuide3Operator,
    Acon3dGeneralPanel,
    ToggleToolbarOperator,
    ApplyToonStyleOperator,
    FileOpenOperator,
    FileRecentOpenOperator,
    FlyOperator,
    SaveOperator,
    SaveAsOperator,
    ImportOperator,
    ImportBlenderOperator,
    ImportFBXOperator,
    ImportSKPOperator,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
