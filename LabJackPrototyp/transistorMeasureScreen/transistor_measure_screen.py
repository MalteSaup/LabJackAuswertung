import math

import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

import threading

import pandas as pd

import matplotlib.backends.qt_compat as qtplt
import matplotlib.pyplot as plt

import export_screen
from transistorMeasureScreen import transistor_measure_screen_plot_widget as tmspw

import calculator
import message_boxes
import calc_result
from settings_component_creator import SettingsComponentCreator

from calc_widget import CalcResultWidget, CalcWidget

from helper import MeasureMethod

if qtplt.is_pyqt5():
    pass
else:
    pass


class TransistorScreen(qt.QWidget):
    def __init__(self, supportClass):
        super().__init__()

        plt.style.use("dark_background")
        plt.tight_layout()

        self.supportClass = supportClass

        self.uceUbeStepCount = 10

        self.transistorPlot = None
        self.calcWidget = None

        self.columnNames = ["Measure Serie", "IC/[mA]", "UCE/[V]", "UBE/[V]", "IB/[μA]", "Estimation Results"]

        self.measureData = [[], [], [], []]
        self.measurePorts = self.supportClass.measureSettings.measurePorts
        self.measureSeriesForMeasureData = []

        self.t = None
        self.tLabelThread = None

        self.r1 = self.supportClass.measureSettings.r1
        self.r2 = self.supportClass.measureSettings.r2

        self.ubeMax = self.supportClass.measureSettings.ubeMax
        self.uceMax = self.supportClass.measureSettings.uceMax

        self.uceTicks = []
        self.uceTicksLabel = []

        self.ubeTicks = []
        self.ubeTicksLabel = []

        self.milli = 1000
        self.mikro = 1e6

        self.pltPadding = 30

        self.notStopped = False

        self.timer = None
        self.timerLabel = None

        self.measureSeriesCount = 1

        self.layout = None

        self.widgetAmount = 1

        self.calculator = calculator.Calculator()

        self.calcResults = []

        self.sampleratePerSecond = 25
        self.samplerate = int(1000/self.sampleratePerSecond)

        self.settingsComponentCreator = SettingsComponentCreator(minWidthWidget=self.supportClass.minWidthWidget,
                                                                 padding=self.pltPadding)

    def initUI(self):
        self.supportClass.container.saveAction.triggered.connect(self.saveClick)
        self.supportClass.container.saveAction.setEnabled(True)

        self.createUceUbeTicks()

        self.layout = qt.QGridLayout()
        settingsWidget = self.settingsComponentCreator.createSettingsWidget(MeasureMethod.TRANSISTOR,
                                                                            options=self.supportClass.options,
                                                                            measurePorts=self.measurePorts)

        self.settingsComponentCreator.startMeasureButton.pressed.connect(self.startMeasureButtonPressed)
        self.settingsComponentCreator.addMeasureSeriesButton.pressed.connect(self.addMeasureSeries)
        self.settingsComponentCreator.reconnectButton.clicked.connect(self.reconnect)
        self.settingsComponentCreator.returnButton.pressed.connect(self.initReturnMessageBox)

        self.transistorPlot = tmspw.TransistorMeasureScreenWidget(self.measureData, self.measureSeriesForMeasureData,
                                                                  self.uceMax,
                                                                  self.ubeMax, self.uceTicks,
                                                                  self.uceTicksLabel,
                                                                  self.ubeTicks, self.ubeTicksLabel,
                                                                  self.supportClass.screenGeometry)
        self.layout.addWidget(settingsWidget, 0, 0)
        self.layout.addWidget(self.calcWidget, 0, 1)
        self.layout.addWidget(self.transistorPlot, 0, 2)
        self.layout.setAlignment(self.transistorPlot, qtcore.Qt.AlignRight)
        self.setLayout(self.layout)


        settingsWidget.setFixedWidth(self.supportClass.minWidthWidget)
        settingsWidget.setContentsMargins(0, 0, 10, 0)
        self.show()

        qtcore.QTimer.singleShot(300, lambda: self.resizeWidgets())

    def reconnect(self):
        if self.supportClass.connectDevice():
            self.settingsComponentCreator.reconnectButton.setVisible(False)

    def resizeEvent(self, a0: qtgui.QResizeEvent) -> None:
        self.resizeWidgets()
        super().resizeEvent(a0)

    def createUceUbeTicks(self):
        uceStep = round(self.uceMax / self.uceUbeStepCount, 1)
        ubeStep = round(self.ubeMax / self.uceUbeStepCount, 1)

        for i in range(self.uceUbeStepCount):
            self.uceTicks.append(round(uceStep * i, 2))
            self.ubeTicks.append(round(ubeStep * i, 2))
            if i > 0:
                self.uceTicksLabel.append(str(round(self.uceTicks[-1], 2)))
                self.ubeTicksLabel.append(str(round(self.ubeTicks[-1], 2)))
            elif i == 0:
                self.uceTicksLabel.append("")
                self.ubeTicksLabel.append("")

    def updateDataset(self):
        if self.notStopped:
            try:
                passedData = self.supportClass.labJackU6.getMeasureData()
                self.measureData[0].append((abs(passedData[self.measurePorts[0]])) / self.r2 * self.milli)
                self.measureData[1].append((abs(passedData[self.measurePorts[1]])))
                self.measureData[2].append((abs(passedData[self.measurePorts[2]])))
                self.measureData[3].append((abs(passedData[self.measurePorts[3]])) / self.r1 * self.mikro)

                self.measureSeriesForMeasureData.append(self.measureSeriesCount)
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

    def addMeasureSeries(self):
        if self.notStopped:
            self.measureSeriesCount += 1
            self.settingsComponentCreator.measureSeriesLabel.setText("Measure Series: " + str(self.measureSeriesCount))
            self.resizeWidgets()

    def addCalcResults(self, measureSeries, amount, b, uearly):
        if not self.doesResultExist(measureSeries):
            self.calcResults.append(calc_result.CalcResult(measureSeries, uearly, b, amount))
            resultWidget = CalcResultWidget(measureSeries, uearly, b, amount, MeasureMethod.TRANSISTOR)
            self.calcWidget.calcResultHolder.layout.addWidget(resultWidget)
            self.transistorPlot.b = b

    def doesResultExist(self, measureSeries):
        for result in self.calcResults:
            if measureSeries == result.measureSerie:
                return True
        return False

    def startMeasureButtonPressed(self):
        if not self.notStopped:
            self.startMeasure()
        else:
            self.stopMeasure()

    def startMeasure(self):
        if self.timer is None:
            self.measureClock()
            self.connectionLostBox = None
        if self.calcWidget is not None:
            self.calcWidget.setParent(None)
            self.calcWidget = None
        self.widgetAmount = 1

        qtcore.QTimer.singleShot(100, lambda: self.resizeWidgets())

        self.transistorPlot.measureSeriesToDisplay = 0
        self.transistorPlot.b = None

        self.settingsComponentCreator.startMeasureButton.setText("Stop Measure")
        self.notStopped = True

    def stopMeasure(self):
        self.notStopped = False
        self.settingsComponentCreator.startMeasureButton.setText("Start Measure")

        self.calcWidget = CalcWidget(self.measureSeriesCount)
        self.calcWidget.chooseDropDown.currentIndexChanged.connect(self.comboChangeEvent)
        self.calcWidget.calcButton.pressed.connect(self.calcClick)
        self.calcWidget.setFixedWidth(self.supportClass.minWidthWidget)
        self.layout.addWidget(self.calcWidget, 0, 1)
        self.widgetAmount = 2

        qtcore.QTimer.singleShot(100, lambda: self.resizeWidgets())

    def comboChangeEvent(self):
        currentIndex = self.calcWidget.chooseDropDown.currentIndex()
        if currentIndex == 0:
            self.transistorPlot.measureSeriesToDisplay = 0
            self.transistorPlot.b = None
        else:
            self.transistorPlot.measureSeriesToDisplay = currentIndex - 1
            b = None
            for calcResult in self.calcResults:
                if calcResult.measureSerie == currentIndex - 1:
                    b = calcResult.value2
                    break
            self.transistorPlot.b = b

    def measureClock(self):
        self.timer = qtcore.QTimer(self)
        self.timer.timeout.connect(self.updateDataset)
        self.timer.start(self.samplerate)
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
            self.exportScreen.show()

    def calcClick(self):
        measureSeries = self.calcWidget.chooseDropDown.currentIndex()
        uce = list(self.measureData[1])
        ic = list(self.measureData[0])
        ib = list(self.measureData[3])
        if measureSeries == 0:
            self.calcAll(uce, ic, ib)
        elif measureSeries == 1:
            self.calcMeasureSeries(uce, ic, ib, lower=-1)
        else:
            self.calcMeasureSeries(uce, ic, ib, measureSeries-1)

    def calcMeasureSeries(self, uce, ic, ib, measureSeries=0, lower=0):
        upper = -1
        if lower == -1:
            uearly = self.calculator.leastSquare(uce, ic)
            b = self.calculator.calcB(ic, ib)
            lower = 0
        else:
            try:
                upper = self.measureSeriesForMeasureData.index(measureSeries + 1)
            except:
                upper = -1
            if measureSeries != 1:
                try:
                    lower = self.measureSeriesForMeasureData.index(measureSeries)
                except:
                    lower = -1
                    upper = -1


            if lower == -1 and upper == -1:
                uearly = "ERROR"
                b = "ERROR"
            else:
                uearly = self.calculator.leastSquare(uce[lower:upper], ic[lower:upper])
                b = self.calculator.calcB(ic[lower:upper], ib[lower:upper])

        if measureSeries == 0:
            measureText = "All Values"
        else:
            measureText = str(measureSeries)

        self.addCalcResults(measureText, len(uce[lower:upper]), uearly, b)

    def calcAll(self, uce, ic, ib):
        for i in range(self.measureSeriesCount):
            self.calcMeasureSeries(uce, ic, ib, i+1)

    def createExportData(self):
        if self.transistorPlot.checkLength()[0]:
            data_ueb = []
            data_ueb.append(self.measureSeriesForMeasureData.copy())
            data_ueb += self.measureData
            fig_ueb = self.transistorPlot.canvas.figure
            dataFrame = pd.DataFrame()

            estimationData = self.createMeasureEstimationCol()

            if (estimationData is not None):
                if len(estimationData) > len(data_ueb[0]):
                    diff = len(estimationData) - len(data_ueb[0])
                    for i in range(len(data_ueb)):
                        for j in range(diff):
                            data_ueb[i].append(math.nan)
                elif len(estimationData) < len(data_ueb[0]):
                    diff = len(data_ueb[0]) - len(estimationData)
                    for i in range(diff):
                        estimationData.append(math.nan)

            for i in range(len(data_ueb)):
                dataFrame.insert(i, self.columnNames[i], data_ueb[i], True)

            if estimationData is not None:
                dataFrame.insert(len(dataFrame.columns), "Estimation Results", estimationData, True)

            return dataFrame, fig_ueb
        else:
            return None, None

    def createMeasureEstimationCol(self):
        if len(self.calcResults) == 0:
            return None
        else:
            data = []
            for calcResult in self.calcResults:
                data.append("Measure Serie: " + str(calcResult.measureSerie))
                data.append("Amount of Measurements:")
                data.append(calcResult.measurePointCount)
                data.append("UEarly/[V]: ")
                data.append(calcResult.value1)
                data.append("B: ")
                data.append(calcResult.value2)
                data.append("")
            return data

    def startUpdateLabel(self):
        self.timerLabel = qtcore.QTimer(self)
        self.timerLabel.timeout.connect(self.updateDataLabel)
        self.timerLabel.start(250)

    def updateDataLabel(self):
        if len(self.measureData[0]) > 0:
            self.settingsComponentCreator.channelData[0][0].setText(
                "{:.3f}".format(self.measureData[0][-1] / self.milli * self.r2) + "V")
            self.settingsComponentCreator.channelData[0][1].setText("{:.3f}".format(self.measureData[0][-1]) + "mA")
            self.settingsComponentCreator.channelData[3][0].setText(
                "{:.3f}".format(self.measureData[3][-1] / self.mikro * self.r1) + "V")
            self.settingsComponentCreator.channelData[3][1].setText("{:.3f}".format(self.measureData[3][-1]) + "µA")

            self.settingsComponentCreator.channelData[1][0].setText("{:.3f}".format(self.measureData[1][-1]) + "V")
            self.settingsComponentCreator.channelData[1][1].setText("{:.3f}".format(self.measureData[1][-1]) + "V")
            self.settingsComponentCreator.channelData[2][0].setText("{:.3f}".format(self.measureData[2][-1]) + "V")
            self.settingsComponentCreator.channelData[2][1].setText("{:.3f}".format(self.measureData[2][-1]) + "V")

    def initReturnMessageBox(self):
        messageBox = message_boxes.ReturnMessageBox()
        result = messageBox.exec_()
        if result == qt.QMessageBox.Ok:
            self.transistorPlot.stopped = True

            if self.timer is not None:
                self.timer.stop()

            if self.timerLabel is not None:
                self.timerLabel.stop()

            if self.transistorPlot.timer is not None:
                self.transistorPlot.timer.stop()

            self.supportClass.returnToSettingsScreen()
        else:
            pass

    def resizeWidgets(self):
        width = self.geometry().width()
        height = self.geometry().height() - self.supportClass.container.statusBar().height()
        if self.transistorPlot is not None:
            self.transistorPlot.canvas.setGeometry(0, 0,
                                                   (width - self.supportClass.minWidthWidget * self.widgetAmount) - self.pltPadding,
                                                   height)
