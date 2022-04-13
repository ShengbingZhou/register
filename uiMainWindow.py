# built-in package
import sys
import os
import time

# pyside2 package
from PySide2.QtWidgets import QWidget, QMainWindow, QMessageBox, QTabBar, QDesktopWidget, QFileDialog
from PySide2.QtCore import Qt, Slot, QDir
from PySide2.QtGui import QIcon

# local package
from ui.Main import Ui_MainWindow
from uiWelcome import uiWelcomeWindow
from uiModule import uiModuleWindow
from uiRegisterAccessLog import uiRegAccessLogWindow
from QRegisterConst import QRegisterConst

class uiMainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Register Tool v%s"%(QRegisterConst.Version))
        self.setWindowIcon(QIcon(os.path.join(QRegisterConst.BaseDir, 'icon/module32.png')))
        self.ui.actionSave_As.setVisible(False)
        self.ui.menuEdit.setTitle('')
        self.resize(1600, 900)
        rect = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        rect.moveCenter(centerPoint)
        self.move(rect.topLeft())
        with open (QRegisterConst.StyleFile) as file:
            style = file.read()
        self.setStyleSheet(style)
        
        # add 1st tab: welcome tab
        self.welcomeWindow = uiWelcomeWindow(self)
        self.welcomeWindow.setAttribute(Qt.WA_DeleteOnClose)
        self.welcomeWindow.updateRecentFiles('')
        self.welcomeWindow.setMainWindow(self)
        self.ui.tabWidget.addTab(self.welcomeWindow, "Welcome")
        self.ui.tabWidget.tabBar().setTabButton(0, QTabBar.RightSide, None)
        
        # create reigster log tab but hide it at default
        self.regLogWindow = uiRegAccessLogWindow(self)
        self.regLogWindow.setMainWindow(self)
        index = self.ui.tabWidget.addTab(self.regLogWindow, "RegLog")
        self.ui.tabWidget.setTabVisible(index, False)
    
    def closeEvent(self, event):
        # close all tabs
        for i in range(self.ui.tabWidget.count()):
            tab = self.ui.tabWidget.widget(i)
            tab.close()
        # clean up files in /home/.reg/*.reg (old > 3 days)
        tmpFolder = QDir.homePath() +  "/.reg/"
        currentTime = time.time()
        outDated = 3 * 24 * 60 * 60 # 3 days
        for file in os.listdir (tmpFolder):
            fileFullPath = os.path.join(tmpFolder, file)
            if os.path.isfile(fileFullPath):
                f, ext = os.path.splitext(fileFullPath)
                if ext == QRegisterConst.DesignFileExt:
                    if currentTime - os.path.getmtime(fileFullPath) > outDated:
                        os.remove(fileFullPath)                   
        event.accept()

    def openFile(self, fileName):
        if os.path.isfile(fileName) == False:
            QMessageBox.warning(self, "Error", "Failed to open %s as it doesn't exist."%fileName)
            return
        moduleWindow = uiModuleWindow(self)
        moduleWindow.setAttribute(Qt.WA_DeleteOnClose)
        if moduleWindow.openDatabase(fileName):
            f_name, f_ext = os.path.splitext(os.path.basename(fileName))
            index = self.ui.tabWidget.addTab(moduleWindow, f_name)
            self.ui.tabWidget.setCurrentIndex(index)
            moduleWindow.setMainWindow(self)
            if self.welcomeWindow != None:
                self.welcomeWindow.updateRecentFiles(fileName)
        return

    def appendRegLog(self, line):
        self.regLogWindow.appendRegLog(line)

    @Slot(int)
    def on_tabWidget_tabCloseRequested(self, index):
        tab = self.ui.tabWidget.widget(index)
        if tab.tabType == QRegisterConst.RegLogTab:            
            self.ui.tabWidget.setTabVisible(index, False)
        else:
            tab.close()
        return

    @Slot()
    def on_actionAbout_triggered(self):
        QMessageBox.information(self, "About", "Copyright by @ShengbingZhou (shengbingzhou@outlook.com) \n\n Source code link: https://github.dev/ShengbingZhou/register \n\n", QMessageBox.Yes)

    @Slot()
    def on_actionRegister_Access_Log_triggered(self):
        for i in range(self.ui.tabWidget.count()):
            tab = self.ui.tabWidget.widget(i)
            if tab.tabType == QRegisterConst.RegLogTab:            
                self.ui.tabWidget.setTabVisible(i, True)
                self.ui.tabWidget.setCurrentIndex(i)

    @Slot()
    def on_actionNew_triggered(self):
        moduleWindow = uiModuleWindow(self)
        moduleWindow.setAttribute(Qt.WA_DeleteOnClose)
        if moduleWindow.newDatabase():
            index = self.ui.tabWidget.addTab(moduleWindow, "NoName")
            self.ui.tabWidget.setCurrentIndex(index)
            moduleWindow.setMainWindow(self)
        return

    @Slot()
    def on_actionOpen_triggered(self):
        fileName, filterUsed = QFileDialog.getOpenFileName(self, "Open register file", QDir.homePath(), "Register File (*%s)"%QRegisterConst.DesignFileExt)
        if fileName != '':
            self.openFile(fileName)
        return
    
    @Slot()
    def on_actionImportYoda_triggered(self):
        fileName, filterUsed = QFileDialog.getOpenFileName(self, "Import Yoda file", QDir.homePath(), "Yoda File (*.sp1)")
        if fileName != '':
            if os.path.isfile(fileName) == False:
                QMessageBox.warning(self, "Error", "Failed to open %s as it doesn't exist."%fileName)
                return
            moduleWindow = uiModuleWindow(self)
            moduleWindow.setAttribute(Qt.WA_DeleteOnClose)
            if moduleWindow.importYodaSp1(fileName):
                index = self.ui.tabWidget.addTab(moduleWindow, "NoName")
                self.ui.tabWidget.setCurrentIndex(index)
                moduleWindow.setMainWindow(self)
        return

    @Slot()
    def on_actionImportIP_XACT_triggered(self):
        fileName, filterUsed = QFileDialog.getOpenFileName(self, "Import ipxact (.xml) file", QDir.homePath(), "ipxact File (*.xml)")
        if fileName != '':
            if os.path.isfile(fileName) == False:
                QMessageBox.warning(self, "Error", "Failed to open %s as it doesn't exist."%fileName)
                return
            moduleWindow = uiModuleWindow(self)
            moduleWindow.setAttribute(Qt.WA_DeleteOnClose)
            if moduleWindow.importIpxact(fileName):
                index = self.ui.tabWidget.addTab(moduleWindow, "NoName")
                self.ui.tabWidget.setCurrentIndex(index)
                moduleWindow.setMainWindow(self)
        return

    @Slot()
    def on_actionExportIP_XACT_triggered(self):
        if self.ui.tabWidget.currentIndex() < 0:
            return
        tab = self.ui.tabWidget.widget(self.ui.tabWidget.currentIndex())
        if tab.tabType == QRegisterConst.ModuleTab:
            tab.exporIpxact()
        return  

    @Slot()
    def on_actionExportDocx_triggered(self):
        if self.ui.tabWidget.currentIndex() < 0:
            return
        tab = self.ui.tabWidget.widget(self.ui.tabWidget.currentIndex())
        if tab.tabType == QRegisterConst.ModuleTab:
            tab.exporDocx()
        return        

    @Slot()
    def on_actionSave_triggered(self):
        if self.ui.tabWidget.currentIndex() < 0:
            return
        tab = self.ui.tabWidget.widget(self.ui.tabWidget.currentIndex())
        if tab.tabType == QRegisterConst.ModuleTab:
            fileName = tab.saveDatabase()
            if fileName != '':
                f_name, f_ext = os.path.splitext(os.path.basename(fileName))
                self.ui.tabWidget.setTabText(self.ui.tabWidget.currentIndex(), f_name)
                if self.welcomeWindow != None:
                    self.welcomeWindow.updateRecentFiles(fileName)
        return

    @Slot()
    def on_actionSave_As_triggered(self):
        return
    
    @Slot()
    def on_actionDesignView_triggered(self):
        if self.ui.tabWidget.currentIndex() < 0:
            return
        tab = self.ui.tabWidget.widget(self.ui.tabWidget.currentIndex())
        if tab.tabType == QRegisterConst.ModuleTab:
            tab.setView(QRegisterConst.DesignView)
        return
    
    @Slot()
    def on_actionDebugView_triggered(self):
        if self.ui.tabWidget.currentIndex() < 0:
            return
        tab = self.ui.tabWidget.widget(self.ui.tabWidget.currentIndex())
        if tab.tabType == QRegisterConst.ModuleTab:
            tab.setView(QRegisterConst.DebugView)
        return
    
    @Slot()
    def on_actionClose_triggered(self):
        if self.ui.tabWidget.currentIndex() < 0:
            return
        tab = self.ui.tabWidget.widget(self.ui.tabWidget.currentIndex())
        if tab.tabType == QRegisterConst.ModuleTab:
            tab.close()
        
    @Slot()
    def on_actionExit_triggered(self):
        self.close()
        sys.exit()
