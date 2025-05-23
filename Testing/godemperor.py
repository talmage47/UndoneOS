# god emperor of UndoneOS
# Talmage Gaisford

import os
from datetime import datetime
from UndoneOS import UndoneOS
from MachineSpec import MachineSpec
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as mpatches
from scipy.spatial import Delaunay
from scipy.interpolate import griddata
import numpy as np

programs = ["two.osx","three.osx"]

def main():
    data = []
    programsToRun = []
    for filename in programs:  
        programsToRun.append([filename,0])
    pageCounts = [1,2,3,4,5,6,7,8]
    pageSizes = [1,2,3,4,5,6,7,8]
    for pageCount in pageCounts:
        for pageSize in pageSizes:
            spec = MachineSpec()
            currentSystem = UndoneOS(spec)
            currentSystem.setPageCount(pageCount)
            currentSystem.setPageSize(pageSize)
            currentSystem.loadPrograms(programsToRun,None)
            currentSystem.runPrograms()
            pageFaultCount = currentSystem.dataFacilitator.pageFaults
            data.append([pageCount,pageSize,pageFaultCount])

    data = np.array(data)
    x = data[:, 0]  # pageCount
    y = data[:, 1]  # pageSize
    z = data[:, 2]  # pageFaultCount

    # Create grid
    xi = np.unique(x)
    yi = np.unique(y)
    xi, yi = np.meshgrid(xi, yi)

    # Grid z values
    zi = griddata((x, y), z, (xi, yi), method='linear')

    # Plotting
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(xi, yi, zi, cmap='viridis')

    # Axis labels
    ax.set_xlabel('Page Number')
    ax.set_ylabel('Page Size')
    ax.set_zlabel('Page Fault Count')

    # Show the plot
    plt.show()
            


if __name__ == "__main__":
    main()

        
