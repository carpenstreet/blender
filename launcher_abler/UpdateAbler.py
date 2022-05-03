import pathlib
import requests
import logging
import os
import os.path
import sys
from typing import Tuple
from enum import Enum
from distutils.version import StrictVersion
import configparser
from AblerLauncherUtils import get_datadir, StateUI


if sys.platform == "win32":
    from win32com.client import Dispatch

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

LOG_FORMAT = (
    "%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s"
)
test_arg = len(sys.argv) > 1 and sys.argv[1] == "--test"
os.makedirs(get_datadir() / "Blender/2.96", exist_ok=True)
os.makedirs(get_datadir() / "Blender/2.96/updater", exist_ok=True) 
logging.basicConfig(
    filename=get_datadir() / "Blender/2.96/updater/AblerLauncher.log",
    format=LOG_FORMAT,
    level=logging.DEBUG,
    filemode="w",
)

logger = logging.getLogger()


def check_abler(dir_, installedversion) -> Tuple[Enum, list]:
    # 최신 릴리즈가 있는지 URL 주소로 확인
    finallist = None
    results = []
    state_ui = None
    url = "https://api.github.com/repos/acon3d/blender/releases/latest"
    if test_arg:
        url = "https://api.github.com/repos/acon3d/blender/releases"
    # TODO: 새 arg 받아서 테스트 레포 url 업데이트

    is_release, req, state_ui = get_req_from_url(url, state_ui, dir_)
    if state_ui:
        return state_ui, finallist

    if not is_release:
        state_ui = StateUI.no_release
        return state_ui, finallist

    get_results_from_req(req, results)

    if results:
        if installedversion is None or installedversion == "":
            installedversion = "0.0.0"

        # ABLER 릴리즈 버전 > 설치 버전
        if StrictVersion(results[0]["version"]) > StrictVersion(installedversion):
            state_ui = StateUI.update_abler
            finallist = results
            return state_ui, finallist

        # ABLER 릴리즈 버전 == 설치 버전
        else:
            state_ui = StateUI.execute

    # 통신 오류로 results가 없어서 바로 ABLER 실행
    else:
        state_ui = StateUI.execute

    return state_ui, finallist


def get_req_from_url(url, state_ui, dir_) -> Tuple[bool,dict,Enum]:
    # 깃헙 서버에서 url의 릴리즈 정보를 받아오는 함수

    # Do path settings save here, in case user has manually edited it
    config = configparser.ConfigParser()
    config.read(get_datadir() / "Blender/2.96/updater/config.ini")
    config.set("main", "path", dir_)
    with open(get_datadir() / "Blender/2.96/updater/config.ini", "w") as f:
        config.write(f)

    try:
        req = requests.get(url).json()
    except Exception as e:
        # self.statusBar().showMessage(
        #     "Error reaching server - check your internet connection"
        # )
        # logger.error(e)
        # self.frm_start.show()
        logger.error(e)
        state_ui = StateUI.error

    if test_arg:
        req = req[0]

    is_release = True
    try:
        is_release = req["message"] != "Not Found"
    except Exception as e:
        logger.debug("Release found")

    return is_release, req, state_ui


def get_results_from_req(req, results) -> None:
    # req에서 필요한 info를 results에 추가
    for asset in req["assets"]:
        target = asset["browser_download_url"]
        filename = target.split("/")[-1]
        target_type = "Release"
        version_tag = req["name"][1:]

        if sys.platform == "win32":
            if "Windows" in target and "zip" in target and target_type in target:
                info = {
                    "url": target,
                    "os": "Windows",
                    "filename": filename,
                    "version": version_tag,
                    "arch": "x64",
                }
                results.append(info)

        elif sys.platform == "darwin":
            if os.system("sysctl -in sysctl.proc_translated") == 1:
                if (
                    "macOS" in target
                    and "zip" in target
                    and target_type in target
                    and "M1" in target
                ):
                    info = {
                        "url": target,
                        "os": "macOS",
                        "filename": filename,
                        "version": version_tag,
                        "arch": "arm64",
                    }
                    results.append(info)
            else:
                if (
                    "macOS" in target
                    and "zip" in target
                    and target_type in target
                    and "Intel" in target
                ):
                    info = {
                        "url": target,
                        "os": "macOS",
                        "filename": filename,
                        "version": version_tag,
                        "arch": "x86_64",
                    }
                    results.append(info)
