import os

from PySide2.QtWidgets import QWidget, QFileDialog, QMessageBox
from PySide2.QtCore import Qt, Slot, QDir
from ui.RegisterAccessLog import Ui_RegisterAccessWindow
from QRegisterConst import QRegisterConst

class uiRegAccessLogWindow(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_RegisterAccessWindow()
        self.ui.setupUi(self)
        self.ui.label.setText("")
        self.tabType = QRegisterConst.RegLogTab
        with open (QRegisterConst.StyleFile) as file:
            style = file.read()
        self.setStyleSheet(style)

    def setMainWindow(self, mainWindow):
        self.mainWindow = mainWindow

    def appendRegLog(self, line):
        self.ui.txtReg.append(line)
        
    @Slot()
    def on_pbClear_clicked(self):
        self.ui.txtReg.clear()

    @Slot()
    def on_pbOpen_clicked(self):
        fileName, filterUsed = QFileDialog.getOpenFileName(self, "Open reg access log file", QDir.homePath(), "Reg access log File (*%s)"%QRegisterConst.RegLogFileExt)
        if os.path.isfile(fileName):
            with open(fileName, 'r') as file:
                self.ui.txtReg.clear()
                self.ui.txtReg.setPlainText(file.read())

    @Slot()
    def on_pbSave_clicked(self):
        fileName, filterUsed = QFileDialog.getSaveFileName(self, "Save reg access log file", QDir.homePath(), "Reg Access Log File (*%s)"%QRegisterConst.RegLogFileExt)
        if fileName == '':
            return
        f_name, f_ext = os.path.splitext(os.path.basename(fileName))
        if f_ext != QRegisterConst.RegLogFileExt:
            fileName += QRegisterConst.RegLogFileExt
            with open(fileName, 'w') as file:
                file.write(str(self.ui.txtReg.toPlainText()))            

    @Slot()
    def on_pbRun_clicked(self):
        log = self.ui.txtReg.toPlainText()
        if QRegisterConst.RegisterAccessDriverClass is None:
            QRegisterConst.findRegAccessDriverClass()            
        if QRegisterConst.RegisterAccessDriverClass is not None:
            regAccessLines = log.split('\n')
            for regAccess in regAccessLines:
                param = regAccess.split(',')
                # DPTX2L, w, 00000058, 00000000, aux_dfp_rx_recv_data_0
                if len(param) == 5:
                    QRegisterConst.RegisterAccessDriverClass.writeReg(param[0], int(param[2], 16), int(param[3], 16))
            QMessageBox.information(self, "Running Register Log", "Done!", QMessageBox.Yes)