from PySide2.QtSql import QSqlDatabase, QSqlQueryModel, QSqlQuery
from PySide2.QtCore import Qt, QAbstractTableModel
from PySide2.QtGui import QColor
from RegisterConst import RegisterConst

class QSqlQueryBfTableModel(QSqlQueryModel):

    def __init__(self):
        QSqlQueryModel.__init__(self)

    def setConn(self, conn):
        self.conn = conn

    def data(self, index, role):
        value = QSqlQueryModel.data(self, index, role)
        if role == Qt.BackgroundColorRole:
            if RegisterConst.recordExist(self.record(index.row())) == False:
                value = QColor('grey') 
        return value

    def flags(self, index):
        flags = QSqlQueryModel.flags(self, index)
        flags |= Qt.ItemIsEditable
        flags |= Qt.ItemIsEnabled
        flags |= Qt.ItemIsSelectable
        return flags

    def setData(self, index, value, role):
        bfId = self.data(QSqlQueryModel.index(self, index.row(), 0), Qt.DisplayRole)
        regId = self.data(QSqlQueryModel.index(self, index.row(), 1), Qt.DisplayRole)
        field = self.record().fieldName(index.column())
        query = QSqlQuery(self.conn)
        result = query.exec_("UPDATE Bitfield SET %s='%s' WHERE id=%s"%(field, value, bfId))
        if result:
            self.setQuery(self.query().executedQuery(), self.conn)
            self.dataChanged.emit(index, index, role)
        return result
