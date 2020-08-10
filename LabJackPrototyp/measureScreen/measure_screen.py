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
        self.measurePoints = []

        self.supportClass = supportClass
        self.settings = None
        self.plt = None

        self.notStopped = True

        self.timer = None
        self.t = None

        self.samplerate = 25
        self.functionCode = functionCode
        self.count = 0

        self.measurePointCount = 1

        self.mVtoV = 1000
        self.mAtoA = 1000
        self.uAtoV = 1e6

        self.minWidthWidget = 190

        self.checkboxes = []

    def initUI(self):
        self.supportClass.container.saveAction.triggered.connect(self.saveClick)
        self.supportClass.container.saveAction.setEnabled(True)

        layout = qt.QHBoxLayout()

        self.settings = mssw.Settings(self.functionCode, self.supportClass.measureSettings.xAxisPort)

        self.checkboxes = self.settings.checkBoxes

        self.settings.returnButton.clicked.connect(self.returnButtonPressed)

        self.plt = mspw.MeasureScreenPlot(self.ax_x, self.ax_y, self.settings.checkBoxes, self.functionCode)

        layout.addWidget(self.settings)
        layout.addWidget(self.plt)

        self.samplerate = int(1000 / self.samplerate)

        if self.functionCode == 0:
            self.measureClock()
        elif self.functionCode == 1:
            self.settings.startMeasureButton.clicked.connect(self.startMeasure)
            self.settings.addMeasurePointButton.clicked.connect(self.addMeasurePoint)

        self.settings.setFixedWidth(self.minWidthWidget)
        qtcore.QTimer.singleShot(300, lambda: self.resizeWidgets())
        self.setLayout(layout)

    def returnButtonPressed(self):
        if self.functionCode == 0:
            self.returnToMainScreen()
        elif self.functionCode == 1:
            self.returnToSettingsScreen()

    def addMeasurePoint(self):
        print("Click")
        self.measurePointCount += 1
        self.settings.measurePointLabel.setText("Measure Points: " + str(self.measurePointCount))

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
        if self.plt is not None:
            self.plt.canvas.setGeometry(0, 0, newWidthCanvas, height)

    def updateDataset(self, index):
        if self.notStopped:
            uebergabe = self.supportClass.device.readRegister(0, 26)
            for i in range(4):
                # Da 1000 mV und 1000 Ohm kann Berechnung vernachlässigt werden da 1000 / 1000 = 1
                #TODO Problem Diodenmessung nomma sagen lassen weil wenn wiederstand nicht 1K dann nicht = 1 => nicht alles egal...
                if self.settings.checkBoxes[i].isChecked():
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
                multiplication = self.mVtoV / self.supportClass.measureSettings.r2
                self.measurePoints.append(self.measurePointCount)
                if index <= 1:
                    self.ax_x.append(abs(uebergabe[index * 2] - uebergabe[index * 2 + 1]))
                elif index == 2:
                    self.ax_x.append(abs(uebergabe[4] - uebergabe[6]))
                elif index == 3:
                    self.ax_x.append(abs(uebergabe[5] - uebergabe[7]))

    def startMeasure(self):
        if self.t is None:
            self.t = threading.Thread(target=self.measureClock(self.supportClass.measureSettings.xAxisPort))
            self.t.start()
            if self.functionCode == 1:
                self.settings.startMeasureButton.setText = "Stop Measurement"
        else:
            print("WASRUM")
            if self.notStopped:
                self.notStopped = False
                self.settings.startMeasureButton.setText = "Start Measurement"
            else:
                self.notStopped = True
                self.settings.startMeasureButton.setText = "Stop Measurement"

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

        if self.plt.timer is not None:
            self.plt.timer.stop()

        self.plt.stopped = True
        self.supportClass.returnToMainScreen()

    def returnToSettingsScreen(self):
        if self.timer is not None:
            self.timer.stop()

        if self.plt.timer is not None:
            self.plt.timer.stop()

        self.plt.stopped = True
        self.supportClass.returnToSettingsScreen()

    def createExportData(self):
        if self.plt.checkXYLength()[0]:
            x_ueb = list(self.ax_x)
            y_ueb = copy.deepcopy(self.ax_y)
            measurePointDate = list(self.measurePoints)
            fig_ueb = self.plt.canvas.figure
            dataFrame = pd.DataFrame()
            dataFrame.insert(0, "Measure Point", measurePointDate, True)
            dataFrame.insert(1, "x0", x_ueb, True)

            for i in range(len(y_ueb)):
                if self.settings.checkBoxes[i].isChecked():
                    dataFrame.insert(len(dataFrame.columns), "Channel " + str(i+1), y_ueb[i], True)

            return dataFrame, fig_ueb

        else:
            timerCreateExData = qtcore.QTimer(self)
            timerCreateExData.timeout.connect(self.saveClick)
            timerCreateExData.setSingleShot(True)
            timerCreateExData.start(100)
            return None, None


