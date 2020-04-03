import tkinter as tk
import sympy
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd

import export_screen

global device, root, df
device = None
root = tk.Tk()
# root.geometry("935x480")
root.title("HAW LabJack")
root.iconbitmap('icon.ico')

frame = tk.Frame(root)

menu = tk.Menu()

exportScreen = export_screen.ExportScreen(root)

dropdown = tk.Menu(menu, tearoff=0)
dropdown.add_command(label="Open File", command=lambda: open_file())
dropdown.add_command(label="Save File", command=lambda: exportScreen.show_export_screen(fig, df))         #um menüpunkt zu deaktivieren state=tk.DISABLED
dropdown.add_command(label="Import Database", command=lambda: print("hi"))

"""
mainScreen = main_screen.MainScreen(root)
mainScreen.show()
transistor_screen = transistor.TransistorShow(root)
canvas = transistor_screen.show()
exportScreen = export_screen.ExportScreen(root)

"""
#dropdown.entryconfig("Save File", state=tk.NORMAL)         um deaktivierten Punkt wieder zu aktivieren

menu.add_cascade(label="File", menu=dropdown)
root.config(menu=menu)

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
    return [arr_x, arr_y[1]], df

def deleteCurrentLayout(layout, is_root=False):
    for obj in layout.winfo_children():
        if str(obj) != ".!menu" or not is_root:
            obj.destroy()

def openDataFile(path):
    global df
    filetype = path[-3:]
    if(filetype == "lsx"):
        df = pd.read_excel(path)
        arr_df = df.to_numpy()
        return createDrawableArr(arr_df, True)
    if(filetype == "csv"):
        df = pd.read_csv(path, sep=",|;", engine="python")
        arr_df = df.to_numpy()
        return createDrawableArr(arr_df)

def createDrawableArr(arr_df, is_excel=False):
    #print(arr_df)
    arr_x = []
    arr_y = []
    sizes = int(len(arr_df[0]) / 2)
    if is_excel:
        add = 1
    else:
        add = 0
    #print(sizes)
    for i in range(sizes):
        arr_x.append([])
        arr_y.append([])

    for obj in arr_df:
        for i in range(sizes):
            #print(sympy.sympify(add + obj[i*2+1]))
            arr_x[i].append(obj[add + i*2])
            arr_y[i].append(sympy.sympify(add + obj[i*2+1]))
    print(arr_y)
    return arr_x, arr_y

def open_file():
    arr_df = df.to_numpy()
    path = tk.filedialog.askopenfilename(initialdir="./", title="Open File", filetypes=(
                                        ("Excel Spreadsheet (.xlsx)", "*.xlsx"), ("CSV Spreadsheet", "*.csv"), ("Any File", "*.*")))

    filetype = path[-4:]
    print(filetype + " " + path)

    arr_x, arr_y = openDataFile(path)

    fig, ax = plt.subplots()
    print(" A A " + str(len(arr_x)))
    #for i in range(len(arr_x)):
     #   ax.plot(arr_x[0], arr_y[0], label="i"+str(i))

    ax.plot(arr_x[0], arr_y[0])

    deleteCurrentLayout(frame)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().grid(row=0, column=1, rowspan=10)



a, df = createSampleData()

plt.style.use("dark_background")
plt.rcParams['toolbar'] = "None"


fig = Figure()

fig.add_subplot().plot(a[0], a[1], linestyle="none", marker=".", markersize=0.8)

canvas = FigureCanvasTkAgg(fig, master=frame)

#print(canvas.get_width_height())

canvas.get_tk_widget().grid(row=0, column=1, rowspan=10)

frame.pack(side=tk.RIGHT)


#deleteCurrentLayout()
"""             so kann man sachen löschen aus dem screen ohne zu wissen wie die namen sind. wichtig später ;-)


root.winfo_children()[1].destroy()
"""
tk.mainloop()

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
