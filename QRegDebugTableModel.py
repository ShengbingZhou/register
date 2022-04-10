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
        if index.column() != 3: # value
            flags &= ~Qt.ItemIsEditable
        return flags

    def data(self, index, role):
        value = QStandardItemModel.data(self, index, role)
        if role == Qt.BackgroundColorRole:
            tableName = QStandardItemModel.data(self, index, QRegisterConst.NameRole)
            #if tableName == "Register":
            #    value = QColor('lightgrey')
        return value

class QRegDebugValueEditDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent: QWidget, option:QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        return

    def setEditorData(self, editor, index: QModelIndex):
        value = index.model().data(index, Qt.DisplayRole)
        driverMod   = __import__("QRegAccessDriver")
        driverClass = getattr(driverMod, "QRegAccessClass")
        driverClass.writeReg(0x0000, 0x0001)

    def setModelData(self, editor, model, index: QModelIndex):
        driverMod   = __import__("QRegAccessDriver")
        driverClass = getattr(driverMod, "QRegAccessClass")
        value = driverClass.readReg(0x0000)
        model.setData(index, value, Qt.DisplayRole)

    def updateEditorGeometry(self, editor, option: QStyleOptionViewItem, index: QModelIndex):
        return editor.setGeometry(option.rect)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        size = super().sizeHint(option, index)
        size.setWidth(200)
        return size