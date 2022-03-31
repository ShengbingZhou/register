from PySide2.QtSql import QSqlDatabase, QSqlQueryModel, QSqlQuery
from PySide2.QtCore import Qt, QAbstractTableModel
from PySide2.QtGui import QStandardItemModel, QStandardItem, QColor, QIcon
from RegisterConst import RegisterConst

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
            tableName = QStandardItemModel.data(self, index, RegisterConst.NameRole)
            #if tableName == "Register":
            #    value = QColor('lightgrey')
        return value