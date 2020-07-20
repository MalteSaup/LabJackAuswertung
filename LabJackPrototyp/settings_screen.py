import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

class SettingsScreen(qt.QWidget):
    def __init__(self, supportClass):
        super().__init__()

        self.supportClass = supportClass
        self.centralWidget = None

    def initUI(self):
        self.centralWidget = LayoutCombine(self.supportClass.options)

        self.initInputsAndComboBoxes()

        self.centralWidget.rightWidget.submitButton.pressed.connect(self.onSubmitClick)
        self.centralWidget.leftWidget.returnButton.pressed.connect(self.supportClass.returnToMainScreen)

    def initInputsAndComboBoxes(self):
        measureSettings = self.supportClass.measureSettings
        inputWidget = self.centralWidget.rightWidget.inputWidgets
        comboBoxes = self.centralWidget.leftWidget.measureComboBoxes.comboBoxes

        inputWidget.inputR1.setText(str(measureSettings.r1))
        inputWidget.inputR2.setText(str(measureSettings.r2))
        inputWidget.inputUbeMin.setText(str(measureSettings.ubeMin))
        inputWidget.inputUbeMax.setText(str(measureSettings.ubeMax))
        inputWidget.inputUceMin.setText(str(measureSettings.uceMin))
        inputWidget.inputUceMax.setText(str(measureSettings.uceMax))

        comboBoxes[0].setCurrentIndex(measureSettings.measurePorts[3]+1)
        comboBoxes[1].setCurrentIndex(measureSettings.measurePorts[0]+1)
        comboBoxes[2].setCurrentIndex(measureSettings.measurePorts[1]+1)
        comboBoxes[3].setCurrentIndex(measureSettings.measurePorts[2]+1)


    def onSubmitClick(self):
        inputWidget = self.centralWidget.rightWidget.inputWidgets
        measureComboBoxes = self.centralWidget.leftWidget.measureComboBoxes.comboBoxes
        measureSetting = self.supportClass.measureSettings

        measurePorts = [
            measureComboBoxes[1].currentIndex() - 1,
            measureComboBoxes[2].currentIndex() - 1,
            measureComboBoxes[3].currentIndex() - 1,
            measureComboBoxes[0].currentIndex() - 1
        ]

        measureSetting.r1 = int(inputWidget.inputR1.text())
        measureSetting.r2 = int(inputWidget.inputR2.text())
        measureSetting.ubeMin = float(inputWidget.inputUbeMin.text())
        measureSetting.ubeMax = float(inputWidget.inputUbeMax.text())
        measureSetting.uceMin = float(inputWidget.inputUceMin.text())
        measureSetting.uceMax = float(inputWidget.inputUceMax.text())
        measureSetting.measurePorts = measurePorts

        self.supportClass.startTransistorScreen()

class LayoutCombine(qt.QWidget):
    def __init__(self, options):
        super().__init__()

        self.options = options

        self.leftWidget = None
        self.rightWidget = None

        self.showUI()

    def showUI(self):
        layout = qt.QHBoxLayout()

        self.leftWidget = LeftLayoutCombine(self.options)
        self.rightWidget = RightLayoutCombine()

        layout.addWidget(self.leftWidget)
        layout.addWidget(self.rightWidget)

        self.setLayout(layout)

        self.show()

class LeftLayoutCombine(qt.QWidget):
    def __init__(self, options):
        super().__init__()

        self.options = options
        self.measureComboBoxes = None
        self.returnButton = None
        self.showUI()

    def showUI(self):
        layout = qt.QVBoxLayout()

        self.measureComboBoxes = MeasurePortsComboBoxes(self.options)
        self.returnButton = qt.QPushButton("Return")

        layout.addWidget(self.measureComboBoxes)
        layout.addWidget(self.returnButton)
        layout.setAlignment(self.returnButton, qtcore.Qt.AlignBottom)

        self.setLayout(layout)

class MeasurePortsComboBoxes(qt.QWidget):
    def __init__(self, options):
        super().__init__()

        self.comboBoxes = []
        self.options = options

        self.showUI()

    def showUI(self):
        layout = qt.QVBoxLayout()


        # Creation Combo Boxes
        cb_ib = qt.QComboBox()
        cb_ic = qt.QComboBox()
        cb_uce = qt.QComboBox()
        cb_ube = qt.QComboBox()

        for option in self.options:
            cb_ib.addItem(option)
            cb_ic.addItem(option)
            cb_uce.addItem(option)
            cb_ube.addItem(option)

        self.comboBoxes.append(cb_ib)
        self.comboBoxes.append(cb_ic)
        self.comboBoxes.append(cb_uce)
        self.comboBoxes.append(cb_ube)

        # Layouting Combo Boxes with Widgets and Layouts
        w_ib = qt.QWidget()
        w_ic = qt.QWidget()
        w_uce = qt.QWidget()
        w_ube = qt.QWidget()

        layout_ib = qt.QHBoxLayout()
        layout_ic = qt.QHBoxLayout()
        layout_uce = qt.QHBoxLayout()
        layout_ube = qt.QHBoxLayout()

        layout_ib.addWidget(qt.QLabel("IB"))
        layout_ic.addWidget(qt.QLabel("IC"))
        layout_uce.addWidget(qt.QLabel("UCE"))
        layout_ube.addWidget(qt.QLabel("UCB"))

        layout_ib.addWidget(cb_ib)
        layout_ic.addWidget(cb_ic)
        layout_uce.addWidget(cb_uce)
        layout_ube.addWidget(cb_ube)

        w_ib.setLayout(layout_ib)
        w_ic.setLayout(layout_ic)
        w_uce.setLayout(layout_uce)
        w_ube.setLayout(layout_ube)

        # Adding Widgets
        layout.addWidget(w_ib)
        layout.addWidget(w_ic)
        layout.addWidget(w_uce)
        layout.addWidget(w_ube)

        self.setLayout(layout)

class RightLayoutCombine(qt.QWidget):
    def __init__(self):
        super().__init__()

        self.inputWidgets = None
        self.submitButton = None
        self.showUI()

    def showUI(self):
        layout = qt.QVBoxLayout()
        self.inputWidgets = DataInputWidget()
        self.submitButton = qt.QPushButton("Submit")



        layout.addWidget(self.inputWidgets)
        layout.addWidget(self.submitButton)
        layout.setAlignment(self.submitButton, qtcore.Qt.AlignBottom)

        self.setLayout(layout)

class DataInputWidget(qt.QWidget):
    def __init__(self):
        super().__init__()

        self.inputR1 = None
        self.inputR2 = None
        self.inputUbeMin = None
        self.inputUbeMax = None
        self.inputUceMin = None
        self.inputUceMax = None

        self.showUI()

    def showUI(self):
        layout = qt.QGridLayout()

        self.inputR1 = qt.QLineEdit()
        self.inputR1.setValidator(qtgui.QIntValidator())
        #self.inputR1.setText("200")

        self.inputR2 = qt.QLineEdit()
        self.inputR2.setValidator(qtgui.QIntValidator())
        #self.inputR2.setText("100000")

        self.inputUbeMin = qt.QLineEdit()
        self.inputUbeMin.setValidator(qtgui.QDoubleValidator())
        #self.inputUbeMin.setText("0")

        self.inputUbeMax = qt.QLineEdit()
        self.inputUbeMax.setValidator(qtgui.QDoubleValidator())
        #self.inputUbeMax.setText("12")

        self.inputUceMin = qt.QLineEdit()
        self.inputUceMin.setValidator(qtgui.QDoubleValidator())
        #self.inputUceMin.setText("0")

        self.inputUceMax = qt.QLineEdit()
        self.inputUceMax.setValidator(qtgui.QDoubleValidator())
        #self.inputUceMax.setText("10")

        r1Label = qt.QLabel("R1 (Ω): ")
        r2Label = qt.QLabel("R2 (Ω): ")

        ubeMinLabel = qt.QLabel("Zu erwartenes Ube Min (V): ")
        ubeMaxLabel = qt.QLabel("Zu erwartenes Ube Max (V): ")
        uceMinLabel = qt.QLabel("Zu erwartenes Uce Min (V): ")
        uceMaxLabel = qt.QLabel("Zu erwartenes Uce Max (V): ")

        layout.addWidget(r1Label, 0, 0)
        layout.addWidget(r2Label, 1, 0)
        layout.addWidget(ubeMinLabel, 2, 0)
        layout.addWidget(ubeMaxLabel, 3, 0)
        layout.addWidget(uceMinLabel, 4, 0)
        layout.addWidget(uceMaxLabel, 5, 0)

        layout.addWidget(self.inputR1, 0, 1)
        layout.addWidget(self.inputR2, 1, 1)
        layout.addWidget(self.inputUbeMin, 2, 1)
        layout.addWidget(self.inputUbeMax, 3, 1)
        layout.addWidget(self.inputUceMin, 4, 1)
        layout.addWidget(self.inputUceMax, 5, 1)

        self.setLayout(layout)