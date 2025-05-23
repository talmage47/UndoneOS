#GanttFacilitator

import time
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class DataFacilitator:
    
    def __init__(self, system):
        self.system = system
        self.dataStructure = []
        self.realTimeStructure = []
        self.startTime = time.time()
        self.pageFaults = 0

    # add data to the gantt chart
    def addData (self,pcb,queue,time):
        self.dataStructure.append([pcb.programPath,"queue" + str(queue.quantum),time])

    # add data to the gantt chart using the real time clock
    def addRealTimeData(self,pcb,queue,startTime,endTime):
        self.realTimeStructure.append([pcb.programPath,"queue" + str(queue.quantum),startTime,endTime])

    # increment the page fault counter
    def addPageFault(self):
        self.pageFaults += 1

    # send the data structure containing the gantt chart data
    def getData(self):
        return self.dataStructure
    
    # send the data structure containing the gantt chart built using the real time clock
    def getRealTimeData(self):
        return self.realTimeStructure
    
    # get the total time since the DataFacilitator was initialized
    def getElapsedTime(self):
        elapsedTime = time.time() - self.startTime
        return elapsedTime
    
    # erase gantt data for a fresh start
    def resetGantt(self):
        self.realTimeStructure = []
    
    # build and display a gantt chart using matplotlibrary
    def getGantt(self):
        ganttChartData = self.realTimeStructure
        with open("ganttData.txt", "w") as file:             
            for item in ganttChartData:
                file.write(str(item))
                file.write("\n")

        unique_queues = sorted(set(entry[1] for entry in ganttChartData))
        queue_colors = {queue: plt.cm.tab10(i / len(unique_queues)) for i, queue in enumerate(unique_queues)}

        programs = sorted(set(entry[0] for entry in ganttChartData))
        program_positions = {prog: i for i, prog in enumerate(programs)}

        fig, ax = plt.subplots(figsize=(10, 6))

        for program, queue, startTime, stopTime in ganttChartData:
            
            ax.barh(program_positions[program], stopTime - startTime, left=startTime, color=queue_colors[queue], edgecolor='none')

        ax.set_yticks(range(len(programs)))
        ax.set_yticklabels(programs)
        ax.set_xlabel("Time")
        ax.set_ylabel("Programs")
        ax.set_title("Gantt Chart of Program Execution")

        legend_patches = [mpatches.Patch(color=color, label=queue) for queue, color in queue_colors.items()]
        ax.legend(handles=legend_patches, title="Queues", loc="upper right")

        plt.grid(axis="x", linestyle="--", alpha=0.7)

        plt.show()
