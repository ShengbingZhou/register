# built-in package
import os

# pyside2 package
from PySide2.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
from PySide2.QtCore import Qt, QDir, QCoreApplication
from PySide2.QtSql import QSqlQuery, QSqlQueryModel
from PySide2.QtGui import QColor

# python-docx package
from docx import Document, oxml, shared
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Inches

class QRegisterConst:

    # tool version
    Version = "0.0.4-(alpha)"
    
    # style file
    StyleFile = "style/style.qss"

    # design file externsion
    DesignFileExt = ".reg"

    # welcome tab text const
    WelcomeTabText = "Welcome"
    
    # module view const
    DesignView  = 0
    DebugView   = 1

    # regmap type
    RegMap = 0
    RegMod = 1

    # reg access value option
    RegAccessValues = ['r', 'w', 'rw', 'rc', 'wc']

    # special role for treeview item
    NameRole       = Qt.UserRole + 1
    infoIdRole     = Qt.UserRole + 2
    MemMapIdRole   = Qt.UserRole + 3
    RegMapIdRole   = Qt.UserRole + 4
    RegIdRole      = Qt.UserRole + 5
    BfIdRole       = Qt.UserRole + 6
    BfEnumIdRole   = Qt.UserRole + 7
    RegMapTypeRole = Qt.UserRole + 8
    
    @staticmethod
    def recordExist(record):
        exist = str(record.value("Exist")).lower()
        if exist == '0' or exist == "n" or exist == 'no':
            return False
        else:
            return True

    @staticmethod
    def genColoredRegBitsUsage(conn, bfId, regId, regW, fontSize):
        if regW == None:
            return

        regW = int(regW)
        
        bfColorsIndex = 0
        bfColors = ["DarkSeaGreen", "LightSalmon", "PowderBlue", "LightPink", "Aquamarine", "Bisque", "LightBlue", "DarkKhaki"] 
        
        bfQColors = [QColor(0x8FBC8F), QColor(0xFFA07A), QColor(0xB0E0E6), QColor(0xFFB6C1), QColor(0x66CDAA), QColor(0xFFE4C4), QColor(0xADD8E6), QColor(0xBDB76B)]
        value = []
            
        regB = regW - 1
        text = ""
        bfQuery = QSqlQuery("SELECT * FROM Bitfield WHERE RegisterId=%s ORDER BY CAST(RegisterOffset as int) DESC"%(regId), conn)
        while bfQuery.next():
            _bfId   = bfQuery.value("id")
            _regOff = int(bfQuery.value("RegisterOffset"))
            _bfW    = int(bfQuery.value("Width"))

            # unused bits before bitfield 
            if _bfW > 0 and regB > (_regOff + _bfW - 1):
                text = ""
                for i in range(_regOff + _bfW, regB + 1):
                    if regB > (_regOff + _bfW):
                        text += "%s,"%(regB)
                    else:
                        text += "%s"%(regB)
                    regB -= 1
                    if regB < 0:
                        break
                value.append((None, text))

            # bitfield bits
            if _bfW > 0 and regB >= 0:
                text = ""
                bfColorsIndex = 0 if (bfColorsIndex + 1) >= len(bfQColors) else bfColorsIndex + 1
                for j in range(_regOff, _regOff + _bfW):
                    if j < (_regOff + _bfW - 1):
                        text += "%s,"%(regB)
                    else:
                        text += "%s"%(regB)
                    regB -= 1
                    if regB < 0:
                        break
                value.append((bfQColors[bfColorsIndex], text))
                
        # left unsed bits
        if regB >= 0:
            text = ""
            for k in range(0, regB + 1):
                if k > 0:
                    text += "%s,"%(regB)
                else:
                    text += "%s"%(regB)
                regB -= 1
            value.append((None, text))

        return value

    @staticmethod
    def exporDocx(parent, conn):
        fileName, filterUsed = QFileDialog.getSaveFileName(parent, "Export Word file", QDir.homePath(), "Word File (*.docx)")
        if fileName == '':
            QMessageBox.warning(parent, "Exporting docx", "file name is empty.", QMessageBox.Yes)
            return

        f_name, f_ext = os.path.splitext(os.path.basename(fileName))
        # add .docx
        if f_ext != ".docx":
            fileName += ".docx"
        docx = Document()
        docx.styles['Heading 1'].font.size = shared.Pt(11)
        docx.styles['Heading 2'].font.size = shared.Pt(10)
        docx.styles['Heading 3'].font.size = shared.Pt(9)
        docx.styles['Heading 4'].font.size = shared.Pt(8)
        docx.styles['Normal'].font.size = shared.Pt(8)
                    
        # memory map
        memoryMapQueryModel = QSqlQueryModel()
        memoryMapQueryModel.setQuery("SELECT * FROM MemoryMap", conn)

        title = docx.add_heading('MemoryMap Table\n', level = 1)
        title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        fields = ['Name', 'Description']
        table = docx.add_table(rows=memoryMapQueryModel.rowCount() + 1, cols=len(fields), style='Table Grid')

        for i, row in enumerate(table.rows):
            for j, (cell, field) in enumerate(zip(row.cells, fields)):
                if i == 0: # table header
                    cell.text = fields[j]
                    cell._tc.get_or_add_tcPr().append(oxml.parse_xml(r'<w:shd {} w:fill="c0c0c0"/>'.format(oxml.ns.nsdecls('w'))))
                else:
                    memMapRecord = memoryMapQueryModel.record(i - 1)
                    if field == 'Name':
                        cell.text = memMapRecord.value("Name")
        docx.add_page_break()

        # setup progress dialog
        dlgProgress = QProgressDialog(parent)
        dlgProgress.setWindowTitle("Exporting ...")
        dlgProgress.setWindowModality(Qt.WindowModal)
        dlgProgress.setMinimum(0)
        dlgProgress.show()

        for i in range(memoryMapQueryModel.rowCount()):
            memMapRecord = memoryMapQueryModel.record(i)
            docx.add_heading('MemoryMap: %s'%(memMapRecord.value("Name")), level = 2)

            # register map
            regMapQueryModel = QSqlQueryModel()
            regMapQueryModel.setQuery("SELECT * FROM RegisterMap WHERE memoryMapId=%s ORDER BY DisplayOrder ASC"%memMapRecord.value("id"), conn)
            
            # progress dialog
            dlgProgress.setMaximum(memoryMapQueryModel.rowCount())
            dlgProgress.setValue(0)
            QCoreApplication.processEvents()              
            
            for j in range(regMapQueryModel.rowCount()):
                regMapRecord = regMapQueryModel.record(j)
                docx.add_heading('RegisterMap: %s'%(regMapRecord.value("Name")), level = 3)
                docx.add_paragraph("Description : %s\n" \
                                    "BaseAddress : %s"%(regMapRecord.value("Description"), regMapRecord.value("OffsetAddress")))

                # update progress dialog
                dlgProgress.setLabelText("Exporting register map '%s' to %s "%(regMapRecord.value("Name"), fileName))
                dlgProgress.setValue(j)
                QCoreApplication.processEvents()    

                # register
                regQueryModel = QSqlQueryModel()
                regQueryModel.setQuery("SELECT * FROM Register WHERE RegisterMapId=%s ORDER BY DisplayOrder ASC"%regMapRecord.value("id"), conn)

                fields = ['Name', 'Address', 'Description']
                table = docx.add_table(rows=regQueryModel.rowCount() + 1, cols=len(fields), style='Table Grid')
                for r, row in enumerate(table.rows):
                    for c, (cell, field) in enumerate(zip(row.cells, fields)):
                        if r == 0:
                            cell.text = fields[c]
                            cell._tc.get_or_add_tcPr().append(oxml.parse_xml(r'<w:shd {} w:fill="c0c0c0"/>'.format(oxml.ns.nsdecls('w'))))
                        else:
                            regRecord = regQueryModel.record(r - 1)
                            if field == 'Name':
                                cell.text = regRecord.value("Name")
                            if field == 'Address':
                                cell.text = "%s"%regRecord.value("OffsetAddress")
                            if field == 'Description':
                                cell.text = regRecord.value("Description")

                for k in range(regQueryModel.rowCount()):
                    regRecord = regQueryModel.record(k)
                    docx.add_heading('Register: %s'%(regRecord.value("Name")), level = 4)
                    docx.add_paragraph('Description : %s\n' \
                                        'Address : %s'%(regRecord.value("Description"), regRecord.value("OffsetAddress")))

                    # bitfield
                    bfQueryModel = QSqlQueryModel()
                    bfQueryModel.setQuery("SELECT * FROM Bitfield WHERE RegisterId=%s ORDER BY DisplayOrder ASC"%regRecord.value("id"), conn)

                    fields = ['Name', 'Bits', 'ResetValue', 'Description']
                    table = docx.add_table(rows=bfQueryModel.rowCount() + 1, cols=len(fields), style='Table Grid')
                    table.allow_autofit = True
                    for r, row in enumerate(table.rows):
                        for c, (cell, field) in enumerate(zip(row.cells, fields)):
                            if r == 0:
                                cell.text = fields[c]
                                cell._tc.get_or_add_tcPr().append(oxml.parse_xml(r'<w:shd {} w:fill="c0c0c0"/>'.format(oxml.ns.nsdecls('w'))))
                            else:
                                bfRecord = bfQueryModel.record(r - 1)
                                if field == 'Name':
                                    cell.text = bfRecord.value("Name")
                                if field == 'Bits':
                                    cell.text = "[%s:%s]"%(int(bfRecord.value("Width")) + int(bfRecord.value("RegisterOffset")) - 1, bfRecord.value("RegisterOffset"))
                                if field == 'ResetValue':
                                    cell.text = "%s"%(bfRecord.value("DefaultValue"))
                                if field == 'Description':
                                    cell.text = bfRecord.value("Description")
                docx.add_page_break()
        docx.add_page_break()
        docx.save(fileName)
        dlgProgress.close()
        QMessageBox.information(parent, "Exporting docx", "Done!", QMessageBox.Yes)
        return