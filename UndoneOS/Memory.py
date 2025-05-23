#Memory
#Talmage Gaisford

from LogType import LogType

class Memory:
    def __init__(self, spec, system):
        self.system = system
        self.spec = spec
        self.mainMemory = [[0 for x in range(self.spec.instructionSize)] for y in range(self.system.spec.memoryLength)] 
        self.modeBit = True
        
        # self.totalFrames = self.spec.instructionSize // self.spec.pageSize
        # self.frameMemory = [None] * self.totalFrames
        # self.frameUsage = []
        
    def checkFrameFreedom(self, frame):
        if all(x == 0 for x in self.mainMemory[frame]):
            freeFrame = True
            for j in range(frame, frame + self.spec.pageSize):
                if j >= len(self.mainMemory):
                    freeFrame = False
                if not all(val == 0 for val in self.mainMemory[j]):
                    freeFrame = False
            return freeFrame
        return False

    def getFreeFrame(self):
        for i in range(0,len(self.mainMemory),self.spec.pageSize):
            if self.checkFrameFreedom(i):
                return i
        return None
        # for i in range(0,len(self.mainMemory),self.spec.pageSize):
        #     # if all(x == 0 for x in self.mainMemory[i]):
        #     for j in range(i, i + self.spec.pageSize):
        #         if j >= len(self.mainMemory):
        #             break
        #         if not all(val == 0 for val in self.mainMemory[j]):
        #             break
        #         return i, None

        # lruFrame = self.frameUsage.pop(0)
        # evictedPage = self.frameMemory[lruFrame]
        # self.frameUsage.append(lruFrame)
        # return lruFrame, evictedPage

    def loadPage(self, pageData, frameNumber):
        if len(pageData) != self.spec.pageSize:
            self.log(LogType.ERROR,"a program is trying to load a page with incorrect size")
        # if self.checkFrameFreedom(frameNumber):
        loadLineIncrementer = 0
        for instruction in pageData:
            self.instructionIntoMemory(instruction, (frameNumber + loadLineIncrementer))
            loadLineIncrementer += 1
        # else:
        #     self.log(LogType.ERROR,"a program is trying to load a page into unfree memory")


    def log(self,logType,logString):
        self.system.logger.log(logType,"memory",logString)

    # def touchFrame(self, frameNumber):
    #     if frameNumber in self.frameUsage:
    #         self.frameUsage.remove(frameNumber)
    #     self.frameUsage.append(frameNumber)

    # def getInstructionFromFrame(self, frameNumber, offset):
    #     return self.frameMemory[frameNumber[offset]]

    # def __repr__(self):
    #     return f"Memory: {self.frameMemory}"
    
    def programIntoMemory(self, program, programBytes):
        loadLineIncrementer = 0
        for i in range(0, len(programBytes), self.spec.instructionSize):
            instruction = programBytes[i:i + self.spec.instructionSize]
            self.instructionIntoMemory(instruction, (program.programLoadLocation + loadLineIncrementer))
            loadLineIncrementer += 1

    def instructionIntoMemory(self, instruction, row):
        columnIndexer = 0
        for byte in instruction:
            self.mainMemory[row][columnIndexer] = byte
            columnIndexer += 1

    def getInstruction(self, instructionPointer):
        return self.mainMemory[instructionPointer]
    
    def checkAvailability(self, newProgram):
        # for program in self.system.readyQueue:
        #     if ((newProgram.programLoadLocation >= program.programLoadLocation and newProgram.programLoadLocation <= program.programEndLocation) or 
        #     (newProgram.programEndLocation >= program.programLoadLocation and newProgram.programEndLocation <= program.programEndLocation)):
        #         newProgram.logger.logError("Segmentation Fault at location: " + str(newProgram.programLoadLocation))
        #         program.logger.logError("Segmentation Fault at location: " + str(newProgram.programLoadLocation))
        #         return False
        if (newProgram.programEndLocation >= self.spec.memoryLength):
            newProgram.logger.logError("Segmentation Fault at location: " + str(newProgram.programLoadLocation))
            newProgram.logger.logError("Program exceeds memory capacity")
            return False
        return True
    
    def isAllZero(self, lst):
        return all(x == 0 for x in lst)

    def summarizeRanges(self, statusList):
        ranges = []
        if not statusList:
            return ranges

        start = statusList[0][0]
        currentType = statusList[0][1]

        for i in range(1, len(statusList)):
            idx, isZero = statusList[i]
            if isZero != currentType or idx != statusList[i - 1][0] + 1:
                end = statusList[i - 1][0]
                ranges.append((start, end, currentType))
                start = idx
                currentType = isZero

        ranges.append((start, statusList[-1][0], currentType))
        return ranges

    def processList(self, mainList):
        status = [(i, self.isAllZero(sublist)) for i, sublist in enumerate(mainList)]
        ranges = self.summarizeRanges(status)

        print("Memory Summary:")
        for start, end, isZero in ranges:
            kind = "empty" if isZero else "full"
            if start == end:
                print(f"Index {start} {kind}")
            else:
                print(f"Indices {start}-{end} {kind}")

        print("\nMemory By Index:")
        for i, sublist in enumerate(mainList):
            if not self.isAllZero(sublist):
                print(f"Index {i}: {sublist}")