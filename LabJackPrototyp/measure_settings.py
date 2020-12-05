from helper import MeasureMethod


class MeasureSettings:
    def __init__(self, r1=100000, r2=200, ubeMax=1.0, uceMax=12, measurePorts=None, idPort=0, udPort=1,
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
        self.ubeMax = ubeMax
        self.uceMax = uceMax
        self.measurePorts = measurePorts
        self.udPort = udPort
        self.idPort = idPort
        self.udMax = udMax
        self.idMax = idMax
        self.measureMethod = measureMethod

    def toString(self):
        return "R1: " + str(self.r1) + " R2: " + str(self.r2) + " UBE Max: " + str(
            self.ubeMax) + " UCE Max: " + str(self.uceMax) + " Measure Ports: " + str(
            self.measurePorts) + " idPort: " + str(self.idPort) + " udPort: " + str(self.udPort) + " udMax: " + str(self.udMax) + " idMax: " + str(
            self.idMax) + " measureMethod: " + str(self.measureMethod)
