
from ppgplot_spb import *
import pyfits
import numpy as N
import sys
from math import pi
import cosmology
import time

import gc
gc.collect()

fg_count = 3.5 - N.log10(25)
bg_count = -0.75 - N.log10(25)

plots_path = '/Users/spb/Work/projects/GalaxyZoo2/plots/'
data_path = '/Users/spb/Work/projects/GalaxyZoo2/'
wvt_path = data_path

bins = {'redshift': (0.01, 0.15, 0.01),
        'petroMag_MrU': (-24.0, -15.0, 0.05),
        'petroR50_r_kpc': (0.0, 15.0, 0.1)}

min_zbin = 0
b = bins['redshift']
max_zbin = len(N.arange(b[0], b[1], b[2]))-1
min_sizebin = 0      # MUST BE ZERO
b = bins['petroR50_r_kpc']
max_sizebin = len(N.arange(b[0], b[1], b[2]))-1
min_magbin = 0       # MUST BE ZERO
b = bins['petroMag_MrU']
max_magbin = len(N.arange(b[0], b[1], b[2]))-1

pgend()

def do_all():
    # starting with gz2sample_final1.fits from CAS
    # execute run_kcorrect.pro in IDL producing gz2sample_final1_kcorrect.fits
    add_physical_sizes()
    add_regions()
    check_regions()
    add_bins()
    add_bin_counts()
    # run wvt_gz2.pro in IDL
    plot_all_wvt()
    add_wvt()
    make_db_table()

def notNaN(x):
    return (x > 0.0) | (x <= 0.0)

def add_physical_sizes():
    p = pyfits.open(data_path+'gz2sample_final1_kcorrect.fits')
    d = p[1].data
    r50_arcsec = d.field('petroR50_r')
    redshift = d.field('redshift')
    r50_kpc = redshift * 0.0
    zmask = notNaN(redshift)
    # H0=70 angular scale
    angscale = cosmology.ang_scale_flat(redshift[zmask]).astype(N.float32)
    r50_kpc[zmask] = (r50_arcsec[zmask] * angscale)
    oldcols = p[1].columns
    cols = []
    for c in oldcols:
	name = c.name
	cols.append(pyfits.Column(name=c.name, format=c.format,
				  array=d.field(c.name)))
    cols.append(pyfits.Column(name='PETROR50_R_KPC', format='E',
			      array=r50_kpc))
    tbhdu=pyfits.new_table(cols)
    tbhdu.name = 'data'
    outfile = data_path+'gz2sample_final1_abs.fits'
    file_exists = os.path.isfile(outfile)
    if file_exists:
	os.remove(outfile)
    tbhdu.writeto(outfile)
    p.close()

def add_regions():
    # get data
    p = pyfits.open(data_path+'gz2sample_final1_abs.fits')
    data = p[1].data
    ra = data.field('RA')
    dec = data.field('DEC')
    n = len(ra)
    print 'Number of objects in catalogue:', n
    # calculate survey coords
    print 'Calculating survey coords'
    lam, eta = ra_dec_to_lambda_eta(ra, dec)
    # divide
    lamdivide = [-90, -23, 2, 27, 90]
    etadivide = [-90, 5, 180]
    region = N.zeros(n)
    pgopen(plots_path + 'gz2_regions.ps/cps')
    pgsetup()
    pgenv(-90, 90, -90, 180)
    pglab('lambda', 'eta', '') 
    pgsch(0.1)
    pgxsci('red') 
    pgxpt(lam[::10], eta[::10], 'dot')
    pgxsci('black')
    for l in lamdivide:
        pgline(N.array([l, l]), N.array([-90, 180]))
    for e in etadivide:
        pgline(N.array([-90, 90]), N.array([e, e]))
    pgsch(0.8*ch)
    for li in range(len(lamdivide)-1):
        for ei in range(len(etadivide)-1):
            s = (lam > lamdivide[li]) & (lam <= lamdivide[li+1])
            s &= (eta > etadivide[ei]) & (eta <= etadivide[ei+1])            
            ns = len(N.where(s)[0])
            r = ei * (len(lamdivide)-1) + li + 1
            region[s] = r
            plam = (lamdivide[li] + lamdivide[li+1])/2.0
            peta = (etadivide[ei] + etadivide[ei+1])/2.0
            pgptxt(plam, peta-10, 0.0, 0.5, '%i'%ns)
            pgptxt(plam, peta+10, 0.0, 0.5, 'R%i'%r)
            print r, li, ei, ns
    pgclos()
    oldcols = p[1].columns
    cols = []
    for c in oldcols:
	name = c.name
        cols.append(pyfits.Column(name=c.name, format=c.format,
                                  array=data.field(c.name)))
    cols.append(pyfits.Column(name='REGION', format='I',
			      array=region))
    tbhdu=pyfits.new_table(cols)
    tbhdu.name = 'data'
    outfile = data_path+'gz2sample_final1_abs_regions.fits'
    file_exists = os.path.isfile(outfile)
    if file_exists:
	os.remove(outfile)
    tbhdu.writeto(outfile)
    p.close()


def check_regions():
    # get data
    data = pyfits.getdata(data_path+'gz2sample_final1_abs_regions.fits')
    ra = data.field('RA')
    dec = data.field('DEC')
    n = len(ra)
    print 'Number of objects in catalogue:', n
    # calculate survey coords
    print 'Calculating survey coords'
    lam, eta = ra_dec_to_lambda_eta(ra, dec)
    # divide
    lamdivide = [-90, -23, 2, 27, 90]
    etadivide = [-90, 5, 180]
    region = data.field('region')
    pgopen(plots_path + 'gz2_regions_check.ps/cps')
    pgsetup()
    pgenv(-90, 90, -90, 180)
    pglab('lambda', 'eta', '') 
    pgsch(0.1)
    pgxsci('red')
    col = ['red', 'green', 'orange', 'blue', 'grape', 'dark-orange',
           'black', 'cyan']
    for r in range(region.min(), region.max()+1):
        pgxsci(col[r-1])
        s = region == r
        pgxpt(lam[s][::10], eta[s][::10], 'dot')
    pgxsci('black')
    for l in lamdivide:
        pgline(N.array([l, l]), N.array([-90, 180]))
    for e in etadivide:
        pgline(N.array([-90, 90]), N.array([e, e]))
    pgsch(0.8*ch)
    for li in range(len(lamdivide)-1):
        for ei in range(len(etadivide)-1):
            r = ei * (len(lamdivide)-1) + li + 1
            s = region == r
            ns = len(N.where(s)[0])
            plam = (lamdivide[li] + lamdivide[li+1])/2.0
            peta = (etadivide[ei] + etadivide[ei+1])/2.0
            pgptxt(plam, peta-10, 0.0, 0.5, '%i'%ns)
            pgptxt(plam, peta+10, 0.0, 0.5, 'R%i'%r)
            print r, li, ei, ns
    pgclos()


def lambda_eta_to_ra_dec(l, e):
    d = N.arcsin(N.cos(l*pi/180)*N.sin((e+32.5)*pi/180))*180/pi
    r = 95 + N.arccos(-N.sin(l*pi/180)/N.cos(d*pi/180))*180/pi
    r = N.where(e+32.5 > 90.0, 190.0 - r, r)
    r = N.where(r < 0.0, r + 360.0, r)
    return r, d

def ra_dec_to_lambda_eta(ra, dec):
    cosdec = N.cos(dec*pi/180)
    #print 'cosdec:', cosdec
    ra95 = ra - 95.0
    lam = N.arcsin(-N.cos(ra95*pi/180)*cosdec)*180/pi
    #print 'lam:', lam
    coslam = N.cos(lam*pi/180)
    #print 'coslam:', coslam
    coslamzero = N.abs(coslam) < 1e-12
    coslam = N.where(coslamzero, 1.0, coslam)
    #print 'coslam:', coslam
    x = N.where(coslamzero, 0.0, N.sin(ra95*pi/180)*cosdec/coslam)
    #print 'x:', x
    eta = N.where(N.abs(x) >= 1.0, -32.5, -32.5 + N.arccos(x)*180/pi)
    #print 'eta:', eta
    eta = N.where((dec < 0.0) & ((ra < 95) | (ra > 180+95)),
                  (180-32.5) + (180-32.5) - eta, eta)
    eta = N.where((dec < 0.0) & ((ra > 95) & (ra < 180+95)),
                  -32.5 - 32.5 - eta, eta)
    #print 'eta:', eta
    return lam, eta

def add_bins():
    p = pyfits.open(data_path+'gz2sample_final1_abs_regions.fits')
    d = p['data'].data
    redshift = d.field('redshift')
    zmask = notNaN(redshift)
    oldcols = p['data'].columns
    bincols = {}
    cols = []
    for c in oldcols:
	cols.append(pyfits.Column(name=c.name, format=c.format,
				  array=d.field(c.name)))
    for k in bins.keys():
        x = d.field(k)[zmask]
        bin_min, bin_max, bin_step = bins[k]
        xbin = N.zeros(redshift.shape, N.int) - 9999
        xbinz = (N.floor((x - bin_min) / bin_step)).astype(N.int)
        maxbin = int(round((bin_max - bin_min) / bin_step))
        print k, maxbin
        low = xbinz < 0
        high = xbinz >= maxbin
        xbinz[low] = -999
        xbinz[high] = 999
        xbin[zmask] = xbinz
        name = '%s_simple_bin'%k
        cols.append(pyfits.Column(name=name,
                                  format='I', array=xbin))
        bin = N.arange(0, maxbin, 1)
        min = bin * bin_step + bin_min
        max = min + bin_step
        center = min + 0.5*bin_step
        bincols[k] = [pyfits.Column(name='bin', format='I', array=bin),
                      pyfits.Column(name='min', format='E', array=min),
                      pyfits.Column(name='max', format='E', array=max),
                      pyfits.Column(name='centre', 
                                    format='E', array=center)]
    hdulist = pyfits.HDUList()
    hdulist.append(pyfits.PrimaryHDU())
    tbhdu=pyfits.new_table(cols)
    tbhdu.name = 'data'
    hdulist.append(tbhdu)
    for k in bincols.keys():
	c = bincols[k]
	tbhdu=pyfits.new_table(c)
        tbhdu.name = '%s_simple_bins'%k
	hdulist.append(tbhdu)
        outfile = data_path+'gz2sample_final1_abs_regions_bins.fits'
    file_exists = os.path.isfile(outfile)
    if file_exists:
	os.remove(outfile)
    hdulist.writeto(outfile)
    p.close()

def add_bin_counts():
    # Determine counts in each mag, size and z bin
    infile = data_path+'gz2sample_final1_abs_regions_bins.fits'
    p = pyfits.open(infile)
    data = p['data'].data
    # determine bins
    zbins = p['redshift_simple_bins'].data.field('bin')
    n_zbins = len(zbins)
    magbins = p['petroMag_MrU_simple_bins'].data.field('bin')
    n_magbins = len(magbins)
    sizebins = p['petroR50_r_kpc_simple_bins'].data.field('bin')
    n_sizebins = len(sizebins)
    print 'n_zbins =', n_zbins
    print 'n_magbins =', n_magbins
    print 'n_sizebins =', n_sizebins
    n_total = n_zbins * n_magbins * n_sizebins
    print 'n_total =', n_total
    n = N.zeros((n_zbins, n_magbins, n_sizebins), N.int)
    tstart = time.time()
    for iz in zbins:
        print 'iz = %i '%iz + '-'*50
        if iz > 0:
            tgone = time.time() - tstart
            ngone = iz * n_magbins * n_sizebins
            ntogo = n_total - ngone
            ttogo = ntogo * tgone / ngone
            tmingone = int(tgone/60)
            tsecgone = int(tgone - tmingone*60)
            tmintogo = int(ttogo/60)
            tsectogo = int(ttogo - tmintogo*60)
            print 'time taken: %i min %i sec'%(tmingone, tsecgone)
            print 'approx. time remaining: %i min %i sec'%(tmintogo, tsectogo)
        sys.stdout.flush()
        z_selection = data.field('redshift_simple_bin') == iz
        if not N.any(z_selection):  continue
        d_z = data[z_selection]
        gc.collect()
        for imag in magbins:
            mag_selection = d_z.field('petroMag_MrU_simple_bin') == imag
            if not N.any(mag_selection):  continue
            d_mag = d_z[mag_selection]
            for isize in sizebins:
                selection = d_mag.field('petroR50_r_kpc_simple_bin') == isize
                if not N.any(selection):  continue
                d = d_mag[selection]
                n[iz, imag, isize] = len(N.where(selection)[0])
    hdu = pyfits.ImageHDU(n) 
    hdu.name = 'simple_bin_counts'
    p.append(hdu)
    outfile = data_path+'gz2sample_final1_abs_regions_counts.fits'
    file_exists = os.path.isfile(outfile)
    if file_exists:
	os.remove(outfile)
    p.writeto(outfile)
    p.close()

def plot_all_wvt():
    fname = 'gz2_wvt_bins'
    fd = wvt_path+fname+'.fits'
    nz = pyfits.getval(fd, 'NAXIS3')
    print nz
    for fname in ['gz2_wvt_bins', 'gz2_wvt_counts_all']:
        for iz in range(nz):
            plot_wvt(iz, fname)
    for iz in range(nz):
        plot_wvt(iz, fname='gz2_wvt_density_all', logplot=True)
    

def plot_wvt(zbin=5, fname='gz2_wvt_bins', logplot=False):
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
    fn = wvt_path+'gz2_wvt_nodes.fits'
    nodes = pyfits.getdata(fn)
    nodes = nodes[zbin]
    nodes = nodes[:,(nodes[0] > 0.001) & (nodes[1] > 0.001)]    
    bin_min, bin_max, bin_step = bins['petroMag_MrU']
    nodes[1] = (nodes[1] + 0.5) * bin_step + bin_min
    bin_min, bin_max, bin_step = bins['petroR50_r_kpc']
    nodes[0] = (nodes[0] + 0.5) * bin_step + bin_min
    f = data_path+'gz2sample_final1_abs_regions_counts.fits'
    p = pyfits.open(f)
    zbins = p['redshift_simple_bins'].data
    magbins = p['petroMag_MrU_simple_bins'].data
    sizebins = p['petroR50_r_kpc_simple_bins'].data
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
        pgimag_s(hires(d), d.max()*1.05, d.min()*0.9)
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
    fwvt = wvt_path+'gz2_wvt_bins.fits'
    wvt = pyfits.getdata(fwvt)
    f = data_path+'gz2sample_final1_abs_regions_counts.fits'
    p = pyfits.open(f)
    d = p['data'].data
    zbin = d.field('redshift_simple_bin')
    nowvt = (zbin > max_zbin) | (zbin < min_zbin)
    zbin = N.where(zbin > max_zbin, max_zbin, zbin)
    zbin = N.where(zbin < min_zbin, min_zbin, zbin)
    magbin = d.field('petroMag_MrU_simple_bin')
    nowvt |= (magbin > max_magbin) | (magbin < min_magbin)
    magbin = N.where(magbin > max_magbin, max_magbin, magbin)
    magbin = N.where(magbin < min_magbin, min_magbin, magbin)
    sizebin = d.field('petroR50_r_kpc_simple_bin')
    nowvt |= (sizebin > max_sizebin) | (sizebin < min_sizebin)
    sizebin = N.where(sizebin > max_sizebin, max_sizebin, sizebin)
    sizebin = N.where(sizebin < min_sizebin, min_sizebin, sizebin)
    wvtbin = wvt[zbin, magbin, sizebin]
    # put wvtbin = 0 where galaxy is not in a wvt bin
    wvtbin = N.where(nowvt, 0, wvtbin)
    oldcols = p['data'].columns
    cols = []
    for c in oldcols:
	name = c.name
	cols.append(pyfits.Column(name=c.name, format=c.format,
				  array=d.field(c.name)))
    cols.append(pyfits.Column(name='WVT_BIN', format='I',
			      array=wvtbin))
    hdulist = pyfits.HDUList()
    hdulist.append(pyfits.PrimaryHDU())
    tbhdu=pyfits.new_table(cols)
    tbhdu.name = 'data'
    hdulist.append(tbhdu)
    for ip in p[1:]:
        if ip.name.lower() != 'data':
            hdulist.append(ip)
    outfile = data_path+'gz2sample_final1_abs_regions_counts_wvt.fits'
    file_exists = os.path.isfile(outfile)
    if file_exists:
	os.remove(outfile)
    hdulist.writeto(outfile)

def make_db_table():
    # table for GZ2 site database
    f = data_path+'gz2sample_final1_abs_regions_counts_wvt.fits'
    p = pyfits.open(f)
    d = p['data'].data
    n = len(d)
    oldcols = p['data'].columns
    cols = []
    for c in oldcols:
	name = c.name.upper()
        if name in ['OBJID', 'RA', 'DEC', 'REDSHIFT', 'PETROR90_R',
                    'REGION', 'REDSHIFT_SIMPLE_BIN', 'WVT_BIN']:
            name = name.replace('PETROR90_R', 'SIZE')
            name = name.replace('_SIMPLE', '')
            cols.append(pyfits.Column(name=name, format=c.format,
                                      array=d.field(c.name)))
    cols.append(pyfits.Column(name='CLASSCOUNT', format='I',
                                   array=N.zeros(n)))
    cols.append(pyfits.Column(name='COMPCOUNT', format='I',
                                   array=N.zeros(n)))
    tbhdu=pyfits.new_table(cols)
    tbhdu.name = 'data'
    outfile = data_path+'gz2sample_db.fits'
    file_exists = os.path.isfile(outfile)
    if file_exists:
	os.remove(outfile)
    tbhdu.writeto(outfile)

def make_db_table2():
    # table for GZ2 site database which matches old table columns
    f = data_path+'gz2sample_final1_abs_regions_counts_wvt.fits'
    p = pyfits.open(f)
    d = p['data'].data
    n = len(d)
    oldcols = p['data'].columns
    cols = []
    i = 0
    colnames = ['objectId', 'run', 'rerun', 'camcol', 'field', 'obj',
                'rightAscension', 'declination', 'apparentMagnitude',
                'petrosianRadius']
    for name in ['OBJID', 'RUN', 'RERUN', 'CAMCOL', 'FIELD', 'OBJ',
                    'RA', 'DEC', 'PETROMAG_R', 'PETROR90_R']:
        for c in oldcols:
            # original GZ table has entries:
            if name ==c.name:
                print c.name, colnames[i]
                cols.append(pyfits.Column(name=colnames[i], format=c.format,
                                          array=d.field(c.name)))
                i += 1
    print cols
    tbhdu=pyfits.new_table(cols)
    tbhdu.name = 'data'
    outfile = data_path+'gz2sample_db2.fits'
    file_exists = os.path.isfile(outfile)
    if file_exists:
	os.remove(outfile)
    tbhdu.writeto(outfile)
