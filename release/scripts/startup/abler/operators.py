import os
import bpy

from .lib.tracker import tracker
from .lib.materials import materials_setup
from .lib.remember_username import read_remembered_checkbox, read_remembered_username


class Acon3dToonStyleOperator(bpy.types.Operator):
    """Iterate all materials and change them into toon style"""

    bl_idname = "acon3d.toon_style"
    bl_label = "Toonify"
    bl_translation_context = "*"

    def execute(self, context):
        materials_setup.apply_ACON_toon_style()
        return {"FINISHED"}


class Acon3dLogoutOperator(bpy.types.Operator):
    """Logout user account"""

    bl_idname = "acon3d.logout"
    bl_label = "Log Out"
    bl_translation_context = "*"

    def execute(self, context):
        # prop를 업데이트 하면 ACON_userInfo도 업데이트
        prop = bpy.data.meshes.get("ACON_userInfo").ACON_prop
        path = bpy.utils.resource_path("USER")
        path_cookiesFolder = os.path.join(path, "cookies")
        path_cookiesFile = os.path.join(path_cookiesFolder, "acon3d_session")

        # TODO: 종료창 대신, is_dirty == True면 save 먼저 실행해주기
        #       save modal과 splash modal이 동시에 겹쳐지는 문제가 있음
        #       render.py에 있는 event timer를 참고하면 좋을듯
        if os.path.exists(path_cookiesFile):
            os.remove(path_cookiesFile)

            # login_status가 SUCCESS가 아닌 상태에서 modal_operator를 실행
            prop.login_status = "IDLE"
            bpy.ops.acon3d.modal_operator("INVOKE_DEFAULT")

            # 아이디 기억하기 체크박스 상태와 아이디 불러오기
            prop.remember_username = read_remembered_checkbox()
            prop.username = read_remembered_username()

            bpy.ops.wm.splash("INVOKE_DEFAULT")
        else:
            print("No login session file")

        tracker.logout()

        return {"FINISHED"}


classes = (
    Acon3dToonStyleOperator,
    Acon3dLogoutOperator,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
