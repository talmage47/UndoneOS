#ConeShell
#Talmage Gaisford

class ConeShell:
    # ConeShell is a skeleton that has no real function other than to switch to UndoneShell
    def __init__(self,virtualMachine):
        self.virtualMachine = virtualMachine

    def runShell(self):
        while True:
            userInput = input("% ")
            inputStrings = userInput.split(' ')
            command = inputStrings[0]
            isVerbose = self.verboseCheck(inputStrings)
            fileName = self.getFileName(inputStrings)
            if command == "exit":
                break
            elif command == "sc":
                if inputStrings[1] == 'UndoneShell':
                    break
                elif inputStrings[1] == 'ConeShell':
                    print('you are already using ConeShell')
                else:
                    print('unknown shell: ' + inputStrings[1])
            elif command == "help":
                print("ConeShell is not as good as UndoneShell")
            elif command == "load":
                if len(fileName) == 0:
                    print('invalid filename: ' + fileName)
                else:
                    self.virtualMachine.unpackProgram(fileName)
            else:
                print('unknown command: ' + command)

    def verboseCheck(self,inputStrings):
        for i in inputStrings:
            if i == '-v':
                return True
        return False
    
    def getFileName(self,inputStrings):
        for i in inputStrings:
            if i.endswith('.osx'):
                return i
        return ''