import os
import datetime

from PySide2.QtWidgets import QWidget
from ui.RegisterAccessLog import Ui_RegisterAccessWindow
from QRegisterConst import QRegisterConst

class uiWelcomeWindow(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_RegisterAccessWindow()
        self.ui.setupUi(self)
        with open (QRegisterConst.StyleFile) as file:
            style = file.read()
        self.setStyleSheet(style)

