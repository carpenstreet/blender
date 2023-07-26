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


def get_first_layer_name_of_object(obj: Object):
    collections = obj.users_collection
    layer_collection = bpy.data.collections.get("Layers")

    if not layer_collection:
        return None

    for c in collections:
        if c.name in layer_collection.children:
            return c.name

    return None


def handle_layer_visibility_on_scene_change(oldScene, newScene):
    if not oldScene or not newScene:
        print("Invalid oldScene / newScene given")
        return

    visited = set()

    def get_parent_values(obj: Object):
        cur = obj.parent
        parent_value = True
        parent_lock = False

        while cur:
            if parent_value or not parent_lock:
                # new scene 에서 변경될 object 의 레이어 정보를 가져옴
                new_scene_layer = None
                for l in newScene.l_exclude:
                    if l.name == get_first_layer_name_of_object(cur):
                        new_scene_layer = l
                        break
                if new_scene_layer:
                    if parent_value:
                        parent_value = parent_value and new_scene_layer.value
                    if not parent_lock:
                        parent_lock = parent_lock or new_scene_layer.lock

            if not parent_value and parent_lock:
                return parent_value, parent_lock
            cur = cur.parent
        return parent_value, parent_lock

    def update_info(obj: Object, new_value: bool, new_lock: bool):
        if obj.name in visited:
            return
        visited.add(obj.name)

        if new_value is not None:
            for l in newScene.l_exclude:
                if l.name == get_first_layer_name_of_object(obj) and not l.value:
                    new_value = False
                    break

            obj.hide_set(not new_value)

        if new_lock is not None:
            if not new_lock:
                for l in newScene.l_exclude:
                    if l.name == get_first_layer_name_of_object(obj) and l.lock:
                        new_lock = True
                        break

            obj.hide_select = new_lock

        for o in obj.children:
            update_info(o, new_value, new_lock)

    for i, oldInfo in enumerate(oldScene.l_exclude):
        # oldScene의 l_exclude 갯수가 newScene보다 오버될 때
        # 오버되는 i는 따로 처리할 필요가 없으므로 넘어가도록 처리함
        if i > len(newScene.l_exclude) - 1:
            break

        newInfo = newScene.l_exclude[i]

        is_value_equal = oldInfo.value is newInfo.value
        is_lock_equal = oldInfo.lock is newInfo.lock

        if not is_value_equal or not is_lock_equal:
            target_layer = bpy.data.collections[newInfo.name]

            new_value = newInfo.value if not is_value_equal else None
            new_lock = newInfo.lock if not is_lock_equal else None

            for obj in target_layer.objects:
                parent_value, parent_lock = get_parent_values(obj)
                new_value = new_value and parent_value
                new_lock = new_lock or parent_lock
                update_info(obj, new_value, new_lock)
