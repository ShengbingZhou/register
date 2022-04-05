# built-in package
import os

# pyside2 package
from PySide2.QtWidgets import QFileDialog, QMessageBox
from PySide2.QtCore import Qt, QDir
from PySide2.QtSql import QSqlQuery, QSqlQueryModel

# python-docx package
from docx import Document, oxml, shared
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Inches

class QRegisterConst:

    # tool version
    Version = "0.0.2-(alpha)"
    
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

    # special role
    NameRole       = Qt.UserRole + 1
    MemMapIdRole   = Qt.UserRole + 2
    RegMapIdRole   = Qt.UserRole + 3
    RegIdRole      = Qt.UserRole + 4
    BfIdRole       = Qt.UserRole + 5
    BfEnumIdRole   = Qt.UserRole + 6
    RegMapTypeRole = Qt.UserRole + 7
    
    @staticmethod
    def recordExist(record):
        exist = str(record.value("Exist")).lower()
        if exist == '0' or exist == "n" or exist == 'no':
            return False
        else:
            return True

    @staticmethod
    def genColoredRegBitsUsage(conn, bfId, regId, regW, fontSize):
        bfColors = ["LightSalmon", "PowderBlue", "LightPink", "Aquamarine", "Bisque", "LightBlue", "DarkKhaki", "DarkSeaGreen"] 
        bfColorsIndex = 0
        if regW == None:
            return None
        regB = regW - 1
        text = ""
        bfQuery = QSqlQuery("SELECT * FROM Bitfield WHERE RegisterId=%s ORDER BY RegisterOffset DESC"%(regId), conn)
        while bfQuery.next():
            _regOff = bfQuery.value("RegisterOffset")
            _bfW  = bfQuery.value("Width")
            _bfId = bfQuery.value("id")

            # unused bits before bitfield 
            if _bfW > 0 and regB > (_regOff + _bfW - 1):
                if fontSize != None:
                    text += "<span style='font-size:%spx'>"%fontSize 
                for i in range(_regOff + _bfW, regB + 1):
                    if regB > (_regOff + _bfW):
                        text += "%s "%(regB) if (regW < 10 or regB > 9) else "%s "%(regB)
                    else:
                        text += "%s"%(regB) if (regW < 10 or regB > 9) else "%s"%(regB)
                    regB -= 1
                    if regB < 0:
                        break
                if fontSize != None:
                    text += " </span>"
                else:
                    text += " "

            # bitfield bits
            if _bfW > 0 and regB >= 0:
                if _bfId == bfId:
                    if fontSize != None:
                        text += "<span style='font-size:%spx;background-color:%s;font-weight:bold;color:red'>"%(fontSize, bfColors[bfColorsIndex])
                    else:
                        text += "<span style='background-color:%s;font-weight:bold;color:red'>"%(bfColors[bfColorsIndex])
                else:
                    if fontSize != None:
                        text += "<span style='font-size:%spx;background-color:%s'>"%(fontSize, bfColors[bfColorsIndex])
                    else:
                        text += "<span style='background-color:%s'>"%(bfColors[bfColorsIndex])
                bfColorsIndex = 0 if (bfColorsIndex + 1) >= len(bfColors) else bfColorsIndex + 1
                for j in range(_regOff, _regOff + _bfW):
                    if j < (_regOff + _bfW - 1):
                        text += "%s "%(regB) if (regW < 10 or regB > 9) else "%s "%(regB)
                    else:
                        text += "%s"%(regB) if (regW < 10 or regB > 9) else "%s"%(regB)
                    regB -= 1
                    if regB < 0:
                        break
                text += "</span>"
                if regB >= 0:
                    text += "<span style='font-size:%spx'> </span>"%fontSize if fontSize != None else " "

        # left unsed bits
        if regB >= 0:
            if fontSize != None:
                text += "<span style='font-size:%spx'>"%fontSize
            for k in range(0, regB + 1):
                text += "%s "%(regB) if (regW < 10 or regB > 9) else "%s "%(regB)
                regB -= 1
            if fontSize != None:
                text += "</span>"
        return text

    @staticmethod
    def exporDocx(parent, conn):
        fileName, filterUsed = QFileDialog.getSaveFileName(parent, "Export Word file", QDir.homePath(), "Word File (*.docx)")
        if fileName !='':
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

            for i in range(memoryMapQueryModel.rowCount()):
                memMapRecord = memoryMapQueryModel.record(i)
                docx.add_heading('MemoryMap: %s'%(memMapRecord.value("Name")), level = 2)

                # register map
                regMapQueryModel = QSqlQueryModel()
                regMapQueryModel.setQuery("SELECT * FROM RegisterMap WHERE memoryMapId=%s ORDER BY DisplayOrder ASC"%memMapRecord.value("id"), conn)
                for j in range(regMapQueryModel.rowCount()):
                    regMapRecord = regMapQueryModel.record(j)
                    docx.add_heading('RegisterMap: %s'%(regMapRecord.value("Name")), level = 3)
                    docx.add_paragraph("Description : %s\n" \
                                       "BaseAddress : %s"%(regMapRecord.value("Description"), regMapRecord.value("OffsetAddress")))

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
                                        cell.text = "[%s:%s]"%(bfRecord.value("Width") + bfRecord.value("RegisterOffset")-1, bfRecord.value("RegisterOffset"))
                                    if field == 'ResetValue':
                                        cell.text = "%s"%(bfRecord.value("DefaultValue"))
                                    if field == 'Description':
                                        cell.text = bfRecord.value("Description")
                    docx.add_page_break()
            docx.add_page_break()
            docx.save(fileName)
            QMessageBox.information(parent, "Exporting docx", "Done!", QMessageBox.Yes)
        return