import os
import shutil
import datetime

from PySide2.QtWidgets import QWidget, QStyle, QAbstractItemView, QMessageBox, QLineEdit
from PySide2.QtCore import Qt, Slot, QItemSelectionModel, QSize
from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtSql import QSqlDatabase, QSqlTableModel, QSqlQueryModel, QSqlRecord
from ui.Module import Ui_ModuleWindow
from QSqlBitfieldTableModel import QSqlBitfieldTableModel

class uiModuleWindow(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ModuleWindow()
        self.ui.setupUi(self)
        self.ui.pbSetColumns.setVisible(False)
        self.ui.treeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableView.setAlternatingRowColors(True)
        with open ('style.qss') as file:
            str = file.read()
        self.setStyleSheet(str)
        
        self.treeViewItemTableNameRole = Qt.UserRole + 1
        self.treeViewItemMemoryMapIdRole = Qt.UserRole + 2
        self.treeViewItemRegMapIdRole = Qt.UserRole + 3
        self.treeViewItemRegIdRole = Qt.UserRole + 4
        self.treeViewItemBfRefIdRole = Qt.UserRole + 5
        self.treeViewItemBfIdRole = Qt.UserRole + 6
        self.treeViewItemBfEnumIdRole = Qt.UserRole + 7
        
        self.tableViewRegQuery = "SELECT * FROM Register WHERE RegisterMapId="
        self.tableViewBfQuery = "SELECT A.id, B.RegisterId, A.Name, A.Access, A.DefaultValue, A.Description, A.Width, B.RegisterOffset, B.BitfieldOffset, B.SliceWidth FROM Bitfield AS A JOIN BitfieldRef AS B ON A.id=B.BitfieldId WHERE B.RegisterId="
        self.tableViewBfEnumQuery = "SELECT * FROM BitfieldEnum WHERE BitfieldId="
        
        self.newModule = True
        self.fileName = ''
        self.newFileName = ''
        return
    
    def closeEvent(self, event):
        if os.path.isfile(self.newFileName):
            os.remove(self.newFileName)
        event.accept()

    def newInfoRow(self, model, updateDate):
        r = model.record()
        r.remove(r.indexOf('id'))
        r.setValue("version", 0)
        r.setValue("author", "Bing")
        r.setValue("lastupdatedate", updateDate)
        model.insertRecord(-1, r)
        r = model.record(model.rowCount() - 1)
        return r

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
        
    def newRegRow(self, model, regMapId, OffsetAddress, Width):
        r = model.record()
        r.remove(r.indexOf('id'))
        r.setValue("RegisterMapId", regMapId)
        r.setValue("Description", "This is no name register")
        r.setValue("OffsetAddress", OffsetAddress)
        r.setValue("Width", Width)
        id = 0
        if model.rowCount() > 0:
            id = model.record(model.rowCount() - 1).value("id")        
        r.setValue("Name", "RegNoName%s"%id)
        model.insertRecord(-1, r)
        r = model.record(model.rowCount() - 1)
        return r
    
    def newBfRow(self, model, bfRefModel, regId, memMapId, Width):                
        r = model.record()
        r.remove(r.indexOf('id'))
        r.setValue("MemoryMapId", memMapId)
        r.setValue("Width", Width)
        r.setValue("Description", "This is no name bitfield")
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
        rr.setValue("RegisterOffset", 0)
        rr.setValue("BitfieldOffset", 0)
        rr.setValue("SliceWidth", Width)
        bfRefModel.insertRecord(-1, rr)
        return r
    
    def newBfEnumRow(self, model, bfId):
        r = model.record()
        r.remove(r.indexOf('id'))
        r.setValue("BitfieldId", bfId)
        r.setValue("Description", "This is no name enum")
        r.setValue("Value", 0)
        id = 0
        if model.rowCount() > 0:
            id = model.record(model.rowCount() - 1).value("id")        
        r.setValue("Name", "EnumNoName%s"%id)
        model.insertRecord(-1, r)
        r = model.record(model.rowCount() - 1)
        return r
    
    def newDatabase(self):
        # create temp database
        now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%_S_%f')
        newName = "__temp_module_%s.db"%now
        shutil.copyfile("module_template.db", newName)
        self.newFileName = newName
        self.newModule = True
        
        # open new database
        if self.__setupModel(newName):
            info0Id = self.newInfoRow(self.infoTableModel, now).value("id")                 # create info row0
            memoryMap0Id = self.newMemoryMapRow(self.memoryMaptableModel).value("id")       # create memorymap row0
            regMap0Id = self.newRegMapRow(self.regMapTableModel, memoryMap0Id).value("id")  # create regmap row0
            reg0Id = self.newRegRow(self.regTableModel, regMap0Id, 0, 8).value("id")        # create register row0
            reg1Id = self.newRegRow(self.regTableModel, regMap0Id, 0, 8).value("id")        # create register row1
            bf0Id = self.newBfRow(self.bfTableModel, self.bfRefTableModel, reg0Id, memoryMap0Id, 8).value("id") # create bitfield row0
            bf1Id = self.newBfRow(self.bfTableModel, self.bfRefTableModel, reg1Id, memoryMap0Id, 8).value("id") # create bitfield row1
            bfEnum0Id = self.newBfEnumRow(self.bfEnumTableModel, bf0Id).value("id")         # create bitfieldenum row0
            self.__setupTreeView()
        else:
            False
        return True
        
    def openDatabase(self, fileName):
        self.fileName = fileName
        self.newModule = False
        if self.__setupModel(fileName):
            self.__setupTreeView()
        else:
            return False
        return True
    
    def __setupModel(self, fileName):
        self.conn = QSqlDatabase.addDatabase("QSQLITE", fileName)
        self.conn.setDatabaseName(fileName)
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
            self.bfRefTableModel.setTable("BitfieldRef")
            self.bfRefTableModel.select()
            
            self.bfTableModel = QSqlTableModel(self, self.conn)
            self.bfTableModel.setEditStrategy(QSqlTableModel.OnFieldChange) 
            self.bfTableModel.setTable("Bitfield")
            self.bfTableModel.select()
            
            self.bfEnumTableModel = QSqlTableModel(self, self.conn)
            self.bfEnumTableModel.setEditStrategy(QSqlTableModel.OnFieldChange) 
            self.bfEnumTableModel.setTable("BitfieldEnum")
            self.bfEnumTableModel.select()
            
            self.bfQueryModel = QSqlBitfieldTableModel()
            self.bfQueryModel.setConn(self.conn)
        else:
            QMessageBox.warning(self, "Error", "Failed to open %s"%fileName)  
            return False
        return True
        
    def __setupTreeView(self):
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
                    bfQueryModel.setQuery("SELECT * FROM Bitfield WHERE EXISTS (SELECT * FROM BitfieldRef WHERE Bitfield.id=BitfieldRef.BitfieldId AND BitfieldRef.RegisterId=%s)"%regRecord.value("id"), self.conn)
                    for k in range(bfQueryModel.rowCount()):
                        bfRecord = bfQueryModel.record(k)
                        bfItem = QStandardItem(bfRecord.value("name"))
                        bfItem.setData("Bitfield", self.treeViewItemTableNameRole)
                        bfItem.setData(memoryMapRecord.value("id"), self.treeViewItemMemoryMapIdRole)
                        bfItem.setData(regMapRecord.value("id"), self.treeViewItemRegMapIdRole)
                        bfItem.setData(regRecord.value("id"), self.treeViewItemRegIdRole)
                        bfItem.setData(bfRecord.value("id"), self.treeViewItemBfIdRole)
                        regItem.appendRow(bfItem)
                        
                        #bitfield enum
                        bfEnumQueryModel = QSqlQueryModel()
                        bfEnumQueryModel.setQuery("SELECT * FROM BitfieldEnum WHERE BitfieldId=%s"%bfRecord.value("id"), self.conn)
                        for j in range(bfEnumQueryModel.rowCount()):
                            bfEnumRecord = bfEnumQueryModel.record(j)
                            bfEnumItem = QStandardItem(bfEnumRecord.value("name"))
                            bfEnumItem.setData("BitfieldEnum", self.treeViewItemTableNameRole)
                            bfEnumItem.setData(memoryMapRecord.value("id"), self.treeViewItemMemoryMapIdRole)
                            bfEnumItem.setData(regMapRecord.value("id"), self.treeViewItemRegMapIdRole)
                            bfEnumItem.setData(regRecord.value("id"), self.treeViewItemRegIdRole)
                            bfEnumItem.setData(bfRecord.value("id"), self.treeViewItemBfIdRole)
                            bfEnumItem.setData(bfEnumRecord.value("id"), self.treeViewItemBfEnumIdRole)
                            bfItem.appendRow(bfEnumItem)

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
        
    @Slot('QItemSelection', 'QItemSelection')
    def do_tableView_selectionChanged(self, selected, deselected):
        i = 0
        return
        
    @Slot()
    def do_treeView_currentChanged(self, current, previous):
        tableName = str(current.data(self.treeViewItemTableNameRole))

        if tableName == "MemoryMap": # memorymap selected, show memorymap table
            self.ui.tableView.setModel(self.memoryMaptableModel)
            self.ui.tableView.selectionModel().selectionChanged.connect(self.do_tableView_selectionChanged)
            self.ui.tableView.hideColumn(0) # id
            self.ui.tableView.showColumn(1) # offset address
            self.ui.tableView.resizeColumnsToContents()
            
            self.ui.pbAddRegMap.setEnabled(True)
            self.ui.pbAddReg.setEnabled(False)
            self.ui.pbAddBf.setEnabled(False)
            self.ui.pbAddBfEnum.setEnabled(False)
            self.ui.labelDescription.setText("Tips: Click <font color=\"red\">%s</font> to add new register map. "%self.ui.pbAddRegMap.text())
            
        elif tableName == "RegisterMap": # regmap or reg selected, show regmap table
            self.ui.tableView.setModel(self.regMapTableModel)
            self.ui.tableView.selectionModel().selectionChanged.connect(self.do_tableView_selectionChanged)
            self.ui.tableView.hideColumn(0) # id
            self.ui.tableView.hideColumn(1) # memmap id
            self.ui.tableView.resizeColumnsToContents()
            
            self.ui.pbAddRegMap.setEnabled(True)
            self.ui.pbAddReg.setEnabled(True)
            self.ui.pbAddBf.setEnabled(False)
            self.ui.pbAddBfEnum.setEnabled(False)
            self.ui.labelDescription.setText("Tips: Click <font color=\"red\">%s</font> to add new register map. "%self.ui.pbAddRegMap.text())
            
        elif tableName == "Register": # reg selected, show reg table
            regMapId = int(current.data(self.treeViewItemRegMapIdRole))
            self.regTableModel.setFilter("RegisterMapId=%s"%regMapId)
            self.regTableModel.select()
            self.ui.tableView.setModel(self.regTableModel)
            
            self.ui.tableView.selectionModel().selectionChanged.connect(self.do_tableView_selectionChanged)
            self.ui.tableView.hideColumn(0) # id
            self.ui.tableView.hideColumn(1) # regmap id
            self.ui.tableView.resizeColumnsToContents()
            
            self.ui.pbAddRegMap.setEnabled(True)
            self.ui.pbAddReg.setEnabled(True)
            self.ui.pbAddBf.setEnabled(True)
            self.ui.pbAddBfEnum.setEnabled(False)
            self.ui.labelDescription.setText("Tips: Click <font color=\"red\">%s</font> to add new register. "%self.ui.pbAddReg.text())
            
        elif tableName == "Bitfield": # bf selected, show bf table
            regId = int(current.data(self.treeViewItemRegIdRole))
            self.bfQueryModel.setQuery("%s%s"%(self.tableViewBfQuery, regId), self.conn)
            self.ui.tableView.setModel(self.bfQueryModel)
            
            self.ui.tableView.selectionModel().selectionChanged.connect(self.do_tableView_selectionChanged)
            self.ui.tableView.hideColumn(0) # id
            self.ui.tableView.hideColumn(1) # regid
            self.ui.tableView.resizeColumnsToContents()
            
            self.ui.pbAddRegMap.setEnabled(True)
            self.ui.pbAddReg.setEnabled(True)
            self.ui.pbAddBf.setEnabled(True)
            self.ui.pbAddBfEnum.setEnabled(True)
            self.ui.labelDescription.setText("Tips: Click <font color=\"red\">%s</font> to add new bitfield. "%self.ui.pbAddBf.text())
            
        elif tableName == "BitfieldEnum": # bfenum selected, show bfenum table
            bfId = int(current.data(self.treeViewItemBfIdRole))            
            self.regTableModel.setFilter("BitfieldId=%s"%bfId)
            self.regTableModel.select()
            self.ui.tableView.setModel(self.bfEnumTableModel)
            self.ui.tableView.selectionModel().selectionChanged.connect(self.do_tableView_selectionChanged)
            self.ui.tableView.hideColumn(0) # id
            self.ui.tableView.hideColumn(1) # bfid
            self.ui.tableView.resizeColumnsToContents()
            
            self.ui.pbAddRegMap.setEnabled(True)
            self.ui.pbAddReg.setEnabled(True)
            self.ui.pbAddBf.setEnabled(True)
            self.ui.pbAddBfEnum.setEnabled(True)
            self.ui.labelDescription.setText("Tips: Click <font color=\"red\">%s</font> to add new bitfield enum. "%self.ui.pbAddBfEnum.text())
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
        elif tableName == "BitfieldEnum":
            standardItem.parent().parent().parent().parent().appendRow(newRegMapItem)
        return

    @Slot()
    def on_pbAddReg_clicked(self):
        current = self.ui.treeView.selectedIndexes().pop()
        tableName = str(current.data(self.treeViewItemTableNameRole))
        memoryMapId = int(current.data(self.treeViewItemMemoryMapIdRole))
        regMapId = int(current.data(self.treeViewItemRegMapIdRole))
        r = self.newRegRow(self.regTableModel, regMapId, 0, 8)
        
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
        elif tableName == "BitfieldEnum":
            standardItem.parent().parent().parent().appendRow(newRegItem)
        return

    @Slot()
    def on_pbAddBf_clicked(self):
        current = self.ui.treeView.selectedIndexes().pop()
        tableName = str(current.data(self.treeViewItemTableNameRole))
        memoryMapId = int(current.data(self.treeViewItemMemoryMapIdRole))
        regMapId = int(current.data(self.treeViewItemRegMapIdRole))
        regId = int(current.data(self.treeViewItemRegIdRole))
        r = self.newBfRow(self.bfTableModel, self.bfRefTableModel, regId, memoryMapId, 8)
        
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
            self.bfQueryModel.setQuery("%s%s"%(self.tableViewBfQuery, regId), self.conn)
        elif tableName == "BitfieldEnum":
            standardItem.parent().parent().appendRow(newBfItem)        
        return

    @Slot()
    def on_pbAddBfEnum_clicked(self):
        current = self.ui.treeView.selectedIndexes().pop()
        tableName = str(current.data(self.treeViewItemTableNameRole))
        memoryMapId = int(current.data(self.treeViewItemMemoryMapIdRole))
        regMapId = int(current.data(self.treeViewItemRegMapIdRole))
        regId = int(current.data(self.treeViewItemRegIdRole))
        bfId = int(current.data(self.treeViewItemBfIdRole))
        r = self.newBfEnumRow(self.bfEnumTableModel, bfId)
        
        newBfEnumItem = QStandardItem(r.value("name"))
        newBfEnumItem.setData("BitfieldEnum", self.treeViewItemTableNameRole)
        newBfEnumItem.setData(memoryMapId, self.treeViewItemMemoryMapIdRole)
        newBfEnumItem.setData(regMapId, self.treeViewItemRegMapIdRole)
        newBfEnumItem.setData(regId, self.treeViewItemRegIdRole)
        newBfEnumItem.setData(bfId, self.treeViewItemBfIdRole)
        newBfEnumItem.setData(r.value("id"), self.treeViewItemBfEnumIdRole)
        
        standardItem = self.standardModel.itemFromIndex(current)
        if tableName == "Bitfield":
            standardItem.appendRow(newBfEnumItem)
        elif tableName == "BitfieldEnum":
            standardItem.parent().appendRow(newBfEnumItem)
        return