class QRegisterAccess:
    
    def readReg(moduleName : str, addr : int) -> int:
        value = 0xaa55
        return value

    def writeReg(moduleName : str, addr : int, value : int) -> int:
        # write value
        return True