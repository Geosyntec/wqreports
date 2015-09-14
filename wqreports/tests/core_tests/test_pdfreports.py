import os

from nose.tools import *
import numpy as np
import numpy.testing as nptest

class _base_PyNSQD_test(object):
    @nottest
    def main_setup(self):

        # basic test data
        self.known_filepath = path
        self.known_ndvals = ndvals

        self.known_rawanalytecol = analytecol
        self.known_rawrescol = rescol
        self.known_rawqualcol = qualcol

        self.known_analytecol = 'analyte'
        self.known_rescol = 'res'
        self.known_qualcol = 'qual'

        self.known_rawdata = None
        self.known_cleandata = None

        # Location stuff
        self.known_station_type = 'inflow'

        self.known_color = np.array((0.32157, 0.45271, 0.66667))
        self.known_rescol = 'res'
        self.known_qualcol = 'qual'
        self.known_all_positive = True
        self.known_include = True
        self.known_exclude = False
        self.known_hasData = True
        self.known_min_detect = 2.00
        self.known_min_DL = 5.00
        self.known_filtered_include = False
