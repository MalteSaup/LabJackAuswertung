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

        self.checkboxChecker = []

        self.supportClass = supportClass
        self.checkboxes = None
        self.pltLayout = None

        self.notStopped = True

        self.timer = None

        self.samplerate = 25
        self.functionCode = functionCode
        self.count = 0

        self.ls = "-"
        self.ms = "."

        self.mVtoV = 1000
        self.mAtoA = 1000

        # self.initUI()

    def initUI(self):
        self.supportClass.container.saveAction.triggered.connect(self.saveClick)
        self.supportClass.container.saveAction.setEnabled(True)

        layout = qt.QHBoxLayout()

        self.checkboxes = CheckBoxes(self.functionCode)

        self.checkboxes.exitButton.pressed.connect(self.returnToMainScreen)
        self.checkboxChecker.append(self.checkboxes.leftCheck.checkBoxes[1])
        self.checkboxChecker.append(self.checkboxes.rightCheck.checkBoxes[1])
        self.checkboxChecker.append(self.checkboxes.leftCheck.checkBoxes[2])
        self.checkboxChecker.append(self.checkboxes.rightCheck.checkBoxes[2])
        self.checkboxChecker.append(self.checkboxes.leftCheck.checkBoxes[0])
        self.checkboxChecker.append(self.checkboxes.rightCheck.checkBoxes[0])

        self.pltLayout = NormalMeasureScreen(self.ax_x, self.ax_y, self.checkboxChecker, self.functionCode, self.count)

        layout.addWidget(self.checkboxes)
        layout.addWidget(self.pltLayout)

        self.samplerate = int(1000 / self.samplerate)

        if self.functionCode == 0:
            self.measureClock()
        elif self.functionCode == 1:
            self.checkboxes.comboBox.currentIndexChanged.connect(self.checkboxLayoutManipulator)
            self.checkboxes.startMeasureButton.pressed.connect(self.startMeasure)

        self.setLayout(layout)

    def updateDataset(self, index):
        if self.notStopped:
            uebergabe = self.supportClass.device.readRegister(0, 26)

            for i in range(4):
                # Da 1000 mV und 1000 Ohm kann Berechnung vernachlässigt werden da 1000 / 1000 = 1
                if self.checkboxChecker[i].isChecked():
                    if i <= 1:
                        self.ax_y[i].append(abs(uebergabe[i*2] - uebergabe[i*2+1]))
                    elif i == 2:
                        self.ax_y[i].append(abs(uebergabe[4] - uebergabe[6]))
                    elif i == 3:
                        self.ax_y[i].append(abs(uebergabe[5] - uebergabe[7]))
                else:
                    self.ax_y[i].append(math.nan)
            if self.functionCode == 0:
                self.ax_x.append(self.count)
                self.count += 1
            elif self.functionCode == 1:
                if index <= 1:
                    self.ax_x.append(abs(uebergabe[index * 2] - uebergabe[index * 2 + 1]) * self.mVtoV)
                elif index == 2:
                    self.ax_x.append(abs(uebergabe[4] - uebergabe[6]) * self.mVtoV)
                elif index == 3:
                    self.ax_x.append(abs(uebergabe[5] - uebergabe[7]) * self.mVtoV)




    def checkboxLayoutManipulator(self):
        for i in range(4):
            type(self.checkboxChecker[i])
            self.checkboxChecker[i].setEnabled(True)
        index = self.checkboxes.comboBox.currentIndex()
        if index % 2 == 1:
            self.checkboxes.rightCheck.checkBoxes[1 + int(index / 3)].setCheckState(False)
            self.checkboxes.rightCheck.checkBoxes[1 + int(index / 3)].setEnabled(False)
        else:
            self.checkboxes.leftCheck.checkBoxes[1 + int(index / 2)].setCheckState(False)
            self.checkboxes.leftCheck.checkBoxes[1 + int(index / 2)].setEnabled(False)

    def startMeasure(self):
        try:
            index = self.checkboxes.comboBox.currentIndex()
        except:
            index = -1
        self.checkboxes.comboBox.setEnabled(False)
        self.measureClock(index)

    def measureClock(self, index=-1):
        self.timer = qtcore.QTimer(self)
        self.timer.timeout.connect(lambda: self.updateDataset(index))
        self.timer.start(self.samplerate)

    def saveClick(self):
        self.notStopped = False
        df, fig = self.createExportData()
        if df is None and fig is None:
            pass
        else:
            self.notStopped = True
            self.exportScreen = export_screen.ExportScreen(df, fig)
            self.exportScreen.show()

    def returnToMainScreen(self):
        if self.timer is not None:
            self.timer.stop()

        if self.pltLayout.timer is not None:
            self.pltLayout.timer.stop()

        self.pltLayout.stopped = True
        self.supportClass.returnMainScreen()

    def createExportData(self):
        if self.pltLayout.checkXYLength()[0]:
            x_ueb = list(self.ax_x)
            y_ueb = copy.deepcopy(self.ax_y)
            fig_ueb = self.pltLayout.canvas.figure
            dataFrame = pd.DataFrame()
            dataFrame.insert(0, "x0", x_ueb, True)
            empty_ueb_arr = [math.nan] * len(x_ueb)
            count = 0
            for i in range(len(y_ueb)):
                if self.checkboxChecker[i].isChecked():
                    dataFrame.insert(len(dataFrame.columns), "y" + str(count), y_ueb[i], True)
                    count += 1
                else:
                    dataFrame.insert(len(dataFrame.columns), "ye" + str(i), empty_ueb_arr, True)

            return dataFrame, fig_ueb
        else:
            timerCreateExData = qtcore.QTimer(self)
            timerCreateExData.timeout.connect(self.saveClick)
            timerCreateExData.setSingleShot(True)
            timerCreateExData.start(100)
            return None, None


class CheckBoxes(qt.QWidget):
    def __init__(self, functionCode):
        super().__init__()
        self.leftCheck = None
        self.rightCheck = None
        self.startMeasureButton = None
        self.exitButton = None
        self.comboBox = None
        self.functionCode = functionCode
        self.initUI()

    def initUI(self):

        hlayout = qt.QHBoxLayout()
        vlayout = qt.QVBoxLayout()

        self.leftCheck = CheckBoxesLeft()
        self.rightCheck = CheckBoxesRight()

        hlayout.addWidget(self.leftCheck)
        hlayout.addWidget(self.rightCheck)

        layoutHolderCheckboxes = qt.QWidget()
        layoutHolderCheckboxes.setLayout(hlayout)

        if self.functionCode == 1:
            label = qt.QLabel("Choose Measure Channel for X-Axes: ")
            options = [
                "Kanal 1",
                "Kanal 2",
                "Kanal 3",
                "Kanal 4"
            ]
            self.comboBox = qt.QComboBox()
            for option in options:
                self.comboBox.addItem(option)
            self.startMeasureButton = qt.QPushButton("Start Measurement")

            vlayout.addWidget(label)
            vlayout.addWidget(self.comboBox)
            vlayout.addWidget(layoutHolderCheckboxes)
            vlayout.addWidget(self.startMeasureButton, 200, qtcore.Qt.AlignBottom)

            self.leftCheck.checkBoxes[1].setCheckState(False)
            self.leftCheck.checkBoxes[1].setEnabled(False)

        else:
            vlayout.addWidget(layoutHolderCheckboxes)

        self.exitButton = qt.QPushButton("Return")
        vlayout.addWidget(self.exitButton)

        self.setLayout(vlayout)


class CheckBoxesLeft(qt.QWidget):
    def __init__(self):
        super().__init__()
        self.checkBoxes = []

        self.initUI()

    def initUI(self):
        layout = qt.QVBoxLayout()

        markerCheck = qt.QCheckBox("Marker", self)
        ai0Check = qt.QCheckBox("AIN0", self)
        ai0Check.setChecked(True)
        ai2Check = qt.QCheckBox("AIN2", self)

        self.checkBoxes.append(markerCheck)
        self.checkBoxes.append(ai0Check)
        self.checkBoxes.append(ai2Check)

        layout.addWidget(markerCheck)
        layout.addWidget(ai0Check)
        layout.addWidget(ai2Check)

        self.setLayout(layout)


class CheckBoxesRight(qt.QWidget):
    def __init__(self):
        super().__init__()
        self.checkBoxes = []

        self.initUI()

    def initUI(self):
        layout = qt.QVBoxLayout()

        lineCheck = qt.QCheckBox("Line", self)
        lineCheck.setChecked(True)
        ai1Check = qt.QCheckBox("AIN1", self)
        ai3Check = qt.QCheckBox("AIN3", self)

        self.checkBoxes.append(lineCheck)
        self.checkBoxes.append(ai1Check)
        self.checkBoxes.append(ai3Check)

        layout.addWidget(lineCheck)
        layout.addWidget(ai1Check)
        layout.addWidget(ai3Check)

        self.setLayout(layout)


class NormalMeasureScreen(qt.QWidget):
    def __init__(self, ax_x, ax_y, checkboxes, functionCode, count=0):
        super().__init__()
        self.ax_x = ax_x
        self.ax_y = ax_y
        self.checkboxes = checkboxes
        self.canvas = None

        self.xue = []
        self.yue = []

        self.resolutionX = 1000

        self.functionCode = functionCode
        self.count = count

        self.stopped = False
        self.timer = None

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

    def animation(self):
        if not self.stopped:
            if self.checkboxes[-2].isChecked():
                self.ms = "."
            else:
                self.ms = "None"
            if self.checkboxes[-1].isChecked():
                self.ls = "-"
            else:
                self.ls = "None"

            drawable, x_ue, y_ue = self.checkXYLength()

            self.ax.clear()
            self.ax.set_ylim([-1, 11])

            if self.functionCode == 0:
                if (self.xue == []):

                    self.ax.set_xlim([0, self.resolutionX])
                else:
                    if (self.xue[-1] > 10):
                        self.ax.set_xlim([self.xue[-1] - self.resolutionX, self.xue[-1]])
                    else:
                        self.ax.set_xlim([0, self.resolutionX])

            elif self.functionCode == 1:
                self.ax.set_xlim([0, self.resolutionX])

            if drawable:
                self.xue = list(x_ue)
                self.yue = copy.deepcopy(y_ue)

                for i in range(4):
                    if self.checkboxes[i].isChecked():
                        self.ax.plot(self.xue, self.yue[i], linestyle=self.ls, marker=self.ms, markersize=0.8)
                self.canvas.figure.canvas.draw()

            else:
                for i in range(4):
                    if self.checkboxes[i].isChecked():
                        self.ax.plot(self.xue, self.yue[i], linestyle=self.ls, marker=self.ms, markersize=0.8)
                self.canvas.figure.canvas.draw()

    def checkXYLength(self):
        x_ue = list(self.ax_x)
        y_ue = copy.deepcopy(self.ax_y)

        lengthX = len(x_ue)

        sameLength = True

        for i in range(4):
            if not lengthX == len(y_ue[i]):
                sameLength = False
        return sameLength, x_ue, y_ue
