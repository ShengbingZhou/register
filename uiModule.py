import shutil
import datetime

from PySide2.QtWidgets import QWidget, QStyle, QAbstractItemView
from PySide2.QtCore import Qt, Slot, QItemSelectionModel, QSize
from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtSql import QSqlDatabase, QSqlTableModel, QSqlRelationalTableModel, QSqlRelationalDelegate, QSqlQueryModel, QSqlRecord
from ui.Module import Ui_ModuleWindow

class uiModuleWindow(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ModuleWindow()
        self.ui.setupUi(self)
        self.ui.treeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.treeViewItemTableNameRole = Qt.UserRole + 1
        self.treeViewItemMemoryMapIdRole = Qt.UserRole + 2
        self.treeViewItemRegMapIdRole = Qt.UserRole + 3
        self.treeViewItemRegIdRole = Qt.UserRole + 4
        self.treeViewItemBfRefIdRole = Qt.UserRole + 5
        self.treeViewItemBfIdRole = Qt.UserRole + 6
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
        return r
    
    def newRegMapRow(self, model, memoryMapId):
        r = model.record()
        r.remove(r.indexOf('id'))
        r.setValue("MemoryMapId", memoryMapId)
        r.setValue("OffsetAddress", 0)
        id = 0
        if model.rowCount() > 0:
            id = model.record(model.rowCount() - 1).value("id")
        r.setValue("Name", "RegMap%s"%id)
        model.insertRecord(-1, r)
        r = model.record(model.rowCount() - 1)
        return r
        
    def newRegRow(self, model, regMapId, Description, OffsetAddress, Width):
        r = model.record()
        r.remove(r.indexOf('id'))
        r.setValue("RegisterMapId", regMapId)
        r.setValue("Description", Description)
        r.setValue("OffsetAddress", OffsetAddress)
        r.setValue("Width", Width)
        id = 0
        if model.rowCount() > 0:
            id = model.record(model.rowCount() - 1).value("id")        
        r.setValue("Name", "RegNoName%s"%id)
        model.insertRecord(-1, r)
        r = model.record(model.rowCount() - 1)
        return r
    
    def newBfRow(self, model, bfRefModel, regId, Width):        
        queryModel = QSqlQueryModel()
        
        queryModel.setQuery("SELECT * FROM Register WHERE id=%s"%regId, model.database())
        regRecord = queryModel.record(0)
        regMapId = regRecord.value("RegisterMapId")
        
        queryModel.setQuery("SELECT * FROM RegisterMap WHERE id=%s"%regMapId, model.database())
        regMapRecord = queryModel.record(0)
        memMapId = regMapRecord.value("MemoyrMapId")
        
        r = model.record()
        r.remove(r.indexOf('id'))
        r.setValue("MemoryMapId", memMapId)
        r.setValue("Width", Width)
        id = 0
        if model.rowCount() > 0:
            id = model.record(model.rowCount() - 1).value("id")   
        r.setValue("Name", "BfNoName%s"%id)
        model.insertRecord(-1, r)
        r = model.record(model.rowCount() - 1)
        bfId = r.value("id")
        
        rr = bfRefModel.record()
        rr.remove(rr.indexOf('id'))
        rr.setValue("RegisterId", regId)
        rr.setValue("BitfieldId", bfId)
        bfRefModel.insertRecord(-1, rr)
        return r
    
    def newDatabase(self):
        # create temp database
        now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        newname = "temp_module_%s.db"%now
        shutil.copyfile("module_template.db", newname)
        
        # open new database
        self.conn = QSqlDatabase.addDatabase("QSQLITE", newname)
        self.conn.setDatabaseName(newname)
        if self.conn.open():
            self.infoTableModel = QSqlTableModel(self, self.conn)
            self.infoTableModel.setEditStrategy(QSqlTableModel.OnFieldChange) 
            self.infoTableModel.setTable("info")
            self.infoTableModel.select()
            
            self.memoryMaptableModel = QSqlTableModel(self, self.conn)
            self.memoryMaptableModel.setEditStrategy(QSqlTableModel.OnFieldChange)  
            self.memoryMaptableModel.setTable("MemoryMap")
            self.memoryMaptableModel.select()
            
            self.regMapTableModel = QSqlTableModel(self, self.conn)
            self.regMapTableModel.setEditStrategy(QSqlTableModel.OnFieldChange)  
            self.regMapTableModel.setTable("RegisterMap")
            self.regMapTableModel.select()
            
            self.regTableModel = QSqlTableModel(self, self.conn)
            self.regTableModel.setEditStrategy(QSqlTableModel.OnFieldChange)  
            self.regTableModel.setTable("Register")
            self.regTableModel.select()
            
            self.bfRefTableModel = QSqlTableModel(self, self.conn)
            self.bfRefTableModel.setEditStrategy(QSqlTableModel.OnFieldChange)
            self.bfRefTableModel.setTable("BitFieldRef")
            self.bfRefTableModel.select()
            
            self.bfTableModel = QSqlTableModel(self, self.conn)
            self.bfTableModel.setEditStrategy(QSqlTableModel.OnFieldChange) 
            self.bfTableModel.setTable("Bitfield")
            self.bfTableModel.select()
            
            # create info row0
            self.newInfoRow(self.infoTableModel, now)
            
            # create memorymap 
            memoryMap0Id = self.newMemoryMapRow(self.memoryMaptableModel).value("id")
            
            # create regmap row0
            regMap0Id = self.newRegMapRow(self.regMapTableModel, memoryMap0Id).value("id")
            
            # create register row0 & row1
            reg0Id = self.newRegRow(self.regTableModel, regMap0Id, "This is no name register", 0, 8).value("id")
            reg1Id = self.newRegRow(self.regTableModel, regMap0Id, "This is no name register", 0, 8).value("id")
            
            # create bitfield row0
            self.newBfRow(self.bfTableModel, self.bfRefTableModel, reg0Id, 4)
            self.newBfRow(self.bfTableModel, self.bfRefTableModel, reg1Id, 4)

            # create standard model for treeview          
            self.standardModel = QStandardItemModel()
            root = self.standardModel.invisibleRootItem()
            
            # memory map
            memoryMapQueryModel = QSqlQueryModel()
            memoryMapQueryModel.setQuery("SELECT * FROM MemoryMap", self.conn)
            for l in range(memoryMapQueryModel.rowCount()):
                memoryMapRecord = memoryMapQueryModel.record(l)
                self.memoryMapItem = QStandardItem("MemoryMap")
                self.memoryMapItem.setData("MemoryMap", self.treeViewItemTableNameRole)
                self.memoryMapItem.setData(memoryMapRecord.value("id"), self.treeViewItemMemoryMapIdRole)
                root.appendRow(self.memoryMapItem)
                
                # register map
                regMapQueryModel = QSqlQueryModel()
                regMapQueryModel.setQuery("SELECT * FROM RegisterMap WHERE memoryMapId=%s"%memoryMapRecord.value("id"), self.conn)
                for i in range(regMapQueryModel.rowCount()):
                    regMapRecord = regMapQueryModel.record(i)
                    regMapitem = QStandardItem(regMapRecord.value("name"))
                    regMapitem.setData("RegisterMap", self.treeViewItemTableNameRole)
                    regMapitem.setData(memoryMapRecord.value("id"), self.treeViewItemMemoryMapIdRole)
                    regMapitem.setData(regMapRecord.value("id"), self.treeViewItemRegMapIdRole)
                    self.memoryMapItem.appendRow(regMapitem)
                    
                    # register
                    regQueryModel = QSqlQueryModel()
                    regQueryModel.setQuery("SELECT * FROM Register WHERE RegisterMapId=%s"%regMapRecord.value("id"), self.conn)
                    for j in range(regQueryModel.rowCount()):
                        regRecord = regQueryModel.record(j)
                        regItem = QStandardItem(regRecord.value("name"))
                        regItem.setData("Register", self.treeViewItemTableNameRole)
                        regItem.setData(memoryMapRecord.value("id"), self.treeViewItemMemoryMapIdRole)
                        regItem.setData(regMapRecord.value("id"), self.treeViewItemRegMapIdRole)
                        regItem.setData(regRecord.value("id"), self.treeViewItemRegIdRole)
                        regMapitem.appendRow(regItem)
                        
                        # bitfield
                        bfQueryModel = QSqlQueryModel()
                        bfQueryModel.setQuery("SELECT * FROM Bitfield WHERE EXISTS (SELECT * FROM BitFieldRef WHERE Bitfield.id=BitFieldRef.BitfieldId AND BitFieldRef.RegisterId=%s)"%regRecord.value("id"), self.conn)
                        for k in range(bfQueryModel.rowCount()):
                            bfRecord = bfQueryModel.record(k)
                            bfItem = QStandardItem(bfRecord.value("name"))
                            bfItem.setData("Bitfield", self.treeViewItemTableNameRole)
                            bfItem.setData(memoryMapRecord.value("id"), self.treeViewItemMemoryMapIdRole)
                            bfItem.setData(regMapRecord.value("id"), self.treeViewItemRegMapIdRole)
                            bfItem.setData(regRecord.value("id"), self.treeViewItemRegIdRole)
                            bfItem.setData(bfRecord.value("id"), self.treeViewItemBfIdRole)
                            regItem.appendRow(bfItem)

            # show tree view nodes
            self.ui.treeView.setModel(self.standardModel)
            self.ui.treeView.expandAll()

            # connect slots
            treeViewSelectionModel = self.ui.treeView.selectionModel()
            treeViewSelectionModel.currentChanged.connect(self.do_treeView_currentChanged)
            
            # select memory map node
            memoryMapItemIndex = self.standardModel.indexFromItem(self.memoryMapItem)
            treeViewSelectionModel.select(memoryMapItemIndex, QItemSelectionModel.ClearAndSelect)
            self.do_treeView_currentChanged(memoryMapItemIndex, None)
        else:
            QMessageBox.warning(self, "Error", "Failed to open template file")
        return
        
    @Slot()
    def do_treeView_currentChanged(self, current, previous):
        tableName = str(current.data(self.treeViewItemTableNameRole))

        if tableName == "MemoryMap": # memorymap selected, show memorymap table
            self.ui.tableView.setModel(self.memoryMaptableModel)
            self.ui.tableView.hideColumn(0)
            self.ui.tableView.showColumn(1)
            self.ui.tableView.resizeColumnsToContents()
            
            self.ui.pbAddRegMap.setEnabled(True)
            self.ui.pbAddReg.setEnabled(False)
            self.ui.pbAddBf.setEnabled(False)
            self.ui.labelDescription.setText("Tips: Click <font color=\"red\">%s</font> to add new register map. "%self.ui.pbAddRegMap.text())
        elif tableName == "RegisterMap": # regmap or reg selected, show regmap table
            self.ui.tableView.setModel(self.regMapTableModel)
            self.ui.tableView.hideColumn(0)
            self.ui.tableView.hideColumn(1)
            self.ui.tableView.resizeColumnsToContents()
            
            self.ui.pbAddRegMap.setEnabled(True)
            self.ui.pbAddReg.setEnabled(True)
            self.ui.pbAddBf.setEnabled(False)
            self.ui.labelDescription.setText("Tips: Click <font color=\"red\">%s</font> to add new register. "%self.ui.pbAddRegMap.text())
        elif tableName == "Register": # reg selected, show reg table
            regMapId = int(current.data(self.treeViewItemRegMapIdRole))
            regQueryModel = QSqlQueryModel()
            regQueryModel.setQuery("SELECT * FROM Register WHERE RegisterMapId=%s"%regMapId, self.conn)
            self.ui.tableView.setModel(regQueryModel)
            self.ui.tableView.hideColumn(0)
            self.ui.tableView.hideColumn(1)
            self.ui.tableView.resizeColumnsToContents()
            
            self.ui.pbAddRegMap.setEnabled(True)
            self.ui.pbAddReg.setEnabled(True)
            self.ui.pbAddBf.setEnabled(True)
            self.ui.labelDescription.setText("Tips: Click <font color=\"red\">%s</font> to add new register. "%self.ui.pbAddReg.text())
        elif tableName == "Bitfield": # bf selected, show bf table
            regId = int(current.data(self.treeViewItemRegIdRole))
            bfQueryModel = QSqlQueryModel()
            bfQueryModel.setQuery("SELECT * FROM Bitfield WHERE EXISTS (SELECT * FROM BitFieldRef WHERE Bitfield.id=BitFieldRef.BitfieldId AND BitFieldRef.RegisterId=%s)"%regId, self.conn)
            self.ui.tableView.setModel(bfQueryModel)
            self.ui.tableView.hideColumn(0)
            self.ui.tableView.hideColumn(1)
            self.ui.tableView.resizeColumnsToContents()
            
            self.ui.pbAddRegMap.setEnabled(True)
            self.ui.pbAddReg.setEnabled(True)
            self.ui.pbAddBf.setEnabled(True)
            self.ui.labelDescription.setText("Tips: Click <font color=\"red\">%s</font> to add new bitfield. "%self.ui.pbAddBf.text())
            #self.ui.labelDescription.setText("Bitfield Mapping: <font size=16>7 6 5 4</font><font size=18 color=\"red\"> 3 2 1 0 </font>")
        return
        
    @Slot()
    def on_pbAddRegMap_clicked(self):
        current = self.ui.treeView.selectedIndexes().pop()
        tableName = str(current.data(self.treeViewItemTableNameRole))
        memoryMapId = int(current.data(self.treeViewItemMemoryMapIdRole))
        r = self.newRegMapRow(self.regMapTableModel, memoryMapId)
        
        newRegMapItem = QStandardItem(r.value("name"))
        newRegMapItem.setData("RegisterMap", self.treeViewItemTableNameRole)
        newRegMapItem.setData(memoryMapId, self.treeViewItemMemoryMapIdRole)
        newRegMapItem.setData(r.value("id"), self.treeViewItemRegMapIdRole)
        
        standardItem = self.standardModel.itemFromIndex(current)
        if tableName == "MemoryMap":
            standardItem.appendRow(newRegMapItem)
        elif tableName == "RegisterMap":
            standardItem.parent().appendRow(newRegMapItem)
        elif tableName == "Register":
            standardItem.parent().parent().appendRow(newRegMapItem)
        elif tableName == "Bitfield":
            standardItem.parent().parent().parent().appendRow(newRegMapItem)
        return

    @Slot()
    def on_pbAddReg_clicked(self):
        current = self.ui.treeView.selectedIndexes().pop()
        tableName = str(current.data(self.treeViewItemTableNameRole))
        memoryMapId = int(current.data(self.treeViewItemMemoryMapIdRole))
        regMapId = int(current.data(self.treeViewItemRegMapIdRole))
        r = self.newRegRow(self.regTableModel, regMapId, "This is no name register", 0, 8)
        
        newRegItem = QStandardItem(r.value("name"))
        newRegItem.setData("Register", self.treeViewItemTableNameRole)
        newRegItem.setData(memoryMapId, self.treeViewItemMemoryMapIdRole)
        newRegItem.setData(regMapId, self.treeViewItemRegMapIdRole)
        newRegItem.setData(r.value("id"), self.treeViewItemRegIdRole)
        
        standardItem = self.standardModel.itemFromIndex(current)
        if tableName == "RegisterMap":
            standardItem.appendRow(newRegItem)
        elif tableName == "Register":
            standardItem.parent().appendRow(newRegItem)
        elif tableName == "Bitfield":
            standardItem.parent().parent().appendRow(newRegItem)
        return

    @Slot()
    def on_pbAddBf_clicked(self):
        current = self.ui.treeView.selectedIndexes().pop()
        tableName = str(current.data(self.treeViewItemTableNameRole))
        memoryMapId = int(current.data(self.treeViewItemMemoryMapIdRole))
        regMapId = int(current.data(self.treeViewItemRegMapIdRole))
        regId = int(current.data(self.treeViewItemRegIdRole))
        r = self.newBfRow(self.bfTableModel, self.bfRefTableModel, regId, 4)
        
        newBfItem = QStandardItem(r.value("name"))
        newBfItem.setData("Bitfield", self.treeViewItemTableNameRole)
        newBfItem.setData(memoryMapId, self.treeViewItemMemoryMapIdRole)
        newBfItem.setData(regMapId, self.treeViewItemRegMapIdRole)
        newBfItem.setData(regId, self.treeViewItemRegIdRole)
        newBfItem.setData(r.value("id"), self.treeViewItemBfIdRole)
        
        standardItem = self.standardModel.itemFromIndex(current)
        if tableName == "Register":
            standardItem.appendRow(newBfItem)
        elif tableName == "Bitfield":
            standardItem.parent().appendRow(newBfItem)
        return
