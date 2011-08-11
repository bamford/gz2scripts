from ppgplot_spb import *
import pyfits
import rostat

pgend()

dbug = pyfits.getdata('../gz2sample_final_dr7_legacy.fits')[::100]
dchildren = pyfits.getdata('../gz2sample_final_dr7_legacy_children.fits')[::100]

def check_children():
    pgopen('../plots/check_children.ps/cps')
    pgsetup(3)
    #print dbug.petroMag_r.min(), dbug.petroMag_r.max()
    #print dchildren.petroMag_r.min(), dchildren.petroMag_r.max()
    make_histo('petroMag_r', 10.0, 18.0)
    make_histo('petroR50_r', 0.0, 15.0)
    make_histo('petroMag_u - petroMag_r', 0.0, 6.0)
    pgclos()


def make_histo(q, low, high):
    print q
    if '-' in q:
        qs = q.split()
        dbugq = dbug.field(qs[0]) - dbug.field(qs[-1])
        dchildrenq = dchildren.field(qs[0]) - dchildren.field(qs[-1])
    else:
        dbugq = dbug.field(q)
        dchildrenq = dchildren.field(q)
    dfullq = N.concatenate((dbugq, dchildrenq))
    xb, yb = bin_array(dbugq, 40, low, high)
    yb /= len(dbugq[(dbugq>low) & (dbugq<=high)])
    xc, yc = bin_array(dchildrenq, 40, low, high)
    yc /= len(dchildrenq[(dchildrenq>low) & (dchildrenq<=high)])
    xf, yf = bin_array(dfullq, 40, low, high)
    yf /= len(dfullq[(dfullq>low) & (dfullq<=high)])
    ymax = max(yb.max(), yc.max())*1.05
    pgpage()
    pgsvp(0.125, 0.875, 0.175, 0.925) 
    pgswin(low, high, 0, ymax)
    pgbox('BCNTS', 0, 0, 'BNTS', 0, 0)
    pgmtxt('B', 2.5, 0.5, 0.5, q)
    pgmtxt('L', 2.5, 0.5, 0.5, 'norm. freq.')
    pgxsci('red')
    pgmtxt('T', 0.5, 0.25, 0.5, 'original')
    pgbin(xb, yb)
    pgxsci('blue')
    pgmtxt('T', 0.5, 0.85, 0.5, 'extra')
    pgbin(xc, yc)
    pgxsci('green')
    #pgmtxt('T', 0.5, 0.5, 0.5, 'full')
    #pgbin(xf, yf)
    d, prob, cumx, cumy = rostat.ks_test(dbugq, dchildrenq)
    pgswin(low, high, 0, 1)
    pgxsls('dotted')
    pgxsci('red')
    pgbin(cumx[0], cumx[1])    
    pgxsci('blue')
    pgbin(cumy[0], cumy[1])    
    pgxsls('solid')
    pgxsci('black')
    pgbox('', 0, 0, 'CMTS', 0, 0)
    pgmtxt('R', 2.5, 0.5, 0.5, 'cum. freq.')
    print 'KS prob.:', prob

