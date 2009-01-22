import pyfits

filename = '/Users/spb/Work/projects/GalaxyZoo2/data/ClassificationGZ2.fits'

classifications = pyfits.getdata(filename, 'CLASSIFICATIONS')
qanda = pyfits.getdata(filename, 'QANDA')
