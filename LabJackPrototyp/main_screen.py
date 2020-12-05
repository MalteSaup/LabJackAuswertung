import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

class MainScreen(qt.QWidget):
    def __init__(self, supportClass):
        super().__init__()
        self.comboBox = None
        self.supportClass = supportClass
        self.startMeasureButton = None
        self.picture = None
        self.pictureLabel = None
        self.options = [
            "Voltage Measurement",
            "Diode Measurement",
            "Transitor Measurement"
        ]


    def initUI(self):
        layout = qt.QHBoxLayout()
        self.supportClass.currentScreen = self

        self.pictureLabel = qt.QLabel()
        self.picture = qtgui.QPixmap("Dioden_Messschaltung.png")
        self.picture = self.picture.scaledToWidth(780)
        self.picture = self.picture.scaledToHeight(440)

        self.pictureLabel.setPixmap(self.picture)
        self.pictureLabel.setMinimumSize(1, 1)

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

        buttonWidget = qt.QWidget()
        buttonWidget.setLayout(buttonLayout)

        buttonWidget.setFixedWidth(self.supportClass.minWidthWidget)

        connectButton.pressed.connect(self.connectDevice)
        self.startMeasureButton.clicked.connect(self.supportClass.startMeasure)
        exitButton.clicked.connect(qtcore.QCoreApplication.instance().quit)

        if not self.supportClass.runningFlag:
            self.startMeasureButton.setEnabled(False)

        layout.addWidget(buttonWidget)
        layout.addWidget(self.pictureLabel)

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

    def resizeEvent(self, a0: qtgui.QResizeEvent):
        super().resizeEvent(a0)
        width = self.geometry().width() - self.supportClass.minWidthWidget
        height = self.geometry().height() - self.supportClass.container.statusBar().height()
        self.picture = qtgui.QPixmap("Dioden_Messschaltung.png")
        self.picture = self.picture.scaled(width, height)
        self.pictureLabel.setPixmap(self.picture)


