import threading
import time

import u6

from helper import LabJackU6Settings


class LabJackU6:
    def __init__(self, supportClass):
        super().__init__()
        self.labJackU6 = None
        self.supportClass = supportClass
        self.runningFlag = False


    def connectDevice(self):
        try:
            if self.runningFlag:
                pass
            else:
                self.labJackU6 = u6.U6()
                self.labJackU6.getCalibrationData()
                self.checkConnectionThread()
                self.supportClass.statusBar.showMessage("Connection State: Connected")
                self.runningFlag = True
                self.supportClass.runningFlag = True
            return True
        except Exception as e:
            print(e)
            return False

    def checkConnectionThread(self):
        self.runningFlag = True
        self.t = threading.Thread(target=self.check)
        self.t.start()

    def check(self):
        while self.runningFlag:
            time.sleep(1)

            try:
                self.labJackU6.getAIN(0)
            except:
                self.supportClass.runningFlag = False
                self.runningFlag = False
                self.supportClass.statusBar.showMessage("Connection State: Connection Lost")
                print(self.supportClass.inMainScreen)
                if self.supportClass.inMainScreen:
                    self.supportClass.currentScreen.startMeasureButton.setEnabled(False)

    def getMeasureData(self):
        currentMeasureData = self.labJackU6.readRegister(0, LabJackU6Settings.MINCHANNELREAD.value)
        processedData = []
        processedData.append(abs(currentMeasureData[0] - currentMeasureData[1]))
        processedData.append(abs(currentMeasureData[2] - currentMeasureData[3]))
        processedData.append(abs(currentMeasureData[4] - currentMeasureData[6]))
        processedData.append(abs(currentMeasureData[5] - currentMeasureData[7]))
        return processedData

