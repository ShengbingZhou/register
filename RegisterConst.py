from PySide2.QtCore import Qt

class RegisterConst:

    # tool version
    Version = "0.0.1-(alpha)"
    
    # style file
    StyleFile = "style/style.qss"

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
    NameRole        = Qt.UserRole + 1
    MemoryMapIdRole = Qt.UserRole + 2
    RegMapIdRole    = Qt.UserRole + 3
    RegIdRole       = Qt.UserRole + 4
    BfIdRole        = Qt.UserRole + 5
    BfEnumIdRole    = Qt.UserRole + 6
    RegMapTypeRole  = Qt.UserRole + 7 # check regmap type
    
    @staticmethod
    def recordExist(record):
        exist = str(record.value("Exist")).lower()
        if exist == '0' or exist == "n" or exist == 'no':
            return False
        else:
            return True
