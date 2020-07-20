import math
import time

import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

import threading

import copy
import pandas as pd

import matplotlib.backends.qt_compat as qtplt
import matplotlib.figure as fig
import matplotlib.pyplot as plt

import export_screen
import settings_screen
import transistor_measure_screen_widget as tmsw
import transistor_measure_screen_settings_widget as tmssw
import transistor_measure_scree_calc_widget as tmscw
import transistor_measure_screen_calc_result_widget as tmscrw
import calculate

if qtplt.is_pyqt5():
    import matplotlib.backends.backend_qt5agg as pyqtplt
else:
    import matplotlib.backends.backend_qt4agg as pyqtplt


class TransistorScreen(qt.QWidget):
    def __init__(self, supportClass):
        super().__init__()

        plt.style.use("dark_background")
        plt.tight_layout()

        self.supportClass = supportClass
        self.sampleratePerSecond = 25
        self.uceUbeStepCount = 9

        self.plt = None
        self.lbh = None
        self.tcw = None

        self.columnNames = ["Measure Point", "IC", "UCE", "UBE", "IB"]

        self.measureSettings = self.supportClass.measureSettings

        self.measureData = [[], [], [], []]
        self.measurePorts = self.measureSettings.measurePorts
        self.measurePointForMeasureData = []

        self.t = None

        self.r1 = self.measureSettings.r1
        self.r2 = self.measureSettings.r2

        self.ubeMin = self.measureSettings.ubeMin
        self.ubeMax = self.measureSettings.ubeMax
        self.uceMin = self.measureSettings.uceMin
        self.uceMax = self.measureSettings.uceMax

        self.uceTicks = []
        self.uceTicksLabel = []

        self.ubeTicks = []
        self.ubeTicksLabel = []

        self.milli = 1000
        self.mikro = 1e6

        self.minWidthWidget = 190

        self.notStopped = True

        self.timer = None

        self.measurePointCount = 1

        self.running = False
        self.stopped = False

        self.layout = None

        self.settingWidgets = 1

        self.calculator = calculate.Calculator()

    def initUI(self):

        #print(self.supportClass.measureSettings.toString())

        self.createUceUbeTicks()

        self.layout = qt.QGridLayout()
        self.lbh = tmssw.LabelHolder(self.supportClass.options, self.measurePorts)
        #self.settingWidgets = 2     #Muss geändert werdene wenn tcw ins layout kommt wegen resizing
        self.plt = tmsw.TransistorMeasureScreenWidget(self.measureData, [self.uceMin, self.uceMax], [self.ubeMin, self.ubeMax], self.uceTicks, self.uceTicksLabel, self.ubeTicks, self.ubeTicksLabel)
        self.layout.addWidget(self.lbh, 0, 0)
        self.layout.addWidget(self.tcw, 0, 1)
        self.layout.addWidget(self.plt, 0, 2)
        self.layout.setAlignment(self.plt, qtcore.Qt.AlignRight)
        self.samplerate = int(1000 / self.sampleratePerSecond)
        self.setLayout(self.layout)
        self.supportClass.container.saveAction.triggered.connect(self.saveClick)
        self.supportClass.container.saveAction.setEnabled(True)

        self.lbh.returnButton.pressed.connect(self.supportClass.returnToSettingsScreen)
        self.lbh.startMeasureButton.pressed.connect(self.startMeasureButtonPressed)
        self.lbh.addMeasurePointButton.pressed.connect(self.addMeasurePoint)

        self.lbh.setFixedWidth(self.minWidthWidget)
        self.plt.resize(self.minWidthWidget, self.supportClass.container.geometry().height() * 0.9)
        self.show()

        qtcore.QTimer.singleShot(300, lambda: self.resizeWidgets())

    def resizeEvent(self, a0: qtgui.QResizeEvent) -> None:
        self.resizeWidgets()
        super().resizeEvent(a0)

    def resizeWidgets(self):
        width = self.supportClass.container.geometry().width()
        height = self.supportClass.container.geometry().height() * 0.9
        if (width / 5) < self.minWidthWidget * self.settingWidgets:
            newWidthCanvas = width - self.minWidthWidget * self.settingWidgets
        else:
            newWidthCanvas = width * 4 / 5
        if self.plt is not None:
            self.plt.canvas.setGeometry(0, 0, newWidthCanvas, height)


    def createUceUbeTicks(self):
        uceStep = round((self.uceMax - self.uceMin) / self.uceUbeStepCount, 1)
        ubeStep = round((self.ubeMax - self.ubeMin) / self.uceUbeStepCount, 1)

        for i in range(self.uceUbeStepCount+1):
            self.uceTicks.append(round(self.uceMin + uceStep * i, 2))
            self.ubeTicks.append(round(self.ubeMin + ubeStep * i, 2))
            if self.uceUbeStepCount > i > 0:
                self.uceTicksLabel.append(str(round(self.uceTicks[-1], 2)))
                self.ubeTicksLabel.append(str(round(self.ubeTicks[-1], 2)))
            elif i == 0:
                self.uceTicksLabel.append("")
                self.ubeTicksLabel.append("")
            elif i == self.uceUbeStepCount:
                self.uceTicksLabel.append("UCE")
                self.ubeTicksLabel.append("UBE")


    def updateDataset(self):
        if self.notStopped and not self.stopped:
            self.measurePointForMeasureData.append(self.measurePointCount)
            uebergabe = self.supportClass.device.readRegister(0, 16)
            uebergabeData = []
            uebergabeData.append(abs(uebergabe[0] - uebergabe[1]))
            uebergabeData.append(abs(uebergabe[2] - uebergabe[3]))
            uebergabeData.append(abs(uebergabe[4] - uebergabe[6]))
            uebergabeData.append(abs(uebergabe[5] - uebergabe[7]))

            self.measureData[0].append((abs(uebergabeData[self.measurePorts[0]])) / self.r2 * self.milli)
            self.measureData[1].append((abs(uebergabeData[self.measurePorts[1]])))
            self.measureData[2].append((abs(uebergabeData[self.measurePorts[2]])))
            self.measureData[3].append((abs(uebergabeData[self.measurePorts[3]])) / self.r1 * self.mikro)

    def addMeasurePoint(self):
        if self.notStopped:
            self.measurePointCount += 1
            self.lbh.measurePointsValueLabel.setText(str(self.measurePointCount))
            self.resizeWidgets()

    def addCalcResults(self, measurePoint, amount, b, uearly):
        resultWidget = tmscrw.CalcResultWidget(measurePoint, b, uearly, amount)
        self.tcw.calcResultHolder.layout.addWidget(resultWidget)

    def startMeasureButtonPressed(self):
        if not self.running:
            self.startMeasure()
            self.running = True
        else:
            self.stopMeasure()
            self.running = False

    def startMeasure(self):
        self.measurePorts = self.measurePorts
        print(self.measurePorts)

        if self.tcw is not None:
            self.tcw.setParent(None)
            self.tcw = None

        self.settingWidgets = 1
        qtcore.QTimer.singleShot(100, lambda: self.resizeWidgets())

        self.stopped = False

        self.lbh.startMeasureButton.setText("Stop Measure")

        self.t = threading.Thread(target=self.measureClock())
        self.t.start()

    def stopMeasure(self):
        self.lbh.startMeasureButton.setText("Start Measure")

        self.stopped = True

        self.tcw = tmscw.TransistorMeasureScreenCalcWidget(self.measurePointCount)
        self.layout.addWidget(self.tcw, 0, 1)
        self.tcw.setFixedWidth(self.minWidthWidget)
        self.settingWidgets = 2

        self.initTCW()

        qtcore.QTimer.singleShot(100, lambda: self.resizeWidgets())

    def measureClock(self):
        self.timer = qtcore.QTimer(self)
        self.timer.timeout.connect(self.updateDataset)
        self.timer.start(self.samplerate)
        self.plt.timer.start()

    def saveClick(self):
        self.notStopped = False
        df, fig = self.createExportData()
        if df is None and fig is None:
            pass
        else:
            self.notStopped = True
            self.exportScreen = export_screen.ExportScreen(df, fig, self.columnNames)
            self.exportScreen.show()

    def calcClick(self):
        measurePoint = self.tcw.chooseDropDown.currentIndex()
        uce = None
        ic = None
        ib = None
        if measurePoint == 1:
            uce = self.measureData[1]
            ic = self.measureData[0]
            ib = self.measureData[3]
        elif measurePoint == 0:
            self.calcAll()
        else:
            if measurePoint - 1 == 1:
                lower = 0
                try:
                    upper = self.measurePointForMeasureData.index(measurePoint)
                except:
                    upper = None
            else:
                lower = self.measurePointForMeasureData.index(measurePoint - 2)
                try:
                    upper = self.measurePointForMeasureData.index(measurePoint)
                except:
                    upper = None

            uce = self.measureData[1][lower:upper]
            ic = self.measureData[0][lower:upper]
            ib = self.measureData[3][lower:upper]
        if uce is None or ic is None or ib is None:
            print("ERROR WITH VALUE INIT")
            return
        uearly, n = self.calculator.leastSquare(uce, ic)
        b = self.calculator.calcB(ic, ib)
        if uearly is None:
            print("ERROR IN UEALRY CALC")
            return
        if measurePoint == 0:
            measureText = "All Values"
        else:
            measureText = str(measurePoint-1)
        self.addCalcResults(measureText, len(uce), b, uearly)

    def calcAll(self):
        lower = 0
        upper = 0
        for i in range(1, self.measurePointCount+1):
            if i - 1 == 0:
                try:
                    upper = self.measurePointForMeasureData.index(i+1)
                except:
                    upper = None
            else:
                lower = upper
                try:
                    upper = self.measurePointForMeasureData.index(i+1)
                except:
                    upper = None
            uce = self.measureData[1][lower:upper]
            ic = self.measureData[0][lower:upper]
            ib = self.measureData[3][lower:upper]

            uearly, n = self.calculator.leastSquare(uce, ic)
            b = self.calculator.calcB(ic, ib)
            if uearly is None:
                print("ERROR IN UEALRY CALC")
                return

            self.addCalcResults(str(i), len(uce), b, uearly)

    def returnToMainScreen(self):
        if self.timer is not None:
            self.timer.stop()

        if self.timer is not None:
            self.timer.stop()

        if self.plt.timer is not None:
            self.plt.timer.stop()

        self.stopped = True
        self.supportClass.returnToMainScreen()

    def createExportData(self):
        if self.plt.checkLength()[0]:
            data_ueb = []
            data_ueb.append(self.measurePointForMeasureData.copy())
            data_ueb += self.measureData
            fig_ueb = self.plt.canvas.figure
            dataFrame = pd.DataFrame()
            print(len(data_ueb))
            print(len(self.columnNames))
            for i in range(len(data_ueb)):
                dataFrame.insert(i, self.columnNames[i], data_ueb[i], True)

            return dataFrame, fig_ueb
        else:
            timerCreateExData = qtcore.QTimer(self)
            timerCreateExData.timeout.connect(self.saveClick)
            timerCreateExData.setSingleShot(True)
            timerCreateExData.start(100)
            return None, None

    def initTCW(self):
        self.tcw.calcButton.pressed.connect(self.calcClick)
