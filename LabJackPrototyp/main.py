import os

import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

import main_screen
import support_class


class MainWindow(qt.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        options = [
            "None",
            "Channel 1",
            "Channel 2",
            "Channel 3",
            "Channel 4"
        ]

        self.setWindowTitle("HAW LabJack")
        self.setWindowIcon(qtgui.QIcon("icon.ico"))
        self.statusBar().showMessage("Connection State: Not Connected")

        self.menu = self.menuBar()

        self.saveAction = qt.QAction("Save Data")
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAction.setEnabled(False)

        self.file = self.menu.addMenu("&File")
        self.file.addAction(self.saveAction)

        supportClass = support_class.SupportClass(self.statusBar(), self, options, screenGeometry)

        supportClass.returnToMainScreen()

        self.setMinimumWidth(570)

        self.show()

    def replaceCentralWidget(self, newWidget):
        self.takeCentralWidget()
        self.setCentralWidget(newWidget)


global screenGeometry
qt.QApplication.setAttribute(qtcore.Qt.AA_EnableHighDpiScaling)
app = qt.QApplication([])
screenGeometry = app.desktop().screenGeometry()                                                                         #reads resolution of screen
screenGeometry.setWidth(screenGeometry.width() * len(app.screens()))                                                    #multiplies width resolution of screen with amount of connected screens
w = MainWindow()

os._exit(app.exec_())