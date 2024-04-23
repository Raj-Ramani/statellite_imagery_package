from setuptools import setup, find_packages

with open("README.md", "r") as rd:
    README_description = rd.read()

setup(
    name = 'aigeanpy',
    version = '0.0.1',
    packages=find_packages(exclude=["test_*","*.test.","test"]),
    url='https://github.com/UCL-COMP0233-22-23/aigeanpy-Working-Group-11.git',
    license='UCL',
    author='Fuyi Huang, Raj, Zhenghao Lu, Viola Yang, Yixiao Chen',
    description='A package for analysing data from different instruments on-board a satellite (Aigean satellite)',
    README_description = README_description,
    README_content_type="text/markdown",
    install_requires=['setuptools',
                      'requests',
                      'argparse',
                      'pathlib',
                      'datetime',
                      'numpy',
                      'h5py',
                      'scikit-image',
                      'asdf',
                      'matplotlib',
                      'responses',
                      'typing',
                      'pytest',
                    ],
    
    classifiers=[
        "Programming Language :: Python ::3",
        "License :: OSI Approved :: UCL License",  
        "Operating System :: OS Independent",   
    ],
    python_requires='>=3.9',
    
    entry_points={ 
        'console_scripts': [
            'aigean_today = aigeanpy.command:aigean_today_process',
            'aigean_metadata = aigeanpy.command:aigean_metadata_process',
            'aigean_mosaic = aigeanpy.command:aigean_mosaic_process'
        ]
    }
)