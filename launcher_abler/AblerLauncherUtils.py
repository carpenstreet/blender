import pathlib
import sys
from enum import Enum, auto


# 테스트용 argument 추가
if len(sys.argv) > 1:
    pre_rel = sys.argv[1] == "--pre-release"
    new_rel = sys.argv[1] == "--new-repo-release"
    new_pre_rel = sys.argv[1] == "--new-repo-pre-release"

    print("\n-> AblerLauncherUtils.py")
    print(f"--pre-release          : {'O' if pre_rel else 'X'}")
    print(f"--new-repo-release     : {'O' if new_rel else 'X'}")
    print(f"--new-repo-pre-release : {'O' if new_pre_rel else 'X'}")
    print("\n")


def set_url() -> str:
    """GitHub Repo의 URL 세팅"""
    url = "https://api.github.com/repos/ACON3D/blender/releases/latest"

    if pre_rel:
        url = "https://api.github.com/repos/ACON3D/blender/releases"
    elif new_rel:
        url = "https://api.github.com/repos/ACON3D/launcherTestRepo/releases/latest"
    elif new_pre_rel:
        # 새 repo가 완전히 비어있을 때는 req에 정보가 없기 때문에 url 정보를 받을 수 없음
        # 따라서 pre-release 생성했을 때만 테스트
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
    no_release = auto()
    update_launcher = auto()
    update_abler = auto()
    execute = auto()
    error = auto()
