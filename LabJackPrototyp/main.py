import os

import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

import pandas as pd

import main_screen
import support_class
import measure_screen
import export_screen

class Fenster(qt.QMainWindow):
    def __init__(self):
        super().__init__()
        self.layout = None
        self.initUI()
        self.supportClass = None

    def initUI(self):
        self.setWindowTitle("HAW LabJack")
        self.setWindowIcon(qtgui.QIcon("icon.ico"))
        self.statusBar().showMessage("Connection State: Not Connected")

        self.menu = self.menuBar()

        self.openAction = qt.QAction("Open Data")
        self.openAction.triggered.connect(lambda: print("Open"))
        self.openAction.setShortcut("Ctrl+O")

        self.saveAction = qt.QAction("Save Data")
        #self.saveAction.triggered.connect(self.saveClick)
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAction.setEnabled(False)

        self.file = self.menu.addMenu("&File")
        self.file.addAction(self.openAction)
        self.file.addAction(self.saveAction)

        self.supportClass = support_class.SupportClass(self.statusBar(), self)

        mainScreen = main_screen.MainScreen(self.supportClass)
        mainScreen.initUI()
        #mainScreen = measure_screen.LayoutCompiler(self.supportClass)
        self.setCentralWidget(mainScreen)
        #self.takeCentralWidget()
        self.show()
        print(self.geometry().width())


    def saveClick(self):
        self.exportScreen = export_screen.ExportScreen(self)
        self.exportScreen.show()

    def replaceCentralWidget(self, newWidget):
        print("H")
        self.takeCentralWidget()
        self.setCentralWidget(newWidget)



app = qt.QApplication([])
w = Fenster()

os._exit(app.exec_())