#! /usr/bin/env python

import get_sdss_images
import pyfits

from get_gz2_data import *
data = gz2data_dr7
parents = gz2data_dr7_parents

def selection():
    s = N.zeros(len(data), N.bool)
    s[:10000:100] = True
    #run = data.field('run')
    #s = s & (run > 1000) & (run < 5000)
    return s

def make_gz2_wget_list():
    get_sdss_images.make_imaging_wget_list(dsel, bands=['r'], getmask=True, getatlas=True, getcat=False)

def get_gz2_images():
    get_sdss_images.cut_out_objects(data[selection()], parents=parents, bands=['r'], clobber=False,
                    getmask=True, getatlas=True, getparent=True,
                    getclean=False, sizescale=6)

if __name__ == "__main__":
    get_gz2_images()
