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
        ModuleWindow.resize(1446, 876)
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
        self.frame_3 = QFrame(self.frame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.NoFrame)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.frame_3.setLineWidth(0)
        self.gridLayout_2 = QGridLayout(self.frame_3)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.tableViewReg = QTableView(self.frame_3)
        self.tableViewReg.setObjectName(u"tableViewReg")

        self.gridLayout_2.addWidget(self.tableViewReg, 3, 0, 1, 1)

        self.tableView = QTableView(self.frame_3)
        self.tableView.setObjectName(u"tableView")

        self.gridLayout_2.addWidget(self.tableView, 2, 0, 1, 1)

        self.frame_4 = QFrame(self.frame_3)
        self.frame_4.setObjectName(u"frame_4")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_4.sizePolicy().hasHeightForWidth())
        self.frame_4.setSizePolicy(sizePolicy1)
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.frame_4.setLineWidth(0)
        self.gridDebugLayout = QGridLayout(self.frame_4)
        self.gridDebugLayout.setObjectName(u"gridDebugLayout")
        self.pbAddReg = QPushButton(self.frame_4)
        self.pbAddReg.setObjectName(u"pbAddReg")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pbAddReg.sizePolicy().hasHeightForWidth())
        self.pbAddReg.setSizePolicy(sizePolicy2)
        self.pbAddReg.setMinimumSize(QSize(200, 0))

        self.gridDebugLayout.addWidget(self.pbAddReg, 0, 2, 1, 1)

        self.pbAddRegMap = QPushButton(self.frame_4)
        self.pbAddRegMap.setObjectName(u"pbAddRegMap")
        sizePolicy2.setHeightForWidth(self.pbAddRegMap.sizePolicy().hasHeightForWidth())
        self.pbAddRegMap.setSizePolicy(sizePolicy2)
        self.pbAddRegMap.setMinimumSize(QSize(200, 0))

        self.gridDebugLayout.addWidget(self.pbAddRegMap, 0, 1, 1, 1)

        self.pbAddBfEnum = QPushButton(self.frame_4)
        self.pbAddBfEnum.setObjectName(u"pbAddBfEnum")
        sizePolicy2.setHeightForWidth(self.pbAddBfEnum.sizePolicy().hasHeightForWidth())
        self.pbAddBfEnum.setSizePolicy(sizePolicy2)
        self.pbAddBfEnum.setMinimumSize(QSize(200, 0))

        self.gridDebugLayout.addWidget(self.pbAddBfEnum, 0, 4, 1, 1)

        self.pbAddBf = QPushButton(self.frame_4)
        self.pbAddBf.setObjectName(u"pbAddBf")
        sizePolicy2.setHeightForWidth(self.pbAddBf.sizePolicy().hasHeightForWidth())
        self.pbAddBf.setSizePolicy(sizePolicy2)
        self.pbAddBf.setMinimumSize(QSize(200, 0))

        self.gridDebugLayout.addWidget(self.pbAddBf, 0, 3, 1, 1)

        self.pbSetColumns = QPushButton(self.frame_4)
        self.pbSetColumns.setObjectName(u"pbSetColumns")
        sizePolicy2.setHeightForWidth(self.pbSetColumns.sizePolicy().hasHeightForWidth())
        self.pbSetColumns.setSizePolicy(sizePolicy2)
        self.pbSetColumns.setMinimumSize(QSize(200, 0))

        self.gridDebugLayout.addWidget(self.pbSetColumns, 0, 5, 1, 1)

        self.pbAddMemMap = QPushButton(self.frame_4)
        self.pbAddMemMap.setObjectName(u"pbAddMemMap")
        sizePolicy2.setHeightForWidth(self.pbAddMemMap.sizePolicy().hasHeightForWidth())
        self.pbAddMemMap.setSizePolicy(sizePolicy2)
        self.pbAddMemMap.setMinimumSize(QSize(200, 0))

        self.gridDebugLayout.addWidget(self.pbAddMemMap, 0, 0, 1, 1)

        self.pbReadAll = QPushButton(self.frame_4)
        self.pbReadAll.setObjectName(u"pbReadAll")
        sizePolicy2.setHeightForWidth(self.pbReadAll.sizePolicy().hasHeightForWidth())
        self.pbReadAll.setSizePolicy(sizePolicy2)
        self.pbReadAll.setMinimumSize(QSize(200, 0))

        self.gridDebugLayout.addWidget(self.pbReadAll, 1, 0, 1, 1)

        self.pbReadSelected = QPushButton(self.frame_4)
        self.pbReadSelected.setObjectName(u"pbReadSelected")
        sizePolicy2.setHeightForWidth(self.pbReadSelected.sizePolicy().hasHeightForWidth())
        self.pbReadSelected.setSizePolicy(sizePolicy2)
        self.pbReadSelected.setMinimumSize(QSize(200, 0))

        self.gridDebugLayout.addWidget(self.pbReadSelected, 1, 1, 1, 1)

        self.pbWriteAll = QPushButton(self.frame_4)
        self.pbWriteAll.setObjectName(u"pbWriteAll")
        sizePolicy2.setHeightForWidth(self.pbWriteAll.sizePolicy().hasHeightForWidth())
        self.pbWriteAll.setSizePolicy(sizePolicy2)
        self.pbWriteAll.setMinimumSize(QSize(200, 0))

        self.gridDebugLayout.addWidget(self.pbWriteAll, 1, 2, 1, 1)

        self.labelDescription = QLabel(self.frame_4)
        self.labelDescription.setObjectName(u"labelDescription")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.labelDescription.sizePolicy().hasHeightForWidth())
        self.labelDescription.setSizePolicy(sizePolicy3)
        self.labelDescription.setMinimumSize(QSize(0, 60))
        font = QFont()
        font.setPointSize(9)
        self.labelDescription.setFont(font)

        self.gridDebugLayout.addWidget(self.labelDescription, 2, 0, 1, 6)


        self.gridLayout_2.addWidget(self.frame_4, 1, 0, 1, 1)


        self.verticalLayout.addWidget(self.frame_3)

        self.splitter.addWidget(self.frame)

        self.gridLayout.addWidget(self.splitter, 0, 1, 1, 1)


        self.retranslateUi(ModuleWindow)

        QMetaObject.connectSlotsByName(ModuleWindow)
    # setupUi

    def retranslateUi(self, ModuleWindow):
        ModuleWindow.setWindowTitle(QCoreApplication.translate("ModuleWindow", u"Form", None))
        self.pbAddReg.setText(QCoreApplication.translate("ModuleWindow", u"+ Register", None))
        self.pbAddRegMap.setText(QCoreApplication.translate("ModuleWindow", u"+ RegisterMap", None))
        self.pbAddBfEnum.setText(QCoreApplication.translate("ModuleWindow", u"+ BitfieldEnum", None))
        self.pbAddBf.setText(QCoreApplication.translate("ModuleWindow", u"+ Bitfield", None))
        self.pbSetColumns.setText(QCoreApplication.translate("ModuleWindow", u"-> ColumnsVisibility", None))
        self.pbAddMemMap.setText(QCoreApplication.translate("ModuleWindow", u"+ MemoryMap", None))
        self.pbReadAll.setText(QCoreApplication.translate("ModuleWindow", u"Read All", None))
        self.pbReadSelected.setText(QCoreApplication.translate("ModuleWindow", u"Read Selected", None))
        self.pbWriteAll.setText(QCoreApplication.translate("ModuleWindow", u"Write All", None))
        self.labelDescription.setText(QCoreApplication.translate("ModuleWindow", u"TextLabel", None))
    # retranslateUi

