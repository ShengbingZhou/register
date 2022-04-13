# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Main.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1045, 749)
        self.actionNew = QAction(MainWindow)
        self.actionNew.setObjectName(u"actionNew")
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.actionSave_As = QAction(MainWindow)
        self.actionSave_As.setObjectName(u"actionSave_As")
        self.actionClose = QAction(MainWindow)
        self.actionClose.setObjectName(u"actionClose")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionCut = QAction(MainWindow)
        self.actionCut.setObjectName(u"actionCut")
        self.actionCopy = QAction(MainWindow)
        self.actionCopy.setObjectName(u"actionCopy")
        self.actionPaste = QAction(MainWindow)
        self.actionPaste.setObjectName(u"actionPaste")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionImportYoda = QAction(MainWindow)
        self.actionImportYoda.setObjectName(u"actionImportYoda")
        self.actionImportIP_XACT = QAction(MainWindow)
        self.actionImportIP_XACT.setObjectName(u"actionImportIP_XACT")
        self.actionExportIP_XACT = QAction(MainWindow)
        self.actionExportIP_XACT.setObjectName(u"actionExportIP_XACT")
        self.actionDesignView = QAction(MainWindow)
        self.actionDesignView.setObjectName(u"actionDesignView")
        self.actionDebugView = QAction(MainWindow)
        self.actionDebugView.setObjectName(u"actionDebugView")
        self.actionExportDocx = QAction(MainWindow)
        self.actionExportDocx.setObjectName(u"actionExportDocx")
        self.actionRegister_Access_Log = QAction(MainWindow)
        self.actionRegister_Access_Log.setObjectName(u"actionRegister_Access_Log")
        self.actionNewDesign = QAction(MainWindow)
        self.actionNewDesign.setObjectName(u"actionNewDesign")
        self.actionOpenDesign = QAction(MainWindow)
        self.actionOpenDesign.setObjectName(u"actionOpenDesign")
        self.actionSaveDesign = QAction(MainWindow)
        self.actionSaveDesign.setObjectName(u"actionSaveDesign")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1045, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuImport = QMenu(self.menuFile)
        self.menuImport.setObjectName(u"menuImport")
        self.menuExport = QMenu(self.menuFile)
        self.menuExport.setObjectName(u"menuExport")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")
        self.menuWindow = QMenu(self.menubar)
        self.menuWindow.setObjectName(u"menuWindow")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuWindow.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.menuImport.menuAction())
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_As)
        self.menuFile.addAction(self.menuExport.menuAction())
        self.menuFile.addAction(self.actionClose)
        self.menuFile.addAction(self.actionExit)
        self.menuImport.addAction(self.actionImportYoda)
        self.menuImport.addAction(self.actionImportIP_XACT)
        self.menuExport.addAction(self.actionExportIP_XACT)
        self.menuExport.addAction(self.actionExportDocx)
        self.menuEdit.addAction(self.actionCut)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menuHelp.addAction(self.actionAbout)
        self.menuView.addAction(self.actionDesignView)
        self.menuView.addAction(self.actionDebugView)
        self.menuWindow.addAction(self.actionRegister_Access_Log)
        self.toolBar.addAction(self.actionNewDesign)
        self.toolBar.addAction(self.actionOpenDesign)
        self.toolBar.addAction(self.actionSaveDesign)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionNew.setText(QCoreApplication.translate("MainWindow", u"New", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.actionSave_As.setText(QCoreApplication.translate("MainWindow", u"Save As", None))
        self.actionClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionCut.setText(QCoreApplication.translate("MainWindow", u"Cut", None))
        self.actionCopy.setText(QCoreApplication.translate("MainWindow", u"Copy", None))
        self.actionPaste.setText(QCoreApplication.translate("MainWindow", u"Paste", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionImportYoda.setText(QCoreApplication.translate("MainWindow", u"yoda", None))
        self.actionImportIP_XACT.setText(QCoreApplication.translate("MainWindow", u"ipxact", None))
        self.actionExportIP_XACT.setText(QCoreApplication.translate("MainWindow", u"ipxact", None))
        self.actionDesignView.setText(QCoreApplication.translate("MainWindow", u"Design", None))
        self.actionDebugView.setText(QCoreApplication.translate("MainWindow", u"Debug", None))
        self.actionExportDocx.setText(QCoreApplication.translate("MainWindow", u"docx", None))
        self.actionRegister_Access_Log.setText(QCoreApplication.translate("MainWindow", u"Register Access Log", None))
        self.actionNewDesign.setText(QCoreApplication.translate("MainWindow", u"New", None))
#if QT_CONFIG(tooltip)
        self.actionNewDesign.setToolTip(QCoreApplication.translate("MainWindow", u"Create a new register design", None))
#endif // QT_CONFIG(tooltip)
        self.actionOpenDesign.setText(QCoreApplication.translate("MainWindow", u"Open", None))
#if QT_CONFIG(tooltip)
        self.actionOpenDesign.setToolTip(QCoreApplication.translate("MainWindow", u"Open a register design", None))
#endif // QT_CONFIG(tooltip)
        self.actionSaveDesign.setText(QCoreApplication.translate("MainWindow", u"Save", None))
#if QT_CONFIG(tooltip)
        self.actionSaveDesign.setToolTip(QCoreApplication.translate("MainWindow", u"Save a register design", None))
#endif // QT_CONFIG(tooltip)
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuImport.setTitle(QCoreApplication.translate("MainWindow", u"Import", None))
        self.menuExport.setTitle(QCoreApplication.translate("MainWindow", u"Export", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.menuWindow.setTitle(QCoreApplication.translate("MainWindow", u"Window", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

