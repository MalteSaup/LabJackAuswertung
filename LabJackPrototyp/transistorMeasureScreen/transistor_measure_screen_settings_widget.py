import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore


class LabelHolder(qt.QWidget):
    def __init__(self, options, measurePorts):
        super().__init__()
        self.measurePointsValueLabel = None
        self.returnButton = None
        self.startMeasureButton = None
        self.addMeasurePointButton = None
        self.bValueLabel = None
        self.uEarlyValueLabel = None
        self.options = options
        self.measurePorts = measurePorts

        self.initUI()

    def initUI(self):
        layout = qt.QGridLayout()

        # Labels
        icLabel = qt.QLabel("IC: ")
        uceLabel = qt.QLabel("UCE: ")
        ubeLabel = qt.QLabel("UBE: ")
        ibLabel = qt.QLabel("IB: ")

        measurePointsLabel = qt.QLabel("Measure Points: ")

        icMeasurePortLabel = qt.QLabel(self.options[self.measurePorts[0] + 1])
        uceMeasurePortLabel = qt.QLabel(self.options[self.measurePorts[1] + 1])
        ubeMeasurePortLabel = qt.QLabel(self.options[self.measurePorts[2] + 1])
        ibMeasurePortLabel = qt.QLabel(self.options[self.measurePorts[3] + 1])

        self.measurePointsValueLabel = qt.QLabel("1")

        #Buttons
        self.startMeasureButton = qt.QPushButton("Start Measure")
        self.addMeasurePointButton = qt.QPushButton("Add Measure Point")
        self.returnButton = qt.QPushButton("Return")

        layout.addWidget(icLabel, 0, 0)
        layout.addWidget(ibLabel, 1, 0)
        layout.addWidget(uceLabel, 2, 0)
        layout.addWidget(ubeLabel, 3, 0)
        layout.addWidget(measurePointsLabel, 4, 0)
        layout.addWidget(self.startMeasureButton, 5, 0, 1, 2)
        layout.addWidget(self.addMeasurePointButton, 6, 0, 1, 2)
        layout.addWidget(self.returnButton, 7, 0, 1, 2)

        layout.addWidget(icMeasurePortLabel, 0, 1)
        layout.addWidget(ibMeasurePortLabel, 1, 1)
        layout.addWidget(uceMeasurePortLabel, 2, 1)
        layout.addWidget(ubeMeasurePortLabel, 3, 1)
        layout.addWidget(self.measurePointsValueLabel, 4, 1)

        self.setLayout(layout)
