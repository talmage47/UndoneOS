#Clock
#Talmage Gaisford

class Clock:
    def __init__(self,system):
        self.system = system
        self.time = 0

    def getTime(self):
        return self.time

    def tick(self, increment = 1):
        self.time += increment


