import sys
import os

os.environ["QT_FONT_DPI"] = "96"

from PySide2.QtWidgets import QApplication, QMainWindow
from uiMainWindow import uiMainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = uiMainWindow()
    mw.show()
    app.exec_()
