import json
import requests
from pathlib import Path
import datetime


# get current time
Now = datetime.datetime.now()
Time_now = Now.strftime("%Y-%m-%d")


def query_isa(start_date = str(Time_now), stop_date = str(Time_now), instrument= ''):
    """Query Irish Space Agency data by given start time, end time and date

    Parameters
    ----------
    start_date : str, optional
        The date the query started, by default str(Time_now)
    stop_date : str, optional
        The date the query ended, by default str(Time_now)
    instrument : str, optional
        Query device, by default ''

    Returns
    -------
    list
        return query information

    Raises
    ------
    ValueError
        Start date has a wrong date formats
    ValueError
        Stop date has a wrong date formats
    ValueError
        The difference between the end time and the start time is greater than 3 days
    ValueError
        Start time is greater than end time
    ConnectionError
        No network connection

    Examples
    --------
    >>> from net import query_isa
    >>> text = query_isa('2022-12-05', '2022-12-05', 'Fand')
    >>> print(text)
    [{'date': '2022-12-05', 'filename': 'aigean_fan_20221205_191610.zip', 'instrument': 'fand', 'resolution': 5, 'time': '19:16:10', 'xcoords': [75.0, 300.0], 'ycoords': [450.0, 500.0]}, {'date': '2022-12-05', 'filename': 'aigean_fan_20221205_192210.zip', 'instrument': 'fand', 'resolution': 5, 'time': '19:22:10', 'xcoords': [300.0, 525.0], 'ycoords': [50.0, 100.0]}, {'date': '2022-12-05', 'filename': 'aigean_fan_20221205_192810.zip', 'instrument': 'fand', 'resolution': 5, 'time': '19:28:10', 'xcoords': [450.0, 675.0], 'ycoords': [100.0, 150.0]}, {'date': '2022-12-05', 'filename': 'aigean_fan_20221205_193510.zip', 'instrument': 'fand', 'resolution': 5, 'time': '19:35:10', 'xcoords': [600.0, 825.0], 'ycoords': [350.0, 400.0]}, {'date': '2022-12-05', 'filename': 'aigean_fan_20221205_194010.zip', 'instrument': 'fand', 'resolution': 5, 'time': '19:40:10', 'xcoords': [675.0, 900.0], 'ycoords': [100.0, 150.0]}, {'date': '2022-12-05', 'filename': 'aigean_fan_20221205_194710.zip', 'instrument': 'fand', 'resolution': 5, 'time': '19:47:10', 'xcoords': [900.0, 1125.0], 'ycoords': [400.0, 450.0]}, {'date': '2022-12-05', 'filename': 'aigean_fan_20221205_195310.zip', 'instrument': 'fand', 'resolution': 5, 'time': '19:53:10', 'xcoords': [975.0, 1200.0], 'ycoords': [400.0, 450.0]}, {'date': '2022-12-05', 'filename': 'aigean_fan_20221205_195810.zip', 'instrument': 'fand', 'resolution': 5, 'time': '19:58:10', 'xcoords': [1050.0, 1275.0], 'ycoords': [250.0, 300.0]}, {'date': '2022-12-05', 'filename': 'aigean_fan_20221205_200510.zip', 'instrument': 'fand', 'resolution': 5, 'time': '20:05:10', 'xcoords': [1125.0, 1350.0], 'ycoords': [150.0, 200.0]}]

    """    
    # Check that the start date is in the correct format
    if not isinstance(start_date, str) or not judge_legal_date(start_date):
        raise TypeError('Start date has a wrong date formats')

    # Check that the stop date is in the correct format
    if not isinstance(stop_date, str) or not judge_legal_date(stop_date):
        raise TypeError('Stop date has a wrong date formats')    
    
    # Check the difference between the start date and end date
    if time_sub(start_date, stop_date)>3:
        raise ValueError('The difference between the end time and the start time is greater than 3 days')

    # Check if end date is before start date
    if time_sub(start_date, stop_date)<0:
        raise ValueError('Start time is greater than end time')   

    # The default input is all instrument
    if instrument != '':
        instrument = '&instrument='+instrument.lower()
    else:
        instrument = ''

    # default end date
    if stop_date != Time_now:
        stop_date = '&stop_date='+ stop_date
    else:
        stop_date = ''

    if start_date != Time_now:
        start_date = '&start_date='+ start_date
    else:
        start_date = ''        
    
        
    url_name = 'http://dokku-app.dokku.arc.ucl.ac.uk/isa-archive/query/?'+ start_date  +stop_date+ instrument

    # check network connection
    try:
        response = requests.get(url_name)
    except:
        raise ConnectionError('No network connection')

    text = response.text
    text = json.loads(text)
    return text

def judge_legal_date(date):
    """Check if the date format is correct

    Parameters
    ----------
    date : str
        date entered

    Returns
    -------
    bool
        Returns the bool value of whether the date format is correct
    """    
    try:
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        return True
    except:
        return False    
        
def time_sub(start_time, stop_time):
    """date subtraction

    Parameters
    ----------
    start_time : str
        Entered start time
    stop_time : str
        Entered stop time

    Returns
    -------
    int
        Returns the difference between two dates
    """    
    date_start = datetime.datetime.strptime(start_time, '%Y-%m-%d')
    date_stop = datetime.datetime.strptime(stop_time, '%Y-%m-%d')
    diffd = (date_stop-date_start).days
    return diffd


def download_isa(filename, save_dir=''):
    """Download the file according to the file name and save path and save it to the specified location

    Parameters
    ----------
    filename : str
        The name of the file to be downloaded
    save_dir : str, optional
        file save path, by default './'

    Raises
    ------
    ValueError
        File is non Aigean file
    ValueError
        File not exists on the network

    Examples
    --------
    >>> from net import download_isa
    >>> download_isa('aigean_fan_20221208_170852.zip', save_dir='')
    >>> import os
    >>> os.path.exists('aigean_fan_20221208_170852.zip')
    True
    """    
    
    # Determine whether the input file type meets the requirements
    if 'zip' not in filename and 'asdf' not in filename and 'hdf5' not in filename and 'csv' not in filename:
        raise TypeError('File is non Aigean file')

    # Check whether the input save path is str type
    if not isinstance(save_dir, str):
        raise TypeError('Save path is not of type str')  
    
    # Get files online
    url_name = 'http://dokku-app.dokku.arc.ucl.ac.uk/isa-archive/download/?filename=' + filename
    response = requests.get(url_name)

    # Check if this file exists on the network
    if response.status_code != 200:
        raise ValueError('File not exists on the network')

    # save document    
    path = Path(save_dir + filename)
    path.write_bytes(response.content)


# download_isa('aigean_ecn_20230115_042844.csv')
# text = query_isa(start_date='2023-1-13', instrument='ecne')
# print(text)
# download_isa('aigean_ecn_20230113_062216.csv')
# download_isa('aigean_fan_20221210_150420.zip')

# text = query_isa()
# print(text)





