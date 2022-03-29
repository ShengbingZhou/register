from PySide2.QtSql import QSqlTableModel
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor
from QSqlBitfieldTableModel import QSqlBitfieldTableModel

class QCustomizedSqlTableModel(QSqlTableModel):

    def __init__(self, parent=None, conn=None):
        super(QCustomizedSqlTableModel, self).__init__(parent, conn)

    def data(self, index, role):
        value = QSqlTableModel.data(self, index, role)
        if role == Qt.BackgroundColorRole:
            if QSqlBitfieldTableModel.exist(QSqlTableModel.record(self, index.row())) == False:
                value = QColor('grey')
        return value

    def flags(self, index):
        return QSqlTableModel.flags(self, index)
