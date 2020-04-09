#!/usr/bin/env python

import sys
import os.path
import pandas as pd
from multiprocessing import Pool

from covid import i18n, Styles, CovidPlot, DailyPlot, OOPlot

try:
    from my_config_row import csv_dir, outdir, n_proc

except ModuleNotFoundError:
    csv_dir = '../COVID-19-world/csse_covid_19_data/csse_covid_19_time_series'
    homedir = os.getenv('HOME')
    outdir = os.path.join(homedir, 'public_html/coronavirus/world')
    n_proc = 1

csv_confirmed = os.path.join(csv_dir, 'time_series_covid19_confirmed_global.csv')
csv_deaths    = os.path.join(csv_dir, 'time_series_covid19_deaths_global.csv')

last_update = sys.argv[1]

def nations_list():

    a = pd.read_csv(csv_confirmed)
    b = a.groupby('Country/Region').sum().reset_index()
    return b.to_numpy()[:,0]

def extract(csv_filename, nation):

    a = pd.read_csv(csv_filename)
    b = a.groupby('Country/Region').sum().reset_index()
    data = b.loc[ b['Country/Region'] == nation].to_numpy()
    return (pd.to_datetime(a.columns[4:].to_series()), data[:,3:].astype('int64').flatten())

try:
    os.makedirs(outdir)
except FileExistsError:
    pass

def plot_nation(nation):

    print(nation)
    html = '<H2>%s</H2><a name="%s"></a>' % (nation, nation)
    p = CovidPlot('it', title=nation)
    p.plot(*extract(csv_confirmed, nation), label='Total cases', **Styles.totalecasi)
    p.plot(*extract(csv_deaths, nation), label='Deaths', **Styles.deceduti)
    p.expfit(*extract(csv_confirmed, nation), **Styles.expfit1)
    p.expfit(*extract(csv_deaths, nation), **Styles.expfit2)
    html += p.save(os.path.join(outdir,'%s.png' % nation))

    p = DailyPlot('en', title='%s - daily cases' % nation)
    p.plot(*extract(csv_confirmed, nation), label='New cases', **Styles.totalecasi)
    p.plot(*extract(csv_deaths, nation), label='Deaths', **Styles.deceduti)
    html += p.save(os.path.join(outdir, '%s_daily.png' % nation))

    p = OOPlot('en', title='%s - Cases' % nation)
    _, cases = extract(csv_confirmed, nation)
    p.plot(cases, smooth=False, **Styles.faintline)
    p.plot(cases)
    html += p.save(os.path.join(outdir, '%s_cases_oo.png' % nation))

    p = OOPlot('en', title='%s - Deaths' % nation,
               xlabel='NumberOfDeaths',
               ylabel='NumberOfDailyDeaths')
    _, cases = extract(csv_deaths, nation)
    p.plot(cases, smooth=False, **Styles.faintline)
    p.plot(cases)
    html += p.save(os.path.join(outdir, '%s_deaths_oo.png' % nation))
    return html

with open(os.path.join(outdir, 'index.html'), 'w') as f:
    f.write('Last update: %s<br>' % last_update)

    for nation in sorted(nations_list()):
        f.write('<a href="#%s">%s</a> ' % (nation, nation))

    with Pool(n_proc) as p:
        html = p.map(plot_nation, sorted(nations_list()))

    f.write('\n'.join(html))


