import os
import bpy
from bpy_extras.io_utils import ImportHelper


class AconImportHelper(ImportHelper):
    def check_path(self, extension: str) -> bool:
        """
        :return: 파일이 아니거나 파일이 없을 경우 False를 반환, 존재하고 파일일 경우 True를 반환
        """
        basename = self.filepath.rsplit(".")[0]
        path = basename + "." + extension
        if not os.path.isfile(path):
            bpy.ops.acon3d.alert(
                "INVOKE_DEFAULT",
                title="File Select Error",
                message_1="No selected file.",
            )
            return False
        else:
            return True
