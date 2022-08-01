import bpy
from bpy.types import Context


def change_bloom_threshold(self, context: Context) -> None:
    props = context.scene.eevee
    prop = context.scene.ACON_prop
    value = prop.bloom_threshold

    props.bloom_threshold = value


def change_bloom_knee(self, context: Context) -> None:
    props = context.scene.eevee
    prop = context.scene.ACON_prop
    value = prop.bloom_knee

    props.bloom_knee = value


def change_bloom_radius(self, context: Context) -> None:
    props = context.scene.eevee
    prop = context.scene.ACON_prop
    value = prop.bloom_radius

    props.bloom_radius = value


def change_bloom_intensity(self, context: Context) -> None:
    props = context.scene.eevee
    prop = context.scene.ACON_prop
    value = prop.bloom_intensity

    props.bloom_intensity = value


def change_bloom_clamp(self, context: Context) -> None:
    props = context.scene.eevee
    prop = context.scene.ACON_prop
    value = prop.bloom_clamp

    props.bloom_clamp = value
