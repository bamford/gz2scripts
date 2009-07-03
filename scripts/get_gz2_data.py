import pyfits
import os.path
import numpy as N
from combine_fits_tables import combine_fits_tables

gz2data_path = '/home/ppzsb1/Projects/GalaxyZoo2/'

#gz2sample_file_dr6 = 'dr6/gz2sample_final1_abs_regions_counts_wvt.fits'
#gz2data_dr6 = pyfits.getdata(gz2data_path+gz2sample_file_dr6)

gz2sample_file_dr7 = 'gz2sample_final_abs_regions_counts_wvt.fits'
gz2data_dr7 = pyfits.getdata(gz2data_path+gz2sample_file_dr7)

gz2sample_file_dr7_parents = 'gz2sample_parents.fits'
gz2data_dr7_parents = pyfits.getdata(gz2data_path+gz2sample_file_dr7_parents)

#gz2extra_file = 'gz2sample_finalextra.fits'
#gz2extra = pyfits.getdata(gz2data_path+gz2extra_file)

# combinedtablenames = [gz2sample_file, gz2extra_file]
# gz2data_file = 'gz2sample_final_combined.fits'
# update = False
# if os.path.isfile(gz2data_path+gz2data_file):
#     tdata = os.path.getmtime(gz2data_path+gz2data_file)
#     tdependencies = tdata - 1
#     for tab in combinedtablenames:
#         t = os.path.getmtime(gz2data_path+tab)
#         tdependencies = max(t, tdependencies)
#     update = tdependencies > tdata
#     if update:
#         print 'Combined data file older than dependencies.  Recreating.'
# else:
#     print 'No combined data file.  Creating.'
#     update = True

# def combine_tables():
#     tables = []
#     for tab in combinedtablenames:
#         tables.append(pyfits.open(gz2data_path+tab))
#     combine_fits_tables(tables, gz2data_path+gz2data_file)

# if update:
#     combine_tables()

#gz2data = pyfits.getdata(gz2data_path+gz2data_file)    
