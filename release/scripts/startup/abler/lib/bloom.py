import bpy
from bpy.types import Context


def change_bloom_threshold(self, context: Context) -> None:
    eevee_prop = context.scene.eevee
    prop = context.scene.ACON_prop
    value = prop.bloom_threshold

    eevee_prop.bloom_threshold = value


def change_bloom_knee(self, context: Context) -> None:
    eevee_prop = context.scene.eevee
    prop = context.scene.ACON_prop
    value = prop.bloom_knee

    eevee_prop.bloom_knee = value


def change_bloom_radius(self, context: Context) -> None:
    eevee_prop = context.scene.eevee
    prop = context.scene.ACON_prop
    value = prop.bloom_radius

    eevee_prop.bloom_radius = value


def change_bloom_color(self, context: Context) -> None:
    eevee_prop = context.scene.eevee
    prop = context.scene.ACON_prop
    value = prop.bloom_color

    eevee_prop.bloom_color = value


def change_bloom_intensity(self, context: Context) -> None:
    eevee_prop = context.scene.eevee
    prop = context.scene.ACON_prop
    value = prop.bloom_intensity

    eevee_prop.bloom_intensity = value


def change_bloom_clamp(self, context: Context) -> None:
    eevee_prop = context.scene.eevee
    prop = context.scene.ACON_prop
    value = prop.bloom_clamp

    eevee_prop.bloom_clamp = value
