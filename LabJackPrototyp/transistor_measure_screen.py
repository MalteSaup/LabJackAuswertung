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

        self.minWidthLBH = 190

        self.notStopped = True

        self.timer = None

        self.measurePointCount = 1

        self.running = False
        self.stopped = False

    def initUI(self):

        #print(self.supportClass.measureSettings.toString())

        self.createUceUbeTicks()

        layout = qt.QHBoxLayout()
        self.lbh = tmssw.LabelHolder(self.supportClass.options, self.measurePorts)
        self.plt = tmsw.TransistorMeasureScreenWidget(self.measureData, [self.uceMin, self.uceMax], [self.ubeMin, self.ubeMax], self.uceTicks, self.uceTicksLabel, self.ubeTicks, self.ubeTicksLabel)
        layout.addWidget(self.lbh)
        layout.addWidget(self.plt)
        layout.setAlignment(self.plt, qtcore.Qt.AlignRight)
        self.samplerate = int(1000 / self.sampleratePerSecond)
        self.setLayout(layout)
        self.supportClass.container.saveAction.triggered.connect(self.saveClick)
        self.supportClass.container.saveAction.setEnabled(True)

        self.lbh.returnButton.pressed.connect(self.supportClass.returnToSettingsScreen)
        self.lbh.startMeasureButton.pressed.connect(self.startMeasureButtonPressed)
        self.lbh.addMeasurePointButton.pressed.connect(self.addMeasurePoint)


        self.lbh.setFixedWidth(self.minWidthLBH)
        self.plt.resize(self.supportClass.container.geometry().width() * 0.8, self.supportClass.container.geometry().height() * 0.9)

        self.show()

        qtcore.QTimer.singleShot(100, lambda: self.resizeWidgets())

    def resizeEvent(self, a0: qtgui.QResizeEvent) -> None:
        self.resizeWidgets()
        super().resizeEvent(a0)

    def resizeWidgets(self):
        width = self.supportClass.container.geometry().width()
        height = self.supportClass.container.geometry().height() * 0.9
        if (width / 5) < self.minWidthLBH:
            newWidthCanvas = width - self.minWidthLBH
        else:
            newWidthCanvas = width * 4 / 5
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

        self.stopped = False

        self.lbh.startMeasureButton.setText("Stop Measure")

        self.t = threading.Thread(target=self.measureClock())
        self.t.start()

    def stopMeasure(self):
        self.lbh.startMeasureButton.setText("Start Measure")

        self.stopped = True

        b = self.calcB()
        uearly = self.calcUEarly()

        self.lbh.bValueLabel.setText(str(b))
        self.lbh.uEarlyValueLabel.setText(str(uearly) + "V")

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

    def calcB(self):
        calcArr = []
        ic = list(self.measureData[0])
        ib = list(self.measureData[3])

        for i in range(len(ic)):
            calcArr.append((ic[i] * 1000) / ib[i])
        upperCutter = True
        lowerCutter = True
        while upperCutter:
            calArr, upperCutter, arr = self.upperLowerCutter(calcArr, True)
        while lowerCutter:
            calArr, lowerCutter, arr = self.upperLowerCutter(calcArr, False)

        durchschnitt = 0
        for i in calcArr:
            durchschnitt += i
        return round(durchschnitt / len(calcArr), 3)

    def calcUEarly(self):
        ic = list(self.measureData[0])
        uce = list(self.measureData[1])

        u1 = None
        u2 = None
        i1 = None
        i2 = None

        maxBeforeProblem = self.getUceProblemMax(uce, ic)
        print(maxBeforeProblem)
        for i in range(len(uce)):
            if uce[i] >= 2.5 and uce[i] < 3 and u1 is None:
                u1 = uce[i]
                i1 = ic[i]
            if uce[i] >= 6.5 and uce[i] < 8 and u2 is None:
                u2 = uce[i]
                i2 = ic[i]
            if u1 is not None and u2 is not None:
                break
        if u1 is None or u2 is None:
            print("not enough measure values")
            return "-0"

        print("U1: " + str(u1) + " I1: " + str(i1) + " U2: " + str(u2) + " I2: " + str(i2))

        uearly = ((u1*i2)-(u2*i1))/(i2-i1)
        return round(uearly, 4)

    def getUceProblemMax(self, uce, ic):
        valueSampleList = []
        for i in range(len(uce)):
            uceSample = round(uce[i], 2)
            try:
                valueSampleList[0].index(uceSample)
            except:
                valueSampleList.append([uceSample, round(ic[i], 2)])
        valueSampleList = sorted(valueSampleList, key=lambda x: x[0])
        prevValue = -10
        problemValue = None
        for i in valueSampleList:
            if prevValue > i[1]:
                if problemValue is None:
                    problemValue = i[1]
                elif problemValue > i[1]:
                    problemValue = i[1]
            else:
                prevValue = i[1]
        return problemValue

    def upperLowerCutter(self, arr, up=False):
        deletedValues = False
        valueArr = []
        arrMax = max(arr)
        for i in arr:
            if up:
                if i >= arrMax * 0.9:
                    valueArr.append(i)
            else:
                if i <= arrMax * 0.1:
                    valueArr.append(i)

        if len(valueArr) < len(arr) * 0.1 and len(valueArr) != 0:
            deletedValues = True
            for delVal in valueArr[::-1]:
                #print(delVal)
                arr.pop(arr.index(delVal))
        return arr, deletedValues, len(valueArr)

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
