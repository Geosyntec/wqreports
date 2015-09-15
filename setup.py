# Setup script for the wqreports package
#
# Usage: python setup.py install
#
import os
from setuptools import setup, find_packages

DESCRIPTION = "wqreports: Create reports from data analyzed with wqio"
LONG_DESCRIPTION = DESCRIPTION
NAME = "wqreports"
VERSION = "0.1"
AUTHOR = "Lucas Nguyen (Geosyntec Consultants)"
AUTHOR_EMAIL = "lnguyen@geosyntec.com"
URL = "https://github.com/Geosyntec/wqreports"
DOWNLOAD_URL = URL
LICENSE = "BSD 3-clause"
PACKAGES = find_packages(exclude=[])
PLATFORMS = "Python 3.3 and later."
CLASSIFIERS = [
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Intended Audience :: Science/Research",
    "Topic :: Formats and Protocols :: Data Formats",
    "Topic :: Scientific/Engineering :: Earth Sciences",
    "Topic :: Software Development :: Libraries :: Python Modules",
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
]
INSTALL_REQUIRES = ['jinja2', 'seaborn', 'wqio']
PACKAGE_DATA = {
    'wqreports.testing': ['*.txt'],
}
DATA_FILES = None

if __name__ == "__main__":
    setup(
        name=NAME,
        version=VERSION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        download_url=DOWNLOAD_URL,
        license=LICENSE,
        packages=PACKAGES,
        package_data=PACKAGE_DATA,
        data_files=DATA_FILES,
        platforms=PLATFORMS,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        zip_safe=False
    )
