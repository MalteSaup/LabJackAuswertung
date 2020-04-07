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
import export_screen

class NormalMeasureScreen:

    def __init__(self, root, device, dropdown, real_root,resolution_x=10, resolution_y=10):
        self.device = device
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.root = root
        self.dropdown = dropdown

        self.dropdown.entryconfigure("Save File", state=tk.ACTIVE, command=self.init_save)

        self.exportScreen = export_screen.ExportScreen(self.root)
        real_root.protocol("WM_DELETE_WINDOW", self.callback)

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

    def callback(self):
        global fig
        plt.close()
        self.root.quit()

    def init_save(self):
        global stopped, df
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
            df_set = True
            return df_set
        else:
            return self.check_for_dfset(self)

    def show(self):
        plt.rcParams['toolbar'] = "None"
        plt.style.use("dark_background")
        plt.grid(True)

        print("WUW")

        x = []
        y = []

        global count, oldtime, stopped, df_set, fig, ax

        fig, ax = plt.subplots()

        count = 0
        oldtime = 0
        stopped = False
        df_set = False


        #ax.plot(x, y, linestyle="-", marker="None", color="#00ff00")

        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.get_tk_widget().pack()

        def animate(i):

            global df_set, count, oldtime, fig, ax
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

                x.append(count)
                y.append(self.device.getAIN(0) / 10 - 1)
                #print(perf_counter()- oldtime)
                #oldtime = perf_counter()

                count += 0.1
                print(count)
                ax.clear()
                ax.set_ylim([-5,5])
                ax.plot(x, y, linestyle="-", marker="None", color="#00ff00")
                #plt.grid(True, color="#444", alpha=0.5, linestyle="--")
                #plt.ylim([0-self.resolution_y/2, 0+self.resolution_y/2])

                #plt.rcParams['toolbar'] = "None"
                if count > 10:
                    ax.set_xlim([count-self.resolution_x, count])
                else:
                    ax.set_xlim([0, self.resolution_x])

                if df_set:
                    df_set = False

                #plt.plot(x, y, linestyle="-", color="#00ff00", markersize=1, alpha=1)
            elif not df_set:
                global df, fig
                df = pd.DataFrame({
                    "x0": x,
                    "y0": y
                })
                df_set = True

        ani = FuncAnimation(fig, animate, interval=100)
        ani._start()
        def getData():
            return fig, df


        #plt.show()
