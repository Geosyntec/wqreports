import os
import sys
from pkg_resources import resource_filename

import nose.tools as nt
import numpy as np
import numpy.testing as nptest
import pandas
import pandas.util.testing as pdtest

from wqio import Location

from wqreports import core

@nt.nottest
class mock_location(object):
    def __init__(self):
        self.N = 21
        self.ND = 3
        self.min = 0.012
        self.max = 4.75
        self.mean = 0.56
        self.mean_conf_interval = (0.37, 0.92)
        self.std = 0.33
        self.logmean = 0.45
        self.logmean_conf_interval = (0.35, 0.85)
        self.logstd = 0.22
        self.geomean = 0.63
        self.geomean_conf_interval = (0.43, 0.72)
        self.cov = 0.35
        self.skew = 0.34
        self.median = 0.51
        self.median_conf_interval = (0.45, 0.62)
        self.pctl25 = 0.17
        self.pctl75 = 2.13

        self.definition = {
            'unit': 'mg/L',
            'thershold': 0.8
        }


def test_make_table():
    dataframe = core.make_table(mock_location())
    cols = ['Result', 'Statistic']
    known_dataframe = pandas.DataFrame({
        'Result': {
            0: '21.000', 1: '3.000', 2: '0.012; 4.750', 3: '0.560\n(0.370; 0.920)',
            4: '0.330', 5: '0.450\n(0.350; 0.850)', 6: '0.220',
            7: '0.630\n(0.430; 0.720)', 8: '0.350', 9: '0.340',
            10: '0.510\n(0.450; 0.620)', 11: '0.170; 2.130'
        },
        'Statistic': {
            0: 'Count', 1: 'Number of NDs', 2: 'Min; Max (mg/L)',
            3: 'Mean (mg/L)\n(95% confidence interval)', 4: 'Standard Deviation (mg/L)',
            5: 'Log. Mean\n(95% confidence interval)', 6: 'Log. Standard Deviation',
            7: 'Geo. Mean (mg/L)\n(95% confidence interval)', 8: 'Coeff. of Variation',
            9: 'Skewness', 10: 'Median (mg/L)\n(95% confidence interval)', 11: 'Quartiles (mg/L)'
        }
    })
    pdtest.assert_frame_equal(dataframe[cols], known_dataframe[cols])



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

    def test_analytes(self):
        nt.assert_true(hasattr(self.report, 'analytes'))
        nt.assert_list_equal(self.report.analytes, self.known_analytes)

    def test_locations(self):
        nt.assert_true(hasattr(self.report, 'locations'))
        nt.assert_true(isinstance(self.report.locations, dict))
        for key, loc in self.report.locations.items():
            nt.assert_true(isinstance(loc, Location))

    def test__make_location(self):
        loc = self.report._make_location("location1", "analyte_a")
        pdtest.assert_frame_equal(
            loc._raw_data,
            self.known_cleandata.query(
                "analyte == 'analyte_a' and location == 'location1'"))

    @nt.raises(ValueError)
    def test__make_location_bad_analyte(self):
        # todo: rename
        loc = self.report._make_location("JUNK", "JUNK")

    @nptest.dec.skipif(True)
    def test_export_pdfs_smoke_test(self):
        self.report.export_pdfs('.', 'test')


class test_PdfReport_defaults(Base_PdfReport_Mixin):
    def setup(self):
        from numpy import nan
        self.path = resource_filename("wqreports.testing", "testdata.txt")
        self.known_ndvals = ['U']
        self.known_final_ndval = 'ND'
        self.known_analytecol = 'analyte'
        self.known_qualcol = 'qual'
        self.known_rescol = 'res'
        self.report = core.PdfReport(self.path)

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
                     18: 0.2776045, 19: 0.3523322},
            'location': {0: 'location1', 1: 'location1', 2: 'location1',
                         3: 'location1', 4: 'location1', 5: 'location1',
                         6: 'location1', 7: 'location1', 8: 'location1',
                         9: 'location1', 10: 'location1', 11: 'location1',
                         12: 'location1', 13: 'location1', 14: 'location1',
                         15: 'location1', 16: 'location1', 17: 'location1',
                         18: 'location1', 19: 'location1'},
            'unit': {0: 'mg/L', 1: 'mg/L', 2: 'mg/L',
                     3: 'mg/L', 4: 'mg/L', 5: 'mg/L',
                     6: 'mg/L', 7: 'mg/L', 8: 'mg/L',
                     9: 'mg/L', 10: 'mg/L', 11: 'mg/L',
                     12: 'mg/L', 13: 'mg/L', 14: 'mg/L',
                     15: 'mg/L', 16: 'mg/L', 17: 'mg/L',
                     18: 'mg/L', 19: 'mg/L'},
            'threshold': {0: '0.8', 1: '0.8', 2: '0.8',
                          3: '0.8', 4: '0.8', 5: '0.8',
                          6: '0.8', 7: '0.8', 8: '0.8',
                          9: '0.8', 10: '0.8', 11: '0.8',
                          12: '0.8', 13: '0.8', 14: '0.8',
                          15: '0.8', 16: '0.8', 17: '0.8',
                          18: '0.8', 19: '0.8'},

        })[['location', 'analyte', 'res', 'qual', 'unit','threshold']]

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
                     18: 0.2776045, 19: 0.3523322},
            'location': {0: 'location1', 1: 'location1', 2: 'location1',
                         3: 'location1', 4: 'location1', 5: 'location1',
                         6: 'location1', 7: 'location1', 8: 'location1',
                         9: 'location1', 10: 'location1', 11: 'location1',
                         12: 'location1', 13: 'location1', 14: 'location1',
                         15: 'location1', 16: 'location1', 17: 'location1',
                         18: 'location1', 19: 'location1'},
            'unit': {0: 'mg/L', 1: 'mg/L', 2: 'mg/L',
                     3: 'mg/L', 4: 'mg/L', 5: 'mg/L',
                     6: 'mg/L', 7: 'mg/L', 8: 'mg/L',
                     9: 'mg/L', 10: 'mg/L', 11: 'mg/L',
                     12: 'mg/L', 13: 'mg/L', 14: 'mg/L',
                     15: 'mg/L', 16: 'mg/L', 17: 'mg/L',
                     18: 'mg/L', 19: 'mg/L'},
            'threshold': {0: '0.8', 1: '0.8', 2: '0.8',
                          3: '0.8', 4: '0.8', 5: '0.8',
                          6: '0.8', 7: '0.8', 8: '0.8',
                          9: '0.8', 10: '0.8', 11: '0.8',
                          12: '0.8', 13: '0.8', 14: '0.8',
                          15: '0.8', 16: '0.8', 17: '0.8',
                          18: '0.8', 19: '0.8'},
        })[['location', 'analyte', 'res', 'qual', 'unit','threshold']]

        self.known_analytes = ['analyte_a', 'analyte_b']
        self.known_locations = ['location1']
