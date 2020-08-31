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

        # Labels
        icLabel = qt.QLabel("IC * R2: ")

        uceLabel = qt.QLabel("UCE: ")
        ubeLabel = qt.QLabel("UBE: ")
        ibLabel = qt.QLabel("IB * R1 ")

        arrowLabel1 = qt.QLabel("=>")
        arrowLabel2 = qt.QLabel("=>")
        arrowLabel3 = qt.QLabel("=>")
        arrowLabel4 = qt.QLabel("=>")

        arrowLabel1.setFixedWidth(50)
        arrowLabel2.setFixedWidth(50)
        arrowLabel3.setFixedWidth(50)
        arrowLabel4.setFixedWidth(50)

        measureSeriesLabel = qt.QLabel("Measure Series: ")

        icMeasurePortLabel = qt.QLabel(self.options[self.measurePorts[0] + 1])
        uceMeasurePortLabel = qt.QLabel(self.options[self.measurePorts[1] + 1])
        ubeMeasurePortLabel = qt.QLabel(self.options[self.measurePorts[2] + 1])
        ibMeasurePortLabel = qt.QLabel(self.options[self.measurePorts[3] + 1])

        self.measureSeriesValueLabel = qt.QLabel("1")

        self.icValLabelRaw = qt.QLabel("0")
        self.icValLabelProcessed = qt.QLabel("0")
        self.ibValLabelRaw = qt.QLabel("0")
        self.ibValLabelProcessed = qt.QLabel("0")

        self.uceValLabelRaw = qt.QLabel("0")
        self.uceValLabelProcessed = qt.QLabel("0")
        self.ubeValLabelRaw = qt.QLabel("0")
        self.ubeValLabelProcessed = qt.QLabel("0")

        #Buttons
        self.startMeasureButton = qt.QPushButton("Start Measure")
        self.addMeasureSeriesButton = qt.QPushButton("Add Measure Serie")
        self.returnButton = qt.QPushButton("Return")

        layout.addWidget(icLabel, 0, 0)
        layout.addWidget(ibLabel, 2, 0)
        layout.addWidget(uceLabel, 4, 0)
        layout.addWidget(ubeLabel, 6, 0)
        layout.addWidget(measureSeriesLabel, 8, 0, 1, 2)
        layout.addWidget(self.startMeasureButton, 9, 0, 1, 3)
        layout.addWidget(self.addMeasureSeriesButton, 10, 0, 1, 3)
        layout.addWidget(self.returnButton, 11, 0, 1, 3)

        layout.addWidget(self.icValLabelRaw, 1, 0)
        layout.addWidget(self.icValLabelProcessed, 1, 2)
        layout.addWidget(self.ibValLabelRaw, 3, 0)
        layout.addWidget(self.ibValLabelProcessed, 3, 2)

        layout.addWidget(self.uceValLabelRaw, 5, 0)
        layout.addWidget(self.uceValLabelProcessed, 5, 2)
        layout.addWidget(self.ubeValLabelRaw, 7, 0)
        layout.addWidget(self.ubeValLabelProcessed, 7, 2)

        layout.addWidget(arrowLabel1, 1, 1, 1, 1, qtcore.Qt.AlignHCenter)
        layout.addWidget(arrowLabel2, 3, 1, 1, 1, qtcore.Qt.AlignHCenter)
        layout.addWidget(arrowLabel3, 5, 1, 1, 1, qtcore.Qt.AlignHCenter)
        layout.addWidget(arrowLabel4, 7, 1, 1, 1, qtcore.Qt.AlignHCenter)

        layout.addWidget(icMeasurePortLabel, 0, 2)
        layout.addWidget(ibMeasurePortLabel, 2, 2)
        layout.addWidget(uceMeasurePortLabel, 4, 2)
        layout.addWidget(ubeMeasurePortLabel, 6, 2)
        layout.addWidget(self.measureSeriesValueLabel, 8, 2)

        self.setLayout(layout)