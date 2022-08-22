import os
import pathlib
import sys
import requests
import subprocess


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
                launcher_ver = line.split("=")[-1]
            elif "installed" in line:
                abler_ver = line.split("=")[-1]

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


def compare_version(local, server):
    print(f"launcher version: {local[0]} vs {server[0]}")
    print(f"abler version: {local[1]} vs {server[1]}")
    launcher, config = get_config()

    if local[0] >= server[0] or local[1] >= server[1]:
        subprocess.call(launcher)


compare_version(get_local_version(), get_server_version(url))
