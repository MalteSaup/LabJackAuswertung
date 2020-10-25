from enum import Enum, unique

@unique
class MeasureMethod(Enum):
    OSZILATOR = 0
    DIODE = 1
    TRANSISTOR = 2

class LabJackU6(Enum):
    MAXVOLTAGE = 10
    USABLEPORTCOUNT = 4
