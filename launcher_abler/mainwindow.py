# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import res_rc


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(700, 550)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(700, 550))
        MainWindow.setMaximumSize(QSize(700, 550))
        icon = QIcon()
        icon.addFile(":/newPrefix/images/abler.png", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet("")
        self.text_stylesheet = "font-size: 10pt;"
        self.download_stylesheet = "background: transparent;\nfont-size: 10pt;"
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.btn_Quit = QPushButton(self.centralwidget)
        self.btn_Quit.setObjectName("btn_Quit")
        self.btn_Quit.setGeometry(QRect(6, 481, 131, 35))
        self.btn_Quit.setFocusPolicy(Qt.StrongFocus)
        self.btn_Quit.setStyleSheet(self.text_stylesheet)
        icon1 = QIcon()
        icon1.addFile(
            ":/newPrefix/images/Application-exit-icon.png",
            QSize(),
            QIcon.Normal,
            QIcon.Off,
        )
        self.btn_Quit.setIcon(icon1)
        self.btn_acon = QPushButton(self.centralwidget)
        self.btn_acon.setObjectName("btn_acon")
        self.btn_acon.setGeometry(QRect(560, 481, 131, 35))
        self.btn_acon.setStyleSheet(self.text_stylesheet)
        icon2 = QIcon()
        icon2.addFile(
            ":/newPrefix/images/favicon.png", QSize(), QIcon.Normal, QIcon.Off
        )
        self.btn_acon.setIcon(icon2)
        self.btn_acon.setAutoDefault(False)
        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setEnabled(True)
        self.progressBar.setGeometry(QRect(140, 431, 551, 30))
        self.progressBar.setStyleSheet("")
        self.progressBar.setValue(24)
        self.progressBar.setTextVisible(True)
        self.progressBar.setInvertedAppearance(False)
        self.lbl_task = QLabel(self.centralwidget)
        self.lbl_task.setObjectName("lbl_task")
        self.lbl_task.setGeometry(QRect(10, 435, 121, 20))
        self.lbl_task.setStyleSheet("")
        self.lbl_available = QLabel(self.centralwidget)
        self.lbl_available.setObjectName("lbl_available")
        self.lbl_available.setGeometry(QRect(6, 25, 645, 20))
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lbl_available.setFont(font)
        self.lbl_available.setAlignment(Qt.AlignCenter)
        self.btn_about = QToolButton(self.centralwidget)
        self.btn_about.setObjectName("btn_about")
        self.btn_about.setGeometry(QRect(657, 10, 35, 35))
        icon3 = QIcon()
        icon3.addFile(
            ":/newPrefix/images/Information-icon.png", QSize(), QIcon.Normal, QIcon.Off
        )
        self.btn_about.setIcon(icon3)
        self.btn_about.setIconSize(QSize(24, 24))
        self.btn_about.setCheckable(False)
        self.btn_about.setChecked(False)
        self.main_rect = QRect(6, 50, 686, 361)
        self.frm_start = QFrame(self.centralwidget)
        self.frm_start.setObjectName("frm_start")
        self.frm_start.setGeometry(self.main_rect)
        self.frm_start.setFrameShape(QFrame.StyledPanel)
        self.frm_start.setFrameShadow(QFrame.Raised)
        self.frm_start.setStyleSheet(
            "background-image: url(':/newPrefix/images/abler_intro_2.png');\nbackground-repeat: no-repeat;\nbackground-position: center;"
        )
        self.btn_cancel = QPushButton(self.centralwidget)
        self.btn_cancel.setObjectName("btn_cancel")
        self.btn_cancel.setGeometry(QRect(110, 435, 24, 24))
        icon5 = QIcon()
        icon5.addFile(
            ":/newPrefix/images/Cancel-icon.png", QSize(), QIcon.Normal, QIcon.Off
        )
        self.btn_cancel.setIcon(icon5)
        self.frm_progress = QFrame(self.centralwidget)
        self.frm_progress.setObjectName("frm_progress")
        self.frm_progress.setGeometry(self.main_rect)
        self.frm_progress.setStyleSheet("")
        self.frm_progress.setFrameShape(QFrame.StyledPanel)
        self.frm_progress.setFrameShadow(QFrame.Raised)
        self.lbl_background_pic = QLabel(self.frm_progress)
        self.lbl_background_pic.setObjectName("lbl_background_pic")
        self.lbl_background_pic.setGeometry(QRect(0, 0, 686, 361))
        self.lbl_background_pic.setAlignment(Qt.AlignCenter)
        background_pixmap = QPixmap(":/newPrefix/images/abler_intro_1.png")
        self.lbl_background_pic.setPixmap(background_pixmap)
        self.lbl_download_pic = QLabel(self.frm_progress)
        self.lbl_download_pic.setObjectName("lbl_download_pic")
        self.lbl_download_pic.setGeometry(QRect(40, 50, 24, 24))
        self.lbl_download_pic.setStyleSheet(self.download_stylesheet)
        self.lbl_extract_pic = QLabel(self.frm_progress)
        self.lbl_extract_pic.setObjectName("lbl_extract_pic")
        self.lbl_extract_pic.setGeometry(QRect(40, 80, 24, 24))
        self.lbl_extract_pic.setStyleSheet(self.download_stylesheet)
        self.lbl_copy_pic = QLabel(self.frm_progress)
        self.lbl_copy_pic.setObjectName("lbl_copy_pic")
        self.lbl_copy_pic.setGeometry(QRect(40, 110, 24, 24))
        self.lbl_copy_pic.setStyleSheet(self.download_stylesheet)
        self.lbl_clean_pic = QLabel(self.frm_progress)
        self.lbl_clean_pic.setObjectName("lbl_clean_pic")
        self.lbl_clean_pic.setGeometry(QRect(40, 140, 24, 24))
        self.lbl_clean_pic.setStyleSheet(self.download_stylesheet)
        self.lbl_downloading = QLabel(self.frm_progress)
        self.lbl_downloading.setObjectName("lbl_downloading")
        self.lbl_downloading.setGeometry(QRect(70, 50, 171, 24))
        self.lbl_downloading.setStyleSheet(self.download_stylesheet)
        self.lbl_extraction = QLabel(self.frm_progress)
        self.lbl_extraction.setObjectName("lbl_extraction")
        self.lbl_extraction.setGeometry(QRect(70, 80, 171, 24))
        self.lbl_extraction.setStyleSheet(self.download_stylesheet)
        self.lbl_copying = QLabel(self.frm_progress)
        self.lbl_copying.setObjectName("lbl_copying")
        self.lbl_copying.setGeometry(QRect(70, 110, 171, 24))
        self.lbl_copying.setStyleSheet(self.download_stylesheet)
        self.lbl_cleanup = QLabel(self.frm_progress)
        self.lbl_cleanup.setObjectName("lbl_cleanup")
        self.lbl_cleanup.setGeometry(QRect(70, 140, 171, 24))
        self.lbl_cleanup.setStyleSheet(self.download_stylesheet)
        self.btngrp_filter = QGroupBox(self.centralwidget)
        self.btngrp_filter.setObjectName("btngrp_filter")
        self.btngrp_filter.setGeometry(QRect(200, 455, 307, 61))
        self.btn_osx = QToolButton(self.btngrp_filter)
        self.btn_osx.setObjectName("btn_osx")
        self.btn_osx.setGeometry(QRect(227, 30, 75, 23))
        self.btn_osx.setStyleSheet("")
        icon6 = QIcon()
        icon6.addFile(
            ":/newPrefix/images/Apple-icon.png", QSize(), QIcon.Normal, QIcon.Off
        )
        self.btn_osx.setIcon(icon6)
        self.btn_osx.setCheckable(True)
        self.btn_osx.setAutoExclusive(True)
        self.btn_windows = QToolButton(self.btngrp_filter)
        self.btn_windows.setObjectName("btn_windows")
        self.btn_windows.setGeometry(QRect(79, 30, 75, 23))
        self.btn_windows.setAutoFillBackground(False)
        icon7 = QIcon()
        icon7.addFile(
            ":/newPrefix/images/Windows-icon.png", QSize(), QIcon.Normal, QIcon.Off
        )
        self.btn_windows.setIcon(icon7)
        self.btn_windows.setCheckable(True)
        self.btn_windows.setAutoExclusive(True)
        self.btn_allos = QToolButton(self.btngrp_filter)
        self.btn_allos.setObjectName("btn_allos")
        self.btn_allos.setGeometry(QRect(5, 30, 75, 23))
        self.btn_allos.setStyleSheet("")
        self.btn_allos.setCheckable(True)
        self.btn_allos.setChecked(True)
        self.btn_allos.setAutoExclusive(True)
        self.btn_linux = QToolButton(self.btngrp_filter)
        self.btn_linux.setObjectName("btn_linux")
        self.btn_linux.setGeometry(QRect(153, 30, 75, 23))
        icon8 = QIcon()
        icon8.addFile(
            ":/newPrefix/images/Linux-icon.png", QSize(), QIcon.Normal, QIcon.Off
        )
        self.btn_linux.setIcon(icon8)
        self.btn_linux.setCheckable(True)
        self.btn_linux.setAutoExclusive(True)
        self.btn_oneclick = QPushButton(self.centralwidget)
        self.btn_oneclick.setObjectName("btn_oneclick")
        self.btn_oneclick.setGeometry(QRect(260, 480, 191, 35))
        self.btn_oneclick.setStyleSheet("")
        icon9 = QIcon()
        icon9.addFile(
            ":/newPrefix/images/Actions-quickopen-icon.png",
            QSize(),
            QIcon.Normal,
            QIcon.Off,
        )
        self.btn_oneclick.setIcon(icon9)
        self.lbl_quick = QLabel(self.centralwidget)
        self.lbl_quick.setObjectName("lbl_quick")
        self.lbl_quick.setGeometry(QRect(290, 460, 131, 20))
        self.lbl_quick.setAlignment(Qt.AlignCenter)
        self.lbl_caution = QLabel(self.centralwidget)
        self.lbl_caution.setObjectName("lbl_caution")
        self.lbl_caution.setGeometry(QRect(6, 3, 645, 20))
        self.lbl_caution.setFont(font)
        self.lbl_caution.setAutoFillBackground(True)
        self.lbl_caution.setAlignment(Qt.AlignCenter)
        self.btn_newVersion = QPushButton(self.centralwidget)
        self.btn_newVersion.setObjectName("btn_newVersion")
        self.btn_newVersion.setGeometry(QRect(500, 10, 151, 35))
        icon10 = QIcon()
        icon10.addFile(
            ":/newPrefix/images/software-update-icon.png",
            QSize(),
            QIcon.Normal,
            QIcon.Off,
        )
        self.btn_newVersion.setIcon(icon10)
        self.btn_newVersion.setIconSize(QSize(24, 24))
        self.btn_newVersion.setCheckable(False)
        self.btn_newVersion.setChecked(False)
        self.btn_execute = QPushButton(self.centralwidget)
        self.btn_execute.setObjectName("btn_execute")
        self.btn_execute.setGeometry(QRect(260, 480, 191, 40))
        self.btn_execute.setStyleSheet(self.text_stylesheet)
        self.btn_update = QPushButton(self.centralwidget)
        self.btn_update.setObjectName("btn_update")
        self.btn_update.setGeometry(QRect(260, 480, 191, 40))
        self.btn_update.setStyleSheet(self.text_stylesheet)
        self.btn_update_launcher = QPushButton(self.centralwidget)
        self.btn_update_launcher.setObjectName("btn_update_launcher")
        self.btn_update_launcher.setGeometry(QRect(260, 480, 191, 40))
        self.btn_update_launcher.setStyleSheet(self.text_stylesheet)
        icon11 = QIcon()
        icon11.addFile(":/newPrefix/images/abler.png", QSize(), QIcon.Normal, QIcon.Off)
        self.btn_execute.setIcon(icon11)
        self.btn_update.setIcon(icon11)
        self.btn_update_launcher.setIcon(icon11)
        MainWindow.setCentralWidget(self.centralwidget)
        self.btngrp_filter.raise_()
        self.frm_start.raise_()
        self.btn_Quit.raise_()
        self.btn_acon.raise_()
        self.progressBar.raise_()
        self.lbl_task.raise_()
        self.lbl_available.raise_()
        self.btn_about.raise_()
        self.btn_cancel.raise_()
        self.frm_progress.raise_()
        self.btn_oneclick.raise_()
        self.lbl_quick.raise_()
        self.lbl_caution.raise_()
        self.btn_newVersion.raise_()
        self.btn_execute.raise_()
        self.btn_update.raise_()
        self.btn_update_launcher.raise_()

        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.btn_acon.setDefault(False)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "ABLER Launcher", None)
        )
        self.btn_Quit.setText(QCoreApplication.translate("MainWindow", "Quit", None))
        self.btn_acon.setText(
            QCoreApplication.translate("MainWindow", "Visit ACON3D", None)
        )
        self.lbl_task.setText(
            QCoreApplication.translate("MainWindow", "TextLabel", None)
        )
        self.lbl_available.setText(
            QCoreApplication.translate(
                "MainWindow", "Available versions from buildbot:", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.btn_about.setToolTip(
            QCoreApplication.translate("MainWindow", "Settings", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.btn_about.setText("")
        self.btn_cancel.setText("")
        self.lbl_download_pic.setText("")
        self.lbl_background_pic.setText("")
        self.lbl_extract_pic.setText("")
        self.lbl_copy_pic.setText("")
        self.lbl_downloading.setText(
            QCoreApplication.translate("MainWindow", "Downloading", None)
        )
        self.lbl_extraction.setText(
            QCoreApplication.translate("MainWindow", "Extraction", None)
        )
        self.lbl_copying.setText(
            QCoreApplication.translate("MainWindow", "Copying files", None)
        )
        self.lbl_clean_pic.setText("")
        self.lbl_cleanup.setText(
            QCoreApplication.translate("MainWindow", "Cleaning up", None)
        )
        self.btngrp_filter.setTitle(
            QCoreApplication.translate("MainWindow", "Filter results", None)
        )
        self.btn_osx.setText(QCoreApplication.translate("MainWindow", "OSX", None))
        self.btn_windows.setText(
            QCoreApplication.translate("MainWindow", "Windows", None)
        )
        self.btn_allos.setText(QCoreApplication.translate("MainWindow", "all OS", None))
        self.btn_linux.setText(QCoreApplication.translate("MainWindow", "Linux", None))
        # if QT_CONFIG(tooltip)
        self.btn_oneclick.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Use last used settings to update blender. Uses the path in the above text field and specified version on the button.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btn_oneclick.setText(
            QCoreApplication.translate("MainWindow", "PushButton", None)
        )
        self.lbl_quick.setText(
            QCoreApplication.translate("MainWindow", "Quick Update", None)
        )
        self.lbl_caution.setText(
            QCoreApplication.translate(
                "MainWindow",
                " ABLER is in its beta phase, please update to the latest build.",
                None,
            )
        )
        # if QT_CONFIG(tooltip)
        self.btn_newVersion.setToolTip(
            QCoreApplication.translate("MainWindow", "New version available", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.btn_newVersion.setText(
            QCoreApplication.translate("MainWindow", "New version available", None)
        )
        # if QT_CONFIG(tooltip)
        self.btn_execute.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Run downloaded ABLER version", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btn_execute.setText(
            QCoreApplication.translate("MainWindow", "Run ABLER", None)
        )
        self.btn_update.setToolTip(
            QCoreApplication.translate("MainWindow", "Update ABLER", None)
        )
        self.btn_update.setText(
            QCoreApplication.translate("MainWindow", "Update ABLER", None)
        )
        self.btn_update_launcher.setToolTip(
            QCoreApplication.translate("MainWindow", "Update ABLER Launcher", None)
        )
        self.btn_update_launcher.setText(
            QCoreApplication.translate("MainWindow", "Update ABLER Launcher", None)
        )

    # retranslateUi
