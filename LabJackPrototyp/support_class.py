from measureScreen import measure_screen
import main_screen
from transistorMeasureScreen import transistor_measure_screen
from helper import MeasureMethod
import settings_screen
import measure_settings
from labjack_u6 import LabJackU6


class SupportClass:
    def __init__(self, statusBar, container, options, screenGeometry):

        self.device = None
        self.runningFlag = False
        self.statusBar = statusBar
        self.inMainScreen = True
        self.container = container
        self.measureSettings = measure_settings.MeasureSettings()

        self.inMeasureScreen = False

        self.currentScreen = None

        self.options = options

        self.screenGeometry = screenGeometry

        self.minWidthWidget = 220
        self.widgetAmount = 1
        self.padding = 15

        self.labJackU6 = None

    def connectDevice(self):
        self.labJackU6 = LabJackU6(self)
        return self.labJackU6.connectDevice()

    def startMeasure(self):
        self.measureSettings.measureMethod = MeasureMethod(self.currentScreen.comboBox.currentIndex())
        if self.measureSettings.measureMethod == MeasureMethod.OSZILATOR:
            self.inMeasureScreen = True
            ms = measure_screen.MeasureScreen(self)
            self.container.replaceCentralWidget(ms)
            ms.initUI()
            self.currentScreen = ms
            self.labJackU6.runningFlag = False
            self.inMainScreen = False
        else:
            settings_screen.SettingsScreenWindow(self, self.container)

    def startTransistorScreen(self):
        ms = transistor_measure_screen.TransistorScreen(self)
        self.container.replaceCentralWidget(ms)
        self.inMeasureScreen = True
        self.inMainScreen = False
        self.currentScreen = ms
        self.labJackU6.runningFlag = False
        ms.initUI()

    def startMeasureScreen(self):
        ms = measure_screen.MeasureScreen(self)
        self.container.replaceCentralWidget(ms)
        self.inMeasureScreen = True
        self.currentScreen = ms
        ms.initUI()

    def returnToMainScreen(self):
        ms = main_screen.MainScreen(self)
        self.container.replaceCentralWidget(ms)
        self.inMeasureScreen = False
        self.inMainScreen = True
        self.labJackU6.checkConnectionThread()
        try:
            ms.initUI()
        except Exception as e:
            print(e)
        self.currentScreen = ms

    def returnToSettingsScreen(self):
       self.returnToMainScreen()
       settings_screen.SettingsScreenWindow(self, self.container)
