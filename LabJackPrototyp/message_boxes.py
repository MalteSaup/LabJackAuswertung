import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui

class ReturnMessageBox(qt.QMessageBox):
    def __init__(self):
        super().__init__()
        self.showUi()

    def showUi(self):
        self.setIcon(qt.QMessageBox.Question)
        self.setText("When you return, all unsafed Data will be lost. Do you really want to return?")
        self.setWindowIcon(qtgui.QIcon("./images/icon.ico"))
        self.setWindowTitle("HAW Labjack")
        self.setStandardButtons(qt.QMessageBox.Ok | qt.QMessageBox.Cancel)

class SaveErrorPermissionDeniedBox(qt.QMessageBox):
    def __init__(self):
        super().__init__()
        self.showUi()

    def showUi(self):
        self.setIcon(qt.QMessageBox.Warning)
        self.setText("ERROR WHILE SAVING. You do not have the Permission to save this file. Maybe you have opened it somewhere.")
        self.setWindowTitle("HAW LabJack")
        self.setWindowIcon(qtgui.QIcon("./images/icon.ico"))
        self.setStandardButtons(qt.QMessageBox.Ok)

class SomethingWentWrongBox(qt.QMessageBox):
    def __init__(self):
        super().__init__()
        self.showUi()

    def showUi(self):
        self.setIcon(qt.QMessageBox.Warning)
        self.setText("Ops Something Went Wrong. Maybe try it again")
        self.setWindowTitle("HAW LabJack")
        self.setWindowIcon(qtgui.QIcon("./images/icon.ico"))
        self.setStandardButtons(qt.QMessageBox.Ok)

class ConnectionLostBox(qt.QMessageBox):
    def __init__(self):
        super().__init__()
        self.showUi()

    def showUi(self):
        self.setIcon(qt.QMessageBox.Warning)
        self.setText("Your Connection to the LabJack U6 was interrupted. The measurement was stopped. Try Reconnect or Save your Data.")
        self.setWindowTitle("HAW LabJack")
        self.setWindowIcon(qtgui.QIcon("./images/icon.ico"))
        self.setStandardButtons(qt.QMessageBox.Ok)
