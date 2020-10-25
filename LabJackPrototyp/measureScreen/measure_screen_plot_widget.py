import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

import math
import threading

import copy

import matplotlib.backends.qt_compat as qtplt
import matplotlib.figure as fig

if qtplt.is_pyqt5():
    import matplotlib.backends.backend_qt5agg as pyqtplt
else:
    import matplotlib.backends.backend_qt4agg as pyqtplt

class MeasureScreenPlot(qt.QWidget):
    def __init__(self, ax_x, ax_y, checkboxes, functionCode, resolutionX = 10):
        super().__init__()
        self.ax_x = ax_x
        self.ax_y = ax_y
        self.checkboxes = checkboxes
        self.canvas = None

        self.xue = []
        self.yue = []

        self.resolutionX = resolutionX

        self.functionCode = functionCode

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

    def createLastMeasurePointData(self, x_ue, y_ue):
        if len(x_ue) == 0:
            return [math.nan],  [[math.nan], [math.nan], [math.nan], [math.nan]]
        xMeasurePoint = [math.nan] * len(x_ue)
        xMeasurePoint[-1] = x_ue[-1]
        yMeasurePoints = []

        emptyArr = [math.nan] * len(y_ue[0])

        for i in range(len(y_ue)):
            yMeasurePoints.append(emptyArr.copy())
            yMeasurePoints[i][-1] = y_ue[i][-1]

        return xMeasurePoint, yMeasurePoints

    def createXAxisLimits(self):
        if self.functionCode == 0:
            if self.xue == [] or self.xue[-1] < self.resolutionX:
                return [0, self.resolutionX]
            else:
                return[self.xue[-1] - self.resolutionX, self.xue[-1]]

        elif self.functionCode == 1:
            return [0, self.resolutionX]

    def checkXYLength(self):
        x_ue = list(self.ax_x)
        y_ue = copy.deepcopy(self.ax_y)

        lengthX = len(x_ue)

        sameLength = True

        for i in range(4):
            if not lengthX == len(y_ue[i]):
                sameLength = False
        return sameLength, x_ue, y_ue

    def animation(self):
        if not self.stopped:
            drawable, x_ue, y_ue = self.checkXYLength()

            self.ax.clear()
            self.ax.set_ylim([0, 1]) #TODO NACH MESS CODE RICHTEN

            self.ax.set_xlim(self.createXAxisLimits())

            if drawable:
                self.xue = list(x_ue)
                self.yue = copy.deepcopy(y_ue)

            xMarker, yMarker = self.createLastMeasurePointData(self.xue, self.yue)

            for i in range(4):
                if self.checkboxes[i].isChecked():
                    if len(self.xue) == 0:
                        self.ax.plot([], [], color=self.colors[i], linestyle="-", marker="None")
                    else:
                        if self.functionCode == 0:
                            self.ax.plot(self.xue, self.yue[i], color=self.colors[i], linestyle="-", marker="None")
                        elif self.functionCode == 1:
                            self.ax.plot(self.xue, self.yue[i], color=self.colors[i], linestyle="None", marker=".",
                                         markersize=1)
                            self.ax.plot(xMarker, yMarker[i], color=self.colors[i], linestyle="None", marker="X",
                                         markersize=4)

            self.canvas.figure.canvas.draw()

