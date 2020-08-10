import PyQt5.QtWidgets as qt

class ReturnMessageBox(qt.QMessageBox):
    def __init__(self):
        super().__init__()
        self.showUi()

    def showUi(self):
        self.setIcon(qt.QMessageBox.Question)
        self.setText("When you return, all unsafed Data will be lost. Do you really want to return?")
        self.setWindowTitle("HAW Labjack")
        self.setStandardButtons(qt.QMessageBox.Ok | qt.QMessageBox.Cancel)