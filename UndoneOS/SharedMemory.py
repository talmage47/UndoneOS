#UndoneShell
#Talmage Gaisford

from threading import Lock

class SharedMemory:
    def __init__(self, name, priveleges, length):
        self.name = name
        self.bufferSize = length
        self.storage = [0] * self.bufferSize
        self.counter = 0
        self.inValue = 0
        self.outValue = 0
        self.locked = False
        self.mutex = Lock()

    def contains(self,item):
        if item in self.queue:
            return True
        else:
            return False

    def get(self):
        self.mutex.acquire()
        output = self.storage[self.outValue]
        #output =  self.storage.pop(self.outValue)
        self.outValue = (self.outValue + 1) % self.bufferSize
        self.counter -= 1
        self.mutex.release()
        return output

    def hasItems(self):
        if self.storage:
            return True
        else:
            return False
        
    def isFull(self):
        self.mutex.acquire()
        isFull = self.counter == self.bufferSize
        self.mutex.release()
        return isFull
    
    def isEmpty(self):
        self.mutex.acquire()
        isEmpty = self.counter == 0
        self.mutex.release()
        return isEmpty
    
    # def lock(self):
    #     if self.locked:
    #         return False
    #     else:
    #         self.locked = True
    #         return True
        
    def put(self,item):
        self.mutex.acquire()
        self.storage[self.inValue] = item
        #self.storage.insert(self.inValue,item)
        self.inValue = (self.inValue + 1) % self.bufferSize
        self.counter += 1
        self.mutex.release()

    # def unlock(self):
    #     self.locked = False

    

    
    