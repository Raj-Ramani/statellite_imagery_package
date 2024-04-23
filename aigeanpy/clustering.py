from math import sqrt, dist
from random import randrange
from argparse import ArgumentParser


def read_data(file_name:str):
  """
  Extracts data from a specified file 

  Parameters:
  -----------
  file_name: name of file to extract data from

  Return:
  --------
  array
    data points from the file
  """
  lines = open(file_name, 'r').readlines()
  points=[]
  for line in lines: 
    points.append(tuple(map(float, line.strip().split(','))))

  return points


def cluster(points: list[tuple], k = 3, max_iterations = 10):
  """
  Each cluster will contain points that are close to each other, and far from the other clusters.
  Prints the centre of the cluster, number of points within the cluster, and the individual points

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

  centres=[points[randrange(len(points))], points[randrange(len(points))], points[randrange(len(points))]]
  alloc=[None]*len(points)
  iterations = 0
  while iterations<max_iterations:
    for i in range(len(points)):
      data_point=points[i]
      distance = []

      for j in range(k):
        distance.append(dist(data_point,centres[j]))
      alloc[i]=distance.index(min(distance))

    for i in range(k):
      alloc_points=[data_point for j, data_point in enumerate(points) if alloc[j] == i]
      new_mean=(sum([a[0] for a in alloc_points]) / len(alloc_points), sum([a[1] for a in alloc_points]) / len(alloc_points), sum([a[2] for a in alloc_points]) / len(alloc_points))
      centres[i]=new_mean
    iterations=iterations+1
  
  # for i in range(k):
  #   alloc_points=[data_point for j, data_point in enumerate(points) if alloc[j] == i]
  #   print("Cluster " + str(i) + " is centred at " + str(centres[i]) + " and has " + str(len(alloc_points)) + " points.")
  #   print(alloc_points)
  
  return centres


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
    cluster(points.tolist(), max_iterations = int(arguments.iters))


if __name__ == "__main__":
  interface()

