#PageTable
#Talmage Gaisford

from LogType import LogType

class PageTableEntry:
    def __init__(self, pageNumber,frameNumber, valid=True):
        self.pageNumber = pageNumber
        self.frameNumber = frameNumber
        self.valid = valid

class PageTable:
    def __init__(self, pcb, pageSize, pageCount, memory):
        self.pcb = pcb
        self.table = {}
        self.pageSize = pageSize
        self.pageCount = pageCount
        self.memory = memory
        self.lruQueue = []

    def addEntry(self, pageNumber, frameNumber, valid=True):
        newTableEntry = PageTableEntry(pageNumber,frameNumber, valid)
        self.table[pageNumber] = newTableEntry
        self.lruQueue.append(newTableEntry)
        self.pcb.sendPageToMemory(pageNumber, frameNumber)

    def updateLRU(self, pageTableEntry):
        if pageTableEntry in self.lruQueue:
            self.lruQueue.remove(pageTableEntry)
        self.lruQueue.append(pageTableEntry)

    def claimNewFrame(self):
        frame = self.memory.getFreeFrame()
        if frame:
            return frame
        else:
            return None

    def freeFrame(self):
        lruPageTableEntry = self.lruQueue.pop(0)
        lruFrame = lruPageTableEntry.frameNumber
        return lruFrame, lruPageTableEntry

    def lookup(self, programLineNumber):
        pageNumber = programLineNumber // self.pageSize
        offset = programLineNumber % self.pageSize

        entry = self.table.get(pageNumber)
        if entry and entry.valid:
            self.pcb.log(LogType.LOG,f"Page {pageNumber} found in frame {entry.frameNumber}.")
            self.updateLRU(entry)
            return entry.frameNumber, offset
        else:
            self.pcb.log(LogType.LOG,f"Page fault on page {pageNumber}!")
            return self.handlePageFault(pageNumber), offset

    def handlePageFault(self, pageNumber):
        self.pcb.system.dataFacilitator.addPageFault()
        if len(self.lruQueue) < self.pageCount:
            frame = self.memory.getFreeFrame()
            if frame:
                self.addEntry(pageNumber,frame)
                return frame
            else:
                self.pcb.log(LogType.ERROR, "program tried to grab more memory but there is none")
        frameNumber, lruPageTableEntry = self.freeFrame()
        evictedPage = lruPageTableEntry.pageNumber
        if evictedPage is not None:
            if evictedPage in self.table:
                self.pcb.log(LogType.LOG,f"Evicting page {evictedPage} from frame {frameNumber}.")
                self.invalidate(evictedPage)
        self.addEntry(pageNumber, frameNumber)
        self.pcb.log(LogType.LOG,f"Loaded page {pageNumber} into frame {frameNumber}.")
        return frameNumber

    def invalidate(self, pageNumber):
        if pageNumber in self.table:
            self.table[pageNumber].valid = False