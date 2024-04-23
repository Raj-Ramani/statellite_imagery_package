from unittest import mock
import unittest
from aigeanpy.satmap import get_satmap, pixel_to_earth, isoverlap, earth_to_pixel, cal_fov, cal_centre, satmap
from aigeanpy.net import download_isa
import os

class mocktest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('test initialization\n')

    @classmethod
    def tearDownClass(cls):
        print('\n test end ')

    # test satmap __add__
    
    download_isa('aigean_fan_20221205_191610.zip')
    download_isa('aigean_fan_20221205_192210.zip')
    download_isa('aigean_man_20221205_191610.hdf5')
    def test_add(self):

        # create function
        
        lir_map1 = get_satmap('aigean_fan_20221205_191610.zip')
        fun = satmap(lir_map1.meta,lir_map1.data, lir_map1.shape, lir_map1.fov, lir_map1.centre )

        lir_map2 = get_satmap('aigean_fan_20221205_192210.zip')
        addmap = lir_map1 + lir_map2

        # use mock test
        
        fun.__add__ = mock.Mock(side_effect=lir_map1.__add__)
        result = fun.__add__(lir_map2)

        self.assertEqual(result.centre,(300, 275))
        self.assertEqual(result.shape, (90, 90))
        self.assertEqual(fun.__add__.called, True)
        self.assertEqual(fun.__add__.call_count, 1)
        
    def test_sub(self):
        lir_map1 = get_satmap('aigean_fan_20221208_170852.zip')
        fun = satmap(lir_map1.meta,lir_map1.data,lir_map1.shape,lir_map1.fov,lir_map1.centre)

        lir_map2 = get_satmap('aigean_fan_20221210_150420.zip')
        submap = lir_map1 - lir_map2

        fun.__sub__ = mock.Mock(side_effect=lir_map1.__sub__)
        result = fun.__sub__(lir_map2)

        self.assertEqual(result.centre,(1237.5, 475.0))
        self.assertEqual(result.shape, (10, 15))
        self.assertEqual(fun.__sub__.called, True)
        self.assertEqual(fun.__sub__.call_count, 1)

    def test_mosaic(self):
        lir_map1 = get_satmap('aigean_lir_20221205_191610.asdf')
        fun = satmap(lir_map1.meta,lir_map1.data,lir_map1.shape,lir_map1.fov,lir_map1.centre)

        lir_map2 = get_satmap('aigean_man_20221205_194510.hdf5')
        satmap_mosaic = satmap.mosaic(lir_map1,lir_map2)

        fun.mosaic = mock.Mock(side_effect=lir_map1.mosaic)
        result = fun.mosaic(lir_map2)

        self.assertEqual(result.centre,(850.0, 350.0))
        self.assertEqual(result.shape, (20, 47))
        self.assertEqual(fun.mosaic.called, True)
        self.assertEqual(fun.mosaic.call_count, 1)

    #def test_visualise(self):
        #lir_map1 = satmap.get_satmap('aigean_fan_20221205_191610.zip')
        #fun = satmap.satmap(lir_map1.meta,lir_map1.data,lir_map1.shape,lir_map1.fov,lir_map1.centre)

       # figure = satmap.satmap.visualise(lir_map1,True)

       # fun.visualise = mock.Mock(side_effect=lir_map1.visualise)
       #  result = fun.visualise(True)

        #self.assertIn(result,os.listdir("."))



    def test_get_satmap(self):
        meta_value = {'instrument': 'Fand', 'observatory': 'Aigean', 'resolution': 5, 'time': '19:22:10', 'date': '2022-12-05', 'xcoords': (300, 525), 'ycoords': (50, 100), 'archive': 'ISA'}
        meta_get = mock.Mock(return_value=meta_value)

        content = meta_get()
        
        lir_map = get_satmap('aigean_fan_20221205_192210.zip')
        meta = lir_map.meta

        self.assertEqual(meta,content,msg='Inconsistent meta data')

        self.assertEqual(meta_get.called, True)
        self.assertEqual(meta_get.call_count, 1)
    
    def test_pixel_to_earth(self):
        earth_coord = (765, 385)
        get_earth_coord = mock.Mock(return_value=earth_coord)

        content = get_earth_coord()

        lir_map = get_satmap('aigean_man_20221205_194510.hdf5')
        result = pixel_to_earth(lir_map.meta, 2, 2)

        self.assertEqual(result,content,msg='Inconsistent earth coordinate')
        self.assertEqual(get_earth_coord.called, True)
        self.assertEqual(get_earth_coord.call_count, 1)

    def test_earth_to_pixel(self):
        pixel_coord = (6,5)
        get_pixel_coord = mock.Mock(return_value=pixel_coord)

        content = get_pixel_coord()

        lir_map = get_satmap('aigean_fan_20221205_191610.zip')
        result = earth_to_pixel(lir_map.meta,100,470)

        self.assertEqual(result,content,msg='Inconsistent pixel coordinate')
        self.assertEqual(get_pixel_coord.called, True)
        self.assertEqual(get_pixel_coord.call_count, 1)

    def test_isoverlap(self):
        result1 = True
        get_result1=mock.Mock(return_value=result1)

        content = get_result1()

        lir_map1 = get_satmap('aigean_lir_20221205_191610.asdf')
        lir_map2 = get_satmap('aigean_lir_20221206_181924.asdf')
        meta1 = lir_map1.meta
        meta2 = lir_map2.meta
        result2 = isoverlap(meta1,meta2)

        self.assertEqual(result2,content,msg='Fail to judge whether maps are overlap or not')
        self.assertEqual(get_result1.called, True)
        self.assertEqual(get_result1.call_count, 1)

    def test_read_hdf5(self):
        
        meta_value = {'instrument': 'Manannan',
                    'observatory': 'Aigean',
                    'resolution': 15,
                    'time': '19:16:10',
                    'date': '2022-12-05',
                    'xcoords': (150, 600),
                    'ycoords': (250, 400),
                    'archive': ''}
        meta_get = mock.Mock(return_value=meta_value)

        content = meta_get()

        man_map = get_satmap('aigean_man_20221205_191610.hdf5')
        meta = man_map.meta

        self.assertEqual(meta,content,msg='Inconsistent meta data')
        self.assertEqual(meta_get.called, True)
        self.assertEqual(meta_get.call_count, 1)

    def test_asdf(self):
        meta_value = {'instrument': 'Lir',
                    'observatory': 'Aigean',
                    'resolution': 30,
                    'time': '19:16:10',
                    'date': '2022-12-05',
                    'xcoords': (500, 1100),
                    'ycoords': (200, 500),
                    'archive': 'ISA'}
        meta_get = mock.Mock(return_value=meta_value)

        content = meta_get()

        lir_map = get_satmap('aigean_lir_20221205_191610.asdf')
        meta = lir_map.meta

        self.assertEqual(meta,content,msg='Inconsistent meta data')
        self.assertEqual(meta_get.called, True)
        self.assertEqual(meta_get.call_count, 1)

    def test_zip(self):
        meta_value = {'instrument': 'Fand',
                    'observatory': 'Aigean',
                    'resolution': 5,
                    'time': '19:16:10',
                    'date': '2022-12-05',
                    'xcoords': (75, 300),
                    'ycoords': (450, 500),
                    'archive': 'ISA'}
        meta_get = mock.Mock(return_value=meta_value)

        content = meta_get()

        fand_map = get_satmap('aigean_fan_20221205_191610.zip')
        meta = fand_map.meta

        self.assertEqual(meta,content,msg='Inconsistent meta data')
        self.assertEqual(meta_get.called, True)
        self.assertEqual(meta_get.call_count, 1)

    def test_cal_fov(self):
        fov = (225, 50)
        get_fov = mock.Mock(return_value=fov)

        content = get_fov()

        fand_map = get_satmap('aigean_fan_20221205_191610.zip')
        meta = fand_map.meta
        result = cal_fov(meta)
        
        self.assertEqual(result,content,msg='Inconsistent field of view')
        self.assertEqual(get_fov.called, True)
        self.assertEqual(get_fov.call_count, 1)

    def test_cal_centre(self):
        centre = (187.5, 475.0)
        get_centre = mock.Mock(return_value=centre)

        content = get_centre()

        fand_map = get_satmap('aigean_fan_20221205_191610.zip')
        meta = fand_map.meta
        result = cal_centre(meta)

        self.assertEqual(result,content,msg='Inconsistent centre')
        self.assertEqual(get_centre.called, True)
        self.assertEqual(get_centre.call_count, 1)


if __name__ == '__main__':
    unittest.main()