import sys
import os
import shutil

from PySide2.QtWidgets import QWidget, QMainWindow, QMessageBox, QTabBar, QStyle, QDesktopWidget, QFileDialog
from PySide2.QtCore import Qt, Slot, QDir
from PySide2.QtSql import QSqlDatabase, QSqlTableModel, QSqlQueryModel, QSqlRecord
from PySide2.QtGui import QIcon
from ui.Main import Ui_MainWindow
from uiWelcome import uiWelcomeWindow
from uiModule import uiModuleWindow
from RegisterConst import RegisterConst

class uiMainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Register Tool v%s"%(RegisterConst.Version))
        self.setWindowIcon(QIcon('icon/module32.png'))
        self.ui.actionSave_As.setVisible(False)
        self.ui.menuEdit.setTitle('')
        self.resize(1440, 900)
        rect = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        rect.moveCenter(centerPoint)
        self.move(rect.topLeft())
        with open (RegisterConst.StyleFile) as file:
            style = file.read()
        self.setStyleSheet(style)
        
        # TODO: add icon for action items?
        #self.ui.actionNew.setIcon(QIcon("icon/new32.png"))
        
        # add welcome tab
        self.welcomeWindow = uiWelcomeWindow(self)
        self.welcomeWindow.setAttribute(Qt.WA_DeleteOnClose)
        self.welcomeWindow.updateRecentFiles('')
        self.welcomeWindow.setMainWindow(self)
        index = self.ui.tabWidget.addTab(self.welcomeWindow, RegisterConst.WelcomeTabText)
        self.ui.tabWidget.setCurrentIndex(index)   
        self.ui.tabWidget.tabBar().setTabButton(0, QTabBar.RightSide, None)
    
    def closeEvent(self, event):
        for i in range(self.ui.tabWidget.count()):
            tab = moduleWindow = self.ui.tabWidget.widget(i)
            tab.close()
        event.accept()
    
    def openFile(self, fileName):
        if os.path.isfile(fileName) == False:
            QMessageBox.warning(self, "Error", "Failed to open %s as it doesn't exist."%fileName)
            return
        moduleWindow = uiModuleWindow(self)
        moduleWindow.setAttribute(Qt.WA_DeleteOnClose)
        if moduleWindow.openDatabase(fileName):
            index = self.ui.tabWidget.addTab(moduleWindow, os.path.basename(fileName))
            self.ui.tabWidget.setCurrentIndex(index)
            moduleWindow.setMainWindow(self)
            if self.welcomeWindow != None:
                self.welcomeWindow.updateRecentFiles(fileName)
        return
        
    def importYodaSp1File(self, fileName):
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
        if moduleWindow.newDatabase():
            index = self.ui.tabWidget.addTab(moduleWindow, "NoName")
            self.ui.tabWidget.setCurrentIndex(index)
            moduleWindow.setMainWindow(self)
        return

    @Slot()
    def on_actionOpen_triggered(self):
        fileName, filterUsed = QFileDialog.getOpenFileName(self, "Open register file", QDir.homePath(), "Register File (*)")
        if fileName != '':
            self.openFile(fileName)
        return
    
    @Slot()
    def on_actionImportYoda_triggered(self):
        fileName, filterUsed = QFileDialog.getOpenFileName(self, "Open Yoda (.sp1) file", QDir.homePath(), "Register File (*)")
        if fileName != '':
            self.importYodaSp1File(fileName)
        return

    @Slot()
    def on_actionImportIP_XACT_triggered(self):
        QMessageBox.information(self, "Import IP-XACT file", "TODO", QMessageBox.Yes)
        return
    
    @Slot()
    def on_actionExportIP_XACT_triggered(self):
        QMessageBox.information(self, "Export IP-XACT file", "TODO", QMessageBox.Yes)
        return    
    
    @Slot()
    def on_actionSave_triggered(self):
        if self.ui.tabWidget.currentIndex() < 0:
            return
        tabText = self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex())
        if tabText != RegisterConst.WelcomeTabText:
            moduleWindow = self.ui.tabWidget.widget(self.ui.tabWidget.currentIndex())
            fileName = moduleWindow.saveDatabase()
            if fileName != '':
                self.ui.tabWidget.setTabText(self.ui.tabWidget.currentIndex(), os.path.basename(fileName))
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
        tabText = self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex())
        if tabText != RegisterConst.WelcomeTabText:
            moduleWindow = self.ui.tabWidget.widget(self.ui.tabWidget.currentIndex())
            moduleWindow.setView(RegisterConst.DesignView)
        return
    
    @Slot()
    def on_actionDebugView_triggered(self):
        if self.ui.tabWidget.currentIndex() < 0:
            return
        tabText = self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex())
        if tabText != RegisterConst.WelcomeTabText:
            moduleWindow = self.ui.tabWidget.widget(self.ui.tabWidget.currentIndex())
            moduleWindow.setView(RegisterConst.DebugView)
        return
    
    @Slot()
    def on_actionClose_triggered(self):
        if self.ui.tabWidget.currentIndex() < 0:
            return
        tabText = self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex())
        if tabText != RegisterConst.WelcomeTabText:
            moduleWindow = self.ui.tabWidget.widget(self.ui.tabWidget.currentIndex())
            moduleWindow.close()
        
    @Slot()
    def on_actionExit_triggered(self):
        self.close()
        sys.exit()
