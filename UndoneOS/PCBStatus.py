#PCBStatus
#Talmage Gaisford

from enum import Enum

class PCBStatus(Enum):
    NEW = 1
    READY = 2
    RUNNING = 3
    WAITING = 4
    TERMINATED = 5
    FAILED = 6