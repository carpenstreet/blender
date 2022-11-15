import bpy
from ..lib.read_cookies import read_remembered_checkbox, read_remembered_username


def get_or_init_user_info():
    if userInfo := bpy.data.meshes.get("ACON_userInfo"):
        return userInfo
    userInfo = bpy.data.meshes.new("ACON_userInfo")
    prop = userInfo.ACON_prop
    prop.remember_username = read_remembered_checkbox()

    if prop.remember_username:
        prop.username = read_remembered_username()

    return userInfo
