from PySide2.QtWidgets import QWidget, QStyle, QAbstractItemView
from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QStandardItemModel, QStandardItem
from ui.Welcome import Ui_WelcomeWindow

class uiWelcomeWindow(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_WelcomeWindow()
        self.ui.setupUi(self)
        
        self.__recentModel = QStandardItemModel(self)
        icon = self.style().standardIcon(QStyle.SP_FileIcon)        
        recentFiles = ["file1.reg", "file1.reg", "file1.reg", "file1.reg", "file1.reg", "file1.reg", "file1.reg", "file1.reg", "file1.reg"]
        for file in recentFiles:
            item = QStandardItem(file)
            item.setText(file)
            item.setIcon(icon)
            item.read
            self.__recentModel.appendRow(item)
        self.ui.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.listView.setModel(self.__recentModel)
        
