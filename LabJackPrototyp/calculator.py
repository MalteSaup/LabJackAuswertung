import numpy as np

class Calculator:
    def calcBHelper(self, icVal, ibVal):
        try:
            return icVal * 1000 / ibVal
        except:
            return-1

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

    def getDatarange(self, uce, ic, maxDifference=0.45, minDifference=0.7):
        icMax = max(ic)
        indexIcMax = ic.index(icMax)
        uceIcMax = uce[indexIcMax]

        for i in range(len(uce)):
            if uce[i] > uceIcMax * maxDifference and uce[i] < uceIcMax * minDifference:
                return i, indexIcMax
        return None, None

    def getAverage(self, arr):
        return sum(arr) / len(arr)

    def subAverageFromValues(self, arr, average):
        arrCopy = arr.copy()
        return [value - average for value in arrCopy]

    def mulArrays(self, arr1, arr2):
        return [arr1Val * arr2Val for arr1Val, arr2Val in zip(arr1, arr2)]

    def leastSquare(self, uceValues, icValues):
        uceValues, icValues = self.sortArraysByArray(uceValues, icValues)

        lower, upper = self.getDatarange(uceValues, icValues)

        if lower is None or upper is None:
            print("No Borders found, Maybe Measure Problem?")
            return "ERROR"

        if lower == upper and upper > 0:
            lower = 0

        uceValuesCutted = uceValues[lower:upper]
        icValuesCutted = icValues[lower:upper]

        uceValuesAverage = self.getAverage(uceValuesCutted)
        icValuesAverage = self.getAverage(icValuesCutted)

        uceValuesAfterSub = self.subAverageFromValues(uceValuesCutted, uceValuesAverage)
        icValuesAfterSub = self.subAverageFromValues(icValuesCutted, icValuesAverage)

        uceIcMultipliedValues = self.mulArrays(uceValuesAfterSub, icValuesAfterSub)

        quadUceValuesAfterSub = [val**2 for val in uceValuesAfterSub]

        sumMulArr = sum(uceIcMultipliedValues)
        sumQuadArr = sum(quadUceValuesAfterSub)

        try:
            slope = sumMulArr / sumQuadArr
            b = icValuesAverage - slope * uceValuesAverage
            cutWithX = -b / slope
        except ZeroDivisionError:
            print("ERROR SLOPE DIVIDE BY ZERO")
            cutWithX = "ERROR"
        except:
            print("ERROR")
            cutWithX = "ERROR"

        return cutWithX

    def calcNd(self, ud1, id1, ud2, id2, ut):
        return ((ud2 - ud1) / np.log(id2 / id1)) / ut

    def calcIs(self, ud, id, nd, ut):
        return np.exp(np.log(id) - ud / (ut * nd))

    def calculateNAndIs(self, ud, id, ut=0.026):
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
        isValue = self.calcIs(udCutted[index], idCutted[index], nValues[index], ud)
        return nValues[index], isValue
