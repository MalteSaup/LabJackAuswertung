import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore


class Settings(qt.QWidget):
    def __init__(self, functionCode):
        super().__init__()
        self.leftCheck = None
        self.rightCheck = None
        self.startMeasureButton = None
        self.exitButton = None
        self.comboBox = None
        self.functionCode = functionCode
        self.initUI()

    def initUI(self):

        hlayout = qt.QHBoxLayout()
        vlayout = qt.QVBoxLayout()

        self.leftCheck = CheckBoxesLeft()
        self.rightCheck = CheckBoxesRight()

        hlayout.addWidget(self.leftCheck)
        hlayout.addWidget(self.rightCheck)

        layoutHolderCheckboxes = qt.QWidget()
        layoutHolderCheckboxes.setLayout(hlayout)

        if self.functionCode == 1:
            label = qt.QLabel("Choose Measure Channel for X-Axes: ")
            options = [
                "Channel 1",
                "Channel 2",
                "Channel 3",
                "Channel 4"
            ]
            self.comboBox = qt.QComboBox()
            for option in options:
                self.comboBox.addItem(option)
            self.startMeasureButton = qt.QPushButton("Start Measurement")

            vlayout.addWidget(label)
            vlayout.addWidget(self.comboBox)
            vlayout.addWidget(layoutHolderCheckboxes)
            vlayout.addWidget(self.startMeasureButton, 200, qtcore.Qt.AlignBottom)

            self.leftCheck.checkBoxes[1].setCheckState(False)
            self.leftCheck.checkBoxes[1].setEnabled(False)

        else:
            vlayout.addWidget(layoutHolderCheckboxes)

        self.exitButton = qt.QPushButton("Return")
        vlayout.addWidget(self.exitButton)

        self.setLayout(vlayout)


class CheckBoxesLeft(qt.QWidget):
    def __init__(self):
        super().__init__()
        self.checkBoxes = []

        self.initUI()

    def initUI(self):
        layout = qt.QVBoxLayout()

        markerCheck = qt.QCheckBox("Marker", self)
        ai0Check = qt.QCheckBox("Channel 1", self)
        ai0Check.setChecked(True)
        ai2Check = qt.QCheckBox("Channel 2", self)

        self.checkBoxes.append(markerCheck)
        self.checkBoxes.append(ai0Check)
        self.checkBoxes.append(ai2Check)

        layout.addWidget(markerCheck)
        layout.addWidget(ai0Check)
        layout.addWidget(ai2Check)

        self.setLayout(layout)


class CheckBoxesRight(qt.QWidget):
    def __init__(self):
        super().__init__()
        self.checkBoxes = []

        self.initUI()

    def initUI(self):
        layout = qt.QVBoxLayout()

        lineCheck = qt.QCheckBox("Line", self)
        lineCheck.setChecked(True)
        ai1Check = qt.QCheckBox("AIN1", self)
        ai3Check = qt.QCheckBox("AIN3", self)

        self.checkBoxes.append(lineCheck)
        self.checkBoxes.append(ai1Check)
        self.checkBoxes.append(ai3Check)

        layout.addWidget(lineCheck)
        layout.addWidget(ai1Check)
        layout.addWidget(ai3Check)

        self.setLayout(layout)
