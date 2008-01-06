from ppgplot_spb import *
import pyfits
import numpy as N

import gc
gc.collect()

plots_path = '../plots/'
wvt_path = '/Users/spb/Work/projects/GalaxyZoo2/adaptive_binning/'
data_path = '/Users/spb/Work/projects/GalaxyZoo/'
data_file = 'dr6_zoo_selected_counts.fits'

binoversamp = 5

min_zbin = 0
max_zbin = 24
min_sizebin = 0      # MUST BE ZERO
max_sizebin = 23*binoversamp
min_magbin = 0       # MUST BE ZERO
max_magbin = 27*binoversamp

scheme = ('WEIGHTS', 'CSUW')

bins = {'REDSHIFT': (0.0, 0.25, 0.01),
        'MR': (-24.0, -15.0, 0.25),
        'R50_KPC': (0.0, 15.0, 0.5)}

fg_count = 3.5 - N.log10(25)
bg_count = -0.75 - N.log10(25)

def plot_all():
    fname='zoo_wvt_bins'
    fd = wvt_path+fname+'.fits'
    nz = pyfits.getval(fd, 'NAXIS3')
    print nz
    for fname in ['zoo_wvt_bins', 'zoo_wvt_counts_all']:
        for iz in range(nz):
            plot(iz, fname)
    for iz in range(nz):
        plot(iz, fname='zoo_wvt_density_all', logplot=True)
    

def plot(zbin=5, fname='zoo_wvt_bins', logplot=False):
    fd = wvt_path+fname+'.fits'
    d = pyfits.getdata(fd)
    d = d[zbin, min_magbin:max_magbin+1,
          min_sizebin:max_sizebin+1]
    d = d.transpose()
    print d.sum()
    if logplot:
        mask = d <= 0.0
        d[mask] = 1.0
        d = N.log10(d)
        d[mask] = bg_count
    fn = wvt_path+'zoo_wvt_nodes.fits'
    nodes = pyfits.getdata(fn)
    nodes = nodes[zbin]
    nodes = nodes[:,(nodes[0] > 0.001) & (nodes[1] > 0.001)]    
    bin_min, bin_max, bin_step = bins['MR']
    bin_step /= binoversamp
    nodes[1] = nodes[1] * bin_step + bin_min
    bin_min, bin_max, bin_step = bins['R50_KPC']
    bin_step /= binoversamp
    nodes[0] = nodes[0] * bin_step + bin_min
    f = data_path+data_file
    p = pyfits.open(f)
    zbins = p['REDSHIFT_ZOO_OVERSAMPLED_BINS'].data
    magbins = p['MR_ZOO_OVERSAMPLED_BINS'].data
    sizebins = p['R50_KPC_ZOO_OVERSAMPLED_BINS'].data
    pgend()
    fplot = fname+'_zbin_%i.ps'%zbin
    pgopen(plots_path+fplot+'/cps')
    pgsetup()
    pgpap(0, float(max_sizebin-min_sizebin+1)/(max_magbin-min_magbin+1))
    setup_colour_table('smooth2', 'ramp', flip_colours=False)
    pgsch(1.2*ch)
    pgenv(magbins[min_magbin].field('MIN'),
          magbins[max_magbin].field('MAX'),
          sizebins[min_sizebin].field('MIN'),
          sizebins[max_sizebin].field('MAX'), -2)
    pglab('M\dr\u', 'R\d50\u (kpc)', '')
    if 'density' in fname and logplot:
        pgimag_s(hires(d), fg_count, bg_count)
    else:
        pgimag_s(hires(d), d.max()*1.1, d.min()*0.9)
    print d.max(), d.min()
    pgbox('BCN', 0, 0, 'BCN', 0, 0)
    pgxsci('white')
    pgxpt(nodes[1], nodes[0], 'point')
    pgclos()


oversamp = 10
def hires(x):
    x_hires = N.zeros([s*oversamp for s in x.shape])
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):    
            x_hires[i*oversamp:(i+1)*oversamp,
                        j*oversamp:(j+1)*oversamp] = x[i, j]
    return x_hires


def add_wvt():
    fwvt = wvt_path+'zoo_wvt_bins.fits'
    wvt = pyfits.getdata(fwvt)
    f = data_path+data_file
    p = pyfits.open(f)
    d = p['DATA'].data
    zbin = d.field('REDSHIFT_ZOO_OVERSAMPLED_BIN')
    zbin = N.where(zbin > max_zbin, max_zbin, zbin)
    zbin = N.where(zbin < min_zbin, min_zbin, zbin)
    magbin = d.field('MR_ZOO_OVERSAMPLED_BIN')
    magbin = N.where(magbin > max_magbin, max_magbin, magbin)
    magbin = N.where(magbin < min_magbin, min_magbin, magbin)
    sizebin = d.field('R50_KPC_ZOO_OVERSAMPLED_BIN')
    sizebin = N.where(sizebin > max_sizebin, max_sizebin, sizebin)
    sizebin = N.where(sizebin < min_sizebin, min_sizebin, sizebin)
    wvtbin = wvt[zbin, magbin, sizebin]
    oldcols = p['DATA'].columns
    cols = []
    smallcols = []
    for c in oldcols:
	name = c.name
	cols.append(pyfits.Column(name=c.name, format=c.format,
				  array=d.field(c.name)))
    cols.append(pyfits.Column(name='WVTBIN', format='I',
			      array=wvtbin))
    smallcols.append(pyfits.Column(name='OBJID', format='K',
                                   array=d.OBJID))
    smallcols.append(pyfits.Column(name='ZBIN', format='I',
                                   array=d.REDSHIFT_ZOO_OVERSAMPLED_BIN))
    smallcols.append(pyfits.Column(name='WVTBIN', format='I',
                                   array=wvtbin))
    hdulist = pyfits.HDUList()
    hdulist.append(pyfits.PrimaryHDU())
    tbhdu=pyfits.new_table(cols)
    tbhdu.name = 'DATA'
    hdulist.append(tbhdu)
    for ip in p[1:]:
        if ip.name != 'DATA':
            hdulist.append(ip)
    outfile = '../dr6_zoo_wvt.fits'
    file_exists = os.path.isfile(outfile)
    if file_exists:
	os.remove(outfile)
    hdulist.writeto(outfile)
    tbhdu=pyfits.new_table(smallcols)
    tbhdu.name = 'WVTBINS'
    outfile = '../dr6_wvt_bins.fits'
    file_exists = os.path.isfile(outfile)
    if file_exists:
	os.remove(outfile)
    tbhdu.writeto(outfile)
    p.close()

