# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'RegisterAccessLog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_RegisterAccessWindow(object):
    def setupUi(self, RegisterAccessWindow):
        if not RegisterAccessWindow.objectName():
            RegisterAccessWindow.setObjectName(u"RegisterAccessWindow")
        RegisterAccessWindow.resize(970, 662)
        self.verticalLayout = QVBoxLayout(RegisterAccessWindow)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(RegisterAccessWindow)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.frame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pbOpen = QPushButton(self.frame)
        self.pbOpen.setObjectName(u"pbOpen")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pbOpen.sizePolicy().hasHeightForWidth())
        self.pbOpen.setSizePolicy(sizePolicy)
        self.pbOpen.setMinimumSize(QSize(200, 0))

        self.gridLayout.addWidget(self.pbOpen, 1, 0, 1, 1)

        self.pbSave = QPushButton(self.frame)
        self.pbSave.setObjectName(u"pbSave")
        sizePolicy.setHeightForWidth(self.pbSave.sizePolicy().hasHeightForWidth())
        self.pbSave.setSizePolicy(sizePolicy)
        self.pbSave.setMinimumSize(QSize(200, 0))
        self.pbSave.setBaseSize(QSize(0, 0))

        self.gridLayout.addWidget(self.pbSave, 1, 1, 1, 1)

        self.pbRun = QPushButton(self.frame)
        self.pbRun.setObjectName(u"pbRun")
        sizePolicy.setHeightForWidth(self.pbRun.sizePolicy().hasHeightForWidth())
        self.pbRun.setSizePolicy(sizePolicy)
        self.pbRun.setMinimumSize(QSize(200, 0))
        self.pbRun.setBaseSize(QSize(0, 0))

        self.gridLayout.addWidget(self.pbRun, 1, 3, 1, 1)


        self.verticalLayout.addWidget(self.frame)

        self.frame_2 = QFrame(RegisterAccessWindow)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(2)
        sizePolicy1.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy1)
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.txtReg = QTextBrowser(self.frame_2)
        self.txtReg.setObjectName(u"txtReg")

        self.verticalLayout_2.addWidget(self.txtReg)


        self.verticalLayout.addWidget(self.frame_2)


        self.retranslateUi(RegisterAccessWindow)

        QMetaObject.connectSlotsByName(RegisterAccessWindow)
    # setupUi

    def retranslateUi(self, RegisterAccessWindow):
        RegisterAccessWindow.setWindowTitle(QCoreApplication.translate("RegisterAccessWindow", u"Form", None))
        self.pbOpen.setText(QCoreApplication.translate("RegisterAccessWindow", u"Open", None))
        self.pbSave.setText(QCoreApplication.translate("RegisterAccessWindow", u"Save", None))
        self.pbRun.setText(QCoreApplication.translate("RegisterAccessWindow", u"Run", None))
    # retranslateUi

