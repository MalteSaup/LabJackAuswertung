import numpy as np

class Calculator:
    def calcBHelper(self, icVal, ibVal):
        try:
            return icVal * 1000 / ibVal
        except:
            return -1

    def calcB(self, ic, ib):
        ib, ic = self.sortArraysByArray(ib, ic)
        bArray = [self.calcBHelper(icVal, ibVal) for icVal, ibVal in zip(ic, ib)]
        bArray = sorted(bArray)
        return bArray[int(len(bArray) / 2)]

    def sortArraysByArray(self, arrSortedAfter, arrGetsSorted):
        arrZip = zip(arrSortedAfter, arrGetsSorted)
        sortedZip = sorted(arrZip)
        arrSortedAfterZip, arrGetsSortedZip = zip(*sortedZip)
        return list(arrSortedAfterZip), list(arrGetsSortedZip)

    def getDatarange(self, array1, array2, maxDifference=0.45, minDifference=0.7):
        array2Max = max(array2)
        indexArray2Max = array2.index(array2Max)
        array1Array2Max = array1[indexArray2Max]

        for i in range(len(array2)):
            if array1[i] > array1Array2Max * maxDifference and array1[i] < array1Array2Max * minDifference:
                return i, indexArray2Max
        return None, None

    def calcUearly(self, uceValues, icValues):
        uceValuesSorted, icValuesSorted = self.sortArraysByArray(uceValues, icValues)

        lower, upper = self.getDatarange(uceValuesSorted, icValuesSorted)

        if lower is None or upper is None:
            print("No Borders found, Maybe Measure Problem?")
            return "ERROR"

        if lower == upper and upper > 0:
            lower = 0

        uceValuesCutted = uceValuesSorted[lower:upper]
        icValuesCutted = icValuesSorted[lower:upper]

        uceNpArr = np.vstack([np.array(uceValuesCutted), np.ones(len(uceValuesCutted))]).T
        icNpArr = np.array(icValuesCutted)

        try:
            slope, b = np.linalg.lstsq(uceNpArr, icNpArr, rcond=None)[0]
            cutWithX = -b / slope
        except ZeroDivisionError:
            print("ERROR SLOPE DIVIDE BY ZERO")
            cutWithX = "ERROR"
        except:
            print("ERROR")
            cutWithX = "ERROR"

        return cutWithX

    def calcNd(self, ud1, id1, ud2, id2, ut):
        if np.log(id2 / id1) == 0:
            raise Exception("Division through Zero")
        return ((ud2 - ud1) / np.log(id2 / id1)) / ut

    def calcIs(self, ud, id, nd, ut):
        return np.exp(np.log(id) - ud / (ut * nd))

    def calculateNAndIs(self, ud, id, ut=0.026):
        try:
            udSorted, idSorted = self.sortArraysByArray(ud, id)
            lower, upper = self.getDatarange(udSorted, idSorted, 0.7, 1)
            udCutted = udSorted[lower:upper]
            idCutted = idSorted[lower:upper]
            nValues = []
            for i in range(int(len(udCutted) / 2)):
                nValues.append(self.calcNd(udCutted[i], idCutted[i], udCutted[int(len(udCutted) / 2) + i],
                                           idCutted[int(len(idCutted) / 2) + i], ut))
            nValuesSorted = sorted(nValues)
            index = nValues.index(nValuesSorted[int(len(nValuesSorted) / 2)])
            isValue = self.calcIs(udCutted[index], idCutted[index], nValues[index], ut)
            return nValues[index], isValue
        except Exception as ex:
            print(ex)
            return "ERROR", "ERROR"
