import pathlib
import sys
from enum import Enum, auto


# 테스트용 argument 추가
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
    url = "https://api.github.com/repos/ACON3D/blender/releases/latest"

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


class StateUI(Enum):
    check = auto()
    empty_repo = auto()
    update_launcher = auto()
    update_abler = auto()
    execute = auto()
    error = auto()
