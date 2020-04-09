#!/usr/bin/env python

import os
import sys
import pandas as pd
from multiprocessing import Pool


from covid import i18n, Styles, CovidPlot, DailyPlot, Table, TestsPlot, OOPlot

try:
    from my_config_italia import csv_dir, outdir, n_proc

except ModuleNotFoundError:
    csv_dir = '../COVID-19-italia'
    homedir = os.getenv('HOME')
    outdir = os.path.join(homedir, 'public_html/coronavirus/italia')
    n_proc = 1


csv_province = os.path.join(csv_dir, 'dati-province/dpc-covid19-ita-province.csv')
csv_regioni = os.path.join(csv_dir, 'dati-regioni/dpc-covid19-ita-regioni.csv')
csv_nazione = os.path.join(csv_dir, 'dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv')


last_update=sys.argv[1]

def lista_province():
    dati = pd.read_csv(csv_province)
    province = filter(lambda x: isinstance(x,str), dati.sigla_provincia.unique())
    # Repeated header becomes a spurious region name
    return filter(lambda x: x != 'sigla_provincia', province)

def lista_regioni():
    dati = pd.read_csv(csv_regioni)
    regioni = filter(lambda x: isinstance(x,str), dati.denominazione_regione.unique())
    # Repeated header becomes a spurious region name
    return filter(lambda x: x != 'denominazione_regione', regioni)

def dati_regione(regione, column):

    dati = pd.read_csv(csv_regioni, parse_dates=['data'])
    filtro = dati['denominazione_regione'] == regione

    data = pd.to_datetime(dati[filtro]['data']).dt.floor('d')
    casi = dati[filtro][column].to_numpy().astype('int64')

    return (data, casi)

def dati_nazione( column):
    dati = pd.read_csv(csv_nazione, parse_dates=['data'])
    data = pd.to_datetime(dati['data']).dt.floor('d')
    casi = dati[column].to_numpy().astype('int64')
    return (data, casi)

def casi_provincia(sigla):
    dati = pd.read_csv(csv_province, parse_dates=['data'])
    filtro = dati['sigla_provincia'] == sigla

    data = pd.to_datetime(dati[filtro]['data']).dt.floor('d')
    casi = dati[filtro]['totale_casi'].to_numpy().astype('int64')
    return (data, casi)

try:
    os.makedirs(outdir)
except FileExistsError:
    pass

def plot_provincia(provincia):
    print(provincia)
    html = '<H2>%s</H2><a name="%s"></a>' % (provincia, provincia)

    p = CovidPlot('it', title=provincia, ymax=1e5)
    p.plot(*casi_provincia(provincia), label='Casi totali', **Styles.totalecasi)
    p.expfit(*casi_provincia(provincia), **Styles.expfit1)
    html += p.save(os.path.join(outdir,'%s.png' % provincia))

    p = DailyPlot('it', title='%s - casi giornalieri' % provincia)
    p.plot(*casi_provincia(provincia), label='Nuovi casi', **Styles.totalecasi)
    html += p.save(os.path.join(outdir, '%s_giornalieri.png' % provincia))

    p = OOPlot('it', title='%s - numero di casi' % provincia)
    _, totale_casi = casi_provincia(provincia)
    p.plot(totale_casi, smooth=False, **Styles.faintline)
    p.plot(totale_casi)
    html += p.save(os.path.join(outdir, '%s_casi_oo.png' % provincia))
    return html

def plot_regione(regione):
    print(regione)
    html = '<H2>%s</H2><a name="%s"></a>' % (regione, regione)
    p = CovidPlot('it', title=regione)
    p.plot(*dati_regione(regione, 'totale_casi'), label='Casi totali', **Styles.totalecasi)
    p.plot(*dati_regione(regione, 'terapia_intensiva'), label='Terapia intensiva', **Styles.ti)
    p.plot(*dati_regione(regione, 'deceduti'), label='Deceduti', **Styles.deceduti)
    p.expfit(*dati_regione(regione, 'totale_casi'), **Styles.expfit1)
    p.expfit(*dati_regione(regione, 'deceduti'), **Styles.expfit2)
    html += p.save(os.path.join(outdir,'%s.png' % regione))

    p = DailyPlot('it', title='%s - casi giornalieri' % regione)
    p.plot(*dati_regione(regione, 'totale_casi'), label='Nuovi casi', **Styles.totalecasi)
    p.plot(*dati_regione(regione, 'deceduti'), label='Deceduti', **Styles.deceduti)
    html += p.save(os.path.join(outdir, '%s_giornalieri.png' % regione))

    p = TestsPlot('it', title='%s - tamponi' % regione)
    data, totale_casi = dati_regione(regione, 'totale_casi')
    _, tamponi = dati_regione(regione, 'tamponi')
    nuovi_casi = totale_casi[1:] - totale_casi[:-1]
    nuovi_tamponi = tamponi[1:] - tamponi[:-1]
    p.plot(data.to_numpy()[1:], nuovi_tamponi, label='Tamponi', width=0.40, color='gray')
    p.plot(data.to_numpy()[1:], nuovi_casi, label='Nuovi casi', shift=0.40, width=0.40, color='red')
    html += p.save(os.path.join(outdir, '%s_tamponi.png' % regione))

    p = OOPlot('it', title='%s - numero di casi' % regione)
    _, totale_casi = dati_regione(regione, 'totale_casi')
    p.plot(totale_casi, smooth=False, **Styles.faintline)
    p.plot(totale_casi)
    html += p.save(os.path.join(outdir, '%s_casi_oo.png' % regione))

    p = OOPlot('it', title='%s - decessi' % regione,
               xlabel='NumberOfDeaths',
               ylabel='NumberOfDailyDeaths')
    _, totale_casi = dati_regione(regione, 'deceduti')
    p.plot(totale_casi, smooth=False, **Styles.faintline)
    p.plot(totale_casi)
    html += p.save(os.path.join(outdir, '%s_deceduti_oo.png' % regione))
    return html



with open(os.path.join(outdir, 'index.html'), 'w') as f:
    f.write('Ultimo aggiornamento: %s<br>' % last_update)
    f.write('<H1>Dati nazionali</H1>\n')
    p = CovidPlot('it', title='Italia')
    p.plot(*dati_nazione('totale_casi'), label='Casi totali', **Styles.totalecasi)
    p.plot(*dati_nazione('terapia_intensiva'), label='Terapia intensiva', **Styles.ti)
    p.plot(*dati_nazione('deceduti'), label='Deceduti', **Styles.deceduti)
    p.expfit(*dati_nazione('totale_casi'), **Styles.expfit1)
    p.expfit(*dati_nazione('deceduti'), **Styles.expfit2)

    t = Table(border=0, style='display: inline-block;')
    f.write(
      t.html( 
        t.row( t.cell( p.save(os.path.join(outdir,'Italia.png')))),
        t.row( t.cell( 'Fit esponenziale sugli ultimi 10 giorni', align='center'))))

    p = CovidPlot('it', title='Italia - andamento')
    p.plot(*dati_nazione('totale_casi'), label='Casi totali', **Styles.totalecasi)
    p.plot(*dati_nazione('deceduti'), label='Deceduti', **Styles.deceduti)
    p.expfit(*dati_nazione('totale_casi'), **Styles.expfit1)
    p.expfit(*dati_nazione('totale_casi'), days_back=1, **Styles.expfit1a)
    p.expfit(*dati_nazione('totale_casi'), days_back=2, **Styles.expfit1b)
    p.expfit(*dati_nazione('totale_casi'), days_back=7, **Styles.expfit1b)

    p.expfit(*dati_nazione('deceduti'), **Styles.expfit2)
    p.expfit(*dati_nazione('deceduti'), days_back=1, **Styles.expfit2a)
    p.expfit(*dati_nazione('deceduti'), days_back=2, **Styles.expfit2b)
    p.expfit(*dati_nazione('deceduti'), days_back=7, **Styles.expfit2b)

    t = Table(border=0, style='display: inline-block;')
    f.write(
      t.html( 
        t.row( t.cell( p.save(os.path.join(outdir,'Italia_andamento.png')))),
        t.row( t.cell( '''Fit esponenziale sugli ultimi 10 giorni, ripetuto
                          per la data odierna, i due giorni precedenti e una settimana fa''', align='center'))))

    p = DailyPlot('it', title='Italia - casi giornalieri')
    p.plot(*dati_nazione('totale_casi'), label='Nuovi casi', **Styles.totalecasi)
    p.plot(*dati_nazione('deceduti'), label='Deceduti', **Styles.deceduti)
    f.write(p.save(os.path.join(outdir, 'Italia_giornalieri.png')))

    p = TestsPlot('it', title='Italia - tamponi')
    data, totale_casi = dati_nazione('totale_casi')
    _, tamponi = dati_nazione('tamponi')
    nuovi_casi = totale_casi[1:] - totale_casi[:-1]
    nuovi_tamponi = tamponi[1:] - tamponi[:-1]
    p.plot(data.to_numpy()[1:], nuovi_tamponi, label='Tamponi', width=0.40, color='gray')
    p.plot(data.to_numpy()[1:], nuovi_casi, label='Nuovi casi', shift=0.40, width=0.40, color='red')
    f.write(p.save(os.path.join(outdir, 'Italia_tamponi.png')))

    p = OOPlot('it', title='Italia - numero di casi')
    _, totale_casi = dati_nazione('totale_casi')
    p.plot(totale_casi, smooth=False, **Styles.faintline)
    p.plot(totale_casi)
    f.write(p.save(os.path.join(outdir, 'Italia_casi_oo.png')))

    p = OOPlot('it', title='Italia - decessi',
                   xlabel='NumberOfDeaths',
                   ylabel='NumberOfDailyDeaths')
    _, totale_casi = dati_nazione('deceduti')
    p.plot(totale_casi, smooth=False, **Styles.faintline)
    p.plot(totale_casi)
    f.write(p.save(os.path.join(outdir, 'Italia_deceduti_oo.png')))

    with Pool(n_proc) as p:
        html = p.map(plot_regione, sorted(lista_regioni()))

    f.write('<H1>Dati regionali</H1>\n')
    for regione in sorted(lista_regioni()):
        f.write('<a href="#%s">%s</a> ' % (regione, regione))
    f.write('\n')

    f.write('\n'.join(html))


    with Pool(n_proc) as p:
        html = p.map(plot_provincia, sorted(lista_province()))

    f.write('<H1>Dati provinciali</H1>\n')
    for provincia in sorted(lista_province()):
        f.write('<a href="#%s">%s</a> ' % (provincia, provincia))
    f.write('\n')
    f.write('\n'.join(html))

    f.write(open('footer.html', 'r').read())

