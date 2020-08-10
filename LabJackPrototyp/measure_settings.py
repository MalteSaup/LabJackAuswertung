class MeasureSettings:
    def __init__(self, r1=100000, r2=200, ubeMin=0, ubeMax=1.0, uceMin=0, uceMax=12, measurePorts=None, xAxisPort=1):
        if measurePorts is None:
            measurePorts = [1, 3, 2, 0]
        self.r1 = r1
        self.r2 = r2
        self.ubeMin = ubeMin
        self.ubeMax = ubeMax
        self.uceMin = uceMin
        self.uceMax = uceMax
        self.measurePorts = measurePorts
        self.xAxisPort = xAxisPort

    def toString(self):
        return "R1: " + str(self.r1) + " R2: " + str(self.r2) + " UBE Min: " + str(self.ubeMin) + " UBE Max: " + str(
            self.ubeMax) + " UCE Min: " + str(self.uceMin) + " UCE Max: " + str(self.uceMax) + " Measure Ports: " + str(
            self.measurePorts + " XAxisPort: " + str(self.xAxisPort))
