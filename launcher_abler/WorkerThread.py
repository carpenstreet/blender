from PySide2 import QtWidgets, QtCore, QtGui
import shutil
import urllib.parse
import urllib.request
import os
import os.path
import sys
import time
from distutils.dir_util import copy_tree
import logging
import pathlib

if sys.platform == "win32":
    from win32com.client import Dispatch

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

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

LOG_FORMAT = (
    "%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s"
)
test_arg = len(sys.argv) > 1 and sys.argv[1] == "--test"
if not os.path.isdir(get_datadir() / "Blender/2.96"):
    os.mkdir(get_datadir() / "Blender/2.96")
if not os.path.isdir(get_datadir() / "Blender/2.96/updater"):
    os.mkdir(get_datadir() / "Blender/2.96/updater")
logging.basicConfig(
    filename=get_datadir() / "Blender/2.96/updater/AblerLauncher.log",
    format=LOG_FORMAT,
    level=logging.DEBUG,
    filemode="w",
)

logger = logging.getLogger()

class WorkerThread(QtCore.QThread):
    """Does all the actual work in the background, informs GUI about status"""

    update = QtCore.Signal(int)
    finishedDL = QtCore.Signal()
    finishedEX = QtCore.Signal()
    finishedCP = QtCore.Signal()
    finishedCL = QtCore.Signal()

    def __init__(self, url, file, path, temp_path):
        super(WorkerThread, self).__init__(parent=app)
        self.filename = file
        self.url = url
        self.path = path
        self.temp_path = temp_path

    def progress(self, count, blockSize, totalSize):
        """Updates progress bar"""
        percent = int(count * blockSize * 100 / totalSize)
        self.update.emit(percent)

    def run(self):
        try:
            urllib.request.urlretrieve(
                self.url, self.filename, reporthook=self.progress
            )
            self.finishedDL.emit()
            shutil.unpack_archive(self.filename, self.temp_path)
            os.remove(self.filename)
            self.finishedEX.emit()
            source = next(os.walk(self.temp_path))
            if "updater" in self.path and sys.platform == "win32":
                if os.path.isfile(f"{self.path}/AblerLauncher.exe"):
                    os.rename(
                        f"{self.path}/AblerLauncher.exe",
                        f"{self.path}/AblerLauncher.bak",
                    )
                time.sleep(1)
                shutil.copyfile(
                    f"{self.temp_path}/AblerLauncher.exe",
                    f"{self.path}/AblerLauncher.exe",
                )

                # sym_path = (
                #     get_datadir()
                #     / "/Microsoft/Windows/Start Menu/Programs/ABLER/Launch ABLER.lnk"
                # )
                # if os.path.isfile(sym_path):
                #     os.remove(sym_path)
                # shell = Dispatch("WScript.Shell")
                # shortcut = shell.CreateShortCut(sym_path)
                # shortcut.Targetpath = self.path / "/AblerLauncher.exe"
                # shortcut.save()
            else:
                # TODO: 추후 macOS에서도 위의 작업과 동일한 작업을 해줘야함
                try:
                    # TODO: copy_tree가 현재 작동하지 않고 바로 except로 넘어감
                    copy_tree(source[0], self.path)
                except Exception as e:
                    logger.error(e)
            self.finishedCP.emit()
            shutil.rmtree(self.temp_path)
            self.finishedCL.emit()
        except Exception as e:
            logger.error(e)