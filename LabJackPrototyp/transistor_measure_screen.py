import math

import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

import copy
import pandas as pd

import matplotlib.backends.qt_compat as qtplt
import matplotlib.figure as fig
import matplotlib.pyplot as plt

import export_screen

if qtplt.is_pyqt5():
    import matplotlib.backends.backend_qt5agg as pyqtplt
else:
    import matplotlib.backends.backend_qt4agg as pyqtplt
"""

canvas = pyqtplt.FigureCanvasAgg(fig)
canvas.resize(774, canvas.get_width_height()[1])"""



class TransistorScreen(qt.QWidget):
    def __init__(self, supportClass):
        super().__init__()
        plt.style.use("dark_background")
        plt.tight_layout()

        self.supportClass = supportClass
        self.samplerate = 25

        self.columnNames = ["IC", "UCE", "UBE", "IB"]

        self.measureData = [[], [], [], []]
        self.measurePorts = None

        self.notStopped = True

        self.timer = None

    def initUI(self):
        layout = qt.QHBoxLayout()
        self.cbh = ComboBoxHolder()
        self.plt = TransistorMeasureScreen(self.measureData)
        layout.addWidget(self.cbh)
        layout.addWidget(self.plt)
        self.samplerate = 1000 / 25
        self.setLayout(layout)
        self.supportClass.container.saveAction.triggered.connect(self.saveClick)
        self.supportClass.container.saveAction.setEnabled(True)

        self.cbh.returnButton.pressed.connect(self.returnToMainScreen)
        self.cbh.startMeasureButton.pressed.connect(self.startMeasure)

        for i in range(len(self.cbh.comboBoxes)):
            self.cbh.comboBoxes[i].currentIndexChanged.connect(lambda x=i: self.comboBoxChecker(x))

        self.show()
        self.plt.canvas.resize(774, 424)

    def comboBoxChecker(self, numb):
        currentIndexe = []
        for i in range(len(self.cbh.comboBoxes)):
            if self.cbh.comboBoxes[i].currentIndex() != 0:
                currentIndexe.append([i, self.cbh.comboBoxes[i].currentIndex()])
        for i in range(len(self.cbh.comboBoxes)):
            for j in range(self.cbh.comboBoxes[i].count()):
                self.cbh.comboBoxes[i].model().item(j).setEnabled(True)
            for index in currentIndexe:
                if i != index[0]:
                    self.cbh.comboBoxes[i].model().item(index[1]).setEnabled(False)

    def updateDataset(self):
        if self.notStopped:
            uebergabe = self.supportClass.device.readRegister(0, 26)

            self.measureData[0].append((abs(uebergabe[self.measurePorts[0]]))*2.0)
            self.measureData[1].append((abs(uebergabe[self.measurePorts[1]]))*22.0)
            self.measureData[2].append((abs(uebergabe[self.measurePorts[2]]))*0.08)
            self.measureData[3].append((abs(uebergabe[self.measurePorts[3]]))*22.0)

            print(self.measureData)

    def comboboxLayoutManipulator(self):
        print()
        #TODO ANHAND DER AUSWAHL BEI COMBOBOXEN DIE ITEMS BEI DEN ANDEREN SPERREN

    def startMeasure(self):
        self.measurePorts = [self.cbh.comboBoxes[1].currentIndex()-1, self.cbh.comboBoxes[2].currentIndex()-1, self.cbh.comboBoxes[3].currentIndex()-1, self.cbh.comboBoxes[0].currentIndex()-1]
        for comboBox in self.cbh.comboBoxes:
            comboBox.setEnabled(False)
        print(self.measurePorts)
        #TODO BEHAVIOUR CHECK WHEN ONE COMBOBOX HAS NO VALUE
        self.measureClock()

    def measureClock(self):
        self.timer = qtcore.QTimer(self)
        self.timer.timeout.connect(self.updateDataset)
        self.timer.start(self.samplerate)
        self.plt.timer.start()

    def saveClick(self):
        self.notStopped = False
        df, fig = self.createExportData()
        if df is None and fig is None:
            pass
        else:
            self.notStopped = True
            self.exportScreen = export_screen.ExportScreen(df, fig, self.columnNames)
            self.exportScreen.show()

    def returnToMainScreen(self):
        if self.timer is not None:
            self.timer.stop()

        if self.pltLayout.timer is not None:
            self.pltLayout.timer.stop()

        self.pltLayout.stopped = True
        self.supportClass.returnMainScreen()

    def createExportData(self):
        if self.plt.checkLength()[0]:
            data_ueb = copy.deepcopy(self.measureData)
            fig_ueb = self.plt.canvas.figure
            dataFrame = pd.DataFrame()
            for i in range(len(data_ueb)):
                dataFrame.insert(i, self.columnNames[i], data_ueb[i], True)

            return dataFrame, fig_ueb
        else:
            timerCreateExData = qtcore.QTimer(self)
            timerCreateExData.timeout.connect(self.saveClick)
            timerCreateExData.setSingleShot(True)
            timerCreateExData.start(100)
            return None, None

    def returnToMainScreen(self):
        if self.timer is not None:
            self.timer.stop()

        if self.plt.timer is not None:
            self.plt.timer.stop()

        self.plt.stopped = True
        self.supportClass.returnMainScreen()

class ComboBoxHolder(qt.QWidget):
    def __init__(self):
        super().__init__()
        self.options = [
            "None",
            "AIN 0",
            "AIN 1",
            "AIN 2",
            "AIN 3"
        ]
        self.comboBoxes = []
        self.returnButton = None
        self.startMeasureButton = None
        self.initUI()


    def initUI(self):
        layout = qt.QVBoxLayout()

        #Creation Combo Boxes
        cb_ib = qt.QComboBox()
        cb_ic = qt.QComboBox()
        cb_uce = qt.QComboBox()
        cb_ube = qt.QComboBox()

        for option in self.options:
            cb_ib.addItem(option)
            cb_ic.addItem(option)
            cb_uce.addItem(option)
            cb_ube.addItem(option)

        self.comboBoxes.append(cb_ib)
        self.comboBoxes.append(cb_ic)
        self.comboBoxes.append(cb_uce)
        self.comboBoxes.append(cb_ube)

        #Layouting Combo Boxes with Widgets and Layouts
        w_ib = qt.QWidget()
        w_ic = qt.QWidget()
        w_uce = qt.QWidget()
        w_ube = qt.QWidget()

        layout_ib = qt.QHBoxLayout()
        layout_ic = qt.QHBoxLayout()
        layout_uce = qt.QHBoxLayout()
        layout_ube = qt.QHBoxLayout()

        layout_ib.addWidget(qt.QLabel("IB"))
        layout_ic.addWidget(qt.QLabel("IC"))
        layout_uce.addWidget(qt.QLabel("UCE"))
        layout_ube.addWidget(qt.QLabel("UCB"))

        layout_ib.addWidget(cb_ib)
        layout_ic.addWidget(cb_ic)
        layout_uce.addWidget(cb_uce)
        layout_ube.addWidget(cb_ube)

        w_ib.setLayout(layout_ib)
        w_ic.setLayout(layout_ic)
        w_uce.setLayout(layout_uce)
        w_ube.setLayout(layout_ube)

        #Adding Widgets
        layout.addWidget(w_ib)
        layout.addWidget(w_ic)
        layout.addWidget(w_uce)
        layout.addWidget(w_ube)

        self.startMeasureButton = qt.QPushButton("Start Measure")
        self.returnButton = qt.QPushButton("Return")

        layout.addWidget(self.startMeasureButton)
        layout.addWidget(self.returnButton)

        self.setLayout(layout)


class TransistorMeasureScreen(qt.QWidget):
    def __init__(self, measureData):
        super().__init__()

        self.stopped = False

        self.axes = None
        self.fig = None

        self.timer = None

        self.canvas = None

        self.measureData = measureData

        self.initUI()

    def initUI(self):
        layout = qt.QHBoxLayout()
        #self.fig, axes = plt.subplots(2, 2, gridspec_kw={"hspace": 0, "wspace": 0})


        self.canvas = pyqtplt.FigureCanvas(fig.Figure())
        axes = self.canvas.figure.subplots(2, 2, gridspec_kw={"hspace": 0, "wspace": 0})
        self.timer = self.canvas.new_timer(250)
        self.timer.add_callback(self.animation)

        self.canvas.figure.set_size_inches(4,4,True)

        layout.addWidget(self.canvas)

        (ax1, ax2), (ax3, ax4) = axes

        self.axes = [ax1, ax2, ax3, ax4]
        layout.addWidget(self.canvas)

        self.initAxes()
        self.setLayout(layout)
    def animation(self):
        sameLength, arrUeb = self.checkLength()
        if sameLength:
            for ax in self.axes:
                ax.clear()
            self.initAxes()
            self.axes[0].plot(arrUeb[3], arrUeb[0], color="green", linestyle="None", marker=".", markersize=0.8)
            self.axes[1].plot(arrUeb[1], arrUeb[0], color="red", linestyle="None", marker=".", markersize=0.8)
            self.axes[2].plot(arrUeb[3], arrUeb[2], color="blue", linestyle="None", marker=".", markersize=0.8)
            self.axes[3].plot(arrUeb[1], arrUeb[2], color="yellow", linestyle="None", marker=".", markersize=0.8)


        """for i in range(4):
            self.ax.plot(self.xue, self.yue[i], linestyle="None", marker=".", markersize=0.8)
        """
        self.canvas.figure.canvas.draw()

    def initAxes(self):
        """t1 = self.t1()
        tx1 = self.tx1()
        t2 = self.t2()
        tx2 = self.tx2()

        self.axes[0].plot(t1, tx1, color="green")
        self.axes[1].plot(t2, tx1, color="red")
        self.axes[2].plot(t1, tx2[::-1], color="blue")
        self.axes[3].plot(t2, tx2, color="yellow")"""

        self.axes[0].spines["top"].set_color("none")
        self.axes[0].spines["left"].set_color("none")
        #self.axes[0].set_xticks([0, 50, 100, 150, 200, 250])
        self.axes[0].set_xlim(0, 270)
        self.axes[0].set_ylim(0, 30)
        self.axes[0].get_xaxis().set_visible(False)
        self.axes[0].get_yaxis().set_visible(False)
        self.axes[0].invert_xaxis()

        self.axes[1].spines["top"].set_color("none")
        self.axes[1].spines["right"].set_color("none")
        self.axes[1].get_xaxis().set_visible(False)
        self.axes[1].set_yticks([0, 10, 20, 30])
        self.axes[1].set_yticklabels(["", 10, 20, 30])
        self.axes[1].set_xlim(0, 30)
        self.axes[1].set_ylim(0, 30)

        self.axes[2].spines["bottom"].set_color("none")
        self.axes[2].spines["left"].set_color("none")
        self.axes[2].get_yaxis().set_visible(False)
        self.axes[2].set_xticks([0, 50, 100, 150, 200, 250])
        self.axes[2].set_xticklabels(["", 50, 100, 150, 200, 250])
        self.axes[2].set_xlim(0, 270)
        self.axes[2].set_ylim(0, 1.0)
        self.axes[2].invert_xaxis()
        self.axes[2].xaxis.tick_top()

        self.axes[3].spines["right"].set_color("none")
        self.axes[3].spines["bottom"].set_color("none")
        self.axes[3].set_xticks([0, 10, 20, 30])
        self.axes[3].set_xticklabels(["", 10, 20, 30])
        self.axes[3].set_yticks([0, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
        self.axes[3].set_yticklabels(["", 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
        self.axes[3].set_xlim(0, 30)
        self.axes[3].set_ylim(0, 1.0)
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

    def t1(self):
        ls = []
        count = 0
        for i in range(100):
            ls.append(count)
            count += 270 / 100
        return ls

    def t2(self):
        ls = []
        count = 0
        for i in range(100):
            ls.append(count)
            count += 40 / 100
        return ls

    def tx1(self):
        ls = []
        count = 0
        for i in range(100):
            ls.append(count)
            count += 30 / 100
        return ls

    def tx2(self):
        ls = []
        count = 0
        for i in range(100):
            ls.append(count)
            count += 1 / 100
        return ls