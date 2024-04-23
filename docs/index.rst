.. aigeanpy-Working-Group-11 documentation master file, created by
   sphinx-quickstart on Wed Jan 18 10:36:08 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to aigeanpy-Working-Group-11's documentation!
=====================================================

Introduction
-----------------
This repository is designed for the creation of a library to analyse data from different instruments on-board a satellite. 
The instruments provide daily updates from a piece of land that can be used to track water levels at different locations. 
Aigean satellite data is used.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Installation
-----------------

   1.Install by local package: download the package and get into the directory. Use the command

   .. code-block:: shell

      pip install .

   2.Install from github: use the command

   .. code-block:: shell
      
      pip install git+git://github.com/UCL-COMP0233-22-23/aigeanpy-Working-Group-11.git 


Usage 
-----------------
The following introduces the use of some functions.

Command line interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We provide some command lines to use:

1. ``aigean_today``: getting the latest image and meta data of the archive.

2. ``aigean_metadata``: Get the meta data of the specified file.

3. ``aigean_mosaic``: Create a mosaic image by given at least 2 images.



Library style interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We provide the function of querying and downloading data:

1. ``query_isa()``: Query data information according to time range and instrument.

2. ``download_isa()``: Download specified file.

You need to use the code

.. code-block:: shell

   from aigeanpy.net import download_isa, query_isa

to import the library tools.



An object to manipulate the data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The satmap is used to read data from different devices and generate a satmap class, 
use the generated stamap class to process data including +, - and mosaic images.

The steps are as follows:

1. Read data to generate satmap class:
use function ``get_satmap()`` to  read difference file

.. code-block:: python
   from aigeanpy.satmap import get_satmap

   satmap_class_zip = get_satmap('data.zip')
   satmap_class_hdf5 = get_satmap('data.hdf5')


2. Visualization:
The ``visualize()`` function allows us to visualize data


3. Add:

We can call the addition operation declared in the class to add two images.
The specific operation is as follows

.. code-block:: python

   download_isa("data1.zip")
   download_isa("data2.zip")

Create stamap class:
.. code-block:: python
   from aigeanpy.satmap import get_satmap

   satmap1 = get_satmap('data1.zip') 
   satmap2 = get_satmap('data2.zip') 

Then use ``+`` to add and use ``visualise()`` to visualise:

.. code-block:: python

   satmap_add = satmap1 + satmap2
   satmap_add.visualise()



4. Subtraction:
We can call the addition operation declared in the class to sub two images.
The specific operation is as follows:

Download file first
.. code-block:: python

   download_isa("data1.hdf5")
   download_isa("data2.hdf5")

Get satmap class

.. code-block:: python

   satmap1 = get_satmap('data1.hdf5') 
   satmap2 = get_satmap('data2.hdf5') 


Then use ``-`` to subtract and use ``visualise()`` to visualise:

.. code-block:: python
   from aigeanpy.satmap import get_satmap

   satmap_sub = satmap1 + satmap2
   satmap_sub.visualise()


5. Mosaic:
Use ``mosaic()`` to combine multiple images with different resolutions. 

Download first:

.. code-block:: python

   download_isa('data1.asdf')
   download_isa('data2.hdf5')

Create stamap class:

.. code-block:: python

   from aigeanpy.satmap import get_satmap
   satmap1 = get_satmap('data1.asdf')
   satmap2 = get_satmap('data2.hdf5')

Then use ``mosaic()`` to combine these two data and use ``visualise()`` to visualise:

.. code-block:: python

   satmap1.mosaic(satmap2)
   satmap1.visualise()

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules



