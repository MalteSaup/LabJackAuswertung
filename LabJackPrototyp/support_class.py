import u6
import threading
import time
import sys

import measure_screen
import main_screen
import transistor_measure_screen
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

        self.inMeasureScreen = False

        self.currentScreen = None

        self.options = options

        self.dpi = round(dpi)
        print(dpi)


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
        print(self.currentScreen.layout.leftLayout.comboBox.currentIndex())
        measureType = 0
        if self.currentScreen.layout.leftLayout.comboBox.currentIndex() == 1:
            measureType = 1
            self.inMeasureScreen = True
        elif self.currentScreen.layout.leftLayout.comboBox.currentIndex() == 2:
            measureType = 2
        if measureType == 2:
            ms = settings_screen.SettingsScreen(self)
        else:
            self.inMeasureScreen = True
            ms = measure_screen.MeasureScreen(self, measureType)

        self.container.replaceCentralWidget(ms)
        try:
            ms.initUI()
        except Exception as e:
            print(e)
        self.currentScreen = ms

    def startTransistorScreen(self):
        ms = transistor_measure_screen.TransistorScreen(self)
        self.container.replaceCentralWidget(ms)
        self.inMeasureScreen = True
        try:
            ms.initUI()
        except Exception as e:
            print(e)
        self.currentScreen = ms

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
        ms = settings_screen.SettingsScreen(self)
        self.container.replaceCentralWidget(ms)
        self.inMeasureScreen = False
        try:
            ms.initUI()
        except Exception as e:
            print(e)
        self.currentScreen = ms


