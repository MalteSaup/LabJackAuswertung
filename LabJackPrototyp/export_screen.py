import PyQt5.QtWidgets as qt
import PyQt5.QtGui as qtgui
import PyQt5.QtCore as qtcore

import math
import pandas as pd

class ExportScreen(qt.QMainWindow):
    def __init__(self, df, fig, columnName=["x0", "y0", "y1", "y2", "y3", "y4", "y5", "y6"]):
        super().__init__()

        self.df = df
        self.fig = fig
        self.layout = None
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
            self.df.get(self.columnName[0]).size #TODO WAS ZUM PRÜTZEL
        except Exception as ex:
            print(ex)
        path_full = qt.QFileDialog.getSaveFileName(self, "Save File", "unnamed", datatypeDescription + " (*"+datatype + ");;Any Files (*.*)")
        path = path_full[0]
        if path != "":
            if datatype == ".png" or datatype == ".jpg" or datatype == ".pdf":
                self.fig.savefig(path)
            else:
                self.df = self.dfPacker(self.df)
                sampleCount = int(self.layout.sampleRate.input.text())
                if datatype == ".csv":
                    if self.df.get(self.columnName[0]).size <= sampleCount or sampleCount == 0:
                        self.df.to_csv(r"" + path, index=False)
                    else:
                        uebergabeDF = self.sampleDown(self.df, sampleCount)
                        uebergabeDF.to_csv(r"" + path, index=False)
                elif datatype == ".xlsx":
                    if self.df.get(self.columnName[0]).size <= sampleCount or sampleCount == 0:
                        self.df.to_excel(r"" + path, index=False)
                    else:
                        uebergabeDF = self.sampleDown(self.df, sampleCount)
                        uebergabeDF.to_excel(r"" + path, index=False)
        self.close()

    def dfPacker(self, df):
        x, y = self.dfToXYArr(df)
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
        x, y = self.mergeSort(x, y)
        dataFrame = pd.DataFrame()
        dataFrame.insert(0, self.columnName[0], x, True)
        for i in range(len(y)):
            if self.isEmpty(y[i]):
               pass
            else:
                dataFrame.insert(len(dataFrame.columns), self.columnName[1+i], y[i], True)
        return dataFrame

    def isEmpty(self, arr):
        for i in arr:
            print(i)
            if not math.isnan(i):
                return False
        return True

    def dfToXYArr(self, df):
        cols = df.columns
        y = []
        for col in cols:
            if col in self.columnName[0]:
                x = df[col].copy().tolist()
            elif col in self.columnName[1:]:
                y.append([])
                y[-1] = df[col].copy().tolist()
            elif col == "":
                y[-1] = df[col].copy().tolist()
        return x, y

    def mergeSort(self, x, y):
        cut = int(len(x) / 2)
        left_x = x[:cut].copy()
        left_y = self.yCutter(y, cut)
        if len(left_x) > 1:
            left_x, left_y = self.mergeSort(left_x, left_y)
        right_x = x[cut:].copy()
        right_y = self.yCutter(y, cut, False)

        if len(right_x) > 1:
            right_x, right_y = self.mergeSort(right_x, right_y)
        return self.merge(left_x, right_x, left_y, right_y)


    def yCutter(self, y, cut, left=True):
        arrUeb = [[]] * len(y)
        for i in range(len(y)):
            if left:
                arrUeb[i] = y[i][:cut].copy()
            else:
                arrUeb[i] = y[i][cut:].copy()
        return arrUeb

    def merge(self, lx, rx, ly, ry):
        x_ueb = [None] * (len(lx) + len(rx))
        y_ueb = []
        mulArr = [None] * (len(ly[0]) + len(ry[0]))
        for i in range(len(ly)):
            y_ueb.append(mulArr.copy())
        i = 0
        j = 0

        for numb in range(len(lx) + len(rx)):
            if i >= len(lx):
                x_ueb[numb] = rx[j]
                y_ueb = self.yMergeHelper(y_ueb, ry, numb, j)
                j += 1
            elif j >= len(rx):
                x_ueb[numb] = lx[i]
                y_ueb = self.yMergeHelper(y_ueb, ly, numb, i)
                i += 1
            elif lx[i] <= rx[j]:
                x_ueb[numb] = lx[i]
                y_ueb = self.yMergeHelper(y_ueb, ly, numb, i)
                i += 1
            else:
                x_ueb[numb] = rx[j]
                y_ueb = self.yMergeHelper(y_ueb, ry, numb, j)
                j += 1
        return x_ueb, y_ueb

    def yMergeHelper(self, arrUeb, y, numb, pos):
        for i in range(len(arrUeb)):
            arrUeb[i][numb] = y[i][pos]
        return arrUeb

    def sampleDown(self, df, sampleCount, customColNames=None):
        x_ueb = []
        y_ueb = []
        x, y = self.dfToXYArr(df)
        lenX = len(x)
        for i in range(len(y)):
            y_ueb.append([])
        count = 0

        for i in range(sampleCount):
            x_ueb.append(x[int(count)])
            for j in range(len(y_ueb)):
                y_ueb[j].append(y[j][int(count)])
            count += lenX / sampleCount
        dataFrame = pd.DataFrame()
        if customColNames is None:
            dataFrame.insert(0, self.columnName[0], x_ueb, True)
            for i in range(len(y)):
                dataFrame.insert(len(dataFrame.columns), self.columnName[1+i], y_ueb[i], True)
        else:
            dataFrame.insert(0, customColNames[0], x_ueb, True)
            for i in range(len(y)):
                dataFrame.insert(len(dataFrame.columns), customColNames[1 + i], y_ueb[i], True)
        return dataFrame

    def exportTransistorData(self, df, sampleCount):     #Column Name => ["IB", "IC", "UCE", "UBE"]
        ib = df[self.columnName[0]].copy().tolist()
        ic = df[self.columnName[1]].copy().tolist()
        uce = df[self.columnName[2]].copy().tolist()
        ube = df[self.columnName[3]].copy().tolist()

        """ic2, y1 = self.mergeSort(list(ic), [list(uce), list(ib)])
        ube2, y2 = self.mergeSort(list(ube), [list(ib), list(uce)])

        dataFrame = pd.DataFrame()
        dataFrame.insert(0, "IC", ic2, True)
        dataFrame.insert(1, "UCE", y1[0], True)
        dataFrame.insert(2, "IB", y1[1], True)
        dataFrame.insert(3, "", [None]*len(ic2), True)
        dataFrame.insert(4, "UBE", ube2, True)
        dataFrame.insert(5, "IB", y2[0], True)
        dataFrame.insert(6, "UCE", y2[1], True)
        """

        if len(df[df.columns[0]]) > sampleCount and sampleCount != 0:
            df = self.sampleDown(df, ["IC", "UCE", "IB", "", "UBE", "IB", "UCE"])



class LayoutCompiler(qt.QWidget):
    def __init__(self):
        super().__init__()
        self.chooseDataType = None
        self.buttonHolder = None
        self.sampleRate = None
        self.showUI()

    def showUI(self):
        layout = qt.QVBoxLayout()
        self.setLayout(layout)

        self.chooseDataType = ChooseDataType()
        self.sampleRate = SampleRate()
        self.buttonHolder = ButtonHolder()
        layout.addWidget(self.chooseDataType)
        layout.addWidget(self.sampleRate)
        layout.addWidget(self.buttonHolder)

        self.sampleRate.hide()

        self.chooseDataType.comboBox.currentTextChanged.connect(self.comboChangeEvent)

    def comboChangeEvent(self):
        print(self.chooseDataType.comboBox.currentText())
        if self.chooseDataType.comboBox.currentText() == self.chooseDataType.options[2] or self.chooseDataType.comboBox.currentText() == self.chooseDataType.options[3]:
            self.sampleRate.show()
        else:
            self.sampleRate.hide()


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

class SampleRate(qt.QWidget):
    def __init__(self):
        super().__init__()
        self.input = None
        self.initUI()

    def initUI(self):
        layout = qt.QHBoxLayout()
        self.setLayout(layout)
        label = qt.QLabel("Choose Sample Rate (0 = All): ")
        label.setFixedWidth(200)
        self.input = qt.QLineEdit()
        self.input.setValidator(qtgui.QIntValidator())
        self.input.setText("0")

        layout.addWidget(label)
        layout.addWidget(self.input)

