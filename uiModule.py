import os
import shutil
import datetime

from PySide2.QtWidgets import QWidget, QAbstractItemView, QMessageBox, QMenu, QAction, QFileDialog, QProgressDialog
from PySide2.QtCore import Qt, Slot, QItemSelectionModel, QSize, QEvent, QDir, QFile, QUrl, QDir
from PySide2.QtGui import QStandardItemModel, QStandardItem, QIcon, QColor
from PySide2.QtSql import QSqlDatabase, QSqlTableModel, QSqlQueryModel, QSqlRecord, QSqlQuery
from PySide2.QtXmlPatterns import QXmlQuery, QXmlSerializer, QXmlResultItems
from PySide2.QtXml import QDomDocument, QDomNodeList
from xml.etree import ElementTree
from ui.Module import Ui_ModuleWindow
from RegisterConst import RegisterConst
from QSqlQueryBfTableModel import QSqlQueryBfTableModel
from QSqlHighlightTableModel import QSqlHighlightTableModel, QRegValueDisplayDelegate
from QRegDebugTableModel import QRegDebugTableModel

class uiModuleWindow(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ModuleWindow()
        self.ui.setupUi(self)
        self.ui.pbSetColumns.setVisible(False)
        self.ui.pbReadAll.setVisible(False)
        self.ui.pbReadSelected.setVisible(False)
        self.ui.pbWriteAll.setVisible(False)
        self.ui.treeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.treeView.installEventFilter(self)
        self.ui.tableView.setAlternatingRowColors(True)
        self.ui.tableViewReg.setAlternatingRowColors(True)
        self.ui.tableViewReg.setVisible(False)
        with open (RegisterConst.StyleFile) as file:
            style = file.read()
        self.setStyleSheet(style)

        self.tableDesignViewBfQuerySql = "SELECT A.id, B.RegisterId, A.DisplayOrder, A.Name, A.Access, A.DefaultValue, A.Description, " \
                                         "A.Width, B.RegisterOffset, A.Exist, A.Notes " \
                                         "FROM Bitfield AS A JOIN BitfieldRef AS B ON A.id=B.BitfieldId WHERE B.RegisterId="
        
        self.moduleIcon = QIcon('icon/module32.png')
        self.regMapIcon = QIcon('icon/regmap32.png')
        self.regIcon = QIcon('icon/reg32.png')
        self.bfIcon = QIcon('icon/bf32.png')
        self.bfenumIcon = QIcon('icon/bfenum32.png')
        
        self.ui.pbAddRegMap.setIcon(QIcon('icon/add32.png'))
        self.ui.pbAddReg.setIcon(QIcon('icon/add32.png'))
        self.ui.pbAddBf.setIcon(QIcon('icon/add32.png'))
        self.ui.pbAddBfEnum.setIcon(QIcon('icon/add32.png'))

        self.ui.pbReadAll.setIcon(QIcon('icon/rdall32.png'))
        self.ui.pbReadSelected.setIcon(QIcon('icon/rdsel32.png'))
        self.ui.pbWriteAll.setIcon(QIcon('icon/wrall32.png'))
        
        # default as design view, no matter it is a new module or just opened module
        self.view = RegisterConst.DesignView
        
        # default as new module
        self.newModule = True
        self.fileName = ''
        self.newFileName = ''

        # default value
        self.__treeViewCurrentTable = None # selected table by treeView
        self.__treeViewCurrentRow = None   # curent row index on treeView
        self.__regMapTypeIndex = None      # regmap table 'Type' column index which should be hidden, while this column should be visible for other tables
        return
    
    def eventFilter(self, obj, event):
        if obj == self.ui.treeView:
            if  event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Delete:
                    self.do_delete_triggered()
        return super(uiModuleWindow, self).eventFilter(obj, event)
    
    def closeEvent(self, event):
        if self.newModule == True:
            reply = QMessageBox.information(self, "Save register ?", "Register design is created but never saved, do you want to save?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.mainWindow.on_actionSave_triggered()
        self.conn.close()
        if os.path.isfile(self.newFileName):
            os.remove(self.newFileName)
        event.accept()

    def setMainWindow(self, mainWindow):
        self.mainWindow = mainWindow

    def setView(self, view):
        if (view != self.view):
            self.view = view
            isDebugView = (self.view == RegisterConst.DebugView)
            self.ui.pbAddRegMap.setVisible(not isDebugView)
            self.ui.pbAddReg.setVisible(not isDebugView)
            self.ui.pbAddBf.setVisible(not isDebugView)
            self.ui.pbAddBfEnum.setVisible(not isDebugView)
            self.ui.labelDescription.setVisible(not isDebugView)
            self.ui.tableView.setAlternatingRowColors(not isDebugView)
            self.ui.tableView.setVisible(isDebugView or ((not isDebugView) and (self.__treeViewCurrentTable != "Register")))
            self.ui.tableViewReg.setVisible((not isDebugView) and (self.__treeViewCurrentTable == "Register"))
            self.ui.pbReadAll.setVisible(isDebugView)
            self.ui.pbReadSelected.setVisible(isDebugView)
            self.ui.pbWriteAll.setVisible(isDebugView)
            if (self.view == RegisterConst.DebugView):
                self.setupDebugViewModels()    
            self.do_treeView_currentChanged(self.ui.treeView.selectedIndexes().pop(), None)

    def newInfoRow(self, model, updateDate):
        r = model.record()
        r.remove(r.indexOf('id'))
        r.setValue("version", RegisterConst.Version)
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
        if newNamePrefix != None:
            r.setValue("Name", "%s%s"%(newNamePrefix,id))
        r.setValue("DisplayOrder", order)
        model.setRecord(exactRow, r)
        r = model.record(exactRow)
        model.select()
        return r
    
    def newRegMapRow(self, model, memoryMapId, row, type = RegisterConst.RegMap, name = None):
        r = model.record()
        r.remove(r.indexOf('id'))
        r.setValue("MemoryMapId", memoryMapId)
        r.setValue("OffsetAddress", 0)
        r.setValue("Type", type)
        if name == None:
            namePrefix = "RegMap" if type == RegisterConst.RegMap else "RegMod"
            r.setValue("Name", namePrefix)
        else:
            namePrefix = None
            r.setValue("Name", name)
        r.setValue("DisplayOrder", -1)
        r = self.newRegMap_Reg_Bf_BfEnum_Row(row, r, namePrefix, model, "RegisterMap")
        return r

    def newRegRow(self, model, regMapId, OffsetAddress, Width, row):
        r = model.record()
        r.remove(r.indexOf('id'))
        r.setValue("RegisterMapId", regMapId)
        r.setValue("Description", "This is no name register")
        r.setValue("OffsetAddress", OffsetAddress)
        r.setValue("Value", 0)
        r.setValue("Width", Width)
        r.setValue("Name", "Reg")
        r.setValue("DisplayOrder", -1)
        r = self.newRegMap_Reg_Bf_BfEnum_Row(row, r, "Reg", model, "Register")
        return r

    def newBfRow(self, model, regId, Width, row):                
        r = model.record()
        r.remove(r.indexOf('id'))
        r.setValue("RegisterId", regId)
        r.setValue("Access", "r/w")
        r.setValue("DefaultValue", 0)
        r.setValue("RegisterOffset", 0)
        r.setValue("Width", Width)
        r.setValue("Description", "This is no name bitfield")
        r.setValue("Value", 0)
        r.setValue("Name", "Bf")
        r.setValue("DisplayOrder", -1)    
        r = self.newRegMap_Reg_Bf_BfEnum_Row(row, r, "Bf", model, "Bitfield")
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
        now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
        newName = "__%s%s"%(now, RegisterConst.DesignFileExt)
        newName = QDir.homePath() + "/.reg/" + newName        
        shutil.copyfile("template/module_template.db", newName)
        self.newFileName = newName
        self.newModule = True
        
        # open new database
        self.regDebugModels = [] # debug model is a list, each member is mapped to a regmap
        if self.setupDesignViewModels(newName):
            self.newInfoRow(self.infoTableModel, now).value("id")                 # create info   row0
            memMap0Id = self.newMemoryMapRow(self.memMaptableModel).value("id")   # create memmap row0
            regMap0Id = self.newRegMapRow(self.regMapTableModel, memMap0Id, -1).value("id") # create regmap row0
            reg0Id = self.newRegRow(self.regTableModel, regMap0Id, 0, 32, -1).value("id")   # create register row0
            bf0Id = self.newBfRow(self.bfTableModel, reg0Id, 8, -1).value("id") # create bitfield row0
            self.newBfEnumRow(self.bfEnumTableModel, bf0Id, -1).value("id")     # create bitfieldenum row0
            self.setupTreeView()
            self.regMapTableModel.dataChanged.connect(self.do_tableView_dataChanged)
            self.regTableModel.dataChanged.connect(self.do_tableView_dataChanged)
            self.bfTableModel.dataChanged.connect(self.do_tableView_dataChanged)
            self.bfEnumTableModel.dataChanged.connect(self.do_tableView_dataChanged)
        else:
            return False
        return True
        
    def openDatabase(self, fileName):
        # create temp database
        now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
        newName = "__%s%s"%(now, RegisterConst.DesignFileExt)
        newName = QDir.homePath() + "/.reg/" + newName  
        shutil.copyfile(fileName, newName)
        self.newFileName = newName
        self.fileName = fileName
        self.newModule = False

        # open existing database
        self.regDebugModels = [] # debug model is a list, each member is mapped to a regmap
        if self.setupDesignViewModels(newName):
            self.setupTreeView()
            self.regMapTableModel.dataChanged.connect(self.do_tableView_dataChanged)
            self.regTableModel.dataChanged.connect(self.do_tableView_dataChanged)
            self.bfTableModel.dataChanged.connect(self.do_tableView_dataChanged)
            self.bfEnumTableModel.dataChanged.connect(self.do_tableView_dataChanged)     
        else:
            return False
        return True
    
    def saveDatabase(self):
        fileName = ''
        if self.newModule == True:
            fileName, filterUsed = QFileDialog.getSaveFileName(self, "Save register file", QDir.homePath(), "Register File (*%s)"%RegisterConst.DesignFileExt)
            if fileName !='':
                if os.path.exists(fileName):                                        
                    os.remove(fileName)
                else:
                    f_name, f_ext = os.path.splitext(fileName)
                    # add .reg when saving new file
                    if f_ext != RegisterConst.DesignFileExt:
                        fileName += RegisterConst.DesignFileExt
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
    
    def importYodaSp1(self, fileName):
        # create temp database
        now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
        newName = "__%s%s"%(now, RegisterConst.DesignFileExt)
        newName = QDir.homePath() + "/.reg/" + newName   
        shutil.copyfile("template/module_template.db", newName)
        self.newFileName = newName
        self.newModule = True  

        # import .sp1 file
        self.regDebugModels = [] # debug model is a list, each member is mapped to a regmap
        if self.setupDesignViewModels(newName):
            infoId = self.newInfoRow(self.infoTableModel, now).value("id")

            # find root
            sp1 = ElementTree.parse(fileName)
            root = sp1.getroot()
    
            # find memory map
            memMapNodes = root.findall('MemoryMap')
            if len(memMapNodes) == 0:
                QMessageBox.warning(self, "Error", "Unable to find memory map", QMessageBox.Yes)
                if os.path.isfile(self.newFileName):
                    os.remove(self.newFileName)
                return False

            # start to import
            regMapDisplayOrder = 0
            regDisplayOrder = 0
            bfDisplayOrder = 0
            query = QSqlQuery(self.conn)
            for memMap in memMapNodes: # actually only 1 memory map node in yoda file, no need to loop
                # add memory record
                memMapAddr = root.find("Properties/Address").text.lower().replace("'h", "0x").replace("'d", "")
                query.exec_("INSERT INTO MemoryMap (OffsetAddress) VALUES ('%s')"%(memMapAddr))
                query.exec_("SELECT max(id) FROM MemoryMap")
                query.next()
                memMapId = query.record().value(0)

                # import regmap/reg/bf
                bfNodes = memMap.findall("BitFields/BitField")
                bfUIDs  = memMap.findall("BitFields/BitField/UID")
                regMapNodes = memMap.findall("RegisterMaps/RegisterMap")

                # prepare progress dialog
                dlgProgress = QProgressDialog("Importing %s ..."%fileName, "Cancel", 0, len(regMapNodes), self)
                dlgProgress.setWindowTitle("Importing...")
                dlgProgress.setWindowModality(Qt.WindowModal)

                for i in range(len(regMapNodes)):
                    regMapNode = regMapNodes[i]
                    regMapName = regMapNode.find("Name").text
                    regMapDesc = regMapNode.find("Description").text
                    regMapAddr = regMapNode.find("Address").text.lower().replace("'h", "0x").replace("'d", "")
                    query.exec_("INSERT INTO RegisterMap (MemoryMapId, DisplayOrder, Name, Description, OffsetAddress) " \
                                "VALUES ('%s', '%s', '%s', '%s', '%s')"%(memMapId, regMapDisplayOrder, regMapName, regMapDesc, regMapAddr))
                    query.exec_("SELECT max(id) FROM RegisterMap")
                    query.next()
                    regMapId = query.record().value(0)
                    regMapDisplayOrder += 1

                    dlgProgress.setLabelText("Importing register map '%s' from %s "%(regMapName, fileName))
                    dlgProgress.setValue(i)
                 
                    regNodes = regMapNode.findall("Registers/Register")
                    for j in range(len(regNodes)):
                        regNode = regNodes[j]
                        regName = regNode.find("Name").text
                        regDesc = regNode.find("Description").text
                        regAddr = regNode.find("Address").text.lower().replace("'h", "0x").replace("'d", "")
                        regWidth = regNode.find("Width").text.lower().replace("'h", "0x").replace("'d", "")
                        query.exec_("INSERT INTO Register (RegisterMapId, DisplayOrder, Name, Description, OffsetAddress, Width) " \
                                    "VALUES ('%s', '%s', '%s', '%s', '%s', '%s')"%(regMapId, regDisplayOrder, regName, regDesc, regAddr, regWidth))
                        query.exec_("SELECT max(id) FROM Register")
                        query.next()
                        regId = query.record().value(0)
                        regDisplayOrder += 1

                        bfRefNodes = regNode.findall("BitFieldRefs/BitFieldRef")
                        for k in range(len(bfRefNodes)):
                            bfRefNode = bfRefNodes[k]
                            bfUID = bfRefNode.find("BF-UID").text
                            regOffset  = bfRefNode.find("RegOffset").text.lower().replace("'h", "0x").replace("'d", "")
                            bitOffset  = bfRefNode.find("BitOffset").text.lower().replace("'h", "0x").replace("'d", "")
                            sliceWidth = bfRefNode.find("SliceWidth").text.lower().replace("'h", "0x").replace("'d", "")
                            for m in range(len(bfNodes)):
                                bfNode = bfNodes[m]
                                if bfUIDs[m].text == bfUID:
                                    bfName = bfNode.find("Name").text
                                    if bfName != "RESERVED":
                                        bfDesc = bfNode.find("Description").text
                                        bfDfValue = bfNode.find("DefaultValue").text.replace("'h", "0x").replace("'d", "").replace("'b", "").replace("'", "")
                                        # TODO: process default value to get sliced value
                                        query.exec_("INSERT INTO Bitfield (RegisterId, DisplayOrder, Name, Description, RegisterOffset, Width, DefaultValue) " \
                                                    "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')"%(regId, bfDisplayOrder, bfName, bfDesc, regOffset, sliceWidth, bfDfValue))
                                        bfDisplayOrder += 1
                                    break
                dlgProgress.close()

            self.memMaptableModel.select()
            self.regMapTableModel.select()
            self.regTableModel.select()
            self.bfTableModel.select()
            self.setupTreeView()
            self.regMapTableModel.dataChanged.connect(self.do_tableView_dataChanged)
            self.regTableModel.dataChanged.connect(self.do_tableView_dataChanged)
            self.bfTableModel.dataChanged.connect(self.do_tableView_dataChanged)
            self.bfEnumTableModel.dataChanged.connect(self.do_tableView_dataChanged)
        return True

    def setupDesignViewModels(self, fileName):  
        self.conn = QSqlDatabase.addDatabase("QSQLITE", fileName)
        self.conn.setDatabaseName(fileName)
        if self.conn.open():
            # enable FK
            query = QSqlQuery(self.conn)
            query.prepare("PRAGMA foreign_keys = ON")
            query.exec_()

            # setup table models
            self.infoTableModel = QSqlTableModel(self, self.conn)
            self.infoTableModel.setEditStrategy(QSqlTableModel.OnFieldChange) 
            self.infoTableModel.setTable("info")
            self.infoTableModel.select()
            
            self.memMaptableModel = QSqlTableModel(self, self.conn)
            self.memMaptableModel.setEditStrategy(QSqlTableModel.OnFieldChange)  
            self.memMaptableModel.setTable("MemoryMap")
            self.memMaptableModel.select()

            self.regMapTableModel = QSqlHighlightTableModel(self, self.conn)
            self.regMapTableModel.setEditStrategy(QSqlTableModel.OnFieldChange)  
            self.regMapTableModel.setTable("RegisterMap")
            self.regMapTableModel.setSort(self.regMapTableModel.fieldIndex("DisplayOrder"), Qt.AscendingOrder)
            self.regMapTableModel.select()
            
            self.regTableModel = QSqlHighlightTableModel(self, self.conn)
            self.regTableModel.setEditStrategy(QSqlTableModel.OnFieldChange)  
            self.regTableModel.setTable("Register")
            self.regTableModel.setSort(self.regTableModel.fieldIndex("DisplayOrder"), Qt.AscendingOrder)
            self.regTableModel.select()
                        
            self.bfTableModel = QSqlHighlightTableModel(self, self.conn)
            self.bfTableModel.setEditStrategy(QSqlTableModel.OnFieldChange) 
            self.bfTableModel.setTable("Bitfield")
            self.bfTableModel.setSort(self.bfTableModel.fieldIndex("DisplayOrder"), Qt.AscendingOrder)
            self.bfTableModel.select()
            
            self.bfEnumTableModel = QSqlHighlightTableModel(self, self.conn)
            self.bfEnumTableModel.setEditStrategy(QSqlTableModel.OnFieldChange) 
            self.bfEnumTableModel.setTable("BitfieldEnum")
            self.bfEnumTableModel.setSort(self.bfEnumTableModel.fieldIndex("DisplayOrder"), Qt.AscendingOrder)
            self.bfEnumTableModel.select()
        else:
            QMessageBox.warning(self, "Error", "Failed to open %s"%fileName)  
            return False
        return True

    def setupTreeView(self):
        # create standard model for treeview          
        self.treeViewTableModel = QStandardItemModel()
        root = self.treeViewTableModel.invisibleRootItem()

        # memory map
        memoryMapQueryModel = QSqlQueryModel()
        memoryMapQueryModel.setQuery("SELECT id FROM MemoryMap", self.conn)
        for i in range(memoryMapQueryModel.rowCount()):
            memoryMapRecord = memoryMapQueryModel.record(i)
            self.memoryMapItem = QStandardItem(self.moduleIcon, "MemoryMap")
            self.memoryMapItem.setData("MemoryMap", RegisterConst.NameRole)
            self.memoryMapItem.setData(memoryMapRecord.value("id"), RegisterConst.MemMapIdRole)
            root.appendRow(self.memoryMapItem)            

            # register map
            regMapQueryModel = QSqlQueryModel()
            regMapQueryModel.setQuery("SELECT id, Name, Type FROM RegisterMap WHERE memoryMapId=%s ORDER BY DisplayOrder ASC"%memoryMapRecord.value("id"), self.conn)
            for j in range(regMapQueryModel.rowCount()):
                regMapRecord = regMapQueryModel.record(j)
                regMapitem = QStandardItem(self.regMapIcon, regMapRecord.value("name"))
                regMapitem.setData("RegisterMap", RegisterConst.NameRole)
                regMapitem.setData(memoryMapRecord.value("id"), RegisterConst.MemMapIdRole)
                regMapitem.setData(regMapRecord.value("id"), RegisterConst.RegMapIdRole)
                regMapitem.setData(regMapRecord.value("Type"), RegisterConst.RegMapTypeRole)
                self.memoryMapItem.appendRow(regMapitem)
                if RegisterConst.recordExist(regMapRecord) == False:
                    regMapitem.setData(QColor('grey'), Qt.BackgroundColorRole)
            
                # register
                regQueryModel = QSqlQueryModel()
                regQueryModel.setQuery("SELECT id, Name FROM Register WHERE RegisterMapId=%s ORDER BY DisplayOrder ASC"%regMapRecord.value("id"), self.conn)
                for k in range(regQueryModel.rowCount()):
                    regRecord = regQueryModel.record(k)
                    regItem = QStandardItem(self.regIcon, regRecord.value("name"))
                    regItem.setData("Register", RegisterConst.NameRole)
                    regItem.setData(memoryMapRecord.value("id"), RegisterConst.MemMapIdRole)
                    regItem.setData(regMapRecord.value("id"), RegisterConst.RegMapIdRole)
                    regItem.setData(regRecord.value("id"), RegisterConst.RegIdRole)
                    regMapitem.appendRow(regItem)
                    if RegisterConst.recordExist(regRecord) == False:
                        regItem.setData(QColor('grey'), Qt.BackgroundColorRole)
                    
                    # bitfield
                    bfQueryModel = QSqlQueryModel()
                    bfQueryModel.setQuery("SELECT id, Name FROM Bitfield WHERE RegisterId=%s ORDER BY DisplayOrder ASC"%regRecord.value("id"), self.conn)
                    for m in range(bfQueryModel.rowCount()):
                        bfRecord = bfQueryModel.record(m)
                        bfItem = QStandardItem(self.bfIcon, bfRecord.value("name"))
                        bfItem.setData("Bitfield", RegisterConst.NameRole)
                        bfItem.setData(memoryMapRecord.value("id"), RegisterConst.MemMapIdRole)
                        bfItem.setData(regMapRecord.value("id"), RegisterConst.RegMapIdRole)
                        bfItem.setData(regRecord.value("id"), RegisterConst.RegIdRole)
                        bfItem.setData(bfRecord.value("id"), RegisterConst.BfIdRole)
                        regItem.appendRow(bfItem)
                        if RegisterConst.recordExist(bfRecord) == False:
                            bfItem.setData(QColor('grey'), Qt.BackgroundColorRole)                       

                        # bitfield enum
                        bfEnumQueryModel = QSqlQueryModel()
                        bfEnumQueryModel.setQuery("SELECT id, Name FROM BitfieldEnum WHERE BitfieldId=%s ORDER BY DisplayOrder ASC"%bfRecord.value("id"), self.conn)
                        for n in range(bfEnumQueryModel.rowCount()):
                            bfEnumRecord = bfEnumQueryModel.record(n)
                            bfEnumItem = QStandardItem(self.bfenumIcon, bfEnumRecord.value("name"))
                            bfEnumItem.setData("BitfieldEnum", RegisterConst.NameRole)
                            bfEnumItem.setData(memoryMapRecord.value("id"), RegisterConst.MemMapIdRole)
                            bfEnumItem.setData(regMapRecord.value("id"), RegisterConst.RegMapIdRole)
                            bfEnumItem.setData(regRecord.value("id"), RegisterConst.RegIdRole)
                            bfEnumItem.setData(bfRecord.value("id"), RegisterConst.BfIdRole)
                            bfEnumItem.setData(bfEnumRecord.value("id"), RegisterConst.BfEnumIdRole)
                            bfItem.appendRow(bfEnumItem)
                            if RegisterConst.recordExist(bfEnumRecord) == False:
                                bfEnumItem.setData(QColor('grey'), Qt.BackgroundColorRole)
        
        # show tree view nodes
        self.ui.treeView.setModel(self.treeViewTableModel)
        self.ui.treeView.expandAll()

        # connect slots
        treeViewSelectionModel = self.ui.treeView.selectionModel()
        treeViewSelectionModel.currentChanged.connect(self.do_treeView_currentChanged)

        self.ui.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.treeView.customContextMenuRequested.connect(self.do_treeView_contextMenuRequested)
        
        # select memory map node
        memoryMapItemIndex = self.treeViewTableModel.indexFromItem(self.memoryMapItem)
        treeViewSelectionModel.select(memoryMapItemIndex, QItemSelectionModel.ClearAndSelect)
        self.do_treeView_currentChanged(memoryMapItemIndex, None)
    
    def setupDebugViewModels(self):
        # clear existing item
        for model in self.regDebugModels:
            model.clear()
        self.regDebugModels.clear()

        # register map
        regMapQueryModel = QSqlQueryModel()
        regMapQueryModel.setQuery("SELECT * FROM RegisterMap ORDER BY DisplayOrder ASC", self.conn)
        for i in range(regMapQueryModel.rowCount()):
            regMapRecord = regMapQueryModel.record(i)
            if RegisterConst.recordExist(regMapRecord) == True:
                debugModel = QRegDebugTableModel()
                debugModel.setRegMapId(regMapRecord.value("id"))
                debugModel.setHorizontalHeaderLabels(["Name", "Address", "Description", "Value"])
                self.regDebugModels.append(debugModel)
            
            # register
            regQueryModel = QSqlQueryModel()
            regQueryModel.setQuery("SELECT * FROM Register WHERE RegisterMapId=%s ORDER BY DisplayOrder ASC"%regMapRecord.value("id"), self.conn)
            for j in range(regQueryModel.rowCount()):
                regRecord = regQueryModel.record(j)
                if RegisterConst.recordExist(regRecord) == True:
                    regItem0 = QStandardItem(self.regIcon, regRecord.value("name"))
                    regItem1 = QStandardItem(str(regRecord.value("OffsetAddress")))
                    regItem2 = QStandardItem(regRecord.value("Description"))
                    regItem3 = QStandardItem(str(regRecord.value("Value")))
                    regItems = [regItem0, regItem1, regItem2, regItem3]
                    for r in regItems:
                        r.setData("Register", RegisterConst.NameRole)
                    debugModel.appendRow(regItems)

                # bitfield
                bfQueryModel = QSqlQueryModel()
                bfQueryModel.setQuery("SELECT Name, Value FROM Bitfield WHERE RegisterId=%s ORDER BY DisplayOrder ASC"%regRecord.value("id"), self.conn)
                for k in range(bfQueryModel.rowCount()):
                    bfRecord = bfQueryModel.record(k)
                    if RegisterConst.recordExist(bfRecord) == True:
                        bfItem0 = QStandardItem(" ")
                        bfItem1 = QStandardItem(" ")
                        bfItem2 = QStandardItem(bfRecord.value("name"))
                        bfItem3 = QStandardItem(str(bfRecord.value("Value")))
                        bfItems = [bfItem0, bfItem1, bfItem2, bfItem3]
                        for r in bfItems:
                            r.setData("Bitfield", RegisterConst.NameRole)                        
                        debugModel.appendRow(bfItems)

    @Slot('QItemSelection', 'QItemSelection')
    def do_tableView_selectionChanged(self, selected, deselected):
        if self.view == RegisterConst.DesignView:
            if self.__treeViewCurrentTable == "Register":                            
                tableViewCurrents = self.ui.tableViewReg.selectionModel().selectedIndexes()                
            else:
                tableViewCurrents = self.ui.tableView.selectionModel().selectedIndexes()
            tableViewCurrent = None if len(tableViewCurrents) == 0 else tableViewCurrents[0]
            if tableViewCurrent != None:
                treeViewCurrent = self.ui.treeView.selectedIndexes()[0]
                if tableViewCurrent.row() != self.__treeViewCurrentRow:
                    sibling = treeViewCurrent.sibling(tableViewCurrent.row(), 0)
                    self.ui.treeView.selectionModel().setCurrentIndex(sibling, QItemSelectionModel.ClearAndSelect)                
        return
    
    @Slot()
    def do_treeView_contextMenuRequested(self, point):
        # do not allow to edit design by context menu in debug view
        if self.view == RegisterConst.DebugView:
            return
        
        # allow to edit by context menu in design view
        index = self.ui.treeView.indexAt(point)
        tableName = str(index.data(RegisterConst.NameRole))
        
        self.treeViewPopMenu = QMenu(self)
        addRegMapAction = QAction("+ RegMap", self)
        addRegModAction = QAction("+ RegMod", self)
        addRegAction = QAction("+ Reg", self)
        addBfAction = QAction("+ Bitfield", self)
        addBfEnumAction = QAction("+ Bitfield Enum", self)
        
        if tableName == "MemoryMap":
            self.treeViewPopMenu.addAction(addRegMapAction)
            addRegMapAction.triggered.connect(self.on_pbAddRegMap_clicked)
            self.treeViewPopMenu.addAction(addRegModAction)
            addRegModAction.triggered.connect(self.do_pbAddRegMod_clicked)
        elif tableName == "RegisterMap":
            regMapType = index.data(RegisterConst.RegMapTypeRole)
            regMapType = RegisterConst.RegMap if regMapType == None or regMapType == '' else int(regMapType) # default as regmap if not set
            if regMapType == RegisterConst.RegMap:
                self.treeViewPopMenu.addAction(addRegAction)
                addRegAction.triggered.connect(self.on_pbAddReg_clicked)
        elif tableName == "Register":
            self.treeViewPopMenu.addAction(addBfAction)
            addBfAction.triggered.connect(self.on_pbAddBf_clicked)
        elif tableName == "Bitfield":
            self.treeViewPopMenu.addAction(addBfEnumAction)
            addBfEnumAction.triggered.connect(self.on_pbAddBfEnum_clicked)

        # do not allow to add anything if bitfield is selected to make usage simple
        # elif tableName == "BitfieldEnum":
        #    self.treeViewPopMenu.addAction(addRegMapAction)
        #    addRegMapAction.triggered.connect(self.on_pbAddRegMap_clicked)
        #    self.treeViewPopMenu.addAction(addRegModAction)
        #    addRegModAction.triggered.connect(self.do_pbAddRegMod_clicked)
        #    self.treeViewPopMenu.addAction(addRegAction)
        #    addRegAction.triggered.connect(self.on_pbAddReg_clicked)
        #    self.treeViewPopMenu.addAction(addBfAction)
        #    addBfAction.triggered.connect(self.on_pbAddBf_clicked)
        #    self.treeViewPopMenu.addAction(addBfEnumAction)
        #    addBfEnumAction.triggered.connect(self.on_pbAddBfEnum_clicked)
        
        if tableName != "MemoryMap" or index.row() != 0:
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
        tableName = str(current.data(RegisterConst.NameRole))
        
        model = None
        idRole = None
        if tableName == "RegisterMap":
            model = self.regMapTableModel
            idRole = RegisterConst.RegMapIdRole
        elif tableName == "Register":
            model = self.regTableModel
            idRole = RegisterConst.RegIdRole
        elif tableName == "Bitfield":
            model = self.bfTableModel
            idRole = RegisterConst.BfIdRole
        elif tableName == "BitfieldEnum":
            model = self.bfEnumTableModel
            idRole = RegisterConst.BfEnumIdRole
        
        # update treeview node accordingly
        # update tree node name if "Name" is changed, or change tree node background color if "Exist" is changed
        if model != None:
            fieldName = model.record().fieldName(bottomRight.column())
            if fieldName == "Name":
                itemId = model.data(model.index(bottomRight.row(), 0), Qt.DisplayRole)
                parentItem = self.treeViewTableModel.itemFromIndex(current.parent())
                for i in range(parentItem.rowCount()):
                    child = current.sibling(i, 0)
                    childId = child.data(idRole)
                    if childId != None and int(childId) == itemId:
                        newName = model.record(bottomRight.row()).value("Name")
                        self.treeViewTableModel.itemFromIndex(child).setData(newName, Qt.DisplayRole)
            elif fieldName == "Exist":
                itemId = model.data(model.index(bottomRight.row(), 0), Qt.DisplayRole) # 'id' is column 0
                parentItem = self.treeViewTableModel.itemFromIndex(current.parent())
                for i in range(parentItem.rowCount()):
                    child = current.sibling(i, 0)
                    childId = child.data(idRole)
                    if childId != None and int(childId) == itemId:
                        if RegisterConst.recordExist(model.record(bottomRight.row())) == False:
                            self.treeViewTableModel.itemFromIndex(child).setData(QColor('grey'), Qt.BackgroundColorRole)
                        else:
                            self.treeViewTableModel.itemFromIndex(child).setData(None, Qt.BackgroundColorRole)

        # resize columns                            
        if tableName == "Register":
            self.ui.tableViewReg.resizeColumnsToContents()            
        else:
            self.ui.tableView.resizeColumnsToContents()
            
        return
    
    @Slot()
    def do_treeView_currentChanged(self, current, previous):
        if self.view == RegisterConst.DesignView:
            tableName = str(current.data(RegisterConst.NameRole))
            if tableName == "MemoryMap": # memmap selected, show memmap table
                self.ui.tableView.setVisible(True)
                self.ui.tableViewReg.setVisible(False)                 
                if self.ui.tableView.model() != self.memMaptableModel:
                    self.ui.tableView.setModel(self.memMaptableModel)
                    self.ui.tableView.selectionModel().selectionChanged.connect(self.do_tableView_selectionChanged)
                    if self.__regMapTypeIndex != None:
                        self.ui.tableView.showColumn(self.__regMapTypeIndex)
                        self.__regMapTypeIndex = None
                    self.ui.tableView.hideColumn(0) # id
                    self.ui.tableView.showColumn(1) # offset address
                    self.ui.tableView.showColumn(2) # notes
                    self.ui.tableView.resizeColumnsToContents()
                    
                # update tips
                self.ui.pbAddRegMap.setEnabled(True)
                self.ui.pbAddReg.setEnabled(False)
                self.ui.pbAddBf.setEnabled(False)
                self.ui.pbAddBfEnum.setEnabled(False)
                self.ui.labelDescription.setText("Tips: <br><br>Click <font color=\"red\">%s</font> to add new register map.</br></br>"%self.ui.pbAddRegMap.text())
                
            elif tableName == "RegisterMap": # regmap or reg selected, show regmap table
                self.ui.tableView.setVisible(True)
                self.ui.tableViewReg.setVisible(False)                 
                if self.ui.tableView.model() != self.regMapTableModel:
                    self.ui.tableView.setModel(self.regMapTableModel)
                    self.ui.tableView.selectionModel().selectionChanged.connect(self.do_tableView_selectionChanged)
                    self.ui.tableView.hideColumn(0) # id
                    self.ui.tableView.hideColumn(1) # memmap id
                    self.ui.tableView.hideColumn(2) # order
                    self.__regMapTypeIndex = self.regMapTableModel.record().indexOf("Type")
                    self.ui.tableView.hideColumn(self.__regMapTypeIndex)
                    self.ui.tableView.resizeColumnsToContents()
                    self.ui.tableView.resizeColumnsToContents()
                                    
                # update tips
                self.ui.pbAddRegMap.setEnabled(False)
                self.ui.pbAddBf.setEnabled(False)
                self.ui.pbAddBfEnum.setEnabled(False)
                regMapType = current.data(RegisterConst.RegMapTypeRole)
                regMapType = RegisterConst.RegMap if regMapType == None or regMapType == '' else int(regMapType) # default as regmap if not set
                self.ui.pbAddReg.setEnabled(regMapType == RegisterConst.RegMap)                
                if regMapType == RegisterConst.RegMap:
                    self.ui.labelDescription.setText("Tips: <br><br>Click <font color=\"red\">%s</font> to add register.</br></br>"%(self.ui.pbAddReg.text()))
                else:
                    self.ui.labelDescription.setText("Tips: <br><br>Assign a filename to sub-module.</br></br>")

            elif tableName == "Register": # reg selected, show reg table
                self.ui.tableView.setVisible(False)
                self.ui.tableViewReg.setVisible(True)                
                regMapId = int(current.data(RegisterConst.RegMapIdRole))
                if self.ui.tableViewReg.model() != self.regTableModel or regMapId != self.regTableModel.parentId:
                    self.__regValueIndex = self.regTableModel.record().indexOf("Value")
                    self.regTableModel.setHeaderData(self.__regValueIndex, Qt.Horizontal, "Bits")
                    self.regTableModel.setParentId(regMapId)
                    self.regTableModel.setFilter("RegisterMapId=%s"%regMapId)
                    self.regTableModel.select()
                    self.ui.tableViewReg.setItemDelegateForColumn(self.__regValueIndex, QRegValueDisplayDelegate())
                    if self.ui.tableViewReg.model() != self.regTableModel:
                        self.ui.tableViewReg.setModel(self.regTableModel)
                    self.ui.tableViewReg.selectionModel().selectionChanged.connect(self.do_tableView_selectionChanged)
                    self.ui.tableViewReg.hideColumn(0) # id
                    self.ui.tableViewReg.hideColumn(1) # regmap id
                    self.ui.tableViewReg.hideColumn(2) # order
                    self.ui.tableViewReg.resizeColumnsToContents()

                # update tips
                self.ui.pbAddRegMap.setEnabled(False)
                self.ui.pbAddReg.setEnabled(False)
                self.ui.pbAddBf.setEnabled(True)
                self.ui.pbAddBfEnum.setEnabled(False)                
                self.ui.labelDescription.setText("Tips: <br><br>Click <font color=\"red\">%s</font> to add bitfield</br></br>"%(self.ui.pbAddBf.text()))
                
            elif tableName == "Bitfield": # bf selected, show bf table
                self.ui.tableView.setVisible(True)
                self.ui.tableViewReg.setVisible(False)
                regId = int(current.data(RegisterConst.RegIdRole))
                bfId  = int(current.data(RegisterConst.BfIdRole))
                if self.ui.tableView.model() != self.bfTableModel or regId != self.bfTableModel.parentId:
                    self.bfTableModel.setParentId(regId)
                    self.bfTableModel.setFilter("RegisterId=%s"%regId)
                    self.ui.tableView.setModel(self.bfTableModel)
                    self.ui.tableView.selectionModel().selectionChanged.connect(self.do_tableView_selectionChanged)
                    if self.__regMapTypeIndex != None:
                        self.ui.tableView.showColumn(self.__regMapTypeIndex)
                        self.__regMapTypeIndex = None
                    self.ui.tableView.hideColumn(0) # id
                    self.ui.tableView.hideColumn(1) # regid
                    self.ui.tableView.hideColumn(2) # order
                    self.ui.tableView.resizeColumnsToContents()
                    
                # update tips
                self.ui.pbAddRegMap.setEnabled(False)
                self.ui.pbAddReg.setEnabled(False)
                self.ui.pbAddBf.setEnabled(False)
                self.ui.pbAddBfEnum.setEnabled(True)                
                regQ = QSqlQuery("SELECT Width FROM Register WHERE id=%s"%(regId), self.conn)
                text = ""
                while regQ.next(): # only 1 item
                    regW = regQ.value(0)
                    text = "Tips: <pre>"
                    text += RegisterConst.genColoredRegBitsUsage(self.conn, bfId, regId, regW, 13)
                    text += "</pre>"
                self.ui.labelDescription.setText(text)

            elif tableName == "BitfieldEnum": # bfenum selected, show bfenum table
                self.ui.tableView.setVisible(True)
                self.ui.tableViewReg.setVisible(False)                 
                bfId = int(current.data(RegisterConst.BfIdRole))      
                if self.ui.tableView.model() != self.bfEnumTableModel or bfId != self.bfEnumTableModel.parentId:
                    self.bfEnumTableModel.setParentId(bfId)
                    self.bfEnumTableModel.setFilter("BitfieldId=%s"%bfId)
                    self.bfEnumTableModel.select()
                    self.ui.tableView.setModel(self.bfEnumTableModel)
                    self.ui.tableView.selectionModel().selectionChanged.connect(self.do_tableView_selectionChanged)
                    if self.__regMapTypeIndex != None:
                        self.ui.tableView.showColumn(self.__regMapTypeIndex)
                        self.__regMapTypeIndex = None
                    self.ui.tableView.hideColumn(0) # id
                    self.ui.tableView.hideColumn(1) # bfid
                    self.ui.tableView.hideColumn(2) # order
                    self.ui.tableView.resizeColumnsToContents()
                    
                # update tips
                self.ui.pbAddRegMap.setEnabled(False)
                self.ui.pbAddReg.setEnabled(False)
                self.ui.pbAddBf.setEnabled(False)
                self.ui.pbAddBfEnum.setEnabled(False)                    
                self.ui.labelDescription.setText("Tips: <br><br>Click <font color=\"red\">%s</font> to add new bitfield enum.</br></br>"%self.ui.pbAddBfEnum.text())

            # select tableView row
            self.__treeViewCurrentTable = tableName
            self.__treeViewCurrentRow = current.row()
            if tableName == "Register":
                tableViewCurrents = self.ui.tableViewReg.selectionModel().selectedIndexes()                
            else:
                tableViewCurrents = self.ui.tableView.selectionModel().selectedIndexes()
            tableViewCurrent = None if len(tableViewCurrents) == 0 else tableViewCurrents[0]
            if tableViewCurrent == None or tableViewCurrent.row() != current.row():
                if tableName == "Register":
                    self.ui.tableViewReg.selectRow(current.row())
                else:
                    self.ui.tableView.selectRow(current.row())                    
        else: # debug view
            tableName = str(current.data(RegisterConst.NameRole))
            if tableName != "MemoryMap":          
                for regDebugModel in self.regDebugModels:
                    regMapId = int(current.data(RegisterConst.RegMapIdRole))
                    if regDebugModel.id == regMapId:
                        self.ui.tableView.setModel(regDebugModel)
                        self.ui.tableView.selectionModel().selectionChanged.connect(self.do_tableView_selectionChanged)
                        if self.__regMapTypeIndex != None:
                            self.ui.tableView.showColumn(self.__regMapTypeIndex)
                            self.__regMapTypeIndex = None
                        self.ui.tableView.showColumn(0)
                        self.ui.tableView.showColumn(1)
                        self.ui.tableView.showColumn(2)
                        self.ui.tableView.resizeColumnsToContents()
                        break
        return

    @Slot()
    def on_pbAddRegMap_clicked(self):
        current = self.ui.treeView.selectedIndexes().pop()
        tableName = str(current.data(RegisterConst.NameRole))
        memoryMapId = int(current.data(RegisterConst.MemMapIdRole))
        newRegMapRowIndex = -1 if tableName != "RegisterMap" else current.row() + 1
        r = self.newRegMapRow(self.regMapTableModel, memoryMapId, newRegMapRowIndex)
        
        newRegMapItem = QStandardItem(self.regMapIcon, r.value("name"))
        newRegMapItem.setData("RegisterMap", RegisterConst.NameRole)
        newRegMapItem.setData(memoryMapId, RegisterConst.MemMapIdRole)
        newRegMapItem.setData(r.value("id"), RegisterConst.RegMapIdRole)
        newRegMapItem.setData(RegisterConst.RegMap, RegisterConst.RegMapTypeRole)
        
        standardItem = self.treeViewTableModel.itemFromIndex(current)
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
    def do_pbAddRegMod_clicked(self):
        current = self.ui.treeView.selectedIndexes().pop()
        tableName = str(current.data(RegisterConst.NameRole))
        memoryMapId = int(current.data(RegisterConst.MemMapIdRole))
        newRegMapRowIndex = -1 if tableName != "RegisterMap" else current.row() + 1
        r = self.newRegMapRow(self.regMapTableModel, memoryMapId, newRegMapRowIndex, RegisterConst.RegMod)
        
        newRegMapItem = QStandardItem(self.regMapIcon, r.value("name"))
        newRegMapItem.setData("RegisterMap", RegisterConst.NameRole)
        newRegMapItem.setData(memoryMapId, RegisterConst.MemMapIdRole)
        newRegMapItem.setData(r.value("id"), RegisterConst.RegMapIdRole)
        newRegMapItem.setData(RegisterConst.RegMod, RegisterConst.RegMapTypeRole)
        
        standardItem = self.treeViewTableModel.itemFromIndex(current)
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
        tableName = str(current.data(RegisterConst.NameRole))
        memoryMapId = int(current.data(RegisterConst.MemMapIdRole))
        regMapId = int(current.data(RegisterConst.RegMapIdRole))
        newRegRowIndex = -1 if tableName != "Register" else current.row() + 1
        r = self.newRegRow(self.regTableModel, regMapId, 0, 32, newRegRowIndex)
        
        newRegItem = QStandardItem(self.regIcon, r.value("name"))
        newRegItem.setData("Register", RegisterConst.NameRole)
        newRegItem.setData(memoryMapId, RegisterConst.MemMapIdRole)
        newRegItem.setData(regMapId, RegisterConst.RegMapIdRole)
        newRegItem.setData(r.value("id"), RegisterConst.RegIdRole)
    
        standardItem = self.treeViewTableModel.itemFromIndex(current)
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
        tableName = str(current.data(RegisterConst.NameRole))
        memoryMapId = int(current.data(RegisterConst.MemMapIdRole))
        regMapId = int(current.data(RegisterConst.RegMapIdRole))
        regId = int(current.data(RegisterConst.RegIdRole))
        newBfRowIndex = -1 if tableName != "Bitfield" else current.row() + 1 
        r = self.newBfRow(self.bfTableModel, regId, 8, newBfRowIndex)
        
        newBfItem = QStandardItem(self.bfIcon, r.value("name"))
        newBfItem.setData("Bitfield", RegisterConst.NameRole)
        newBfItem.setData(memoryMapId, RegisterConst.MemMapIdRole)
        newBfItem.setData(regMapId, RegisterConst.RegMapIdRole)
        newBfItem.setData(regId, RegisterConst.RegIdRole)
        newBfItem.setData(r.value("id"), RegisterConst.BfIdRole)

        standardItem = self.treeViewTableModel.itemFromIndex(current)
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
        elif tableName == "BitfieldEnum":
            standardItem.parent().parent().appendRow(newBfItem)
        return

    @Slot()
    def on_pbAddBfEnum_clicked(self):
        current = self.ui.treeView.selectedIndexes().pop()
        tableName = str(current.data(RegisterConst.NameRole))
        memoryMapId = int(current.data(RegisterConst.MemMapIdRole))
        regMapId = int(current.data(RegisterConst.RegMapIdRole))
        regId = int(current.data(RegisterConst.RegIdRole))
        bfId = int(current.data(RegisterConst.BfIdRole))
        newBfEnumRowIndex = -1 if tableName != "BitfieldEnum" else current.row() + 1
        r = self.newBfEnumRow(self.bfEnumTableModel, bfId, newBfEnumRowIndex)
        
        newBfEnumItem = QStandardItem(self.bfenumIcon, r.value("name"))
        newBfEnumItem.setData("BitfieldEnum", RegisterConst.NameRole)
        newBfEnumItem.setData(memoryMapId, RegisterConst.MemMapIdRole)
        newBfEnumItem.setData(regMapId, RegisterConst.RegMapIdRole)
        newBfEnumItem.setData(regId, RegisterConst.RegIdRole)
        newBfEnumItem.setData(bfId, RegisterConst.BfIdRole)
        newBfEnumItem.setData(r.value("id"), RegisterConst.BfEnumIdRole)
        
        standardItem = self.treeViewTableModel.itemFromIndex(current)
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
        tableName = str(current.data(RegisterConst.NameRole))
        
        # remove from table
        if tableName == "MemoryMap" and current.row() != 0:
            memMapId = int(current.data(RegisterConst.MemMapIdRole))
            for i in range(self.memMaptableModel.rowCount()):
                if self.memMaptableModel.record(i).value("id") == memMapId:
                    self.memMaptableModel.removeRows(i, 1)
                    break
            self.regMapTableModel.select()
        elif tableName == "RegisterMap":
            regMapId = int(current.data(RegisterConst.RegMapIdRole))
            for i in range(self.regMapTableModel.rowCount()):
                if self.regMapTableModel.record(i).value("id") == regMapId:
                    self.regMapTableModel.removeRows(i, 1)
                    break
            self.regMapTableModel.select()
        elif tableName == "Register":
            regId = int(current.data(RegisterConst.RegIdRole))
            for i in range(self.regTableModel.rowCount()):
                if self.regTableModel.record(i).value("id") == regId:
                    self.regTableModel.removeRows(i, 1)
                    break
            self.regTableModel.select()
        elif tableName == "Bitfield":
            bfId = int(current.data(RegisterConst.BfIdRole))
            for i in range(self.bfTableModel.rowCount()):
                if self.bfTableModel.record(i).value("id") == bfId:
                    self.bfTableModel.removeRows(i, 1)
                    break
            self.bfTableModel.select()
        elif tableName == "BitfieldEnum":
            bfEnumId = int(current.data(RegisterConst.BfEnumIdRole))
            for i in range(self.bfEnumTableModel.rowCount()):
                if self.bfEnumTableModel.record(i).value("id") == bfEnumId:
                    self.bfEnumTableModel.removeRows(i, 1)
                    break
            self.bfEnumTableModel.select()
        
        # remove from tree but keep last memory map node
        if tableName != "MemoryMap" or current.row() != 0:
            parentItem = self.treeViewTableModel.itemFromIndex(current.parent())
            parentItem.removeRow(current.row())
        
        return