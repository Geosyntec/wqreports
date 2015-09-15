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

# pip install https://github.com/Geosyntec/python-pdfkit/archive/master.zip
import pdfkit
from ..utils import (html_template, css_template)
import wqio

sns.set(style='ticks', context='paper')


def make_table(loc):
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

    return  pd.DataFrame(rows, columns=['Statistic', 'Result'])


def make_report(loc, savename, analyte=None, statplot_options={}):
    """ Produces a statistical report for the specified analyte.

    Parameters
    ----------
    loc : wqio.Location
        The Location object to be summarized.
    savename : str
        Filename/path of the output pdf
    analyte : str, optional
        Optional name for the analyte in the ``loc``'s data.
    statplot_options : dict, optional
        Dictionary of keyward arguments to be passed to
        wqio.Location.statplot

    Returns
    -------
    None

    See also
    --------
    wqio.Location
    wqio.Location.statplot

    """

    if analyte is None:
        analyte = loc.definition.get("analyte", "unknown")

    # make the table
    table = make_table(loc)
    table_html = table.to_html(index=False, justify='left').replace('\\n', '\n')

    # wqio figure - !can move args to main func later!
    fig = loc.statplot(**statplot_options)
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
                     'analyte_table': table_html,
                     'image': uri}

    html_out = template.render(template_vars)
    pdf = pdfkit.from_string(html_out, savename, css=css_template)


class PdfReport(object):
    """ Class to generate generic 1-page reports from wqio objects.

    Parameters
    ----------
    path : str
        Filepath to the CSV file containing input data.
    analytecol : str (default = 'analyte')
        Column in the input file that contains the analyte name.
    rescol : str (default='res')
        Column in the input file that contains the result values.
    qualcol : str (default='qual')
        Column in the input file that contains the data qualifiers
        labeling data as right-censored (non-detect) or not.
    ndvals : list of strings
        List of values found in ``qualcol`` that flag data as being
        right-censored (non-detect). Any value in ``qualcol`` that is
        *not* in this list will be assumed to denote an uncensored
        (detected value).
    bsIter : int (default = 10000)
        Number of iterations used to refined statistics via a bias-
        corrected and accelerated (BCA) bootstrapping method.
    useROS : bool (default is True)
        Toggles the use of regression-on-order statistics to estimate
        censored (non-detect) values when computing summary statistics.

    Examples
    --------
    >>> import wqreports
    >>> report = wqreports.PdfReport("~/data/arsenic.csv", ndvals=['U', 'UJ', '<'])
    >>> report.make_report(...)

    """

    def __init__(self, path, analytecol='analyte', rescol='res',
                 qualcol='qual', ndvals=['U'], bsIter=5000,
                 useROS=True):
        self.filepath = path
        self.ndvals = ndvals
        self.final_ndval = 'ND'
        self.bsIter = bsIter
        self.useROS = True

        self.analytecol = analytecol
        self.rescol = rescol
        self.qualcol = qualcol

        self._rawdata = None
        self._cleandata = None
        self._analytes = None
        self._locations = None

    @property
    def rawdata(self):
        """ Raw data as parsed by pandas.read_csv(self.filepath)
        """
        if self._rawdata is None:
            self._rawdata = pd.read_csv(self.filepath)
        return self._rawdata

    @property
    def cleandata(self):
        """ Cleaned data with simpler qualifiers.
        """
        if self._cleandata is None:
            self._cleandata = (
                self.rawdata
                    .replace({self.qualcol:{_: self.final_ndval for _ in self.ndvals}})
            )
        return self._cleandata

    @property
    def analytes(self):
        """ Simple list of the analytes to be analyzed.
        """
        if self._analytes is None:
            self._analytes = self.cleandata[self.analytecol].unique().tolist()
            self._analytes.sort()
        return self._analytes

    @property
    def locations(self):
        """ Simple list of wqio.Location objects for each analyte.
        """
        if self._locations is None:
            self._locations = {}
            for a in self.analytes:
                loc = self._make_location(a)
                loc.definition = {"analyte": a}
                self._locations[a] = loc

        return self._locations

    def _make_location(self, analyte):
        """ Make a wqio.Location from an analyte.

        Parameters
        ----------
        analyte : string
            The pollutant to be included in the Location.

        Returns
        -------
        loc : wqio.Location
            A wqio.Location object for the provided analyte.

        """
        if analyte not in self.analytes:
            raise ValueError("{} is not in the dataset".format(analyte))

        # get target analyte
        querystring = "{} == @analyte".format(self.analytecol)
        data = self.cleandata.query(querystring)

        loc = wqio.features.Location(data, bsIter=self.bsIter, ndval=self.final_ndval,
                                     rescol=self.rescol, qualcol=self.qualcol,
                                     useROS=self.useROS, include=True)

        return loc

    def export_pdfs(self, output_path, basename=None, **statplot_options):
        """ Export 1-pg summary PDF for each analyte in the data.

        Parameters
        ----------
        output_path : string
            Folder path in which all PDFs will be saved
        basename : string, optional
            Prefix for the filename of each PDF. If omitted, the
            filename will simply the be analyte.
        statplot_options : optional keyword arguments
            Options passed directly to wqio.Location.statplot

        """

        if basename is None:
            basename = ""

        for analyte, loc in self.locations.items():
            filename = os.path.join(output_path, '{}{}.pdf'.format(basename, analyte))
            make_report(loc, filename, analyte=analyte, statplot_options=statplot_options)
