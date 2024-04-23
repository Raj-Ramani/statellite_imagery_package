import pytest
from aigeanpy.net import query_isa, judge_legal_date, time_sub, download_isa
import os
import requests
import responses

def test_start_date_format():
    with pytest.raises(TypeError):
        query = query_isa('12-05-2022', '2022-12-05', 'Fand') #The start date '12-05-2022' has a wrong date format(MM-DD-YY), so it should raise TypeError

def test_start_date_type():
    with pytest.raises(TypeError):
        query = query_isa(2022-12-12,'2022-12-13','Fand') #The start date 2022-12-12 is not a string, so it should raise TypeError

def test_stop_date_format():
    with pytest.raises(TypeError):
        query = query_isa('2022-12-05', '12-05-2022', 'Fand') #The stop date '12-05-2022' has a wrong date format(MM-DD-YY), so it should raise TypeError

def test_stop_date_type():
    with pytest.raises(TypeError):
        query = query_isa('2022-12-12',2022-12-13,'Fand') #The stop date 2022-12-13 is not a string, so it should raise TypeError

def test_time_sub_value1():
    with pytest.raises(ValueError):
        query = query_isa('2022-12-05', '2022-12-09', 'Fand') #The difference between the end date and the start date is greater than 3 days, so it should raise ValueError

def test_time_sub_value2():
    with pytest.raises(ValueError):
        query = query_isa('2022-12-07', '2022-12-05', 'Fand') #The start date is greater than end date, so it should raise ValueError

def test_judge_legal_date():
    date = '2022-12-05'
    assert judge_legal_date(date)

def test_time_sub():
    start_date = '2022-12-05'
    stop_date = '2022-12-07'
    assert 2 == time_sub(start_date,stop_date)

def test_filename():
    with pytest.raises(TypeError):
        download_isa('aigean_fan_20221208_170852.txt', save_dir='') #The filename is not Aigean file(no zip/asdf/hdf5 in filename), so it should raise TypeError

def test_savedir():
    with pytest.raises(TypeError):
        download_isa('aigean_fan_20221208_170852.zip', save_dir= 7) #The save path is not of type string, so it should raise TypeError

def test_func():
    try:
        # some code which calls 'http://dokku-app.dokku.arc.ucl.ac.uk/isa-archive/query/?start_date=2022-12-05&stop_date=2022-12-07&instrument=Fand' 
        # and might cause requests.ConnectionError
        requests.get('http://dokku-app.dokku.arc.ucl.ac.uk/isa-archive/query/?start_date=2022-12-05&stop_date=2022-12-07&instrument=Fand')
    except requests.ConnectionError:
        return False

@responses.activate
def test_get_system_failure():
    responses.add(responses.GET,'http://dokku-app.dokku.arc.ucl.ac.uk/isa-archive/query/?start_date=2022-12-05&stop_date=2022-12-07&instrument=Fand',
        body=requests.ConnectionError())

    assert test_func() is False

# def test_net_connect():
#     with pytest.raises(ConnectionError):
#         net.query_isa()


def test_query_isa():
    query_result = [{'date': '2022-12-05',
        'filename': 'aigean_lir_20221205_191610.asdf',
        'instrument': 'lir',
        'resolution': 30,
        'time': '19:16:10',
        'xcoords': [500.0, 1100.0],
        'ycoords': [200.0, 500.0]},
        {'date': '2022-12-05',
        'filename': 'aigean_lir_20221205_194510.asdf',
        'instrument': 'lir',
        'resolution': 30,
        'time': '19:45:10',
        'xcoords': [800.0, 1400.0],
        'ycoords': [100.0, 400.0]}]
    assert query_result == query_isa('2022-12-05', '2022-12-05', 'lir')

def test_download_isa():
    download_isa('aigean_fan_20221208_170852.zip',save_dir='./')
    os.path.exists('aigean_fan_20221208_170852.zip')

