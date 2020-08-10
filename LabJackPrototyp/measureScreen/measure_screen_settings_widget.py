import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore


class Settings(qt.QWidget):
    def __init__(self, functionCode, xAxisPlot = 0):
        super().__init__()
        self.startMeasureButton = None
        self.returnButton = None
        self.addMeasurePointButton = None
        self.measurePointLabel = None
        self.checkBoxes = []
        self.xAxisPlot = xAxisPlot
        self.functionCode = functionCode
        self.initUI()
        self.channel1Check = None
        self.channel2Check = None
        self.channel3Check = None
        self.channel4Check = None

    def initUI(self):

        layout = qt.QGridLayout()

        xAxisPlotLabel = qt.QLabel("X-Axis Plotted Channel: " + str(self.xAxisPlot))
        self.measurePointLabel = qt.QLabel("Measure Points: 1")

        self.channel1Check = qt.QCheckBox("Channel 1", self)
        self.channel2Check = qt.QCheckBox("Channel 2", self)
        self.channel3Check = qt.QCheckBox("Channel 3", self)
        self.channel4Check = qt.QCheckBox("Channel 4", self)

        self.checkBoxes.append(self.channel1Check)
        self.checkBoxes.append(self.channel2Check)
        self.checkBoxes.append(self.channel3Check)
        self.checkBoxes.append(self.channel4Check)

        self.startMeasureButton = qt.QPushButton("Start Measurement")
        self.addMeasurePointButton = qt.QPushButton("Add Measure Point")
        self.returnButton = qt.QPushButton("Return")

        layout.addWidget(self.channel1Check, 1, 0)
        layout.addWidget(self.channel2Check, 2, 0)
        layout.addWidget(self.channel3Check, 3, 0)
        layout.addWidget(self.channel4Check, 4, 0)
        layout.addWidget(self.returnButton, 8, 0, 1, 2)

        if self.functionCode == 1:
            layout.addWidget(xAxisPlotLabel, 0, 0)
            layout.addWidget(self.measurePointLabel, 5, 0)
            layout.addWidget(self.startMeasureButton, 6, 0, 1, 2)
            layout.addWidget(self.addMeasurePointButton, 7, 0, 1, 2)

        self.setLayout(layout)

