import os
import bpy
from bpy_extras.io_utils import ImportHelper


class AconImportHelper(ImportHelper):
    def execute(self, context):
        path = self.filepath
        if path.endswith('/') or path.endswith('\\') or path.endswith('//'):
            return {"FINISHED"}
        elif not os.path.isfile(path):
            bpy.ops.acon3d.alert(
                "INVOKE_DEFAULT",
                title="File not found",
                message_1="Selected file does not exist",
            )
            return {"FINISHED"}
        else:
            return None
