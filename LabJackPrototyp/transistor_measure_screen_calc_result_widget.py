import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

class CalcResultWidget(qt.QWidget):
    def __init__(self, measurePoint, b, uearly, amount):
        super().__init__()

        self.measurePoint = measurePoint
        self.b = b
        self.uearly = uearly
        self.amount = amount

        self.initUI()

    def initUI(self):
        layout = qt.QVBoxLayout()

        measurePointLabel = qt.QLabel("Measure Point: " + str(self.measurePoint))
        amountLabel = qt.QLabel("Amount Measurements: " + str(self.amount))
        bLabel = qt.QLabel("B: " + str(self.b))
        uEarlyLabel = qt.QLabel("UEarly: " + str(self.uearly) + "V")

        layout.addWidget(measurePointLabel)
        layout.addWidget(amountLabel)
        layout.addWidget(bLabel)
        layout.addWidget(uEarlyLabel)

        self.setLayout(layout)