# built-in package
import os
import sys
import re

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
    Version = "0.0.5-(alpha)"
    
    # Base Directory
    BaseDir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))

    # style file
    StyleFile = os.path.join(BaseDir, "style/style.qss")

    # design file ext
    DesignFileExt = ".reg"
    
    # reg access log file ext
    RegLogFileExt = ".log"
    
    # tab type const
    WelcomeTab = 0
    ModuleTab  = 1
    RegLogTab  = 2
    
    # module view const
    DesignView  = 0
    DebugView   = 1

    # regmap type
    RegMap = 0
    RegMod = 1

    # reg access value option
    RegAccessTypes = ['r', 'w', 'rw', 'rc', 'wc']

    # special role for treeview item
    TableNameRole  = Qt.UserRole + 1
    infoIdRole     = Qt.UserRole + 2
    MemMapIdRole   = Qt.UserRole + 3
    RegMapIdRole   = Qt.UserRole + 4
    RegIdRole      = Qt.UserRole + 5
    BfIdRole       = Qt.UserRole + 6
    BfEnumIdRole   = Qt.UserRole + 7
    RegMapTypeRole = Qt.UserRole + 8

    # hardware access driver
    RegisterAccessDriverClass= None
    
    # value column index in debug view
    ValueColumnOfDebugView = 3

    @staticmethod
    def strToInt(text):
        if text is None:
            return 0
        if text.startswith("0x"):         # 0x1234
            return int(text, 16)
        if text.startswith("'h"):         # 'h1234
            text = text.replace("'h", "")
            return int(text, 16)
        if text.startswith("'d"):
            text = text.replace("'d", "") # 'd1234
            return int(text)
        if text.startswith("'b"):
            text = text.replace("'b", "") # 'b1011
            return int(text, 2)
        if "'h" in text:                  # 16'h1234
            t = text.split("'h")
            return int(t[1], 16)
        if "'d" in text:                  # 16'd1234
            t = text.split("'d")
            return int(t[1])
        if "'b" in text:                  # 16'b1011
            t = text.split("'b")
            return int(t[1], 2)
        return int(text)

    @staticmethod
    def recordExist(record):
        exist = record.value("Exist")
        if exist is None:
            return True
        else:
            if exist == '0' or exist == "n" or exist == 'no':
                return False
            else:
                return True

    @staticmethod
    def findRegAccessDriverClass():
        if QRegisterConst.RegisterAccessDriverClass is None:
            if os.path.isfile(QDir.homePath() + "/QRegisterAccessDriver/QRegisterAccess.py"):        
                DriverPath  = QDir.homePath() + "/QRegisterAccessDriver"
                sys.path.append(DriverPath)
                DriverMod   = __import__("QRegisterAccess")
                QRegisterConst.RegisterAccessDriverClass = getattr(DriverMod, "QRegisterAccess")        

    @staticmethod
    def genColoredRegBitsUsage(conn, bfId, regId, regW, fontSize):
        if regW == None:
            return

        bfColorsIndex = 0
        bfColors  = ["DarkSeaGreen",  "LightSalmon",     "PowderBlue",     "LightPink",      "Aquamarine",     "Bisque",         "LightSteelBlue", "DarkKhaki"]         
        bfQColors = [QColor(0x8FBC8F), QColor(0xFFA07A), QColor(0xB0E0E6), QColor(0xFFB6C1), QColor(0x66CDAA), QColor(0xFFE4C4), QColor(0xB0C4DE), QColor(0xBDB76B)]
        value = []

        regW = int(regW)
        regB = regW - 1
        bfQuery = QSqlQuery("SELECT * FROM Bitfield WHERE RegisterId=%s ORDER BY CAST(RegisterOffset as int) DESC"%(regId), conn)
        while bfQuery.next():
            _bfId   = bfQuery.value("id")
            _regOff = QRegisterConst.strToInt(bfQuery.value("RegisterOffset"))
            _bfW    = int(bfQuery.value("Width"))

            # unused bits before bitfield 
            if _bfW > 0 and regB > (_regOff + _bfW - 1):
                text  = ""
                start = _regOff + _bfW
                end   = regB + 1
                for i in range(start, end):
                    text += "%s,"%(regB) if i < (end - 1) and regB > 0 else "%s"%(regB)
                    regB -= 1
                    if regB < 0:
                        break
                value.append((None, text))

            # bitfield bits
            if _bfW > 0 and regB >= 0:
                text = ""
                start = _regOff
                end   = _regOff + _bfW               
                for j in range(_regOff, _regOff + _bfW):                    
                    text += "%s,"%(regB) if j < (end - 1) and regB > 0 else "%s"%(regB)
                    regB -= 1
                    if regB < 0:
                        break
                if bfId == _bfId:
                    value.append((bfQColors[bfColorsIndex], text, _bfId, 1))
                else:
                    value.append((bfQColors[bfColorsIndex], text, _bfId))
                bfColorsIndex = 0 if (bfColorsIndex + 1) >= len(bfQColors) else bfColorsIndex + 1

        # left unsed bits
        if regB >= 0:
            text = ""
            for k in range(0, regB + 1):
                text += "%s,"%(regB) if regB > 0 else "%s"%(regB)
                regB -= 1
            value.append((None, text))

        return value

    @staticmethod
    def genRegValueFromBitfields(conn, regId):
        regValue = 0
        bfQuery = conn.exec_("SELECT * FROM Bitfield WHERE RegisterId=%s"%(regId))
        while bfQuery.next():
            regOff    = QRegisterConst.strToInt(bfQuery.value("RegisterOffset"))
            bfDefault = QRegisterConst.strToInt(bfQuery.value("DefaultValue"))
            regValue += bfDefault << regOff
        return regValue

    @staticmethod
    def exporDocx(parent, conn):
        fileName, filterUsed = QFileDialog.getSaveFileName(parent, "Export Word file", QDir.homePath(), "Word File (*.docx)")
        if fileName == '':           
            return
        
        try:
            f_name, f_ext = os.path.splitext(os.path.basename(fileName))
            # add .docx
            if f_ext != ".docx":
                fileName += ".docx"
            docx = Document()
            docx.styles['Heading 1'].font.size = shared.Pt(11)
            docx.styles['Heading 2'].font.size = shared.Pt(10)
            docx.styles['Heading 3'].font.size = shared.Pt(9)
            docx.styles['Heading 4'].font.size = shared.Pt(8)
            docx.styles['Normal'].font.size    = shared.Pt(8)
                        
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
                    table = docx.add_table(1, cols=len(fields), style='Table Grid')
                    for c, (cell, field) in enumerate(zip(table.rows[0].cells, fields)):
                        cell.text = fields[c]
                        cell._tc.get_or_add_tcPr().append(oxml.parse_xml(r'<w:shd {} w:fill="c0c0c0"/>'.format(oxml.ns.nsdecls('w'))))
                    regRe = re.compile('\d+:\d+')                
                    for r in range(regQueryModel.rowCount()):
                        regRecord = regQueryModel.record(r)
                        regWidth = int(regRecord.value("Width"))
                        regDesc = regRecord.value("Description")
                        regMatch = regRe.match(regRecord.value("Array"))
                        if regMatch is None:
                            regName = regRecord.value("Name")
                            regAddr = "%s"%regRecord.value("OffsetAddress")                        
                            row = table.add_row()
                            row.cells[0].text = regName
                            row.cells[1].text = regAddr
                            row.cells[2].text = regDesc                        
                        else:                        
                            regArray = regMatch.string.split(':')
                            regArray0 = int(regArray[0])
                            regArray1 = int(regArray[1])
                            start = min(regArray0, regArray1)
                            end   = max(regArray0, regArray1)
                            for regI in range(start, end + 1):
                                regName = "%s%s"%(regRecord.value("Name"), regI)
                                regAddr = hex(QRegisterConst.strToInt(regRecord.value("OffsetAddress")) + int(regWidth * (regI - start) / 8))
                                row = table.add_row()
                                row.cells[0].text = regName
                                row.cells[1].text = regAddr
                                row.cells[2].text = regDesc

                    for k in range(regQueryModel.rowCount()):
                        regRecord = regQueryModel.record(k)
                        regMatch = regRe.match(regRecord.value("Array"))
                        if regMatch is None:
                            docx.add_heading('Register: %s'%(regRecord.value("Name")), level = 4)
                            docx.add_paragraph('Description : %s\n' \
                                            'Address : %s'%(regRecord.value("Description"), regRecord.value("OffsetAddress")))
                        else:
                            regArray = regMatch.string.split(':')
                            regArray0 = int(regArray[0])
                            regArray1 = int(regArray[1])
                            start = min(regArray0, regArray1)
                            end   = max(regArray0, regArray1)
                            regAddrStart = hex(QRegisterConst.strToInt(regRecord.value("OffsetAddress")))
                            regAddrend   = hex(QRegisterConst.strToInt(regRecord.value("OffsetAddress")) + int(regWidth * (end - start) / 8))
                            docx.add_heading('Register: %s%s ~ %s%s'%(regRecord.value("Name"), start, regRecord.value("Name"), end), level = 4)
                            docx.add_paragraph('Description : %s\n' \
                                            'Address : %s ~ %s'%(regRecord.value("Description"), regAddrStart, regAddrend))

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
                                        cell.text = "[%s:%s]"%(int(bfRecord.value("Width")) + QRegisterConst.strToInt(bfRecord.value("RegisterOffset")) - 1, QRegisterConst.strToInt(bfRecord.value("RegisterOffset")))
                                    if field == 'ResetValue':
                                        cell.text = "%s"%(bfRecord.value("DefaultValue"))
                                    if field == 'Description':
                                        cell.text = bfRecord.value("Description")
                    docx.add_page_break()
            docx.add_page_break()
            docx.save(fileName)
            dlgProgress.close()
        except BaseException as e:
            QMessageBox.warning(parent, "Exporting docx", str(e), QMessageBox.Yes)
            return
        QMessageBox.information(parent, "Exporting docx", "Done!", QMessageBox.Yes)
        return