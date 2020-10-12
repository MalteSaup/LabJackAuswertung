import u6
import threading
import time

from measureScreen import measure_screen
import main_screen
from transistorMeasureScreen import transistor_measure_screen
import settings_screen
import measure_settings

class SupportClass:
    def __init__(self, statusBar, container, options, dpi):

        self.device = None
        self.runningFlag = False
        self.statusBar = statusBar
        self.inMainScreen = False
        self.startMeasureButton = None
        self.container = container
        self.measureSettings = measure_settings.MeasureSettings()

        self.measureType = 0

        self.inMeasureScreen = False

        self.currentScreen = None

        self.options = options

        self.minWidthWidget = 220
        self.widgetAmount = 1
        self.padding = 15


    def initSC(self):
        print()

    def connectDevice(self):
        try:
            if self.runningFlag:
                pass
            else:
                self.device = u6.U6()
                print(self.device)
                print(self.device.getAIN(0))
                self.device.getCalibrationData()
                self.checkConnectionThread()
            return True
        except:
            return False

    def checkConnectionThread(self):
        self.runningFlag = True
        self.t = threading.Thread(target=self.check)
        self.t.start()

    def check(self):
        while self.runningFlag:
            time.sleep(1)

            try:
                self.device.getAIN(0)
            except:
                self.runningFlag = False
                self.statusBar.showMessage("Connection State: Connection Lost")
                if self.inMainScreen:
                    self.currentScreen.startMeasureButton.setEnabled = False


    def startMeasure(self):
        self.measureType = self.currentScreen.layout.leftLayout.comboBox.currentIndex()
        if self.measureType == 0:
            self.inMeasureScreen = True
            ms = measure_screen.MeasureScreen(self, self.measureType)
            self.container.replaceCentralWidget(ms)
            ms.initUI()
            self.currentScreen = ms
        else:
            settings_screen.SettingsScreen(self, self.measureType, self.container)


    def startTransistorScreen(self):
        ms = transistor_measure_screen.TransistorScreen(self)
        self.container.replaceCentralWidget(ms)
        self.inMeasureScreen = True
        self.currentScreen = ms
        ms.initUI()

    def startMeasureScreen(self):
        ms = measure_screen.MeasureScreen(self, self.measureType)
        self.container.replaceCentralWidget(ms)
        self.inMeasureScreen = True
        self.currentScreen = ms
        ms.initUI()

    def returnToMainScreen(self):
        ms = main_screen.MainScreen(self)
        self.container.replaceCentralWidget(ms)
        self.inMeasureScreen = False
        try:
            ms.initUI()
        except Exception as e:
            print(e)
        self.currentScreen = ms

    def returnToSettingsScreen(self):
       self.returnToMainScreen()
       settings_screen.SettingsScreen(self, self.measureType, self.container)

    def resizeWidgets(self, plt):
        width = self.container.geometry().width()
        height = self.container.geometry().height() - self.container.statusBar().height()
        print(self.minWidthWidget * self.widgetAmount)
        print((width - self.minWidthWidget * self.widgetAmount) - self.padding)
        print("  ")
        if plt is not None:
            plt.setGeometry(self.minWidthWidget * self.widgetAmount, 0, (width - self.minWidthWidget * self.widgetAmount) - self.padding, height)
            plt.canvas.setGeometry(0, 0, (width - self.minWidthWidget * self.widgetAmount) - self.padding, height)