from bpy.types import PropertyGroup, WindowManager
from bpy.props import IntProperty, FloatProperty, PointerProperty, BoolProperty


class ProgressProperty(PropertyGroup):
    @classmethod
    def register(cls):
        WindowManager.SKP_prop = PointerProperty(type=ProgressProperty)

    @classmethod
    def unregister(cls):
        del WindowManager.SKP_prop

    total_progress: FloatProperty(default=0)

    start_date: IntProperty(default=0)

    end_date: IntProperty(default=0)

    is_crashed: BoolProperty(default=False)
