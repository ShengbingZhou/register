import sys

from PySide2.QtWidgets import QWidget, QMainWindow
from PySide2.QtCore import Qt, Slot
from ui.Main import Ui_MainWindow
from uiWelcome import uiWelcomeWindow
from uiModule import uiModuleWindow

class uiMainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Register Tool")
        
        # add welcome tab
        welcomeWindow = uiWelcomeWindow(self)
        welcomeWindow.setAttribute(Qt.WA_DeleteOnClose)
        index = self.ui.tabWidget.addTab(welcomeWindow, "Welcome")
        self.ui.tabWidget.setCurrentIndex(index)
        
    @Slot(int)
    def on_tabWidget_tabCloseRequested(self, index):
        if (index < 0):
            return
        tab = self.ui.tabWidget.widget(index)
        tab.close()
            
    @Slot()
    def on_actionNew_triggered(self):
        moduleWindow = uiModuleWindow(self)
        moduleWindow.setAttribute(Qt.WA_DeleteOnClose)
        moduleWindow.newDatabase()
        index = self.ui.tabWidget.addTab(moduleWindow, "NoName")
        self.ui.tabWidget.setCurrentIndex(index)
        
    @Slot()
    def on_actionOpen_triggered(self):
        i = 0
        
    @Slot()
    def on_actionSave_triggered(self):
        i = 0
        
    @Slot()
    def on_actionSave_As_triggered(self):
        i = 0
        
    @Slot()
    def on_actionClose_triggered(self):
        i = 0
        
    @Slot()
    def on_actionExit_triggered(self):
        sys.exit()