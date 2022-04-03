from PySide2.QtCore import Qt
from PySide2.QtSql import QSqlQuery

class RegisterConst:

    # tool version
    Version = "0.0.1-(alpha)"
    
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
    RegMapTypeRole = Qt.UserRole + 7 # check regmap type
    
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
                        text += "%s "%(regB) if (regW < 10 or regB > 9) else "0%s "%(regB)
                    else:
                        text += "%s"%(regB) if (regW < 10 or regB > 9) else "0%s"%(regB)
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
                        text += "%s "%(regB) if (regW < 10 or regB > 9) else "0%s "%(regB)
                    else:
                        text += "%s"%(regB) if (regW < 10 or regB > 9) else "0%s"%(regB)
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
                text += "%s "%(regB) if (regW < 10 or regB > 9) else "0%s "%(regB)
                regB -= 1
            if fontSize != None:
                text += "</span>"
        return text
