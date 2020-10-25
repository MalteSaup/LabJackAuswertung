import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

import math

import copy

import matplotlib.backends.qt_compat as qtplt
import matplotlib.figure as fig

from helper import MeasureMethod, LabJackU6

if qtplt.is_pyqt5():
    import matplotlib.backends.backend_qt5agg as pyqtplt
else:
    import matplotlib.backends.backend_qt4agg as pyqtplt


class MeasureScreenPlot(qt.QWidget):
    def __init__(self, axisX, axisY, checkboxes, supportClass, resolutionX=100):
        super().__init__()
        self.axisX = axisX
        self.axisY = axisY
        self.checkboxes = checkboxes
        self.canvas = None
        self.ax = None

        self.xData = []
        self.yData = []

        self.resolutionX = resolutionX

        self.measureMethod = supportClass.measureSettings.measureMethod

        self.supportClass = supportClass

        self.stopped = False
        self.timer = None

        self.colors = ["red", "blue", "green", "yellow"]

        self.initUI()

    def initUI(self):
        layout = qt.QHBoxLayout()
        self.canvas = pyqtplt.FigureCanvas(fig.Figure())
        self.ax = self.canvas.figure.subplots()

        self.timer = self.canvas.new_timer(150)
        self.timer.add_callback(self.animation)
        self.timer.start()

        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def createLastMeasurePointData(self, xData, yData):
        if len(xData) == 0:
            return [math.nan], [[math.nan], [math.nan], [math.nan], [math.nan]]
        xMeasurePoint = [math.nan] * len(xData)
        xMeasurePoint[-1] = xData[-1]
        yMeasurePoints = []

        emptyArr = [math.nan] * len(yData[0])

        for i in range(len(yData)):
            yMeasurePoints.append(emptyArr.copy())
            yMeasurePoints[i][-1] = yData[i][-1]

        return xMeasurePoint, yMeasurePoints

    def createXAxisLimits(self):
        if self.measureMethod == MeasureMethod.OSZILATOR:
            if self.xData == [] or self.xData[-1] < self.resolutionX:
                return [0, self.resolutionX]
            else:
                return [self.xData[-1] - self.resolutionX, self.xData[-1]]

        elif self.measureMethod == MeasureMethod.DIODE:
            return [0, self.supportClass.measureSettings.udMax]

    def createYAxisLimits(self):
        if (self.supportClass.measureSettings.measureMethod == MeasureMethod.OSZILATOR):
            return [0, LabJackU6.MAXVOLTAGE.value]
        if (self.supportClass.measureSettings.measureMethod == MeasureMethod.DIODE):
            return [0, self.supportClass.measureSettings.idMax]

    def checkXYLength(self):
        xData = list(self.axisX)
        yData = copy.deepcopy(self.axisY)

        lengthX = len(xData)

        sameLength = True

        for i in range(4):
            if not lengthX == len(yData[i]):
                sameLength = False
        return sameLength, xData, yData

    def animation(self):
        if not self.stopped:
            drawable, xData, yData = self.checkXYLength()

            self.ax.clear()

            self.ax.set_xlim(self.createXAxisLimits())
            self.ax.set_ylim(self.createYAxisLimits())

            if drawable:
                self.xData = list(xData)
                self.yData = copy.deepcopy(yData)

            xMarker, yMarker = self.createLastMeasurePointData(self.xData, self.yData)

            for i in range(4):
                if self.checkboxes[i].isChecked() and (
                        self.supportClass.measureSettings.udPort != i or self.measureMethod == MeasureMethod.OSZILATOR):
                    if len(self.xData) == 0:
                        self.ax.plot([], [], color=self.colors[i], linestyle="-", marker="None")
                    else:
                        if self.measureMethod == MeasureMethod.OSZILATOR:
                            self.ax.plot(self.xData, self.yData[i], color=self.colors[i], linestyle="-", marker="None")
                        elif self.measureMethod == MeasureMethod.DIODE:
                            self.ax.plot(self.xData, self.yData[i], color=self.colors[i], linestyle="None", marker=".",
                                         markersize=1.5)
                            self.ax.plot(xMarker, yMarker[i], color=self.colors[i], linestyle="None", marker="X",
                                         markersize=4)

            if self.measureMethod == MeasureMethod.OSZILATOR:
                self.ax.text(-0.05, 0.5, "Voltage/[V]", horizontalalignment='right',
                             verticalalignment='center',
                             rotation='vertical',
                             transform=self.ax.transAxes)
                self.ax.text(0.5, -0.08, "Samplecount", horizontalalignment='center',
                             verticalalignment='top',
                             transform=self.ax.transAxes)

            if self.measureMethod == MeasureMethod.DIODE:
                self.ax.text(-0.05, 0.5, "Ud/[V]", horizontalalignment='right',
                             verticalalignment='center',
                             rotation='vertical',
                             transform=self.ax.transAxes)
                self.ax.text(0.5, -0.08, "Id/[mA]", horizontalalignment='center',
                             verticalalignment='top',
                             transform=self.ax.transAxes)

            self.canvas.figure.canvas.draw()
