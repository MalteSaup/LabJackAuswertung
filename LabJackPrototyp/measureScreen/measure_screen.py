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
        self.measureSeries = []

        self.supportClass = supportClass
        self.settings = None
        self.plt = None

        self.notStopped = True

        self.timer = None
        self.t = None

        self.samplerate = 25
        self.functionCode = functionCode
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

        self.settings = mssw.Settings(self.functionCode, self.supportClass.measureSettings.xAxisPort)

        self.checkboxes = self.settings.checkBoxes

        self.settings.returnButton.clicked.connect(self.initMessageBox)

        self.plt = mspw.MeasureScreenPlot(self.ax_x, self.ax_y, self.settings.checkBoxes, self.functionCode)

        layout.addWidget(self.settings)
        layout.addWidget(self.plt)

        self.samplerate = int(1000 / self.samplerate)

        if self.functionCode == 0:
            self.measureClock()
        elif self.functionCode == 1:
            self.settings.startMeasureButton.clicked.connect(self.startMeasure)
            self.settings.addMeasureSeriesButton.clicked.connect(self.addMeasureSerie)

        self.settings.setFixedWidth(self.minWidthWidget)

        self.setLayout(layout)

        if self.functionCode == 1:
            self.checkboxes[self.supportClass.measureSettings.xAxisPort].setEnabled(False)
            self.checkboxes[self.supportClass.measureSettings.xAxisPort].setChecked(True)

    def messageBoxButtonClick(self):
        if self.functionCode == 0:
            self.returnToMainScreen()
        elif self.functionCode == 1:
            self.returnToSettingsScreen()

    def addMeasureSerie(self):
        self.measureSeriesCount += 1
        self.settings.measureSeriesLabel.setText("Measure Points: " + str(self.measureSeriesCount))



    def updateDataset(self, index):
        if self.notStopped:
            uebergabe = self.supportClass.device.readRegister(0, 26)
            multiplication = self.mAtoA / self.supportClass.measureSettings.r2

            for i in range(4):
                # TODO Problem Diodenmessung nomma sagen lassen weil wenn wiederstand nicht 1K dann nicht = 1 => nicht alles egal...
                if self.settings.checkBoxes[i].isChecked() and i != index:
                    if i <= 1:
                        self.ax_y[i].append(abs(uebergabe[i * 2] - uebergabe[i * 2 + 1]) * multiplication)
                    elif i == 2:
                        self.ax_y[i].append(abs(uebergabe[4] - uebergabe[6]) * multiplication)
                    elif i == 3:
                        self.ax_y[i].append(abs(uebergabe[5] - uebergabe[7]) * multiplication)
                else:
                    self.ax_y[i].append(math.nan)
            if self.functionCode == 0:
                self.ax_x.append(self.count)
                self.count += 1
            elif self.functionCode == 1:
                self.measureSeries.append(self.measureSeriesCount)
                if index <= 1:
                    self.ax_x.append(abs(uebergabe[index * 2] - uebergabe[index * 2 + 1]))
                elif index == 2:
                    self.ax_x.append(abs(uebergabe[4] - uebergabe[6]))
                elif index == 3:
                    self.ax_x.append(abs(uebergabe[5] - uebergabe[7]))

    def startMeasure(self):
        if self.t is None:
            if self.functionCode == 1:
                self.settings.startMeasureButton.setText("Stop Measurement")
                self.notStopped = True
            self.t = threading.Thread(target=self.measureClock(self.supportClass.measureSettings.xAxisPort))
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
            x_ueb = list(self.ax_x)
            y_ueb = copy.deepcopy(self.ax_y)

            fig_ueb = self.plt.canvas.figure
            dataFrame = pd.DataFrame()

            columnNames = []

            if self.functionCode == 1:
                measureSeriesDate = list(self.measureSeries)
                dataFrame.insert(0, "Measure Serie", measureSeriesDate, True)
                dataFrame.insert(1, "XAxis Channel " + str(self.supportClass.measureSettings.xAxisPort), x_ueb, True)
                columnNames.append("Measure Serie")
                columnNames.append("XAxis Channel " + str(self.supportClass.measureSettings.xAxisPort))
            else:
                dataFrame.insert(0, "Ticks Passed", x_ueb, True)
                columnNames.append("Ticks Passed")
            for i in range(len(y_ueb)):
                if self.settings.checkBoxes[i].isChecked():
                    dataFrame.insert(len(dataFrame.columns), "Channel " + str(i + 1), y_ueb[i], True)
                    columnNames.append("Channel " + str(i + 1))
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
        if self.functionCode == 1:
            self.settings.channelData[self.supportClass.measureSettings.xAxisPort][0].setText(
                "{:.3f}".format(self.ax_x[-1] / self.mVtoV * self.supportClass.measureSettings.r2) + "V")
            self.settings.channelData[self.supportClass.measureSettings.xAxisPort][1].setText(
                "{:.3f}".format(self.ax_x[-1]) + "mA")

        for i in range(4):
            if self.checkboxes[i].isChecked() and (i != self.supportClass.measureSettings.xAxisPort or self.functionCode != 1):
                self.settings.channelData[i][0].setText("{:.3f}".format(self.ax_y[i][-1]) + "V")
                self.settings.channelData[i][1].setText("{:.3f}".format(self.ax_y[i][-1]) + "V")
            elif i != self.supportClass.measureSettings.xAxisPort:
                self.settings.channelData[i][0].setText("-")
                self.settings.channelData[i][1].setText("-")
