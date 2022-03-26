import sys
import os

from PySide2.QtWidgets import QApplication, QMainWindow
from uiMainWindow import uiMainWindow

os.environ["QT_FONT_DPI"] = "110" # fix dpi on different monitor

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = uiMainWindow()
    mw.show()
    app.exec_()
