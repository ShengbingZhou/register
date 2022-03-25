from PySide2.QtWidgets import QWidget, QStyle, QAbstractItemView
from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtSql import QSqlDatabase, QSqlTableModel
from ui.Welcome import Ui_WelcomeWindow

class uiWelcomeWindow(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_WelcomeWindow()
        self.ui.setupUi(self)
        self.icon = self.style().standardIcon(QStyle.SP_FileIcon)
        
    def updateRecentFiles(self, fileName):
        self.conn = QSqlDatabase.addDatabase("QSQLITE", "recent_files.db")
        self.conn.setDatabaseName("recent_files.db")
        if self.conn.open():
            recentFilesTableModel = QSqlTableModel(self, self.conn)
            recentFilesTableModel.setEditStrategy(QSqlTableModel.OnFieldChange)
            recentFilesTableModel.setTable("RecentFiles")
            recentFilesTableModel.select()
            if fileName != '':
                r = recentFilesTableModel.record()
                r.remove(r.indexOf('id'))
                r.setValue("path", fileName)
                recentFilesTableModel.insertRecord(0, r) 
                if recentFilesTableModel.rowCount() > 6:
                    recentFilesTableModel.removeRows(6, 1)
                recentFilesTableModel.submit()
            standardModel = QStandardItemModel(self)
            for i in range(recentFilesTableModel.rowCount()):
                record = recentFilesTableModel.record(i)
                item = QStandardItem(record.value("path"))
                item.setIcon(self.icon)
                standardModel.appendRow(item)
            self.ui.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.ui.listView.setModel(standardModel)
            self.conn.close()
        else:
            QMessageBox.warning("Error", "Unable to open files list.", QMessageBox.Yes)            
        return

        