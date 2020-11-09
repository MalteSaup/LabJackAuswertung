import math

import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

import threading

import pandas as pd

import matplotlib.backends.qt_compat as qtplt
import matplotlib.pyplot as plt

import export_screen
from transistorMeasureScreen import transistor_measure_screen_plot_widget as tmspw, \
    transistor_measure_screen_calc_result_widget as tmscrw, \
    transistor_measure_scree_calc_widget as tmscw
import calculator
import message_boxes
import calc_result
from settings_component_creator import SettingsComponentCreator

from helper import LabJackU6, MeasureMethod

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
        self.sampleratePerSecond = 25
        self.uceUbeStepCount = 9

        self.transistorPlot = None
        self.settingsComponentCreator = None
        self.transistorCalcResultWidget = None

        self.columnNames = ["Measure Serie", "IC", "UCE", "UBE", "IB", "Estimation Results"]

        self.measureSettings = self.supportClass.measureSettings

        self.measureData = [[], [], [], []]
        self.measurePorts = self.measureSettings.measurePorts
        self.measureSeriesForMeasureData = []

        self.t = None
        self.tLabelThread = None

        self.r1 = self.measureSettings.r1
        self.r2 = self.measureSettings.r2

        self.ubeMin = self.measureSettings.ubeMin
        self.ubeMax = self.measureSettings.ubeMax
        self.uceMax = self.measureSettings.uceMax

        self.uceTicks = []
        self.uceTicksLabel = []

        self.ubeTicks = []
        self.ubeTicksLabel = []

        self.milli = 1000
        self.mikro = 1e6

        self.minWidthWidget = 220
        self.pltPadding = 20

        self.notStopped = True

        self.timer = None
        self.timerLabel = None

        self.measureSeriesCount = 1

        self.running = False
        self.stopped = False

        self.layout = None

        self.widgetAmount = 1

        self.calculator = calculator.Calculator()

        self.calcResults = []

        self.settingsComponentCreator = SettingsComponentCreator(minWidthWidget=self.minWidthWidget,
                                                                 padding=self.pltPadding)

    def initUI(self):

        # print(self.supportClass.measureSettings.toString())

        self.createUceUbeTicks()

        self.layout = qt.QGridLayout()
        settingsWidget = self.settingsComponentCreator.createSettingsWidget(MeasureMethod.TRANSISTOR,
                                                                            options=self.supportClass.options,
                                                                            measurePorts=self.measurePorts)
        # self.settingWidgets = 2     #Muss geändert werdene wenn tcw ins layout kommt wegen resizing
        self.transistorPlot = tmspw.TransistorMeasureScreenWidget(self.measureData, self.measureSeriesForMeasureData,
                                                                  self.uceMax,
                                                                  self.ubeMax, self.uceTicks,
                                                                  self.uceTicksLabel,
                                                                  self.ubeTicks, self.ubeTicksLabel,
                                                                  self.supportClass.screenGeometry)
        self.layout.addWidget(settingsWidget, 0, 0)
        self.layout.addWidget(self.transistorCalcResultWidget, 0, 1)
        self.layout.addWidget(self.transistorPlot, 0, 2)
        self.layout.setAlignment(self.transistorPlot, qtcore.Qt.AlignRight)
        self.samplerate = int(1000 / self.sampleratePerSecond)
        self.setLayout(self.layout)
        self.supportClass.container.saveAction.triggered.connect(self.saveClick)
        self.supportClass.container.saveAction.setEnabled(True)

        self.settingsComponentCreator.returnButton.pressed.connect(self.initReturnMessageBox)
        self.settingsComponentCreator.startMeasureButton.pressed.connect(self.startMeasureButtonPressed)
        self.settingsComponentCreator.addMeasureSeriesButton.pressed.connect(self.addMeasureSeries)

        settingsWidget.setFixedWidth(self.minWidthWidget)
        settingsWidget.setContentsMargins(0, 0, 10, 0)
        self.show()

        qtcore.QTimer.singleShot(300, lambda: self.resizeWidgets())

    def resizeEvent(self, a0: qtgui.QResizeEvent) -> None:
        self.resizeWidgets()
        super().resizeEvent(a0)

    def createUceUbeTicks(self):
        uceStep = round(self.uceMax / self.uceUbeStepCount, 1)
        ubeStep = round(self.ubeMax / self.uceUbeStepCount, 1)

        for i in range(self.uceUbeStepCount + 1):
            self.uceTicks.append(round(uceStep * i, 2))
            self.ubeTicks.append(round(ubeStep * i, 2))
            if i > 0:
                self.uceTicksLabel.append(str(round(self.uceTicks[-1], 2)))
                self.ubeTicksLabel.append(str(round(self.ubeTicks[-1], 2)))
            elif i == 0:
                self.uceTicksLabel.append("")
                self.ubeTicksLabel.append("")

    def updateDataset(self):
        if self.notStopped and not self.stopped:
            self.measureSeriesForMeasureData.append(self.measureSeriesCount)
            uebergabe = self.supportClass.device.readRegister(0, LabJackU6.MINCHANNELREAD.value)
            uebergabeData = []
            uebergabeData.append(abs(uebergabe[0] - uebergabe[1]))
            uebergabeData.append(abs(uebergabe[2] - uebergabe[3]))
            uebergabeData.append(abs(uebergabe[4] - uebergabe[6]))
            uebergabeData.append(abs(uebergabe[5] - uebergabe[7]))

            self.measureData[0].append((abs(uebergabeData[self.measurePorts[0]])) / self.r2 * self.milli)
            self.measureData[1].append((abs(uebergabeData[self.measurePorts[1]])))
            self.measureData[2].append((abs(uebergabeData[self.measurePorts[2]])))
            self.measureData[3].append((abs(uebergabeData[self.measurePorts[3]])) / self.r1 * self.mikro)

    def addMeasureSeries(self):
        if self.notStopped:
            self.measureSeriesCount += 1
            self.settingsComponentCreator.measureSeriesLabel.setText(str(self.measureSeriesCount))
            self.resizeWidgets()

    def addCalcResults(self, measureSeries, amount, b, uearly):
        if not self.doesResultExist(measureSeries):
            self.calcResults.append(calc_result.CalcResult(measureSeries, uearly, b, amount))
            resultWidget = tmscrw.CalcResultWidget(measureSeries, b, uearly, amount)
            self.transistorCalcResultWidget.calcResultHolder.layout.addWidget(resultWidget)

            if self.transistorCalcResultWidget.chooseDropDown.currentIndex() > 1:
                self.transistorPlot.b = b
                self.transistorPlot.measureSeriesToDisplay = int(measureSeries)

    def doesResultExist(self, measureSeries):
        for result in self.calcResults:
            if measureSeries == result.measureSerie:
                return True
        return False

    def startMeasureButtonPressed(self):
        if not self.running:
            self.startMeasure()
            self.running = True
            self.calcResults = []
        else:
            self.stopMeasure()
            self.running = False

    def startMeasure(self):
        self.measurePorts = self.measurePorts

        self.transistorPlot.measureSeriesToDisplay = 0
        self.transistorPlot.b = None

        if self.transistorCalcResultWidget is not None:
            self.transistorCalcResultWidget.setParent(None)
            self.transistorCalcResultWidget = None

        self.widgetAmount = 1
        qtcore.QTimer.singleShot(100, lambda: self.resizeWidgets())

        self.stopped = False

        self.settingsComponentCreator.startMeasureButton.setText("Stop Measure")

        self.t = threading.Thread(target=self.measureClock())
        self.t.start()

        self.tLabelThread = threading.Thread(target=self.startUpdateLabel())
        self.tLabelThread.start()

    def stopMeasure(self):
        self.settingsComponentCreator.startMeasureButton.setText("Start Measure")

        self.stopped = True

        self.transistorCalcResultWidget = tmscw.TransistorMeasureScreenCalcWidget(self.measureSeriesCount)
        self.transistorCalcResultWidget.chooseDropDown.currentIndexChanged.connect(self.comboChangeEvent)
        self.layout.addWidget(self.transistorCalcResultWidget, 0, 1)
        self.transistorCalcResultWidget.setFixedWidth(self.minWidthWidget)
        self.widgetAmount = 2

        self.transistorPlot.updateLabel()

        self.initTCW()

        qtcore.QTimer.singleShot(100, lambda: self.resizeWidgets())

    def comboChangeEvent(self):
        if self.transistorCalcResultWidget.chooseDropDown.currentIndex() < 2:
            self.transistorPlot.measureSeriesToDisplay = 0
            self.transistorPlot.b = None
        else:
            self.transistorPlot.measureSeriesToDisplay = self.transistorCalcResultWidget.chooseDropDown.currentIndex() - 1
            bSet = False
            for calcResult in self.calcResults:
                if int(calcResult.measureSerie) == self.transistorCalcResultWidget.chooseDropDown.currentIndex() - 1:
                    self.transistorPlot.b = calcResult.b
                    bSet = True
                    break
            if not bSet:
                self.transistorPlot.b = None

    def measureClock(self):
        self.timer = qtcore.QTimer(self)
        self.timer.timeout.connect(self.updateDataset)
        self.timer.start(self.samplerate)
        self.transistorPlot.timer.start()

    def saveClick(self):
        self.notStopped = False
        self.transistorPlot.updateLabel()
        df, fig = self.createExportData()
        if df is None and fig is None:
            pass
        else:
            self.notStopped = True
            self.exportScreen = export_screen.ExportScreen(df, fig, self.columnNames)
            self.exportScreen.show()

    def calcClick(self):
        measureSeries = self.transistorCalcResultWidget.chooseDropDown.currentIndex()
        print(measureSeries)
        uce = None
        ic = None
        ib = None
        if measureSeries == 1:
            uce = self.measureData[1]
            ic = self.measureData[0]
            ib = self.measureData[3]
        elif measureSeries == 0:
            self.calcAll()
        else:
            lower = 0
            upper = 0
            if measureSeries - 1 == 1:
                try:
                    upper = self.measureSeriesForMeasureData.index(measureSeries)
                except:
                    upper = -1
            else:
                lower = self.measureSeriesForMeasureData.index(measureSeries - 1)
                try:
                    upper = self.measureSeriesForMeasureData.index(measureSeries)
                except:
                    upper = -1
            print("u" + str(upper))
            print("l" + str(lower))
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
            uearly = "ERROR"
        if measureSeries == 0:
            measureText = "All Values"
        else:
            measureText = str(measureSeries - 1)
        self.addCalcResults(measureText, len(uce), b, uearly)

    def calcAll(self):
        lower = 0
        upper = 0
        for i in range(1, self.measureSeriesCount + 1):
            if i - 1 == 0:
                try:
                    upper = self.measureSeriesForMeasureData.index(i + 1)
                except:
                    upper = -1
            else:
                lower = upper
                try:
                    upper = self.measureSeriesForMeasureData.index(i + 1)
                except:
                    upper = None

            uce = self.measureData[1][lower:upper]
            ic = self.measureData[0][lower:upper]
            ib = self.measureData[3][lower:upper]

            uearly, n = self.calculator.leastSquare(uce, ic)
            b = self.calculator.calcB(ic, ib)

            if uearly is None:
                print("ERROR IN UEALRY CALC")
                uearly = "ERROR"

            self.addCalcResults(str(i), len(uce), b, uearly)

    def returnToSettingsScreen(self):
        if self.timer is not None:
            self.timer.stop()

        if self.timerLabel is not None:
            self.timerLabel.stop()

        if self.transistorPlot.timer is not None:
            self.transistorPlot.timer.stop()

        self.stopped = True
        self.supportClass.returnToSettingsScreen()

    def createExportData(self):
        if self.transistorPlot.checkLength()[0]:
            data_ueb = []
            data_ueb.append(self.measureSeriesForMeasureData.copy())
            data_ueb += self.measureData
            fig_ueb = self.transistorPlot.canvas.figure
            dataFrame = pd.DataFrame()
            print(len(data_ueb))
            print(len(self.columnNames))

            estimationData = self.createMeasureEstimationCol()

            print("EDD")
            print(estimationData)

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
            timerCreateExportData = qtcore.QTimer(self)
            timerCreateExportData.timeout.connect(self.saveClick)
            timerCreateExportData.setSingleShot(True)
            timerCreateExportData.start(100)
            return None, None

    def createMeasureEstimationCol(self):
        if len(self.calcResults) == 0:
            return None
        else:
            data = []
            for calcResult in self.calcResults:
                data.append("Measure Serie: " + str(calcResult.measureSerie))
                if type(calcResult.uearly) == str:
                    data.append("UEarly: " + calcResult.uearly)
                else:
                    data.append("UEarly: " + str(round(calcResult.uearly, 3)) + "V")
                if type(calcResult.b) == str:
                    data.append("B: " + calcResult.b)
                else:
                    data.append("B: " + str(round(calcResult.b, 3)))
                data.append("Measure Point Amount: " + str(calcResult.measurePointCount))
                data.append("")
            return data

    def startUpdateLabel(self):
        self.timerLabel = qtcore.QTimer(self)
        self.timerLabel.timeout.connect(self.updateDataLabel)
        self.timerLabel.start(250)

    def updateDataLabel(self):
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

    def initTCW(self):
        self.transistorCalcResultWidget.calcButton.pressed.connect(self.calcClick)

    def initReturnMessageBox(self):
        # self.messageBox = message_boxes.ReturnMessageBox()
        # self.messageBox.buttonClicked.connect(self.messageBoxButtonClick)
        # self.messageBox.exec_()
        self.initConnectionLossMessageBox()

    def messageBoxButtonClick(self, value):
        print(value)
        # if (value.text() == "OK"):
        #    self.returnToSettingsScreen()

    def initConnectionLossMessageBox(self):
        # self.messageBox = message_boxes.ConnectionLostBox()
        # self.messageBox.buttonClicked.connect(self.messageBoxButtonClick())
        # self.messageBox.exec_()
        print()

    def resizeWidgets(self):
        width = self.geometry().width()
        height = self.geometry().height() - self.supportClass.container.statusBar().height()
        if self.transistorPlot is not None:
            self.transistorPlot.canvas.setGeometry(0, 0,
                                                   (width - self.minWidthWidget * self.widgetAmount) - self.pltPadding,
                                                   height)
