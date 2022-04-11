import os
import datetime

from PySide2.QtWidgets import QWidget
from ui.RegisterAccessLog import Ui_RegisterAccessWindow
from QRegisterConst import QRegisterConst

class uiRegAccessLogWindow(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_RegisterAccessWindow()
        self.ui.setupUi(self)
        self.ui.label.setText("")
        self.tabType = QRegisterConst.RegLogTab
        with open (QRegisterConst.StyleFile) as file:
            style = file.read()
        self.setStyleSheet(style)

    def setMainWindow(self, mainWindow):
        self.mainWindow = mainWindow

    def appendRegLog(self, line):
        self.ui.txtReg.append(line)