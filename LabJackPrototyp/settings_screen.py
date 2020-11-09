import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore
from helper import MeasureMethod, LabJackU6

class SettingsScreenWindow(qt.QWidget):
    def __init__(self, supportClass, parent=None):
        super().__init__(parent)
        self.supportClass = supportClass
        self.centralWidget = None
        self.measureMethod = supportClass.measureSettings.measureMethod

        self.showUI()

    def showUI(self):
        self.centralWidget = SettingsScreen(self.supportClass)

class SettingsScreen(qt.QWidget):
    def __init__(self, supportClass):
        super().__init__()

        self.supportClass = supportClass
        self.centralWidget = None
        self.measureMethod = supportClass.measureSettings.measureMethod

        self.comboBoxes = []
        self.transistorLabelText = ["IB", "IC", "UCE", "UBE"]

        self.initUI()

        self.inputR1 = None
        self.inputR2 = None

        self.inputVal1Max = None
        self.inputVal2Max = None

        self.submitButton = None
        self.returnButton = None


    def initUI(self):
        layoutComboBoxes = qt.QGridLayout()
        layoutInputFields = qt.QGridLayout()

        self.inputR1 = qt.QLineEdit()
        self.inputR1.setValidator(qtgui.QIntValidator())

        self.inputR2 = qt.QLineEdit()
        self.inputR2.setValidator(qtgui.QIntValidator())

        self.inputVal1Max = qt.QLineEdit()
        self.inputVal1Max.setValidator(qtgui.QIntValidator())

        self.inputVal2Max = qt.QLineEdit()
        self.inputVal2Max.setValidator(qtgui.QIntValidator())

        layoutInputFields.addWidget(qt.QLabel("R1 (Ω): "), 0, 0, 1, 1)
        layoutInputFields.addWidget(self.inputR1, 0, 1, 1, 1, qtcore.Qt.AlignRight)
        layoutInputFields.addWidget(qt.QLabel("R2 (Ω): "), 1, 0, 1, 1, qtcore.Qt.AlignLeft)
        layoutInputFields.addWidget(self.inputR2, 1, 1, 1, 1, qtcore.Qt.AlignRight)

        layoutInputFields.addWidget(self.inputVal1Max, 2, 1, 1, 1, qtcore.Qt.AlignRight)
        layoutInputFields.addWidget(self.inputVal2Max, 3, 1, 1, 1, qtcore.Qt.AlignRight)

        if self.supportClass.measureSettings.measureMethod == MeasureMethod.TRANSISTOR:
            for i in range(LabJackU6.USABLEPORTCOUNT.value):
                comboBox = qt.QComboBox()
                comboBox.setMinimumWidth(150)
                for option in self.supportClass.options:
                    comboBox.addItem(option)
                self.comboBoxes.append(comboBox)
                layoutComboBoxes.addWidget(qt.QLabel(self.transistorLabelText[i]), i, 0, 1, 1, qtcore.Qt.AlignLeft)
                layoutComboBoxes.addWidget(self.comboBoxes[-1], i, 1, 1, 1, qtcore.Qt.AlignRight)

            layoutInputFields.addWidget(qt.QLabel("Zu erwartenes Ube Max (V): "), 2, 0, 1, 1, qtcore.Qt.AlignLeft)
            layoutInputFields.addWidget(qt.QLabel("Zu erwartenes Uce Max (V): "), 3, 0, 1, 1, qtcore.Qt.AlignLeft)

        elif self.supportClass.measureSettings.measureMethod == MeasureMethod.DIODE:
            comboBox = qt.QComboBox()
            for i in range(3):
                comboBox.addItem(self.supportClass.options[i])
            self.comboBoxes.append(comboBox)
            layoutComboBoxes.addWidget(qt.QLabel("Id Measure Channel"), 0, 0, 1, 1, qtcore.Qt.AlignLeft)
            layoutComboBoxes.addWidget(self.comboBoxes[0], 0, 1, 1, qtcore.Qt.AlignLeft)

            layoutInputFields.addWidget(qt.QLabel("Zu erwartendes Ud Max [V]: "), 2, 0, 1, 1, qtcore.Qt.AlignLeft)
            layoutInputFields.addWidget(qt.QLabel("Zu erwartendes Id Max [mA]: "), 3, 0, 1, 1, qtcore.Qt.AlignLeft)

        self.submitButton = qt.QPushButton("Submit")
        self.returnButton = qt.QPushButton("Return")

        layoutInputFields.addWidget(self.submitButton, LabJackU6.USABLEPORTCOUNT.value + 2, 0, 1, 2, qtcore.Qt.AlignBottom)
        layoutComboBoxes.addWidget(self.returnButton, LabJackU6.USABLEPORTCOUNT.value + 2, 0, 1, 2, qtcore.Qt.AlignBottom)

        self.initInputsAndComboBoxes()

        self.submitButton.clicked.connect(self.onSubmitClick)
        self.returnButton.clicked.connect(self.close)

        layout = qt.QHBoxLayout()
        layout.addLayout(layoutComboBoxes)
        layout.addLayout(layoutInputFields)

        self.setLayout(layout)

        self.setWindowModality(qtcore.Qt.ApplicationModal)

        self.show()

        print(self.submitButton.geometry().width())

    def initInputsAndComboBoxes(self):
        measureSettings = self.supportClass.measureSettings

        if self.measureMethod == MeasureMethod.DIODE:
            self.inputVal1Max.setText(str(measureSettings.udMax))
            self.inputVal2Max.setText(str(measureSettings.idMax))
            print(measureSettings.toString())
            if measureSettings.r1 == 100000:
                self.inputR1.setText(str(10000))
            else:
                self.inputR1.setText(str(measureSettings.r1))
            if measureSettings.r2 == 200:
                self.inputR2.setText(str(1000))
            else:
                self.inputR2.setText(str(measureSettings.r2))

        if self.supportClass.measureSettings.measureMethod == MeasureMethod.TRANSISTOR:
            self.inputVal1Max.setText(str(measureSettings.ubeMax))
            self.inputVal2Max.setText(str(measureSettings.uceMax))
            self.inputR1.setText(str(measureSettings.r1))
            self.inputR2.setText(str(measureSettings.r2))


        if self.supportClass.measureSettings.measureMethod == MeasureMethod.TRANSISTOR:

            self.comboBoxes[0].setCurrentIndex(measureSettings.measurePorts[3]+1)
            self.comboBoxes[1].setCurrentIndex(measureSettings.measurePorts[0]+1)
            self.comboBoxes[2].setCurrentIndex(measureSettings.measurePorts[1]+1)
            self.comboBoxes[3].setCurrentIndex(measureSettings.measurePorts[2]+1)

        elif self.supportClass.measureSettings.measureMethod == MeasureMethod.DIODE:
            self.comboBoxes[0].setCurrentIndex(measureSettings.idPort + 1)

    def closeEvent(self, closeEvent):
        print(closeEvent)
        closeEvent.accept()

    def onSubmitClick(self):

        self.supportClass.measureSettings.r1 = int(self.inputR1.text())
        self.supportClass.measureSettings.r2 = int(self.inputR2.text())

        if self.supportClass.measureSettings.measureMethod == MeasureMethod.TRANSISTOR:
            measurePorts = [
                self.comboBoxes[1].currentIndex() - 1,
                self.comboBoxes[2].currentIndex() - 1,
                self.comboBoxes[3].currentIndex() - 1,
                self.comboBoxes[0].currentIndex() - 1
            ]

            self.supportClass.measureSettings.ubeMax = float(self.inputVal1Max.text())
            self.supportClass.measureSettings.uceMax = float(self.inputVal2Max.text())
            self.supportClass.measureSettings.measurePorts = measurePorts

            self.supportClass.startTransistorScreen()

        elif self.supportClass.measureSettings.measureMethod == MeasureMethod.DIODE:
            self.supportClass.measureSettings.udMax = int(self.inputVal1Max.text())
            self.supportClass.measureSettings.idMax = int(self.inputVal2Max.text())
            self.supportClass.measureSettings.idPort = self.comboBoxes[0].currentIndex() - 1

            self.supportClass.startMeasureScreen()

        self.close()

    def onReturnClick(self):
        self.close()

