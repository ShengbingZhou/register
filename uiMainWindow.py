import sys
import os
import shutil

from PySide2.QtWidgets import QWidget, QMainWindow, QFileDialog, QMessageBox, QTabBar, QStyle
from PySide2.QtCore import Qt, Slot, QDir
from PySide2.QtSql import QSqlDatabase, QSqlTableModel, QSqlQueryModel, QSqlRecord
from ui.Main import Ui_MainWindow
from uiWelcome import uiWelcomeWindow
from uiModule import uiModuleWindow

class uiMainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Register Tool")
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.ui.actionSave_As.setVisible(False)
        with open ('style.qss') as file:
            str = file.read()
        self.setStyleSheet(str)
        
        # add welcome tab
        self.welcomeWindow = uiWelcomeWindow(self)
        self.welcomeWindow.setAttribute(Qt.WA_DeleteOnClose)
        self.welcomeWindow.updateRecentFiles('')
        self.welcomeWindow.setMainWindow(self)
        index = self.ui.tabWidget.addTab(self.welcomeWindow, "Welcome")
        self.ui.tabWidget.setCurrentIndex(index)   
        self.ui.tabWidget.tabBar().setTabButton(0, QTabBar.RightSide, None)
    
    def closeEvent(self, event):
        for i in range(self.ui.tabWidget.count()):
            tab = moduleWindow = self.ui.tabWidget.widget(i)
            tab.close()
        event.accept()
    
    def openFile(self, fileName):
        moduleWindow = uiModuleWindow(self)
        moduleWindow.setAttribute(Qt.WA_DeleteOnClose)
        if moduleWindow.openDatabase(fileName):
            index = self.ui.tabWidget.addTab(moduleWindow, os.path.basename(fileName))
            self.ui.tabWidget.setCurrentIndex(index)
            if self.welcomeWindow != None:
                self.welcomeWindow.updateRecentFiles(fileName)
    @Slot(int)
    def on_tabWidget_tabCloseRequested(self, index):
        if (index < 0):
            return
        tab = self.ui.tabWidget.widget(index)
        tab.close()
        return

    @Slot()
    def on_actionAbout_triggered(self):
        QMessageBox.information(self, "About", "Copyright by @ShengbingZhou (shengbingzhou@outlook.com) \n\n Source code link: https://github.dev/ShengbingZhou/register \n\n", QMessageBox.Yes)

    @Slot()
    def on_actionNew_triggered(self):
        moduleWindow = uiModuleWindow(self)
        moduleWindow.setAttribute(Qt.WA_DeleteOnClose)
        moduleWindow.newDatabase()
        index = self.ui.tabWidget.addTab(moduleWindow, "NoName")
        self.ui.tabWidget.setCurrentIndex(index)
        return

    @Slot()
    def on_actionOpen_triggered(self):
        fileName, filterUsed = QFileDialog.getOpenFileName(self, "Open register file", QDir.homePath(), "Register Files (*)", "(*.*)")
        if fileName != '':
            self.openFile(fileName)
        return
    
    @Slot()
    def on_actionSave_triggered(self):
        if self.ui.tabWidget.currentIndex() < 0:
            return
        tabText = self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex())
        if tabText != "Welcome":
            moduleWindow = self.ui.tabWidget.widget(self.ui.tabWidget.currentIndex())
            if moduleWindow.newModule == True:
                fileName, filterUsed = QFileDialog.getSaveFileName(self, "Save register file", QDir.homePath(), "Register Files (*)", "(*.*)")
                if fileName !='':
                    try:
                        # TODO: push db?
                        shutil.copy(moduleWindow.newFileName, fileName)
                    except:
                        QMessageBox.warning(self, "Error", "Save Error", QMessageBox.Yes)
                        return
                    moduleWindow.fileName = fileName
                    moduleWindow.newModule = False
                    self.ui.tabWidget.setTabText(self.ui.tabWidget.currentIndex(), os.path.basename(fileName))
                    
                    # update recent file list
                    if self.welcomeWindow != None:
                        self.welcomeWindow.updateRecentFiles(fileName)
            else:
                # TODO: push db?
                if moduleWindow.newFileName != '':
                    shutil.copy(moduleWindow.newFileName, moduleWindow.fileName)
        return

    @Slot()
    def on_actionSave_As_triggered(self):
        return
    
    @Slot()
    def on_actionClose_triggered(self):
        if self.ui.tabWidget.currentIndex() < 0:
            return
        tabText = self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex())
        if tabText != "Welcome":
            moduleWindow = self.ui.tabWidget.widget(self.ui.tabWidget.currentIndex())
            moduleWindow.close()
        
    @Slot()
    def on_actionExit_triggered(self):
        self.close()
        sys.exit()
