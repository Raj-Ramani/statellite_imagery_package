from aigeanpy.clustering import cluster, read_data
import pytest
import numpy as np
from aigeanpy.clustering_numpy import indices
import aigeanpy.analysis as analysis
from benchmark.performance import standard_runtime, numpy_runtime
from aigeanpy.net import download_isa

download_isa('aigean_ecn_20230115_042844.csv')


def test_points_type():
    with pytest.raises(TypeError):
        points = (4.77193, 5.07066, 2.70127),
        (5.1202, 6.00523, 1.11497),
        (6.67254, 5.55893, 3.11361)
        cluster(points, k = 3, max_iterations = 10)
#points is tuple but not list, so it should raise TypeError

def test_k_type():
    with pytest.raises(TypeError):
        points = read_data(file_name='aigean_ecn_20230115_042844.csv')
        cluster(points,k='3',max_iterations = 10)
#The number of cluster k = '3' is a str, so it should raise TypeError

def test_k_value():
    with pytest.raises(ValueError):
        points = read_data(file_name='aigean_ecn_20230115_042844.csv')
        cluster(points,k=0,max_iterations = 10)
#The number of cluster k=0, so it should raise ValueError

def test_max_interation_type():
    with pytest.raises(TypeError):
        points = read_data(file_name='aigean_ecn_20230115_042844.csv')
        cluster(points,k=3,max_iterations = '10')
#Max interation = '10' is a str, so it should raise TypeError

def test_max_interation_value():
    with pytest.raises(ValueError):
        points = read_data(file_name='aigean_ecn_20230115_042844.csv')
        cluster(points,k=3,max_iterations = -2)
#Max interation = -2 which is negative, so it should raise ValueError

def test_read_data_in_clustering():
    result = read_data('aigean_ecn_20230115_042844.csv')
    assert type(result) == list


def test_cluster_in_clustering():
    points = read_data('aigean_ecn_20230115_042844.csv')
    result = cluster(points, k = 3, max_iterations = 10)
    assert type(result) == list
    
def test_read_data_in_clustering_numpy():
    result = read_data('aigean_ecn_20230115_042844.csv')
    assert type(result) == list

def test_indices():
    points = [[ 4.77193e+00,  5.07066e+00,  2.70127e+00],
       [ 5.12020e+00,  6.00523e+00,  1.11497e+00],
       [ 6.67254e+00,  5.55893e+00,  3.11361e+00]]
    result = indices(points,k = 3, max_iterations = 10)
    assert type(result) == np.ndarray
    np.random.seed(0)
    assert result.all() == np.array([2,1,0]).all()

def test_cluster_in_clustering_numpy():
    points = [[ 4.77193e+00,  5.07066e+00,  2.70127e+00],
       [ 5.12020e+00,  6.00523e+00,  1.11497e+00],
       [ 6.67254e+00,  5.55893e+00,  3.11361e+00]]
    result = indices(points,k = 3, max_iterations = 10)
    assert type(result) == np.ndarray
    np.random.seed(0)
    assert len(result) == 3
    assert result.any() == np.array([[6.67254, 5.55893, 3.11361],
                                    [5.1202 , 6.00523, 1.11497],
                                    [4.77193, 5.07066, 2.70127]]).any()

def test_kmeans():
    with pytest.raises(ValueError):
        analysis.kmeans(7,k=3,max_iterations=10)
#The file is not a path or string, so it should raise ValueError

def test_performance():
    N_values = np.arange(100,3000,100)
    time_std = standard_runtime(N_values)
    time_np = numpy_runtime(N_values)
    assert(time_np[5] -time_std[5]<0)

   