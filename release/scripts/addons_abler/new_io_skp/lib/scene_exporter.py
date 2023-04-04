import os
from .skp_log import *


class SceneExporter:
    def __init__(self):
        self.filepath = "/tmp/untitled.skp"

    def set_filename(self, filename):
        self.filepath = filename
        self.basepath, self.skp_filename = os.path.split(self.filepath)

        return self

    def save(self, context, **options):
        skp_log(f"Finished exporting: {self.filepath}")

        return {"FINISHED"}
