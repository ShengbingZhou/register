from PySide2.QtSql import QSqlTableModel
from PySide2.QtCore import Qt, QRect, QSize
from PySide2.QtGui import QColor, QBrush, QFontMetrics
from PySide2.QtWidgets import QComboBox, QWidget, QStyledItemDelegate, QItemDelegate
from QRegisterConst import QRegisterConst

class QSqlHighlightTableModel(QSqlTableModel):
    def __init__(self, parent=None, conn=None):
        super(QSqlHighlightTableModel, self).__init__(parent, conn)
        self.parentId = None

    def data(self, index, role):
        value = QSqlTableModel.data(self, index, role)
        #if role == Qt.BackgroundColorRole:
        #    if QRegisterConst.recordExist(QSqlTableModel.record(self, index.row())) == False:
        #        value = QColor('grey')
        if role == Qt.TextColorRole:
            if QRegisterConst.recordExist(QSqlTableModel.record(self, index.row())) == False:
                value = QColor('grey')
        if role == Qt.DisplayRole:
            tableName = index.model().tableName()
            if tableName == "Register":
                fieldName = index.model().record().fieldName(index.column())
        if role == Qt.CheckStateRole:
            tableName = index.model().tableName()
            if tableName == "Bitfield":
                fieldName = index.model().record().fieldName(index.column())
        return value

    def flags(self, index):
        flags = QSqlTableModel.flags(self, index)
        return flags

    def setParentId(self, id):
        self.parentId = id

class QNoEditorColumnDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent: QWidget, option, index):          
        # no editor
        return None

class QRegTableColumnDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent: QWidget, option, index):
        # no editor for "Exist" and "Value"
        return None

    def updateEditorGeometry(self, editor, option, index):
        return editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        fieldName = index.model().record().fieldName(index.column())        
        if fieldName == 'Value':
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
                    if rect.x() +  pixelsWide > option.rect.left() + option.rect.width():
                        break
                    painter.setPen(transparent)
                    painter.drawRect(rect)
                    painter.setPen(defaultBrush.color())
                    painter.drawText(rect, Qt.AlignCenter, d)
                    rect.setX(rect.x() + pixelsWide + 1)
                    rect.setWidth(pixelsWide)
            painter.setPen(defaultBrush.color())
            painter.setBrush(defaultBrush)
        else:
            QStyledItemDelegate.paint(self, painter, option, index)            
        return

    def sizeHint(self, option, index):
        fieldName = index.model().record().fieldName(index.column())        
        if fieldName == 'Value':        
            record = index.model().record(index.row())
            bits = int(record.value("Width"))
            fm = QFontMetrics(option.font)
            pixelsWide = fm.width(" ZB ") + 1
            w = pixelsWide * bits + 10 # bitwidth*bits + 2*margin 
            h = option.rect.height()
            return QSize(w, h)
        else:
            return QStyledItemDelegate.sizeHint(self, option, index)
