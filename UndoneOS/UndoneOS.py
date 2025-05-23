#!/usr/bin/env python3
#UndoneOS
#Talmage Gaisford

from Clock import Clock
from DataFacilitator import DataFacilitator
from Logger import Logger
from LogType import LogType
from MachineSpec import MachineSpec
from Memory import Memory
from PCB import PCB
from PCBStatus import PCBStatus
from OSSchedules import OSSchedules
from Queue import Queue
from QueueController import QueueController
from SharedMemory import SharedMemory
import time

class UndoneOS:
    
    def __init__(self, spec = MachineSpec()): #, shellSwitch = True):
        self.spec = spec
        #self.shell = UndoneShell(self)
        self.logger = Logger(self)
        self.memory = Memory(spec, self)
        self.registers = [0]*self.spec.registerCount
        self.clock = Clock(self)
        self.schedule = self.spec.schedule
        self.isVerbose = False
        
        self.queueController = QueueController(self)
        self.jobQueue = Queue()
        self.fcfsQueue = Queue()
        self.ioQueue = Queue()
        self.readyQueue1 = Queue(self.spec.quantum1)
        self.readyQueue2 = Queue(self.spec.quantum2)
        
        self.programs = {}
        self.failedPrograms = {}
        
        #self.shellSwitch = shellSwitch
        self.dataFacilitator = DataFacilitator(self)
        self.startTime = time.time()
        
        # if self.shellSwitch:
        #     self.shell.runShell()

        
    def addProgram(self, programPath, loadTime,sharedMemoryObject):
        pcb = PCB(self,programPath,self.getInitialQueue(),loadTime,sharedMemoryObject)
        self.jobQueue.append(pcb)

    def createSharedMemoryObject(self,sharedMemoryCommand):
        if sharedMemoryCommand is None:
            return None
        sharedMemoryCommand = sharedMemoryCommand[0]
        if not sharedMemoryCommand.startswith("shm_open(") or not sharedMemoryCommand.endswith(")"):
            raise ValueError("Invalid shm_open syntax")

        argumentString = sharedMemoryCommand[len("shm_open("):-1]
        arguments = [arg.strip() for arg in argumentString.split(",")]
        if len(arguments) != 3:
            raise ValueError("shm_open must have exactly 3 arguments")
        name = arguments[0]
        mode = arguments[1]
        try:
            size = int(arguments[2])
        except ValueError:
            raise ValueError("Size must be an integer")

        return SharedMemory(name,mode,size)

    def detectRunStatus(self):
        if (not self.jobQueue.hasItems() 
            and not self.readyQueue1.hasItems() 
            and not self.readyQueue2.hasItems() 
            and not self.fcfsQueue.hasItems() 
            and not self.ioQueue.hasItems()):
            return False
        return True

    def loadPrograms(self, programList,sharedMemoryCommand):
        self.dataFacilitator.resetGantt()
        sortedPrograms = sorted(programList, key = lambda x: x[1])
        sharedMemoryObject = self.createSharedMemoryObject(sharedMemoryCommand)
        for programData in sortedPrograms:
            self.addProgram(programData[0],programData[1],sharedMemoryObject)
        try:
            while self.jobQueue.getFirst().loadTime <= self.clock.getTime():
                self.readyProgram(self.jobQueue.pull())
        except IndexError:
            pass

    def fork(self,parentPCB,childPath):
        childPCB = PCB(self,childPath,self.fcfsQueue,0)
        parentPCB.children.append(childPCB)
        parentPCB.status = PCBStatus.WAITING
        self.readyProgram(childPCB)

    def getInitialQueue(self):
        if self.schedule == OSSchedules.FCFS:
            return self.fcfsQueue
        else:
            return self.readyQueue1

    def getSchedule(self):
        return self.schedule

    def log(self,logType,logString):
        self.logger.log(logType,"UndoneOS",logString)

    def outputPageFaults(self):
        print("Page Fault Count = " + str(self.dataFacilitator.pageFaults))

    def psDump(self):
        self.memory.processList(self.memory.mainMemory)

    def readyProgram(self,pcb):
        if pcb.initialLoad():
            self.programs.update({
                pcb.programPath : pcb
            })
            self.getInitialQueue().append(pcb)
        else:
            self.failedPrograms.update({
                pcb.programPath : pcb
            })

    def runLoop(self):
        while self.detectRunStatus():
            if self.jobQueue.hasItems():
                try:
                    while self.jobQueue.getFirst().loadTime <= self.clock.getTime():
                        self.readyProgram(self.jobQueue.pull())
                except IndexError:
                    pass
            if self.ioQueue.hasItems():
                self.queueController.kickIO()
            elif (self.readyQueue1.hasItems() 
                  or self.readyQueue2.hasItems() 
                  or self.fcfsQueue.hasItems()):
                self.queueController.kick()

    def runPrograms(self):
        self.log(LogType.LOG, "run loop initiated")
        self.runLoop()

    def setPageCount(self,number):
        self.spec.pageCount = int(number)
        self.log(LogType.LOG, "page number set to " + str(number))

    def setPageSize(self,number):
        self.spec.pageSize = int(number)
        self.log(LogType.LOG, "page size set to " + str(number))

    def setRR(self,quantum1,quantum2):
        self.readyQueue1.quantum = int(quantum1)
        self.readyQueue2.quantum = int(quantum2)
        self.log(LogType.LOG, "first queue set to " + str(quantum1))
        self.log(LogType.LOG, "second queue set to " + str(quantum2))

    def setSchedule(self,scheduleString):
        match scheduleString:
            case "RR":
                self.schedule = OSSchedules.RR
            case "FCFS":
                self.schedule = OSSchedules.FCFS
            case "MFQ":
                self.schedule = OSSchedules.MFQ
        self.log(LogType.LOG, "schedule set to " + scheduleString)

    def setVerbose(self,isVerbose):
        self.isVerbose = isVerbose

    def tickClock(self, increment = 1):
        self.clock.tick(increment)

    def waitingQueueCheck(self):
        for pcb in self.ioQueue:
            if pcb.waitingCheck():
                pcb.status = PCBStatus.READY
                self.readyQueue.append(pcb)
                self.ioQueue.remove(pcb)
                return
        return
