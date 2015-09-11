import sys
import os
import io
from jinja2 import Environment, FileSystemLoader, FunctionLoader
import urllib
import base64

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

from . import pdfkit
from ..utils import (html_template, css_template)
import wqio


sns.set(style='ticks', context='paper')

class PdfReport(object):
    """
    A wrapper class for wqio and pybmp for use the NSQD data.
    """
    def __init__(self, path, analytecol='analyte', rescol='res',
                 qualcol='qual', ndvals=['U']):
        """
        Requires:
            path: str, filepath to the inpuit data
            analytecol: str (default='analyte'), column in the input file that
                contains the constituent name.
            rescol: str (default='res'), column in the input file that
                contains the result values.
            qualcol: str (default='qual'), column in the input file that
                contains the data qualifiers.
        """
        self.filepath = path
        self.ndvals = ndvals

        self._rawanalytecol = analytecol
        self._rawrescol = rescol
        self._rawqualcol = qualcol

        self.analytecol = 'analyte'
        self.rescol = 'res'
        self.qualcol = 'qual'

        self._rawdata = None
        self._cleandata = None

    @property
    def rawdata(self):
        """
        Raw data as parsed by pandas.read_csv(self.filepath)
        """
        if self._rawdata is None:
            self._rawdata = pd.read_csv(self.filepath)
        return self._rawdata

    @property
    def cleandata(self):
        """
        Cleaned data with the original columns renamed to
        'analyte', 'result', 'qual'.
        """
        if self._cleandata is None:
            self._cleandata = (self.rawdata
                .rename(columns={
                    self._rawanalytecol: self.analytecol,
                    self._rawrescol: self.rescol,
                    self._rawqualcol: self.qualcol,
                })
                .set_index(self.analytecol, append=True)
                .replace({self.qualcol:{_:'ND' for _ in self.ndvals}})
            )
        return self._cleandata

    def make_report(self, analyte, savename, bsIter=10000, station_type='inflow',
                    useROS=True, include=True, pos=1, yscale='log', notch=True,
                    showmean=True, width=0.8, bacteria=False,
                    axtype='prob', patch_artist=False):
        """
        Produces a statistical report for the specified analyte.

        Requires:
            analyte: str, th specified analyte
            savename, str, name of the output pdf
        Optional:
            bsIter=10000,
            station_type='inflow',
            useROS=True,
            include=True
        """
        # get target analyte
        data = self.cleandata.xs(analyte, level=self.analytecol)

        loc = wqio.features.Location(data, bsIter=bsIter,
            station_type=station_type, useROS=useROS, include=include)

        # make table
        singlevarfmtr = '{0:.3f}'
        doublevarfmtr = '{0:.3f}; {1:.3f}'
        multilinefmtr = '{0:.3f}\n({1:.3f}; {2:.3f})'

        rows = [
            ['Count', singlevarfmtr.format(loc.N)],
            ['Number of NDs', singlevarfmtr.format(loc.ND)],
            ['Min; Max', doublevarfmtr.format(loc.min,loc.max)],
            ['Mean\n(95% confidence interval)', multilinefmtr.format(
                    loc.mean, *loc.mean_conf_interval)],
            ['Standard Deviation', singlevarfmtr.format(loc.std)],
            ['Log. Mean\n(95% confidence interval)', multilinefmtr.format(
                    loc.logmean, *loc.logmean_conf_interval)],
            ['Log. Standard Deviation', singlevarfmtr.format(loc.logstd)],
            ['Geo. Mean\n(95% confidence interval)', multilinefmtr.format(
                    loc.geomean, *loc.geomean_conf_interval)],
            ['Coeff. of Variation', singlevarfmtr.format(loc.cov)],
            ['Skewness', singlevarfmtr.format(loc.skew)],
            ['Median\n(95% confidence interval)', multilinefmtr.format(
                    loc.median, *loc.median_conf_interval)],
            ['Quartiles', doublevarfmtr.format(loc.pctl25, loc.pctl75)],
        ]

        df = pd.DataFrame(rows, columns=['Statistic', 'Result'])

        # wqio figure - !can move args to main func later!
        fig = loc.statplot(pos=pos, yscale=yscale, notch=notch, showmean=showmean,
            width=width, bacteria=bacteria, ylabel=analyte, axtype=axtype,
            patch_artist=patch_artist)
        fig.tight_layout()

        # force figure to a byte object in memory then encode
        img = io.BytesIO()
        fig.savefig(img, format="png", dpi=300)
        img.seek(0)
        uri = ('data:image/png;base64,'
            + urllib.parse.quote(base64.b64encode(img.read())))

        # html magic
        env = Environment(loader=FileSystemLoader(r'.\utils'))
        template = env.from_string(html_template.getvalue())

        # create pdf report
        template_vars = {'title' : analyte,
                         'body': analyte,
                         'analyte_table': df.to_html(
                            index=False, justify='left').replace('\\n', '\n'),
                         'image': uri}

        html_out = template.render(template_vars)
        pdf = pdfkit.from_string(html_out, savename, css=css_template)
