from PySide2.QtWidgets import QWidget, QStyledItemDelegate, QStyleOptionViewItem, QLabel
from PySide2.QtSql import QSqlDatabase, QSqlQueryModel, QSqlQuery
from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex, QSize, Signal
from PySide2.QtGui import QStandardItemModel, QStandardItem, QColor, QIcon, QPainter
from QRegisterConst import QRegisterConst

class QRegDebugTableModel(QStandardItemModel):

    # module name (from info) / 'w' / address / value / comment
    regWritten = Signal(str, str, str, str, str)

    # module name passed to 'regWritten'
    modName = ""

    def __init__(self):
        QStandardItemModel.__init__(self)
        
    def setConn(self, conn):
        self.conn = conn
       
    def setModuleName(self, moduleName):
        self.modName = moduleName

    def setRegMapId(self, id):
        self.id = id

    def flags(self, index):
        flags = QStandardItemModel.flags(self, index)                       
        if index.column() != QRegisterConst.ValueColumnOfDebugView:
            flags &= ~Qt.ItemIsEditable  # only allow value column to editable
        else:
            readOnly = index.data(QRegisterConst.BfReadOnlyRole)
            if readOnly is not None and readOnly is True:
                flags &= ~Qt.ItemIsEditable
        return flags

    def data(self, index, role):
        value = QStandardItemModel.data(self, index, role)
        if role == Qt.BackgroundColorRole:
            tableName = index.data(QRegisterConst.TableNameRole)
            if tableName == "Register":
                value = QColor('lightgrey')  # highlight register row
            else:
                if index.column() ==  QRegisterConst.ValueColumnOfDebugView and self.flags(index) & Qt.ItemIsEditable == 0:
                    value = QColor('yellow') # highlight readonly row
        return value

    def setData(self, index, value, role=Qt.EditRole):

        if role != Qt.EditRole:
            QStandardItemModel.setData(self, index, value, role)
    
        # get table name
        tableName = index.data(QRegisterConst.TableNameRole)

        # get register address
        regId = index.data(QRegisterConst.RegIdRole)
        bfId  = None
        query = self.conn.exec_("SELECT * FROM Register WHERE id=%s"%regId)
        query.next()
        regName = query.value("Name")
        regAddr = QRegisterConst.strToInt(query.value("OffsetAddress"))
        
        # generate new register value
        if tableName == "Register":
            # get latest reg value
            regValue = QRegisterConst.strToInt(str(value))
            regRow   = index.row()

            # trigger signal
            self.regWritten.emit(self.modName, "w", "%08x"%(regAddr), "%08x"%(regValue), regName)

        if tableName == "Bitfield":
            regRow = index.row() - 1
            while index.sibling(regRow, 0).data(QRegisterConst.TableNameRole) != "Register":
                regRow = regRow - 1

            # get current reg value
            if QRegisterConst.RegisterAccessDriverClass is None:
                regValue = QRegisterConst.strToInt(index.sibling(regRow, QRegisterConst.ValueColumnOfDebugView).data(Qt.DisplayRole))
            else:
                regValue = QRegisterConst.RegisterAccessDriverClass.readReg(self.modName, regAddr)

            # update bitfield value to get latest reg value
            bfId = index.data(QRegisterConst.BfIdRole)
            query = self.conn.exec_("SELECT * FROM Bitfield WHERE id=%s"%bfId)
            query.next()
            bfName  = query.value("Name")
            bfWidth = int(query.value("Width"))
            bfValue = QRegisterConst.strToInt(str(value)) & ((1 << bfWidth) - 1)
            regOff  = QRegisterConst.strToInt(query.value("RegisterOffset"))
            regValue -= (((1 << bfWidth) - 1) << regOff) & regValue
            regValue += bfValue << regOff

            # trigger signal
            self.regWritten.emit(self.modName, "w", "%08x"%(regAddr), "%08x"%(regValue), "%s:%s:%08x"%(regName, bfName, bfValue))

        # write reg value to hardware, then read latest reg value back
        if QRegisterConst.RegisterAccessDriverClass is not None:
            QRegisterConst.RegisterAccessDriverClass.writeReg(self.modName, regAddr, regValue)
            regValue = QRegisterConst.RegisterAccessDriverClass.readReg(self.modName, regAddr)

        # update register and bitfield display value
        value = hex(regValue) # default as reg return value, will be overwritten if it is for bitfield
        query = self.conn.exec_("SELECT * FROM Bitfield WHERE RegisterId=%s ORDER BY DisplayOrder ASC"%regId)
        bfRow = regRow + 1
        while query.next():
            bfWidth = int(query.value("Width"))
            regOff  = QRegisterConst.strToInt(query.value("RegisterOffset"))
            bfValue = (regValue >>  regOff) & ((1 << bfWidth) - 1)
            item = index.model().itemFromIndex(index.sibling(bfRow, QRegisterConst.ValueColumnOfDebugView))
            bfRow = bfRow + 1
            if bfId != None and bfId == query.value("id"):
                value = hex(bfValue)
            else:
                item.setData(hex(bfValue), Qt.DisplayRole)
        if tableName == "Bitfield":
            item = index.model().itemFromIndex(index.sibling(regRow, QRegisterConst.ValueColumnOfDebugView))
            item.setData(hex(regValue), Qt.DisplayRole)

        QStandardItemModel.setData(self, index, value, role)
        return True

    # read hardware then update reg value and bf value belong to this reg on GUI
    def readReg(self, index):

        if QRegisterConst.RegisterAccessDriverClass is None:
            return
        if index.data(QRegisterConst.TableNameRole) != "Register":
            return

        regId = index.data(QRegisterConst.RegIdRole)
        query = self.conn.exec_("SELECT * FROM Register WHERE id=%s"%regId)
        query.next()
        regAddr = QRegisterConst.strToInt(query.value("OffsetAddress"))

        # read hardware
        value = QRegisterConst.RegisterAccessDriverClass.readReg(self.modName, regAddr)

        self.setData(index, hex(value), Qt.DisplayRole)
        regId = index.data(QRegisterConst.RegIdRole)
        query = self.conn.exec_("SELECT * FROM Bitfield WHERE RegisterId=%s ORDER BY DisplayOrder ASC"%regId)
        bfRow = index.row() + 1
        while query.next():
            bfWidth = int(query.value("Width"))
            regOff  = QRegisterConst.strToInt(query.value("RegisterOffset"))
            bfValue = (value >>  regOff) & ((1 << bfWidth) - 1)
            item = index.model().itemFromIndex(index.sibling(bfRow, QRegisterConst.ValueColumnOfDebugView))
            bfRow = bfRow + 1
            item.setData(hex(bfValue), Qt.DisplayRole)
