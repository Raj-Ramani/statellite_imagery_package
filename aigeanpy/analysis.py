from typing import Union
from pathlib import Path
import csv
import numpy as np

from aigeanpy.clustering_numpy import indices, read_data


def kmeans(file: Union[Path, str], k:int = 3, max_iterations:int = 10) -> list:
  """
  Calls the cluster function from the numpy version of clustering and returns a list with the measurement indices that belong to each group
  
  Parameters:
  -----------
  file: directory path of file's location or name of file
  k: number of clusters
  max_iterations: maximum iterations to run the above steps over

  Return:
  -------
  list
    the cluster that each data point belongs to
  """

  if isinstance(file, Path):
    points = []

    with open(file, newline="") as f:
        file_reader = csv.DictReader(f)
        for line in file_reader:     
            points.append(tuple(map(float, line.strip().split(','))))

  elif type(file) ==  str:
    points = read_data(file)

  else:
    raise ValueError("The input file name must either be a path or a string.")

  if type(points) == list:
    indices(points)

  elif type(points) != list:  
    indices(points.tolist())       #convert non-type list to list type data structure
  