from pyftdi.spi import SpiController

class QRegisterAccess:
    
    # Instantiate a SPI controller
    spi = SpiController()

    # Configure the first interface (IF/1) of the FTDI device as a SPI master
    spi.configure('ftdi://ftdi:2232h/1')

    # Get a port to a SPI slave w/ /CS on A*BUS3 and SPI mode 0 @ 12MHz
    slave = spi.get_port(cs=0, freq=12000000, mode=0)

    # Request the JEDEC ID from the SPI slave
    jedec_id = slave.exchange([0x9f], 3)
    
    def readReg(moduleName : str, addr : int) -> int:
        value = 0xaa55
        return value

    def writeReg(moduleName : str, addr : int, value : int) -> int:
        # write value
        return True