from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty


class CollectionLayerExcludeProperties(PropertyGroup):
    name: StringProperty(name="Layer Name", default="")
    init: BoolProperty(name="Layer Initialized", default=False)
    value: BoolProperty(name="Layer Exclude", default=True)
    lock: BoolProperty(name="Layer Lock", default=False)
