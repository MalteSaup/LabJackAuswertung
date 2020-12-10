import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qtcore

from helper import LabJackU6Settings, MeasureMethod


class SettingsComponentCreator:
    def __init__(self, minWidthWidget=220, padding=10):
        super().__init__()
        self.minWidthWidget = minWidthWidget
        self.padding = padding

        self.startMeasureButton = None
        self.addMeasureSeriesButton = None
        self.reconnectButton = None
        self.returnButton = None

        self.measureSeriesLabel = None

        self.checkBoxes = []
        self.channelData = []

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

    def createSettingsWidget(self, measureMethod, idPort=0, measurePorts=[], options=[]):

        self.measureSeriesLabel = qt.QLabel("Measure Series: 1")
        self.startMeasureButton = qt.QPushButton("Start Measurement")
        self.addMeasureSeriesButton = qt.QPushButton("Add Measure Serie")
        self.reconnectButton = qt.QPushButton("Reconnect")
        self.returnButton = qt.QPushButton("Return")

        widget = qt.QWidget()
        layout = qt.QGridLayout()

        if measureMethod == MeasureMethod.DIODE:
            udPort = 1 - idPort

            self.channelData.append([qt.QLabel("-"), qt.QLabel("-")])
            self.channelData.append([qt.QLabel("-"), qt.QLabel("-")])
            layout.addWidget(
                self.createGroupBox("Id über Diode:",
                                    "Id * R2/[V]",
                                    "Id/[mA]",
                                    self.channelData[idPort]))
            layout.addWidget(
                self.createGroupBox("Ud",
                                    "Ud/[V]",
                                    "Ud/[V]",
                                    self.channelData[udPort]))

        elif measureMethod == MeasureMethod.OSZILATOR:
            for i in range(LabJackU6Settings.USABLEPORTCOUNT.value):
                self.channelData.append([qt.QLabel("-"), qt.QLabel("-")])
                self.checkBoxes.append(qt.QCheckBox("Active"))
                layout.addWidget(self.createGroupBox("Channel " + str(i), "U/[V]", "U/[V]",
                                                     self.channelData[-1],
                                                     self.checkBoxes[-1]))

        elif measureMethod == MeasureMethod.TRANSISTOR:
            for i in range(LabJackU6Settings.USABLEPORTCOUNT.value):
                self.channelData.append([qt.QLabel("-"), qt.QLabel("-")])
                if measurePorts.index(i) == 0:
                    groupBox = self.createGroupBox(options[i + 1], "IC * R2/[V]",
                                                   "IC/[mA]", self.channelData[-1])
                elif measurePorts.index(i) == 1:
                    groupBox = self.createGroupBox(options[i + 1], "UCE/[V]",
                                                   "UCE/[V]", self.channelData[-1])
                elif measurePorts.index(i) == 2:
                    groupBox = self.createGroupBox(options[i + 1], "UBE/[V]",
                                                   "UBE/[V]", self.channelData[-1])
                else:
                    groupBox = self.createGroupBox(options[i + 1], "IB * R1/[V]",
                                                   "IB/[μA]", self.channelData[-1])
                layout.addWidget(groupBox, i, 0, 1, 2)

        layout.addWidget(self.measureSeriesLabel, LabJackU6Settings.USABLEPORTCOUNT.value + 1, 0, 1, 2)
        layout.addWidget(self.startMeasureButton, LabJackU6Settings.USABLEPORTCOUNT.value + 2, 0, 1, 2)
        layout.addWidget(self.addMeasureSeriesButton, LabJackU6Settings.USABLEPORTCOUNT.value + 3, 0, 1, 2)

        self.reconnectButton.setVisible(False)

        layout.addWidget(self.reconnectButton, LabJackU6Settings.USABLEPORTCOUNT.value + 4, 0, 1, 2)
        layout.addWidget(self.returnButton, LabJackU6Settings.USABLEPORTCOUNT.value + 5, 0, 1, 2)

        widget.setLayout(layout)

        return widget
