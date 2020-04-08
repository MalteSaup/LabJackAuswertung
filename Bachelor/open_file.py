import sympy
import pandas as pd
import tkinter as tk
from matplotlib import pyplot as plt


def openDataFile(path):
    if path != "":
        df = pd.DataFrame()
        filetype = path[-3:]
        if (filetype == "lsx"):
            df = pd.read_excel(path)
            col = df.columns
            print(col)
            arr_df = df.to_numpy()
            return createDrawableArr(df, df)
        if (filetype == "csv"):
            df = pd.read_csv(path, sep=",|;", engine="python")
            arr_df = df.to_numpy()
            return createDrawableArr(df, df)
    else:
        return None, None, None


def createDrawableArr(arr_df, df):
    x = None
    arr_y = []
    add = 0
    count = 0
    for i in range(len(arr_df.columns)):
        count += 1
        if "Unnamed" in arr_df.columns[i]:
            add += 1
        elif "x" in arr_df.columns[i] and x is None:
            x = arr_df.iloc[:, i]
        elif "y" in arr_df.columns[i]:
            arr_y.append(arr_df.iloc[:, i])

    return x, arr_y, df


def open_file():
    # arr_df = df.to_numpy()
    path = tk.filedialog.askopenfilename(initialdir="./", title="Open File", filetypes=(
        ("Excel Spreadsheet (.xlsx)", "*.xlsx"), ("CSV Spreadsheet", "*.csv"), ("Any File", "*.*")))

    filetype = path[-4:]
    print(filetype + " " + path)

    x, arr_y, df = openDataFile(path)
    if(x is None):
        return None, None, None
    
    fig, ax = plt.subplots()

    for i in range(len(arr_y)):
        ax.plot(x, arr_y[i], label="i" + str(i), linestyle="none", marker=".", markersize=0.8)

    # ax.plot(arr_x[0], arr_y[1], linestyle="none", marker=".", markersize=0.8)

    # deleteCurrentLayout(frame)
    # canvas = FigureCanvasTkAgg(fig, master=frame)
    # canvas.get_tk_widget().grid(row=0, column=1, rowspan=10)
    return fig, ax, df
