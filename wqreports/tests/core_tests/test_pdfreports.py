import os
from pkg_resources import resource_filename

import nose.tools as nt
import numpy as np
import numpy.testing as nptest
import pandas
import pandas.util.testing as pdtest

import wqreports


class Base_PdfReport_Mixin(object):
    def test_filepath(self):
        nt.assert_true(hasattr(self.report, 'filepath'))
        nt.assert_equal(self.report.filepath, self.path)

    def test_ndvals(self):
        nt.assert_true(hasattr(self.report, "ndvals"))
        nt.assert_list_equal(self.report.ndvals, self.known_ndvals)

    def test_finalndval(self):
        nt.assert_true(hasattr(self.report, "final_ndval"))
        nt.assert_equal(self.report.final_ndval, self.known_final_ndval)

    def test_analytecol(self):
        nt.assert_true(hasattr(self.report, "analytecol"))
        nt.assert_equal(self.report.analytecol, self.known_analytecol)

    def test_qualcol(self):
        nt.assert_true(hasattr(self.report, "qualcol"))
        nt.assert_equal(self.report.qualcol, self.known_qualcol)

    def test_rescol(self):
        nt.assert_true(hasattr(self.report, "rescol"))
        nt.assert_equal(self.report.rescol, self.known_rescol)

    def test_rawdata(self):
        nt.assert_true(hasattr(self.report, 'rawdata'))
        nt.assert_true(isinstance(self.report.rawdata, pandas.DataFrame))
        pdtest.assert_frame_equal(self.report.rawdata, self.known_rawdata)

    def test_cleandata(self):
        nt.assert_true(hasattr(self.report, 'cleandata'))
        nt.assert_true(isinstance(self.report.cleandata, pandas.DataFrame))
        pdtest.assert_frame_equal(self.report.cleandata, self.known_cleandata)


class test_PdfReport_defaults(Base_PdfReport_Mixin):
    def setup(self):
        from numpy import nan
        self.path = resource_filename("wqreports.testing", "testdata.txt")
        self.known_ndvals = ['U']
        self.known_final_ndval = 'ND'
        self.known_analytecol = 'analyte'
        self.known_qualcol = 'qual'
        self.known_rescol = 'res'
        self.report = wqreports.PdfReport(self.path)

        self.known_rawdata = pandas.DataFrame({
            'analyte': {0: 'analyte_b', 1: 'analyte_a', 2: 'analyte_a',
                        3: 'analyte_b', 4: 'analyte_a', 5: 'analyte_a',
                        6: 'analyte_a', 7: 'analyte_b', 8: 'analyte_a',
                        9: 'analyte_a', 10: 'analyte_b', 11: 'analyte_a',
                       12: 'analyte_b', 13: 'analyte_a', 14: 'analyte_b',
                       15: 'analyte_b', 16: 'analyte_b', 17: 'analyte_a',
                       18: 'analyte_a', 19: 'analyte_b'},
            'qual': {0: nan, 1: 'U', 2: nan, 3: nan, 4: 'U', 5: 'U',
                     6: nan, 7: 'U', 8: 'U', 9: nan, 10: nan, 11: nan,
                    12: nan, 13: nan, 14: nan, 15: 'U', 16: 'U', 17: nan,
                    18: 'U', 19: 'U'},
            'res': { 0: 0.38320585, 1: 0.75877428, 2: 0.75050629,
                     3: 0.29815660, 4: 0.73783721, 5: 0.09132073,
                     6: 0.53183929, 7: 0.21272010, 8: 0.82763004,
                     9: 0.70941756, 10: 0.7486036, 11: 0.5187555,
                     12: 0.0476615, 13: 0.6662081, 14: 0.0276759,
                     15: 0.1535038, 16: 0.6039080, 17: 0.7387704,
                     18: 0.2776045, 19: 0.3523322}
        })[['analyte', 'res', 'qual']]

        self.known_cleandata = pandas.DataFrame({
            'analyte': {0: 'analyte_b', 1: 'analyte_a', 2: 'analyte_a',
                        3: 'analyte_b', 4: 'analyte_a', 5: 'analyte_a',
                        6: 'analyte_a', 7: 'analyte_b', 8: 'analyte_a',
                        9: 'analyte_a', 10: 'analyte_b', 11: 'analyte_a',
                       12: 'analyte_b', 13: 'analyte_a', 14: 'analyte_b',
                       15: 'analyte_b', 16: 'analyte_b', 17: 'analyte_a',
                       18: 'analyte_a', 19: 'analyte_b'},
            'qual': {0: nan, 1: 'ND', 2: nan, 3: nan, 4: 'ND', 5: 'ND',
                     6: nan, 7: 'ND', 8: 'ND', 9: nan, 10: nan, 11: nan,
                    12: nan, 13: nan, 14: nan, 15: 'ND', 16: 'ND', 17: nan,
                    18: 'ND', 19: 'ND'},
            'res': { 0: 0.38320585, 1: 0.75877428, 2: 0.75050629,
                     3: 0.29815660, 4: 0.73783721, 5: 0.09132073,
                     6: 0.53183929, 7: 0.21272010, 8: 0.82763004,
                     9: 0.70941756, 10: 0.7486036, 11: 0.5187555,
                     12: 0.0476615, 13: 0.6662081, 14: 0.0276759,
                     15: 0.1535038, 16: 0.6039080, 17: 0.7387704,
                     18: 0.2776045, 19: 0.3523322}
        })[['analyte', 'res', 'qual']]
