import math
import threading

import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

import copy
import pandas as pd

import matplotlib.pyplot as plt

import export_screen
import message_boxes
from helper import MeasureMethod

from measureScreen import measure_screen_plot_widget as mspw, measure_screen_settings_widget as mssw


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

        self.checkboxes = []

    def initUI(self):
        self.supportClass.container.saveAction.triggered.connect(self.saveClick)
        self.supportClass.container.saveAction.setEnabled(True)

        layout = qt.QHBoxLayout()

        self.settings = mssw.Settings(self.supportClass.measureSettings.measureMethod,
                                      self.supportClass.measureSettings.udPort)

        self.checkboxes = self.settings.checkBoxes

        self.settings.reconnectButton.clicked.connect(self.reconnect)
        self.settings.returnButton.clicked.connect(self.initMessageBox)

        self.plt = mspw.MeasureScreenPlot(self.ax_x, self.ax_y, self.settings.checkBoxes, self.supportClass)

        layout.addWidget(self.settings)
        layout.addWidget(self.plt)

        self.samplerate = int(1000 / self.samplerate)

        if self.measureMethod == MeasureMethod.OSZILATOR:
            self.startMeasure()
        elif self.measureMethod == MeasureMethod.DIODE:
            self.settings.startMeasureButton.clicked.connect(self.startMeasure)
            self.settings.addMeasureSeriesButton.clicked.connect(self.addMeasureSerie)

        self.settings.setFixedWidth(self.minWidthWidget)

        self.setLayout(layout)

        if self.measureMethod == MeasureMethod.DIODE:
            self.checkboxes[self.supportClass.measureSettings.udPort].setEnabled(False)
            self.checkboxes[self.supportClass.measureSettings.udPort].setChecked(True)

    def reconnect(self):
        if self.supportClass.connectDevice():
            self.settings.reconnectButton.setVisible(False)
            if self.measureMethod == MeasureMethod.OSZILATOR:
                self.startMeasure()

    def messageBoxButtonClick(self):
        if self.measureMethod == MeasureMethod.OSZILATOR:
            self.returnToMainScreen()
        elif self.measureMethod == MeasureMethod.DIODE:
            self.returnToSettingsScreen()

    def addMeasureSerie(self):
        self.measureSeriesCount += 1
        self.settings.measureSeriesLabel.setText("Measure Points: " + str(self.measureSeriesCount))

    def updateDataset(self, index):
        if self.notStopped:
            try:
                data = self.supportClass.device.readRegister(0, 8)

                multiplication = 1

                if self.measureMethod == MeasureMethod.DIODE:
                    multiplication = self.mAtoA / self.supportClass.measureSettings.r2

                print(multiplication)
                print(index)

                for i in range(4):
                    if self.settings.checkBoxes[i].isChecked() and (self.supportClass.measureSettings.measureMethod == MeasureMethod.OSZILATOR or i == index):
                        print(abs(data[i * 2] - data[i * 2 + 1]) * multiplication)
                        if i <= 1:
                            self.ax_y[i].append(abs(data[i * 2] - data[i * 2 + 1]) * multiplication)
                        elif i == 2:
                            self.ax_y[i].append(abs(data[4] - data[6]) * multiplication)
                        elif i == 3:
                            self.ax_y[i].append(abs(data[5] - data[7]) * multiplication)
                    else:
                        self.ax_y[i].append(math.nan)
                if self.measureMethod == MeasureMethod.OSZILATOR:
                    self.ax_x.append(self.count)
                    self.count += 1
                elif self.measureMethod == MeasureMethod.DIODE:
                    self.measureSeries.append(self.measureSeriesCount)
                    if index <= 1:
                        self.ax_x.append(abs(data[index * 2] - data[index * 2 + 1]))
                    elif index == 2:
                        self.ax_x.append(abs(data[4] - data[6]))
                    elif index == 3:
                        self.ax_x.append(abs(data[5] - data[7]))
            except:
                if self.notStopped:
                    self.startMeasure()
                    self.timer.stop()
                    self.t.join()
                    qtcore.QTimer.singleShot(1000, lambda: self.killThread())

                if self.connectionLostBox == None:
                    self.supportClass.runningFlag = False
                    self.connectionLostBox = message_boxes.ConnectionLost()
                    self.connectionLostBox.exec_()
                    self.settings.reconnectButton.setVisible(True)

    def killThread(self):
        print(str(self.t) + " 1 ")
        print(str(self.timer))
        self.t = None
        self.timer = None

    def connectionLostBoxClick(self, buttonPressed):
        if (buttonPressed.text() == "Ok"):
            print("Ok")
            self.connectionLostBox.exec()
        else:
            print("Not Ok")

    def startMeasure(self):
        if self.t is None:
            self.notStopped = True
            self.connectionLostBox = None
            if self.measureMethod == MeasureMethod.DIODE:
                self.settings.startMeasureButton.setText("Stop Measurement")
                self.t = threading.Thread(target=self.measureClock(self.supportClass.measureSettings.udPort))
            if self.measureMethod == MeasureMethod.OSZILATOR:
                self.t = threading.Thread(target=self.measureClock())
            self.t.start()
        else:
            if self.notStopped:
                self.notStopped = False
                self.settings.startMeasureButton.setText("Start Measurement")
            else:
                self.notStopped = True
                self.settings.startMeasureButton.setText("Stop Measurement")

    def measureClock(self, index=-1):
        self.timer = qtcore.QTimer(self)
        self.timer.timeout.connect(lambda: self.updateDataset(index))
        self.timer.start(self.samplerate)
        self.startUpdateLabel()

    def saveClick(self):
        self.notStopped = False
        df, fig, columnNames = self.createExportData()
        if df is None and fig is None:
            pass
        else:
            self.notStopped = True
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

            if self.measureMethod == MeasureMethod.DIODE:
                measureSeriesData = list(self.measureSeries)
                dataFrame.insert(0, "Measure Serie", measureSeriesData, True)
                dataFrame.insert(1, "Ud/[V]", xData, True)
                columnNames.append("Measure Serie")
                columnNames.append("Ud/[V]")
            else:
                dataFrame.insert(0, "Sample", xData, True)
                columnNames.append("Sample")
            count = 1
            for i in range(len(yData)):
                if self.settings.checkBoxes[i].isChecked():
                    if self.measureMethod == MeasureMethod.DIODE:
                        dataFrame.insert(len(dataFrame.columns), "Id " + str(count) + "/[mA]", yData[i], True)
                        columnNames.append("Id " + str(count) + "/[mA]")
                    if self.measureMethod == MeasureMethod.OSZILATOR:
                        dataFrame.insert(len(dataFrame.columns), "Channel " + str(i + 1) + "/[V]", yData[i], True)
                        columnNames.append("Channel " + str(i + 1) + "/[V]")

            return dataFrame, fig_ueb, columnNames

        else:
            timerCreateExData = qtcore.QTimer(self)
            timerCreateExData.timeout.connect(self.saveClick)
            timerCreateExData.setSingleShot(True)
            timerCreateExData.start(100)
            return None, None

    def initMessageBox(self):
        self.messageBox = message_boxes.ReturnMessageBox()
        self.messageBox.buttonClicked.connect(self.messageBoxButtonClick)
        self.messageBox.exec_()

    def startUpdateLabel(self):
        self.timerLabel = qtcore.QTimer(self)
        self.timerLabel.timeout.connect(self.updateDataLabel)
        self.timerLabel.start(250)

    def updateDataLabel(self):
        if self.measureMethod == MeasureMethod.DIODE:
            for i in range(4):
                if len(self.settings.channelData[i]) > 0:
                    if self.checkboxes[i].isChecked():
                        if i == self.supportClass.measureSettings.udPort:
                            self.settings.channelData[i][0].setText("{:.3f}".format(self.ax_x[-1]) + "V")
                            self.settings.channelData[i][1].setText("{:.3f}".format(self.ax_x[-1]) + "V")
                        else:
                            self.settings.channelData[i][0].setText("{:.3f}".format(self.ax_y[i][-1] * self.supportClass.measureSettings.r2 / self.mVtoV) + "V")
                            self.settings.channelData[i][1].setText("{:.3f}".format(self.ax_y[i][-1]) + "mA")
                    else:
                        self.settings.channelData[i][0].setText("-")
                        self.settings.channelData[i][1].setText("-")
        else:
            for i in range(4):
                if len(self.settings.channelData[i]) > 0:
                    if self.checkboxes[i].isChecked():
                        self.settings.channelData[i][0].setText("{:.3f}".format(self.ax_y[i][-1]) + "V")
                        self.settings.channelData[i][1].setText("{:.3f}".format(self.ax_y[i][-1]) + "V")
                    elif i != self.supportClass.measureSettings.udPort:
                        self.settings.channelData[i][0].setText("-")
                        self.settings.channelData[i][1].setText("-")
