from argparse import ArgumentParser
from aigeanpy.net import download_isa, query_isa
from aigeanpy.satmap import get_satmap, satmap
import requests

def aigean_today_process():
    """Command line function :Download today newest instrument data and generate png figure. If there has flag, save the png figure.
    
    Input in command line
    --------------------------
    --instrument (or use -i) <instrument>: str
        --instrument is a flag (or use -i), then add a str type name(One of the four instrument names (lir, manannan, fand or ecne))
    
    --saveplot (or use -s)
        --saveplot is a flag (or use -s), once use it, png figure will be saved.
    
    Output
    -------
    The data file in current folder
    
    Show the png figure in a window
    
    If has --saveplot (or -s), the png figrue will be saved in current folder
    
    Raises
    ------
    TypeError
        The instrument (arguments.instrument) do not has data in today
    
    Exception
        The instrument name is wrong, use one of the four instrument names (lir, manannan, fand or ecne)
    """
    #Read data from the command line
    parser = ArgumentParser(description="Download instrument data and generate png figure")
    parser.add_argument('--instrument', '-i', default= None, type = str,  help = 'One of the four instrument names (lir, manannan, fand or ecne)')
    parser.add_argument('--saveplot', '-s', action="store_true", default= False)
    arguments = parser.parse_args()
    
    #Convert to a unified lowercase case
    arguments.instrument = arguments.instrument.lower()
    if arguments.instrument != 'lir' and arguments.instrument != 'manannan' and arguments.instrument != 'fand' and arguments.instrument != 'ecne':
        raise Exception('The instrument name is wrong, use one of the four instrument names (lir, manannan, fand or ecne)')
    
    #Query the data summary for web 
    text = query_isa(instrument=arguments.instrument)
    
    #Check if has data from the query
    if len(text) == 0:
        raise TypeError('The instrument '+ arguments.instrument +' do not has data in today')
    
    #Get the newest filename
    filename = [x['filename'] for x in text]
    
    #Download the newest data base on the newest filename
    download_isa(filename[-1])
    
    #Check whether it is ence. If it is, output statements that it cannot be visualized
    if arguments.instrument == 'ecne':
        print('The typed file downloaded can not be visualised, data had be saved')
        exit (0) 
    
    #Chieve the visualise and check if it needs to be saved
    satmap_0 = get_satmap(filename[-1])
    satmap_0.visualise(save = arguments.saveplot)
    
def aigean_metadata_process():
    """Show the metadata information in specified local file name
    
    Input in command line
    --------------------------
    <filename_i> [<filename_j> ...]: str or str str ...
        Can input a file or list of them

    Output
    -------
    On command line interface
        Value available in the metadata (like archive, observatory, instrument, etc)
    
        If there are several files, the filename will be added before each values
    
        Files failed while being processed will be outputed in the end
    """
    #Read data from the command line
    parser = ArgumentParser(description="Metadata show in detail by enter file name")
    parser.add_argument('filename_list',  action = 'extend', nargs="+", type=str)
    arguments = parser.parse_args()
    
    #Initialize flag which will check if needs the filename added before data value
    flag_filename = 0
    
    #If one file only or 2 more
    if len(arguments.filename_list) == 1:
        satmap_nam = get_satmap(arguments.filename_list[0])
        print_meta(satmap_nam.meta, flag_filename)
    else:
        flag_filename = 1
        fail_file_list = []
        
        #Print part and fail_file_list created
        for filenamess in arguments.filename_list:
            try:
                satmap_nam = get_satmap(filenamess)
                print_meta(satmap_nam.meta, flag_filename, filenamess)
            except:
                fail_file_list.append(filenamess)
       
        # Print failed files name 
        if len(fail_file_list) != 0:
            fail_file_print(fail_file_list)

def aigean_mosaic_process():
    """Accept two or more filenames and make a mosaic form figure
    
    Input in command line
    --------------------------
    --resolution <number> : int
        Enter a non-0 natural number as the resolution of the image
    
    <filename_i> [<filename_j> ...]: str or str str ...
        Can input a file or list of them

    Raises:
        TypeError
            The internet is wrong, Need internet to check if the file with the filename is inside the web: http://dokku-app.dokku.arc.ucl.ac.uk
        TypeError
            The filename ('filenames') is wrong
        Exception
            The file number is: ' + str(len(arguments.filename_list)) +' which is less than 2(min numbers)

    Output
    -------
    On command line interface
        save_name for png figure in str
    
    png type file will be saved in current folder for the mosaiced figure with ordered resolution
    """
    #Read data from the command line
    parser = ArgumentParser(description="Achieve the visualisation of the resulting satmap and return the filename")
    parser.add_argument('--resolution', type = int)
    parser.add_argument('filename_list',  action = 'extend', nargs='+', type=str)
    arguments = parser.parse_args()
    
    #Check if all filenames are right
    for filenames in arguments.filename_list:
        url_name = 'http://dokku-app.dokku.arc.ucl.ac.uk/isa-archive/download/?filename=' + filenames
        
        #Check if the internet had problem
        try:
            response = requests.get(url_name)
        except:
            raise TypeError('The internet is wrong, Need internet to check if the file with the filename is inside the web: http://dokku-app.dokku.arc.ucl.ac.uk')
        
        #Check the filename is valid
        if response.status_code != 200:
            raise TypeError('The filename ('+ filenames +') is wrong')
    
    #Check if the file number is >=2
    if len(arguments.filename_list) < 2:
        raise Exception('The file number is: ' + str(len(arguments.filename_list)) +' which is less than 2(min numbers)')
    
    #Download the data from web if it is missing
    for filename in arguments.filename_list:
        download_isa(filename)
    
    satmap_a = get_satmap(arguments.filename_list[0])
    
    #Achieve the mosaic instruments
    for fielname in arguments.filename_list[1:]:
        satmap_b = get_satmap(fielname)
        satmap_a = satmap_a.mosaic(satmap_b, resolution = arguments.resolution)
    
    #Achieve visualise(save figure part) and print the filename
    satmap_a.visualise(save = True)
    time = satmap_a.meta['time'].replace(':', '')
    date = satmap_a.meta['date'].replace('-', '')
    save_name = satmap_a.meta['observatory'].lower() +'_'+satmap_a.meta['instrument'].lower()[:3]+'_'+ date +'_'+time+'_'+ 'mosaic' +'.png'
    print(save_name)



def print_meta(meta, flag_filename, filename=' :'):
    """Print the meta data

    Parameters
    ----------
        meta: dict
            Meta data, including 'instrument','observatory','resolution','time','date','xcoords','ycoords', 'archive' message
        flag_filename: int(0 or 1)
            When it is 0, filename do not be printed; When it is 1, filename will be printed
        filename: (str, optional)
            File name. Defaults to ' :'.
    
    Output
    -------
    Print the metadata('instrument','observatory','resolution','time','date','xcoords','ycoords', 'archive' message)
    """
    if flag_filename:
        filenamess = filename + ':'
    else:
        filenamess = ''

    #Print part
    print(filenamess, 'archive: ISA', sep='')
    print(filenamess, 'observatory: ', meta['observatory'], sep='')
    print(filenamess, 'instrument: ', meta['instrument'], sep='')
    print(filenamess, 'obs_date: ', meta['date'], ' ', meta['time'], sep='')
    print(filenamess, 'resolution: ' + str(meta['resolution']), sep='')
    print(filenamess, 'xcoords: ' + str(meta['xcoords']), sep='')
    print(filenamess, 'ycoords: ' + str(meta['ycoords']), sep='')
    
def fail_file_print(fail_file_list: list):
    """Print the file which is failed to open

    Parameters
    ----------
        fail_file_list (list): 
            The str list of failed file names
            
    Output
    ------
    Print all the failed file names  
    """
    print('These files failed while being processed')
    for fail_file_name in fail_file_list:
        print(' - ', fail_file_name)
        
