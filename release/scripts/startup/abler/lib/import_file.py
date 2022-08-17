import os
import bpy
from bpy_extras.io_utils import ImportHelper


class AconImportHelper(ImportHelper):
    def check_path(self) -> bool:
        """
        :return: 파일이 아니거나 파일이 없을 경우 False를 반환, 존재하고 파일일 경우 True를 반환
        """
        path = self.filepath
        if path.endswith('/') or path.endswith('\\') or path.endswith('//'):
            return False
        elif not os.path.isfile(path):
            bpy.ops.acon3d.alert(
                "INVOKE_DEFAULT",
                title="File not found",
                message_1="Selected file does not exist",
            )
            return False
        else:
            return True
