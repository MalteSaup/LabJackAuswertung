

class Calculator:
    def calcB(self, ic, ib):
        ib, ic = self.sortArrayByArray(ib, ic)
        try:
            bArray = [icVal * 1000 / ibVal for icVal, ibVal in zip(ic, ib[int(len(ib)*0.1):])]
            bArray = sorted(bArray)
            return bArray[int(len(bArray) / 2)]
        except:
            print("DIVIDED BY ZERO")
            return 0

    def sortArrayByArray(self, arrSortedAfter, arr2):
        arrZip = zip(arrSortedAfter, arr2)
        sortedZip = sorted(arrZip)
        aSAZip, arr2Zip = zip(*sortedZip)
        return list(aSAZip), list(arr2Zip)

    def getBorders(self, aSA, arr2):
        icMax = max(arr2)
        indexIcMax = arr2.index(icMax)
        uceIcMax = aSA[indexIcMax]
        uceIcLower = uceIcMax * 0.5
        for i in range(len(aSA)):
            if aSA[i] > uceIcLower - 0.02 and arr2[i] < uceIcLower + 0.1:
                return i, indexIcMax
        return None, None

    def getAverage(self, arr):
        return sum(arr) / len(arr)

    def subAverageFromValues(self, arr, average):
        arrCopy = arr.copy()
        return [value - average for value in arrCopy]

    def mulArrays(self, arr1, arr2):
        return [arr1Val * arr2Val for arr1Val, arr2Val in zip(arr1, arr2)]

    def leastSquare(self, arrSortedAfter, arr2, borders=None):
        arrSortedAfter, arr2 = self.sortArrayByArray(arrSortedAfter, arr2)

        if borders is None:
            lower, upper = self.getBorders(arrSortedAfter, arr2)
            if lower == upper and upper > 0:
                lower = 0
        else:
            try:
                lower = borders[0]
                upper = borders[0]
            except:
                print("Not Enough Values Passed")
                return None, None

        if lower is None or upper is None:
            print("No Borders found")
            return None, None

        aSACutted = arrSortedAfter[lower:upper]
        arr2Cutted = arr2[lower:upper]

        aSAAverage = self.getAverage(aSACutted)
        arr2Average = self.getAverage(arr2Cutted)

        aSAAfterSub = self.subAverageFromValues(aSACutted, aSAAverage)
        arr2AfterSub = self.subAverageFromValues(arr2Cutted, arr2Average)

        mulArr = self.mulArrays(aSAAfterSub, arr2AfterSub)

        quadASAAfterSub = [val**2 for val in aSAAfterSub]

        sumMulArr = sum(mulArr)
        sumQuadArr = sum(quadASAAfterSub)

        try:
            slope = sumMulArr / sumQuadArr
        except ZeroDivisionError:
            print("ERROR SLOPE DIVIDE BY ZERO")
            slope = "ERROR"


        try:
            b = arr2Average - slope * aSAAverage
            cutWithX = -b/slope
        except ZeroDivisionError:
            print("ERROR SLOPE DIVIDE BY ZERO")
            cutWithX = "ERROR"
        except TypeError:
            b = "ERROR"
            cutWithX = "ERROR"

        return cutWithX, b
