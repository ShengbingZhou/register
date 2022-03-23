import shutil
import datetime

from PySide2.QtWidgets import QWidget, QStyle, QAbstractItemView
from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtSql import QSqlDatabase, QSqlTableModel, QSqlRelationalTableModel, QSqlRelationalDelegate, QSqlQueryModel
from ui.Module import Ui_ModuleWindow

class uiModuleWindow(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ModuleWindow()
        self.ui.setupUi(self)
        self.ui.pbSetColumns.setVisible(False)
        return
    
    def newInfoRow(self, model, updateDate):
        r = model.record()
        r.remove(r.indexOf('id'))
        r.setValue("version", "0")
        r.setValue("filename", "")
        r.setValue("savedbefore", "0")
        r.setValue("author", "Bing")
        r.setValue("lastupdatedate", updateDate)
        model.insertRecord(-1, r)
        return

    def newMemoryMapRow(self, model):
        r = model.record()
        r.remove(r.indexOf('id'))
        r.setValue("OffsetAddress", 0)
        model.insertRecord(-1, r)
        r = model.record(model.rowCount() - 1)
        return r.value("id")
        
    def newRegMapRow(self, model, memoryMapId):
        r = model.record()
        r.remove(r.indexOf('id'))
        r.setValue("MemoryMapId", memoryMapId)
        r.setValue("Name", "RegMap")
        r.setValue("OffsetAddress", 0)
        model.insertRecord(-1, r)
        r = model.record(model.rowCount() - 1)
        return r.value("id")
        
    def newRegRow(self, model, regMapId):
        r = model.record()
        r.remove(r.indexOf('id'))
        r.setValue("RegisterMapId", regMapId)
        r.setValue("Name", "NoNameReg")
        r.setValue("Description", "This is a test register")
        r.setValue("OffsetAddress", 0)
        r.setValue("Width", 8)
        model.insertRecord(-1, r)
        r = model.record(model.rowCount() - 1)
        return r.value("id")
    
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
            
            # create info row0
            self.tableModel.setTable("info")
            self.tableModel.select()
            self.newInfoRow(self.tableModel, now)
            
            # create memorymap row0
            self.tableModel.setTable("MemoryMap")
            self.tableModel.select()
            memoryMapRow0Id = self.newMemoryMapRow(self.tableModel)
            
            # create regmap row0
            self.tableModel.setTable("RegisterMap")
            self.tableModel.select()
            regMapRow0Id = self.newRegMapRow(self.tableModel, memoryMapRow0Id)
            
            # create register row0 & row1
            self.tableModel.setTable("Register")
            self.tableModel.select()
            regId = self.newRegRow(self.tableModel, regMapRow0Id)
            regId = self.newRegRow(self.tableModel, regMapRow0Id)

            # create standard model for treeview          
            self.standardModel = QStandardItemModel()
            
            memoryMapItem = QStandardItem("MemoryMap")
            self.standardModel.setItem(0, 0, memoryMapItem)
            
            regMapsItem = QStandardItem("RegisterMaps")
            memoryMapItem.setChild(0, 0, regMapsItem)
            
            self.tableModel.setTable("RegisterMap")
            self.tableModel.select()
            for i in range(self.tableModel.rowCount()):
                # register map
                regMapRecord = self.tableModel.record(i)
                regMapitem = QStandardItem(regMapRecord.value("name"))
                regMapsItem.setChild(i, 0, regMapitem)
                
                # register
                regQueryModel = QSqlQueryModel()
                regQueryModel.setQuery("SELECT * FROM Register WHERE RegisterMapId=%s"%regMapRecord.value("id"), self.conn)
                for j in range(regQueryModel.rowCount()):
                    regRecord = regQueryModel.record(j)
                    regItem = QStandardItem(regRecord.value("name"))
                    regMapitem.setChild(j, 0, regItem)
                    
                    # bitfield
                    bfRefQueryModel = QSqlQueryModel()
                    bfRefQueryModel.setQuery("SELECT * FROM  WHERE RegisterId=%s"%regRecord.value("id"), self.conn)
                    bfQueryModel = QSqlQueryModel()
                    for k in range(bfRefQueryModel.rowCount()):
                        bfQueryModel.setQuery("SELECT * FROM  WHERE id=%s"%bfRefQueryModel.record(k).value("BitFieldId"), self.conn)
                        bfItem = QStandardItem(bfQueryModel.record(0).value("name"))
                        regItem.setChild(k, 0, bfItem)
                    
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
        
        

        
