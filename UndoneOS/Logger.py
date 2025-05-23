#Logger
#Talmage Gaisford

from ConeShell import ConeShell
import os
from LogType import LogType
import time

class Logger:
    def __init__(self, system):
        self.system = system
        self.logs = []
        self.errors = []

    def log(self,logType,entity,inputString):
        with open("UndoneLogs.txt", "w") as file:             
            file.write(str(time.time()) + " , " + str(logType) + " , " + str(entity) + " , " + inputString)
        self.logs.append(str(logType) + " , " + str(entity) + " , " + inputString)
        if self.system.isVerbose and (logType == LogType.LOG or logType == LogType.ERROR):
            print(str(entity) + " " + inputString)
        if logType == LogType.ERROR:
            self.logError(logType,entity,inputString)

    # def logStep(step,pcbPath,stepString):

    def logError(self, logType, pcbPath, inputString):
        self.errors.append(str(logType) + " , " + str(pcbPath) + " , " + inputString)