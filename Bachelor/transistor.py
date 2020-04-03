from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
import sympy
def createDataSet():
    ls = []
    for i in range(100):
        ls.append((100 - i)/100)
    return ls

def createAx2Data(x):
    ls = []
    for i in range(100):
        ls.append(sympy.root(i, 16) - x)
    return ls

def createAx3Data():
    ls = []
    for i in range(100):
        ls.append(sympy.root(i, 16)-0.35)
    return ls

def createAx1Data():
    ls = []
    for i in range(100):
        ls.append((100 - i)/100)
    return ls

class TransistorShow:
    def __init__(self, root):
        self.root = root

    def show(self):
        fig, axs = plt.subplots(2, 2,
                                gridspec_kw={"hspace": 0, "wspace": 0})



        (ax1, ax2), (ax3, ax4) = axs

        ax2ls1 = createAx2Data(0)
        ax2ls2 = createAx2Data(0.35)
        ax2ls3 = createAx2Data(0.2)
        ax2ls4 = createAx2Data(0.1)

        ax4ls1 = createAx2Data(0.5)
        ax4ls2 = createAx2Data(0.55)
        ax4ls3 = createAx2Data(0.6)
        ax4ls4 = createAx2Data(0.62)

        ax1.plot(createAx1Data())
        ax2.plot(ax2ls1, color="red")
        ax2.plot(ax2ls2, color="red")
        ax2.plot(ax2ls3, color="red")
        ax2.plot(ax2ls4, color="red")

        ax3.plot(createAx3Data())

        ax4.plot(ax4ls1, color="yellow")
        ax4.plot(ax4ls2, color="yellow")
        ax4.plot(ax4ls3, color="yellow")
        ax4.plot(ax4ls4, color="yellow")






        ax1.spines["left"].set_color("none")
        ax1.spines["top"].set_color("none")
        ax1.get_yaxis().set_visible(False)
        ax1.get_xaxis().set_visible(False)
        ax1.set_ylim(0,1.5)
        ax1.set_xlim(0, 100)


        ax2.spines["right"].set_color("none")
        ax2.spines["top"].set_color("none")
        ax2.get_xaxis().set_visible(False)
        ax2.set_ylim(0,1.5)
        ax2.set_xlim(0, 100)
        ax2.yaxis.set_ticklabels(["", 0.25, 0.50, 0.75, 1.00, 1.25, 1.50])
        #plt.show()

        ax3.invert_xaxis()
        ax3.xaxis.tick_top()
        ax3.set_ylim([1, 0])
        ax3.set_xlim(0, 100)
        ax3.xaxis.set_ticklabels(["", 20, 40, 60, 80, 100])
        ax3.invert_xaxis()
        ax3.spines["left"].set_color("none")
        ax3.spines["bottom"].set_color("none")

        ax3.get_yaxis().set_visible(False)


        ax4.invert_yaxis()
        ax4.set_ylim([1, 0])
        ax4.set_xlim(0, 100)
        ax4.xaxis.set_ticklabels(["", 20, 40, 60, 80, 100])
        ax4.yaxis.set_ticklabels(["", 0.2, 0.4, 0.6, 0.8, 1.0])
        ax4.spines["right"].set_color("none")
        ax4.spines["bottom"].set_color("none")
        ax4.xaxis.tick_top()

        """
        
        fig1 = plt.figure()
        ax = fig1.add_subplot()
        
        ax.spines["left"].set_position("center")
        ax.spines["bottom"].set_position("center")
        
        ax.spines["right"].set_color("none")
        ax.spines["top"].set_color("none")
        """



        return FigureCanvasTkAgg(fig, master=self.root)

