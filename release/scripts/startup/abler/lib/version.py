import os
import pathlib
import sys
import requests


def get_config():
    home = pathlib.Path.home()
    updater = None

    if sys.platform == "win32":
        updater = os.path.join(
            home, "AppData/Roaming/Blender Foundation/Blender/2.96/updater"
        )
    elif sys.platform == "darwin":
        updater = os.path.join(
            home, "Library/Application Support/Blender/2.96/updater"
        )

    launcher = os.path.join(updater, "AblerLauncher.exe")
    config = os.path.join(updater, "config.ini")

    return config


def get_config_version(config):
    abler_ver = None
    launcher_ver = None

    with open(config, "r") as f:
        for line in f.readlines():
            line = line.strip("\n")

            if "installed" in line:
                abler_ver = line.split(" ")[-1]
            elif "launcher" in line:
                launcher_ver = line.split(" ")[-1]

    print(f"[config.ini]")
    print(f"ABLER    ver : {abler_ver}")
    print(f"Launcher ver : {launcher_ver}")


def get_server_version():
    # Pre-Release 고려하지 않고 url 정보 받아오기

    """GitHub Repo의 URL 세팅"""
    url = "https://api.github.com/repos/ACON3D/blender/releases/latest"
    req = None
    is_release = None
    version_tag = None

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

            # print(f"Version tag: {version_tag}")

            if "Launcher" in target:
                print(f"Launcher version: {version_tag}")
            elif "Release" in target:
                print(f"ABLER version: {version_tag}")




get_config_version(get_config())
get_server_version()
