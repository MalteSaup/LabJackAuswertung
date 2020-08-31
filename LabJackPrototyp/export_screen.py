import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

import math
import pandas as pd

import return_message_box

class ExportScreen(qt.QMainWindow):
    def __init__(self, df, fig, columnName=["x0", "y0", "y1", "y2", "y3", "y4", "y5", "y6"]):
        super().__init__()

        self.df = df
        self.fig = fig
        self.layout = None
        self.errorBox = None
        self.columnName = columnName
        self.showUI()

    def showUI(self):
        self.layout = LayoutCompiler()

        self.layout.buttonHolder.cancelButton.pressed.connect(lambda: self.close)
        self.layout.buttonHolder.saveButton.pressed.connect(self.saveClick)

        self.setWindowModality(qtcore.Qt.ApplicationModal)  #Makes underlying window unclickable

        self.setCentralWidget(self.layout)

    def saveClick(self):
        if self.layout.chooseDataType.comboBox.currentText() == self.layout.chooseDataType.options[0]:
            self.saveFile("PDF", ".pdf")
        elif self.layout.chooseDataType.comboBox.currentText() == self.layout.chooseDataType.options[1]:
            self.saveFile("JPEG", ".jpg")
        elif self.layout.chooseDataType.comboBox.currentText() == self.layout.chooseDataType.options[2]:
            self.saveFile("Excel Spreadsheet", ".xlsx")
        elif self.layout.chooseDataType.comboBox.currentText() == self.layout.chooseDataType.options[3]:
            self.saveFile("CSV File", ".csv")


    def saveFile(self, datatypeDescription, datatype):
        try:
            print("GRÖSSE " + str(self.df.get(self.columnName[0]).size))
        except Exception as ex:
            print(ex)
        path_full = qt.QFileDialog.getSaveFileName(self, "Save File", "unnamed", datatypeDescription + " (*"+datatype + ");;Any Files (*.*)")
        path = path_full[0]
        try:
            if path != "":
                if datatype == ".png" or datatype == ".jpg" or datatype == ".pdf":
                    self.fig.savefig(path)
                else:
                    self.df = self.dfPacker(self.df)
                    print(self.df.columns)
                    if datatype == ".csv":
                        self.df.to_csv(r"" + path, index=False)
                    elif datatype == ".xlsx":
                        self.df.to_excel(r"" + path, index=False)
                self.close()
        except PermissionError:
            self.errorBox = return_message_box.SaveErrorPermissionDeniedBox()
            self.errorBox.exec_()
        except Exception as ex:
            self.errorBox = return_message_box.SomethingWentWrong()
            self.errorBox.exec_()

    def dfPacker(self, df):
        x, y = self.dfToXYArr(df)
        print(y)
        deleteArray = []
        for i in y:
            yTotalEmpty = self.isEmpty(i)
            if not yTotalEmpty:
                break
        if not yTotalEmpty:
            for i in range(len(y[0])):
                delete = True
                for col in y:
                    if not math.isnan(col[i]):
                        delete = False
                        break
                if delete:
                    deleteArray.append(i)
            for i in range(len(deleteArray) -1, -1, -1):
                x.pop(deleteArray[i])
                for col in y:
                    col.pop(deleteArray[i])
        #x, y = self.mergeSort(x, y)
        dataFrame = pd.DataFrame()
        dataFrame.insert(0, self.columnName[0], x, True)
        for i in range(len(y)):
            if self.isEmpty(y[i]):
               pass
            else:
                dataFrame.insert(len(dataFrame.columns), self.columnName[i+1], y[i], True)
        return dataFrame

    def isEmpty(self, arr):
        for i in arr:
            print(i)
            if type(i) == str or not math.isnan(i):
                return False
        return True

    def dfToXYArr(self, df):
        cols = df.columns
        print(cols)
        y = []
        for col in cols:
            if col in self.columnName[0]:
                x = df[col].copy().tolist()
            elif col in self.columnName[1:]:
                print(col)
                y.append([])
                y[-1] = df[col].copy().tolist()
            elif col == "":
                y[-1] = df[col].copy().tolist()
        return x, y

class LayoutCompiler(qt.QWidget):
    def __init__(self):
        super().__init__()
        self.chooseDataType = None
        self.buttonHolder = None
        self.showUI()

    def showUI(self):
        layout = qt.QVBoxLayout()
        self.setLayout(layout)

        self.chooseDataType = ChooseDataType()
        self.buttonHolder = ButtonHolder()
        layout.addWidget(self.chooseDataType)
        layout.addWidget(self.buttonHolder)

class ChooseDataType(qt.QWidget):
    def __init__(self):
        super().__init__()
        self.options = [
            "PDF (.pdf)",
            "JPEG (.jpg)",
            "Excel Spreadsheet (.xlsx)",
            "CSV File (.csv)"
        ]
        self.comboBox = None

        self.showUI()

    def showUI(self):
        layout = qt.QHBoxLayout()
        self.setLayout(layout)
        label = qt.QLabel("Choose Datatype: ")
        label.setFixedWidth(200)
        # DropDown
        self.comboBox = qt.QComboBox()
        for option in self.options:
            self.comboBox.addItem(option)

        layout.addWidget(label)
        layout.addWidget(self.comboBox)


class ButtonHolder(qt.QWidget):
    def __init__(self):
        super().__init__()

        self.saveButton = None
        self.cancelButton = None

        self.initUI()

    def initUI(self):
        layout = qt.QHBoxLayout()
        self.setLayout(layout)
        self.saveButton = qt.QPushButton("Save Data")
        self.cancelButton = qt.QPushButton("Cancel")

        self.saveButton.setFixedWidth(100)
        self.cancelButton.setFixedWidth(100)

        layout.addWidget(self.saveButton)
        layout.addWidget(self.cancelButton)