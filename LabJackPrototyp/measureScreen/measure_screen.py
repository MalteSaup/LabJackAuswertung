import math
import threading

import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qtcore
import PyQt5.QtGui as qtgui

import copy
import pandas as pd

import matplotlib.pyplot as plt

import export_screen
import message_boxes
from helper import MeasureMethod, LabJackU6Settings

from measureScreen import measure_screen_plot_widget as mspw
from settings_component_creator import SettingsComponentCreator
from calc_widget import CalcWidget, CalcResultWidget
from calculator import Calculator
from calc_result import CalcResult


class MeasureScreen(qt.QWidget):
    def __init__(self, supportClass):
        super().__init__()
        plt.style.use("dark_background")

        self.xData = []
        self.yData = [[], [], [], []]

        self.measureSeries = []

        self.supportClass = supportClass
        self.plt = None
        self.calcWidget = None

        self.calcResults = []

        self.notStopped = False

        self.timer = None

        self.samplerate = 25
        self.sampleratePerSecond = int(1000 / self.samplerate)
        self.measureMethod = supportClass.measureSettings.measureMethod
        self.count = 0

        self.measureSeriesCount = 1

        self.mVtoV = 1000
        self.mAtoA = 1000
        self.uAtoV = 1e6

        self.minWidthWidget = 220
        self.pltPadding = 30
        self.widgetAmount = 1

        self.layout = None

        self.checkBoxes = []

        self.settingsComponentCreator = SettingsComponentCreator()
        self.calculator = Calculator()

    def initUI(self):
        self.supportClass.container.saveAction.triggered.connect(self.saveClick)
        self.supportClass.container.saveAction.setEnabled(True)

        self.layout = qt.QGridLayout()

        settingsWidget = self.settingsComponentCreator.createSettingsWidget(self.measureMethod,
                                                                            idPort=self.supportClass.measureSettings.idPort)

        self.settingsComponentCreator.startMeasureButton.clicked.connect(self.startMeasureButtonPressed)
        self.settingsComponentCreator.addMeasureSeriesButton.clicked.connect(self.addMeasureSerie)
        self.settingsComponentCreator.reconnectButton.clicked.connect(self.reconnect)
        self.settingsComponentCreator.returnButton.clicked.connect(self.initReturnMessageBox)

        self.checkBoxes = self.settingsComponentCreator.checkBoxes

        self.plt = mspw.MeasureScreenPlot(self.xData, self.yData, self.measureSeries, self.checkBoxes,
                                          self.supportClass)

        self.layout.addWidget(settingsWidget, 0, 0)
        self.layout.addWidget(self.calcWidget, 0, 1)
        self.layout.addWidget(self.plt, 0, 2)

        settingsWidget.setFixedWidth(self.minWidthWidget)

        self.setLayout(self.layout)

    def reconnect(self):
        if self.supportClass.connectDevice():
            self.settingsComponentCreator.reconnectButton.setVisible(False)
            if self.measureMethod == MeasureMethod.OSZILATOR:
                self.startMeasure()

    def addMeasureSerie(self):
        self.measureSeriesCount += 1
        self.settingsComponentCreator.measureSeriesLabel.setText("Measure Series: " + str(self.measureSeriesCount))

    def updateDataset(self):
        if self.notStopped:
            try:
                measureData = self.supportClass.labJackU6.getMeasureData()

                if self.measureMethod == MeasureMethod.DIODE:
                    multiplication = self.mAtoA / self.supportClass.measureSettings.r2
                    self.xData.append(measureData[self.supportClass.measureSettings.udPort])
                    self.yData[0].append(measureData[self.supportClass.measureSettings.idPort] * multiplication)
                else:
                    for i in range(LabJackU6Settings.USABLEPORTCOUNT.value):
                        if self.checkBoxes[i].isChecked():
                            self.yData[i].append(measureData[i])
                        else:
                            self.yData[i].append(math.nan)
                    self.xData.append(self.count)
                    self.count += 1
                self.measureSeries.append(self.measureSeriesCount)

            except Exception as e:
                print(e)
                self.supportClass.runningFlag = False
                if self.notStopped:
                    self.startMeasure()
                    self.timer.stop()
                    qtcore.QTimer.singleShot(1000, lambda: self.killThread())

                if self.connectionLostBox == None:
                    self.supportClass.runningFlag = False
                    self.connectionLostBox = message_boxes.ConnectionLost()
                    self.connectionLostBox.exec_()
                    self.settingsComponentCreator.reconnectButton.setVisible(True)

    def killThread(self):
        self.timer = None

    def startMeasureButtonPressed(self):
        if self.notStopped:
            self.stopMeasure()
        else:
            self.startMeasure()

    def startMeasure(self):
        if self.timer is None:
            self.measureClock()
            self.connectionLostBox = None
        if self.calcWidget is not None:
            self.calcWidget.setParent(None)
            self.calcWidget = None
        self.widgetAmount = 1

        qtcore.QTimer.singleShot(100, lambda: self.resizeWidgets())

        self.settingsComponentCreator.startMeasureButton.setText("Stop Measurement")
        self.notStopped = True

    def stopMeasure(self):
        self.notStopped = False
        self.settingsComponentCreator.startMeasureButton.setText("Start Measurement")

        if self.measureMethod == MeasureMethod.DIODE:
            self.calcWidget = CalcWidget(self.measureSeriesCount)
            self.calcWidget.chooseDropDown.currentIndexChanged.connect(self.comboChangeEvent)
            self.calcWidget.calcButton.pressed.connect(self.calcClick)
            self.calcWidget.setFixedWidth(self.minWidthWidget)
            self.layout.addWidget(self.calcWidget, 0, 1)
            self.widgetAmount = 2

            qtcore.QTimer.singleShot(100, lambda: self.resizeWidgets())

    def calcClick(self):
        measureSeries = self.calcWidget.chooseDropDown.currentIndex()
        ud = list(self.xData)
        id = list(self.yData[0])
        if measureSeries == 0:
            self.calcAll(ud, id)
        elif measureSeries == 1:
            self.calcMeasureSeries(ud, id, lower=-1)
        else:
            self.calcMeasureSeries(ud, id, measureSeries-1)

    def calcAll(self, ud, id):
        for i in range(self.measureSeriesCount):
            self.calcMeasureSeries(ud, id, i+1)

    def calcMeasureSeries(self, ud, id, measureSeries=-1, lower=0):
        upper = -1
        if lower == -1:                     #Flag for All Values
            n, iS = self.calculator.calculateNAndIs(ud, id)
            measureText = "All Values"
            lower = 0                       #All Values are counted for measurement Amount
        else:
            try:
                upper = self.measureSeries.index(measureSeries + 1)
            except:
                upper = -1
            if measureSeries != 1:
                try:
                    lower = self.measureSeries.index(measureSeries)
                except:                 #Only throws error when a measureSeries has no Values at all, so [-1:-1] return an empty array
                    lower = -1
                    upper = -1
            n, iS = self.calculator.calculateNAndIs(ud[lower:upper], id[lower:upper])
            measureText = str(measureSeries)
        self.addCalcResults(measureText, len(ud[lower:upper]), n, iS)

    def addCalcResults(self, measureSeries, amount, n, iS):
        if not self.doesResultExist(measureSeries):
            self.calcResults.append(CalcResult(measureSeries, n, iS, amount))
            resultWidget = CalcResultWidget(measureSeries, n, iS, amount, self.measureMethod)
            self.calcWidget.calcResultHolder.layout.addWidget(resultWidget)

    def doesResultExist(self, measureSeries):
        for result in self.calcResults:
            if measureSeries == result.measureSerie:
                return True
        return False

    def measureClock(self):
        self.timer = qtcore.QTimer(self)
        self.timer.timeout.connect(lambda: self.updateDataset())
        self.timer.start(self.sampleratePerSecond)
        self.startUpdateLabel()

    def saveClick(self, wasStopped=False):
        if self.notStopped:
            wasStopped = True
            self.notStopped = False
        df, fig, columnNames = self.createExportData()
        if df is None and fig is None:
            self.saveClick(wasStopped)
        else:
            self.notStopped = wasStopped
            self.exportScreen = export_screen.ExportScreen(df, fig, columnNames)

    def returnToMainScreen(self):
        if self.timer is not None:
            self.timer.stop()

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
            xData = list(self.xData)
            yData = copy.deepcopy(self.yData)

            fig_ueb = self.plt.canvas.figure
            dataFrame = pd.DataFrame()

            columnNames = []

            measureSeriesData = list(self.measureSeries)

            estimationData = self.createEstimationCol()

            if estimationData is not None:
                if len(estimationData) > len(xData):
                    diff = len(estimationData) - len(xData)
                    for i in range(diff):
                        xData.append(math.nan)
                        yData[0].append(math.nan)
                        measureSeriesData.append(math.nan)
                elif len(estimationData) < len(xData):
                    diff = len(xData) - len(estimationData)
                    for i in range(diff):
                        estimationData.append(math.nan)

            if self.measureMethod == MeasureMethod.DIODE:
                dataFrame.insert(0, "Measure Serie", measureSeriesData, True)
                dataFrame.insert(1, "Id/[mA]", yData[0], True)
                dataFrame.insert(2, "Ud/[V]", xData, True)
                columnNames.append("Measure Serie")
                columnNames.append("Id/[mA]")
                columnNames.append("Ud/[V]")
                if estimationData is not None:
                    dataFrame.insert(3, "Estimation Results", estimationData, True)
                    columnNames.append("Estimation Results")
            elif self.measureMethod == MeasureMethod.OSZILATOR:
                dataFrame.insert(0, "Measure Serie", measureSeriesData)
                dataFrame.insert(1, "Sample", xData, True)
                columnNames.append("Measure Serie")
                columnNames.append("Sample")
                for i in range(len(yData)):
                    if self.checkBoxes[i].isChecked():
                        dataFrame.insert(len(dataFrame.columns), "Channel " + str(i + 1) + "/[V]", yData[i], True)
                        columnNames.append("Channel " + str(i + 1) + "/[V]")

            return dataFrame, fig_ueb, columnNames
        else:
            timerCreateExData = qtcore.QTimer(self)
            timerCreateExData.timeout.connect(self.saveClick)
            timerCreateExData.setSingleShot(True)
            timerCreateExData.start(100)
            return None, None

    def createEstimationCol(self):
        if len(self.calcResults) == 0 or self.measureMethod == MeasureMethod.OSZILATOR:
            return None
        else:
            data = []
            for calcResult in self.calcResults:
                data.append("Measure Serie: " + str(calcResult.measureSerie))
                data.append("Amount of Measurements:")
                data.append(calcResult.measurePointCount)
                data.append("Nd: ")
                data.append(calcResult.value1)
                data.append("Is/[A]: ")
                data.append(calcResult.value2)
                data.append("")
            return data

    def initReturnMessageBox(self):
        if self.plt.timer is not None:
            self.plt.timer.stop()
        self.messageBox = message_boxes.ReturnMessageBox()
        result = self.messageBox.exec_()
        if result == qt.QMessageBox.Ok:
            if self.timer is not None:
                self.timer.stop()

            if self.timerLabel is not None:
                self.timerLabel.stop()

            if self.plt.timer is not None:
                self.plt.timer.stop()
            if self.measureMethod == MeasureMethod.OSZILATOR:
                self.returnToMainScreen()
            elif self.measureMethod == MeasureMethod.DIODE:
                self.returnToSettingsScreen()
        else:
            pass

    def startUpdateLabel(self):
        self.timerLabel = qtcore.QTimer(self)
        self.timerLabel.timeout.connect(self.updateDataLabel)
        self.timerLabel.start(250)

    def updateDataLabel(self):
        if self.measureMethod == MeasureMethod.DIODE:
            multiplication = self.supportClass.measureSettings.r2 / self.mVtoV
            if len(self.settingsComponentCreator.channelData[0]) > 0:
                udPort = 1 - self.supportClass.measureSettings.idPort
                self.settingsComponentCreator.channelData[self.supportClass.measureSettings.idPort][0].setText(
                    "{:.3f}".format(self.yData[0][-1] * multiplication) + "V")
                self.settingsComponentCreator.channelData[self.supportClass.measureSettings.idPort][1].setText(
                    "{:.3f}".format(self.yData[0][-1]) + "mA")
                self.settingsComponentCreator.channelData[udPort][0].setText("{:.3f}".format(self.xData[-1]) + "V")
                self.settingsComponentCreator.channelData[udPort][1].setText("{:.3f}".format(self.xData[-1]) + "V")

        else:
            if len(self.settingsComponentCreator.channelData[0]) > 0:
                for i in range(4):
                    if self.checkBoxes[i].isChecked():
                        self.settingsComponentCreator.channelData[i][0].setText(
                            "{:.3f}".format(self.yData[i][-1]) + "V")
                        self.settingsComponentCreator.channelData[i][1].setText(
                            "{:.3f}".format(self.yData[i][-1]) + "V")
                    elif i != self.supportClass.measureSettings.idPort:
                        self.settingsComponentCreator.channelData[i][0].setText("-")
                        self.settingsComponentCreator.channelData[i][1].setText("-")

    def comboChangeEvent(self):
        if self.calcWidget.chooseDropDown.currentIndex() < 2:
            self.plt.measureSeriesToDisplay = 0
        else:
            self.plt.measureSeriesToDisplay = self.calcWidget.chooseDropDown.currentIndex() - 1
        pass

    def resizeWidgets(self):
        width = self.geometry().width()
        height = self.geometry().height() - self.supportClass.container.statusBar().height()
        if self.plt is not None:
            self.plt.canvas.setGeometry(0, 0, (width - self.minWidthWidget * self.widgetAmount) - self.pltPadding,
                                        height)
