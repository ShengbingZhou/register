import sys
import os

from PySide2.QtWidgets import QApplication, QMainWindow
from qt_material import apply_stylesheet
from uiMainWindow import uiMainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')
    mw = uiMainWindow()
    mw.show()
    app.exec_()
