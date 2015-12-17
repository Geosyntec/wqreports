import sys
import os
import io
from jinja2 import Environment, FileSystemLoader, FunctionLoader
import urllib
import base64
import copy
import gc

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats

# pip install https://github.com/Geosyntec/python-pdfkit/archive/master.zip
import pdfkit
from ..utils import (html_template, css_template)
import wqio

sns.set(style='ticks', context='paper')
mpl.rcParams['text.usetex'] = False
mpl.rcParams['lines.markeredgewidth'] = .5
mpl.rcParams['font.family'] = ['sans-serif']
mpl.rcParams['mathtext.default'] = 'regular'


def make_table(loc):
    # make table
    singlevarfmtr = '{0:.3f}'
    doublevarfmtr = '{0:.3f}; {1:.3f}'
    multilinefmtr = '{0:.3f}\n({1:.3f}; {2:.3f})'

    rows = [
        ['Count', singlevarfmtr.format(loc.N)],
        ['Number of NDs', singlevarfmtr.format(loc.ND)],
        ['Min; Max ({})'.format(loc.definition['unit']),
            doublevarfmtr.format(loc.min,loc.max)],
        ['Mean ({})\n(95% confidence interval)'.format(loc.definition['unit']),
            multilinefmtr.format(
                loc.mean, *loc.mean_conf_interval)],
        ['Standard Deviation ({})'.format(loc.definition['unit']),
            singlevarfmtr.format(loc.std)],
        ['Log. Mean\n(95% confidence interval)', multilinefmtr.format(
                loc.logmean, *loc.logmean_conf_interval)],
        ['Log. Standard Deviation', singlevarfmtr.format(loc.logstd)],
        ['Geo. Mean ({})\n(95% confidence interval)'.format(loc.definition['unit']),
            multilinefmtr.format(
                loc.geomean, *loc.geomean_conf_interval)],
        ['Coeff. of Variation', singlevarfmtr.format(loc.cov)],
        ['Skewness', singlevarfmtr.format(loc.skew)],
        ['Median ({})\n(95% confidence interval)'.format(loc.definition['unit']),
            multilinefmtr.format(
                loc.median, *loc.median_conf_interval)],
        ['Quartiles ({})'.format(loc.definition['unit']),
            doublevarfmtr.format(loc.pctl25, loc.pctl75)],
    ]

    return  pd.DataFrame(rows, columns=['Statistic', 'Result'])


def make_report(loc, savename, analyte=None, geolocation=None, statplot_options={}):
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
    if loc.full_data.shape[0] >= 3:
        if analyte is None:
            analyte = loc.definition.get("analyte", "unknown")
        if geolocation is None:
            geolocation = loc.definition.get("geolocation", "unknown")

        unit = loc.definition['unit']
        thershold = loc.definition['thershold']

        if 'ylabel' not in statplot_options:
            statplot_options['ylabel'] = analyte + ' ' + '(' + unit + ')'
        if 'xlabel' not in statplot_options:
            statplot_options['xlabel'] = 'Monitoring Location' #used to be geolocation

        # make the table
        table = make_table(loc)
        table_html = table.to_html(index=False, justify='left').replace('\\n', '\n')

        # wqio figure - !can move args to main func later!
        fig = loc.statplot(**statplot_options)

        ax1, ax2 = fig.get_axes()
        ax1xlim = ax1.get_xlim()
        ax2xlim = ax2.get_xlim()

        if loc.dataframe[loc.dataframe[loc.cencol]].shape[0] > 0:
            # print(loc.dataframe.head())
            qntls, ranked = stats.probplot(loc.data, fit=False)
            xvalues = stats.norm.cdf(qntls) * 100
            figdata = loc.dataframe.sort(columns='modeled')
            figdata['xvalues'] =  xvalues
            figdata = figdata[figdata[loc.cencol]]
            ax2.plot(figdata.xvalues, figdata['modeled'], linestyle='', marker='s',
                     color='tomato', label='Extrapolated values')


        ax2.plot(ax2xlim, [thershold]*2, color=sns.color_palette()[-1], label='Threshold')

        handles, labels = ax2.get_legend_handles_labels()
        labels[0] = 'Data'
        ax2.legend(handles, labels, loc='best')
        ax2.set_xlabel('Percent less than value')

        ax1.set_xlim(ax1xlim)
        ax2.set_xlim(ax2xlim)

        ax2ylim = ax2.get_ylim()
        ax1.set_ylim(ax2ylim)

        fig.tight_layout()

        # force figure to a byte object in memory then encode
        boxplot_img = io.BytesIO()
        fig.savefig(boxplot_img, format="png", dpi=300)
        boxplot_img.seek(0)
        boxplot_uri = ('data:image/png;base64,'
            + urllib.parse.quote(base64.b64encode(boxplot_img.read())))

        figl, axl = plt.subplots(1,1, figsize=(7,10))

        wqio.utils.figutils.boxplot_legend(axl, notch=True, showmean=True, fontsize=13)

        legend_img = io.BytesIO()
        figl.savefig(legend_img, format="png", dpi=300, bbox_inches='tight')
        legend_img.seek(0)
        legend_uri = ('data:image/png;base64,'
            + urllib.parse.quote(base64.b64encode(legend_img.read())))

        # html magic
        env = Environment(loader=FileSystemLoader(r'.\utils'))
        template = env.from_string(html_template.getvalue())

        # create pdf report
        template_vars = {'analyte' : analyte,
                         'location': geolocation,
                         'analyte_table': table_html,
                         'legend': legend_uri,
                         'boxplot': boxplot_uri}

        html_out = template.render(template_vars)
        csst = copy.copy(css_template)
        try:
            print('Creating report {}'.format(savename))
            pdf = pdfkit.from_string(html_out, savename, css=csst)
        except OSError as e:
            raise OSError('The tool cannot write to the destination path. '
                          'Please check that the destination pdf is not open.\n'
                          'Trace back:\n{}'.format(e))
        plt.close(fig)
        del boxplot_img
        del figl
    else:
        print('{} does not have greater than 3 data points, skipping...'.format(savename))

    print('\n')
    gc.collect()


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
                 qualcol='qual', unitcol='unit', locationcol='location',
                 thersholdcol='threshold', ndvals=['U'], bsIter=5000,
                 useROS=True):

        self.filepath = path
        self.ndvals = ndvals
        self.final_ndval = 'ND'
        self.bsIter = bsIter
        self.useROS = True

        self.analytecol = analytecol
        self.unitcol = unitcol
        self.locationcol = locationcol
        self.thersholdcol = thersholdcol
        self.rescol = rescol
        self.qualcol = qualcol

        self._rawdata = None
        self._cleandata = None
        self._analytes = None
        self._geolocations = None
        self._thresholds = None
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
    def geolocations(self):
        """Simple list of the physical locations in the dataset.
        """
        if self._geolocations is None:
            self._geolocations = self.cleandata[self.locationcol].unique().tolist()
            self._geolocations.sort()
        return self._geolocations

    @property
    def thresholds(self):
        """Simple dictionary of thresholds per each analyte.
        """
        if self._thresholds is None:
            thresholds = (self.cleandata.loc[:,[self.analytecol, self.thersholdcol]]
                              .drop_duplicates())
            tshape = thresholds.shape[0]
            thresholds = thresholds.set_index(self.analytecol).loc[:,self.thersholdcol]
            thresholds = thresholds.to_dict()
            if tshape != len(thresholds):
                e = ('An analyte has mroe than one thershold value, please'
                    ' check the input data')
                raise ValueError(e)
            self._thresholds = thresholds
        return self._thresholds


    @property
    def locations(self):
        """ Simple list of wqio.Location objects for each analyte.
        """
        if self._locations is None:
            self._locations = {}
            gb = self.cleandata.groupby([self.locationcol, self.analytecol])
            for gl, a in gb.groups.keys():
                loc = self._make_location(gl, a)
                loc.definition.update({"analyte": a, "geolocation": gl})
                self._locations[(gl, a)] = loc

        return self._locations

    def _make_location(self, location, analyte):
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
        if location not in self.geolocations:
            raise ValueError("{} is not in the dataset".format(location))

        # get target analyte
        querystring = "{} == @location and {} == @analyte".format(self.locationcol, self.analytecol)
        data = self.cleandata.query(querystring)

        if data[self.unitcol].unique().shape[0] > 1:
            e = 'More than one unit detected for {}-{}. Please check the input file'
            raise ValueError(e)

        loc = wqio.features.Location(data, bsIter=self.bsIter, ndval=self.final_ndval,
                                     rescol=self.rescol, qualcol=self.qualcol,
                                     useROS=self.useROS, include=True)
        loc.definition = {
            'unit': data[self.unitcol].iloc[0],
            'thershold': self.thresholds[analyte]
        }

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

        for (geolocation, analyte), loc in self.locations.items():
            san_geolocation = wqio.utils.processFilename(geolocation)
            san_analyte = wqio.utils.processFilename(analyte)
            filename = os.path.join(output_path, '{}{}{}.pdf'.format(
                basename, san_geolocation, san_analyte))

            # need to make a copy so that the dict does not get changed in
            # the low functions
            spo = copy.copy(statplot_options)

            make_report(loc, filename, analyte=analyte, geolocation=geolocation,
             statplot_options=spo)
