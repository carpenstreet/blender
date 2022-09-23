import pathlib
import sys
import psutil
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
    url = "https://cms.abler3d.biz/abler_update_info"

    # TODO: Pre-Release, Test Repository Release API 등에 대해서도 교체 필요
    if pre_rel:
        url = "https://api.github.com/repos/ACON3D/blender/releases"
    elif new_repo_rel:
        url = "https://api.github.com/repos/ACON3D/launcherTestRepo/releases/latest"
    elif new_repo_pre_rel:
        url = "https://api.github.com/repos/ACON3D/launcherTestRepo/releases"

    return url


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


def count_process(proc) -> int:
    """현재 실행되고 있는 프로세스의 개수를 세기"""

    proc_list = [p.name() for p in psutil.process_iter()]
    proc_count = sum(i.startswith(proc) for i in proc_list)
    return proc_count


class StateUI(Enum):
    check = auto()
    empty_repo = auto()
    update_launcher = auto()
    update_abler = auto()
    execute = auto()
    error = auto()
