
import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

import copy


import matplotlib.backends.qt_compat as qtplt
import matplotlib.figure as fig
import matplotlib.pyplot as plt
if qtplt.is_pyqt5():
    import matplotlib.backends.backend_qt5agg as pyqtplt
else:
    import matplotlib.backends.backend_qt4agg as pyqtplt

class TransistorMeasureScreenWidget(qt.QWidget):
    def __init__(self, measureData, uceMinMax, ubeMinMax, uceTick, uceTickLabel, ubeTick, ubeTickLabel):
        super().__init__()

        self.stopped = False

        self.axes = None
        self.fig = None

        self.timer = None

        self.canvas = None

        self.measureData = measureData
        self.uceTick = uceTick
        self.ubeTick = ubeTick
        self.uceTickLabel = uceTickLabel
        self.ubeTickLabel = ubeTickLabel
        self.uceMinMax = uceMinMax
        self.ubeMinMax = ubeMinMax

        self.initUI()

    def initUI(self):
        layout = qt.QHBoxLayout()

        self.canvas = pyqtplt.FigureCanvas(fig.Figure())

        axes = self.canvas.figure.subplots(2, 2, gridspec_kw={"hspace": 0, "wspace": 0})
        self.timer = self.canvas.new_timer(250)
        self.timer.add_callback(self.animation)

        layout.addWidget(self.canvas)
        (ax1, ax2), (ax3, ax4) = axes

        self.axes = [ax1, ax2, ax3, ax4]
        layout.addWidget(self.canvas)

        self.initAxes()
        self.setLayout(layout)

    def animation(self):
        sameLength, arrUeb = self.checkLength()
        #print(sameLength)
        if sameLength:

            length = len(arrUeb)
            emptyArr = [None] * length
            icCross = emptyArr.copy()
            uceCross = emptyArr.copy()
            ubeCross = emptyArr.copy()
            ibCross = emptyArr.copy()

            icCross[-1] = arrUeb[0][-1]
            uceCross[-1] = arrUeb[1][-1]
            ubeCross[-1] = arrUeb[2][-1]
            ibCross[-1] = arrUeb[3][-1]

            for ax in self.axes:
                ax.clear()
            self.initAxes()
            self.axes[0].plot(arrUeb[3], arrUeb[0], color="green", linestyle="None", marker=".", markersize=1)
            self.axes[1].plot(arrUeb[1], arrUeb[0], color="red", linestyle="None", marker=".", markersize=1)
            self.axes[2].plot(arrUeb[3], arrUeb[2], color="blue", linestyle="None", marker=".", markersize=1)

            self.axes[0].plot(ibCross, icCross, color="yellow", linestyle="None", marker="X", markersize=4)
            self.axes[1].plot(uceCross, icCross, color="yellow", linestyle="None", marker="X", markersize=4)
            self.axes[2].plot(ibCross, ubeCross, color="yellow", linestyle="None", marker="X", markersize=4)

        self.canvas.figure.canvas.draw()

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
        self.axes[1].set_yticklabels(["", 10, 20, 30, "Ic"])
        self.axes[1].set_xlim(0, 12)
        self.axes[1].set_ylim(0, 40)
        self.axes[1].get_xaxis().set_visible(False)

        self.axes[2].spines["bottom"].set_color("none")
        self.axes[2].spines["left"].set_color("none")
        self.axes[2].get_yaxis().set_visible(False)
        self.axes[2].set_xticks([0, 50, 100, 150, 200, 220])
        self.axes[2].set_xticklabels(["", 50, 100, 150, 200, "Ib"])
        self.axes[2].set_xlim(0, 220)
        self.axes[2].set_ylim(0, 1.0)
        self.axes[2].invert_xaxis()
        self.axes[2].invert_yaxis()
        self.axes[2].xaxis.tick_top()

        self.axes[3].spines["right"].set_color("none")
        self.axes[3].spines["bottom"].set_color("none")
        self.axes[3].set_xticks(self.uceTick)
        self.axes[3].set_xticklabels(self.uceTickLabel)
        self.axes[3].set_yticks(self.ubeTick)
        self.axes[3].set_yticklabels(self.ubeTickLabel)
        self.axes[3].set_xlim(self.uceMinMax[0], self.uceMinMax[1])
        self.axes[3].set_ylim(self.ubeMinMax[0], self.ubeMinMax[1])
        self.axes[3].invert_yaxis()
        self.axes[3].xaxis.tick_top()



    def checkLength(self):

        arr_ueb = copy.deepcopy(self.measureData)

        length = len(arr_ueb[0])

        sameLength = True

        for i in range(len(arr_ueb)):
            if not length == len(arr_ueb[i]):
                sameLength = False
        return sameLength, arr_ueb