#!/usr/bin/env python

import sys
import os.path
import pandas as pd
from datetime import date, timedelta

from covid import i18n, Styles, CovidPlot, DailyPlot, OOPlot


try:
    from my_config_us import csv_dir, outdir

except ModuleNotFoundError:
    csv_dir = '../COVID-19-world/csse_covid_19_data/csse_covid_19_daily_reports'
    homedir = os.getenv('HOME')
    outdir = os.path.join(homedir, 'public_html/coronavirus/us')

last_update = sys.argv[1]

def states_list():

#    return ['Alabama', 'New York']
    a = pd.read_csv(os.path.join(csv_dir, '03-19-2020.csv'))
    b = a.loc[ a['Country/Region'] == 'US']
    c = b.loc[ b['Province/State'].str.contains(',') == False]
    d = c.loc[ c['Province/State'].str.contains('Princess') == False]
    e = d.loc[ d['Province/State'] != 'US']
    return e.to_numpy()[:,0]

def parse_old_csv(filename, date):
    a = pd.read_csv(filename)
    b = a.loc[ a['Country/Region'] == 'US']
    c = b.loc[ b['Province/State'].str.contains(',') == False]
    d = c.loc[ c['Province/State'].str.contains('Princess') == False]
    e = d.loc[ d['Province/State'] != 'US']
    f = e[['Province/State', 'Last Update', 'Confirmed', 'Deaths']].copy()
    f['Last Update'] = date
    return f

def parse_new_csv(filename, date):
    a = pd.read_csv(filename)
    b = a.loc[ a['Country_Region'] == 'US']
    c = b.groupby('Province_State').sum().reset_index()
    d = c[['Province_State', 'Confirmed', 'Deaths']].copy()
    d['Last Update'] = date
    d = d.rename(columns={'Province_State': 'Province/State'})
    return d

def parse_all(csv_dir):

    # Previous format
    dates = pd.date_range('2020-03-10', '2020-03-21')
    f = [(os.path.join(csv_dir, date.strftime('%m-%d-%Y')+'.csv'), date) for date in dates]
    csv_old = [parse_old_csv(fname, date) for fname,date in f]

    # New format
    dates = pd.date_range('2020-03-22', date.today() - timedelta(days=1))
    f = [(os.path.join(csv_dir, date.strftime('%m-%d-%Y')+'.csv'), date) for date in dates]
    csv_new = [parse_new_csv(fname, date) for fname,date in f]
    return pd.concat(csv_old + csv_new)

def extract(csv_all, state, column_name):

    df = csv_all.loc[ csv_all['Province/State'] == state]
    date = pd.to_datetime(df['Last Update']).dt.floor('d')
    series = df[column_name]

    return (date, series.to_numpy().astype('int64'))
    
try:
    os.makedirs(outdir)
except FileExistsError:
    pass

with open(os.path.join(outdir, 'index.html'), 'w') as f:

    csv_all = parse_all(csv_dir)

    f.write('Last update: %s<br>' % last_update)
    for state in sorted(states_list()):
        f.write('<a href="#%s">%s</a> ' % (state, state))

    for state in sorted(states_list()):
        print(state)
        f.write('<H2>%s</H2><a name="%s"></a>' % (state, state))
        p = CovidPlot('en', title=state)
        p.plot(*extract(csv_all, state, 'Confirmed'), label='Total cases', **Styles.totalecasi)
        p.plot(*extract(csv_all, state, 'Deaths'), label='Deaths', **Styles.deceduti)
        p.expfit(*extract(csv_all, state, 'Confirmed'), **Styles.expfit1)
        p.expfit(*extract(csv_all, state, 'Deaths'), **Styles.expfit2)
        f.write(p.save(os.path.join(outdir,'%s.png' % state)))

        p = DailyPlot('en', title='%s - daily cases' % state)
        p.plot(*extract(csv_all, state, 'Confirmed'), label='New cases', **Styles.totalecasi)
        p.plot(*extract(csv_all, state, 'Deaths'), label='Deaths', **Styles.deceduti)
        f.write(p.save(os.path.join(outdir, '%s_daily.png' % state)))

        p = OOPlot('en', title='%s - Cases' % state)
        _, cases = extract(csv_all, state, 'Confirmed')
        p.plot(cases, smooth=False, **Styles.faintline)
        p.plot(cases)
        f.write(p.save(os.path.join(outdir, '%s_cases_oo.png' % state)))

        p = OOPlot('en', title='%s - Deaths' % state,
                           xlabel='NumberOfDeaths',
                           ylabel='NumberOfDailyDeaths')
        _, cases = extract(csv_all, state, 'Deaths')
        p.plot(cases, smooth=False, **Styles.faintline)
        p.plot(cases)
        f.write(p.save(os.path.join(outdir, '%s_deaths_oo.png' % state)))



