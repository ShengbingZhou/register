#! /usr/bin/python3
import sys
import os
import traceback

from PySide2.QtWidgets import QApplication, QMessageBox
from uiMainWindow import uiMainWindow

os.environ["QT_FONT_DPI"] = "96" # fix dpi on different monitor

def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("Error")
    msg.setInformativeText(tb)
    msg.setWindowTitle("Error")
    msg.exec_()

if __name__ == "__main__":
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    mw = uiMainWindow()
    mw.show()
    app.exec_()
