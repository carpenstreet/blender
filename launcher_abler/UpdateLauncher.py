import privilege_helper
import pathlib
from PySide2 import QtWidgets, QtCore, QtGui
import qdarkstyle
import mainwindow
import requests
import configparser
import logging
import os
import os.path
import platform
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
import time
from distutils.dir_util import copy_tree
from distutils.version import StrictVersion
from typing import Optional

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


def hbytes(num) -> str:
    """Translate to human readable file size."""
    for x in [" bytes", " KB", " MB", " GB"]:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, " TB")


appversion = "1.9.8"
dir_ = ""
if sys.platform == "darwin":
    dir_ = "/Applications"
elif sys.platform == "win32":
    dir_ = "C:/Program Files (x86)/ABLER"
launcherdir_ = get_datadir() / "Blender/2.96/updater"
config = configparser.ConfigParser()
btn = {}
lastversion = ""
installedversion = ""
launcher_installed = ""
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


def check_launcher(launcherdir_,launcher_installed) -> bool:
    # global dir_
    # global launcherdir_
    # global launcher_installed
    # global lastversion
    # global installedversion
    print("AAA")
    launcher_need_install = False
    results = []
    state_ui = None
    url = "https://api.github.com/repos/acon3d/blender/releases/latest"
    if test_arg:
        url = "https://api.github.com/repos/acon3d/blender/releases"
    # TODO: 새 arg 받아서 테스트 레포 url 업데이트

    is_release, req, state_ui = get_req_from_url(launcherdir_, url, state_ui)
    if state_ui:
        return state_ui, False

    if not is_release:
        state_ui = "no release"
        return state_ui, False

    else:
        get_results_from_req(launcherdir_, req, results)

        if finallist := results:
            if launcher_installed is None or launcher_installed == "":
                launcher_installed = "0.0.0"

            # Launcher 릴리즈 버전 > 설치 버전
            # -> launcher_need_install = True가 반환
            if StrictVersion(finallist[0]["version"]) > StrictVersion(launcher_installed):
                setup_update_launcher_ui(finallist)
                launcher_need_install = True

        # Launcher 릴리즈 버전 == 설치 버전
        # -> launcher_need_install = False가 반환
        return launcher_need_install


def get_req_from_url(dir_name, url, state_ui):
    # 깃헙 서버에서 url의 릴리즈 정보를 받아오는 함수
    global dir_
    global launcherdir_
    global launcher_installed

    # Do path settings save here, in case user has manually edited it
    global config
    config.read(get_datadir() / "Blender/2.96/updater/config.ini")

    if dir_name == launcherdir_:
        launcher_installed = config.get("main", "launcher")

    config.set("main", "path", dir_)
    with open(get_datadir() / "Blender/2.96/updater/config.ini", "w") as f:
        config.write(f)
    f.close()

    try:
        req = requests.get(url).json()
    except Exception as e:
        # self.statusBar().showMessage(
        #     "Error reaching server - check your internet connection"
        # )
        # logger.error(e)
        # self.frm_start.show()
        logger.error(e)
        state_ui = "error"

    if test_arg:
        req = req[0]

    is_release = True
    try:
        is_release = req["message"] != "Not Found"
    except Exception as e:
        logger.debug("Release found")

    return is_release, req, state_ui

def get_results_from_req(dir_name, req, results):
    # req에서 필요한 info를 results에 추가
    for asset in req["assets"]:
        target = asset["browser_download_url"]
        filename = target.split("/")[-1]

        if dir_name == dir_:
            target_type = "Release"
            version_tag = req["name"][1:]

        elif dir_name == launcherdir_:
            target_type = "Launcher"
            version_tag = filename.split("_")[-1][1:-4]

        if sys.platform == "win32":
            if (
                "Windows" in target
                and "zip" in target
                and target_type in target
            ):
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

def setup_update_launcher_ui(self, finallist):
    self.btn_update_launcher.show()
    self.btn_update.hide()
    self.btn_execute.hide()
    self.btn_update_launcher.clicked.connect(
                lambda throwaway=0, entry=finallist[0]: download(entry, dir_name=launcherdir_)
            )

def download(self, entry, dir_name):
    """Download routines."""
    temp_name = "./blendertemp" if dir_name == dir_ else "./launchertemp"

    url = entry["url"]
    version = entry["version"]
    variation = entry["arch"]

    if os.path.isdir(temp_name):
        shutil.rmtree(temp_name)

    os.makedirs(temp_name)

    global config
    config.read(get_datadir() / "Blender/2.96/updater/config.ini")

    if dir_name == dir_:
        config.set("main", "path", dir_)
        config.set("main", "flavor", variation)
        config.set("main", "installed", version)
    else:
        config.set("main", "launcher", version)
        logger.info(f"1 {config.get('main', 'installed')}")

    with open(get_datadir() / "Blender/2.96/updater/config.ini", "w") as f:
        config.write(f)
    f.close()

    ##########################
    # Do the actual download #
    ##########################

    if dir_name == dir_:
        for i in btn:
            btn[i].hide()
    logger.info(f"Starting download thread for {url}{version}")

    self.setup_download_ui(entry, dir_name)

    self.exec_dir_name = os.path.join(dir_name, "")
    filename = temp_name + entry["filename"]

    thread = WorkerThread(url, filename, self.exec_dir_name, temp_name)
    thread.update.connect(updatepb)
    thread.finishedDL.connect(extraction)
    thread.finishedEX.connect(finalcopy)
    thread.finishedCP.connect(cleanup)
    thread.finishedCL.connect(done_launcher)

    thread.start()

def updatepb(self, percent):
    self.progressBar.setValue(percent)

def extraction(self):
    # 다운로드 받은 파일 압축 해제
    logger.info("Extracting to temp directory")
    self.lbl_task.setText("Extracting...")
    self.btn_Quit.setEnabled(False)
    nowpixmap = QtGui.QPixmap(":/newPrefix/images/Actions-arrow-right-icon.png")
    donepixmap = QtGui.QPixmap(":/newPrefix/images/Check-icon.png")
    self.lbl_download_pic.setPixmap(donepixmap)
    self.lbl_extract_pic.setPixmap(nowpixmap)
    self.lbl_extraction.setText("<b>Extraction</b>")
    self.statusbar.showMessage("Extracting to temporary folder, please wait...")
    self.progressBar.setMaximum(0)
    self.progressBar.setMinimum(0)
    self.progressBar.setValue(-1)

def finalcopy(self):
    # 설치 파일 복사
    exec_dir_name = self.exec_dir_name
    logger.info(f"Copying to {exec_dir_name}")
    nowpixmap = QtGui.QPixmap(":/newPrefix/images/Actions-arrow-right-icon.png")
    donepixmap = QtGui.QPixmap(":/newPrefix/images/Check-icon.png")
    self.lbl_extract_pic.setPixmap(donepixmap)
    self.lbl_copy_pic.setPixmap(nowpixmap)
    self.lbl_copying.setText("<b>Copying</b>")
    self.lbl_task.setText("Copying files...")
    self.statusbar.showMessage(f"Copying files to {exec_dir_name}, please wait... ")

def cleanup(self):
    # 설치 파일 임시 폴더 제거
    logger.info("Cleaning up temp files")
    nowpixmap = QtGui.QPixmap(":/newPrefix/images/Actions-arrow-right-icon.png")
    donepixmap = QtGui.QPixmap(":/newPrefix/images/Check-icon.png")
    self.lbl_copy_pic.setPixmap(donepixmap)
    self.lbl_clean_pic.setPixmap(nowpixmap)
    self.lbl_cleanup.setText("<b>Cleaning up</b>")
    self.lbl_task.setText("Cleaning up...")
    self.statusbar.showMessage("Cleaning temporary files")

def done_launcher(self):
    # 최신 릴리즈의 launcher를 다운받고 나서는 launcher를 재실행
    self.setup_download_done_ui()
    QtWidgets.QMessageBox.information(
        self,
        "Launcher updated",
        "ABLER launcher has been updated. Please re-run the launcher.",
    )
    try:
        if test_arg:
            _ = subprocess.Popen(
                [f"{get_datadir()}Blender/2.96/updater/AblerLauncher.exe", "--test"]
            )

        else:
            _ = subprocess.Popen(
                get_datadir() / "Blender/2.96/updater/AblerLauncher.exe"
            )
        QtCore.QCoreApplication.instance().quit()
        # TODO: Launcher를 다시 실행할 수 있게 해주면?
    except Exception as e:
        logger.error(e)
        try:
            if test_arg:
                _ = subprocess.Popen(
                    [
                        get_datadir() / "Blender/2.93/updater/AblerLauncher.exe",
                        "--test",
                    ]
                )

            else:
                _ = subprocess.Popen(
                    get_datadir() / "Blender/2.93/updater/AblerLauncher.exe"
                )
            QtCore.QCoreApplication.instance().quit()
        except Exception as ee:
            logger.error(ee)
            QtCore.QCoreApplication.instance().quit()
