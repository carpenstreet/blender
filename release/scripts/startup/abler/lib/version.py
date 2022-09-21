import os
import pathlib
import sys
import requests
import bpy
import configparser
from distutils.version import StrictVersion
from typing import Optional
from enum import Enum

# GitHub Repo의 URL 세팅
url = "https://api.github.com/repos/ACON3D/blender/releases/latest"
user_path = bpy.utils.resource_path("USER")
low_version_warning_visibility_path = os.path.join(user_path, "lvwh")


def set_updater():
    home = pathlib.Path.home()
    updater = None

    if sys.platform == "win32":
        # Pre-Release 고려하지 않고 런처 받아오기
        updater = os.path.join(
            home, "AppData/Roaming/Blender Foundation/Blender/2.96/updater"
        )
    elif sys.platform == "darwin":
        updater = os.path.join(home, "Library/Application Support/Blender/2.96/updater")

    return updater


def get_launcher():
    launcher = os.path.join(set_updater(), "AblerLauncher.exe")
    return launcher


def get_local_version():
    config = configparser.ConfigParser()
    if os.path.isfile(os.path.join(set_updater(), "config.ini")):
        config.read(os.path.join(set_updater(), "config.ini"))
        abler_ver = config["main"]["installed"]
    else:
        abler_ver = "0.0.0"

    # config.ini에 installed 정보가 없을 때 버전 처리
    if abler_ver == (None or ""):
        abler_ver = "0.0.0"

    return abler_ver


def get_server_version(url) -> Optional[str]:
    # Pre-Release 고려하지 않고 url 정보 받아오기
    req = None
    is_release = None
    abler_ver = None

    try:
        req = requests.get(url, timeout=5).json()
    except Exception as e:
        return None

    if ("message" in req.keys()) and (req["message"] == "Not Found"):
        print("Release Not Found.")
    elif "assets" in req.keys():
        for asset in req["assets"]:
            target = asset["browser_download_url"]
            filename = target.split("/")[-1]
            version_tag = filename.split("_")[-1][1:-4]

            if "Release" in target:
                abler_ver = version_tag
    else:
        print("GitHub API URL Error.")

    return abler_ver


def has_server_update():
    # 에이블러 버전만 비교하기
    server_ver_str = get_server_version(url)
    if not server_ver_str:
        return False

    local_ver = StrictVersion(get_local_version())
    server_ver = StrictVersion(server_ver_str)

    if local_ver < server_ver:
        return True


def get_file_version() -> Optional[str]:
    """
    파일이 어떤 에이블러 버전에서 저장되었는지를 반환

    0.2.6 이전 버전에서는 이 기능이 없었으므로, None 반환됨
    """
    if text_data := bpy.data.texts.get("ACON_metadata"):
        return text_data.ACON_metadata.file_version
    else:
        return None


class FileVersionCheckResult:
    CURRENT_VERSION = 1
    LOW_FILE_VERSION = 2
    HIGHER_FILE_VERSION = 3


def check_file_version():
    local_version = get_local_version()
    if file_version := get_file_version():
        sfv = StrictVersion(file_version)
        slv = StrictVersion(local_version)
        if sfv > slv:
            return FileVersionCheckResult.HIGHER_FILE_VERSION

        elif sfv < slv:
            return FileVersionCheckResult.LOW_FILE_VERSION

        else:
            return FileVersionCheckResult.CURRENT_VERSION
    else:
        return FileVersionCheckResult.LOW_FILE_VERSION


def update_file_version():
    text_data = bpy.data.texts.get("ACON_metadata")
    if text_data is None:
        text_data = bpy.data.texts.new("ACON_metadata")
    metadata = text_data.ACON_metadata
    metadata.file_version = get_local_version()


def read_low_version_warning_hidden() -> bool:
    try:
        with open(low_version_warning_visibility_path, "r") as f:
            return f.read().strip() == get_local_version()
    except:
        return False


def remember_low_version_warning_visibility(self, context):
    try:
        if context.window_manager.ACON_prop.hide_low_version_warning:
            with open(low_version_warning_visibility_path, "w") as f:
                f.write(get_local_version())
        else:
            os.remove(low_version_warning_visibility_path)
    except:
        pass
