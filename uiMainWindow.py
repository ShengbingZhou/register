from PySide2.QtWidgets import QWidget, QMainWindow
from PySide2.QtCore import Qt, Slot
from ui.Main import Ui_MainWindow
from uiWelcome import uiWelcomeWindow

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
            
        