import os
import pathlib
import sys
import requests
import bpy
import configparser
from distutils.version import StrictVersion
from typing import Optional

# GitHub Repo의 URL 세팅
url = "https://api.github.com/repos/ACON3D/blender/releases/latest"


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


def show_update_alert():
    # 에이블러 버전만 비교하기
    server_ver_str = get_server_version(url)
    if not server_ver_str:
        return False

    local_ver = StrictVersion(get_local_version())
    server_ver = StrictVersion(server_ver_str)

    if (len(sys.argv) > 1) and (local_ver < server_ver):
        bpy.ops.acon3d.update_alert("INVOKE_DEFAULT")
