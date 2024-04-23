import json
import numpy as np
import asdf
import h5py
from zipfile import ZipFile
from io import BytesIO
import matplotlib.pyplot as plt
import math
from skimage.transform import rescale
import os

class satmap():
    
    def __init__(self, meta, data, shape, fov, centre) -> None:
        """initialization class

        Parameters
        ----------
        meta : dict
            Meta data, including 'instrument','observatory','resolution','time','date','xcoords','ycoords', 'archive' message
        data : array
            Image information captured by remote sensing satellites
        shape : turple
            The shape of the image information
        fov : turple
            Field of View of image   
        centre : turple
            image center point

        Raises
        ------
        ValueError
            The data shape does not match the input shape
        """        
      
        self.meta = meta
        self.data = data
        self.shape = shape
        self.fov = fov
        self.centre = centre

        if not isinstance(meta, dict):
            raise TypeError('The data type of meta is wrong')
        if not isinstance(data, np.ndarray):
            raise TypeError('The data type of data is wrong')    
        if not isinstance(fov, tuple):
            raise TypeError('The data type of fov is wrong')      
        if not isinstance(centre, tuple):
            raise TypeError('The data type of centre is wrong')  
        if data.shape != self.shape:
            raise ValueError('The data shape does not match the input shape')    

    def __sub__(self, another_lirmap):
        """ - image 

        Parameters
        ----------
        another_lirmap : class
            another class of input

        Returns
        -------
        class
            Returns the new class after + two classes

        Raises
        ------
        ValueError
            The two maps are from same date and from same instrument, can not -
        ValueError
            The two maps is not overlap, can not -

        Examples
        --------
        >>> from satmap import get_satmap
        >>> lir_map1 = get_satmap('aigean_fan_20221208_170852.zip')
        >>> lir_map2 = get_satmap('aigean_fan_20221210_150420.zip')
        >>> from satmap import satmap
        >>> SatMap = lir_map1 - lir_map2    
        >>> SatMap.meta                     
        {'instrument': 'Fand', 'observatory': 'Aigean', 'resolution': 5, 'time': '17:08:52', 'date': '2022-12-08', 'xcoords': [1200, 1275], 'ycoords': [450, 500], 'archive': 'ISA'}
        >>> SatMap.data[5,9]
        0.0
        >>> SatMap.data[0,0] 
        0.0
        """        
        # judge type
        if not isinstance(another_lirmap, satmap):
            raise TypeError('The input is not of satmap class type')

        # when they are taken on different days, but still from the same instrument.
        if self.meta['date'] == another_lirmap.meta['date'] and self.meta['instrument'] == another_lirmap.meta['instrument']:
            raise ValueError('The two maps are from same date and from same instrument, can not - ')
        else:
            if isoverlap(self.meta, another_lirmap.meta) == True:
                meta = self.meta.copy()
                
                # Get the earth coordinates of the edge
                x11 = self.meta['xcoords'][0]
                x12 = self.meta['xcoords'][1]
                y11 = self.meta['ycoords'][0]
                y12 = self.meta['ycoords'][1]
                x21 = another_lirmap.meta['xcoords'][0]
                x22 = another_lirmap.meta['xcoords'][1]
                y21 = another_lirmap.meta['ycoords'][0]
                y22 = another_lirmap.meta['ycoords'][1]

                # Get the sub coords
                meta['xcoords'] = [max(x11, x21), min(x12, x22)]
                meta['ycoords'] = [max(y11, y21), min(y12, y22)]

                # save coords
                x = meta['xcoords']
                y = meta['ycoords']

                
                # earth coords to pixel coords 
                pixel_xy = earth_to_pixel(meta, meta['xcoords'][1], meta['ycoords'][0])

                # creat sub data 
                data = np.zeros([pixel_xy[0], pixel_xy[1]])

                # get the coordinates of the upper left point
                meta['xcoords'] = [x21, x22]
                meta['ycoords'] = [y21, y22]
                pixel_start_2 = earth_to_pixel(meta,x[0], y[1])
                pixel_end_2 = earth_to_pixel(meta,x[1], y[0])

                # get the coordinates of the lower right point
                meta['xcoords'] = [x11, x12]
                meta['ycoords'] = [y11, y12]
                pixel_start_1 = earth_to_pixel(meta,x[0], y[1])
                pixel_end_1 = earth_to_pixel(meta, x[1], y[0])

                # assign value to data
                data[:,:] = self.data[pixel_start_1[0]:pixel_end_1[0], pixel_start_1[1]:pixel_end_1[1]] - another_lirmap.data[pixel_start_2[0]:pixel_end_2[0], pixel_start_2[1]:pixel_end_2[1]]
                
                # assign values to other elements of the satmap class
                meta['xcoords'] = x
                meta['ycoords'] = y

                fov = (meta['xcoords'][1] - meta['xcoords'][0], meta['ycoords'][1] - meta['ycoords'][0])
                centre = ((meta['xcoords'][1] + meta['xcoords'][0])/2, (meta['ycoords'][1] + meta['ycoords'][0])/2)
                shape = data.shape

                # create new satmap class
                map_sub = type(self)(meta, data, shape, fov, centre)
                return  map_sub
            else:
                raise ValueError('The two maps is not overlap, can not -')    


    def __add__(self, another_lirmap):
        """ - image

        Parameters
        ----------
        another_lirmap : class
            another class of input

        Returns
        -------
        class
            Returns the new class after + two classes

        Raises
        ------
        ValueError
            The two maps are from different date or from different instrument, can not +

        Examples
        --------
        # >>> from satmap import get_satmap
        # >>> lir_map1 = get_satmap('aigean_fan_20221205_191610.zip')
        # >>> lir_map2 = get_satmap('aigean_fan_20221205_192210.zip')
        # >>> from satmap import satmap
        # >>> SatMap = lir_map1 + lir_map2
        # >>> SatMap.meta                     
        # {'instrument': 'Fand', 'observatory': 'Aigean', 'resolution': 5, 'time': '19:16:10', 'date': '2022-12-05', 'xcoords': [75, 525], 'ycoords': [50, 500], 'archive': 'ISA'}
        # >>> SatMap.data[2,4] 
        # 636.3636363636364
        # >>> SatMap.data[9,15] 
        # 633.939393939394
        """        

        if not isinstance(another_lirmap, satmap):
            raise TypeError('Input is not satmap class')
        # same instrument (and with the same resolution) taken on the same day
        # Determine whether it is the same device on the same day
        if self.meta['resolution'] == another_lirmap.meta['resolution']:
            meta = self.meta.copy()

            # Get the earth coordinates of the edge
            x11 = self.meta['xcoords'][0]
            x12 = self.meta['xcoords'][1]
            y11 = self.meta['ycoords'][0]
            y12 = self.meta['ycoords'][1]
            x21 = another_lirmap.meta['xcoords'][0]
            x22 = another_lirmap.meta['xcoords'][1]
            y21 = another_lirmap.meta['ycoords'][0]
            y22 = another_lirmap.meta['ycoords'][1]

            # get the coordinates of the add map
            meta['xcoords'] = [min(x11, x21), max(x12, x22)]
            meta['ycoords'] = [min(y11, y21), max(y12, y22)]

            # earth coords to pixel coords 
            pixel_xy = earth_to_pixel(meta, meta['xcoords'][1], meta['ycoords'][0])

            # create add map data
            data = np.zeros([pixel_xy[0], pixel_xy[1]])

            # get the upper right and lower left point of the pixel array
            pixel_start_1 = np.array(earth_to_pixel(meta, x11, y12))
            pixel_end_1 = np.array(earth_to_pixel(meta, x12, y11))
            pixel_start_2 = np.array(earth_to_pixel(meta, x21, y22))
            pixel_end_2 = np.array(earth_to_pixel(meta, x22, y21))

            # assign the value to the data
            pixel_start_1[0], pixel_end_1[0] = handle_edge(pixel_start_1[0], pixel_end_1[0], self.data.shape[0])
            pixel_start_1[1], pixel_end_1[1] = handle_edge(pixel_start_1[1], pixel_end_1[1], self.data.shape[1])

            pixel_start_2[0], pixel_end_2[0] = handle_edge(pixel_start_2[0], pixel_end_2[0], another_lirmap.data.shape[0])
            pixel_start_2[1], pixel_end_2[1] = handle_edge(pixel_start_2[1], pixel_end_2[1], another_lirmap.data.shape[1])            


            # handle edge

            data[pixel_start_1[0]:pixel_end_1[0], pixel_start_1[1]:pixel_end_1[1]] = self.data[:,:]
            data[pixel_start_2[0]:pixel_end_2[0],pixel_start_2[1]:pixel_end_2[1]] = another_lirmap.data[:,:]
 
            # assign values to other elements of the satmap class
            fov = (meta['xcoords'][1] - meta['xcoords'][0], meta['ycoords'][1] - meta['ycoords'][0])
            centre = ((meta['xcoords'][1] + meta['xcoords'][0])/2, (meta['ycoords'][1] + meta['ycoords'][0])/2)
            shape = data.shape

            # create new satmap for addmap
            map_add = type(self)(meta, data, shape, fov, centre)
            return  map_add               
                
        else:
            raise ValueError('The two maps are from different date or from different instrument, can not +')



    def mosaic(self, another_satmap, resolution='', padding=True):
        """mosaic operation on two classes

        Parameters
        ----------
        another_satmap : class
            another class of input
        resolution : int, optional
            image resolution, by default ''
        padding : bool, optional
            Whether to perform padding operation, by default True

        Returns
        -------
        class
            Returns the class that completes the masaic operation

        Examples
        --------
        >>> from satmap import get_satmap
        >>> lir_map1 = get_satmap('aigean_lir_20221205_191610.asdf')
        >>> lir_map2 = get_satmap('aigean_man_20221205_194510.hdf5')
        >>> from satmap import satmap
        >>> SatMap = satmap.mosaic(lir_map1, lir_map2)
        >>> SatMap.meta                     
        {'instrument': 'Lir', 'observatory': 'Aigean', 'resolution': 15, 'time': '19:16:10', 'date': '2022-12-05', 'xcoords': [500, 1200], 'ycoords': [200, 500], 'archive': 'ISA'}
        >>> SatMap.data[2,4] 
        563.4006734006733
        >>> SatMap.data[9,15] 
        618.5530303030301
        """        
        
        # judge type
        if not isinstance(another_satmap, satmap):
            raise TypeError('The input is not of satmap class type')

        if not isinstance(resolution, int) and resolution!='':
            raise TypeError('The resolution is not int type')    
        
        if not isinstance(padding, bool):
            raise TypeError('The padding is not bool type')

 
        map_self_meta = self.meta.copy()
        map_another_meta = another_satmap.meta.copy()
        
        # use the min resolution as both resolution
        if resolution == '':
            resolution = min(self.meta['resolution'], another_satmap.meta['resolution'])
            map_self_meta['resolution'] = resolution
            map_another_meta['resolution'] = resolution
            map_self_data = rescale(self.data, self.meta['resolution']/resolution)
            map_another_data = rescale(another_satmap.data, another_satmap.meta['resolution']/resolution)

        # use the given resolution    
        else:
            # judge the value of resolution
            if resolution<=0:
                raise ValueError('resolution less than 0')   
            map_self_data = rescale(self.data, self.meta['resolution']/resolution)
            map_another_data = rescale(another_satmap.data, another_satmap.meta['resolution']/resolution)
            map_self_meta['resolution'] = resolution
            map_another_meta['resolution'] = resolution

        # assign the value to other elements of satmap class
        map_self_fov = (map_self_meta['xcoords'][1] - map_self_meta['xcoords'][0], map_self_meta['ycoords'][1] - map_self_meta['ycoords'][0])
        map_self_shape = map_self_data.shape
        map_self_centre = ((map_self_meta['xcoords'][1] + map_self_meta['xcoords'][0])/2, (map_self_meta['ycoords'][1] + map_self_meta['ycoords'][0])/2)

        map_another_fov = (map_another_meta['xcoords'][1] - map_another_meta['xcoords'][0], map_another_meta['ycoords'][1] - map_another_meta['ycoords'][0])
        map_another_shape = map_another_data.shape
        map_another_centre = ((map_another_meta['xcoords'][1] + map_another_meta['xcoords'][0])/2, (map_another_meta['ycoords'][1] + map_another_meta['ycoords'][0])/2)

        # creat new satmap class
        map_self = type(self)(map_self_meta, map_self_data, map_self_shape, map_self_fov, map_self_centre)
        map_another = type(self)(map_another_meta, map_another_data, map_another_shape, map_another_fov, map_another_centre) 

        # get the mosaic satmap class
        map_mosaic = map_self + map_another
        if padding:    
            return map_mosaic   
            
        else:
            # judge 4 area1
            # satmap 1 area
            area1 = map_self.data.shape[0]*map_self.data.shape[1]
            # satmap 2 area
            area2 = map_another.data.shape[0]*map_another.data.shape[1]
     
            data_process = np.copy(map_mosaic.data).astype(float)
            
            # row area
            data_row = []
            for i in range(data_process.shape[0]):
                if 0 not in data_process[i,:]:
                    data_row.append(data_process[i,:])
            data_row = np.array(data_row)
            area3 = data_row.shape[0]*data_row.shape[1]
            
            # column area
            data_column = []
            for i in range(data_process.shape[1]):
                if 0 not in data_process[:,i]:
                    data_column.append(data_process[:,i])
            data_column = np.array(data_column)
            area4 = data_column.shape[0]*data_column.shape[1]
            
            # get the index of max area
            area_list = [area1, area2, area3, area4]
            area_index = area_list.index(max(area_list))
            
            # return different data according to the index
            if area_index == 0:
                map_mosaic.data = self.data
            if area_index == 1:
                map_mosaic.data = another_satmap.data
            if area_index == 2:
                map_mosaic.data = data_row
            if area_index == 3:
                map_mosaic.data = data_column        
            
            return map_mosaic
                        

    def visualise(self, save=False, savepath=''):
        """Visual operation

        Parameters
        ----------
        save : bool, optional
            Whether to save the image, by default False
        savepath : str, optional
            saved path, by default './'
        Examples
        --------
        >>> from satmap import get_satmap
        >>> lir_map = get_satmap('aigean_fan_20221205_191610.zip')
        >>> satmap.visualise(lir_map,save=True)
        >>> import os 
        >>> os.path.exists('Aigean_Fand_2022-12-05_19_16_10_extra.png')
        True
        """        
        
        # judge type
        if not isinstance(save, bool):
            raise TypeError('the input save is not bool type')

        if not isinstance(savepath, str):
            raise TypeError('The saved path is not str type')    

        # plot array in earth coordinates
        plt.imshow(self.data, origin='lower', 
        extent=[self.meta['xcoords'][0], self.meta['xcoords'][1], 
        self.meta['ycoords'][0], self.meta['ycoords'][1]])
        
        # save image
        if save:
            time = self.meta['time'].replace(':', '')
            date = self.meta['date'].replace('-', '')
            instrument = self.meta['instrument'].lower()[:3]
            save_name = self.meta['observatory'] +'_'+instrument+'_'+date+'_'+time+'_'+'mosaic'+'.png'
            full_name = os.path.join(savepath, save_name)
            plt.savefig(full_name)

        # plot image    
        else:
            plt.show()   
  
def pixel_to_earth(meta, pixel_x, pixel_y):
    """Conversion from pixel coordinates to earth coordinates

    Parameters
    ----------
    meta : dict
        Meta data, including 'instrument','observatory','resolution','time','date','xcoords','ycoords', 'archive' message    
    pixel_x : int
        input pixel x-coordinate
    pixel_y : int
        input pixel y-coordinate

    Returns
    -------
    turple
        returns an earth coordinate pair
    """        
    earth_x = int (meta['xcoords'][0] + pixel_y * meta['resolution']/2)
    earth_y = int (meta['ycoords'][1] - pixel_x * meta['resolution']/2)
    earth = (earth_x, earth_y)
    return earth


def earth_to_pixel(meta, earth_x, earth_y):
    """Conversion from earth coordinates to pixel coordinates

    Parameters
    ----------
    meta : dict
        Meta data, including 'instrument','observatory','resolution','time','date','xcoords','ycoords', 'archive' message
    earth_x : int
        input earth x-coordinate
    earth_y : int
        input earth y-coordinate

    Returns
    -------
    turple
        returns an pixel coordinate pair
    """        
    
    # Value check
    if earth_x < meta['xcoords'][0] or earth_x > meta['xcoords'][1] or earth_y < meta['ycoords'][0] or earth_y > meta['ycoords'][1]:
        raise ValueError('Earth coordinates out of range') 
    
    # Get the pixel coordinates
    pixel_x = round(abs((earth_y-meta['ycoords'][1])/meta['resolution']))
    pixel_y= round((earth_x-meta['xcoords'][0])/meta['resolution'])
    pixel = (pixel_x, pixel_y)
    return pixel   

def handle_edge(start, end, shape):
    if end - start != shape:
        if start>0:
            start = end - shape
        else:
            end = start + shape    
    return start, end        

def isoverlap(meta1, meta2):
    """Determine whether two images overlap

    Parameters
    ----------
    meta1 : dict
        Meta data in a file
    meta2 : dict
        Meta data in another file

    Returns
    -------
    bool
        Returns a bool value to determine whether it overlaps
    """    
    if meta1['xcoords'][0] >= meta2['xcoords'][1] or meta1['xcoords'][1] <= meta2['xcoords'][0] or meta1['ycoords'][1]<= meta2['ycoords'][0] or meta1['ycoords'][0] >= meta2['ycoords'][1]:
        return False
    else:
        return True



def get_satmap(filename):
    """read different files

    Parameters
    ----------
    filename : str
        input file name

    Returns
    -------
    class
        Return satmap class, including meta, data, shape, fov, centre
    """    
    if 'hdf5' in filename:
        meta, data = read_hdf5(filename)         

    elif 'asdf' in filename:
        meta,data = read_asdf(filename)

    elif 'zip' in filename:
        meta, data = read_zip(filename)
    else:
        raise ValueError('The input file type is wrong')    

    shape = data.shape
    fov = cal_fov(meta)
    centre = cal_centre(meta)
    SatMap = satmap(meta, data, shape, fov, centre)    
    return SatMap


def process_meta(meta_file):
    """read meta from different files

    Parameters
    ----------
    meta_file : dict
        Dictionary file containing meta data

    Returns
    -------
    dict
        Return meta dictionary data
    """    
    meta_list = ['instrument','observatory','resolution','time','date','xcoords','ycoords', 'archive']
    meta = {}
    for key in meta_list:
        try:
            meta[key] = meta_file[key]
        except:
            meta[key] = ''
        if 'coords' in key:
            meta[key] = tuple(map(int,meta[key]))
    return meta


def read_hdf5(filename):
    """read hdf5 file

    Parameters
    ----------
    filename : str
        file name

    Returns
    -------
    dict, np.array 
        Returns the read image data and meta dictionary
    """    
    f = h5py.File(filename, 'r')
    group = f[list(f.keys())[0]]
    data = group['data']
    data = np.array(data)
    meta = process_meta(group.attrs)
    f.close()
    return meta, data


def read_asdf(filename):
    """read asdf file

    Parameters
    ----------
    filename : str
        file name

    Returns
    -------
    dict, np.array 
        Returns the read image data and meta dictionary
    """    
    af = asdf.open(filename)
    meta = process_meta(af)         
    data = np.array(af['data'])
    af.close()
    return meta, data


def read_zip(filename):
    """read zip file

    Parameters
    ----------
    filename : str
        file name

    Returns
    -------
    dict, np.array 
        Returns the read image data and meta dictionary
    """     
    zfile = ZipFile(filename, 'r')
    jsonf = json.load(BytesIO(zfile.read(zfile.namelist()[0])))
    meta = process_meta(jsonf)
    data = np.load(BytesIO(zfile.read(zfile.namelist()[1])))
    return meta, data

def cal_fov(meta):
    """Calculate the field of view of an image

    Parameters
    ----------
    meta : dict
        input meta data

    Returns
    -------
    turple
        field of view of an image
    """    
    fov = (meta['xcoords'][1] - meta['xcoords'][0], meta['ycoords'][1] - meta['ycoords'][0])
    return fov

def cal_centre(meta):
    """Calculate the center point of the image

    Parameters
    ----------
    meta : dict
        input meta data

    Returns
    -------
    turple
        The coordinates of the center point of the image
    """    
    centre = ((meta['xcoords'][1] + meta['xcoords'][0])/2, (meta['ycoords'][1] + meta['ycoords'][0])/2)
    return centre


#  test add map
# lir_map1 = get_satmap('aigean_fan_20221205_191610.zip')
# lir_map2 = get_satmap('aigean_fan_20221205_192210.zip')
# SatMap = lir_map1 + lir_map2
# plt.imshow(SatMap.data)
# plt.show()
# print(SatMap.meta)



# test sub map
# lir_map1 = get_satmap('aigean_fan_20221208_170852.zip')
# lir_map2 = get_satmap('aigean_fan_20221210_150420.zip')
# SatMap = lir_map1 - lir_map2
# plt.imshow(SatMap.data)
# plt.show()
# print(SatMap.meta)

# test masaic
# lir_map1 = get_satmap('aigean_lir_20221205_191610.asdf')
# lir_map2 = get_satmap('aigean_man_20221205_194510.hdf5')
# SatMap = satmap.mosaic(lir_map1, lir_map2, resolution=1)
# plt.imshow(SatMap.data)
# plt.show()
# print(SatMap.meta)


# test visualise
# lir_map1 = get_satmap('aigean_fan_20221205_191610.zip')
# satmap.visualise(lir_map1, True)
# print(lir_map1.meta)



