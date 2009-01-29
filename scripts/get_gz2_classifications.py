import pyfits

filename = '/Users/spb/Work/projects/GalaxyZoo2/data/ClassificationGZ2.fits'
#filename = '/Users/spb/Work/projects/GalaxyZoo2/data/ClassificationGZ2_sample100.fits'
#filename = '/Users/spb/Work/projects/GalaxyZoo2/data/ClassificationGZ2_sample20.fits'

classifications = pyfits.getdata(filename, 'CLASSIFICATIONS')
qanda = pyfits.getdata(filename, 'QANDA')
