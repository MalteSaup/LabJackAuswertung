from matplotlib import pyplot as plt
from tkinter import *
from PIL import ImageTk, Image
import u6
import threading
import time

import normal_measure_screen

global root, device, running_flag

class MainScreen:
    def __init__(self, root, dropdown, support_class):
        self.root = root
        self.dropdown = dropdown
        self.support_class = support_class

        self.connection_state_label = None

    def callback(self):
        self.support_class.running_flag = False
        self.support_class.root.destroy()

    def connect_device(self):
        global device, connection_state_label, running_flag
        try:
            self.support_class.device = u6.U6()
            self.support_class.device.getCalibrationData()

            self.connection_state_label = Label(self.root, text="Connection State: Connection Completed")
            self.support_class.check_connection_state_loop()
        except:
            print(self.connection_state_label)
            if self.connection_state_label is not None:
                self.connection_state_label.grid_remove()
            self.connection_state_label = Label(self.root, text="Connection State: Connection Failed")

        self.connection_state_label.grid(sticky=SW, row=11, column=0, columnspan=2, pady=10)



    def close(self):
        global running_flag
        running_flag = False
        self.root.quit()

    def show(self):
        self.support_class.root.protocol("WM_DELETE_WINDOW", self.callback)

        options = [
            "Experiment 1",
            "Experiment 2",
            "Experiment 3",
            "Experiment 4"
        ]
        self.image_orig = [Image.open("./Dioden_Messschaltung.png")]
        self.image = [ImageTk.PhotoImage(self.image_orig[0].resize((760, 380), Image.ANTIALIAS))]


#        plt.style.use("dark_background")
#        plt.rcParams['toolbar'] = "None"

        #transistor = transistor.TransistroShow(root)
        #transistor.show().get_tk_widget().grid(row=0, column=0)


        var = StringVar()
        var.set(options[0])
        dropdown_experiment = OptionMenu(self.root, var, *options)                  #stern benötigt damit es options als liste erkennt
        dropdown_experiment.config(width=18, height=1)

        connection_state_label = Label(self.root, text="Connection State: Not Connected")
        connect_button = Button(self.root, text="Connect to Device", width=20, height=2, command=self.connect_device)
        start_measure_button = Button(self.root, text="Start Measurement", width=20, height=2, command=self.startMeasure)
        exit_button = Button(self.root, text="Exit", command=self.close, width=20, height=2)

        image_label = Label(self.root, image=self.image[0], width=760, height=380)

        connect_button.grid(row=0, column=0, pady=5, padx=5)
        dropdown_experiment.grid(row=1, column=0, pady=5, padx=5)
        start_measure_button.grid(row=2, column=0, pady=5, padx=5)
        exit_button.grid(row=9, column=0, pady=5, padx=5)
        connection_state_label.grid(sticky=SW, row=11, column=0, columnspan=2, pady=10)

        image_label.grid(row=0, column=1, rowspan=10)

        self.root.rowconfigure(11, weight=1)
        self.root.rowconfigure(1, weight=2)
        self.root.columnconfigure(1, weight=2)

        #mainloop()

    def startMeasure(self):
        self.support_class.showNMS(10, 10)



