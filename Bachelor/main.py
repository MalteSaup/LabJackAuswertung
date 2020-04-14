import tkinter as tk
import sympy
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
import threading

import export_screen
import open_file
import support_class
import transistor
import main_screen
import normal_measure_screen

global device, root, df, fig, measureScreen
device = None
root = tk.Tk()
# root.geometry("935x480")
root.title("HAW LabJack")
root.iconbitmap('icon.ico')

container = tk.Frame(root)

menu = tk.Menu()

dropdown = tk.Menu(menu, tearoff=0)

dropdown.add_command(label="Open File", command=lambda: open_file_function())
dropdown.add_command(label="Save File", state=tk.DISABLED)         #um menüpunkt zu deaktivieren state=tk.DISABLED
dropdown.add_command(label="Import Database", command=lambda: print("hi"))

menu.add_cascade(label="File", menu=dropdown)

root.config(menu=menu)

container.pack()

supportClass = support_class.SupportClass(root, device, container, dropdown)

supportClass.createExportScreen()

supportClass.showMS()

#dropdown.entryconfig("Save File", state=tk.NORMAL)         um deaktivierten Punkt wieder zu aktivieren

def saveMeasureData():
    threading.Thread(supportClass.exportScreen.show_export_screen(supportClass.measureScreen.getData())).start()

def createSampleData():
    arr_x = []
    arr_y = [[],[]]
    for i in range(100):
        arr_y[0].append(sympy.root(i, 16))
        arr_y[1].append(sympy.sin((i*3.6)/180*sympy.pi))
        arr_x.append(i / 100)

    df = pd.DataFrame({
        "x1": arr_x,
        "y1": arr_y[0],
        "x2": arr_x,
        "y2": arr_y[1]
    })
    return [arr_x, arr_y[0]], df

def open_file_function():
    global df
    fig = None
    fig, ax, df = open_file.open_file()
    if fig is None:
        pass
    else:
        supportClass.deleteCurrentLayout(container)
        canvas = FigureCanvasTkAgg(fig, master=container)

        canvas.get_tk_widget().grid(row=0, column=1, rowspan=10)

        root.protocol("WM_DELETE_WINDOW", callback)

def callback():
    exit(666)

tk.mainloop()



#dropdown.entryconfigure("Save File", state=tk.ACTIVE, command=lambda: print("Hi"))

#for i in range(s+1):
#    print(dropdown.entrycget(i, "label"))


"""
a, df = createSampleData()

plt.style.use("dark_background")
plt.rcParams['toolbar'] = "None"


fig = Figure()

fig.add_subplot().plot(a[0], a[1], linestyle="none", marker=".", markersize=0.8)

canvas = FigureCanvasTkAgg(fig, master=frame)

#print(canvas.get_width_height())

canvas.get_tk_widget().grid(row=0, column=1, rowspan=10)

frame.pack(side=tk.RIGHT)

"""
#deleteCurrentLayout()
"""             so kann man sachen löschen aus dem screen ohne zu wissen wie die namen sind. wichtig später ;-)


root.winfo_children()[1].destroy()
"""

"""
def a(e):
    global height_old, width_old
    height = root.winfo_height()
    width = root.winfo_width()
    if(height != height_old or width != width_old):
        global image, image_orig, image_label
        height_old = height
        width_old = width
        height = int(height)
        width = int(height * 2)

        image_label.grid_remove()
        image[0] = [ImageTk.PhotoImage(image_orig[0].resize((width, height), Image.ANTIALIAS))]

        image_label = Label(root, image=image[0], width=width, height=height)
        image_label.grid(row=0, column=1, rowspan=10)
        print(str(height) + " " + str(height_old)+ " " + str(width) + "  " + str(width_old))


#root.bind("<Configure>", a)
"""

# root.geometry(str(root.winfo_screenwidth()) + "x" + str(root.winfo_screenheight()))                                #Creates Fullscreen
