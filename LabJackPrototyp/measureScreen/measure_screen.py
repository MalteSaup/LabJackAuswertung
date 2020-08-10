import math
import threading

import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

import copy
import pandas as pd

import matplotlib.pyplot as plt

import export_screen

from measureScreen import measure_screen_plot_widget as mspw, measure_screen_settings_widget as mssw



class MeasureScreen(qt.QWidget):
    def __init__(self, supportClass, functionCode=0):
        super().__init__()
        plt.style.use("dark_background")
        self.ax_x = []
        self.ax_y = [[],
                     [],
                     [],
                     []
                     ]

        self.xue = []
        self.yue = []

        self.checkboxChecker = []

        self.supportClass = supportClass
        self.checkboxes = None
        self.pltLayout = None

        self.notStopped = True

        self.timer = None

        self.samplerate = 25
        self.functionCode = functionCode
        self.count = 0

        self.ls = "-"
        self.ms = "."

        self.mVtoV = 1000
        self.mAtoA = 1000
        self.uAtoV = 1e6

        self.minWidthWidget = 190

    def initUI(self):
        self.supportClass.container.saveAction.triggered.connect(self.saveClick)
        self.supportClass.container.saveAction.setEnabled(True)

        layout = qt.QHBoxLayout()

        self.checkboxes = mssw.Settings(self.functionCode)

        self.checkboxes.exitButton.pressed.connect(self.returnToMainScreen)
        self.checkboxChecker.append(self.checkboxes.leftCheck.checkBoxes[1])
        self.checkboxChecker.append(self.checkboxes.rightCheck.checkBoxes[1])
        self.checkboxChecker.append(self.checkboxes.leftCheck.checkBoxes[2])
        self.checkboxChecker.append(self.checkboxes.rightCheck.checkBoxes[2])
        self.checkboxChecker.append(self.checkboxes.leftCheck.checkBoxes[0])
        self.checkboxChecker.append(self.checkboxes.rightCheck.checkBoxes[0])

        self.pltLayout = mspw.MeasureScreenPlot(self.ax_x, self.ax_y, self.checkboxChecker, self.functionCode)

        layout.addWidget(self.checkboxes)
        layout.addWidget(self.pltLayout)

        self.samplerate = int(1000 / self.samplerate)

        if self.functionCode == 0:
            self.measureClock()
        elif self.functionCode == 1:
            self.checkboxes.comboBox.currentIndexChanged.connect(self.checkboxLayoutManipulator)
            self.checkboxes.startMeasureButton.pressed.connect(self.startMeasure)

        self.checkboxes.setFixedWidth(self.minWidthWidget)
        qtcore.QTimer.singleShot(300, lambda: self.resizeWidgets())
        self.setLayout(layout)

    def resizeEvent(self, a0: qtgui.QResizeEvent) -> None:
        self.resizeWidgets()
        super().resizeEvent(a0)

    def resizeWidgets(self):
        width = self.supportClass.container.geometry().width()
        height = self.supportClass.container.geometry().height() * 0.9
        if (width / 5) < self.minWidthWidget:
            newWidthCanvas = width - self.minWidthWidget
        else:
            newWidthCanvas = width * 4 / 5
        if self.pltLayout is not None:
            self.pltLayout.canvas.setGeometry(0, 0, newWidthCanvas, height)

    def updateDataset(self, index):
        if self.notStopped:
            uebergabe = self.supportClass.device.readRegister(0, 26)

            for i in range(4):
                # Da 1000 mV und 1000 Ohm kann Berechnung vernachlässigt werden da 1000 / 1000 = 1
                #TODO ADDING UNIT AND RESISTANCE AS VARIABLE TO CALCULATE IT WITH DIFFERENT UNITS AND RESISTANCE. MAYBE INPUT FIELD UNTER COMBOBOXES
                if self.checkboxChecker[i].isChecked():
                    if i <= 1:
                        self.ax_y[i].append(abs(uebergabe[i*2] - uebergabe[i*2+1]))
                    elif i == 2:
                        self.ax_y[i].append(abs(uebergabe[4] - uebergabe[6]))
                    elif i == 3:
                        self.ax_y[i].append(abs(uebergabe[5] - uebergabe[7]))
                else:
                    self.ax_y[i].append(math.nan)
            if self.functionCode == 0:
                self.ax_x.append(self.count)
                self.count += 1
            elif self.functionCode == 1:
                if index <= 1:
                    self.ax_x.append(abs(uebergabe[index * 2] - uebergabe[index * 2 + 1]) * self.mVtoV)
                elif index == 2:
                    self.ax_x.append(abs(uebergabe[4] - uebergabe[6]) * self.mVtoV)
                elif index == 3:
                    self.ax_x.append(abs(uebergabe[5] - uebergabe[7]) * self.mVtoV)



    def checkboxLayoutManipulator(self):
        for i in range(4):
            type(self.checkboxChecker[i])
            self.checkboxChecker[i].setEnabled(True)
        index = self.checkboxes.comboBox.currentIndex()
        if index % 2 == 1:
            self.checkboxes.rightCheck.checkBoxes[1 + int(index / 3)].setCheckState(False)
            self.checkboxes.rightCheck.checkBoxes[1 + int(index / 3)].setEnabled(False)
        else:
            self.checkboxes.leftCheck.checkBoxes[1 + int(index / 2)].setCheckState(False)
            self.checkboxes.leftCheck.checkBoxes[1 + int(index / 2)].setEnabled(False)

    def startMeasure(self):
        try:
            index = self.checkboxes.comboBox.currentIndex()
        except:
            index = -1
        self.checkboxes.comboBox.setEnabled(False)
        self.t = threading.Thread(target=self.measureClock(index))
        self.t.start()

    def measureClock(self, index=-1):
        self.timer = qtcore.QTimer(self)
        self.timer.timeout.connect(lambda: self.updateDataset(index))
        self.timer.start(self.samplerate)

    def saveClick(self):
        self.notStopped = False
        df, fig = self.createExportData()
        if df is None and fig is None:
            pass
        else:
            self.notStopped = True
            self.exportScreen = export_screen.ExportScreen(df, fig)
            self.exportScreen.show()

    def returnToMainScreen(self):
        if self.timer is not None:
            self.timer.stop()

        if self.pltLayout.timer is not None:
            self.pltLayout.timer.stop()

        self.pltLayout.stopped = True
        self.supportClass.returnToMainScreen()

    def createExportData(self):
        if self.pltLayout.checkXYLength()[0]:
            x_ueb = list(self.ax_x)
            y_ueb = copy.deepcopy(self.ax_y)
            fig_ueb = self.pltLayout.canvas.figure
            dataFrame = pd.DataFrame()
            dataFrame.insert(0, "x0", x_ueb, True)
            empty_ueb_arr = [math.nan] * len(x_ueb)
            count = 0
            for i in range(len(y_ueb)):
                if self.checkboxChecker[i].isChecked():
                    dataFrame.insert(len(dataFrame.columns), "y" + str(count), y_ueb[i], True)
                    count += 1
                else:
                    dataFrame.insert(len(dataFrame.columns), "ye" + str(i), empty_ueb_arr, True)

            return dataFrame, fig_ueb
        else:
            timerCreateExData = qtcore.QTimer(self)
            timerCreateExData.timeout.connect(self.saveClick)
            timerCreateExData.setSingleShot(True)
            timerCreateExData.start(100)
            return None, None


