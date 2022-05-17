import pathlib
import sys
from enum import Enum, auto


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
