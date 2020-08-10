import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

class MainScreen(qt.QWidget):
    def __init__(self, supportClass):
        super().__init__()
        self.layout = None
        self.supportClass = supportClass


    def initUI(self):
        self.layout = LayoutCompiler(self.supportClass)
        self.supportClass.currentScreen = self
        self.setLayout(self.layout)
        self.show()

class ButtonHolder(qt.QVBoxLayout):
    def __init__(self, label, supportClass):
        super().__init__()
        self.layout = None
        self.comboBox = None
        self.label = label
        self.supportClass = supportClass
        self.options = [
            "Oszi",
            "Normal Messen",
            "Show Transistor",
            "Experiment 4"
        ]
        self.initUI()

    def initUI(self):
        self.options = [
            "Oszi",
            "Normal Messen",
            "Show Transistor",
            "Experiment 4"
        ]

        # DropDown
        self.comboBox = qt.QComboBox()
        for option in self.options:
            self.comboBox.addItem(option)


        #print(type(super))
        connectButton = qt.QPushButton("Connect to Device")
        self.startMeasureButton = qt.QPushButton("Start Measurement")

        exitButton = qt.QPushButton("Exit")

        self.addWidget(self.startMeasureButton)
        self.addWidget(connectButton)
        self.addWidget(self.comboBox)
        self.addWidget(exitButton)


        connectButton.pressed.connect(self.connectDevice)
        self.startMeasureButton.clicked.connect(self.supportClass.startMeasure)
        self.supportClass.startMeasureButton = self.startMeasureButton
        exitButton.clicked.connect(qtcore.QCoreApplication.instance().quit)


        if not self.supportClass.runningFlag:
            self.startMeasureButton.setEnabled(False)


    def changeStatusBar(self, string):

        self.supportClass.statusBar.showMessage(string)
        self.startMeasureButton.setEnabled(True)

    def connectDevice(self):
        if(self.supportClass.connectDevice()):
            self.changeStatusBar("Connection State: Connected")
        else:
            self.changeStatusBar("Connection State: Connection Error")

class LayoutCompiler(qt.QHBoxLayout):
    def __init__(self, supportClass):
        super().__init__()
        self.supportClass = supportClass
        self.leftLayout = None
        self.initUI()

    def initUI(self):
        label = qt.QLabel()
        picture = qtgui.QPixmap("Dioden_Messschaltung.png")
        picture = picture.scaled(780, 440)
        label.setPixmap(picture)
        self.leftLayout = ButtonHolder(label, self.supportClass)

        self.addLayout(self.leftLayout)
        self.addWidget(label)



