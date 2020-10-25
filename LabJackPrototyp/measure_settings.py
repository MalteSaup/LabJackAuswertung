from helper import MeasureMethod


class MeasureSettings:
    def __init__(self, r1=100000, r2=200, ubeMin=0, ubeMax=1.0, uceMin=0, uceMax=12, measurePorts=None, udPort=0,
                 udMax=1, idMax=10, measureMethod=MeasureMethod.TRANSISTOR):
        if measurePorts is None:
            measurePorts = [1, 3, 2, 0]
        if measureMethod == MeasureMethod.DIODE:
            if r1 == 100000:
                r1 = 10000
            if r2 == 200:
                r2 = 1000
        self.r1 = r1
        self.r2 = r2
        self.ubeMin = ubeMin
        self.ubeMax = ubeMax
        self.uceMin = uceMin
        self.uceMax = uceMax
        self.measurePorts = measurePorts
        self.udPort = udPort
        self.udMax = udMax
        self.idMax = idMax
        self.measureMethod = measureMethod

    def toString(self):
        return "R1: " + str(self.r1) + " R2: " + str(self.r2) + " UBE Min: " + str(self.ubeMin) + " UBE Max: " + str(
            self.ubeMax) + " UCE Min: " + str(self.uceMin) + " UCE Max: " + str(self.uceMax) + " Measure Ports: " + str(
            self.measurePorts + " udPort: " + str(self.udPort)) + " udMax: " + str(self.udMax) + " idMax: " + str(
            self.idMax) + " measureMethod: " + str(self.measureMethod)
