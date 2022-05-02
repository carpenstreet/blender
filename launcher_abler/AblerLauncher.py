"""
    Copyright 2016-2019 Tobias Kummer/Overmind Studios.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import privilege_helper
from PySide2 import QtWidgets, QtCore, QtGui
import qdarkstyle
import mainwindow
import configparser
import logging
import os
import os.path
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
import time
from distutils.dir_util import copy_tree
from AblerLauncherUtils import get_datadir, hbytes, StateUI

if sys.platform == "win32":
    from win32com.client import Dispatch

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

app = QtWidgets.QApplication(sys.argv)

app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

appversion = "1.9.8"
dir_ = ""
launcherdir_ = get_datadir() / "Blender/2.96/updater"

if sys.platform == "darwin":
    dir_ = "/Applications"
elif sys.platform == "win32":
    dir_ = "C:/Program Files (x86)/ABLER"

btn = {}



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


class BlenderUpdater(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self, parent=None):
        logger.info(f"Running version {appversion}")
        logger.debug("Constructing UI")
        super(BlenderUpdater, self).__init__(parent)
        self.setupUi(self)
        self.btn_oneclick.hide()
        self.lbl_quick.hide()
        self.lbl_caution.hide()
        self.btn_newVersion.hide()
        self.btn_update.hide()
        self.btn_execute.hide()
        self.lbl_caution.setStyleSheet("background: rgb(255, 155, 8);\n" "color: white")
        lastversion = ""
        installedversion = ""
        self.launcher_installed = ""
        global dir_
        config = configparser.ConfigParser()

        if os.path.isfile(get_datadir() / "Blender/2.96/updater/AblerLauncher.bak"):
            os.remove(get_datadir() / "Blender/2.96/updater/AblerLauncher.bak")
        if os.path.isfile(get_datadir() / "Blender/2.96/config/startup.blend"):
            os.remove(get_datadir() / "Blender/2.96/config/startup.blend")
        if os.path.isfile(get_datadir() / "Blender/2.96/config/userpref.blend"):
            os.remove(get_datadir() / "Blender/2.96/config/userpref.blend")
        if os.path.isfile(get_datadir() / "Blender/2.96/updater/config.ini"):
            config_exist = True
            logger.info("Reading existing configuration file")
            config.read(get_datadir() / "Blender/2.96/updater/config.ini")
            lastcheck = config.get("main", "lastcheck")
            lastversion = config.get("main", "lastdl")
            installedversion = config.get("main", "installed")
            self.launcher_installed = config.get("main", "launcher")
            flavor = config.get("main", "flavor")
            if lastversion != "":
                self.btn_oneclick.setText(f"{flavor} | {lastversion}")
        else:
            logger.debug("No previous config found")
            self.btn_oneclick.hide()
            config_exist = False
            config.read(get_datadir() / "Blender/2.96/updater/config.ini")
            config.add_section("main")
            config.set("main", "path", "")
            lastcheck = "Never"
            config.set("main", "lastcheck", lastcheck)
            config.set("main", "lastdl", "")
            config.set("main", "installed", "")
            config.set("main", "launcher", "")
            config.set("main", "flavor", "")
            with open(get_datadir() / "Blender/2.96/updater/config.ini", "w") as f:
                config.write(f)
        self.btn_cancel.hide()
        self.frm_progress.hide()
        self.btngrp_filter.hide()
        self.btn_acon.setFocus()
        self.lbl_available.hide()
        self.progressBar.setValue(0)
        self.progressBar.hide()
        self.lbl_task.hide()
        self.statusbar.showMessage(f"Ready - Last check: {lastcheck}")
        self.btn_Quit.clicked.connect(QtCore.QCoreApplication.instance().quit)
        self.btn_about.clicked.connect(self.about)
        self.btn_acon.clicked.connect(self.open_acon3d)
        try:
            import UpdateAbler, UpdateLauncher

            state_ui, finallist = UpdateLauncher.check_launcher(
                dir_, self.launcher_installed
            )
            self.launcher_state_parse(state_ui, finallist)
            if not state_ui:
                state_ui, finallist = UpdateAbler.check_abler(dir_, installedversion)
                self.abler_state_parse(state_ui, finallist)
        except Exception as e:
            logger.error(e)

    def launcher_state_parse(self, state_ui, finallist):
        if state_ui == StateUI.error:
            self.statusBar().showMessage(
                "Error reaching server - check your internet connection"
            )
            self.frm_start.show()

        elif state_ui == StateUI.no_release:
            # TODO: 테스트 서버에서 릴리즈가 없이 테스트할 때 self.setup_execute_ui()에서
            #       click 빼야하는지, 있어도 되는지 확인하기
            self.frm_start.show()
            self.btn_execute.show()
            self.btn_update_launcher.hide()
            self.btn_update.hide()
            # self.setup_execute_ui()

        elif state_ui == StateUI.update_launcher:
            self.setup_update_launcher_ui(finallist)
        else:
            return

    def abler_state_parse(self, state_ui, finallist):
        if state_ui == StateUI.error:
            self.statusBar().showMessage(
                "Error reaching server - check your internet connection"
            )
            self.frm_start.show()

        elif state_ui == StateUI.no_release:
            self.frm_start.show()
            self.setup_execute_ui()

        elif state_ui == StateUI.update_abler:
            self.setup_update_abler_ui(finallist)

        elif state_ui == StateUI.execute:
            self.setup_execute_ui()

        else:
            return

    def setup_update_launcher_ui(self, finallist):
        self.btn_update_launcher.show()
        self.btn_update.hide()
        self.btn_execute.hide()
        self.btn_update_launcher.clicked.connect(
            lambda throwaway=0, entry=finallist[0]: self.download(
                entry, dir_name=launcherdir_
            )
        )

    def setup_update_abler_ui(self, finallist):
        # ABLER를 업데이트
        # TODO: 버튼 한번 클릭되면 비활성화 기능 넣기
        self.btn_update_launcher.hide()
        self.btn_update.show()
        self.btn_execute.hide()
        self.btn_update.clicked.connect(
            lambda throwaway=0, entry=finallist[0]: self.download(entry, dir_name=dir_)
        )

    def setup_execute_ui(self):
        self.btn_update_launcher.hide()
        self.btn_update.hide()
        self.btn_execute.show()

        if sys.platform == "win32":
            self.btn_execute.clicked.connect(self.exec_windows)
        elif sys.platform == "darwin":
            self.btn_execute.clicked.connect(self.exec_osx)
        elif sys.platform == "linux":
            self.btn_execute.clicked.connect(self.exec_linux)

    def download(self, entry, dir_name):
        """Download routines."""
        temp_name = "./blendertemp" if dir_name == dir_ else "./launchertemp"

        url = entry["url"]
        version = entry["version"]
        variation = entry["arch"]

        if os.path.isdir(temp_name):
            shutil.rmtree(temp_name)

        os.makedirs(temp_name)

        config = configparser.ConfigParser()
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
                print(i)
                btn[i].hide()
        logger.info(f"Starting download thread for {url}{version}")

        self.setup_download_ui(entry, dir_name)

        self.exec_dir_name = os.path.join(dir_name, "")
        filename = temp_name + entry["filename"]

        thread = WorkerThread(url, filename, self.exec_dir_name, temp_name)
        thread.update.connect(self.updatepb)
        thread.finishedDL.connect(self.extraction)
        thread.finishedEX.connect(self.finalcopy)
        thread.finishedCP.connect(self.cleanup)

        if dir_name == dir_:
            thread.finishedCL.connect(self.done_abler)
        else:
            thread.finishedCL.connect(self.done_launcher)

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

    def done_abler(self):
        # 최신 릴리즈의 ABLER를 다운받고 나서는 self.setup_execute_ui() 실행
        self.setup_download_done_ui()
        self.setup_execute_ui()

    def setup_download_ui(self, entry, dir_name):
        url = entry["url"]
        version = entry["version"]
        # TODO: exec_name 있으면 ui가 깨져서 뺄지 논의
        exec_name = "ABLER" if dir_name == dir_ else "Launcher"

        file = urllib.request.urlopen(url)
        totalsize = file.info()["Content-Length"]
        size_readable = hbytes(float(totalsize))

        self.lbl_available.hide()
        self.lbl_caution.hide()
        self.progressBar.show()
        self.btngrp_filter.hide()
        self.lbl_task.setText("Downloading")
        self.lbl_task.show()
        self.frm_progress.show()
        nowpixmap = QtGui.QPixmap(":/newPrefix/images/Actions-arrow-right-icon.png")
        self.lbl_download_pic.setPixmap(nowpixmap)
        self.lbl_downloading.setText(f"<b>Downloading {exec_name} {version}</b>")
        self.progressBar.setValue(0)
        self.statusbar.showMessage(f"Downloading {size_readable}")

    def setup_download_done_ui(self):
        logger.info("Finished")
        donepixmap = QtGui.QPixmap(":/newPrefix/images/Check-icon.png")
        self.lbl_clean_pic.setPixmap(donepixmap)
        self.statusbar.showMessage("Ready")
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(100)
        self.lbl_task.setText("Finished")
        self.btn_Quit.setEnabled(True)

    def exec_windows(self):
        try:
            if privilege_helper.isUserAdmin():
                _ = privilege_helper.runas_shell_user(
                    os.path.join('"' + dir_ + "/blender.exe" + '"')
                )  # pid와 tid를 리턴함
            logger.info(f"Executing {dir_}blender.exe")
            QtCore.QCoreApplication.instance().quit()
        except Exception as e:
            logger.error(e)

    def exec_osx(self):
        try:
            if getattr(sys, "frozen", False):
                application_path = os.path.dirname(sys.executable)
            elif __file__:
                application_path = os.path.dirname(__file__)
            BlenderOSXPath = os.path.join(f"{application_path}/ABLER")
            os.system(f"chmod +x {BlenderOSXPath}")
            _ = subprocess.Popen(BlenderOSXPath)
            logger.info(f"Executing {BlenderOSXPath}")
            QtCore.QCoreApplication.instance().quit()
        except Exception as e:
            logger.error(e)

    def exec_linux(self):
        _ = subprocess.Popen(os.path.join(f"{dir_}/blender"))
        logger.info(f"Executing {dir_}blender")

    def open_acon3d(self):
        url = QtCore.QUrl("https://www.acon3d.com/")
        QtGui.QDesktopServices.openUrl(url)

    def about(self):
        aboutText = (
            '<html><head/><body><p>Utility to update ABLER to the latest version available at<br> \
        <a href="https://builder.blender.org/download/"><span style=" text-decoration: underline; color:#2980b9;">\
        https://builder.blender.org/download/</span></a></p><p><br/>Developed by Tobias Kummer for \
        <a href="http://www.overmind-studios.de"><span style="text-decoration:underline; color:#2980b9;"> \
        Overmind Studios</span></a></p><p>\
        Licensed under the <a href="https://www.gnu.org/licenses/gpl-3.0-standalone.html"><span style=" text-decoration:\
        underline; color:#2980b9;">GPL v3 license</span></a></p><p>Project home: \
        <a href="https://overmindstudios.github.io/BlenderUpdater/"><span style=" text-decoration:\
        underline; color:#2980b9;">https://overmindstudios.github.io/BlenderUpdater/</a></p> \
        <p style="text-align: center;"></p> \
        <p>Application based on the version: '
            + self.launcher_installed
            + "</p></body></html> "
        )
        QtWidgets.QMessageBox.about(self, "About", aboutText)


def macos_prework():
    if sys.platform != "darwin":
        return
    if len(sys.argv) > 1 and sys.argv[1].endswith(".blend"):
        try:
            if getattr(sys, "frozen", False):
                application_path = os.path.dirname(sys.executable)
            elif __file__:
                application_path = os.path.dirname(__file__)
            BlenderOSXPath = os.path.join(f"{application_path}/ABLER")
            os.system(f"chmod +x {BlenderOSXPath}")
            _ = subprocess.Popen([BlenderOSXPath, sys.argv[1]])
            logger.info(f"Executing {BlenderOSXPath}")
            sys.exit()
        except Exception as e:
            logger.error(e)


def main():
    macos_prework()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    window = BlenderUpdater()
    window.setWindowTitle("ABLER Launcher")
    window.statusbar.setSizeGripEnabled(False)
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
