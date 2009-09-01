import urllib
import os.path
import numpy as N
#from ppgplot_spb import *
import time
from scipy import median
from scipy.ndimage import median_filter
import string
import gc
import webbrowser
from glob import glob
import subprocess

from get_gz2_data import *
data = gz2data_dr7
#parents = gz2data_dr7_parents

#field_path = '/Volumes/Storage/data/SDSS/fields/'
#object_path = '/Volumes/Storage/data/SDSS/gzobjects/' 
field_path = '/home/ppzsb1/SDSSdata/fields/'
mask_path = '/home/ppzsb1/SDSSdata/masks/'
object_path = '/home/ppzsb1/SDSSdata/gzobjects/'
fieldid_format = '%(run)06i-%(band)s%(camcol)i-%(field)04i'
fpC_file_format = 'fpC-%s.fit.gz'
fpM_file_format = 'fpM-%s.fit'
fpA_file_format = 'fpAtlas-%(run)06i-%(camcol)i-%(field)04i.fit'
drObj_file_format = 'drObj-%(run)06i-%(camcol)i-%(rerun)i-%(field)04i.fit'
mask_file_format = 'obj-%s.fit'
fpC_format = 'imaging/%(run)i/%(rerun)i/corr/%(camcol)i/fpC-%(run)06i-%(band)s%(camcol)i-%(field)04i.fit.gz'
fpM_format = 'imaging/%(run)i/%(rerun)i/objcs/%(camcol)i/fpM-%(run)06i-%(band)s%(camcol)i-%(field)04i.fit'
fpA_format = 'imaging/%(run)i/%(rerun)i/objcs/%(camcol)i/fpAtlas-%(run)06i-%(camcol)i-%(field)04i.fit'
drObj_format = 'imaging/%(run)i/%(rerun)i/dr/%(camcol)i/drObj-%(run)06i-%(camcol)i-%(rerun)i-%(field)04i.fit'

band_index = {'u':0,'g':1,'r':2,'i':3,'z':4}

pixscale = 0.396127  # arcsec/pixel

nskyiter = 3
skyconv = 0.01

#pgend()

def selection():
    s = N.zeros(len(data), N.bool)
    s[:10000:100] = True
    #run = data.field('run')
    #s = s & (run > 1000) & (run < 5000)
    return s

def bands():
    return ['r']
    #return ['g', 'r', 'i']

def cut_out_objects(clobber=False, getmask=True, getatlas=True, getparent=True):    
    dsel = data[selection()]
    pid = parents.field('objid')
    pobj = parents.field('obj')
    #dsel = data
    log = file('../cut_out_objects.log', 'w', buffering=1)
    log.write('%i objects'%len(dsel)+'\n')
    log.write('%i bands'%len(bands())+'\n')
    fieldspec = []
    for band in bands():
        fieldspec = []
        for d in dsel:
                fieldspec_info = {'run': d.field('run'),
                                  'rerun': d.field('rerun'),
                                  'camcol': d.field('camcol'),
                                  'band': band,
                                  'field': d.field('field')}
                fieldspec.append(fieldid_format%fieldspec_info)
        fieldspec = N.array(fieldspec)
        fieldspecuniq = N.unique(fieldspec)
        unretrieved_fields = 0
        unretrieved_objects = 0
        for fieldid in fieldspecuniq:
            log.write('### Field: '+fieldid+'\n')
            select = fieldspec == fieldid
            nobj = len(select.nonzero()[0])
            field = None
            mask = None
            log.write('%i objects in field'%nobj+'\n')
            for d in dsel[select]:
                objid = d.field('objID')
                size = int(d.field('petroR90_r') * 6.0 / pixscale)
                log.write('*** Object: '+str(objid)+'\n')
                rowc = d.field('rowc_%s'%band)
                colc = d.field('colc_%s'%band)
                obj = d.field('obj')
                parentidx = (pid==objid).nonzero()[0]
                if len(parentidx) > 0:
                    parentobj = pobj[parentidx]
                else:
                    parentobj = None
                fpAid = {'run':d.field('run'), 'camcol':d.field('camcol'),
                         'field':d.field('field')}
                log.write('rowc: %.2f  colc: %.2f  obj: %i'%(rowc, colc, obj)+'\n')
                f = object_path+'%s%s.fits'%(objid,band)
                fm = object_path+'%s%sm.fits'%(objid,band)
                fa = object_path+'%s%sa.fits'%(objid,band)
                fp = object_path+'%s%sp.fits'%(objid,band)
                if clobber or not os.path.exists(f):
                    if field is None:
                        if getmask:
                            field, fieldheader, mask = get_field(fieldid,
                                                                 getmask=True)
                        else:
                            field, fieldheader = get_field(fieldid, getmask=False)
                        if field is None:
                            log.write('Could not retrieve field'+'\n')
                            unretrieved_fields += 1
                            unretrieved_objects += nobj
                            continue
                        if getmask and mask is None:
                            log.write('Could not retrieve mask'+'\n')
                            unretrieved_fields += 1
                            unretrieved_objects += nobj
                            continue
                    halfsize = size/2
                    section, sectionheader = get_section(field, rowc, colc,
                                                         halfsize, fieldheader)
                    hdu = pyfits.PrimaryHDU(section, sectionheader)
                    hdu.writeto(f, clobber=clobber, output_verify='fix')
                    if getmask:
                        mask = get_section(mask, rowc, colc, halfsize,
                                           maskfill=True)
                        hdu = pyfits.PrimaryHDU(mask)
                        hdu.writeto(fm, clobber=clobber, output_verify='fix')
                    if getatlas:
                        if os.path.exists(fa) and clobber:
                            os.remove(fa)
                        if not os.path.exists(fa):
                            fpA = os.path.join(field_path, fpA_file_format%fpAid)
                            bi = band_index[band]
                            status = subprocess.Popen('read_atlas_image -c %i %s %i %s'%(bi, fpA, obj, fa), shell=True).communicate()
                            print status
                            if status != '':
                                'Error reading object atlas image'
                    if getparent:
                        if os.path.exists(fp) and clobber:
                            os.remove(fp)
                        if not os.path.exists(fp):
                            if parentobj is not None:
                                fpA = os.path.join(field_path, fpA_file_format%fpAid)
                                bi = band_index[band]
                                status = subprocess.Popen('read_atlas_image -c %i %s %i %s'%(bi, fpA, parentobj, fp), shell=True).communicate()
                                print status
                                if status != '':
                                    'Error reading parent atlas image'
                            else:
                                os.system('ln -s %s %s'%(fa, fp))
                else:
                    log.write('Object file already present - not overwriting'+'\n')
            #remove_field(fieldid, band)
    log.write('%i objects in %i fields could not be retrieved'%(unretrieved_objects,
                                                unretrieved_fields)+'\n')

def get_section(image, rowc, colc, halfsize, header=None,
                maskfill=False, blank=-1.0):
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
    if maskfill:
        section = N.where(floodfill(section, [halfsize, halfsize],
                                    section[halfsize, halfsize], 99) == 99, 1, 0)
    if header is not None:
        section_header = header.copy()
        section_header['CRPIX1'] += seccolmin - colmin
        section_header['CRPIX2'] += secrowmin - rowmin
        return section, section_header
    else:
        return section

def get_field(fieldid, subsky=False, getmask=True):
    field_filename = os.path.join(field_path, fpC_file_format%fieldid)
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
        if subsky:
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
        if getmask:
            mask_filename = os.path.join(mask_path, mask_file_format%fieldid)
            if os.path.exists(mask_filename):
                hdu = pyfits.open(mask_filename)
                hdu.verify('fix')
                mask = hdu[0].data
                hdu.close()
            else:
                mask = None
    else:
        field = fieldheader = mask = None
    if getmask:
        return field, fieldheader, mask
    else:
        return field, fieldheader

def convert_masks(clobber=False):
    finlist = glob(os.path.join(field_path, fpM_file_format%'*'))
    for fin in finlist:
        fout = fin.replace(field_path, mask_path)
        fout = fout.replace('fpM', 'obj')
        if os.path.exists(fout) and clobber:
            os.remove(fout)
        if not os.path.exists(fout):
            os.system('read_mask %s 0 %s'%(fin, fout))


def make_imaging_wget_list(getmask=True, getatlas=True, getcat=False):
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
            location = fpC_format%location_info
            included.append(location)
            if getmask:
                location = fpM_format%location_info
                included.append(location)
            if getatlas:
                location = fpA_format%location_info
                included.append(location)
            if getcat:
                location = drObj_format%location_info
                included.append(location)
#         ls = location.split('/')
#         n = len(ls)
#         for i in range(1, n):
#             l = string.join(ls[:i], '/')
#             if l not in included:
#                 included.append(l)
    included = N.unique(included)
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


def get_lesson_images(rmin=10.0, rmax=25.0, magmax=14, n=400, browser=False):
    selection = data.field('petroR90_r') > rmin
    selection &= data.field('petroR90_r') < rmax
    selection &= data.field('petroMag_r') < magmax
    selection = selection.nonzero()[0]
    count = len(selection)
    print count
    skip = count/n 
    selection = selection[::skip]
    selection = selection[:n]
    print len(selection)
    objids = data.field('objid')[selection]
    urls = get_jpeg_url(objids, openinbrowser=browser,
                        imgsize=600, ratio=1.5, scale=0.6)
    page = "<html><body>\n"
    for u in urls:
        page += '<a href="%s" target="_blank"><img style="margin:10px" src="%s" width="450px" height="300px"/></a>\n'%(u, u)
    page += "</html></body>"
    f = file('../lesson/images.html', 'w')
    f.write(page)
    f.close()
    f = file('../lesson/images_list', 'w')
    for i, u in enumerate(urls):
        o = objids[i]
        text = '%s %s\n'%(o, u)
        f.write(text)
    f.close()

def get_jpeg_url(objid, openinbrowser=False, imgsize=424, ratio=1, scale=1.0, adaptscale=False):
    urlformat = 'http://casjobs.sdss.org/ImgCutoutDR7/getjpeg.aspx?ra=%(ra).6f&dec=%(dec).6f&scale=%(scale).6f&width=%(imgsizex)i&height=%(imgsizey)i'
    imgsizex = imgsizey = imgsize
    if ratio != 1:
        imgsizex = imgsize*ratio
    sortidx = data.field('objid').argsort()
    n = len(sortidx)
    select = N.searchsorted(data.field('objid')[sortidx], objid)
    select = sortidx[select]
    bad = select >= n
    N.putmask(select, bad, 0)
    if n < 1:
        print 'Warning: no objids found!'%(str(objid))
        return ''
    ra = data.field('ra')[select]
    dec = data.field('dec')[select]
    size = data.field('PETROR90_R')[select]
    urls = []
    for i in range(len(objid)):
        if bad[i]:
            urls.append('')
        else:
            if adaptscale:
                imgscale = size[i] * 0.02 * scale
            else:
                imgscale = scale * pixscale
            info = {'ra':ra[i], 'dec':dec[i], 'scale':imgscale,
                    'imgsizex':imgsizex, 'imgsizey':imgsizey}
            url = urlformat%info
            if openinbrowser:
                webbrowser.open(url)
            urls.append(url)
    if n == 1:
        return urls[0]
    else:
        return urls


def floodfill(image, node, target, replacement):
    if image[node[0], node[1]] != target:  return
    im = N.array(image, N.int)
    Q = [node]
    while len(Q) > 0:
        n = Q.pop(0)
        if im[n[0], n[1]] == target:
            w = e = n[1]
            while (w != 0) and (im[n[0], w] == target):  w = w-1
            while (e != image.shape[1]-1) and (im[n[0], e] == target):  e = e+1
            im[n[0], w+1:e] = replacement
            for m in range(w+1, e):
                if (n[0] != image.shape[0]-1) and (im[n[0]+1, m] == target):
                    Q.append([n[0]+1, m])
                if (n[0] != 0) and (im[n[0]-1, m] == target):
                    Q.append([n[0]-1, m])
    return im
