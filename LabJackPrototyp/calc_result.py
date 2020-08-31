class CalcResult:
    def __init__(self, measureSerie, uearly, b, measurePointCount):
        if type(uearly) == str:
            self.uearly = uearly
        else:
            self.uearly = round(uearly, 3)
        if type(b) == str:
            self.b = b
        else:
            self.b = round(b, 3)
        self.measurePointCount = measurePointCount
        self.measureSerie = measureSerie