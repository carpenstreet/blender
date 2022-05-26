import os
import bpy
from .lib.materials import materials_setup
from .lib.remember_username import read_remembered_checkbox, read_remembered_username


class Acon3dToonStyleOperator(bpy.types.Operator):
    """Iterate all materials and change them into toon style"""

    bl_idname = "acon3d.toon_style"
    bl_label = "Toonify"
    bl_translation_context = "*"

    def execute(self, context):
        materials_setup.applyAconToonStyle()
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

        # TODO: New, Quit 대화창을 사용하지 말고, is_dirty == True 면 save_as() 실행해주기
        #       save_as()에서 modal을 실행할 때, sleep()을 하면 return {"FINISHED"}가 늦어져서 sleep() 사용 불가능
        #       Render에 있는 event timer를 참고하면 좋을 것 같음
        if os.path.exists(path_cookiesFile):
            os.remove(path_cookiesFile)

            # login_status가 SUCCESS가 아닌 상태에서 modal_operator를 실행
            prop.login_status = "IDLE"
            bpy.ops.acon3d.modal_operator("INVOKE_DEFAULT")

            # 아이디 기억하기 체크박스 상태와 아이디 불러오기
            prop.remember_username = read_remembered_checkbox()
            prop.username = read_remembered_username()

            bpy.ops.wm.splash("INVOKE_DEFAULT")

            # TODO: bpy.ops.wm.read_homefile()을 사용해 현재 파일 처리 과정 구현
            #       현재 splash 화면에서 프로그램을 종료하면 Quit 대화창으로 저장 기능을 사용할 수는 있지만
            #       splash 화면과 저장 modal이 충돌할 가능성 있음

        else:
            print("No login session file")

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
