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

        if path_ext not in accepted or not os.path.isfile(path):
            bpy.ops.acon3d.alert(
                "INVOKE_DEFAULT",
                title="File Select Error",
                message_1="No selected file.",
            )
            return False
        else:
            return True
