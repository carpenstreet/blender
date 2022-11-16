import os
import bpy
from bpy_extras.io_utils import ImportHelper


class AconImportHelper(ImportHelper):
    def check_path(self, accepted: list[str]) -> bool:
        """
        :param accepted: 허용할 extension 리스트

        :return: accepted 에 파일의 확장자가 없는 경우,
            파일 형식이 아닌 경우, 파일이 없는 경우 False 반환,
            그 외의 경우 True 반환
        """
        path = self.filepath
        path_ext = path.rsplit(".")[-1]
        if path_ext in accepted and os.path.isfile(path):
            return self._turn_on_addon(ext=path_ext, accepted=accepted)
        bpy.ops.acon3d.alert(
            "INVOKE_DEFAULT",
            title="File Select Error",
            message_1="No selected file.",
        )
        return False

    @staticmethod
    def _turn_on_addon(ext: str, accepted: list[str]) -> bool:
        """
        :param ext: 켜줄 extension
        :param accepted: 허용할 extension 리스트
        """
        # 지원하지 않는 확장자이면 False 를 리턴
        if ext not in accepted:
            return False
        try:
            if ext == "fbx":
                bpy.ops.preferences.addon_enable(module="io_scene_fbx")
            elif ext == "skp":
                bpy.ops.preferences.addon_enable(module="io_skp")
        except Exception as e:
            print(e)
            # 뭔가 오류가 있어서 켜지지 않으면 False 리턴
            return False
        else:
            # 잘 되는 경우는 True 리턴
            return True

    def draw(self, context):
        # FileBrowser UI 변경
        space = context.space_data
        params = space.params

        params.display_type = "THUMBNAIL"
        params.display_size = "LARGE"
        params.recursion_level = "NONE"
        params.sort_method = "FILE_SORT_TIME"
        params.use_sort_invert = True
        params.use_filter = False
