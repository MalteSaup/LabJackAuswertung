import u6
from time import perf_counter
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd

global device, resolution_x, resolution_y

class NormalMeasureScreen:
    global device, resolution_x, resolution_y
    def __init__(self, root, device, resolution_x=10, resolution_y=10):
        self.device = device
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.root = root

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
    def show(self):
        plt.rcParams['toolbar'] = "None"
        plt.style.use("dark_background")
        plt.grid(True)



        x = []
        y = []

        global count, oldtime, stopped, df_set
        count = 0
        oldtime = 0
        stopped = False
        df_set = False
        def animate(i):

            global df_set, count, oldtime
            if not stopped:

                y.append(device.getAIN(0) / 10 - 1)
                print(device.getAIN(2))
                #print(perf_counter()- oldtime)
                oldtime = perf_counter()
                x.append(count)
                count += 0.1

                plt.cla()
                plt.grid(True, color="#444", alpha=0.5, linestyle="--")
                plt.ylim([0-resolution_y/2, 0+resolution_y/2])

                #plt.rcParams['toolbar'] = "None"
                if count > 10:
                    plt.xlim([count-resolution_x, count])
                else:
                    plt.xlim([0, resolution_x])

                if df_set:
                    df_set = False

                plt.plot(x, y, linestyle="-", color="#00ff00", markersize=1, alpha=1)
            elif not df_set:
                global df, fig
                fig, ax = plt.subplots()
                df = pd.DataFrame({
                    "x0": x,
                    "y0": y
                })
                df_set = True

        def getData():
            return fig, df

        ani = FuncAnimation(plt.gcf(), animate, interval=100)
        plt.show()
