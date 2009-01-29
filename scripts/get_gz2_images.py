import urllib
import os.path
import numpy as N
from ppgplot_spb import *
import time
from scipy import median
from scipy.ndimage import median_filter
import string
import gc
import webbrowser

from get_gz2_data import *
data = gz2data

field_path = '/Volumes/Storage/data/SDSS/fields/'
object_path = '/Volumes/Storage/data/SDSS/gzobjects/' 
#field_path = '/Volumes/scratch/data/SDSS/fields/'
#object_path = '/Volumes/scratch/data/SDSS/gzobjects/' 
location_format = 'imaging/%(run)i/%(rerun)i/corr/%(camcol)i/fpC-%(run)06i-%(band)s%(camcol)i-%(field)04i.fit.gz'

pixscale = 0.396127  # arcsec/pixel

nskyiter = 3
skyconv = 0.01

pgend()

def selection():
    s = N.zeros(len(data), N.bool)
    s[:10000:100] = True
    #run = data.field('run')
    #s = s & (run > 1000) & (run < 5000)
    return s

def bands():
    return ['g', 'r', 'i']

def cut_out_objects(clobber=False):    
    dsel = data[selection()]
    #dsel = data
    print '%i objects'%len(dsel)
    print '%i bands'%len(bands())
    fieldspec = []
    for band in bands():
        fieldspec = []
        for d in dsel:
                fieldspec_info = {'run': d.field('run'),
                                  'rerun': d.field('rerun'),
                                  'camcol': d.field('camcol'),
                                  'band': band,
                                  'field': d.field('field')}
                fieldspec.append(location_format%fieldspec_info)
        fieldspec = N.array(fieldspec)
        fieldspecuniq = N.unique(fieldspec)
        unretrieved_fields = 0
        unretrieved_objects = 0
        for fieldid in fieldspecuniq:
            print 'Field:', fieldid
            select = fieldspec == fieldid
            nobj = select.astype(N.int).sum()
            field = None
            print '%i objects in field'%nobj
            for d in dsel[select]:
                objid = d.field('objID')
                size = int(d.field('petroR90_r') * 4.0 / pixscale)
                print 'Object:', objid
                f = object_path+'%s%s.fits'%(objid,band)
                if clobber or not os.path.exists(f):
                    if field is None:
                        field, fieldheader = get_field(fieldid)
                        fieldheader = fieldheader
                        if field is None:
                            print 'Could not retrieve field'
                            unretrieved_fields += 1
                            unretrieved_objects += nobj
                            continue
                    halfsize = size/2
                    rowc = d.field('rowc_%s'%band)
                    colc = d.field('colc_%s'%band)
                    section = get_section(field, rowc, colc, halfsize)
                    hdu = pyfits.PrimaryHDU(section, fieldheader)
                    hdu.writeto(f, clobber=clobber, output_verify='fix')
                else:
                    print 'Object file already present - not overwriting'
            #remove_field(fieldid, band)
    print '%i objects in %i fields could not be retrieved'%(unretrieved_objects,
                                                          unretrieved_fields)

def get_section(image, rowc, colc, halfsize,
                blank=-1.0):
    rowc = int(round(rowc))
    colc = int(round(colc))
    size = 2*halfsize
    rowmin = rowc-halfsize
    rowmax = rowc+halfsize
    colmin = colc-halfsize
    colmax = colc+halfsize
    secrowmin = 0
    secrowmax = size                
    if rowmin < 1:
        secrowmin = -rowmin
        rowmin = 0
    if rowmax > image.shape[0]:
        secrowmax = size+image.shape[0]-rowmax
        rowmax = image.shape[0]
    seccolmin = 0
    seccolmax = size                
    if colmin < 1:
        seccolmin = -colmin
        colmin = 0
    if colmax > image.shape[1]:
        seccolmax = size+image.shape[1]-colmax
        colmax = image.shape[1]
    section = N.zeros((size, size), N.float) + blank
    section[secrowmin:secrowmax, seccolmin:seccolmax] = image[rowmin:rowmax, colmin:colmax]
    return section

def get_field(field_location):
    field_filename = os.path.join(field_path, field_location)
    if os.path.exists(field_filename):
        hdu = pyfits.open(field_filename)
        hdu.verify('fix')
        field = hdu[0].data
        fieldheader = hdu[0].header
        hdu.close()
        keys = [i for i,j in fieldheader.items()]
        if 'SOFTBIAS' in keys:
            softbias = fieldheader['SOFTBIAS']
        else:
            softbias = 1000.0
        field -= softbias
        if 'SKY' in keys:
            sky = fieldheader['SKY']
        else:
            print 'No sky in header'
            sky = median(field.ravel())
            oldsky = sky
            for i in range(nskyiter):
                sky = median(field[field < sky + 3*N.sqrt(sky)].ravel())
                if (oldsky - sky)/sky < skyconv:
                    break
                print "Sky estimate didn't converge to %.2f percent"%(skyconv*100)
        field -= sky
    else:
        field = fieldheader = None
    return field, fieldheader

def make_imaging_wget_list():
    dsel = data[selection()]
    print '%i objects'%len(dsel)
    included = []
    for d in dsel:
        for band in bands():
            location_info = {'run': d.field('run'),
                             'rerun': d.field('rerun'),
                             'camcol': d.field('camcol'),
                             'band': band,
                             'field': d.field('field')}
            location = location_format%location_info
            included.append(location)
#         ls = location.split('/')
#         n = len(ls)
#         for i in range(1, n):
#             l = string.join(ls[:i], '/')
#             if l not in included:
#                 included.append(l)
    included.sort()
    filename='/tmp/sdss.list'
    f = open(filename, 'w')
    for i in included:
        f.write('%s\n'%i)
    f.close()
    print 'Execute commands:'
    print 'export http_proxy="http://wwwcache.nottingham.ac.uk:3128"'
    print 'wget -c -P %s -B http://das.sdss.org/ -i %s'%(field_path, filename)
    #print 'Execute command:'
    #print 'rsync -vtrLPR rsync://user@rsync.sdss.org/imaging %s --include-from=%s'%(field_path, filename)
    #print "The password is 'sdss'"


def get_jpeg_url(objid, openinbrowser=False, imgsize=424, scale=1.0):
    urlformat = 'http://skyservice.pha.jhu.edu/dr6/ImgCutout/getjpeg.aspx?ra=%(ra).6f&dec=%(dec).6f&scale=%(scale).6f&width=%(imgsize)i&height=%(imgsize)i'
    select = N.where(data.field('objid') == objid)[0]
    if len(select) < 1:
        #print 'Warning: objid=%s not found!'%(str(objid))
        return ''
    elif len(select) > 1:
        print 'Warning: multiple objects selected!'
        select = select[0]
    ra = data.field('ra')[select]
    dec = data.field('dec')[select]
    size = data.field('PETROR90_R')[select]
    info = {'ra':ra, 'dec':dec, 'scale':size * 0.02 * scale, 'imgsize':imgsize}
    url = urlformat%info
    if openinbrowser:
        webbrowser.open(url)
#   size = data.field('PETROR50_R')[select]
#     info = {'ra':ra, 'dec':dec, 'scale':pixscale * size * 0.15}
#     url = urlformat%info
#     if openinbrowser:
#         webbrowser.open(url)
    return url
