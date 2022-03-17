from typing import Any, Dict, List, Union, Tuple, Optional
from bpy.types import Context
import bpy
from . import cameras
from .tracker import tracker


def toggleConstraintToCamera(self, context):

    cameras.makeSureCameraExists()

    obj = context.object
    if obj.ACON_prop.constraint_to_camera_rotation_z:
        tracker.look_at_me()

    setConstraintToCameraByObject(obj, context)


# items should be a global variable due to a bug in EnumProperty
items: List[Tuple[str, str, str]] = []


def add_group_list_from_collection(
    self, context: Context
) -> List[Tuple[str, str, str]]:
    items.clear()

    obj = context.object
    items.append((obj.name, obj.name, "", "OUTLINER_OB_MESH", 0))

    if collection := bpy.context.object.ACON_prop.group:
        for item in collection:
            items.append((item.name, item.name, "", "OUTLINER_COLLECTION", 1))

    return items


def setConstraintToCameraByObject(obj, context=None):

    if not context:
        context = bpy.context

    look_at_me = obj.ACON_prop.constraint_to_camera_rotation_z

    for obj in context.selected_objects:

        prop = obj.ACON_prop
        const = obj.constraints.get("ACON_const_copyRotation")

        if look_at_me:

            if not const:
                const = obj.constraints.new(type="COPY_ROTATION")
                const.name = "ACON_const_copyRotation"
                const.use_x = False
                const.use_y = False
                const.use_z = True

            const.target = context.scene.camera
            const.mute = False

        elif const:

            const.mute = True

        if prop.constraint_to_camera_rotation_z != look_at_me:
            prop.constraint_to_camera_rotation_z = look_at_me


def step(edge0: tuple[float], edge1: tuple[float], x: float) -> tuple[float]:
    return tuple(edge0[i] + ((edge1[i] - edge0[i]) * x) for i in [0, 1, 2])


def toggleUseState(self, context):

    use_state = self.use_state

    prop = context.object.ACON_prop
    if prop.use_state:
        tracker.use_state_on()
    else:
        tracker.use_state_off()

    if use_state:

        for obj in context.selected_objects:

            prop = obj.ACON_prop

            if (obj == context.object or not prop.use_state) and not prop.state_exists:
                for att in ["location", "rotation_euler", "scale"]:

                    vector = getattr(obj, att)
                    setattr(prop.state_begin, att, vector)
                    setattr(prop.state_end, att, vector)

                prop.state_exists = True

            if not prop.use_state:

                prop.use_state = True

        prop.state_slider = 1

    else:

        context.object.ACON_prop.state_slider = 0

        for obj in context.selected_objects:

            prop = obj.ACON_prop

            if prop.use_state:

                prop.use_state = False


def moveState(self, context):

    state_slider = self.state_slider

    for obj in context.selected_objects:

        prop = obj.ACON_prop

        if obj != context.object and not prop.use_state:
            continue

        for att in ["location", "rotation_euler", "scale"]:

            vector_begin = getattr(prop.state_begin, att)
            vector_end = getattr(prop.state_end, att)
            vector_mid = step(vector_begin, vector_end, state_slider)

            setattr(obj, att, vector_mid)

        if prop.state_slider != state_slider:
            prop.state_slider = state_slider
