#MachineSpec
#Talmage Gaisford

from OSSchedules import OSSchedules

class MachineSpec:
    def __init__(self, quantum1 = 10, quantum2 = 50, schedule = OSSchedules.RR, pageSize = 4, pageCount = 3, memoryLength = 1000, registerCount = 12, instructionSize = 6):
        self.instructionSize = instructionSize
        self.memoryLength = memoryLength
        self.registerCount = registerCount
        self.programLoadLocationIndex = self.instructionSize + 2
        self.quantum1 = quantum1
        self.quantum2 = quantum2
        self.schedule = schedule
        self.pageSize = pageSize
        self.pageCount = pageCount