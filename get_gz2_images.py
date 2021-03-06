#! /usr/bin/env python

import get_sdss_images
import pyfits

datafilename = 'gz2and1master.fits'
data = pyfits.getdata(datafilename, 1)

def selection(start=0, end=None):
    # get objects to retrieve
    flagged = data.field('arms_clean_union').nonzero()[0]
    idx = data.field('objid')[flagged].argsort()
    sel = flagged[idx]
    n = len(sel)
    print('Selected %i objects in total'%n)
    if (end is None):
        end = n
    sel = sel[start:end]
    print('Restricted selection to %i objects'%len(sel))
    return sel

def make_gz2_wget_list(start=0, end=None):
    get_sdss_images.make_imaging_wget_list(data[selection(start, end)],
                                           bands=['u', 'g', 'r', 'i', 'z'],
                                           getmask=True, getatlas=True, getcat=False)

def get_gz2_images(start=0, end=None):
    get_sdss_images.cut_out_objects(data[selection(start, end)],
                                    parents=None, bands=['u', 'g', 'r', 'i', 'z'], clobber=False,
                                    getmask=True, getatlas=True, getparent=True,
                                    getclean=True, sizescale=10)
