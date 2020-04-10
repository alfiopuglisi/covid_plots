#!/usr/bin/env python

import random
import os.path
import numpy as np
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
import matplotlib.dates as mdates



csv_province = 'COVID-19-italia/dati-province/dpc-covid19-ita-province.csv'
csv_regioni = 'COVID-19-italia/dati-regioni/dpc-covid19-ita-regioni.csv'
csv_nazione = 'COVID-19-italia/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv'
outdirs = 'output'

i18n = dict()
i18n['it'] = dict()
i18n['en'] = dict()
i18n['it']['Date'] = 'Data'
i18n['en']['Date'] = 'Date'

i18n['it']['DoublingTimeLabel'] = 'T raddoppio'
i18n['en']['DoublingTimeLabel'] = 'Doubling time'

i18n['it']['DoublingTimeUnit'] = 'gg'
i18n['en']['DoublingTimeUnit'] = 'days'

i18n['it']['NumberOfCases'] = 'Numero di casi totali'
i18n['en']['NumberOfCases'] = 'Total number of cases'

i18n['it']['NumberOfDailyCases'] = 'Numero di casi al giorno'
i18n['en']['NumberOfDailyCases'] = 'Number of cases per day'

i18n['it']['NumberOfTests'] = 'Tamponi'
i18n['en']['NumberOfTests'] = 'Number of tests'

i18n['it']['NumberOfDeaths'] = 'Numero di deceduti totali'
i18n['en']['NumberOfDeaths'] = 'Total number of deaths'

i18n['it']['NumberOfDailyDeaths'] = 'Numero di deceduti al giorno'
i18n['en']['NumberOfDailyDeaths'] = 'Number of deaths per day'

i18n['it']['PositiveCases'] = 'Positivi'
i18n['en']['PositiveCases'] = 'Positive results'

class Styles():

    totalecasi = {'marker':'o',
                  'markersize':4,
                   'color':'C0'}

    deceduti = { 'marker':'o',
                  'markersize':4,
                 'color':'red'}

    ti = { 'marker':'o',
                  'markersize':4,
           'color':'orange'}

    expfit1 = {'color':'black',
              'linewidth':1}

    expfit1a = {'color':'gray',
              'linewidth':1}

    expfit1b = {'color':'lightgray',
              'linewidth':1}

    expfit2 = {'color':'black',
              'linestyle':'--',
              'linewidth':1}

    expfit2a = {'color':'gray',
              'linestyle':'--',
              'linewidth':1}

    expfit2b = {'color':'lightgray',
              'linestyle':'--',
              'linewidth':1}

    faintline = {'color':'lightgray',
                 'linewidth':1}



def func(x, a, b, c):
    return a * np.exp(x*b) +c


class Table():

    def __init__(self, **kwargs):
        self.attributes = self.args(**kwargs)

    @staticmethod
    def attribute(k,v):
        return '%s="%s"' % (k,v)

    @staticmethod
    def args(**kwargs):
        return ' '.join([Table.attribute(k,v) for k,v in kwargs.items()])

    @staticmethod
    def row(html, **kwargs):
        return '<tr %s>\n%s\n</tr>\n' % (Table.args(**kwargs), html)

    @staticmethod
    def cell(html, **kwargs):
        return '<td %s>\n%s\n</td>\n' % (Table.args(**kwargs), html)

    def html(self, *args):
        content = ''.join(args)
        return '<table %s>%s</table>\n' % (self.attributes, content)

class DailyPlot():

    def __init__(self, lang='it', title=None, ymax=1e5):
        self.fig, ax = plt.subplots()
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        ax.yaxis.set_ticks_position('both')
        ax.tick_params(labeltop=False, labelright=True)
        plt.yscale('log')
        plt.ylim(ymin=1, ymax=ymax)
        plt.xlabel(i18n[lang]['Date'])
        plt.ylabel(i18n[lang]['NumberOfCases'])
        if title is not None:
            plt.title(title)

    def plot(self, data, casi, **kwargs):

        daily = casi[1:] - casi[0:-1]
        plt.plot(data[1:], daily, **kwargs)

    def save(self, filename):
        plt.legend()
        plt.savefig(filename)
        plt.close(self.fig)
        suffix = str(random.random())
        return '<img src="%s?%s">\n' % (os.path.basename(filename), suffix)

class TestsPlot():

    def __init__(self, lang='it', title=None):
        self.fig, ax = plt.subplots()
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        ax.yaxis.set_ticks_position('both')
        ax.tick_params(labeltop=False, labelright=True)
        plt.xlabel(i18n[lang]['Date'])
        plt.ylabel(i18n[lang]['NumberOfTests'])
        if title is not None:
            plt.title(title)
        self.lang=lang

    def plot(self, dates, y, shift=0, **kwargs):

        dd = mdates.date2num(dates)
        plt.bar(dd+shift, y, **kwargs)

    def save(self, filename):
        plt.legend()
        plt.savefig(filename)
        plt.close(self.fig)
        suffix = str(random.random())
        return '<img src="%s?%s">\n' % (os.path.basename(filename), suffix)

def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / float(N)

class OOPlot():

    def __init__(self, lang='it', title=None,
                       xlabel='NumberOfCases',
		       ylabel='NumberOfDailyCases'):
        self.fig, ax = plt.subplots()
        ax.yaxis.set_ticks_position('both')
        ax.tick_params(labeltop=False, labelright=True)
        plt.yscale('log')
        plt.xscale('log')
        plt.xlabel(i18n[lang][xlabel])
        plt.ylabel(i18n[lang][ylabel])
        if title is not None:
            plt.title(title)
        self.legend=False

    def plot(self, series, wsize=15, order=3, smooth=True, **kwargs):

        series = series[np.where(series>=10)]
        if smooth:
            if len(series) < wsize+2:
                return
            log_series = np.log(series)
            x = savgol_filter(log_series, wsize, order)
            x = np.exp(x)
        else:
            x = series
        daily = x[1:] - x[:-1]
        plt.plot(x[1:], daily, **kwargs)

#        daily = series[1:] -  series[:-1]
#        if smooth:
#            lowess = sm.nonparametric.lowess(daily, series[1:], 0.1)
#            plt.plot(lowess[:,0], lowess[:,1], **kwargs)
#        else:
#            plt.plot(series[1:], daily, **kwargs)

        if 'legend' in kwargs:
            self.legend=True

    def save(self, filename):
        if self.legend:
            plt.legend()
        plt.savefig(filename)
        plt.close(self.fig)
        suffix = str(random.random())
        return '<img src="%s?%s">\n' % (os.path.basename(filename), suffix)


class CovidPlot():

    def __init__(self, lang='it', title=None, ymax=1e6):
        self.fig, ax = plt.subplots()
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        ax.yaxis.set_ticks_position('both')
        ax.tick_params(labeltop=False, labelright=True)
        plt.yscale('log')
        plt.ylim(ymin=1, ymax=ymax)
        plt.xlabel(i18n[lang]['Date'])
        plt.ylabel(i18n[lang]['NumberOfCases'])
        if title is not None:
            plt.title(title)

    def plot(self, data, casi, **kwargs):

        plt.plot(data, casi, **kwargs)

    def expfit(self, data, casi, npoints=10, days_back=0, label='default', **kwargs):

        # Exponential fittings over the last points
        if len(data) >= npoints+days_back:
            x = (data - min(data)).dt.days.to_numpy()
            if isinstance(casi, np.ndarray):
                y = casi
            else:
                y = casi.to_numpy()
            r = range(npoints+days_back,days_back,-1)
            xx = np.array([[x[-j], 1] for j in r])
            yy = np.array([y[-j] for j in r]).astype(np.float32)
            if not np.all(yy>0):
                return
            # Set rcond=-1 to avoid a warning
            a,b = np.linalg.lstsq(xx, np.log(yy), rcond=-1)[0]
            exp_casi = np.exp(a*x+b)
            exp_data = data
            doubling_time = np.log(2)/a
            if label == 'default':
                label = 'T raddoppio = %.1f gg' % doubling_time
            if not label:
                label=None
            plt.plot(exp_data, exp_casi, label=label, **kwargs)

    def save(self, filename):
        plt.legend()
        plt.savefig(filename)
        plt.close(self.fig)
        suffix = str(random.random())
        return '<img src="%s?%s">\n' % (os.path.basename(filename), suffix)

