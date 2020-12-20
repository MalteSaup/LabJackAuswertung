import PyQt5.QtWidgets as qt
import PyQt5.QtCore as qtcore

from calculator import Calculator
from settings_component_creator import SettingsComponentCreator
from message_boxes import ReturnMessageBox
from helper import MeasureMethod
from calc_widget import CalcWidget
from export_screen import ExportScreen

class AbstractMeasureScreen(qt.QWidget):
    def __init__(self, supportClass):
        super().__init__()
        self.supportClass = supportClass
        self.measureSeries = []
        self.measureSeriesCount = 1
        self.plt = None
        self.calcWidget = None
        self.calcResults = []
        self.notStopped = False
        self.timer = None
        self.timerLabel = None
        self.sampleratePerSecond = 25
        self.samplerate = int(1000/self.sampleratePerSecond)
        self.milli = 1000
        self.mikro = 1e6
        self.layout = None
        self.widgetAmount = 1
        self.calculator = Calculator()
        self.settingsComponentCreator = SettingsComponentCreator(minWidthWidget=self.supportClass.minWidthWidget, padding=self.supportClass.padding*2)
        self.connectionLostBox = None

    def initReturnMessageBox(self):
        if self.plt.timer is not None:
            self.plt.timer.stop()
        self.messageBox = ReturnMessageBox()
        result = self.messageBox.exec_()
        if result == qt.QMessageBox.Ok:
            if self.timer is not None:
                self.timer.stop()

            if self.timerLabel is not None:
                self.timerLabel.stop()

            if self.plt.timer is not None:
                self.plt.timer.stop()
            if self.supportClass.measureSettings.measureMethod == MeasureMethod.OSZILATOR:
                self.returnToMainScreen()
            elif self.supportClass.measureSettings.measureMethod == MeasureMethod.DIODE or self.supportClass.measureSettings.measureMethod == MeasureMethod.TRANSISTOR:
                self.returnToSettingsScreen()
        else:
            pass

    def killThread(self):
        self.timer = None

    def resizeWidgets(self):
        width = self.geometry().width()
        height = self.geometry().height() - self.supportClass.container.statusBar().height()
        if self.plt is not None:
            self.plt.canvas.setGeometry(0, 0, (width - self.supportClass.minWidthWidget * self.widgetAmount) - self.supportClass.padding * 2,
                                        height)

    def stopMeasure(self):
        self.notStopped = False
        self.settingsComponentCreator.startMeasureButton.setText("Start Measure")

        if self.supportClass.measureSettings.measureMethod != MeasureMethod.OSZILATOR:
            self.calcWidget = CalcWidget(self.measureSeriesCount)
            self.calcWidget.chooseDropDown.currentIndexChanged.connect(self.comboChangeEvent)
            self.calcWidget.calcButton.pressed.connect(self.calcClick)
            self.calcWidget.setFixedWidth(self.supportClass.minWidthWidget)
            self.layout.addWidget(self.calcWidget, 0, 1)
            self.widgetAmount = 2

        if self.supportClass.measureSettings.measureMethod == MeasureMethod.TRANSISTOR or self.supportClass.measureSettings.measureMethod == MeasureMethod.DIODE:
            self.plt.updateLabel()

        qtcore.QTimer.singleShot(100, lambda: self.resizeWidgets())

    def startMeasure(self):
        if self.timer is None:
            self.startMeasureClock()
            self.connectionLostBox = None
        if self.calcWidget is not None:
            self.calcWidget.setParent(None)
            self.calcWidget = None
        self.widgetAmount = 1

        self.calcResults= []

        qtcore.QTimer.singleShot(100, lambda: self.resizeWidgets())

        self.plt.measureSeriesToDisplay = 0

        if self.supportClass.measureSettings.measureMethod == MeasureMethod.TRANSISTOR:
            self.plt.b = None

        self.settingsComponentCreator.startMeasureButton.setText("Stop Measure")
        self.notStopped = True

    def startMeasureClock(self):
        self.timer = qtcore.QTimer(self)
        self.timer.timeout.connect(lambda: self.updateDataset())
        self.timer.start(self.sampleratePerSecond)
        self.startUpdateLabel()

    def reconnect(self):
        if self.supportClass.connectDevice():
            self.settingsComponentCreator.reconnectButton.setVisible(False)
            if self.supportClass.measureSettings.measureMethod == MeasureMethod.OSZILATOR:
                self.startMeasure()

    def addMeasureSerie(self):
        if self.notStopped:
            self.measureSeriesCount += 1
            self.settingsComponentCreator.measureSeriesLabel.setText("Measure Series: " + str(self.measureSeriesCount))
            self.resizeWidgets()

    def startMeasureButtonPressed(self):
        if self.notStopped:
            self.stopMeasure()
        else:
            self.startMeasure()

    def doesResultExist(self, measureSeries):
        for result in self.calcResults:
            if measureSeries == result.measureSerie:
                return True
        return False

    def saveClick(self, wasStopped=False):
        if self.supportClass.measureSettings.measureMethod == MeasureMethod.TRANSISTOR or self.supportClass.measureSettings.measureMethod == MeasureMethod.DIODE:
            self.plt.updateLabel()
        if self.notStopped:
            wasStopped = True
            self.notStopped = False
        df, fig, columnNames = self.createExportData()
        if df is None and fig is None:
            self.saveClick(wasStopped)
        else:
            self.notStopped = wasStopped
            self.exportScreen = ExportScreen(df, fig, columnNames)
            self.exportScreen.show()

    def startUpdateLabel(self):
        self.timerLabel = qtcore.QTimer(self)
        self.timerLabel.timeout.connect(self.updateDataLabel)
        self.timerLabel.start(250)

    def returnToSettingsScreen(self):
        if self.timer is not None:
            self.timer.stop()

        if self.plt.timer is not None:
            self.plt.timer.stop()

        if self.timerLabel is not None:
            self.timerLabel.stop()

        self.plt.stopped = True
        self.supportClass.returnToSettingsScreen()