import tkinter as tk
import pandas as pd

global sample_shown, sample_entry, sample_label, options, df, window, root
def on_save_screen_destroy(window):
    window.grab_release()
    window.destroy()

def callback(P):
    if str.isdigit(P) or P == "":
        return True
    else:
        return False

def save_file(datatype_description, datatype, fig, df, samplecount=0):
    global window, root

    path = tk.filedialog.asksaveasfilename(initialfile="unnamed", initialdir="./", title="Save as",
                                        filetypes=[(datatype_description, "*"+datatype),
                                                   ("Any File", "*.*")])
    print(path)
    if path != "":
        path += datatype

        if datatype == ".png" or datatype == ".jpg" or datatype == ".pdf":
            fig.savefig(path)
        elif datatype == ".csv":
            if(df.get("x1").size <= samplecount or samplecount == 0):
                df.to_csv(r""+path, index=False)
            else:
                uebergabe_df = sample_down(df, samplecount)
                uebergabe_df.to_csv(r""+path, index=False)
        elif datatype == ".xlsx":
            if (df.get("x1").size <= samplecount or samplecount == 0):
                df.to_excel(path)
            else:
                uebergabe_df = sample_down(df, samplecount)
                uebergabe_df.to_excel(path)
        on_save_screen_destroy(window)

def sample_down(df, samplecount):
    arr_df = df.to_numpy()
    arr_size = float(len(arr_df))
    sizes = int(len(arr_df[0]) / 2)
    """
    arr_x = []
    arr_y = []
    sizes = int(len(arr_df[0]) / 2)
    print(sizes)
    for i in range(sizes):
        arr_x.append([])
        arr_y.append([])

    for obj in arr_df:
        for i in range(sizes):
            arr_x[i].append(obj[i * 2])
            arr_y[i].append(sympy.sympify(obj[i * 2 + 1]))"""

    arr_x = []
    arr_y = []
    df_arr_x = []
    df_arr_y = []
    count = 0

    for i in range(sizes):
        arr_x.append([])
        arr_y.append([])

    #print(arr_df)

    for i in range(samplecount):
        for j in range(sizes):
            arr_x[j].append(arr_df[int(count)][j*2])
            arr_y[j].append(arr_df[int(count)][j*2+1])
        count += arr_size / samplecount
    print(arr_x)

    data_frames = []

    for i in range(sizes):
        data_frames.append(pd.DataFrame({"x" + str(i): arr_x[i]}))
        data_frames.append(pd.DataFrame({"y" + str(i): arr_y[i]}))

    df_uebergabe = data_frames[0]
    print(len(data_frames))
    for i in range(1, len(data_frames)):
        df_uebergabe = df_uebergabe.join(data_frames[i])

    print(df_uebergabe)
    return df_uebergabe


def var_change(var):
    global sample_shown, sample_entry, sample_label, options
    if var == options[0] or var == options[1]:
        if sample_shown:
            sample_entry.grid_remove()
            sample_label.grid_remove()
            sample_shown = False
    elif var == options[2] or var == options[3]:
        if not sample_shown:
            sample_label.grid(row=1, column=0, padx=10, pady=10)
            sample_entry.grid(row=1, column=1, padx=10, pady=10)
            sample_entry.insert(0, "20")
            sample_shown = True

def save_click(var, fig, df):
    global options, sample_entry
    print(var)
    if var == options[0]:
        save_file("PDF", ".pdf", fig, None)
    elif var == options[1]:
        save_file("JPEG", ".jpg", fig, None)
    elif var == options[2]:
        samplecount = int(sample_entry.get())
        print(samplecount)
        save_file("Excel Spreadsheet", ".xlsx", fig, df, samplecount)
    elif var == options[3]:
        samplecount = int(sample_entry.get())
        save_file("CSV File", ".csv", fig, df, samplecount)

class ExportScreen:
    def __init__(self, root):
        self.root = root



    def show_export_screen(self, fig, df):
        global sample_shown, sample_entry, sample_label, options, window
        var = tk.StringVar()

        var.trace("w", lambda *args: var_change(var.get()))

        sample_shown = False

        window = tk.Toplevel(self.root)
        window.grab_set()
        window.resizable(False, False)
        window.title("Export as")
        window.iconbitmap('icon.ico')
        window.protocol("WM_DELETE_WINDOW", lambda: on_save_screen_destroy(window))

        cancel_button = tk.Button(window, text="Cancel", command=lambda: on_save_screen_destroy(window), width=10, height=1)
        save_button = tk.Button(window, text="Export", width=10, height=1, command=lambda: save_click(var.get(), fig, df))
        options = [
            "PDF (.pdf)",
            "JPEG (.jpg)",
            "Excel Spreadsheet (.xlsx)",
            "CSV File (.csv)"
        ]
        var.set(options[0])
        dropdown_dataformat = tk.OptionMenu(window, var, *options)  # stern benötigt damit es options als liste erkennt
        dropdown_dataformat.config(width=22, height=1)
        data_label = tk.Label(window, text="Choose Dataformat to Export to: ", width=50)

        vcmd = (window.register(callback))

        sample_label = tk.Label(window, text="Count of Sampledatas you want to export: ")
        sample_entry = tk.Entry(window, width=22, validate="all", validatecommand=(vcmd, "%P"))

        data_label.grid(row=0, column=0, padx=10, pady=10)
        dropdown_dataformat.grid(row=0, column=1, padx=10, pady=10)

        cancel_button.grid(row=2, column=0, pady=10)
        save_button.grid(row=2, column=1, pady=10)