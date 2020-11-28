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


class MeasureScreen(qt.QWidget):
    def __init__(self, supportClass):
        super().__init__()
        plt.style.use("dark_background")
        self.ax_x = []
        self.ax_y = [[], [], [], []]

        self.xue = []
        self.yue = []
        self.measureSeries = []

        self.supportClass = supportClass
        self.settings = None
        self.plt = None

        self.notStopped = True

        self.timer = None
        self.t = None

        self.connectionLostBox = None

        self.samplerate = 25
        self.measureMethod = supportClass.measureSettings.measureMethod
        self.count = 0

        self.measureSeriesCount = 1

        self.mVtoV = 1000
        self.mAtoA = 1000
        self.uAtoV = 1e6

        self.minWidthWidget = 220

        self.checkBoxes = []

        self.settingsComponentCreator = SettingsComponentCreator()

    def initUI(self):
        self.supportClass.container.saveAction.triggered.connect(self.saveClick)
        self.supportClass.container.saveAction.setEnabled(True)

        layout = qt.QHBoxLayout()

        settingsWidget = self.settingsComponentCreator.createSettingsWidget(self.measureMethod, idPort=self.supportClass.measureSettings.idPort)

        self.checkBoxes = self.settingsComponentCreator.checkBoxes

        self.settingsComponentCreator.reconnectButton.clicked.connect(self.reconnect)
        self.settingsComponentCreator.returnButton.clicked.connect(self.initReturnMessageBox)

        self.plt = mspw.MeasureScreenPlot(self.ax_x, self.ax_y, self.checkBoxes, self.supportClass)

        layout.addWidget(settingsWidget)
        layout.addWidget(self.plt)

        self.samplerate = int(1000 / self.samplerate)

        self.settingsComponentCreator.startMeasureButton.clicked.connect(self.startMeasure)
        self.settingsComponentCreator.addMeasureSeriesButton.clicked.connect(self.addMeasureSerie)

        settingsWidget.setFixedWidth(self.minWidthWidget)

        self.setLayout(layout)

    def reconnect(self):
        if self.supportClass.connectDevice():
            self.settingsComponentCreator.reconnectButton.setVisible(False)
            if self.measureMethod == MeasureMethod.OSZILATOR:
                self.startMeasure()

    def addMeasureSerie(self):
        self.measureSeriesCount += 1
        self.settingsComponentCreator.measureSeriesLabel.setText("Measure Points: " + str(self.measureSeriesCount))

    def updateDataset(self):
        print("H"+ str(self.measureMethod))
        if self.notStopped:
            try:
                measureData = self.supportClass.labJackU6.getMeasureData()

                if self.measureMethod == MeasureMethod.DIODE:
                    multiplication = self.mAtoA / self.supportClass.measureSettings.r2
                    self.ax_x.append(measureData[self.supportClass.measureSettings.udPort])
                    self.ax_y[0].append(measureData[self.supportClass.measureSettings.idPort] * multiplication)
                else:
                    for i in range(LabJackU6Settings.USABLEPORTCOUNT.value):
                        if self.checkBoxes[i].isChecked():
                            self.ax_y[i].append(measureData[i])
                        else:
                            self.ax_y[i].append(math.nan)
                    self.ax_x.append(self.count)
                    self.count += 1
                self.measureSeries.append(self.measureSeriesCount)

            except Exception as e:
                print(e)
                self.supportClass.runningFlag = False
                if self.notStopped:
                    self.startMeasure()
                    self.timer.stop()
                    self.t.join()
                    qtcore.QTimer.singleShot(1000, lambda: self.killThread())

                if self.connectionLostBox == None:
                    self.supportClass.runningFlag = False
                    self.connectionLostBox = message_boxes.ConnectionLost()
                    self.connectionLostBox.exec_()
                    self.settingsComponentCreator.reconnectButton.setVisible(True)

    def killThread(self):
        self.t = None
        self.timer = None

    def connectionLostBoxClick(self):
        self.connectionLostBox.exec()

    def startMeasure(self):
        if self.t is None:
            self.notStopped = True
            self.connectionLostBox = None
            self.t = threading.Thread(target=self.measureClock())
            self.t.start()
            self.settingsComponentCreator.startMeasureButton.setText("Stop Measurement")

        else:
            if self.notStopped:
                self.notStopped = False
                self.settingsComponentCreator.startMeasureButton.setText("Start Measurement")
            else:
                self.notStopped = True
                self.settingsComponentCreator.startMeasureButton.setText("Stop Measurement")

    def measureClock(self):
        self.timer = qtcore.QTimer(self)
        self.timer.timeout.connect(lambda: self.updateDataset())
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
            xData = list(self.ax_x)
            yData = copy.deepcopy(self.ax_y)

            fig_ueb = self.plt.canvas.figure
            dataFrame = pd.DataFrame()

            columnNames = []

            measureSeriesData = list(self.measureSeries)

            if self.measureMethod == MeasureMethod.DIODE:
                dataFrame.insert(0, "Measure Serie", measureSeriesData, True)
                dataFrame.insert(1, "Id/[mA]", yData[0], True)
                dataFrame.insert(2, "Ud/[V]", xData, True)
                columnNames.append("Measure Serie")
                columnNames.append("Id/[mA]")
                columnNames.append("Ud/[V]")
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

    def initReturnMessageBox(self):
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
                    "{:.3f}".format(self.ax_y[0][-1] * multiplication) + "V")
                self.settingsComponentCreator.channelData[self.supportClass.measureSettings.idPort][1].setText(
                    "{:.3f}".format(self.ax_y[0][-1]) + "mA")
                self.settingsComponentCreator.channelData[udPort][0].setText("{:.3f}".format(self.ax_x[-1]) + "V")
                self.settingsComponentCreator.channelData[udPort][1].setText("{:.3f}".format(self.ax_x[-1]) + "V")

        else:
            if len(self.settingsComponentCreator.channelData[0]) > 0:
                for i in range(4):
                    if self.checkBoxes[i].isChecked():
                        self.settingsComponentCreator.channelData[i][0].setText("{:.3f}".format(self.ax_y[i][-1]) + "V")
                        self.settingsComponentCreator.channelData[i][1].setText("{:.3f}".format(self.ax_y[i][-1]) + "V")
                    elif i != self.supportClass.measureSettings.idPort:
                        self.settingsComponentCreator.channelData[i][0].setText("-")
                        self.settingsComponentCreator.channelData[i][1].setText("-")
