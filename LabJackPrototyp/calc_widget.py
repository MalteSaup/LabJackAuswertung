import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qtcore
from helper import MeasureMethod


class CalcWidget(qt.QWidget):
        def __init__(self, amountOfMeasureSeries):
            super().__init__()

            self.amountOfMeasureSeries = amountOfMeasureSeries
            self.calcResultHolder = None
            self.calcButton = None
            self.chooseDropDown = None

            self.initUI()

        def initUI(self):
            layout = qt.QGridLayout()

            options = self.createOptions()

            scroll = qt.QScrollArea()
            scroll.setHorizontalScrollBarPolicy(qtcore.Qt.ScrollBarAlwaysOff)
            scroll.setWidgetResizable(True)

            self.calcResultHolder = CalcResultHolder()

            self.calcButton = qt.QPushButton("Estimate")
            self.chooseDropDown = qt.QComboBox()

            for option in options:
                self.chooseDropDown.addItem(option)

            scroll.setWidget(self.calcResultHolder)

            layout.addWidget(scroll, 0, 0, 8, 1)
            layout.addWidget(self.chooseDropDown, 9, 0)
            layout.addWidget(self.calcButton, 10, 0)

            self.setLayout(layout)

        def createOptions(self):
            options = []
            options.append("All")
            options.append("All Together")
            for i in range(self.amountOfMeasureSeries):
                options.append("Measure Serie: " + str(i+1))
            return options

class CalcResultHolder(qt.QWidget):
    def __init__(self):
        super().__init__()

        self.layout = None

        self.initUI()

    def initUI(self):
        self.layout = qt.QVBoxLayout()
        self.setLayout(self.layout)

class CalcResultWidget(qt.QGroupBox):
    def __init__(self, measureSeries, value1, value2, amount, measureMethode):
        super().__init__()
        if type(value1) == str:
            self.value1 = value1
        else:
            self.value1 = float('{:0.2e}'.format(value1))
        if type(value2) == str:
            self.value2 = value2
        else:
            self.value2 = float('{:0.2e}'.format(value2))
        self.measureSeries = measureSeries
        self.amount = amount
        self.measureMethode = measureMethode

        self.initUI()

    def initUI(self):
        layout = qt.QVBoxLayout()

        measureSeriesLabel = qt.QLabel("Measure Serie: " + str(self.measureSeries))
        amountLabel = qt.QLabel("Measurements: " + str(self.amount))

        value1Label, value2Label = None, None

        if (self.measureMethode == MeasureMethod.TRANSISTOR):
            if type(self.value1) == str:
                value1Label = qt.QLabel("UEarly: " + self.value1)
            else:
                value1Label = qt.QLabel("UEarly: " + str(self.value1) + "V")
            value2Label = qt.QLabel("B: " + str(self.value2))
        elif (self.measureMethode == MeasureMethod.DIODE):
            value1Label = qt.QLabel("Nd: " + str(self.value1))
            if type(self.value2) == str:
                value2Label = qt.QLabel("Is: " + self.value2)
            else:
                value2Label = qt.QLabel("Is: " + str(self.value2) + "A")

        layout.addWidget(measureSeriesLabel)
        layout.addWidget(amountLabel)
        layout.addWidget(value1Label)
        layout.addWidget(value2Label)

        sizePolicy = qt.QSizePolicy()
        sizePolicy.setHorizontalPolicy(qt.QSizePolicy.Minimum)

        self.setSizePolicy(sizePolicy)

        self.setLayout(layout)