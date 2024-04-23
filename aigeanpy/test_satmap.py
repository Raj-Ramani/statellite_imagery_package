import pytest
from  aigeanpy.satmap import get_satmap, satmap, pixel_to_earth, earth_to_pixel, isoverlap, read_zip, read_asdf, read_hdf5, cal_fov, cal_centre
import numpy as np
import os
from aigeanpy.net import  download_isa

download_isa('aigean_lir_20221205_191610.asdf')
download_isa('aigean_fan_20221208_170852.zip')
download_isa('aigean_fan_20221210_150420.zip')
download_isa('aigean_lir_20221205_194510.asdf')
download_isa('aigean_fan_20221205_192210.zip')
download_isa('aigean_lir_20221206_181924.asdf')
download_isa('aigean_fan_20221205_191610.zip')
download_isa('aigean_man_20221205_194510.hdf5')

def test_shape():
    with pytest.raises(ValueError):
        lir_map = get_satmap('aigean_lir_20221205_191610.asdf')
        lir_map.shape = [2,2]
        satmap(lir_map.meta, lir_map.data, lir_map.shape, lir_map.fov, lir_map.centre)
#lir_map.shape != lir_map.data.shape, so it should raise ValueError
 

def test_meta_type():
    with pytest.raises(TypeError):
        lir_map = get_satmap('aigean_lir_20221205_191610.asdf')
        lir_map.meta = [1,2]
        satmap(lir_map.meta, lir_map.data, lir_map.shape, lir_map.fov, lir_map.centre)
# [1,2] is list but not a dict for meta type, so it should raise TypeError

def test_data_type():
    with pytest.raises(TypeError):
        lir_map = get_satmap('aigean_lir_20221205_191610.asdf')
        data = [[1,2],[1,0]]
        lir_map.data = data
        satmap(lir_map.meta, lir_map.data, lir_map.shape, lir_map.fov, lir_map.centre)
 # [[1,2],[1,0]] is list but not array for data type, so it should raise TypeError

def test_fov_type():
    with pytest.raises(TypeError):
        lir_map = get_satmap('aigean_lir_20221205_191610.asdf')
        lir_map.fov = [225,50]
        satmap(lir_map.meta, lir_map.data, lir_map.shape, lir_map.fov, lir_map.centre)
 #[225,50] is list but not tuple for fov type, so it should raise TypeError

def test_centre_type():
    with pytest.raises(TypeError):
        lir_map = get_satmap('aigean_lir_20221205_191610.asdf')
        lir_map.centre = [187.5,475.0]
        satmap(lir_map.meta, lir_map.data, lir_map.shape, lir_map.fov, lir_map.centre)
 #[187.5, 475.0] is list but not tuple for centre type, so it should raise TypeError

def test_sub():
    lir_map1 = get_satmap('aigean_fan_20221208_170852.zip')
    lir_map2 = get_satmap('aigean_fan_20221210_150420.zip')
    left_bottom_1 = (lir_map1.meta['xcoords'][0],lir_map1.meta['ycoords'][0])
    right_top_1 = (lir_map1.meta['xcoords'][1],lir_map1.meta['ycoords'][1])
    left_bottom_2 = (lir_map2.meta['xcoords'][0],lir_map2.meta['ycoords'][0])
    right_top_2 = (lir_map2.meta['xcoords'][1],lir_map2.meta['ycoords'][1])
    SatMap = lir_map1 - lir_map2
    lb_SatMap = (SatMap.meta['xcoords'][0],SatMap.meta['ycoords'][0])
    rt_SatMap = (SatMap.meta['xcoords'][1],SatMap.meta['ycoords'][1])
    assert lb_SatMap,rt_SatMap == (left_bottom_1,right_top_2)
    assert SatMap.data[5,9] == 0.0
    assert SatMap.data[0,0] == 0.0

def test_sub_date():
    with pytest.raises(ValueError):
        lir_map1 = get_satmap('aigean_lir_20221205_191610.asdf')
        lir_map2 = get_satmap('aigean_lir_20221205_194510.asdf')
        lir_map1 - lir_map2
#These two satmaps are taken from the same date and same instrument, so cannot'-'
#it should raise ValueError

def test_sub_type():
    with pytest.raises(TypeError):
        lir_map1 = get_satmap('aigean_fan_20221205_192210.zip')
        lir_map2 = 7
        lir_map1 - lir_map2
#The second input is an integer, not the satmap class, so it should raise TypeError       

def test_non_overlap():
    with pytest.raises(ValueError):
        lir_map1 = get_satmap('aigean_fan_20221205_192210.zip')
        lir_map2 = get_satmap('aigean_fan_20221205_191610.zip')
        lir_map1 - lir_map2
#These two satmaps are not overlap, so it should raise ValueError

def test_add():
    lir_map1 = get_satmap('aigean_fan_20221205_191610.zip')
    lir_map2 = get_satmap('aigean_fan_20221205_192210.zip')
    left_bottom = (lir_map1.meta['xcoords'][0],lir_map2.meta['ycoords'][0])
    right_top = (lir_map2.meta['xcoords'][1],lir_map1.meta['ycoords'][1])
    SatMap = lir_map1 + lir_map2
    lb_SatMap = (SatMap.meta['xcoords'][0],SatMap.meta['ycoords'][0])
    rt_SatMap = (SatMap.meta['xcoords'][1],SatMap.meta['ycoords'][1])
    assert lb_SatMap,rt_SatMap == (left_bottom,right_top)
    assert SatMap.data[2,4] == pytest.approx(636.3636363636364)
    assert SatMap.data[9,15] == pytest.approx(633.939393939394)

def test_add_type():
    with pytest.raises(TypeError):
        lir_map1 = get_satmap('aigean_fan_20221205_192210.zip')
        lir_map2 = 7
        lir_map1 + lir_map2
#The second input is an integer, not the satmap class, so it should raise TypeError  

def test_add_date():
    with pytest.raises(ValueError):
        lir_map1 = get_satmap('aigean_fan_20221208_170852.zip')
        lir_map2 = get_satmap('aigean_lir_20221206_181924.asdf')
        lir_map1 + lir_map2
#These two satmap are taken from different dates, so cannot '+', 
#it should raise ValueError

def test_add_instrument():
    with pytest.raises(ValueError):
        lir_map1 = get_satmap('aigean_fan_20221205_191610.zip')
        lir_map2 = get_satmap('aigean_lir_20221205_191610.asdf')
        lir_map1 + lir_map2
#These two satmap are taken from same date but by different instruments,
#so cannot '+', it should raise ValueError

def test_mosaic():
    lir_map1 = get_satmap('aigean_lir_20221205_191610.asdf')
    lir_map2 = get_satmap('aigean_man_20221205_194510.hdf5')
    SatMap = satmap.mosaic(lir_map1,lir_map2)
    left_bottom = (lir_map1.meta['xcoords'][0],lir_map1.meta['ycoords'][0])
    right_top = ((lir_map2.meta['xcoords'][1],lir_map1.meta['ycoords'][1]))
    lb_SatMap = (SatMap.meta['xcoords'][0],SatMap.meta['ycoords'][0])
    rt_SatMap = (SatMap.meta['xcoords'][1],SatMap.meta['ycoords'][1])
    assert lb_SatMap,rt_SatMap == (left_bottom,right_top)
    assert SatMap.data[2,4] == pytest.approx(563.4006734006733)
    assert SatMap.data[9,15] == pytest.approx(618.5530303030301)

def test_mosaic_satmap_type():
    with pytest.raises(TypeError):
        lir_map1 = get_satmap('aigean_lir_20221205_191610.asdf')
        lir_map2 = 7
        satmap.mosaic(lir_map1,lir_map2,resolution='15',padding=True)
#The second input is an integer, not the satmap class, so it should raise TypeError       

def test_mosaic_resolution_type():
    with pytest.raises(TypeError):
        lir_map1 = get_satmap('aigean_lir_20221205_191610.asdf')
        lir_map2 = get_satmap('aigean_man_20221205_194510.hdf5')
        satmap.mosaic(lir_map1,lir_map2,resolution=15.0,padding=True)
#The resolution 15.0 is not int and str, so it should raise TypeError

def test_mosaic_padding_type():
    with pytest.raises(TypeError):
        lir_map1 = get_satmap('aigean_lir_20221205_191610.asdf')
        lir_map2 = get_satmap('aigean_man_20221205_194510.hdf5')
        satmap.mosaic(lir_map1,lir_map2,resolution='15',padding=7)
#The padding 7 is not bool type, so it should raise TypeError

def test_visualise():
    lir_map1 = get_satmap('aigean_fan_20221205_191610.zip')
    satmap.visualise(lir_map1, True)
    os.path.exists('Aigean_Fand_2022-12-05_19_16_10_extra.png')

def test_visualise_save_type():
    with pytest.raises(TypeError):
        lir_map1 = get_satmap('aigean_fan_20221205_191610.zip')
        satmap.visualise(lir_map1, save=7,savepath='./')
#The input save=7 is not a bool type, so it should raise TypeError

def test_visualise_savepath_type():
    with pytest.raises(TypeError):
        lir_map1 = get_satmap('aigean_fan_20221205_191610.zip')
        satmap.visualise(lir_map1, save=True,savepath=7)
#The input savepath is not str, so it should raise TypeError

def test_pixel_to_earth():
    lir_map2 = get_satmap('aigean_man_20221205_194510.hdf5')
    earth = pixel_to_earth(lir_map2.meta, 2, 2)
    assert (765, 385) == earth

def test_earth_to_pixel():
    lir_map2 = get_satmap('aigean_fan_20221205_191610.zip')
    pixel = earth_to_pixel(lir_map2.meta,100,470)
    assert (6, 5) == pixel

def test_earth_to_pixel_value():
    with pytest.raises(ValueError):
         lir_map = get_satmap('aigean_fan_20221205_191610.zip')
         earth_to_pixel(lir_map.meta,100,100)
#earth_y=100 < lir_map.meta['ycoords'][0]=450, so it should raise ValueError

def test_isoverlap():
    lir_map1 = get_satmap('aigean_lir_20221205_191610.asdf')
    lir_map2 = get_satmap('aigean_lir_20221206_181924.asdf')
    meta1 = lir_map1.meta
    meta2 = lir_map2.meta
    assert isoverlap(meta1,meta2)

def test_get_satmap_file_type():
    with pytest.raises(ValueError):
        get_satmap('aigean_lir_20221205_191610.txt')
#The file 'txt' doesn't belong to Aigean file, so it should raise ValueError


def test_read_zip():
    fand_map = get_satmap('aigean_fan_20221205_191610.zip')
    meta = fand_map.meta
    data = fand_map.data
    answer = (meta,data)

    result = read_zip('aigean_fan_20221205_191610.zip')
    assert type(answer) == type(result)
    assert len(answer) == len(result)
    assert answer[0] == result[0] and answer[1].all() == result[1].all()

def test_read_asdf():
    lir_map = get_satmap('aigean_lir_20221205_191610.asdf')
    meta = lir_map.meta
    data = lir_map.data
    answer = (meta,data)

    result = read_asdf('aigean_lir_20221205_191610.asdf')
    assert type(answer) == type(result)
    assert len(answer) == len(result)
    assert answer[0] == result[0] and answer[1].all() == result[1].all()

def test_read_hdf5():
    download_isa('aigean_man_20221205_191610.hdf5')
    man_map = get_satmap('aigean_man_20221205_191610.hdf5')
    meta = man_map.meta
    data = man_map.data
    answer = (meta,data)

    result = read_hdf5('aigean_man_20221205_191610.hdf5')
    assert type(answer) == type(result)
    assert len(answer) == len(result)
    assert answer[0] == result[0] and answer[1].all() == result[1].all()

def test_cal_fov():
    fand_map = get_satmap('aigean_fan_20221205_191610.zip')
    meta = fand_map.meta
    fov = (225, 50)
    assert fov == cal_fov(meta)

def test_cal_centre():
    fand_map = get_satmap('aigean_fan_20221205_191610.zip')
    meta = fand_map.meta
    centre = (187.5, 475.0)
    assert centre == cal_centre(meta)

# def test_net_connect():
#     with pytest.raises(ConnectionError):
#         net.query_isa()
