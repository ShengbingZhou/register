import shutil
import datetime

from PySide2.QtWidgets import QWidget, QStyle, QAbstractItemView
from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtSql import QSqlDatabase, QSqlTableModel, QSqlRelationalTableModel, QSqlRelationalDelegate
from ui.Module import Ui_ModuleWindow

class uiModuleWindow(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ModuleWindow()
        self.ui.setupUi(self)
        self.ui.pbSetColumns.setVisible(False)
        return
        
    def newDatabase(self):
        # create temp database
        now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        newname = "temp_module_%s.db"%now
        shutil.copyfile("module_template.db", newname)
        
        # open new database
        self.conn = QSqlDatabase.addDatabase("QSQLITE", newname)
        self.conn.setDatabaseName(newname)
        if self.conn.open():
            self.tableModel = QSqlTableModel(self, self.conn)
            self.tableModel.setEditStrategy(QSqlTableModel.OnFieldChange)
            
            self.regTableModel = QSqlTableModel(self, self.conn)
            self.regTableModel.setTable("Register")
            self.regTableModel.select()
            
            # create info row0
            self.tableModel.setTable("info")
            self.tableModel.select()
            r = self.tableModel.record()
            r.remove(r.indexOf('id'))
            r.setValue("version", "0")
            r.setValue("filename", "")
            r.setValue("savedbefore", "0")
            r.setValue("author", "Bing")
            r.setValue("lastupdatedate", now)
            self.tableModel.insertRecord(-1, r)
            
            # create memorymap row0
            self.tableModel.setTable("MemoryMap")
            self.tableModel.select()
            r = self.tableModel.record()
            r.remove(r.indexOf('id'))
            r.setValue("OffsetAddress", 0)
            self.tableModel.insertRecord(-1, r)
            r = self.tableModel.record(0)
            memorymaprow0id = r.value("id")
            
            # create regmaps row0
            self.tableModel.setTable("RegisterMaps")
            self.tableModel.select()
            r = self.tableModel.record()
            r.remove(r.indexOf('id'))
            r.setValue("MemoryMapId", memorymaprow0id)
            self.tableModel.insertRecord(-1, r)
            r = self.tableModel.record(0)
            registermapsrow0id = r.value("id")
            
            # create regmap row0
            self.tableModel.setTable("RegisterMap")
            self.tableModel.select()
            r = self.tableModel.record()
            r.remove(r.indexOf('id'))
            r.setValue("RegisterMapsId", registermapsrow0id)
            r.setValue("Name", "RegMap")
            r.setValue("OffsetAddress", 0)
            self.tableModel.insertRecord(-1, r)
            r = self.tableModel.record(0)
            registermaprow0id = r.value("id")
            
            # create register row0 & row1
            self.regTableModel.setTable("Register")
            self.regTableModel.select()
            r = self.regTableModel.record()
            r.remove(r.indexOf('id'))
            r.setValue("RegisterMapId", registermaprow0id)
            r.setValue("Name", "NoNameReg")
            r.setValue("Description", "This is a test register")
            r.setValue("OffsetAddress", 0)
            r.setValue("Width", 8)
            self.regTableModel.insertRecord(-1, r)
            r.setValue("OffsetAddress", 1)
            self.regTableModel.insertRecord(-1, r)

            # create standard model for treeview          
            self.standardModel = QStandardItemModel()
            memoryMapItem = QStandardItem("MemoryMap")
            self.standardModel.setItem(0, 0, memoryMapItem)
            regMapsItem = QStandardItem("RegisterMaps")
            memoryMapItem.setChild(0, 0, regMapsItem)
            
            self.tableModel.setTable("RegisterMap")
            self.tableModel.select()
            for i in range(self.tableModel.rowCount()):
                regMapRecord = self.tableModel.record(i)
                regMapitem = QStandardItem(regMapRecord.value("name"))
                regMapsItem.setChild(i, 0, regMapitem)
                for j in range(self.regTableModel.rowCount()):
                    regRecord = self.regTableModel.record(j)
                    if regRecord.value("RegisterMapId") == regMapRecord.value("id"):
                        regItem = QStandardItem(regRecord.value("name"))
                        regMapitem.setChild(j, 0, regItem)
            self.ui.treeView.setModel(self.standardModel)
            self.ui.treeView.expandAll()
            
            # show register table
            self.tableModel.setTable("Register")
            self.tableModel.select();
            self.ui.tableView.setModel(self.tableModel)
            self.ui.tableView.resizeColumnsToContents()
        else:
            QMessageBox.warning(self, "Error", "Failed to open template file")
        return
        
        

        
