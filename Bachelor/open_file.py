import sympy
import pandas as pd
import tkinter as tk
from matplotlib import pyplot as plt

def openDataFile(path):
    df = pd.DataFrame()
    filetype = path[-3:]
    if(filetype == "lsx"):
        df = pd.read_excel(path)
        arr_df = df.to_numpy()
        return createDrawableArr(arr_df, df, 1)
    if(filetype == "csv"):
        df = pd.read_csv(path, sep=",|;", engine="python")
        arr_df = df.to_numpy()
        return createDrawableArr(arr_df, df)

def createDrawableArr(arr_df, df, add=0):
    #print(arr_df)
    arr_x = []
    arr_y = []
    sizes = int(len(arr_df[0]) / 2)

    for i in range(sizes):
        arr_x.append([])
        arr_y.append([])

    for obj in arr_df:
        for i in range(sizes):
            arr_x[i].append(obj[add + i*2])
            arr_y[i].append(sympy.sympify(obj[add + i*2+1]))
    return arr_x, arr_y, df

def open_file():
    #arr_df = df.to_numpy()
    path = tk.filedialog.askopenfilename(initialdir="./", title="Open File", filetypes=(
                                        ("Excel Spreadsheet (.xlsx)", "*.xlsx"), ("CSV Spreadsheet", "*.csv"), ("Any File", "*.*")))

    filetype = path[-4:]
    print(filetype + " " + path)

    arr_x, arr_y, df = openDataFile(path)

    fig, ax = plt.subplots()
    print(" A A " + str(len(arr_x)))
    for i in range(len(arr_x)):
        ax.plot(arr_x[0], arr_y[i], label="i"+str(i), linestyle="none", marker=".", markersize=0.8)

    #ax.plot(arr_x[0], arr_y[1], linestyle="none", marker=".", markersize=0.8)

    #deleteCurrentLayout(frame)
    #canvas = FigureCanvasTkAgg(fig, master=frame)
    #canvas.get_tk_widget().grid(row=0, column=1, rowspan=10)
    return fig, ax, df