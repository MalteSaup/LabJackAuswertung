import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

class MainScreen(qt.QWidget):
    def __init__(self, supportClass):
        super().__init__()
        self.comboBox = None
        self.supportClass = supportClass
        self.startMeasureButton = None

        self.options = [
            "Voltage Measurement",
            "Diode Measurement",
            "Transitor Measurement"
        ]


    def initUI(self):
        layout = qt.QHBoxLayout()
        self.supportClass.currentScreen = self

        pictureLabel = qt.QLabel()
        picture = qtgui.QPixmap("Dioden_Messschaltung.png")
        picture = picture.scaled(780, 440)
        pictureLabel.setPixmap(picture)

        buttonLayout = qt.QVBoxLayout()

        # DropDown
        self.comboBox = qt.QComboBox()
        for option in self.options:
            self.comboBox.addItem(option)

        connectButton = qt.QPushButton("Connect to Device")
        self.startMeasureButton = qt.QPushButton("Go to Measurement")

        exitButton = qt.QPushButton("Exit")

        buttonLayout.addWidget(self.startMeasureButton)
        buttonLayout.addWidget(connectButton)
        buttonLayout.addWidget(self.comboBox)
        buttonLayout.addWidget(exitButton)

        connectButton.pressed.connect(self.connectDevice)
        self.startMeasureButton.clicked.connect(self.supportClass.startMeasure)
        exitButton.clicked.connect(qtcore.QCoreApplication.instance().quit)

        if not self.supportClass.runningFlag:
            self.startMeasureButton.setEnabled(False)

        layout.addLayout(buttonLayout)
        layout.addWidget(pictureLabel)

        self.setLayout(layout)
        self.show()

    def changeStatusBar(self, string):
        self.supportClass.statusBar.showMessage(string)

    def connectDevice(self):
        if(self.supportClass.connectDevice()):
            self.startMeasureButton.setEnabled(True)
            self.changeStatusBar("Connection State: Connected")
        else:
            self.changeStatusBar("Connection State: Connection Error")
