import numpy as np
import matplotlib.pyplot as plt
import time 
import random

from aigeanpy.clustering import cluster as cluster_standard
from aigeanpy.clustering_numpy import cluster as cluster_numpy

def sample_data(N):
    """
    Creating N data points
    Parameters:
    -----------
    N: number of points
    Return:
    -------
    list
        data points
    """
    data_points = np.random.uniform(low = -8, high = 8, size = (N, 3))    #a 3D data point i.e. (x,y,z)

    return list(map(tuple,data_points))
    
    
def standard_runtime(N_values):
    """
    Calculating the time required to run the standard python base clustering function with varying input size
    Parameters:
    -----------
    N_values: number of data points
    Returns:
    --------
    list
        times to run the standard base clustering function on different values of N_values
    """
    standard_times = []

    for N in N_values:
        data_points = sample_data(N)
        standard_start = time.time()          #initialise the timer
        cluster_standard(data_points)        #call the function to begin the calculation
        standard_times.append(time.time() - standard_start)       #runtime 

    return standard_times

def numpy_runtime(N_values):
    """
    Calculating the time required to run the numpy version clustering function with varying input size
    Parameters:
    -----------
    N_values: number of data points
    Returns:
    --------
    list
        times to run the numpy clustering function on different values of N_values
    """
    numpy_times = []

    for N in N_values:
        data_points = sample_data(N)
        numpy_start = time.time()
        cluster_numpy(data_points)
        numpy_times.append(time.time() - numpy_start)

    return numpy_times


def plot_figure(N_values, save = False):
    """
    Plots the time required against trhe size of the input, with both versions on the same plot
    Parameters:
    -----------
    N_values: number of data points
    """

    plt.figure()
    plt.plot(N_values, standard_runtime(N_values), label = "Standard")
    plt.plot(N_values, numpy_runtime(N_values), label = "Numpy")
    plt.xlabel("Number of points, N")
    plt.ylabel("Time (s)")
    plt.legend(loc = "best")

    if save == True:
        plt.savefig("performance.png")

    plt.show()

if __name__ == "__main__":
    N_values = np.arange(100,10000,100)            #100 data points spaced between 100 and 10,000
    plot_figure(N_values, True)
