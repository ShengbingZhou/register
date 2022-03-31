from PySide2.QtSql import QSqlTableModel
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor
from RegisterConst import RegisterConst

class QSqlHighlightTableModel(QSqlTableModel):

    def __init__(self, parent=None, conn=None):
        super(QSqlHighlightTableModel, self).__init__(parent, conn)

    def data(self, index, role):
        value = QSqlTableModel.data(self, index, role)
        if role == Qt.BackgroundColorRole:
            if RegisterConst.recordExist(QSqlTableModel.record(self, index.row())) == False:
                value = QColor('lightgrey')
        return value

    def flags(self, index):
        return QSqlTableModel.flags(self, index)

    def setParentId(self, id):
        self.parentId = id
