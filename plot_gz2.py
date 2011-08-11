from ppgplot_spb import *
import numpy
import pyfits
import tables
from scipy.interpolate import splrep, splev

pgend()

def plot_user_consistency():
    f = '../data/final/user_consistency_cumhisto1.csv'
    d = numpy.genfromtxt(f, dtype=[('consistency', 'f4'), ('count', 'i4'),
                                   ('avg_n_class', 'f4'), ('cumcount', 'i8'),
                                   ('cumfrac', 'f4')], names=None, delimiter=',')
    pgopen('../plots/user_consistency.ps/cps')
    pgsetup()
    total = d['cumcount'][-1]
    logtotal = numpy.log10(total)
    pgsvp(0.2, 0.7, 0.2, 0.7)
    pgswin(0, 1, logtotal-4, logtotal)
    pgbox('', 0, 0, 'CMTSL', 0, 0)
    pgswin(0, 1, -4, 0)
    pgbox('BCNTS', 0, 0, 'BNTSL', 0, 0)
    pgmtxt('B', 2.5, 0.5, 0.5, 'consistency')
    pgmtxt('L', 2.5, 0.5, 0.5, 'cumulative fraction')
    pgmtxt('R', 2.5, 0.5, 0.5, 'cumulative count')
    for i in (1,3):
        f = '../data/final/user_consistency_cumhisto%i.csv'%i
        d = numpy.genfromtxt(f, dtype=[('consistency', 'f4'), ('count', 'i4'),
                                       ('avg_n_class', 'f4'), ('cumcount', 'i8'),
                                       ('cumfrac', 'f4')], names=None, delimiter=',')
        x = d['consistency']
        y = numpy.log10(numpy.maximum(d['cumfrac'], 1.0e-5))
        if i == 3:
            ls = 1
            pgsls(2)
            y1 = y[numpy.argmin(numpy.abs(x-0.60))]
            y2 = y[numpy.argmin(numpy.abs(x-0.35))]
            pgline(numpy.array([0.6, 0.6]), numpy.array([-5, y1]))
            pgline(numpy.array([0.0, 0.6]), numpy.array([y1, y1]))
            pgline(numpy.array([0.35, 0.35]), numpy.array([-5, y2]))
            pgline(numpy.array([0.0, 0.35]), numpy.array([y2, y2]))
        elif i == 2:
            ls = 2
        else:
            ls = 4
        pgsls(ls)
        pgbin(x, y)
    pgsvp(0.2, 0.7, 0.7, 0.9)
    n = numpy.log10(d['avg_n_class'])
    pgswin(0, 1, 0.1, n.max()*1.1)
    pgbox('BCTS', 0, 0, 'BCNTSVL', 0, 0)
    pgmtxt('L', 2.5, 0.3, 0.5, '\(2227)n\(2228)')
    pgbin(x, n)
    pgclos()
    return d


def plot_classification_counts():
    h5file = tables.openFile('../data/final/gz2table.h5')
    d = h5file.root.gz2table
    pgopen('../plots/classification_counts.ps/cps')
    pgsetup()
    #nall = d.col('t01_smooth_or_features_total_weight')
    nall = d.col('t01_smooth_or_features_total_count')
    pgsvp(0.3, 0.9, 0.3, 0.9)
    nmax = 70
    pgswin(0, nmax, 0, 0.2)
    pgbox('BCNTS', 0, 0, 'BCNTS', 0, 0)
    pgmtxt('B', 2.5, 0.5, 0.5, 'classification count')
    pgmtxt('L', 2.5, 0.5, 0.5, 'fraction')
    sample = d.col('sample')
    c = ['strawberry', 'blue', 'green', 'aqua', 'orange', 'grape']
    for i, s in enumerate(('original', 'extra', 'stripe82',
                           'stripe82_coadd_1', 'stripe82_coadd_2')):
        print s,
        if s == 'standard':
            n = nall[(sample == 'original') | (sample == 'extra')]
        else:
            n = nall[sample == s]
        lenn = len(n)
        print lenn
        if lenn < 1: continue
        xbin, ybin = bin_array(n, nmax, 0, nmax)
        ybin /= lenn
        pgxsci(c[i])
        pgbin(xbin+i*0.2-0.4, ybin)
        pgtext(30, 0.185-i*0.012, s)
        pgsci(1)
    pgclos()
    h5file.close()


def plot_classifications_per_user(s=0.0):
    f = '../data/final/count_classifications_per_user.csv'
    d = numpy.genfromtxt(f, dtype=[('nclassifications', 'i8'), ('nusers', 'i8'),
                                   ('fracusers', 'f4'),
                                   ('fracclassifications', 'f4'),
                                   ('cumnusers', 'i8'),
                                   ('cumfracusers', 'f4'),
                                   ('cumfracclassifications', 'f4')],
                         names=None, delimiter=',')
    pgopen('../plots/classifications_per_user.ps/cps')
    pgsetup()
    pgslw(2*lw)
    pgsch(1.2*ch)
    pgsvp(0.2, 0.9, 0.2, 0.9)
    #xmax = N.log10(d['nclassifications'][-1])
    xmax = 5.2
    pgswin(0, xmax, -0.002, 1)
    pgbox('BCLNTS', 0, 0, 'BCTS', 0.2, 4)
    pgmtxt('B', 2.5, 0.5, 0.5, 'classifications per user')
    pgxsci('lightgray')
    pgbox('', 0, 0, 'M', 0.2, 4)
    pgmtxt('R', 2.5, 0.5, 0.5, 'cumulative fraction')
    pgxsci('darkgray')
    pgbox('', 0, 0, 'N', 0.2, 4)
    pgmtxt('L', 2.5, 0.5, 0.5, 'fraction per dex')
    pgxsci('dark-blue')
    pgtext(0.2, 0.825, 'users')
    pgxsci('dark-red')
    pgtext(0.2, 0.9, 'classifications')
    x = N.log10(d['nclassifications'])
    y = d['cumfracusers']
    z = d['cumfracclassifications']
    x = N.concatenate(([-1], x, [xmax+1]))
    y = N.concatenate(([0.001], y, [1.0]))
    z = N.concatenate(([0.001], z, [1.0]))
    # interpolate
    #tcky = splrep(x, y, s=s)
    #tckz = splrep(x, z, s=s)
    t = N.arange(0.25, xmax, 0.3)
    tcky = splrep(x, y, t=t)
    tckz = splrep(x, z, t=t)
    # interpolated versions
    xf = N.arange(0, xmax+0.1, 0.1)
    yf = splev(xf, tcky, 0)
    ydf = splev(xf, tcky, 1)
    zf = splev(xf, tckz, 0)
    zdf = splev(xf, tckz, 1)
    pgslw(2*lw)
    pgxsci('light-blue')
    pgline(xf, yf)
    pgxsls('dashed')
    pgxsci('light-red')    
    pgline(xf, zf)
    pgxsls('solid')
    dy, y = bin_array(N.log10(d['nclassifications']), 30, -0.2, xmax,
                      weights=d['nusers'])
    y /= y.sum() * (xmax+0.2)/30
    #dy = N.concatenate(([0], dy))
    #y = N.concatenate((d['fracusers'][:1], y))
    dz, z = bin_array(N.log10(d['nclassifications']), 30, -0.2, xmax,
                      weights=d['nusers']*d['nclassifications'])
    z /= z.sum() * (xmax+0.2)/30
    #ymax = max(y.max(), z.max()) * 1.1
    #pgswin(0, xmax, 0, ymax)
    #pgbox('', 0, 0, 'BNTS', 0.2, 4)
    #pgswin(0, xmax, 0, 1.0)
    pgslw(4*lw)
    pgxsci('dark-blue')
    pgline(xf, ydf)
    pgxsls('dashed')
    pgxsci('dark-red')
    pgline(xf, zdf)
    pgxsls('solid')
    pgxsci('black')
    pgslw(lw)
    pgclos()
