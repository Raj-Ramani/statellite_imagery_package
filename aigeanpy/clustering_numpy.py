from argparse import ArgumentParser
import numpy as np



def read_data(file_name:str):
  """
  Extracts data from a specified file using numpy structure
  
  Parameters:
  -----------
  file_name: name of file to extract data from

  Return:
  --------
  array
    data points from the file
  """
  points = np.loadtxt(file_name, delimiter = ",")

  return points


def indices(points, k = 3, max_iterations = 10):
  """
  Assign each data point to a cluster by computing its distance from all cluster centres, and assign it to the nearest centre.
  Update the centre of each cluster by setting it to the average of all points assigned to the cluster.
  Each cluster will contain points that are close to each other, and far from the other clusters.

  Parameters:
  -----------
  points: list of data points
  k: number of clusters (set as 3 by default)
  max_iterations: maximum iterations to run the above steps over (set as 10 by default)

  Return:
  -------
  list of int
    The indices of the cluster that each data point belongs to
  """
  if type(points) != list:
      raise TypeError("The points sample must be a list")

  if type(k) != int and type(max_iterations) != int:
    raise TypeError("The number of clusters (k) and the maximum number of iterations (max_iterations) must be a positive integer")

  if k <= 0 or max_iterations <= 0:
    raise ValueError("The number of clusters (k) must be greater than 0 and the maximum number of iterations (max_iterations) a positive integer")
  
  points = np.array(points)    
  centres = points[np.random.choice(points.shape[0], size = k, replace = False)]
  iterations = 0
  while iterations<max_iterations:
    square = np.square(np.repeat(points, k, axis=0).reshape(points.shape[0], k, points.shape[1]) - centres)
    dist = np.sqrt(np.sum(square, axis=2))
    index = np.argmin(dist, axis=1)
    for i in range(k):
      centres[i] = np.mean(points[index == i], axis=0)
    iterations = iterations + 1

  return index


def cluster(points, k = 3, max_iterations = 10):
  """
  Calls the "indices" function which contains the indices of the cluster that each data point belongs to.


  Parameters:
  -----------
  points: list of data points
  k: number of clusters (set as 3 by default)
  max_iterations: maximum iterations to run the above steps over (set as 10 by default)

  Return:
  ------
  array
    Centre of k clusters
  """
  if type(points) != list:
      raise TypeError("The points sample must be a list")

  if type(k) != int and type(max_iterations) != int:
    raise TypeError("The number of clusters (k) and the maximum number of iterations (max_iterations) must be a positive integer")

  if k <= 0 or max_iterations <= 0:
    raise ValueError("The number of clusters (k) must be greater than 0 and the maximum number of iterations (max_iterations) a positive integer")
  

  index = indices(points, k, max_iterations)
  points = np.array(points)
  
  centres = [np.mean(points[index == i], axis=0) for i in range(k)]


  return np.array(centres)


def interface():
  """
  Command-line interface so that a user can call it by specifying a file and, optionally, a number of iterations
  """
  parser = ArgumentParser(description="Generate k clusters with k means algorithm")

  parser.add_argument("file_name", help = "Specify the file which contains the list of points")
  parser.add_argument("--iters", default = 10, help = "Number of iterations to run the k-means algorithm over")

  arguments = parser.parse_args()

  if ".csv" not in arguments.file_name:
    raise RuntimeError("The input file must be a csv file")

  if int(arguments.iters) <= 0:
    raise ValueError("The maximum number of iterations must be a positive integer")

  points = read_data(arguments.file_name)
  if type(points) == list:
    cluster(points, max_iterations = int(arguments.iters))

  elif type(points) != list:  
    cluster(points.tolist(), max_iterations = int(arguments.iters))       #convert non-type list to list type data structure


if __name__ == "__main__":
  interface()
