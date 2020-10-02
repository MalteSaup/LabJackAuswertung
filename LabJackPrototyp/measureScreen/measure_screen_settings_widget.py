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

        xAxisPlotLabel = qt.QLabel("X-Axis: Channel " + str(self.xAxisPlot + 1))
        self.measureSeriesLabel = qt.QLabel("Measure Series: 1")

        channel1Check = qt.QCheckBox("Active")
        channel2Check = qt.QCheckBox("Active")
        channel3Check = qt.QCheckBox("Active")
        channel4Check = qt.QCheckBox("Active")

        self.checkBoxes.append(channel1Check)
        self.checkBoxes.append(channel2Check)
        self.checkBoxes.append(channel3Check)
        self.checkBoxes.append(channel4Check)

        self.startMeasureButton = qt.QPushButton("Start Measurement")
        self.addMeasureSeriesButton = qt.QPushButton("Add Measure Serie")
        self.returnButton = qt.QPushButton("Return")

        icValLabelRaw = qt.QLabel("-")
        icValLabelProcessed = qt.QLabel("-")
        ibValLabelRaw = qt.QLabel("-")
        ibValLabelProcessed = qt.QLabel("-")

        uceValLabelRaw = qt.QLabel("-")
        uceValLabelProcessed = qt.QLabel("-")
        ubeValLabelRaw = qt.QLabel("-")
        ubeValLabelProcessed = qt.QLabel("-")

        self.channelData.append([icValLabelRaw, icValLabelProcessed])
        self.channelData.append([uceValLabelRaw, uceValLabelProcessed])
        self.channelData.append([ubeValLabelRaw, ubeValLabelProcessed])
        self.channelData.append([ibValLabelRaw, ibValLabelProcessed])


        icGroupBox = self.createGroupBox("Channel 1", "IC", "IC * R2", icValLabelRaw, icValLabelProcessed, channel1Check)
        uceGroupBox = self.createGroupBox("Channel 1", "UCE", "UCE", uceValLabelRaw, uceValLabelProcessed, channel2Check)
        ubeGroupBox = self.createGroupBox("Channel 1", "UBE", "UBE", ubeValLabelRaw, ubeValLabelProcessed, channel3Check)
        ibGroupBox = self.createGroupBox("Channel 1", "IB", "IB * R1", ibValLabelRaw, ibValLabelProcessed, channel4Check)

        layout.addWidget(icGroupBox, 1, 0, 1, 2)
        layout.addWidget(uceGroupBox, 2, 0, 1, 2)
        layout.addWidget(ubeGroupBox, 3, 0, 1, 2)
        layout.addWidget(ibGroupBox, 4, 0, 1, 2)


        layout.addWidget(self.returnButton, 8, 0, 1, 2)

        if self.functionCode == 1:
            layout.addWidget(xAxisPlotLabel, 0, 0, 1, 2)
            layout.addWidget(self.measureSeriesLabel, 5, 0, 1, 2)
            layout.addWidget(self.startMeasureButton, 6, 0, 1, 2)
            layout.addWidget(self.addMeasureSeriesButton, 7, 0, 1, 2)

        self.setLayout(layout)

    def createGroupBox(self, groupName, descriptionLeftSide, descriptionRightSide, rawLabel, processedLabel, checkbox=None):
        groupBox = qt.QGroupBox(groupName)
        arrowLabel = qt.QLabel("=>")
        descriptionLeftSideLabel = qt.QLabel(descriptionLeftSide)
        descriptionRightSideLabel = qt.QLabel(descriptionRightSide)
        layout = qt.QGridLayout()

        if checkbox is not None:
            layout.addWidget(checkbox, 0, 0, 1, 2, qtcore.Qt.AlignLeft)

        layout.addWidget(descriptionLeftSideLabel, 1, 0, 1, 1, qtcore.Qt.AlignLeft)
        layout.addWidget(descriptionRightSideLabel, 1, 2, 1, 1, qtcore.Qt.AlignRight)
        layout.addWidget(rawLabel, 2, 0, 1, 1, qtcore.Qt.AlignLeft)
        layout.addWidget(processedLabel, 2, 2, 1, 1, qtcore.Qt.AlignRight)
        layout.addWidget(arrowLabel, 2, 1, 1, 1, qtcore.Qt.AlignHCenter)

        layout.setHorizontalSpacing(0)

        groupBox.setLayout(layout)

        return groupBox