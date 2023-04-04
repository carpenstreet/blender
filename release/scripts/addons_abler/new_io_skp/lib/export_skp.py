from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from .scene_exporter import SceneExporter


class ExportSKP(Operator, ExportHelper):
    """Load a Trimble Sketchup SKP file"""

    bl_idname = "acon3d.export_skp"
    bl_label = "Export SKP"
    bl_options = {"PRESET", "UNDO"}

    filename_ext = ".skp"

    def execute(self, context):
        keywords = self.as_keywords()
        return (
            SceneExporter().set_filename(keywords["filepath"]).save(context, **keywords)
        )
