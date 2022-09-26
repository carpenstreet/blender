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


import ctypes
import os
import pickle
import platform
import sys
import textwrap
import webbrowser
from json import JSONDecodeError

import bpy
import requests
from bpy.app.handlers import persistent

from .lib.async_task import AsyncTask
from .lib.login import is_process_single
from .lib.read_cookies import *

from .lib.tracker import tracker
from .lib.tracker._get_ip import user_ip
from .warning_modal import BlockingModalOperator
import subprocess
from .lib.version import (
    get_launcher,
    check_file_version,
    FileVersionCheckResult,
    update_file_version,
    has_server_update,
    get_file_version,
    get_local_version,
    read_low_version_warning_hidden,
)


is_first_run = False


def is_blend_open():
    return bpy.data.filepath != ""


class Acon3dStartUpFlowOperator(bpy.types.Operator):
    bl_idname = "acon3d.startup_flow"
    bl_label = "Startup flow"
    bl_translation_context = "*"

    def execute(self, context):
        global is_first_run
        is_first_run = True
        run_startup_flow()
        setup_next_startup_flow()
        return {"FINISHED"}


def setup_next_startup_flow():
    # NOTE: 블렌더 초기화 시점에 load_post.append 로 핸들러를 등록하면 startup_flow_handler 가 두 번 실행되는 문제가 있음.
    # 이를 회피하기 위해 첫 번째 실행을 하고 나서 핸들러 등록하고, wm_init_exit.c 에서 if 문 제거하는 workaround 적용함
    bpy.app.handlers.load_post.append(startup_flow_handler)


@persistent
def startup_flow_handler(_dummy):
    global is_first_run
    is_first_run = False
    run_startup_flow()


def run_startup_flow():
    if is_blend_open():
        start_check_file_version()
    elif is_first_run:
        start_check_server_version()


def start_check_file_version():
    hide_low_version_warning = read_low_version_warning_hidden()
    bpy.context.window_manager.ACON_prop.hide_low_version_warning = (
        hide_low_version_warning
    )
    check_result = check_file_version()
    if check_result == FileVersionCheckResult.HIGHER_FILE_VERSION:
        bpy.ops.acon3d.higher_file_version_error("INVOKE_DEFAULT")
    elif (
        check_result == FileVersionCheckResult.LOW_FILE_VERSION
        and not hide_low_version_warning
    ):
        bpy.ops.acon3d.low_file_version_warning("INVOKE_DEFAULT")
    elif is_first_run:
        start_check_server_version()
    else:
        start_authentication()


def start_check_server_version():
    if not is_first_run:
        return
    if has_server_update():
        bpy.ops.acon3d.update_alert("INVOKE_DEFAULT")
    else:
        start_authentication()


class Acon3dAlertOperator(bpy.types.Operator):
    bl_idname = "acon3d.alert"
    bl_label = ""

    title: bpy.props.StringProperty(name="Title")

    message_1: bpy.props.StringProperty(name="Message")

    message_2: bpy.props.StringProperty(name="Message")

    message_3: bpy.props.StringProperty(name="Message")

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text=self.title)
        if self.message_1:
            row = layout.row()
            row.scale_y = 0.7
            row.label(text=self.message_1)
        if self.message_2:
            row = layout.row()
            row.scale_y = 0.7
            row.label(text=self.message_2)
        if self.message_3:
            row = layout.row()
            row.scale_y = 0.7
            row.label(text=self.message_3)
        layout.separator()
        layout.separator()


class Acon3dNoticeInvokeOperator(bpy.types.Operator):
    bl_idname = "acon3d.notice_invoke"
    bl_label = ""

    width: 750
    title: bpy.props.StringProperty(name="Title")
    content: bpy.props.StringProperty(name="Content")
    link: bpy.props.StringProperty(name="Link")
    link_name: bpy.props.StringProperty(name="Link name")

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        self.width = 750
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=self.width)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        # 제목 위에 점으로 만든 줄
        row.scale_y = 0.5
        row.label(text="." * 1000)
        # 제목도 혹시 몰라서 line wrap 추가
        sub_lns = textwrap.fill(self.title, 70)
        spl = sub_lns.split("\n")
        for i, s in enumerate(spl):
            row = layout.row()
            if i == 0:
                row.label(text=s, icon="RIGHTARROW")
            else:
                row.label(text=s)

        row = layout.row()
        # 제목 아래에 점으로 만든 줄
        row.scale_y = 0.2
        row.label(text="." * 1000)
        # 내용에는 line wrap 넣어놨음. 현재 box 사이즈에 맞춰서 line wrap 하는 방법 추가 가능하면 좋겠음
        notice_list = self.content.split("\r\n")  # 개행문자를 기준으로 나눠서 리스트로 만든다.
        for notice_line in notice_list:
            if notice_line != "":
                sub_lns = textwrap.fill(notice_line, 75)
                spl = sub_lns.split("\n")
                for s in spl:
                    row = layout.row()
                    row.label(text=s)
            else:
                row = layout.row()
                row.separator()
        # link 집어넣는 코드
        if self.link != "" and self.link_name != "":
            row = layout.row()
            anchor = row.operator("acon3d.anchor", text=self.link_name, icon="URL")
            anchor.href = self.link
        layout.separator()


class Acon3dNoticeOperator(bpy.types.Operator):
    bl_idname = "acon3d.notice"
    bl_label = ""
    bl_description = "ABLER Service Notice"
    title: bpy.props.StringProperty(name="Title")
    content: bpy.props.StringProperty(name="Content", description="content")
    link: bpy.props.StringProperty(name="Link", description="link")
    link_name: bpy.props.StringProperty(name="Link Name", description="link_name")

    def execute(self, context):
        bpy.ops.acon3d.notice_invoke(
            "INVOKE_DEFAULT",
            title=self.title,
            content=self.content,
            link=self.link,
            link_name=self.link_name,
        )
        return {"FINISHED"}


class Acon3dModalOperator(BlockingModalOperator):
    bl_idname = "acon3d.modal_operator"
    bl_label = "Login Modal Operator"

    def _invoke_actual_modal(self, context, event):
        bpy.ops.wm.splash("INVOKE_DEFAULT")

    def should_close(self, context, event) -> bool:
        userInfo = bpy.data.meshes.get("ACON_userInfo")

        splash_closing = event.type in (
            "LEFTMOUSE",
            "MIDDLEMOUSE",
            "RIGHTMOUSE",
            "ESC",
            "RET",
        )

        if (
            userInfo
            and userInfo.ACON_prop.login_status == "SUCCESS"
            and (splash_closing or is_blend_open())
        ):
            return True
        return False

    def after_close(self, context, event):
        if read_remembered_show_guide():
            bpy.ops.acon3d.tutorial_guide_popup()


class NamedException(Exception):
    def __init__(self):
        super().__init__(type(self).__name__)


class GodoBadRequest(NamedException):
    """사용자 책임의 고도몰 응답 에러"""

    def __init__(self, response: requests.Response):
        super().__init__()
        self.response = response


class GodoServerError(NamedException):
    """서버 책임의 고도몰 응답 에러"""

    def __init__(self, response: requests.Response):
        super().__init__()
        self.response = response


class AconServerError(NamedException):
    """서버 책임의 사내 인증 서버 에러"""

    def __init__(self, response: requests.Response):
        super().__init__()
        self.response = response


class LoginTask(AsyncTask):
    cookies_final = None

    def __init__(self):
        super().__init__(timeout=10)

        self.prop = bpy.data.meshes.get("ACON_userInfo").ACON_prop
        self.username = self.prop.username
        self.password = (
            self.prop.password_shown if self.prop.show_password else self.prop.password
        )

    def request_login(self):
        prop = self.prop

        prop.login_status = "LOADING"
        self.start()

    def _task(self):
        response_godo = requests.post(
            "https://www.acon3d.com/api/login.php",
            data={"loginId": self.username, "loginPwd": self.password},
        )

        if response_godo.status_code >= 500:
            raise GodoServerError(response_godo)

        try:
            response_godo.json()
        # username/password 틀렸을 때는 200 상태코드로
        # 일반 텍스트 형식의 한국어 에러 메시지가 오고 있음 -> JSONDecodeError 발생
        except JSONDecodeError:
            raise GodoBadRequest(response_godo)

        cookies_godo = response_godo.cookies

        response = requests.post(
            "https://api-v2.acon3d.com/auth/acon3d/signin",
            data={"account": self.username, "password": self.password},
            cookies=cookies_godo,
        )

        # 고도몰 인증을 통과했다면 반드시 200 상태코드로 응답이 와야 함
        if response.status_code != 200:
            raise AconServerError(response)

        self.cookie_final = requests.cookies.merge_cookies(
            cookies_godo, response.cookies
        )

    def _on_success(self):

        tracker.login()
        tracker.update_profile(self.username, user_ip)

        prop = self.prop
        path = bpy.utils.resource_path("USER")
        path_cookiesFolder = os.path.join(path, "cookies")
        path_cookiesFile = os.path.join(path_cookiesFolder, "acon3d_session")

        with open(path_cookiesFile, "wb") as cookies_file:
            pickle.dump(self.cookie_final, cookies_file)

        if prop.remember_username:
            remember_username(prop.username)
        else:
            delete_remembered_username()

        prop.login_status = "SUCCESS"
        prop.username = ""
        prop.password = ""
        prop.password_shown = ""

        window = bpy.context.window
        width = window.width
        height = window.height
        window.cursor_warp(width / 2, height / 2)

        def moveMouse():
            window.cursor_warp(width / 2, (height / 2) - 150)

        bpy.app.timers.register(moveMouse, first_interval=0.1)
        bpy.context.window.cursor_set("DEFAULT")

    def _on_failure(self, e: BaseException):
        tracker.login_fail(type(e).__name__)

        self.prop.login_status = "FAIL"
        print("Login request has failed.")
        print(e)

        if isinstance(e, GodoBadRequest):
            bpy.ops.acon3d.alert(
                "INVOKE_DEFAULT",
                title="Login failed",
                message_1="Incorrect username or password.",
            )
        else:
            bpy.ops.acon3d.alert(
                "INVOKE_DEFAULT",
                title="Login failed",
                message_1="If this happens continuously",
                message_2='please contact us at "cs@acon3d.com".',
            )
            # 사용자 책임의 에러가 아닌 경우 Sentry error reporting
            raise e


class Acon3dLoginOperator(bpy.types.Operator):
    bl_idname = "acon3d.login"
    bl_label = "Login"
    bl_translation_context = "*"

    def execute(self, context):
        context.window.cursor_set("WAIT")
        LoginTask().request_login()
        return {"FINISHED"}


class Acon3dAnchorOperator(bpy.types.Operator):
    bl_idname = "acon3d.anchor"
    bl_label = "Go to link"
    bl_translation_context = "*"

    href: bpy.props.StringProperty(name="href", description="href")
    description_text: bpy.props.StringProperty(
        name="description_text", description="description_text"
    )

    @classmethod
    def description(cls, context, properties):
        if properties.description_text:
            return bpy.app.translations.pgettext(properties.description_text)
        else:
            return None

    def execute(self, context):
        webbrowser.open(self.href)

        return {"FINISHED"}


@persistent
def start_authentication():
    prefs = bpy.context.preferences
    prefs.view.show_splash = True

    userInfo = bpy.data.meshes.new("ACON_userInfo")
    prop = userInfo.ACON_prop
    prop.login_status = "IDLE"

    try:
        path = bpy.utils.resource_path("USER")
        path_cookiesFolder = os.path.join(path, "cookies")
        path_cookiesFile = os.path.join(path_cookiesFolder, "acon3d_session")

        if not os.path.isdir(path_cookiesFolder):
            os.mkdir(path_cookiesFolder)

        if not os.path.exists(path_cookiesFile):
            raise
        prop.remember_username = read_remembered_checkbox()

        with open(path_cookiesFile, "rb") as cookiesFile:
            cookies = pickle.load(cookiesFile)

        response = requests.get(
            "https://api-v2.acon3d.com/auth/acon3d/refresh", cookies=cookies
        )

        responseData = response.json()
        if token := responseData["accessToken"]:
            if is_process_single():
                tracker.login_auto()
            prop.login_status = "SUCCESS"

    except:
        print("Failed to load cookies")

    if prop.remember_username:
        prop.username = read_remembered_username()

    if is_first_run:
        bpy.ops.acon3d.modal_operator("INVOKE_DEFAULT")


class Acon3dUpdateAlertOperator(BlockingModalOperator):
    bl_idname = "acon3d.update_alert"
    bl_label = ""
    bl_translation_context = "*"

    def draw_modal(self, layout):
        padding_size = 0.01
        content_size = 1.0 - 2 * padding_size
        box = layout.box()
        main = box.column()

        main.label(text="")

        row = main.split(factor=padding_size)
        row.label(text="")
        row = row.split(factor=content_size)
        col = row.column()
        col.label(text="Latest version found for ABLER. Do you want to update?")
        col.label(
            text="When using an older version of ABLER, some features may not work properly."
        )
        col.operator("acon3d.update_abler", text="Update ABLER")
        col.operator("acon3d.close_blocking_modal", text="Close")
        row.label(text="")

        main.label(text="")

    def after_close(self, context, event):
        start_authentication()


class Acon3dUpdateAblerOperator(bpy.types.Operator):
    bl_idname = "acon3d.update_abler"
    bl_label = ""
    bl_description = "Update ABLER with ABLER Launcher"
    bl_translation_context = "*"

    def execute(self, context):
        launcher = get_launcher()

        # 관리자 권한이 필요한 프로그램을 실행하는 옵션
        subprocess.Popen(launcher, shell=True)
        bpy.ops.wm.quit_blender()

        return {"FINISHED"}


class Acon3dLowFileVersionWarning(BlockingModalOperator):
    bl_idname = "acon3d.low_file_version_warning"
    bl_label = "Warning"

    def draw_modal(self, layout):
        tr = bpy.app.translations.pgettext
        file_version = get_file_version() or "< 0.2.6"
        client_version = get_local_version()

        padding_size = 0.01
        content_size = 1.0 - 2 * padding_size
        box = layout.box()
        main = box.column()

        main.label(text="")

        row = main.split(factor=padding_size)
        row.label(text="")
        row = row.split(factor=content_size)
        col = row.column()
        col.label(
            text=tr(
                "This file was created in a older version of ABLER ($(fileVer))"
            ).replace("$(fileVer)", file_version)
        )
        col.label(
            text=tr(
                "If you save in the current version ($(clientVer)), you will not be able to load this file from older version of ABLER."
            ).replace("$(clientVer)", client_version)
        )

        row = col.row()
        row.prop(
            bpy.context.window_manager.ACON_prop,
            "hide_low_version_warning",
            text="",
            icon="CHECKBOX_HLT",
            emboss=False,
            invert_checkbox=True,
        )
        row.label(text="Don’t show this message again.")

        col.operator("acon3d.close_blocking_modal", text="Close")
        row.label(text="")

        main.label(text="")

    def after_close(self, context, event):
        start_check_server_version()


class Acon3dHigherFileVersionError(BlockingModalOperator):
    bl_idname = "acon3d.higher_file_version_error"
    bl_label = "Higher File Version Error"

    def draw_modal(self, layout):
        tr = bpy.app.translations.pgettext
        padding_size = 0.01
        content_size = 1.0 - 2 * padding_size
        box = layout.box()
        main = box.column()

        main.label(text="")

        row = main.split(factor=padding_size)
        row.label(text="")
        row = row.split(factor=content_size)
        col = row.column()
        col.label(text="The file was created in a newer version of ABLER.")
        col.label(
            text=tr("You have ABLER version $(clientVer)").replace(
                "$(clientVer)", get_local_version()
            )
        )
        col.label(
            text=tr("You need ABLER version $(fileVer)").replace(
                "$(fileVer)", get_file_version()
            )
        )
        col.operator("acon3d.update_abler", text="Update ABLER")
        col.operator("acon3d.close_abler", text="Close ABLER")
        row.label(text="")

        main.label(text="")

    def after_close(self, context, event):
        start_check_server_version()


class Acon3dCloseAblerOprator(bpy.types.Operator):
    bl_idname = "acon3d.close_abler"
    bl_label = "Close ABLER"
    bl_description = "Close ABLER"
    bl_translation_context = "*"

    def execute(self, context):
        bpy.ops.wm.quit_blender()
        return {"FINISHED"}


classes = (
    Acon3dAlertOperator,
    Acon3dModalOperator,
    Acon3dLoginOperator,
    Acon3dAnchorOperator,
    Acon3dNoticeOperator,
    Acon3dNoticeInvokeOperator,
    Acon3dUpdateAlertOperator,
    Acon3dUpdateAblerOperator,
    Acon3dLowFileVersionWarning,
    Acon3dHigherFileVersionError,
    Acon3dStartUpFlowOperator,
    Acon3dCloseAblerOprator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
