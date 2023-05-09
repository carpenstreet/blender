from __future__ import annotations

import pathlib
import sys
import psutil
import requests
from enum import Enum, auto

# TODO: 필요시에 Dev 환경에서 테스트하기
# https://acontainer.slack.com/archives/C02K1NPTV42/p1683614079788509
"""
dev = None

if len(sys.argv) > 1:
    dev = sys.argv[1] == "--dev"
"""


def set_url() -> str:
    """ABLER 최신 버전 확인을 위한 URL 세팅"""

    # ABLER의 최신 버전에 대한 XML 확인
    """
    if dev:
        url = "https://download.dev.abler.world/windows/info/latest.xml"
    """
    url = "https://download.abler.world/windows/info/latest.xml"

    return url


def get_target_url(install_type: Enum) -> str | None:
    if install_type == InstallType.launcher:
        """
        if dev:
            return "https://download.dev.abler.world/windows/launcher/latest.zip"
        """
        return "https://download.abler.world/windows/launcher/latest.zip"
    elif install_type == InstallType.abler:
        """
        if dev:
            return "https://download.dev.abler.world/windows/release/latest.zip"
        """
        return "https://download.abler.world/windows/release/latest.zip"
    else:
        return None


def get_datadir() -> pathlib.Path:
    """
    Returns a parent directory path
    where persistent application data can be stored.

    windows: C:/Users/<USER>/AppData/Roaming
    """
    home = pathlib.Path.home()
    return home / "AppData/Roaming/Blender Foundation"


def hbytes(num) -> str:
    """Translate to human-readable file size."""
    for x in [" bytes", " KB", " MB", " GB"]:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, " TB")


def process_count(proc) -> int:
    """현재 실행되고 있는 프로세스의 개수를 세기"""

    proc_list = [p.name() for p in psutil.process_iter()]
    return sum(i.startswith(proc) for i in proc_list)


def get_network_connection() -> bool:
    """네트워크 연결 상태를 bool 타입으로 return"""

    try:
        request = requests.get(set_url(), timeout=5)
        return True
    except (requests.ConnectionError, requests.ConnectTimeout) as exception:
        return False


class StateUI(Enum):
    """UI 상태를 나타내는 Enum"""

    none = auto()
    check = auto()
    empty_repo = auto()
    update_launcher = auto()
    update_abler = auto()
    execute = auto()
    error = auto()


class InstallType(Enum):
    """설치 타입을 나타내는 Enum"""

    launcher = auto()
    abler = auto()
