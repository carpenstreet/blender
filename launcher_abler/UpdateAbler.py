from __future__ import annotations

from enum import Enum

import requests
from xml.etree.ElementTree import fromstring, Element
import logging
import os
import os.path
import sys
from typing import Tuple, Optional
from distutils.version import StrictVersion
import configparser
from AblerLauncherUtils import *

if sys.platform == "win32":
    from win32com.client import Dispatch

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

LOG_FORMAT = (
    "%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s"
)
os.makedirs(get_datadir() / "Blender/2.96", exist_ok=True)
os.makedirs(get_datadir() / "Blender/2.96/updater", exist_ok=True)
logging.basicConfig(
    filename=get_datadir() / "Blender/2.96/updater/AblerLauncher.log",
    format=LOG_FORMAT,
    level=logging.DEBUG,
    filemode="w",
)

logger = logging.getLogger()


def check_abler(dir_: str, installedversion: str) -> Tuple[Enum, Optional[list]]:
    """최신 릴리즈가 있는지 URL 주소로 확인"""

    finallist = None
    results = []
    state_ui = StateUI.none

    # URL settings
    # Pre-Release 테스트 시에는 req = req[0]으로 pre-release 데이터 받아오기
    url = set_url()

    is_release, req, state_ui = get_req_from_url(url, state_ui, dir_)

    if state_ui != StateUI.none:
        return state_ui, finallist

    if not is_release:
        state_ui = StateUI.empty_repo
        return state_ui, finallist

    get_results_from_req(req, results)

    if results:
        if installedversion is None or not installedversion:
            installedversion = "0.0.0"

        # ABLER 릴리즈 버전 > 설치 버전
        if StrictVersion(results[0]["version"]) > StrictVersion(installedversion):
            state_ui = StateUI.update_abler
            finallist = results
            return state_ui, finallist

        # ABLER 릴리즈 버전 == 설치 버전
        else:
            state_ui = StateUI.execute

    else:
        state_ui = StateUI.execute
    return state_ui, finallist


def get_req_from_url(
    url: str, state_ui: Enum, dir_: str
) -> tuple[bool, str | None, Enum]:
    """깃헙 서버에서 url의 릴리즈 정보를 받아오는 함수"""

    # Do path settings save here, in case user has manually edited it
    config = configparser.ConfigParser()
    config.read(get_datadir() / "Blender/2.96/updater/config.ini")
    config.set("main", "path", dir_)
    with open(get_datadir() / "Blender/2.96/updater/config.ini", "w") as f:
        config.write(f)
    req_version = ""
    is_release = True
    try:
        req: str = requests.get(url).text
        req_elem: Element = fromstring(req)
        req_version = req_elem[0][1][1].text

    except Exception as e:
        logger.error(e)
        state_ui = StateUI.error
        return False, req_version, state_ui

    return is_release, req_version, state_ui


def get_results_from_req(req: str, results: list) -> None:
    """req에서 필요한 info를 results에 추가"""

    target = get_target_url(InstallType.abler)
    filename = target.split("/")[-1]
    version_tag = req.split("v")[-1]

    info = {
        "url": target,
        "os": "Windows",
        "filename": filename,
        "version": version_tag,
        "arch": "x64",
    }
    # TODO: print 제거해야함
    print(info)
    results.append(info)
