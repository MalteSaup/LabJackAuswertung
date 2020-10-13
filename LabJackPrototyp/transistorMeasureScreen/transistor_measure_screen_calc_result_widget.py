import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

class CalcResultWidget(qt.QGroupBox):
    def __init__(self, measureSeries, b, uearly, amount):
        super().__init__()
        if type(uearly) == str:
            self.uearly = uearly
        else:
            self.uearly = round(uearly, 3)

        self.measureSeries = measureSeries
        self.b = round(b, 3)

        self.amount = amount

        self.initUI()

    def initUI(self):
        layout = qt.QVBoxLayout()

        measureSeriesLabel = qt.QLabel("Measure Serie: " + str(self.measureSeries))
        amountLabel = qt.QLabel("Amount Measurements: " + str(self.amount))
        bLabel = qt.QLabel("B: " + str(self.b))

        if type(self.uearly) == str:
            uEarlyLabel = qt.QLabel("UEarly: " + self.uearly)
        else:
            uEarlyLabel = qt.QLabel("UEarly: " + str(self.uearly) + "V")

        layout.addWidget(measureSeriesLabel)
        layout.addWidget(amountLabel)
        layout.addWidget(bLabel)
        layout.addWidget(uEarlyLabel)

        sizePolicy = qt.QSizePolicy()
        sizePolicy.setHorizontalPolicy(qt.QSizePolicy.Minimum)

        self.setSizePolicy(sizePolicy)

        self.setLayout(layout)