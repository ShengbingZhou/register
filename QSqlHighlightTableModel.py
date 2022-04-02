from PySide2.QtSql import QSqlTableModel, QSqlQuery
from PySide2.QtCore import Qt, QRect, QSize
from PySide2.QtGui import QColor, QTextDocument, QAbstractTextDocumentLayout
from PySide2.QtWidgets import QWidget, QStyledItemDelegate, QStyle, QStyleOptionViewItem, QApplication
from RegisterConst import RegisterConst

class QSqlHighlightTableModel(QSqlTableModel):

    def __init__(self, parent=None, conn=None):
        super(QSqlHighlightTableModel, self).__init__(parent, conn)

    def data(self, index, role):
        value = QSqlTableModel.data(self, index, role)
        if role == Qt.BackgroundColorRole:
            if RegisterConst.recordExist(QSqlTableModel.record(self, index.row())) == False:
                value = QColor('lightgrey')
        if role == Qt.DisplayRole:
            if self.tableName() == "Register":
                field = self.record().fieldName(index.column())
                if field == "Value": # show bitfield usage info in this column
                    regId = self.record(index.row()).value("id")
                    regW  = self.record(index.row()).value("Width")
                    value  = RegisterConst.genColoredRegBitsUsage(self.database(), None, regId, regW, None)
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
        options = option
        self.initStyleOption(options,index)
        style = QApplication.style() if options.widget is None else options.widget.style()
        doc = QTextDocument()
        doc.setHtml(options.text)
        options.text = ""
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)
        ctx = QAbstractTextDocumentLayout.PaintContext()
        textRect = style.subElementRect(QStyle.SE_ItemViewItemText, options)
        painter.save()
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        options = option
        self.initStyleOption(options, index)
        doc = QTextDocument()
        doc.setHtml(options.text)
        doc.setTextWidth(-1)
        return QSize(doc.idealWidth(), doc.size().height())
