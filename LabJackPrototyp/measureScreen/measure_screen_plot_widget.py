import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

import math

import copy

from datetime import datetime

import matplotlib.backends.qt_compat as qtplt
import matplotlib.figure as fig

from helper import MeasureMethod, LabJackU6Settings

if qtplt.is_pyqt5():
    import matplotlib.backends.backend_qt5agg as pyqtplt
else:
    import matplotlib.backends.backend_qt4agg as pyqtplt


class MeasureScreenPlot(qt.QWidget):
    def __init__(self, axisX, axisY, measureSeries, checkboxes, supportClass, resolutionX=100):
        super().__init__()
        self.axisX = axisX
        self.axisY = axisY
        self.measureSeries = measureSeries
        self.checkboxes = checkboxes
        self.canvas = None
        self.ax = None

        self.resolutionX = resolutionX

        self.supportClass = supportClass

        self.stopped = False
        self.timer = None

        self.colors = ["red", "blue", "green", "yellow"]

        self.measureSeriesToDisplay = 0

        self.now = datetime.now().strftime('%Y.%m.%d %H:%M')

        self.lines = []

        self.initUI()

    def initUI(self):
        layout = qt.QHBoxLayout()
        self.canvas = pyqtplt.FigureCanvas(fig.Figure())
        self.ax = self.canvas.figure.subplots()

        self.initAxes()
        self.getLines()

        self.timer = self.canvas.new_timer(150)
        self.timer.add_callback(self.animation)
        self.timer.start()

        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def createLastMeasurePointData(self):
        if len(self.axisX) == 0:
            return [math.nan], [[math.nan], [math.nan], [math.nan], [math.nan]]
        xMeasurePoint = [math.nan] * len(self.axisX)
        xMeasurePoint[-1] = self.axisX[-1]
        yMeasurePoints = []

        emptyArr = [math.nan] * len(self.axisY[0])

        if self.supportClass.measureSettings.measureMethod == MeasureMethod.OSZILATOR:
            for i in range(len(self.axisY)):
                yMeasurePoints.append(emptyArr.copy())
                yMeasurePoints[i][-1] = self.axisY[i][-1]
        elif self.supportClass.measureSettings.measureMethod == MeasureMethod.DIODE:
            yMeasurePoints.append(emptyArr.copy())
            yMeasurePoints[0][-1] = self.axisY[0][-1]
        return xMeasurePoint, yMeasurePoints

    def createXAxisLimits(self):
        if self.supportClass.measureSettings.measureMethod == MeasureMethod.OSZILATOR:
            if self.axisX == [] or self.axisX[-1] < self.resolutionX:
                return [0, self.resolutionX]
            else:
                return [self.axisX[-1] - self.resolutionX, self.axisX[-1]]

        elif self.supportClass.measureSettings.measureMethod == MeasureMethod.DIODE:
            return [0, self.supportClass.measureSettings.udMax]

    def createYAxisLimits(self):
        if (self.supportClass.measureSettings.measureMethod == MeasureMethod.OSZILATOR):
            return [0, LabJackU6Settings.MAXVOLTAGE.value]
        if (self.supportClass.measureSettings.measureMethod == MeasureMethod.DIODE):
            return [0, self.supportClass.measureSettings.idMax]

    def checkXYLength(self):
        xData = list(self.axisX)
        yData = copy.deepcopy(self.axisY)

        lengthX = len(xData)

        sameLength = True

        if self.supportClass.measureSettings.measureMethod == MeasureMethod.OSZILATOR:
            for i in range(4):
                if not lengthX == len(yData[i]):
                    sameLength = False
        elif self.supportClass.measureSettings.measureMethod == MeasureMethod.DIODE:
            indexMin, indexMax = 0, -1
            if self.measureSeriesToDisplay != 0:
                try:
                    indexMax = self.measureSeries.index(self.measureSeriesToDisplay + 1) - 1
                except:
                    indexMax = -1
                try:
                    indexMin = self.measureSeries.index(self.measureSeriesToDisplay)
                except:
                    indexMax = -1
                    indexMin = -1


            if not lengthX == len(yData[0]):
                sameLength = False

            xData = xData[indexMin:indexMax]
            yData[0] = yData[0][indexMin:indexMax]

        return sameLength, xData, yData

    def initAxes(self):
        self.ax.set_xlim(self.createXAxisLimits())
        self.ax.set_ylim(self.createYAxisLimits())

        if self.supportClass.measureSettings.measureMethod == MeasureMethod.OSZILATOR:
            self.ax.text(-0.05, 0.5, "Voltage/[V]", horizontalalignment='right',
                         verticalalignment='center',
                         rotation='vertical',
                         transform=self.ax.transAxes)
            self.ax.text(0.5, -0.08, "Samplecount", horizontalalignment='center',
                         verticalalignment='top',
                         transform=self.ax.transAxes)

        if self.supportClass.measureSettings.measureMethod == MeasureMethod.DIODE:
            self.ax.text(-0.05, 0.5, "Id/[mA]", horizontalalignment='right',
                         verticalalignment='center',
                         rotation='vertical',
                         transform=self.ax.transAxes)
            self.ax.text(0.5, -0.08, "Ud/[V]", horizontalalignment='center',
                         verticalalignment='top',
                         transform=self.ax.transAxes)

    def getLines(self):
        if self.supportClass.measureSettings.measureMethod == MeasureMethod.DIODE:
            line1, = self.ax.plot([], [], color=self.colors[3], linestyle="None", marker=".", markersize=1)
            line2, = self.ax.plot([], [], color="white", linestyle="None", marker="X", markersize=4)
            self.lines.append(line1)
            self.lines.append(line2)

    def animation(self):
        if not self.stopped:
            drawable, xData, yData = self.checkXYLength()

            if drawable:
                if self.supportClass.measureSettings.measureMethod == MeasureMethod.OSZILATOR:
                    self.ax.clear()
                    self.initAxes()
                    for i in range(LabJackU6Settings.USABLEPORTCOUNT.value):
                        if self.checkboxes[i].isChecked():
                            self.ax.plot(xData, yData[i], color=self.colors[i], marker="None", linestyle="-")
                        else:
                            self.ax.plot([], [], color=self.colors[i], marker="None", linestyle="-")
                    self.canvas.figure.canvas.draw()
                elif self.supportClass.measureSettings.measureMethod == MeasureMethod.DIODE:
                    lastPointX, lastPointY = self.createLastMeasurePointData()
                    self.lines[0].set_xdata(xData)
                    self.lines[0].set_ydata(yData[0])
                    self.lines[1].set_xdata(lastPointX)
                    self.lines[1].set_ydata(lastPointY)

                    self.canvas.draw()
                    self.canvas.flush_events()
