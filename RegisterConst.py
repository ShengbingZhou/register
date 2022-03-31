from PySide2.QtCore import Qt

class RegisterConst:

    # Tool version
    Version = "0.0.1-(alpha)"

    # welcome tab text const
    WelcomeTabText = "Welcome"
    
    # module view const
    DesignView  = 0
    DebugView   = 1

    # special role 
    NameRole        = Qt.UserRole + 1
    MemoryMapIdRole = Qt.UserRole + 2
    RegMapIdRole    = Qt.UserRole + 3
    RegIdRole       = Qt.UserRole + 4
    BfIdRole        = Qt.UserRole + 5
    BfEnumIdRole    = Qt.UserRole + 6
    
    @staticmethod
    def recordExist(record):
        exist = str(record.value("Exist")).lower()
        if exist == '0' or exist == "n" or exist == 'no':
            return False
        else:
            return True

