#!/usr/bin/env python3
#UndoneShell
#Talmage Gaisford

from UndoneOS import UndoneOS
from ConeShell import ConeShell
import os
import subprocess

class UndoneShell:
    def __init__(self,systemInput = UndoneOS()):
        self.system = systemInput
        self.runShell()

    def runShell(self):
        while True:
            userInput = input("$ ")
            inputStrings = userInput.split(' ')
            command = inputStrings[0]
            match command:
                case "coredump":
                    self.coredump()
                case "errordump":
                    self.errordump(inputStrings)
                case "execute":
                    self.executePrograms(inputStrings)
                case "exit":
                    break
                case "gantt":
                    self.getGantt()
                case "getpagenumber":
                    print("page number = " + str(self.system.spec.pageCount))
                case "getpagesize":
                    print("page size = " + str(self.system.spec.pageSize))
                case "getpagefaults":
                    self.getPageFaults(inputStrings)
                case "help":
                    print("UndoneShell is the best shell")
                case "load":
                    self.loadPrograms(inputStrings)
                case "osx_mac":
                    self.compileOSX(inputStrings)
                case "pwd":
                    print(os.getcwd())
                case "ps":
                    self.psDump(inputStrings)
                case "reboot":
                    self.system = UndoneOS()
                case "run":
                    self.runPrograms(inputStrings)
                case "sc":
                    self.shellChange(inputStrings)
                case "setpagenumber":
                    self.setPageNumber(inputStrings)
                case "setpagesize":
                    self.setPageSize(inputStrings)
                case "setRR":
                    self.setRR(inputStrings)
                case "setsched":
                    self.setSchedule(inputStrings)
                case "verbose":
                    self.verboseCheck(inputStrings)
                case _:
                    print('unknown command: ' + command)

    def compileOSX(self,inputStrings):
        if len(inputStrings) not in {2,3,4}:
            print('Error: To compile a file use: osx_mac <yourfile.asm> <loader address> [-v]')
        elif len(inputStrings) == 2:
            try:
                process = subprocess.run(["osx_mac", inputStrings[1], "0"])
            except subprocess.CalledProcessError as e:
                print("Error code:", e.returncode)
                print("Error output:", e.stderr)
            except FileNotFoundError:
                print("The specified executable was not found.")
        elif len(inputStrings) == 3:
            try:
                process = subprocess.run(["osx_mac", inputStrings[1], inputStrings[2]])
            except subprocess.CalledProcessError as e:
                print("Error code:", e.returncode)
                print("Error output:", e.stderr)
            except FileNotFoundError:
                print("The specified executable was not found.")
        elif len(inputStrings) == 4:
            try:
                process = subprocess.run(["osx_mac", inputStrings[1], inputStrings[2], inputStrings[3]])
            except subprocess.CalledProcessError as e:
                print("Error code:", e.returncode)
                print("Error output:", e.stderr)
            except FileNotFoundError:
                print("The specified executable was not found.")
    
    def coredump(self):
        print()
        print("registers:")
        print(self.system.registers)
        print()
        print("programs")
        for program in self.system.programs:
            print(str(program) + " : " + str(self.system.programs[program]))
        print()
        print("failed programs")
        for program in self.system.failedPrograms:
            print(str(program) + " : " + str(self.system.failedPrograms[program]))
        print()
        print("memory")
        for line in self.system.memory.mainMemory:
            print(line)
        print()

    def errordump(self,inputStrings):
        fileName = self.getFileName(inputStrings)
        if fileName in self.system.programs:
            print()
            print("printing errors for " + fileName)
            if len(self.system.programs[fileName].logger.errors) == 0:
                    print('no errors')
            else:
                for error in self.system.programs[fileName].logger.errors:
                    print(error)
        elif fileName in self.system.failedPrograms:
            print()
            print("printing errors for " + fileName)
            if len(self.system.failedPrograms[fileName].logger.errors) == 0:
                    print('no errors')
            else:
                for error in self.system.failedPrograms[fileName].logger.errors:
                    print(error)
        else:
            print()
            print("printing errors for all files")
            for program in self.system.programs.values():
                print()
                print(program.programPath)
                if len(program.logger.errors) == 0:
                    print('no errors')
                for error in program.logger.errors:
                    print(error)
            for program in self.system.failedPrograms.values():
                print()
                print(program.programPath)
                if len(program.logger.errors) == 0:
                    print('no errors')
                for error in program.logger.errors:
                    print(error)
        print()

    def executePrograms(self,inputStrings):
        self.loadPrograms(inputStrings)
        self.runPrograms(inputStrings)

    def splitOnPipe(self,lst):
        if "|" not in lst:
            return lst, []

        index = lst.index("|")
        left = lst[:index]
        right = lst[index + 1:]
        return left, right

    def loadPrograms(self,inputStrings):
        executions = []
        inputStrings = self.verboseCheck(inputStrings)[1:]
        sharedMemoryCommand = None
        if "|" in inputStrings:
            inputStrings, sharedMemoryCommand = self.splitOnPipe(inputStrings)
        for i in range(len(inputStrings)):
            if inputStrings[i] == "-v" or inputStrings[i] == "-d":
                continue
            if inputStrings[i].isnumeric():
                continue
            if not inputStrings[i].endswith('.osx'):
                print("invalid filename: " + inputStrings[i])
                return
            elif not os.path.exists(inputStrings[i]):
                print("file not found: " + inputStrings[i])
                return
            else:
                try:
                    if inputStrings[i+1].isnumeric():
                        executions.append([inputStrings[i],int(inputStrings[i+1])])
                    else:
                        executions.append([inputStrings[i],0])
                except IndexError:
                    executions.append([inputStrings[i],0])
        self.system.loadPrograms(executions,sharedMemoryCommand)
    
    def getFileName(self,inputStrings):
        for i in inputStrings:
            if i.endswith('.osx'):
                return i
        return ''
    
    def getPageFaults(self,inputStrings):
        self.system.outputPageFaults()
    
    def psDump(self, inputStrings):
        self.system.psDump()
    
    def runPrograms(self,inputStrings):
        # inputStrings = self.verboseCheck(inputStrings)
        # fileName = self.getFileName(inputStrings)
        # if len(fileName) == 0:
        #     print('invalid filename')
        # elif not os.path.exists(fileName):
        #     print("file not found")
        # elif not (fileName) in self.system.programs:
        #     print("file not loaded into memory")
        # else:
        #     self.system.runPrograms(fileName)
        self.system.runPrograms()
    
    def shellChange(self,inputStrings):
        if inputStrings[1] == 'ConeShell':
            newShell = ConeShell(self.system)
            newShell.runShell()
        elif inputStrings[1] == 'UndoneShell':
            print('you are already using UndoneShell')
        else:
            print('unknown shell: ' + inputStrings[1])

    def setPageNumber(self,inputStrings):
        if len(inputStrings) != 2:
            print("to set page number, type: 'setpagenumber [number]'")
        else:
            self.system.setPageCount(inputStrings[1])

    def setPageSize(self,inputStrings):
        if len(inputStrings) != 2:
            print("to set page size, type: 'setpagesize [number]'")
        else:
            self.system.setPageSize(inputStrings[1])

    def setRR(self,inputStrings):
        inputStrings = self.verboseCheck(inputStrings)
        if len(inputStrings) != 3:
            print("to setRR, type: 'setRR –v quantum1 quantum2'")
        elif not inputStrings[1].isdigit() or not inputStrings[2].isdigit():
            print("quantum values must be integers")
        else:
            self.system.setRR(inputStrings[1],inputStrings[2])

    def setSchedule(self,inputStrings):
        inputStrings = self.verboseCheck(inputStrings)
        if len(inputStrings) != 2 or inputStrings[1] not in ["RR", "FCFS", "MFQ"]:
            print("to setsched, type: 'setsched scheduling_algorithm (RR, FCFS, MFQ)'")
        else:
            self.system.setSchedule(inputStrings[1])

    def verboseCheck(self,inputStrings):
        isVerbose = False
        for i in inputStrings:
            if i == "-v" or i == "-d":
                isVerbose = True
                inputStrings.remove(i)
        self.system.setVerbose(isVerbose)
        return inputStrings
    
    def getGantt(self):
        self.system.dataFacilitator.getGantt()




    

    