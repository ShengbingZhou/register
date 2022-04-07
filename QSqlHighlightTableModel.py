from PySide2.QtSql import QSqlTableModel, QSqlQuery
from PySide2.QtCore import Qt, QRect, QSize
from PySide2.QtGui import QColor, QTextDocument, QBrush, QFontMetrics
from PySide2.QtWidgets import QWidget, QStyledItemDelegate, QStyle, QStyleOptionViewItem, QApplication
from QRegisterConst import QRegisterConst

class QSqlHighlightTableModel(QSqlTableModel):

    def __init__(self, parent=None, conn=None):
        super(QSqlHighlightTableModel, self).__init__(parent, conn)

    def data(self, index, role):
        value = QSqlTableModel.data(self, index, role)
        if role == Qt.BackgroundColorRole:
            if QRegisterConst.recordExist(QSqlTableModel.record(self, index.row())) == False:
                value = QColor('grey')
        return value

    def flags(self, index):
        return QSqlTableModel.flags(self, index)

    def setParentId(self, id):
        self.parentId = id

class QRegValueDisplayDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent: QWidget, option, index):
        return

    def setEditorData(self, editor, index):
        self.value = index.model().data(index, Qt.DisplayRole)

    def setModelData(self, editor, model, index):
        model.setData(index, self.value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        return editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        self.initStyleOption(option, index)

        record = index.model().record(index.row())
        regId = record.value("id")
        regW  = record.value("Width")
        value  = QRegisterConst.genColoredRegBitsUsage(index.model().database(), None, regId, regW, None)

        margin = 5
        fm = QFontMetrics(option.font)
        pixelsWide = fm.width(" ZB ")
        rect = QRect(option.rect.left() + margin, option.rect.top() + margin, pixelsWide, option.rect.height() -  2 * margin)

        defaultBrush = painter.brush()
        transparent  = QColor(0,0,0,0)
        for i in range(len(value)):
            digits = value[i][1].split(',')
            if value[i][0] is None:
                painter.setBrush(defaultBrush)
            else:
                painter.setBrush(QBrush(value[i][0]))
            for d in digits:
                painter.setPen(transparent)
                painter.drawRect(rect)
                painter.setPen(defaultBrush.color())
                painter.drawText(rect, Qt.AlignCenter, d)
                rect.setX(rect.x() + pixelsWide + 1)
                rect.setWidth(pixelsWide)
        painter.setPen(defaultBrush.color())
        painter.setBrush(defaultBrush)

    def sizeHint(self, option, index):
        record = index.model().record(index.row())
        bits = int(record.value("Width"))
        fm = QFontMetrics(option.font)
        pixelsWide = fm.width(" ZB ") + 1
        w = pixelsWide * bits + 10 # 2*margin + bits * bits width
        h = option.rect.height()
        return QSize(w, h)
