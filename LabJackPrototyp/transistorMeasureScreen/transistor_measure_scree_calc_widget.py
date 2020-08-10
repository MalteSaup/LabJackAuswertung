import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore



class TransistorMeasureScreenCalcWidget(qt.QWidget):
        def __init__(self, amountOfMeasurePoints):
            super().__init__()

            self.amountOfMeasurePoints = amountOfMeasurePoints
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
            self.calcButton = qt.QPushButton("Calculate")
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
            for i in range(self.amountOfMeasurePoints):
                options.append("Measurepoint: " + str(i+1))
            return options






class CalcResultHolder(qt.QWidget):
    def __init__(self):
        super().__init__()

        self.layout = None

        self.initUI()

    def initUI(self):
        self.layout = qt.QVBoxLayout()

        self.setLayout(self.layout)
