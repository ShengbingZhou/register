import os
import shutil
import datetime

from PySide2.QtWidgets import QWidget, QStyle, QAbstractItemView, QMessageBox, QLineEdit, QMenu, QAction, QFileDialog
from PySide2.QtCore import Qt, Slot, QItemSelectionModel, QSize, QEvent, QDir
from PySide2.QtGui import QStandardItemModel, QStandardItem, QIcon, QColor
from PySide2.QtSql import QSqlDatabase, QSqlTableModel, QSqlQueryModel, QSqlRecord, QSqlQuery
from ui.Module import Ui_ModuleWindow
from QSqlBitfieldTableModel import QSqlBitfieldTableModel
from QCustomizedSqlTableModel import QCustomizedSqlTableModel

class uiModuleWindow(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ModuleWindow()
        self.ui.setupUi(self)
        self.ui.pbSetColumns.setVisible(False)
        self.ui.treeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableView.setAlternatingRowColors(True)
        self.ui.treeView.installEventFilter(self)
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
        self.tableViewBfQuery = "SELECT A.id, B.RegisterId, A.DisplayOrder, A.Name, A.Access, A.DefaultValue, A.Description, A.Width, B.RegisterOffset, B.BitfieldOffset, B.SliceWidth, A.Exist, A.Notes FROM Bitfield AS A JOIN BitfieldRef AS B ON A.id=B.BitfieldId WHERE B.RegisterId="
        self.tableViewBfEnumQuery = "SELECT * FROM BitfieldEnum WHERE BitfieldId="
        
        self.moduleIcon = QIcon('icon/module32.png')
        self.regMapIcon = QIcon('icon/regmap32.png')
        self.regIcon = QIcon('icon/reg32.png')
        self.bfIcon = QIcon('icon/bf32.png')
        self.bfenumIcon = QIcon('icon/bfenum32.png')
        
        self.ui.pbAddRegMap.setIcon(QIcon('icon/add32.png'))
        self.ui.pbAddReg.setIcon(QIcon('icon/add32.png'))
        self.ui.pbAddBf.setIcon(QIcon('icon/add32.png'))
        self.ui.pbAddBfEnum.setIcon(QIcon('icon/add32.png'))
        
        self.newModule = True
        self.fileName = ''
        self.newFileName = ''
        return
    
    def eventFilter(self, obj, event):
        if obj == self.ui.treeView:
            if  event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Delete:
                    self.do_delete_triggered()
        return super(uiModuleWindow, self).eventFilter(obj, event)
    
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
    
    ## general function to add regmap/reg/bf/bf enum row
    #  @param row integer, row index that new row will be
    #  @param r   QSqlRecord, regmap/reg/bf record to add to model
    #  @newNamePrefix string, name prefix for new record
    #  @model model to add new record
    #  @table tatble that model select
    def newRegMap_Reg_Bf_BfEnum_Row(self, row, r, newNamePrefix, model, table):
        if model.rowCount() == 0:
            # find max DisplayOrder value from table, as model data may be just part of table
            query = QSqlQuery("SELECT max(DisplayOrder) FROM %s"%table, self.conn)
            query.next()
            o = query.record().value(0)
            order = 0 if o == '' else int(o) + 1
            exactRow = 0
            model.insertRecord(-1, r)
        elif row >= model.rowCount() or row == -1:
            if row == -1: # current selected node in treeView is from 'table'
                # model may be not matched to current selected node from other table, like "RegMap1" is selected while reg model is matched to "RegMap0"
                query = QSqlQuery("SELECT max(DisplayOrder) FROM %s"%table, self.conn)
                query.next()
                o = query.record().value(0)
                order = 0 if o == '' else int(o) + 1
            else:
                order = model.record(model.rowCount() - 1).value("DisplayOrder") + 1
            exactRow = model.rowCount()
            model.insertRecord(-1, r)
        else:
            order = 0 if row == 0 else model.record(row - 1).value("DisplayOrder") + 1
            exactRow = row
            model.insertRecord(row, r)
        
        query = QSqlQuery(self.conn)
        query.exec_("UPDATE %s SET DisplayOrder=DisplayOrder+1 WHERE DisplayOrder>=%s"%(table, order))          

        id = model.record(exactRow).value("id")
        r.setValue("id", id)
        r.setValue("Name", "%s%s"%(newNamePrefix,id))
        r.setValue("DisplayOrder", order)
        model.setRecord(exactRow, r)
        r = model.record(exactRow)
        model.select()
        return r
    
    def newRegMapRow(self, model, memoryMapId, row):
        r = model.record()
        r.remove(r.indexOf('id'))
        r.setValue("MemoryMapId", memoryMapId)
        r.setValue("OffsetAddress", 0)        
        r.setValue("Name", "RegMap")
        r.setValue("DisplayOrder", -1)
        r = self.newRegMap_Reg_Bf_BfEnum_Row(row, r, "RegMap", model, "RegisterMap")
        return r
        
    def newRegRow(self, model, regMapId, OffsetAddress, Width, row):
        r = model.record()
        r.remove(r.indexOf('id'))
        r.setValue("RegisterMapId", regMapId)
        r.setValue("Description", "This is no name register")
        r.setValue("OffsetAddress", OffsetAddress)
        r.setValue("Width", Width)
        r.setValue("Name", "Reg")
        r.setValue("DisplayOrder", -1)
        r = self.newRegMap_Reg_Bf_BfEnum_Row(row, r, "Reg", model, "Register")
        return r
    
    def newBfRow(self, model, bfRefModel, regId, memMapId, Width, row):                
        r = model.record()
        r.remove(r.indexOf('id'))
        r.setValue("MemoryMapId", memMapId)
        r.setValue("Width", Width)
        r.setValue("Description", "This is no name bitfield")
        r.setValue("Name", "Bf")
        r.setValue("DisplayOrder", -1)    
        r = self.newRegMap_Reg_Bf_BfEnum_Row(row, r, "Bf", model, "Bitfield")
        
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
    
    def newBfEnumRow(self, model, bfId, row):
        r = model.record()
        r.remove(r.indexOf('id'))
        r.setValue("BitfieldId", bfId)
        r.setValue("Description", "This is no name enum")
        r.setValue("Value", 0)
        r.setValue("Name", "BfEnum")
        r.setValue("DisplayOrder", -1)    
        r = self.newRegMap_Reg_Bf_BfEnum_Row(row, r, "BfEnum", model, "BitfieldEnum")
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
            regMap0Id = self.newRegMapRow(self.regMapTableModel, memoryMap0Id, -1).value("id")  # create regmap row0
            reg0Id = self.newRegRow(self.regTableModel, regMap0Id, 0, 8, -1).value("id")        # create register row0
            reg1Id = self.newRegRow(self.regTableModel, regMap0Id, 0, 8, -1).value("id")        # create register row1
            bf0Id = self.newBfRow(self.bfTableModel, self.bfRefTableModel, reg0Id, memoryMap0Id, 8, -1).value("id") # create bitfield row0
            bf1Id = self.newBfRow(self.bfTableModel, self.bfRefTableModel, reg1Id, memoryMap0Id, 8, -1).value("id") # create bitfield row1
            bfEnum0Id = self.newBfEnumRow(self.bfEnumTableModel, bf0Id, -1).value("id")         # create bitfieldenum row0
            self.__setupTreeView()
            self.regMapTableModel.dataChanged.connect(self.do_tableView_dataChanged)
            self.regTableModel.dataChanged.connect(self.do_tableView_dataChanged)
            self.bfQueryModel.dataChanged.connect(self.do_tableView_dataChanged)
            self.bfEnumTableModel.dataChanged.connect(self.do_tableView_dataChanged)
        else:
            False
        return True
        
    def openDatabase(self, fileName):
        # create temp database
        now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%_S_%f')
        newName = "__temp_module_%s.db"%now
        shutil.copyfile(fileName, newName)
        self.newFileName = newName
        self.fileName = fileName
        self.newModule = False
        if self.__setupModel(newName):
            self.__setupTreeView()
            self.regMapTableModel.dataChanged.connect(self.do_tableView_dataChanged)
            self.regTableModel.dataChanged.connect(self.do_tableView_dataChanged)
            self.bfQueryModel.dataChanged.connect(self.do_tableView_dataChanged)
            self.bfEnumTableModel.dataChanged.connect(self.do_tableView_dataChanged)     
        else:
            return False
        return True
    
    def saveDatabase(self):
        fileName = ''
        if self.newModule == True:
            fileName, filterUsed = QFileDialog.getSaveFileName(self, "Save register file", QDir.homePath(), "Register Files (*)", "(*.*)")
            if fileName !='':
                if os.path.exists(fileName):
                    os.remove(fileName)
                shutil.copy(self.newFileName, fileName)
                self.fileName = fileName
                self.newModule = False
        else:
            if self.newFileName != '':
                if os.path.exists(fileName):
                    os.remove(fileName)
                shutil.copy(self.newFileName, self.fileName)
                fileName = self.fileName
        return fileName
    
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
            
            self.regMapTableModel = QCustomizedSqlTableModel(self, self.conn)
            self.regMapTableModel.setEditStrategy(QSqlTableModel.OnFieldChange)  
            self.regMapTableModel.setTable("RegisterMap")
            self.regMapTableModel.setSort(self.regMapTableModel.fieldIndex("DisplayOrder"), Qt.AscendingOrder)
            self.regMapTableModel.select()
            
            self.regTableModel = QCustomizedSqlTableModel(self, self.conn)
            self.regTableModel.setEditStrategy(QSqlTableModel.OnFieldChange)  
            self.regTableModel.setTable("Register")
            self.regTableModel.setSort(self.regTableModel.fieldIndex("DisplayOrder"), Qt.AscendingOrder)
            self.regTableModel.select()
            
            self.bfRefTableModel = QSqlTableModel(self, self.conn)
            self.bfRefTableModel.setEditStrategy(QSqlTableModel.OnFieldChange)
            self.bfRefTableModel.setTable("BitfieldRef")
            self.bfRefTableModel.select()
            
            self.bfTableModel = QCustomizedSqlTableModel(self, self.conn)
            self.bfTableModel.setEditStrategy(QSqlTableModel.OnFieldChange) 
            self.bfTableModel.setTable("Bitfield")
            self.bfTableModel.setSort(self.bfTableModel.fieldIndex("DisplayOrder"), Qt.AscendingOrder)
            self.bfTableModel.select()
            
            self.bfEnumTableModel = QCustomizedSqlTableModel(self, self.conn)
            self.bfEnumTableModel.setEditStrategy(QSqlTableModel.OnFieldChange) 
            self.bfEnumTableModel.setTable("BitfieldEnum")
            self.bfEnumTableModel.setSort(self.bfEnumTableModel.fieldIndex("DisplayOrder"), Qt.AscendingOrder)
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
            self.memoryMapItem = QStandardItem(self.moduleIcon, "MemoryMap")
            self.memoryMapItem.setData("MemoryMap", self.treeViewItemTableNameRole)
            self.memoryMapItem.setData(memoryMapRecord.value("id"), self.treeViewItemMemoryMapIdRole)
            root.appendRow(self.memoryMapItem)
            
            # register map
            regMapQueryModel = QSqlQueryModel()
            regMapQueryModel.setQuery("SELECT * FROM RegisterMap WHERE memoryMapId=%s ORDER BY DisplayOrder ASC"%memoryMapRecord.value("id"), self.conn)
            for i in range(regMapQueryModel.rowCount()):
                regMapRecord = regMapQueryModel.record(i)
                regMapitem = QStandardItem(self.regMapIcon, regMapRecord.value("name"))
                regMapitem.setData("RegisterMap", self.treeViewItemTableNameRole)
                regMapitem.setData(memoryMapRecord.value("id"), self.treeViewItemMemoryMapIdRole)
                regMapitem.setData(regMapRecord.value("id"), self.treeViewItemRegMapIdRole)
                self.memoryMapItem.appendRow(regMapitem)
                if QSqlBitfieldTableModel.exist(regMapRecord) == False:
                    regMapitem.setData(QColor('grey'), Qt.BackgroundColorRole)
                
                # register
                regQueryModel = QSqlQueryModel()
                regQueryModel.setQuery("SELECT * FROM Register WHERE RegisterMapId=%s ORDER BY DisplayOrder ASC"%regMapRecord.value("id"), self.conn)
                for j in range(regQueryModel.rowCount()):
                    regRecord = regQueryModel.record(j)
                    regItem = QStandardItem(self.regIcon, regRecord.value("name"))
                    regItem.setData("Register", self.treeViewItemTableNameRole)
                    regItem.setData(memoryMapRecord.value("id"), self.treeViewItemMemoryMapIdRole)
                    regItem.setData(regMapRecord.value("id"), self.treeViewItemRegMapIdRole)
                    regItem.setData(regRecord.value("id"), self.treeViewItemRegIdRole)
                    regMapitem.appendRow(regItem)
                    if QSqlBitfieldTableModel.exist(regRecord) == False:
                        regItem.setData(QColor('grey'), Qt.BackgroundColorRole)
                        
                    # bitfield
                    bfQueryModel = QSqlQueryModel()
                    bfQueryModel.setQuery("SELECT * FROM Bitfield WHERE EXISTS (SELECT * FROM BitfieldRef WHERE Bitfield.id=BitfieldRef.BitfieldId AND BitfieldRef.RegisterId=%s) ORDER BY DisplayOrder ASC"%regRecord.value("id"), self.conn)
                    for k in range(bfQueryModel.rowCount()):
                        bfRecord = bfQueryModel.record(k)
                        bfItem = QStandardItem(self.bfIcon, bfRecord.value("name"))
                        bfItem.setData("Bitfield", self.treeViewItemTableNameRole)
                        bfItem.setData(memoryMapRecord.value("id"), self.treeViewItemMemoryMapIdRole)
                        bfItem.setData(regMapRecord.value("id"), self.treeViewItemRegMapIdRole)
                        bfItem.setData(regRecord.value("id"), self.treeViewItemRegIdRole)
                        bfItem.setData(bfRecord.value("id"), self.treeViewItemBfIdRole)
                        regItem.appendRow(bfItem)
                        if QSqlBitfieldTableModel.exist(bfRecord) == False:
                            bfItem.setData(QColor('grey'), Qt.BackgroundColorRole)
                            
                        #bitfield enum
                        bfEnumQueryModel = QSqlQueryModel()
                        bfEnumQueryModel.setQuery("SELECT * FROM BitfieldEnum WHERE BitfieldId=%s ORDER BY DisplayOrder ASC"%bfRecord.value("id"), self.conn)
                        for j in range(bfEnumQueryModel.rowCount()):
                            bfEnumRecord = bfEnumQueryModel.record(j)
                            bfEnumItem = QStandardItem(self.bfenumIcon, bfEnumRecord.value("name"))
                            bfEnumItem.setData("BitfieldEnum", self.treeViewItemTableNameRole)
                            bfEnumItem.setData(memoryMapRecord.value("id"), self.treeViewItemMemoryMapIdRole)
                            bfEnumItem.setData(regMapRecord.value("id"), self.treeViewItemRegMapIdRole)
                            bfEnumItem.setData(regRecord.value("id"), self.treeViewItemRegIdRole)
                            bfEnumItem.setData(bfRecord.value("id"), self.treeViewItemBfIdRole)
                            bfEnumItem.setData(bfEnumRecord.value("id"), self.treeViewItemBfEnumIdRole)
                            bfItem.appendRow(bfEnumItem)
                            if QSqlBitfieldTableModel.exist(bfEnumRecord) == False:
                                bfEnumItem.setData(QColor('grey'), Qt.BackgroundColorRole)
                                
        # show tree view nodes
        self.ui.treeView.setModel(self.standardModel)
        self.ui.treeView.expandAll()

        # connect slots
        treeViewSelectionModel = self.ui.treeView.selectionModel()
        treeViewSelectionModel.currentChanged.connect(self.do_treeView_currentChanged)

        self.ui.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.treeView.customContextMenuRequested.connect(self.do_treeView_contextMenuRequested)
        
        # select memory map node
        memoryMapItemIndex = self.standardModel.indexFromItem(self.memoryMapItem)
        treeViewSelectionModel.select(memoryMapItemIndex, QItemSelectionModel.ClearAndSelect)
        self.do_treeView_currentChanged(memoryMapItemIndex, None)
        
    @Slot('QItemSelection', 'QItemSelection')
    def do_tableView_selectionChanged(self, selected, deselected):
        return
    
    @Slot()
    def do_treeView_contextMenuRequested(self, point):
        index = self.ui.treeView.indexAt(point)
        tableName = str(index.data(self.treeViewItemTableNameRole))
        
        self.treeViewPopMenu = QMenu(self)
        addRegMapAction = QAction("+ RegMap", self)
        addRegAction = QAction("+ Reg", self)
        addBfAction = QAction("+ Bitfield", self)
        addBfEnumAction = QAction("+ Bitfield Enum", self)
        
        if tableName == "MemoryMap":
            self.treeViewPopMenu.addAction(addRegMapAction)
            addRegMapAction.triggered.connect(self.on_pbAddRegMap_clicked)
        elif tableName == "RegisterMap":
            self.treeViewPopMenu.addAction(addRegMapAction)
            addRegMapAction.triggered.connect(self.on_pbAddRegMap_clicked)
            self.treeViewPopMenu.addAction(addRegAction)
            addRegAction.triggered.connect(self.on_pbAddReg_clicked)
        elif tableName == "Register":
            self.treeViewPopMenu.addAction(addRegMapAction)
            addRegMapAction.triggered.connect(self.on_pbAddRegMap_clicked)
            self.treeViewPopMenu.addAction(addRegAction)
            addRegAction.triggered.connect(self.on_pbAddReg_clicked)
            self.treeViewPopMenu.addAction(addBfAction)
            addBfAction.triggered.connect(self.on_pbAddBf_clicked)
        elif tableName == "Bitfield":
            self.treeViewPopMenu.addAction(addRegMapAction)
            addRegMapAction.triggered.connect(self.on_pbAddRegMap_clicked)
            self.treeViewPopMenu.addAction(addRegAction)
            addRegAction.triggered.connect(self.on_pbAddReg_clicked)
            self.treeViewPopMenu.addAction(addBfAction)
            addBfAction.triggered.connect(self.on_pbAddBf_clicked)
            self.treeViewPopMenu.addAction(addBfEnumAction)
            addBfEnumAction.triggered.connect(self.on_pbAddBfEnum_clicked)
        elif tableName == "BitfieldEnum":
            self.treeViewPopMenu.addAction(addRegMapAction)
            addRegMapAction.triggered.connect(self.on_pbAddRegMap_clicked)
            self.treeViewPopMenu.addAction(addRegAction)
            addRegAction.triggered.connect(self.on_pbAddReg_clicked)
            self.treeViewPopMenu.addAction(addBfAction)
            addBfAction.triggered.connect(self.on_pbAddBf_clicked)
            self.treeViewPopMenu.addAction(addBfEnumAction)
            addBfEnumAction.triggered.connect(self.on_pbAddBfEnum_clicked)
        self.treeViewPopMenu.addSeparator()
        delAction = QAction("Delete", self)
        self.treeViewPopMenu.addAction(delAction)
        delAction.triggered.connect(self.do_delete_triggered)
        
        menuPosition = self.ui.treeView.viewport().mapToGlobal(point)
        self.treeViewPopMenu.move(menuPosition)
        self.treeViewPopMenu.show()
    
    @Slot()
    def do_tableView_dataChanged(self, topLeft, bottomRight, roles):
        current = self.ui.treeView.selectedIndexes().pop()
        tableName = str(current.data(self.treeViewItemTableNameRole))
        
        model = None
        idRole = None
        if tableName == "RegisterMap":
            model = self.regMapTableModel
            idRole = self.treeViewItemRegMapIdRole
        elif tableName == "Register":
            model = self.regTableModel
            idRole = self.treeViewItemRegIdRole
        elif tableName == "Bitfield":
            model = self.bfQueryModel
            idRole = self.treeViewItemBfIdRole
        elif tableName == "BitfieldEnum":
            model = self.bfEnumTableModel
            idRole = self.treeViewItemBfEnumIdRole
        
        # update display name field of tree node to latest "Name" field
        if model != None:
            fieldName = model.record().fieldName(bottomRight.column())
            if fieldName == "Name":
                itemId = model.data(model.index(bottomRight.row(), 0), Qt.DisplayRole)
                parentItem = self.standardModel.itemFromIndex(current.parent())
                for i in range(parentItem.rowCount()):
                    child = current.sibling(i, 0)
                    childId = child.data(idRole)
                    if childId != None and int(childId) == itemId:
                        newName = model.record(bottomRight.row()).value("Name")
                        self.standardModel.itemFromIndex(child).setData(newName, Qt.DisplayRole)
            elif fieldName == "Exist":
                itemId = model.data(model.index(bottomRight.row(), 0), Qt.DisplayRole) # 'id' is column 0
                parentItem = self.standardModel.itemFromIndex(current.parent())
                for i in range(parentItem.rowCount()):
                    child = current.sibling(i, 0)
                    childId = child.data(idRole)
                    if childId != None and int(childId) == itemId:
                        if QSqlBitfieldTableModel.exist(model.record(bottomRight.row())) == False:
                            self.standardModel.itemFromIndex(child).setData(QColor('grey'), Qt.BackgroundColorRole)
                        else:
                            self.standardModel.itemFromIndex(child).setData(None, Qt.BackgroundColorRole)
        self.ui.tableView.resizeColumnsToContents()
        return
    
    @Slot()
    def do_treeView_currentChanged(self, current, previous):
        tableName = str(current.data(self.treeViewItemTableNameRole))

        if tableName == "MemoryMap": # memorymap selected, show memorymap table
            self.ui.tableView.setModel(self.memoryMaptableModel)
            self.ui.tableView.selectionModel().selectionChanged.connect(self.do_tableView_selectionChanged)
            self.ui.tableView.hideColumn(0) # id
            self.ui.tableView.showColumn(1) # offset address
            self.ui.tableView.showColumn(2) # notes
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
            self.ui.tableView.hideColumn(2) # order
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
            self.ui.tableView.hideColumn(2) # order
            self.ui.tableView.resizeColumnsToContents()
            
            self.ui.pbAddRegMap.setEnabled(True)
            self.ui.pbAddReg.setEnabled(True)
            self.ui.pbAddBf.setEnabled(True)
            self.ui.pbAddBfEnum.setEnabled(False)
            self.ui.labelDescription.setText("Tips: Click <font color=\"red\">%s</font> to add new register. "%self.ui.pbAddReg.text())
            
        elif tableName == "Bitfield": # bf selected, show bf table
            regId = int(current.data(self.treeViewItemRegIdRole))
            self.bfQueryModel.setQuery("%s%s ORDER BY A.DisplayOrder ASC"%(self.tableViewBfQuery, regId), self.conn)
            self.ui.tableView.setModel(self.bfQueryModel)
            
            self.ui.tableView.selectionModel().selectionChanged.connect(self.do_tableView_selectionChanged)
            self.ui.tableView.hideColumn(0) # id
            self.ui.tableView.hideColumn(1) # regid
            self.ui.tableView.hideColumn(2) # order
            self.ui.tableView.resizeColumnsToContents()
            
            self.ui.pbAddRegMap.setEnabled(True)
            self.ui.pbAddReg.setEnabled(True)
            self.ui.pbAddBf.setEnabled(True)
            self.ui.pbAddBfEnum.setEnabled(True)
            self.ui.labelDescription.setText("Tips: Click <font color=\"red\">%s</font> to add new bitfield. "%self.ui.pbAddBf.text())
            
        elif tableName == "BitfieldEnum": # bfenum selected, show bfenum table
            bfId = int(current.data(self.treeViewItemBfIdRole))            
            self.bfEnumTableModel.setFilter("BitfieldId=%s"%bfId)
            self.bfEnumTableModel.select()
            self.ui.tableView.setModel(self.bfEnumTableModel)
            self.ui.tableView.selectionModel().selectionChanged.connect(self.do_tableView_selectionChanged)
            self.ui.tableView.hideColumn(0) # id
            self.ui.tableView.hideColumn(1) # bfid
            self.ui.tableView.hideColumn(2) # order
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
        newRegMapRowIndex = -1 if tableName != "RegisterMap" else current.row() + 1
        r = self.newRegMapRow(self.regMapTableModel, memoryMapId, newRegMapRowIndex)
        
        newRegMapItem = QStandardItem(self.regMapIcon, r.value("name"))
        newRegMapItem.setData("RegisterMap", self.treeViewItemTableNameRole)
        newRegMapItem.setData(memoryMapId, self.treeViewItemMemoryMapIdRole)
        newRegMapItem.setData(r.value("id"), self.treeViewItemRegMapIdRole)
        
        standardItem = self.standardModel.itemFromIndex(current)
        if tableName == "MemoryMap":
            standardItem.appendRow(newRegMapItem)
        elif tableName == "RegisterMap":
            if (current.row() + 1) == standardItem.parent().rowCount(): # current is last one
                standardItem.parent().appendRow(newRegMapItem)
                item = standardItem.parent().child(current.row() + 1)
                self.ui.treeView.selectionModel().setCurrentIndex(item.index(), QItemSelectionModel.ClearAndSelect)
            else:
                standardItem.parent().insertRows(current.row() + 1, 1)
                standardItem.parent().setChild(current.row() + 1, newRegMapItem)
                item = standardItem.parent().child(current.row() + 1)
                self.ui.treeView.selectionModel().setCurrentIndex(item.index(), QItemSelectionModel.ClearAndSelect)
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
        newRegRowIndex = -1 if tableName != "Register" else current.row() + 1        
        r = self.newRegRow(self.regTableModel, regMapId, 0, 8, newRegRowIndex)
        
        newRegItem = QStandardItem(self.regIcon, r.value("name"))
        newRegItem.setData("Register", self.treeViewItemTableNameRole)
        newRegItem.setData(memoryMapId, self.treeViewItemMemoryMapIdRole)
        newRegItem.setData(regMapId, self.treeViewItemRegMapIdRole)
        newRegItem.setData(r.value("id"), self.treeViewItemRegIdRole)
        
        standardItem = self.standardModel.itemFromIndex(current)
        if tableName == "RegisterMap":
            standardItem.appendRow(newRegItem)
        elif tableName == "Register":
            if (current.row() + 1) == standardItem.parent().rowCount(): # current is last one
                standardItem.parent().appendRow(newRegItem)
                item = standardItem.parent().child(current.row() + 1)
                self.ui.treeView.selectionModel().setCurrentIndex(item.index(), QItemSelectionModel.ClearAndSelect)
            else:
                standardItem.parent().insertRows(current.row() + 1, 1)
                standardItem.parent().setChild(current.row() + 1, newRegItem)
                item = standardItem.parent().child(current.row() + 1)
                self.ui.treeView.selectionModel().setCurrentIndex(item.index(), QItemSelectionModel.ClearAndSelect)
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
        newBfRowIndex = -1 if tableName != "Bitfield" else current.row() + 1 
        r = self.newBfRow(self.bfTableModel, self.bfRefTableModel, regId, memoryMapId, 8, newBfRowIndex)
        
        newBfItem = QStandardItem(self.bfIcon, r.value("name"))
        newBfItem.setData("Bitfield", self.treeViewItemTableNameRole)
        newBfItem.setData(memoryMapId, self.treeViewItemMemoryMapIdRole)
        newBfItem.setData(regMapId, self.treeViewItemRegMapIdRole)
        newBfItem.setData(regId, self.treeViewItemRegIdRole)
        newBfItem.setData(r.value("id"), self.treeViewItemBfIdRole)
        
        standardItem = self.standardModel.itemFromIndex(current)
        if tableName == "Register":
            standardItem.appendRow(newBfItem)
        elif tableName == "Bitfield":
            if (current.row() + 1) == standardItem.parent().rowCount(): # current is last one
                standardItem.parent().appendRow(newBfItem)
                item = standardItem.parent().child(current.row() + 1)
                self.ui.treeView.selectionModel().setCurrentIndex(item.index(), QItemSelectionModel.ClearAndSelect)
            else:
                standardItem.parent().insertRows(current.row() + 1, 1)
                standardItem.parent().setChild(current.row() + 1, newBfItem)
                item = standardItem.parent().child(current.row() + 1)
                self.ui.treeView.selectionModel().setCurrentIndex(item.index(), QItemSelectionModel.ClearAndSelect)
            self.bfQueryModel.setQuery("%s%s ORDER BY A.DisplayOrder ASC"%(self.tableViewBfQuery, regId), self.conn)
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
        newBfEnumRowIndex = -1 if tableName != "BitfieldEnum" else current.row() + 1
        r = self.newBfEnumRow(self.bfEnumTableModel, bfId, newBfEnumRowIndex)
        
        newBfEnumItem = QStandardItem(self.bfenumIcon, r.value("name"))
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
            if (current.row() + 1) == standardItem.parent().rowCount(): # current is last one
                standardItem.parent().appendRow(newBfEnumItem)
                item = standardItem.parent().child(current.row() + 1)
                self.ui.treeView.selectionModel().setCurrentIndex(item.index(), QItemSelectionModel.ClearAndSelect)
            else:
                standardItem.parent().insertRows(current.row() + 1, 1)
                standardItem.parent().setChild(current.row() + 1, newBfEnumItem)
                item = standardItem.parent().child(current.row() + 1)
                self.ui.treeView.selectionModel().setCurrentIndex(item.index(), QItemSelectionModel.ClearAndSelect)
        return
    
    @Slot()
    def do_delete_triggered(self):
        current = self.ui.treeView.selectedIndexes().pop()
        tableName = str(current.data(self.treeViewItemTableNameRole))
        
        # remove from table
        if tableName == "RegisterMap":
            regMapId = int(current.data(self.treeViewItemRegMapIdRole))
            for i in range(self.regMapTableModel.rowCount()):
                if self.regMapTableModel.record(i).value("id") == regMapId:
                    self.regMapTableModel.removeRows(i, 1)
                    break
            self.regMapTableModel.select()
        elif tableName == "Register":
            regId = int(current.data(self.treeViewItemRegIdRole))
            for i in range(self.regTableModel.rowCount()):
                if self.regTableModel.record(i).value("id") == regId:
                    self.regTableModel.removeRows(i, 1)
                    break
            self.regTableModel.select()
        elif tableName == "Bitfield":
            bfId = int(current.data(self.treeViewItemBfIdRole))
            for i in range(self.bfTableModel.rowCount()):
                if self.bfTableModel.record(i).value("id") == bfId:
                    self.bfTableModel.removeRows(i, 1)
                    break
            self.bfTableModel.select()
        elif tableName == "BitfieldEnum":
            bfEnumId = int(current.data(self.treeViewItemBfEnumIdRole))
            for i in range(self.bfEnumTableModel.rowCount()):
                if self.bfEnumTableModel.record(i).value("id") == bfEnumId:
                    self.bfEnumTableModel.removeRows(i, 1)
                    break
            self.bfEnumTableModel.select()
        
        # remove from tree
        if tableName != "MemoryMap":
            parentItem = self.standardModel.itemFromIndex(current.parent())
            parentItem.removeRow(current.row())
        
        return