import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore


class Settings(qt.QWidget):
    def __init__(self, functionCode, xAxisPlot = 0):
        super().__init__()

        self.startMeasureButton = None
        self.returnButton = None
        self.addMeasureSeriesButton = None

        self.measureSeriesLabel = None

        self.checkBoxes = []

        self.xAxisPlot = xAxisPlot
        self.functionCode = functionCode

        self.channelData = []

        self.channel1Check = None
        self.channel2Check = None
        self.channel3Check = None
        self.channel4Check = None

        self.initUI()



    def initUI(self):

        layout = qt.QGridLayout()

        xAxisPlotLabel = qt.QLabel("X-Axis: Channel " + str(self.xAxisPlot))
        self.measureSeriesLabel = qt.QLabel("Measure Series: 1")

        self.channel1Check = qt.QCheckBox("Channel 1", self)
        self.channel2Check = qt.QCheckBox("Channel 2", self)
        self.channel3Check = qt.QCheckBox("Channel 3", self)
        self.channel4Check = qt.QCheckBox("Channel 4", self)

        self.checkBoxes.append(self.channel1Check)
        self.checkBoxes.append(self.channel2Check)
        self.checkBoxes.append(self.channel3Check)
        self.checkBoxes.append(self.channel4Check)

        self.startMeasureButton = qt.QPushButton("Start Measurement")
        self.addMeasureSeriesButton = qt.QPushButton("Add Measure Serie")
        self.returnButton = qt.QPushButton("Return")

        channel1ValLabelRaw = qt.QLabel("-")
        channel1ValLabelProcessed = qt.QLabel("-")
        channel2ValLabelRaw = qt.QLabel("-")
        channel2ValLabelProcessed = qt.QLabel("-")

        channel3ValLabelRaw = qt.QLabel("-")
        channel3ValLabelProcessed = qt.QLabel("-")
        channel4ValLabelRaw = qt.QLabel("-")
        channel4ValLabelProcessed = qt.QLabel("-")

        arrowLabel1 = qt.QLabel("=>")
        arrowLabel2 = qt.QLabel("=>")
        arrowLabel3 = qt.QLabel("=>")
        arrowLabel4 = qt.QLabel("=>")

        arrowLabel1.setFixedWidth(50)
        arrowLabel2.setFixedWidth(50)
        arrowLabel3.setFixedWidth(50)
        arrowLabel4.setFixedWidth(50)

        self.channelData.append([channel1ValLabelRaw, channel1ValLabelProcessed])
        self.channelData.append([channel2ValLabelRaw, channel2ValLabelProcessed])
        self.channelData.append([channel3ValLabelRaw, channel3ValLabelProcessed])
        self.channelData.append([channel4ValLabelRaw, channel4ValLabelProcessed])

        layout.addWidget(self.channel1Check, 1, 0, 1, 3)
        layout.addWidget(channel1ValLabelRaw, 2, 0)
        layout.addWidget(arrowLabel1, 2, 1)
        layout.addWidget(channel1ValLabelProcessed, 2, 2)

        layout.addWidget(self.channel2Check, 3, 0, 1, 3)
        layout.addWidget(channel2ValLabelRaw, 4, 0)
        layout.addWidget(arrowLabel2, 4, 1)
        layout.addWidget(channel2ValLabelProcessed, 4, 2)

        layout.addWidget(self.channel3Check, 5, 0, 1, 3)
        layout.addWidget(channel3ValLabelRaw, 6, 0)
        layout.addWidget(arrowLabel3, 6, 1)
        layout.addWidget(channel3ValLabelProcessed, 6, 2)

        layout.addWidget(self.channel4Check, 7, 0, 1, 3)
        layout.addWidget(channel4ValLabelRaw, 8, 0)
        layout.addWidget(arrowLabel4, 8, 1)
        layout.addWidget(channel4ValLabelProcessed, 8, 2)

        layout.addWidget(self.returnButton, 13, 0, 1, 3)

        if self.functionCode == 1:
            layout.addWidget(xAxisPlotLabel, 0, 0, 1, 3)
            layout.addWidget(self.measureSeriesLabel, 10, 0, 1, 3)
            layout.addWidget(self.startMeasureButton, 11, 0, 1, 3)
            layout.addWidget(self.addMeasureSeriesButton, 12, 0, 1, 3)

        self.setLayout(layout)

