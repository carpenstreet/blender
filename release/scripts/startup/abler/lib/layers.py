# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


import bpy
from bpy.app.handlers import persistent
from bpy.types import Collection, Object
from typing import Any, List, Optional, Tuple, Union


def handleLayerVisibilityOnSceneChange(oldScene, newScene):

    if not oldScene or not newScene:
        print("Invalid oldScene / newScene given")
        return

    for i, oldProp in enumerate(oldScene.l_exclude):
        newProp = newScene.l_exclude[i]

        if oldProp.value is not newProp.value:
            target_layer = bpy.data.collections[newProp.name]
            for objs in target_layer.objects:
                objs.hide_viewport = not (newProp.value)
                objs.hide_render = not (newProp.value)

        if oldProp.lock is not newProp.lock:
            target_layer = bpy.data.collections[newProp.name]
            for objs in target_layer.objects:
                objs.hide_select = newProp.lock


def up(group_list: List[Collection], group_item: Collection) -> Optional[Collection]:
    """
    group_list: List of ancester collections
    group_item: Collection to find upper item of
    """
    try:
        idx: int = group_list.index(group_item)
        return group_list[idx - 1] if idx > 0 else group_list[0]
    except:
        return None


def down(
    group_list: List[Collection], group_item: Collection
) -> Optional[Union[Collection, str]]:
    """
    group_list: List of ancester collections
    group_item: Collection to find item below of
    """
    try:
        idx: int = group_list.index(group_item)
        return group_list[idx + 1] if idx < len(group_list) - 1 else "object"
    except:
        return None


def group_navigate_up(
    selected_group_prop: Any,
    root_ancester_collection: Collection,
    ordered_ancester_collections: List[Collection],
) -> None:
    if selected_group_prop.current_root_group != root_ancester_collection.name:
        return
    if selected_group_prop.current_group == "":
        selection = ordered_ancester_collections[-1]
    else:
        selection = up(
            ordered_ancester_collections,
            bpy.data.collections[selected_group_prop.current_group],
        )
    if not selection:
        try:
            selection = ordered_ancester_collections[-1]
            selected_group_prop.current_group = selection.name
        except Exception as e:
            print(e)
            return selectByGroup("TOP")
    # group-group-object의 구조를 가진 경우, UP을 실행해도
    # 여러번 눌러야 하는 경우가 있음. 그래서 while 문으로
    # 처리했지만, root group까지 이런 구조인 오브젝트들이
    # 있어서 for loop로 최대 5회 돌도록 처리함.
    for _ in range(5):
        if len(selection.all_objects) > 1:
            break
        selection = up(ordered_ancester_collections, selection)
    selected_group_prop.current_group = selection.name
    for obj in selection.all_objects:
        obj.select_set(True)


def group_navigate_top(
    selected_group_prop: Any,
    root_ancester_collection: Collection,
    ordered_ancester_collections: List[Collection],
):
    selected_group_prop.current_group = root_ancester_collection.name
    for obj in root_ancester_collection.all_objects:
        obj.select_set(True)


def group_navigate_down(
    selected_group_prop: Any,
    root_ancester_collection: Collection,
    ordered_ancester_collections: List[Collection],
) -> None:
    if selected_group_prop.current_root_group != root_ancester_collection.name:
        return
    if selected_group_prop.current_group == "":
        selection = "object"
    else:
        selection = down(
            ordered_ancester_collections,
            bpy.data.collections[selected_group_prop.current_group],
        )
    if not selection:
        return selectByGroup("BOTTOM")
    slctd_objs = bpy.context.selected_objects.copy()
    if selection == "object":
        selected_group_prop.current_group = ""
        for obj in slctd_objs:
            if obj != bpy.context.active_object:
                obj.select_set(False)
        return
    selected_group_prop.current_group = selection.name
    for obj in slctd_objs:
        if obj.name not in selection.all_objects:
            obj.select_set(False)


def group_navigate_bottom(
    selected_group_prop: Any,
    root_ancester_collection: Collection,
    ordered_ancester_collections: List[Collection],
):
    # Put last group in prop
    selected_group_prop.current_group = ""
    slctd_objs = bpy.context.selected_objects.copy()
    for obj in slctd_objs:
        if obj != bpy.context.active_object:
            obj.select_set(False)


def init_group_navigation(
    direction: str,
) -> Optional[Tuple[Any, Collection, List[Collection]]]:
    selected_object: Object = bpy.context.active_object
    selected_group_prop = bpy.context.scene.ACON_selected_group
    if not selected_object:
        selected_group_prop.current_root_group = ""
        selected_group_prop.current_group = ""
        return

    group_props = selected_object.ACON_prop.group
    group_length = len(group_props)
    if not group_length:
        return
    last_group_prop = group_props[0]
    ordered_group_list = [
        bpy.data.collections[item.name]
        for item in reversed(group_props)
        if item.name in bpy.data.collections.keys()
    ]
    # skip component-defined groups when navigating
    selected_group = None
    g_index = 0
    while selected_group is None and g_index < group_length:
        selected_group = bpy.data.collections.get(group_props[g_index].name)
        g_index += 1

    ordered_ancester_collections = ordered_group_list
    if ordered_ancester_collections:
        root_ancester_collection: Collection = ordered_ancester_collections[0]
    else:
        return

    # Put root group in prop
    selected_group_prop.current_root_group = root_ancester_collection.name

    return selected_group_prop, root_ancester_collection, ordered_ancester_collections


def selectByGroup(direction: str) -> None:
    if bpy.context.active_object is None:
        return
    init_val = init_group_navigation(direction)
    if init_val is None:
        return
    (
        selected_group_prop,
        root_ancester_collection,
        ordered_ancester_collections,
    ) = init_val
    if direction == "BOTTOM":
        group_navigate_bottom(
            selected_group_prop, root_ancester_collection, ordered_ancester_collections
        )
    elif direction == "DOWN":
        group_navigate_down(
            selected_group_prop, root_ancester_collection, ordered_ancester_collections
        )
    elif direction == "TOP":
        group_navigate_top(
            selected_group_prop, root_ancester_collection, ordered_ancester_collections
        )
    elif direction == "UP":
        group_navigate_up(
            selected_group_prop, root_ancester_collection, ordered_ancester_collections
        )


def select_group_prop(name: str) -> None:
    if name in bpy.data.collections.keys():
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        for obj in bpy.data.collections.get(name).all_objects:
            obj.select_set(True)


@persistent
def checkObjectSelectionChange(dummy):

    depsgraph = bpy.context.evaluated_depsgraph_get()
    if not depsgraph.id_type_updated("SCENE"):
        return

    new_selected_objects_str = "".join(obj.name for obj in bpy.context.selected_objects)

    ACON_prop = bpy.context.scene.ACON_prop

    if new_selected_objects_str == ACON_prop.selected_objects_str:
        return

    if new_selected_objects_str:
        selectByGroup(bpy.context.scene.ACON_selected_group.direction)

    ACON_prop.selected_objects_str = "".join(
        obj.name for obj in bpy.context.selected_objects
    )


# -----------------------------------------------------------------------------
# Not used for now


# def get_ordered_ancester_collections_from_object(
#     obj: Object,
# ) -> List[Collection]:
#     if not obj or not obj.ACON_prop or not obj.ACON_prop.group:
#         return

#     group_props = obj.ACON_prop.group

#     group_length = len(group_props)
#     if not group_length:
#         return

#     last_group_prop = group_props[-1]

#     selected_group = bpy.data.collections.get(last_group_prop.name)
#     return get_ordered_ancester_collections(selected_group)


# def get_ordered_ancester_collections(
#     collection: Collection,
# ) -> List[Collection]:
#     parents = []
#     get_ancester_collections(collection, parents)
#     ret_list = list(reversed(quick_sort_by_hierarchy(parents)))
#     ret_list.append(collection)
#     return ret_list


# def is_ancester_collection(a: Collection, b: Collection) -> bool:
#     parents = []
#     get_ancester_collections(a, parents)
#     return b in parents


# def get_ancester_collections(collection: Collection, parents: List[Collection]) -> None:
#     for parent_collection in bpy.data.collections:
#         if collection.name in parent_collection.children.keys():
#             if not is_component_collection(parent_collection):
#                 parents.append(parent_collection)
#             get_ancester_collections(parent_collection, parents)
#             return


# def get_parent_collection(
#     collection: Collection,
# ) -> Collection:
#     for parent_collection in bpy.data.collections:
#         if collection.name in parent_collection.children.keys():
#             return parent_collection


# def is_component_collection(collection: Collection) -> bool:
#     return (
#         collection.name in bpy.data.collections.get("Components").children.keys()
#         or collection.name == "Components"
#     )


# def quick_sort_by_hierarchy(
#     arr: List[Collection],
# ) -> List[Collection]:
#     if len(arr) <= 1:
#         return arr
#     pivot = arr[len(arr) // 2]
#     lesser_arr, equal_arr, greater_arr = [], [], []
#     for col in arr:
#         if is_ancester_collection(col, pivot):
#             lesser_arr.append(col)
#         elif is_ancester_collection(pivot, col):
#             greater_arr.append(col)
#         else:
#             equal_arr.append(col)
#     return (
#         quick_sort_by_hierarchy(lesser_arr)
#         + equal_arr
#         + quick_sort_by_hierarchy(greater_arr)
#     )
