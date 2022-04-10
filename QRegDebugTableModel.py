from PySide2.QtWidgets import QWidget, QStyledItemDelegate, QStyleOptionViewItem, QLabel
from PySide2.QtSql import QSqlDatabase, QSqlQueryModel, QSqlQuery
from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex, QSize
from PySide2.QtGui import QStandardItemModel, QStandardItem, QColor, QIcon, QPainter
from QRegisterConst import QRegisterConst

class QRegDebugTableModel(QStandardItemModel):

    def __init__(self):
        QStandardItemModel.__init__(self)
        
    def setRegMapId(self, id):
        self.id = id
       
    def flags(self, index):
        flags = QStandardItemModel.flags(self, index)                
        if index.column() != 3: # value column
            flags &= ~Qt.ItemIsEditable
        return flags

    def data(self, index, role):
        value = QStandardItemModel.data(self, index, role)
        if role == Qt.BackgroundColorRole:
            tableName = index.data(QRegisterConst.TableNameRole)
            #if tableName == "Register":
            #    value = QColor('lightgrey') # highlight register row
        return value

    def setData(self, index, value, role=Qt.EditRole):
        if QRegisterConst.DriverClass is not None:
            QRegisterConst.DriverClass.writeReg(0x0000, 0x0001)
            value = hex(QRegisterConst.DriverClass.readReg(0x0000))
        QStandardItemModel.setData(self, index, value, role)
        return True
