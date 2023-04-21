from __future__ import annotations

import pathlib
import sys
import psutil
import requests
from enum import Enum, auto

# 테스트용 argument 추가
pre_rel = None
new_repo_rel = None
new_repo_pre_rel = None

if len(sys.argv) > 1:
    pre_rel = sys.argv[1] == "--pre-release"
    new_repo_rel = sys.argv[1] == "--new-repo-release"
    new_repo_pre_rel = sys.argv[1] == "--new-repo-pre-release"

    print("\n> release test argv 확인")
    print(f"> --pre-release          : {'O' if pre_rel else 'X'}")
    print(f"> --new-repo-release     : {'O' if new_repo_rel else 'X'}")
    print(f"> --new-repo-pre-release : {'O' if new_repo_pre_rel else 'X'}")
    print("\n")


def set_url() -> str:
    """GitHub Repo의 URL 세팅"""

    # GitHub API에는 접근 횟수 60회가 있어, 캐시를 받아오는 URL로 대체
    # url = "https://api.github.com/repos/ACON3D/blender/releases/latest"
    url = "https://download.abler.world/windows/latest.zip"  # 이거 사실 xml임

    # TODO: Pre-Release, Test Repository Release API 등에 대해서도 교체 필요
    if pre_rel:
        url = "https://download.abler.world/windows/latest.zip123"
    elif new_repo_rel:
        url = "https://download.abler.world/windows/latest.zip33"
    elif new_repo_pre_rel:
        url = "https://download.abler.world/windows/latest.zip333"

    return url


def get_target_url(install_type: Enum) -> str | None:
    if install_type == InstallType.launcher:
        # TODO: 진짜 정해지는 URL로 교체
        return "https://github.com/carpenstreet/blender/releases/download/ABLER%2Fv0.3.3/ABLER_Launcher_Windows_v0.0.15.zip"
    elif install_type == InstallType.abler:
        # TODO: 진짜 정해지는 URL로 교체
        return "https://github.com/carpenstreet/blender/releases/download/ABLER%2Fv0.3.3/ABLER_Release_Windows_v0.3.3.zip"
    else:
        return None


def get_datadir() -> pathlib.Path:
    """
    Returns a parent directory path
    where persistent application data can be stored.

    linux: ~/.local/share
    macOS: ~/Library/Application Support
    windows: C:/Users/<USER>/AppData/Roaming
    """

    home = pathlib.Path.home()

    if sys.platform == "win32":
        return home / "AppData/Roaming/Blender Foundation"
    elif sys.platform == "linux":
        return home / ".local/share"
    elif sys.platform == "darwin":
        return home / "Library/Application Support"


def hbytes(num) -> str:
    """Translate to human readable file size."""
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
