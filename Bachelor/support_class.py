import normal_measure_screen
import export_screen
import main_screen
import time
import threading

import tkinter as tk

class SupportClass:
    def __init__(self, root, device, container, dropdown):
        self.root = root
        self.device = device
        self.container = container
        self.dropdown = dropdown
        self.measureScreen = None
        self.mainScreen = None
        self.exportScreen = None
        self.transistorScreen = None
        self.inMS = False
        self.t = None

        self.running_flag = False

    def deleteCurrentLayout(self, view):
        for obj in view.winfo_children():
            if str(obj) != ".!menu":
                obj.destroy()

    def showNMS(self, resolution_x=10, resolution_y=10):
        self.inMS = False
        if self.measureScreen is None:
            self.measureScreen = normal_measure_screen.NormalMeasureScreen(self.container, self.device, self.dropdown, self, resolution_x, resolution_y)

        if self.measureScreen.resolution_x != resolution_x:
            self.measureScreen.resolution_x = resolution_x
            self.measureScreen.resolution_y = resolution_y

        self.deleteCurrentLayout(self.container)

        self.measureScreen.show()

    def showMS(self):
        self.inMS = True
        if self.mainScreen is None:
            self.mainScreen = main_screen.MainScreen(self.container, self.dropdown, self)

        self.deleteCurrentLayout(self.container)

        self.mainScreen.show()

    def createExportScreen(self):
        self.exportScreen = export_screen.ExportScreen(self.root)

    def check_connection_state_loop(self):

        self.running_flag = True

        self.t = threading.Thread(target=self.check)
        self.t.start()

    def check(self):
        while self.running_flag:
            time.sleep(0.5)
            try:
                print("OOF" + str(self.device.getAIN(0)))
            except:
                self.running_flag = False
                if self.inMs:
                    self.mainScreen.connection_state_label.grid_remove()
                    self.mainScreen.connection_state_label = tk.Label(self.root, text="Connection State: Connection Lost")
                    self.mainScreen.connection_state_label.grid(sticky=tk.SW, row=11, column=0, columnspan=2, pady=10)




