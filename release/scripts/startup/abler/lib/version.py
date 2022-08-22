import os
import pathlib
import sys
import requests
import subprocess
import bpy
from distutils.version import StrictVersion


# GitHub Repo의 URL 세팅
url = "https://api.github.com/repos/ACON3D/blender/releases/latest"


def get_config():
    home = pathlib.Path.home()
    updater = None
    launcher = None

    if sys.platform == "win32":
        updater = os.path.join(
            home, "AppData/Roaming/Blender Foundation/Blender/2.96/updater"
        )
        launcher = os.path.join(updater, "AblerLauncher.exe")
    elif sys.platform == "darwin":
        updater = os.path.join(home, "Library/Application Support/Blender/2.96/updater")

    config = os.path.join(updater, "config.ini")

    return launcher, config


def get_local_version():
    launcher_ver = None
    abler_ver = None
    launcher, config = get_config()

    with open(config, "r") as f:
        for line in f.readlines():
            line = line.strip("\n")

            if "launcher" in line:
                launcher_ver = line.split("=")[-1].strip()
            elif "installed" in line:
                abler_ver = line.split("=")[-1].strip()

    return [launcher_ver, abler_ver]


def get_server_version(url):
    # Pre-Release 고려하지 않고 url 정보 받아오기
    req = None
    is_release = None
    launcher_ver = None
    abler_ver = None

    try:
        req = requests.get(url).json()
    except Exception as e:
        print(f"Error: {e}")

    try:
        is_release = req["message"] != "Not Found"
    except Exception as e:
        print(f"Release found")
    finally:
        for asset in req["assets"]:
            target = asset["browser_download_url"]
            filename = target.split("/")[-1]
            version_tag = filename.split("_")[-1][1:-4]

            if "Launcher" in target:
                launcher_ver = version_tag
            elif "Release" in target:
                abler_ver = version_tag

    return [launcher_ver, abler_ver]


def compare_version():
    # 에이블러 버전만 비교하기
    launcher, config = get_config()
    local_ver = StrictVersion(get_local_version()[1])
    server_ver = StrictVersion(get_server_version(url)[1])

    if len(sys.argv) > 1:
        if local_ver < server_ver:
            bpy.ops.acon3d.alert_update(
                "INVOKE_DEFAULT",
                title="에이블러 업데이트 안내",
                message_1="최신 버전의 에이블러가 있습니다. 업데이트 하시겠습니까?",
                message_2="이전 버전의 에이블러 사용 시, 일부 기능이 작동하지 않을 수 있습니다."
            )
        else:
            # TODO: 현재 테스트 중이기 때문에, 에이블러 계속 실행하는 것으로 바뀌주기
            bpy.ops.acon3d.alert_update(
                "INVOKE_DEFAULT",
                title="에이블러 업데이트 안내",
                message_1="최신 버전의 에이블러가 있습니다. 업데이트 하시겠습니까?",
                message_2="이전 버전의 에이블러 사용 시, 일부 기능이 작동하지 않을 수 있습니다."
            )
