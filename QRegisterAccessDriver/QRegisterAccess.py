class QRegisterAccess:
    
    def readReg(addr : int) -> int:
        value = 0xaa55
        return value

    def writeReg(addr : int, value : int) -> int:
        # write value
        return True