import u6
from time import perf_counter
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
import random
import os
import copy

import export_screen

class NormalMeasureScreen:

    def __init__(self, root, device, dropdown, support_class, measure_type=0, resolution_x=10, resolution_y=10):
        self.device = device
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.measure_type = measure_type
        self.root = root
        self.dropdown = dropdown
        self.support_class = support_class

        self.ani = None

        self.dropdown.entryconfigure("Save File", state=tk.ACTIVE, command=self.init_save)

        self.exportScreen = self.support_class.exportScreen

        self.checkboxes = []
        self.checkbox_container = None
        self.plotting_container = None

    """
    def clock(ratehz):
        start_time = perf_counter()
        while(perf_counter() - start_time < 1 / ratehz):
            pass
        print(d.getAIN(2))
    
    st = perf_counter()
    for i in range(100000):
        clock(100)
    et = perf_counter()
    print(str((et - st)))
    """

    def init_save(self):
        global stopped
        stopped = True
        thread = threading.Thread(target=self.check_for_dfset)
        thread.start()

    def check_for_dfset(self):
        global df_set
        time.sleep(0.2)
        print("_____-----_____")
        if df_set:
            global fig, df, stopped
            self.exportScreen.show_export_screen(fig, df)
            stopped = False
            return df_set
        else:
            return self.check_for_dfset()

    def return_to_menu(self):
        response = tk.messagebox.askquestion("HAW LabJack", "Do you want to Exit the Measure Screen? All unsafed Data will be lost")
        if response == "yes":
            self.support_class.showMS()

    def show(self):
        self.support_class.root.protocol("WM_DELETE_WINDOW", self.callback)

        plt.rcParams['toolbar'] = "None"
        plt.style.use("dark_background")
        plt.grid(True)
        # plt.block(False)

        print("WUW")

        x = []
        y = []

        global count, oldtime, stopped, df_set, fig, ax, vars, ls, ms, running, t, axes
        t = None

        ls = "-"
        ms = "None"

        running = True

        colors = [
            "#00ff00",
            "#ff0000",
            "#0000ff",
            "#ffffff"
        ]

        fig, ax = plt.subplots()

        count = 0
        oldtime = 0
        stopped = False
        df_set = False

        # ax.plot(x, y, linestyle="-", marker="None", color="#00ff00")

        self.checkbox_container = tk.Frame(self.root)
        self.plotting_container = tk.Frame(self.root)
        self.checkbox_container.pack(side=tk.LEFT)
        self.plotting_container.pack(side=tk.RIGHT)
        # ------------------------------------

        vars = []

        tk.Label(self.checkbox_container, text="Chose AIN to Plot").grid(row=0, column=0, columnspan=2)
        return_button = tk.Button(self.checkbox_container, text="Return to Menu", command=self.return_to_menu)
        return_button.grid(row = 4, column=0, columnspan=2, padx=5, pady=5)
        for i in range(4):
            vars.append(tk.IntVar())
            if (i == 0):
                vars[i].set(1)
            self.checkboxes.append(tk.Checkbutton(self.checkbox_container, text="AIN" + str(i), variable=vars[i]))
            self.checkboxes[i].grid(row=1 + int(i / 2), column=i % 2, padx=5, pady=5)
            y.append([])
        # ------------------------------------
        vars.append(tk.IntVar())
        vars.append(tk.IntVar())
        vars[-2].set(1)
        self.checkboxes.append(tk.Checkbutton(self.checkbox_container, text="Line", variable=vars[-2]))
        self.checkboxes.append(tk.Checkbutton(self.checkbox_container, text="Marker", variable=vars[-1]))
        self.checkboxes[-2].grid(row=3, column=0, padx=5, pady=5)
        self.checkboxes[-1].grid(row=3, column=1, padx=5, pady=5)

        # self.checkbox_container.pack()

        if self.measure_type != 2:
            canvas = FigureCanvasTkAgg(fig, master=self.plotting_container)
            canvas.get_tk_widget().pack()
        else:
            fig, axes = self.support_class.showTransistor(self.plotting_container)
            canvas = FigureCanvasTkAgg(fig, master=self.plotting_container)
            canvas.get_tk_widget().pack()

        def set_df():
            global df_set, df
            numb = 0

            all_same_size, x_ue, y_ue, arr_ueb = check_xy_length()

            if all_same_size:
                df = pd.DataFrame()
                df.insert(0, "x0", x_ue, True)  # True is allow duplicates
                for i in range(len(y)):
                    if vars[i].get() == 1:
                        #print(len(df.columns))
                        df.insert(len(df.columns), "y" + str(numb), y_ue[i], True)
                        numb += 1
                        #print(df)
                df_set = True
            return df_set

        def check_xy_length():
            y_ue = copy.deepcopy(y)
            x_ue = list(x)
            check_arr = []

            same_length = True
            for j in range(4):
                if vars[j].get() == 1:
                    check_arr.append(j)

            for i in check_arr:
                #print(len(x_ue))
                #print(len(y_ue[i]))
                if not len(x_ue) == len(y_ue[i]):
                    same_length = False

            return same_length, x_ue, y_ue, check_arr

        def animate_oszi(i):

            global df_set, fig, ax, ls, ms

            if not stopped:
                """
                a, df = createSampleData()

                plt.style.use("dark_background")
                plt.rcParams['toolbar'] = "None"

                fig = Figure()

                fig.add_subplot().plot(a[0], a[1], linestyle="none", marker=".", markersize=0.8)

                canvas = FigureCanvasTkAgg(fig, master=frame)

                # print(canvas.get_width_height())

                

                frame.pack(side=tk.RIGHT)
                
                fig, ax, df = open_file.open_file()

                deleteCurrentLayout(frame)
                canvas = FigureCanvasTkAgg(fig, master=frame)

                canvas.get_tk_widget().grid(row=0, column=1, rowspan=10)
                
                
                
                
                """
                if (vars[-2].get() == 1):
                    ls = "-"
                else:
                    ls = "None"

                if (vars[-1].get() == 1):
                    ms = "."
                else:
                    ms = "None"

                all_drawable, x_ue, y_ue, check_arr = check_xy_length()


                #print(all_drawable)
                #print(check_arr)

                if len(check_arr) == 0:
                    ax.clear()
                else:   #Flakker Schutz durch externen Thread entstehende inkonsitenzen der Datensätze
                    if all_drawable:
                        ax.clear()
                        for i in check_arr:
                            ax.plot(x_ue, y_ue[i], linestyle=ls, marker=ms, color=colors[i], markersize=0.8)
                        if x_ue == []:
                            ax.set_xlim([0, self.resolution_x])
                        elif x_ue[-1] > 10:
                            ax.set_xlim([count - self.resolution_x, count])
                        else:
                            ax.set_xlim([0, self.resolution_x])
                ax.set_ylim([-10, 15])

                if df_set:
                    df_set = False

            elif not df_set:
                set_df()

        def animate_normal(i):
            global df_set, count, oldtime, fig, ax, ls, ms

            if not stopped:

                # print(len(uebergabe))
                if (vars[-2].get() == 1):
                    ls = "-"
                else:
                    ls = "None"

                if (vars[-1].get() == 1):
                    ms = "."
                else:
                    ms = "None"

                all_drawable, x_ue, y_ue, check_arr = check_xy_length()


                if len(check_arr) == 0:
                    ax.clear()
                else:   #Flakker Schutz durch externen Thread entstehende inkonsitenzen der Datensätze
                    if all_drawable:
                        ax.clear()
                        for i in check_arr:
                            ax.plot(y_ue[i], x_ue, linestyle=ls, marker=ms, color=colors[i], markersize=0.8)

                ax.set_ylim([-0.5, 1.5])
                # print(perf_counter()- oldtime)
                # oldtime = perf_counter()

                count += 0.1
                # print("count" + str(count))
                # plt.grid(True, color="#444", alpha=0.5, linestyle="--")
                # plt.ylim([0-self.resolution_y/2, 0+self.resolution_y/2])

                # plt.rcParams['toolbar'] = "None"
                ax.set_xlim([-0.5, 1.5])

                if df_set:
                    df_set = False



                # plt.plot(x, y, linestyle="-", color="#00ff00", markersize=1, alpha=1)
            elif not df_set:
                set_df()

        def animate_transistor(i):
            if (vars[-2].get() == 1):
                ls = "-"
            else:
                ls = "None"

            if (vars[-1].get() == 1):
                ms = "."
            else:
                ms = "None"

        animations = [animate_oszi, animate_normal, animate_transistor]

        def test(self):
            global running
            time.sleep(0.2)
            while running:
                clock(self, 1000)


        #print(self.measure_type)
        self.ani = FuncAnimation(fig, animations[self.measure_type], interval=150)

        def clock(self, ratehz):
            start_time = perf_counter()
            #print("HO")
            while (perf_counter() - start_time < 1 / ratehz):
                pass

            uebergabe = self.device.readRegister(0, numReg=26)
            for j in range(4):
                if vars[j].get() == 1:
                    # print(colors[j])
                    y[j].append(abs(uebergabe[j * 2] / 10))
                else:
                    y[j].append(None)

            if self.measure_type == 0:      #Oszi
                global count
                x.append(count)
                count += 0.01

            elif self.measure_type == 1:    #Rand Show Later Read Measure Data
                x.append(float(random.randint(0, 100) / 100))

        t = threading.Thread(target=lambda: test(self))
        t.start()

        def getData():
            return fig, df

        # plt.show()

    def callback(self):
        global ax, fig, t, running
        response = tk.messagebox.askquestion("HAW LabJack",
                                             "Do you want to Exit Programm? All unsafed Data will be lost")
        if response == "yes":
            running = False
            #t.join()

            ax.clear()
            fig.clear()

            plt.close()
            self.ani.event_source.stop()

            self.support_class.running_flag = False
            self.support_class.root.destroy()
            print("VORHER")
            self.support_class.t.running_flag = False
            os._exit(666)  # nötig da sonst skript unendlich weiter läuft todo fehlersuche