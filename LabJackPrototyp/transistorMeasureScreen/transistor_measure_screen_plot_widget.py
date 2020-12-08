import math

import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

import copy
from datetime import datetime

import matplotlib.backends.qt_compat as qtplt
import matplotlib.figure as fig
import matplotlib.pyplot as plt
if qtplt.is_pyqt5():
    import matplotlib.backends.backend_qt5agg as pyqtplt
else:
    import matplotlib.backends.backend_qt4agg as pyqtplt

class TransistorMeasureScreenWidget(qt.QWidget):
    def __init__(self, measureData, measureSeriesForMeasureData, uceMax, ubeMax, uceTick, uceTickLabel, ubeTick, ubeTickLabel, screenGeometry):
        super().__init__()

        self.stopped = False

        self.axes = None
        self.lines = []
        self.fig = None

        self.timer = None

        self.canvas = None

        self.b = None
        self.prevB = None

        self.screenGeometry = screenGeometry

        self.measureData = measureData
        self.measureSeries = measureSeriesForMeasureData
        self.uceTick = uceTick
        self.ubeTick = ubeTick
        self.uceTickLabel = uceTickLabel
        self.ubeTickLabel = ubeTickLabel
        self.uceMax = uceMax
        self.ubeMax = ubeMax
        self.ibMax = 250

        self.colors = ["green", "red", "blue", "white"]
        self.now = datetime.now().strftime('%Y.%m.%d %H:%M')

        self.measureSeriesToDisplay = 0

        self.initUI()

    def initUI(self):
        layout = qt.QHBoxLayout()
        self.setFixedWidth(self.screenGeometry.width())

        self.canvas = pyqtplt.FigureCanvas(fig.Figure())
        axes = self.canvas.figure.subplots(2, 2, gridspec_kw={"hspace": 0, "wspace": 0})

        layout.addWidget(self.canvas)
        (ax1, ax2), (ax3, ax4) = axes

        self.axes = [ax1, ax2, ax3, ax4]
        layout.addWidget(self.canvas)

        self.initAxes()
        self.setLayout(layout)

        self.timer = self.canvas.new_timer(150)
        self.timer.add_callback(self.animation)
        self.timer.start()

        self.initAxes()
        self.getLines()


    def createBData(self):
        bDataIb = []
        bDataIc = []
        count = 0
        step = self.ibMax / 100
        for i in range(100):
            bDataIb.append(count)
            bDataIc.append(count * self.b / 1000)
            count += step
        return [bDataIb, bDataIc]

    def animation(self):
        if not self.stopped:
            sameLength, arrUeb = self.checkLength()

            if sameLength and len(arrUeb[0]) > 0:

                bData = None
                print(self.b, self.prevB)
                if self.b != self.prevB:
                    if self.b is None or type(self.b) == str:
                        bData = [[], []]
                    else:
                        bData = self.createBData()
                    self.prevB = self.b
                    print(bData)

                length = len(arrUeb)
                emptyArr = [math.nan] * length
                icCross = emptyArr.copy()
                uceCross = emptyArr.copy()
                ubeCross = emptyArr.copy()
                ibCross = emptyArr.copy()

                icCross[-1] = arrUeb[0][-1]
                uceCross[-1] = arrUeb[1][-1]
                ubeCross[-1] = arrUeb[2][-1]
                ibCross[-1] = arrUeb[3][-1]

                self.lines[0][0].set_xdata(arrUeb[3])
                self.lines[0][0].set_ydata(arrUeb[0])

                self.lines[1][0].set_xdata(arrUeb[1])
                self.lines[1][0].set_ydata(arrUeb[0])

                self.lines[2][0].set_xdata(arrUeb[3])
                self.lines[2][0].set_ydata(arrUeb[2])

                self.lines[0][1].set_xdata(ibCross)
                self.lines[0][1].set_ydata(icCross)

                self.lines[1][1].set_xdata(uceCross)
                self.lines[1][1].set_ydata(icCross)

                self.lines[2][1].set_xdata(ibCross)
                self.lines[2][1].set_ydata(ubeCross)

                if bData is not None:
                    self.lines[3][1].set_xdata(bData[0])
                    self.lines[3][1].set_ydata(bData[1])


                self.canvas.draw()
                self.canvas.flush_events()

    def initAxes(self):
        self.axes[0].spines["top"].set_color("none")
        self.axes[0].spines["left"].set_color("none")
        self.axes[0].set_xlim(0, 200)
        self.axes[0].set_ylim(0, 40)
        self.axes[0].get_xaxis().set_visible(False)
        self.axes[0].get_yaxis().set_visible(False)
        self.axes[0].invert_xaxis()

        self.axes[1].spines["top"].set_color("none")
        self.axes[1].spines["right"].set_color("none")
        self.axes[1].set_yticks([0, 10, 20, 30, 40])
        self.axes[1].set_yticklabels(["", 10, 20, 30, 40])
        self.axes[1].set_xlim(0, 12)
        self.axes[1].set_ylim(0, 40)
        self.axes[1].get_xaxis().set_visible(False)
        self.axes[1].text(0, 1.1, "Ic/[mA]", horizontalalignment='center', verticalalignment='center', transform=self.axes[1].transAxes)

        self.axes[2].spines["bottom"].set_color("none")
        self.axes[2].spines["left"].set_color("none")
        self.axes[2].get_yaxis().set_visible(False)
        self.axes[2].set_xticks([0, 50, 100, 150, 200, 200])
        self.axes[2].set_xticklabels(["", 50, 100, 150, 200])
        self.axes[2].set_yticks(self.ubeTick)
        self.axes[2].set_xlim(0, 220)
        self.axes[2].set_ylim(0, self.ubeMax)
        self.axes[2].invert_xaxis()
        self.axes[2].invert_yaxis()
        self.axes[2].xaxis.tick_top()
        self.axes[2].text(-0.05, 1, "Ib/[μA]", horizontalalignment='right', verticalalignment='center', transform=self.axes[2].transAxes)
        self.axes[2].text(1, -0.1, "Ube/[V]", horizontalalignment='center', verticalalignment='center', transform=self.axes[2].transAxes)

        self.axes[3].spines["right"].set_color("none")
        self.axes[3].spines["bottom"].set_color("none")
        self.axes[3].set_xticks(self.uceTick)
        self.axes[3].set_xticklabels(self.uceTickLabel)
        self.axes[3].set_yticks(self.ubeTick)
        self.axes[3].set_yticklabels(self.ubeTickLabel)
        self.axes[3].set_xlim(0, self.uceMax)
        self.axes[3].set_ylim(0, self.ubeMax)
        self.axes[3].invert_yaxis()
        self.axes[3].xaxis.tick_top()
        self.axes[3].yaxis.tick_right()
        self.axes[3].spines["right"].set_position(["axes", 0])
        self.axes[3].text(1.25, 1, "Uce/[V]", horizontalalignment='right', verticalalignment='center',
                          transform=self.axes[3].transAxes)

    def getLines(self):
        for i in range(3):
            linePlt, = self.axes[i].plot([], [], color=self.colors[i], linestyle="None", marker=".", markersize=1)
            lineCross, = self.axes[i].plot([], [], color="yellow", linestyle="None", marker="X", markersize=4)
            self.lines.append([linePlt, lineCross])
        linePlt, = self.axes[3].plot([], [], color="white", linestyle="None", marker="None")
        lineB, = self.axes[0].plot([], [], color="white", linestyle="-", marker="None")
        self.lines.append([linePlt, lineB])

    def updateLabel(self):
        self.now = datetime.now().strftime('%Y.%m.%d %H:%M')

    def checkLength(self):
        arr_ueb = copy.deepcopy(self.measureData)

        length = len(arr_ueb[0])

        sameLength = True

        for i in range(len(arr_ueb)):
            if not length == len(arr_ueb[i]):
                sameLength = False

        if self.measureSeriesToDisplay == 0:
            return sameLength, arr_ueb
        else:
            try:
                upper = self.measureSeries.index(self.measureSeriesToDisplay + 1)
            except:
                upper = -1
            try:
                lower = self.measureSeries.index(self.measureSeriesToDisplay)
            except:
                upper = -1
                lower = -1

            arrCutted = [arr[lower:upper] for arr in arr_ueb]


            return sameLength, arrCutted
