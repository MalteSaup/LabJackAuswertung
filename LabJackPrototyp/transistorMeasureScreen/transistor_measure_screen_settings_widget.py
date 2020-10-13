import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

import copy

class LabelHolder(qt.QWidget):
    def __init__(self, options, measurePorts):
        super().__init__()
        self.measureSeriesValueLabel = None
        self.returnButton = None
        self.startMeasureButton = None
        self.addMeasureSeriesButton = None
        self.bValueLabel = None
        self.uEarlyValueLabel = None
        self.options = options
        self.measurePorts = measurePorts

        self.icValLabelRaw = None
        self.icValLabelProcessed = None
        self.icValLabelRaw = None
        self.ibValLabelProcessed = None

        self.uceValLabelRaw = None
        self.uceValLabelProcessed = None
        self.ubeValLabelRaw = None
        self.ubeValLabelProcessed = None

        self.initUI()

    def initUI(self):
        layout = qt.QGridLayout()

        measureSeriesLabel = qt.QLabel("Measure Series: ")
        self.measureSeriesValueLabel = qt.QLabel("1")

        self.icValLabelRaw = qt.QLabel("-")
        self.icValLabelProcessed = qt.QLabel("-")
        self.ibValLabelRaw = qt.QLabel("-")
        self.ibValLabelProcessed = qt.QLabel("-")

        self.uceValLabelRaw = qt.QLabel("-")
        self.uceValLabelProcessed = qt.QLabel("-")
        self.ubeValLabelRaw = qt.QLabel("-")
        self.ubeValLabelProcessed = qt.QLabel("-")

        #groupName, descriptionLeftSide, descriptionRightSide, rawLabel, processedLabel

        icGroupBox = self.createGroupBox(self.options[self.measurePorts[0] + 1], "IC", "IC * R2", self.icValLabelRaw, self.icValLabelProcessed)
        uceGroupBox = self.createGroupBox(self.options[self.measurePorts[1] + 1], "UCE", "UCE", self.uceValLabelRaw, self.uceValLabelProcessed)
        ubeGroupBox = self.createGroupBox(self.options[self.measurePorts[2] + 1], "UBE", "UBE", self.ubeValLabelRaw, self.ubeValLabelProcessed)
        ibGroupBox = self.createGroupBox(self.options[self.measurePorts[3] + 1], "IB", "IB * R1", self.ibValLabelRaw, self.ibValLabelProcessed)

        #Buttons
        self.startMeasureButton = qt.QPushButton("Start Measure")
        self.addMeasureSeriesButton = qt.QPushButton("Add Measure Serie")
        self.returnButton = qt.QPushButton("Return")

        layout.addWidget(icGroupBox, 0, 0, 1, 2)
        layout.addWidget(uceGroupBox, 1, 0, 1, 2)
        layout.addWidget(ubeGroupBox, 2, 0, 1, 2)
        layout.addWidget(ibGroupBox, 3, 0, 1, 2)

        layout.addWidget(measureSeriesLabel, 4, 0)
        layout.addWidget(self.measureSeriesValueLabel, 4, 1)

        layout.addWidget(self.startMeasureButton, 5, 0, 1, 2)
        layout.addWidget(self.addMeasureSeriesButton, 6, 0, 1, 2)
        layout.addWidget(self.returnButton, 7, 0, 1, 2)


        self.setLayout(layout)

    def createGroupBox(self, groupName, descriptionLeftSide, descriptionRightSide, rawLabel, processedLabel):
        groupBox = qt.QGroupBox(groupName)
        arrowLabel = qt.QLabel("=>")
        descriptionLeftSideLabel = qt.QLabel(descriptionLeftSide)
        descriptionRightSideLabel = qt.QLabel(descriptionRightSide)
        layout = qt.QGridLayout()

        layout.addWidget(descriptionLeftSideLabel, 0, 0, 1, 1, qtcore.Qt.AlignLeft)
        layout.addWidget(descriptionRightSideLabel, 0, 2, 1, 1, qtcore.Qt.AlignRight)
        layout.addWidget(rawLabel, 1, 0, 1, 1, qtcore.Qt.AlignLeft)
        layout.addWidget(processedLabel, 1, 2, 1, 1, qtcore.Qt.AlignRight)
        layout.addWidget(arrowLabel, 1, 1, 1, 1, qtcore.Qt.AlignHCenter)

        sizePolicy = qt.QSizePolicy()
        sizePolicy.setHorizontalPolicy(qt.QSizePolicy.Minimum)

        groupBox.setSizePolicy(sizePolicy)

        groupBox.setLayout(layout)

        return groupBox
