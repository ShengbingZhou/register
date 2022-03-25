# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Module.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_ModuleWindow(object):
    def setupUi(self, ModuleWindow):
        if not ModuleWindow.objectName():
            ModuleWindow.setObjectName(u"ModuleWindow")
        ModuleWindow.resize(1014, 675)
        self.gridLayout = QGridLayout(ModuleWindow)
        self.gridLayout.setObjectName(u"gridLayout")
        self.splitter = QSplitter(ModuleWindow)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.treeView = QTreeView(self.splitter)
        self.treeView.setObjectName(u"treeView")
        self.splitter.addWidget(self.treeView)
        self.frame = QFrame(self.splitter)
        self.frame.setObjectName(u"frame")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setLineWidth(0)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_2 = QFrame(self.frame)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.frame_2.setLineWidth(0)
        self.horizontalLayout = QHBoxLayout(self.frame_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.line = QFrame(self.frame_2)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout.addWidget(self.line)

        self.pbAddRegMap = QPushButton(self.frame_2)
        self.pbAddRegMap.setObjectName(u"pbAddRegMap")

        self.horizontalLayout.addWidget(self.pbAddRegMap)

        self.pbAddReg = QPushButton(self.frame_2)
        self.pbAddReg.setObjectName(u"pbAddReg")

        self.horizontalLayout.addWidget(self.pbAddReg)

        self.line_5 = QFrame(self.frame_2)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.VLine)
        self.line_5.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout.addWidget(self.line_5)

        self.line_3 = QFrame(self.frame_2)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.VLine)
        self.line_3.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout.addWidget(self.line_3)

        self.pbAddBf = QPushButton(self.frame_2)
        self.pbAddBf.setObjectName(u"pbAddBf")

        self.horizontalLayout.addWidget(self.pbAddBf)

        self.line_2 = QFrame(self.frame_2)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.VLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout.addWidget(self.line_2)

        self.pbAddBfEnum = QPushButton(self.frame_2)
        self.pbAddBfEnum.setObjectName(u"pbAddBfEnum")

        self.horizontalLayout.addWidget(self.pbAddBfEnum)

        self.line_6 = QFrame(self.frame_2)
        self.line_6.setObjectName(u"line_6")
        self.line_6.setFrameShape(QFrame.VLine)
        self.line_6.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout.addWidget(self.line_6)

        self.pbSetColumns = QPushButton(self.frame_2)
        self.pbSetColumns.setObjectName(u"pbSetColumns")

        self.horizontalLayout.addWidget(self.pbSetColumns)


        self.verticalLayout.addWidget(self.frame_2)

        self.frame_4 = QFrame(self.frame)
        self.frame_4.setObjectName(u"frame_4")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_4.sizePolicy().hasHeightForWidth())
        self.frame_4.setSizePolicy(sizePolicy1)
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.line_4 = QFrame(self.frame_4)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.VLine)
        self.line_4.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_2.addWidget(self.line_4)

        self.labelDescription = QLabel(self.frame_4)
        self.labelDescription.setObjectName(u"labelDescription")
        sizePolicy2 = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.labelDescription.sizePolicy().hasHeightForWidth())
        self.labelDescription.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.labelDescription)


        self.verticalLayout.addWidget(self.frame_4)

        self.frame_3 = QFrame(self.frame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.frame_3.setLineWidth(0)
        self.gridLayout_2 = QGridLayout(self.frame_3)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.tableView = QTableView(self.frame_3)
        self.tableView.setObjectName(u"tableView")

        self.gridLayout_2.addWidget(self.tableView, 1, 0, 1, 1)


        self.verticalLayout.addWidget(self.frame_3)

        self.splitter.addWidget(self.frame)

        self.gridLayout.addWidget(self.splitter, 0, 1, 1, 1)


        self.retranslateUi(ModuleWindow)

        QMetaObject.connectSlotsByName(ModuleWindow)
    # setupUi

    def retranslateUi(self, ModuleWindow):
        ModuleWindow.setWindowTitle(QCoreApplication.translate("ModuleWindow", u"Form", None))
        self.pbAddRegMap.setText(QCoreApplication.translate("ModuleWindow", u"+ RegisterMap", None))
        self.pbAddReg.setText(QCoreApplication.translate("ModuleWindow", u"+ Register", None))
        self.pbAddBf.setText(QCoreApplication.translate("ModuleWindow", u"+ Bitfield", None))
        self.pbAddBfEnum.setText(QCoreApplication.translate("ModuleWindow", u"+ BitfieldEnum", None))
        self.pbSetColumns.setText(QCoreApplication.translate("ModuleWindow", u"-> ColumnsVisibility", None))
        self.labelDescription.setText(QCoreApplication.translate("ModuleWindow", u"TextLabel", None))
    # retranslateUi

