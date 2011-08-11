#! /usr/bin/env python

import get_sdss_images
import pyfits

datafilename = 'gz2and1master.fits'
data = pyfits.getdata(datafilename, 1)

def selection():
    s = data.field('arms_clean_union')
    return s

def make_gz2_wget_list():
    get_sdss_images.make_imaging_wget_list(data[selection()], bands=['r'],
                                           getmask=True, getatlas=True, getcat=False)

def get_gz2_images():
    get_sdss_images.cut_out_objects(data[selection()],
                                    parents=None, bands=['r'], clobber=False,
                                    getmask=True, getatlas=True, getparent=True,
                                    getclean=True, sizescale=10)

if __name__ == "__main__":
    get_gz2_images()
