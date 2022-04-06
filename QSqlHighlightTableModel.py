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
        if role == Qt.DisplayRole:
            if self.tableName() == "Register":
                field = self.record().fieldName(index.column())
                if field == "Value": # show bitfield usage info in this column
                    regId = self.record(index.row()).value("id")
                    regW  = self.record(index.row()).value("Width")
                    value  = QRegisterConst.genColoredRegBitsUsage(self.database(), None, regId, regW, None)
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
        value = index.data()
        margin = 5
        
        fm = QFontMetrics(painter.font())
        pixelsWide = fm.width(" ZB ")
        rect = QRect(option.rect.left() + margin, option.rect.top() + margin, pixelsWide, option.rect.height() - 2*margin)

        defaultBrush = painter.brush()
        #defaultPen = painter.pen()
        for i in range(len(value)):
            digits = value[i][1].split(',')
            for d in digits:
                if value[i][0] is None:
                    painter.setPen(defaultBrush.color())
                    painter.setBrush(defaultBrush)
                else:
                    painter.setPen(value[i][0])
                    painter.setBrush(QBrush(value[i][0]))
                painter.drawRect(rect)
                painter.setPen(defaultBrush.color())
                painter.setBrush(defaultBrush)
                painter.drawText(rect, Qt.AlignCenter, d)
                rect.setX(rect.x() + pixelsWide + 2)
                rect.setWidth(pixelsWide)
        
    def sizeHint(self, option, index):
        options = option
        self.initStyleOption(options, index)
        doc = QTextDocument()
        doc.setHtml(options.text)
        doc.setTextWidth(-1)
        return QSize(doc.idealWidth(), doc.size().height())
