import bpy
from bpy.types import FloatProperty, PropertyGroup


def change_bloom_threshold(self, context):
    props = context.scene.eevee

    prop = context.scene.ACON_prop
    value = prop.bloom_threshold

    props.bloom_threshold = value
