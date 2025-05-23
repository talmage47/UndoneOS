from VMOperator import VMOperator, SWIOperator
from PCBStatus import PCBStatus
from LogType import LogType
from PageTable import PageTable
from PageTable import PageTableEntry
import random
import time

class PCB:
    
    def __init__(self, system, programPath, queue, loadTime, sharedMemory):
        self.system = system
        self.programByteSize = 0
        self.programLineSize = 0
        self.programLoadLocation = 0
        self.programEndLocation = 0
        self.instructionPointer = int(self.programLoadLocation)
        self.programPath = programPath
        self.loadTime = loadTime
        self.status = PCBStatus.NEW
        self.burstCompletionRecord = 0.8
        self.queue = queue
        self.registerArchive = []
        self.children = []
        self.sharedMemory = sharedMemory
        self.pageTable = PageTable(self, self.system.spec.pageSize,self.system.spec.pageCount,self.system.memory)
        
        self.programData = []
        with open(self.programPath, 'rb') as openedProgram:
            programBytes = openedProgram.read()
        self.programByteSize = int.from_bytes(programBytes[:3], byteorder = 'little')
        self.programLineSize = self.programByteSize/self.system.spec.instructionSize
        self.programEndLocation = int(self.programLoadLocation + self.programLineSize)

        #splice program to remove non-instructions
        programBytes = programBytes[(self.system.spec.instructionSize * 2):]

        for i in range(0, len(programBytes), self.system.spec.instructionSize):
            instruction = programBytes[i:i + self.system.spec.instructionSize]
            self.programData.append(instruction)

    def fork(self):
        self.system.fork(self,"child.osx")

    def finish(self):
        if not self.children:
            self.status = PCBStatus.TERMINATED
            self.log(LogType.LOG, str(self.programPath) + " terminated")
            self.log(LogType.LOG,"PCB status set to TERMINATED")
        else:
            for child in self.children:
                if child.status != PCBStatus.TERMINATED:
                    self.log(LogType.ERROR,"IMPOSSIBLE: " + self.programPath + " tried to terminate with live children")
                    return
            self.status = PCBStatus.TERMINATED
            self.log(LogType.LOG, str(self.programPath) + " terminated")
            self.log(LogType.LOG,"PCB status set to TERMINATED")

    def getBurstCompletion(self):
        return self.burstCompletionRecord
    
    def getNextPage(self):
        return self.programData[self.instructionPointer:self.instructionPointer + self.system.spec.pageSize]

    def log(self,logType,logString):
        self.system.logger.log(logType,self.programPath,logString)

    def resetBurstCompletion(self):
        self.burstCompletionRecord = 0.8

    def sendPageToMemory(self, pageNumber, frameNumber):
        pageData = []
        firstLineOfPage = pageNumber * self.system.spec.pageSize
        for offset in range(self.system.spec.pageSize):
            if firstLineOfPage + offset < len(self.programData):
                pageData.append(self.programData[firstLineOfPage + offset])
        self.system.memory.loadPage(pageData, frameNumber)

    def startProgram(self):
        self.instructionPointer = self.programLoadLocation
        for i in range(self.programLoadLocation, self.programEndLocation):  
            self.step()
        self.instructionPointer = self.programLoadLocation

    def initialLoad(self):
        loads = 0
        for pageNumber in range(self.system.spec.pageCount):
            memoryFrame = self.system.memory.getFreeFrame()
            if memoryFrame is not None:
                self.pageTable.addEntry(pageNumber,memoryFrame)
                loads += 1
        if loads == self.system.spec.pageCount:
            self.status = PCBStatus.READY
            return True
        elif loads > 0:
            self.status = PCBStatus.READY
            self.log(LogType.ERROR, "initial load was partially completed")
            return True
        else:
            self.status = PCBStatus.FAILED
            self.log(LogType.ERROR,"Unable to load program at location: " + str(self.programLoadLocation))
            return False



        # if self.system.memory.checkAvailability(self):
        #     self.system.memory.programIntoMemory(self,programBytes)
        #     self.status = PCBStatus.READY
        #     self.log(LogType.LOG, str(self.programPath) + " initialized")
        #     self.log(LogType.LOG,"PCB status set to READY")
        #     return True
        # else:
        #     self.log(LogType.ERRUR,"Unable to load program at location: " + str(self.programLoadLocation))
        #     self.status = PCBStatus.FAILED
        #     self.log(LogType.LOG,"PCB status set to FAILED")
        #     return False
        
    def updateBurstCompletion(self,completion):
        self.burstCompletionRecord = 0.8 * self.burstCompletionRecord + 0.2 * completion

    def waitingCheck(self):
        for pcb in self.children:
            if pcb.status != PCBStatus.TERMINATED:
                return False
        return True


# MARK: VMOperators
    def step(self):
        self.status = PCBStatus.RUNNING
        self.log(LogType.LOG,"PCB status set to RUNNING")
        runStartTime = time.time() - self.system.startTime
        if self.instructionPointer >= self.programEndLocation:
            self.log(LogType.LOG,"Program Pointer Causing Program to Finish")
            self.finish()
            return
        frameNumber, offset = self.pageTable.lookup(self.instructionPointer)
        memoryLocation = frameNumber + offset
        currentInstruction = self.system.memory.getInstruction(memoryLocation)
        match currentInstruction[0]:
            
            #Arithmetic
            case VMOperator.ADD:
                self.system.registers[currentInstruction[1]] = self.system.registers[currentInstruction[2]] + self.system.registers[currentInstruction[3]]
                self.log(LogType.LOGSTEP,'ADDITION: reg' + str(currentInstruction[1]) + ' = reg' + str(currentInstruction[2]) + ' + reg' + str(currentInstruction[3]))
            case VMOperator.SUB:
                self.system.registers[currentInstruction[1]] = self.system.registers[currentInstruction[2]] - self.system.registers[currentInstruction[3]]
                self.log(LogType.LOGSTEP,'SUBTRACTION: reg' + str(currentInstruction[1]) + ' = reg' + str(currentInstruction[2]) + ' - reg' + str(currentInstruction[3]))
            case VMOperator.MUL:
                self.system.registers[currentInstruction[1]] = self.system.registers[currentInstruction[2]] * self.system.registers[currentInstruction[3]]
                self.log(LogType.LOGSTEP,'MULTIPLICATION: reg' + str(currentInstruction[1]) + ' = reg' + str(currentInstruction[2]) + ' * reg' + str(currentInstruction[3]))
            case VMOperator.DIV:
                self.system.registers[currentInstruction[1]] = self.system.registers[currentInstruction[2]] // self.system.registers[currentInstruction[3]]
                self.log(LogType.LOGSTEP,'DIVISION: reg' + str(currentInstruction[1]) + ' = reg' + str(currentInstruction[2]) + ' / reg' + str(currentInstruction[3]))                
            
            #Move data
            case VMOperator.MOV:
                self.system.registers[currentInstruction[1]] = self.system.registers[currentInstruction[2]]
                self.log(LogType.LOGSTEP,' MOV: reg' + str(currentInstruction[1]) + ' = reg' + str(currentInstruction[2]))
            case VMOperator.MVI:
                self.system.registers[currentInstruction[1]] = currentInstruction[2]
                self.log(LogType.LOGSTEP,"MVI: reg " + str(currentInstruction[1]) + " = " + str(currentInstruction[2]))
            case VMOperator.STR:
                self.log(LogType.ERROR,"STR is not yet implemented")
            case VMOperator.STRB:
                self.log(LogType.ERROR,"STRB is not yet implemented")
            case VMOperator.LDR:
                self.log(LogType.ERROR,"LDR is not yet implemented")
            case VMOperator.LDRB:
                self.log(LogType.ERROR,"LDRB is not yet implemented")
            
            #Branch
            case VMOperator.B:
                self.log(LogType.ERROR,"B is not yet implemented")
            case VMOperator.BL:
                self.log(LogType.ERROR,"BL is not yet implemented")
            case VMOperator.BX:
                self.log(LogType.ERROR,"BX is not yet implemented")
            case VMOperator.BNE:
                self.log(LogType.ERROR,"BNE is not yet implemented")
            case VMOperator.BGT:
                self.log(LogType.ERROR,"BGT is not yet implemented")
            case VMOperator.BLT:
                self.log(LogType.ERROR,"BLT is not yet implemented")
            case VMOperator.BEQ:
                self.log(LogType.ERROR,"BEQ is not yet implemented")

             #Logical
            case VMOperator.CMP:
                self.log(LogType.ERROR,"CMP is not yet implemented")
            case VMOperator.AND:
                self.log(LogType.ERROR,"AND is not yet implemented")
            case VMOperator.ORR:
                self.log(LogType.ERROR,"ORR is not yet implemented")
            case VMOperator.EOR:
                self.log(LogType.ERROR,"EOR is not yet implemented")

            #Interrupts
            case VMOperator.SWI:
                self.status = PCBStatus.WAITING
                runStopTime = time.time() - self.system.startTime
                self.system.dataFacilitator.addRealTimeData(self,self.queue,runStartTime,runStopTime)
                return
            case _:
                self.log(LogType.ERROR,"Unknown Operator Error: " + str(currentInstruction[0]))

        self.instructionPointer += 1
        self.status = PCBStatus.READY
        self.log(LogType.LOG,"PCB status set to READY")
        self.system.tickClock()
        runStopTime = time.time() - self.system.startTime
        
        #self.system.dataFacilitator.addData(self,self.queue,self.system.clock.getTime())
        self.system.dataFacilitator.addRealTimeData(self,self.queue,runStartTime,runStopTime)

    def stepIO(self):
        operationSuccess = True
        if self.instructionPointer >= self.programEndLocation:
            self.finish()
            return
        frameNumber, offset = self.pageTable.lookup(self.instructionPointer)
        memoryLocation = frameNumber + offset
        currentInstruction = self.system.memory.getInstruction(memoryLocation)
        self.system.memory.modeBit = False
        self.log(LogType.LOG,"kernel mode enabled")
        match currentInstruction[1]:
    
            case SWIOperator.PRINT:                      
                print("register 0 = " + str(self.system.registers[0]))
                self.log(LogType.LOG,"printed register 0 " + str(self.system.registers[0]))
            case SWIOperator.FORK:
                self.log(LogType.LOG,"forking to child program")
                self.fork()
            case SWIOperator.SHAREDPUSH:
                try:
                    if not self.sharedMemory.isFull():
                        self.sharedMemory.put(self.system.registers[0])
                        self.log(LogType.LOG, str(self.system.registers[0]) + " put into shared memory buffer")
                    else:
                        operationSuccess = False
                        self.log(LogType.ERROR, "shared memory is full. cannot push to buffer")
                except AttributeError:
                    self.log(LogType.ERROR, "shared memory was not initialized")
            case SWIOperator.SHAREDPULL:
                try:
                    if not self.sharedMemory.isEmpty():
                        self.system.registers[0] = self.sharedMemory.get()
                        self.log(LogType.LOG, str(self.system.registers[0]) + " pulled from shared memory buffer")
                    else:
                        operationSuccess = False
                        self.log(LogType.ERROR, "shared memory is empty. cannot pull from buffer")
                except AttributeError:
                    self.log(LogType.ERROR, "shared memory was not initialized")
            case _:
                self.log(LogType.ERROR,"Error: Unknown SWI Operator")

        self.system.memory.modeBit = True
        self.log(LogType.LOG,"kernel mode disabled")
        if operationSuccess:
            self.instructionPointer += 1
        self.status = PCBStatus.READY
        self.log(LogType.LOG,"PCB status set to READY")
        #self.system.tickClock(random.randint(1,8))
