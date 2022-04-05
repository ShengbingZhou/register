import os
import datetime
import shutil

from PySide2.QtWidgets import QWidget, QAbstractItemView, QMessageBox
from PySide2.QtCore import Qt, Slot, QDir
from PySide2.QtGui import QStandardItemModel, QStandardItem, QIcon
from PySide2.QtSql import QSqlDatabase, QSqlTableModel
from ui.Welcome import Ui_WelcomeWindow
from QRegisterConst import QRegisterConst

class uiWelcomeWindow(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_WelcomeWindow()
        self.ui.setupUi(self)
        self.ui.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.icon = QIcon('icon/file32.png')
        with open (QRegisterConst.StyleFile) as file:
            style = file.read()
        self.setStyleSheet(style)
        self.ui.listView.doubleClicked.connect(self.do_listView_doubleCliced)

    def updateRecentFiles(self, fileName):
        now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
        self.conn = QSqlDatabase.addDatabase("QSQLITE", "%srecent_files.db"%now)
        rf = QDir.homePath() + "/.reg/recent_files.db"
        if os.path.isfile(rf):
            self.conn.setDatabaseName(rf)
        else:
            dir = QDir.homePath() + "/.reg"
            if not os.path.exists(dir):            
                os.mkdir(dir)
            shutil.copyfile("template/recent_files.db", rf)
            self.conn.setDatabaseName(rf)
        if self.conn.open():
            recentFilesTableModel = QSqlTableModel(self, self.conn)
            recentFilesTableModel.setEditStrategy(QSqlTableModel.OnManualSubmit )
            recentFilesTableModel.setTable("RecentFiles")
            recentFilesTableModel.select()
            
            maxRow = 20
            
            if os.path.isfile(fileName):
                for i in range(recentFilesTableModel.rowCount()):
                    if recentFilesTableModel.record(i).value("path") == fileName:
                        recentFilesTableModel.removeRows(i, 1)
                r = recentFilesTableModel.record()
                r.remove(r.indexOf('id'))
                r.setValue("path", fileName)
                recentFilesTableModel.insertRecord(-1, r) 
                rows = recentFilesTableModel.rowCount()
                if rows > maxRow:
                    recentFilesTableModel.removeRows(0, rows - maxRow)
                recentFilesTableModel.submitAll()
            
            recentFilesTableModel.select()
            rows = recentFilesTableModel.rowCount()
            self.standardModel = QStandardItemModel(self)
            for i in range(rows):
                record = recentFilesTableModel.record(rows - i - 1)
                item = QStandardItem(record.value("path"))
                item.setIcon(self.icon)
                self.standardModel.appendRow(item)
            self.ui.listView.setModel(self.standardModel)
            
            self.conn.close()
        else:
            QMessageBox.warning("Error", "Unable to open files list.", QMessageBox.Yes)            
        return
    
    def setMainWindow(self, mainWindow):
        self.mainWindow = mainWindow

    @Slot()
    def do_listView_doubleCliced(self, current):
        fileName = current.data(Qt.DisplayRole)
        self.mainWindow.openFile(fileName)
        return    