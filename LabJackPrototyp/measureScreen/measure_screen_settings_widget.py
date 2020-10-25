import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qtcore

from helper import MeasureMethod, LabJackU6


class Settings(qt.QWidget):
    def __init__(self, measureMethod, udPort=0, minWidthWidget=220, padding=10):
        super().__init__()

        self.startMeasureButton = None
        self.returnButton = None
        self.addMeasureSeriesButton = None

        self.measureSeriesLabel = None

        self.checkBoxes = []

        self.udPort = udPort
        self.measureMethod = measureMethod
        self.minWidthWidget = minWidthWidget
        self.padding = padding

        self.channelData = []

        self.channel1Check = None
        self.channel2Check = None
        self.channel3Check = None
        self.channel4Check = None

        self.initUI()

    def initUI(self):

        layout = qt.QGridLayout()

        self.measureSeriesLabel = qt.QLabel("Measure Series: 1")
        self.startMeasureButton = qt.QPushButton("Start Measurement")
        self.addMeasureSeriesButton = qt.QPushButton("Add Measure Serie")
        self.returnButton = qt.QPushButton("Return")

        self.checkBoxes = []

        for i in range(LabJackU6.USABLEPORTCOUNT.value):
            self.checkBoxes.append(qt.QCheckBox("Active"))
            self.channelData.append([qt.QLabel("-"), qt.QLabel("-")])

            if self.measureMethod == MeasureMethod.OSZILATOR:
                layout.addWidget(self.createGroupBox("Channel " + str(i), "U/[V]", "U/[V]", self.channelData[-1],
                                                      self.checkBoxes[-1]))

            if self.measureMethod == MeasureMethod.DIODE:
                if i == self.udPort:
                    layout.addWidget(self.createGroupBox("Ud", "Ud/[V]", "Ud/[V]", self.channelData[-1],
                                                          self.checkBoxes[-1]))
                else:
                    if self.udPort > i:
                        layout.addWidget(self.createGroupBox("Id Diode: " + str(i), "Id " + str(i+1) + " * R2/[V]", "Id " + str(i) + "/[mA]",
                                                              self.channelData[-1], self.checkBoxes[-1]))
                    else:
                        layout.addWidget(self.createGroupBox("Id Diode: " + str(i), "Id " + str(i) + " * R2/[V]", "Id " + str(i) + "/[mA]",
                                                              self.channelData[-1], self.checkBoxes[-1]))

        if self.measureMethod == MeasureMethod.DIODE:
            layout.addWidget(self.measureSeriesLabel, LabJackU6.USABLEPORTCOUNT.value + 1, 0, 1, 2)
            layout.addWidget(self.startMeasureButton, LabJackU6.USABLEPORTCOUNT.value + 2, 0, 1, 2)
            layout.addWidget(self.addMeasureSeriesButton, LabJackU6.USABLEPORTCOUNT.value + 3, 0, 1, 2)

        layout.addWidget(self.returnButton, LabJackU6.USABLEPORTCOUNT.value + 4, 0, 1, 2)

        self.setLayout(layout)

    def createGroupBox(self, groupName, descriptionLeftSide, descriptionRightSide, dataLabel,
                       checkbox=None):
        groupBox = qt.QGroupBox(groupName)
        arrowLabel = qt.QLabel("=>")
        descriptionLeftSideLabel = qt.QLabel(descriptionLeftSide)
        descriptionRightSideLabel = qt.QLabel(descriptionRightSide)
        layout = qt.QGridLayout()

        if checkbox is not None:
            layout.addWidget(checkbox, 0, 0, 1, 2, qtcore.Qt.AlignLeft)

        layout.addWidget(descriptionLeftSideLabel, 1, 0, 1, 1, qtcore.Qt.AlignLeft)
        layout.addWidget(descriptionRightSideLabel, 1, 2, 1, 1, qtcore.Qt.AlignRight)
        layout.addWidget(dataLabel[0], 2, 0, 1, 1, qtcore.Qt.AlignLeft)
        layout.addWidget(dataLabel[1], 2, 2, 1, 1, qtcore.Qt.AlignRight)
        layout.addWidget(arrowLabel, 2, 1, 1, 1, qtcore.Qt.AlignHCenter)

        layout.setHorizontalSpacing(0)

        sizePolicy = qt.QSizePolicy()
        sizePolicy.setHorizontalPolicy(qt.QSizePolicy.Minimum)

        groupBox.setSizePolicy(sizePolicy)

        groupBox.setLayout(layout)

        groupBox.setMinimumWidth(self.minWidthWidget - self.padding)

        return groupBox
