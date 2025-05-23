#UndoneShell
#Talmage Gaisford

class Queue:
    def __init__(self,quantum = 10**10):
        self.quantum = quantum
        self.queue = []

    def append(self,item):
        self.queue.append(item)

    def contains(self,item):
        if item in self.queue:
            return True
        else:
            return False

    def getFirst(self):
        return self.queue[0]
    
    def hasItems(self):
        if self.queue:
            return True
        else:
            return False

    def insertFront(self,item):
        self.queue.insert(0,item)

    def pull(self):
        return self.queue.pop(0)
    
    def remove(self,item):
        self.queue.remove(item)
    