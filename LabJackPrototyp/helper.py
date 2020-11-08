from enum import Enum, unique

@unique
class MeasureMethod(Enum):
    OSZILATOR = 0
    DIODE = 1
    TRANSISTOR = 2

class LabJackU6(Enum):
    MAXVOLTAGE = 10
    USABLEPORTCOUNT = 4
    MINCHANNELREAD = USABLEPORTCOUNT * 2 * 2      #Ports needs two channels to read properly the voltage and this needs to be doubled to be read properly from the LabJack U6

