#QueueController
#Talmage Gaisford

from LogType import LogType
from OSSchedules import OSSchedules
from PCBStatus import PCBStatus

class QueueController:
    def __init__(self,system, lowerQueueBound = 0.6, upperQueueBound = 0.92, quantumQuantum = 10):
        self.system = system
        self.lowerQueueBound = lowerQueueBound
        self.upperQueueBound = upperQueueBound
        self.quantumQuantum = quantumQuantum

    def kick(self):
        match self.system.getSchedule():
            case OSSchedules.FCFS:
                if self.system.fcfsQueue.hasItems():
                    self.loopFCFS(self.system.fcfsQueue)
                else:
                    self.log(LogType.ERROR,"queue controller kicked with empty FCFS queue")
            case OSSchedules.RR:
                if self.system.readyQueue1.hasItems():
                    self.loopRR(self.system.readyQueue1)
                else:
                    self.log(LogType.ERROR,"queue controller kicked with empty ready1 queue")
            case OSSchedules.MFQ:
                if (self.system.readyQueue1.hasItems() 
                    or self.system.readyQueue2.hasItems() 
                    or self.system.fcfsQueue.hasItems()):
                    self.loopMFQ(self.system.readyQueue1,self.system.readyQueue2,self.system.fcfsQueue)
                else:
                    self.log(LogType.ERROR,"queue controller kicked with empty ready queues")
            case _:
                self.log(LogType.ERROR,"Unknown schedule")
        self.system.clock.tick()

    def kickIO(self):
        if self.system.ioQueue.hasItems():
            currentPCB = self.system.ioQueue.pull()
            if currentPCB.status != PCBStatus.WAITING:
                self.log(LogType.ERROR,"non-waiting PCB in the IO queue")
            if currentPCB.registerArchive:
                self.system.registers = list(currentPCB.registerArchive)
            currentPCB.stepIO()
            currentPCB.registerArchive = list(self.system.registers)
            if currentPCB.status == PCBStatus.READY:
                pcbQueue = currentPCB.queue
                pcbQueue.append(currentPCB)
            elif currentPCB.status == PCBStatus.WAITING:
                self.system.ioQueue.append(currentPCB)
            elif not currentPCB.status == PCBStatus.TERMINATED:
                self.log(LogType.ERROR,"unexpected PCB status")
        else:
            self.log(LogType.ERROR,"queue controller received IO kick with empty IO queue")

    def log(self,logType,logString):
        self.system.logger.log(logType,logString)

    def loopFCFS(self,fcfsQueue):
        if fcfsQueue.hasItems():
            currentPCB = fcfsQueue.pull()
            if currentPCB.status != PCBStatus.READY:
                self.log(LogType.ERROR,"unready PCB in the FCFS queue")
            if currentPCB.registerArchive:
                self.system.registers = currentPCB.registerArchive
            while currentPCB.status != PCBStatus.TERMINATED:
                currentPCB.step()
                if currentPCB.status == PCBStatus.WAITING:
                    currentPCB.stepIO()
                if currentPCB.status not in [PCBStatus.WAITING,PCBStatus.READY]:
                    self.log(LogType.ERROR,"unexpected PCB status")
            if not currentPCB.status == PCBStatus.TERMINATED:
                self.log(LogType.ERROR,"unexpected PCB status")

    def loopMFQ(self,readyQueue1,readyQueue2,fcfsQueue):
        for _ in range(self.quantumQuantum):
            pcb1 = self.loopRR(readyQueue1)
            if pcb1:
                self.queueAdjustment(pcb1,readyQueue1,readyQueue2,fcfsQueue)
            pcb2 = self.loopRR(readyQueue2)
            if pcb2:
                self.queueAdjustment(pcb2,readyQueue1,readyQueue2,fcfsQueue)
        self.loopFCFS(fcfsQueue)

    def loopRR(self,rrQueue):
        if rrQueue.hasItems():
            currentPCB = rrQueue.pull()
            if currentPCB.status != PCBStatus.READY:
                self.log(LogType.ERROR,"unready PCB in the ready queue")
            if currentPCB.registerArchive:
                self.system.registers = list(currentPCB.registerArchive)
            for i in range(rrQueue.quantum):
                if currentPCB.status == PCBStatus.READY:
                    currentPCB.step()
                else:
                    break
            currentPCB.registerArchive = list(self.system.registers)
            if currentPCB.status == PCBStatus.READY:
                currentPCB.updateBurstCompletion(0)
                rrQueue.append(currentPCB)
                return currentPCB
            elif currentPCB.status == PCBStatus.WAITING:
                currentPCB.updateBurstCompletion(1)
                self.system.ioQueue.append(currentPCB)
                return currentPCB
            elif not currentPCB.status == PCBStatus.TERMINATED:
                self.log(LogType.ERROR,"unexpected PCB status")

    def queueAdjustment(self,pcb,readyQueue1,readyQueue2,fcfsQueue):
        if pcb.getBurstCompletion() < self.lowerQueueBound:
            if pcb.queue == readyQueue1:
                if readyQueue1.contains(pcb):
                    readyQueue1.remove(pcb)
                    readyQueue2.append(pcb)
                pcb.queue = readyQueue2
                self.log(LogType.LOG, pcb.programPath + " success rate =  " + str(pcb.burstCompletionRecord))
                self.log(LogType.LOG, pcb.programPath + " moved to queue " + str(readyQueue2.quantum))
            elif pcb.queue == readyQueue2:
                if readyQueue2.contains(pcb):
                    readyQueue2.remove(pcb)
                    fcfsQueue.append(pcb)
                pcb.queue = fcfsQueue
                self.log(LogType.LOG, pcb.programPath + " success rate =  " + str(pcb.burstCompletionRecord))
                self.log(LogType.LOG, pcb.programPath + " moved to fcfs queue")
            pcb.resetBurstCompletion()
        elif pcb.getBurstCompletion() > self.upperQueueBound:
            if pcb.queue == readyQueue2:
                if readyQueue2.contains(pcb):
                    readyQueue2.remove(pcb)
                    readyQueue1.append(pcb)
                pcb.queue = readyQueue1
                self.log(LogType.LOG, pcb.programPath + " success rate =  " + str(pcb.burstCompletionRecord))
                self.log(LogType.LOG, pcb.programPath + " moved to queue " + str(readyQueue1.quantum))
            pcb.resetBurstCompletion()



# def queueAdjustment(self,pcb):
#     if pcb.getBurstCompletion() < self.lowerQueueBound:
#         if pcb.queue == self.system.readyQueue1:
#             self.system.readyQueue1.remove(pcb)
#             self.system.readyQueue2.append(pcb)
#             pcb.queue = self.system.readyQueue2
#         if pcb.queue == self.system.readyQueue2:
#             self.system.readyQueue2.remove(pcb)
#             self.system.fcfsQueue.append(pcb)
#             pcb.queue = self.system.fcfsQueue
#     elif pcb.getBurstCompletion() > self.upperQueueBound:
#         if pcb.queue == self.system.readyQueue2:
#             self.system.readyQueue2.remove(pcb)
#             self.system.readyQueue1.append(pcb)
#             pcb.queue = self.system.readyQueue1
            
# def improvedLoopFCFS(self,fcfsQueue):
#     if self.system.fcfsQueue:
#         currentPCB = fcfsQueue.pull()
#         if currentPCB.status != PCBStatus.READY:
#             self.log(LogType.ERROR,"unready PCB in the FCFS queue")
#         if currentPCB.registerArchive:
#             self.system.registers = currentPCB.registerArchive
#         while currentPCB.status == PCBStatus.READY:
#             currentPCB.step()
#         currentPCB.registerArchive = self.system.registers
#         if currentPCB.status == PCBStatus.READY:
#             fcfsQueue.append(currentPCB)
#         elif currentPCB.status == PCBStatus.WAITING:
#             self.ioQueue.append(currentPCB)
#         elif not currentPCB.status == PCBStatus.TERMINATED:
#             self.log(LogType.ERROR,"unexpected PCB status")