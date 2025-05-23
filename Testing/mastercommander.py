# master commander of UndoneOS
# Talmage Gaisford

import os
from datetime import datetime
from UndoneOS import UndoneOS
from MachineSpec import MachineSpec
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as mpatches
from scipy.spatial import Delaunay
import numpy as np

programFolder = "testprograms/osx"
desiredRuns = ["p10len50"]#,"p5len500","p20len500"]

def main():
    mainDataFolder = "runData"
    if not os.path.exists(mainDataFolder):
        os.makedirs(mainDataFolder)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dataFolderPath = os.path.join(mainDataFolder, timestamp)
    os.makedirs(dataFolderPath)
    tableData = []
    tableColumns = ["type","min response","min wait","min turnaround","max throughput"]
    
    for subProgramFolder in os.listdir(programFolder):
        subProgramFolderPath = os.path.join(programFolder, subProgramFolder)
        if os.path.isdir(subProgramFolderPath):
            subDataFolderPath = os.path.join(dataFolderPath, subProgramFolder)
            if not os.path.exists(subDataFolderPath):
                os.makedirs(subDataFolderPath)
            dataTextFileName = subProgramFolder + "data.txt"
            dataTextFilePath = os.path.join(subDataFolderPath,dataTextFileName)
            with open(dataTextFilePath, "w") as file:
                file.write(timestamp + " " + subProgramFolder + " data")
            
            completionTimePoints = []
            throughputPoints = []
            averageWaitTimePoints = []
            averageTurnaroundTimePoints = []
            averageResponseTimePoints = []

            programsToRun = []
            for filename in os.listdir(subProgramFolderPath):  
                filePath = os.path.join(subProgramFolderPath, filename)
                if os.path.isfile(filePath):
                    programsToRun.append([filePath,0])

            for quantum1 in [1,2,4,8,16,32,64,128,256]:
                for quantumRatio in [1,2,4,8,16,32,64,128]:
                    quantum2 = quantum1 * quantumRatio
                    specifications = MachineSpec(quantum1, quantum2)
                    operatingSystem = UndoneOS(specifications)
                    operatingSystem.setRR(quantum1,quantum2)
                    operatingSystem.setSchedule("MFQ")
                    operatingSystem.execute(programsToRun)
                    ganttChartData = operatingSystem.ganttFacilitator.getRealTimeData()  

                    programData = []

                    unique_queues = sorted(set(entry[1] for entry in ganttChartData))
                    queue_colors = {queue: plt.cm.tab10(i / len(unique_queues)) for i, queue in enumerate(unique_queues)}

                    programs = sorted(set(entry[0] for entry in ganttChartData))
                    program_positions = {prog: i for i, prog in enumerate(programs)}

                    fig, ax = plt.subplots(figsize=(10, 6))

                    for program, queue, startTime, stopTime in ganttChartData:

                        for myDictionary in programData:
                            if myDictionary["name"] == program:
                                myDictionary["turnaroundTime"] = stopTime
                                myDictionary["runTime"] += stopTime - startTime
                                myDictionary["waitTime"] = myDictionary["turnaroundTime"] - myDictionary["runTime"]

                        if program not in [d.get("name") for d in programData if "name" in d]:
                            programData.append({"name": program, "responseTime": startTime, "turnaroundTime": stopTime, "runTime": startTime - stopTime, "waitTime": startTime})
                        
                        ax.barh(program_positions[program], stopTime - startTime, left=startTime, color=queue_colors[queue], edgecolor='none')

                    ax.set_yticks(range(len(programs)))
                    ax.set_yticklabels(programs)
                    ax.set_xlabel("Time")
                    ax.set_ylabel("Programs")
                    ax.set_title("Gantt Chart of Program Execution")

                    legend_patches = [mpatches.Patch(color=color, label=queue) for queue, color in queue_colors.items()]
                    ax.legend(handles=legend_patches, title="Queues", loc="upper right")

                    plt.grid(axis="x", linestyle="--", alpha=0.7)

                    ganttFigureName = "Q" + str(quantum1) + "Q" + str(quantum2) + " gantt.png"
                    ganttFigurePath = os.path.join(subDataFolderPath, ganttFigureName)
                    plt.savefig(ganttFigurePath)
                    plt.close()


                    completionTime = ganttChartData[-1][2]
                    averageWaitTime = np.mean([d["waitTime"] for d in programData]) if programData else 0
                    averageTunaroundTime = np.mean([d["turnaroundTime"] for d in programData]) if programData else 0
                    averageResponseTime = np.mean([d["responseTime"] for d in programData]) if programData else 0
                    
                    completionTimePoints.append([quantum1,quantum2/quantum1,completionTime])
                    throughputPoints.append([quantum1,quantum2/quantum1,len(programData)/completionTime])
                    averageWaitTimePoints.append([quantum1,quantum2/quantum1,averageWaitTime])
                    averageTurnaroundTimePoints.append([quantum1,quantum2/quantum1,averageTunaroundTime])
                    averageResponseTimePoints.append([quantum1,quantum2/quantum1,averageResponseTime])

                    with open(dataTextFilePath, "a") as file:
                        file.write("\n")
                        file.write("\n")
                        file.write("Quantum 1: " + str(quantum1) + "  Quantum 2: " + str(quantum2))
                        file.write("\n")
                        file.write("Throughput = " + str(len(programData)) + " programs per " + str(completionTime) + " seconds")
                        file.write("\n")
                        file.write("Throughput = " + str(len(programData)/completionTime) + " programs per second")
                        file.write("\n")
                        file.write("Average Wait Time = " + str(averageWaitTime)) 
                        file.write("\n")
                        file.write("Average Turnaround Time = " + str(averageTunaroundTime))
                        file.write("\n")
                        file.write("Average Response Time = " + str(averageResponseTime))

                        for program in programData:
                            file.write("\n")
                            file.write(program["name"])
                            file.write("\n")
                            file.write("   Wait Time = " + str(program["waitTime"]))
                            file.write("\n")
                            file.write("   Turnaround Time = " + str(program["turnaroundTime"]))
                            file.write("\n")
                            file.write("   Response Time = " + str(program["responseTime"]))

            minCompletion = findMinimum(completionTimePoints)
            maxCompletion = findMaximum(completionTimePoints)
            minThroughput = findMinimum(throughputPoints)
            maxThroughput = findMaximum(throughputPoints)
            minWait = findMinimum(averageWaitTimePoints)
            maxWait = findMaximum(averageWaitTimePoints)
            minTurnaround = findMinimum(averageTurnaroundTimePoints)
            maxTurnaround = findMaximum(averageTurnaroundTimePoints)
            minResponse = findMinimum(averageResponseTimePoints)
            maxResponse = findMaximum(averageResponseTimePoints)

            minimumsTextFileName = subProgramFolder + "minimums.txt"
            minimumsTextFilePath = os.path.join(subDataFolderPath,minimumsTextFileName)
            with open(minimumsTextFilePath, "w") as file:
                file.write(timestamp + " " + subProgramFolder + " minimums and maximums")
                file.write("\n")
                file.write("Minimum completion time =  " + str(minCompletion[2]))
                file.write("\n")
                file.write("   Quantum1 = " + str(minCompletion[0]))
                file.write("\n")
                file.write("   Quantum2 = " + str(minCompletion[1] * minCompletion[0]))
                file.write("\n")
                file.write("   Quantum Ratio = " + str(minCompletion[1]))
                file.write("\n")
                file.write("Maximum completion time =  " + str(maxCompletion[2]))
                file.write("\n")
                file.write("   Quantum1 = " + str(maxCompletion[0]))
                file.write("\n")
                file.write("   Quantum2 = " + str(maxCompletion[1] * maxCompletion[0]))
                file.write("\n")
                file.write("   Quantum Ratio = " + str(maxCompletion[1]))
                file.write("\n")
                file.write("\n")
                file.write("Minimum throughput =  " + str(minThroughput[2]))
                file.write("\n")
                file.write("   Quantum1 = " + str(minThroughput[0]))
                file.write("\n")
                file.write("   Quantum2 = " + str(minThroughput[1] * minThroughput[0]))
                file.write("\n")
                file.write("   Quantum Ratio = " + str(minThroughput[1]))
                file.write("\n")
                file.write("Maximum throughput =  " + str(maxThroughput[2]))
                file.write("\n")
                file.write("   Quantum1 = " + str(maxThroughput[0]))
                file.write("\n")
                file.write("   Quantum2 = " + str(maxThroughput[1] * maxThroughput[0]))
                file.write("\n")
                file.write("   Quantum Ratio = " + str(maxThroughput[1]))
                file.write("\n")
                file.write("\n")
                file.write("Minimum average wait time =  " + str(minWait[2]))
                file.write("\n")
                file.write("   Quantum1 = " + str(minWait[0]))
                file.write("\n")
                file.write("   Quantum2 = " + str(minWait[1] * minWait[0]))
                file.write("\n")
                file.write("   Quantum Ratio = " + str(minWait[1]))
                file.write("\n")
                file.write("Maximum average wait time =  " + str(maxWait[2]))
                file.write("\n")
                file.write("   Quantum1 = " + str(maxWait[0]))
                file.write("\n")
                file.write("   Quantum2 = " + str(maxWait[1] * maxWait[0]))
                file.write("\n")
                file.write("   Quantum Ratio = " + str(maxWait[1]))
                file.write("\n")
                file.write("\n")
                file.write("Minimum average turnaround time =  " + str(minTurnaround[2]))
                file.write("\n")
                file.write("   Quantum1 = " + str(minTurnaround[0]))
                file.write("\n")
                file.write("   Quantum2 = " + str(minTurnaround[1] * minTurnaround[0]))
                file.write("\n")
                file.write("   Quantum Ratio = " + str(minTurnaround[1]))
                file.write("\n")
                file.write("Maximum average tunaround time =  " + str(maxTurnaround[2]))
                file.write("\n")
                file.write("   Quantum1 = " + str(maxTurnaround[0]))
                file.write("\n")
                file.write("   Quantum2 = " + str(maxTurnaround[1] * maxTurnaround[0]))
                file.write("\n")
                file.write("   Quantum Ratio = " + str(maxTurnaround[1]))
                file.write("\n")
                file.write("\n")
                file.write("Minimum average response time =  " + str(minResponse[2]))
                file.write("\n")
                file.write("   Quantum1 = " + str(minResponse[0]))
                file.write("\n")
                file.write("   Quantum2 = " + str(minResponse[1] * minResponse[0]))
                file.write("\n")
                file.write("   Quantum Ratio = " + str(minResponse[1]))
                file.write("\n")
                file.write("Maximum average response time =  " + str(maxResponse[2]))
                file.write("\n")
                file.write("   Quantum1 = " + str(maxResponse[0]))
                file.write("\n")
                file.write("   Quantum2 = " + str(maxResponse[1] * maxResponse[0]))
                file.write("\n")
                file.write("   Quantum Ratio = " + str(maxResponse[1]))

            sets = [np.array(removeOutliers(completionTimePoints)),
                    np.array(removeOutliers(throughputPoints)), 
                    np.array(removeOutliers(averageWaitTimePoints)), 
                    np.array(removeOutliers(averageTurnaroundTimePoints)), 
                    np.array(removeOutliers(averageResponseTimePoints))]
            # sets = [np.array(completionTimePoints),
            #         np.array(throughputPoints), 
            #         np.array(averageWaitTimePoints), 
            #         np.array(averageTurnaroundTimePoints), 
            #         np.array(averageResponseTimePoints)]
            setNames = ["CompletionTime", "Throughput", "Average Wait Time", "Average Turnaround Time", "Average Response Time"]

            for i, points in enumerate(sets):
                points = np.array(points)
                x, y, z = points[:, 0], points[:, 1], points[:, 2]

                tri = Delaunay(points[:, :2])

                fig = plt.figure(figsize=(10, 7))
                ax = fig.add_subplot(111, projection='3d')

                ax.plot_trisurf(x, y, z, triangles=tri.simplices, cmap="viridis", edgecolor="none")

                ax.set_title(setNames[i])
                ax.set_xlabel("Q1")
                ax.set_ylabel("Q2/Q1")
                ax.set_zlabel("")

                graphFigureName = setNames[i] + " graph.png"
                graphFigurePath = os.path.join(subDataFolderPath, graphFigureName)
                plt.savefig(graphFigurePath)
                plt.close()

            print(subProgramFolder + "completed")

            tableData.append([subProgramFolder,str(minResponse),str(minWait),str(minTurnaround),str(maxThroughput)])

    fig, ax = plt.subplots(figsize=(5, 2)) 
    ax.axis('tight')
    ax.axis('off')
    ax.table(cellText=tableData, colLabels=tableColumns, cellLoc='center', loc='center')

    tableFigurePath = os.path.join(dataFolderPath, "dataTable.png")
    plt.savefig(tableFigurePath, dpi=300) 
    
    print("")
    print("master commander script completed")
    

def getProgramName(longName):
    programName = longName
    index = longName.find("c")
    if index != -1 and index + 1 < len(longName):  
        nextChar = longName[index + 1]
        programName = "program " + nextChar
    return programName

def findMinimum(points):
    minPoint = min(points, key=lambda p: p[2])
    return [minPoint[0], minPoint[1], minPoint[2]]

def findMaximum(points):
    maxPoint = max(points, key=lambda p: p[2])
    return [maxPoint[0], maxPoint[1], maxPoint[2]]

def removeOutliers(points, std_factor=3):
   
    z_values = [p[2] for p in points]
    mean_z = np.mean(z_values)
    std_z = np.std(z_values)

    z_min, z_max = mean_z - std_factor * std_z, mean_z + std_factor * std_z

    filtered_points = [p for p in points if z_min <= p[2] <= z_max]

    return filtered_points

if __name__ == "__main__":
    main()

        
