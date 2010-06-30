import time
import numpy
import cProfile as profile
import random
import pylab
from math import floor
pylab.close()

def wars_sort_swap(galaxies, winners, losers, niter=32, damped=True, progressive_damping=True, dfactor=7.0):
    ngal = len(galaxies)
    nwars = len(winners)
    sorted = numpy.random.permutation(galaxies)
    for i in range(niter):
        previous = sorted.copy()
        nswap = 0
        if progressive_damping:
            d = dfactor*i
        else:
            d = dfactor
        for battle in numpy.random.permutation(nwars):
            w = winners[battle]
            l = losers[battle]
            iw = (sorted == w).nonzero()[0][0]
            il = (sorted == l).nonzero()[0][0]
            if iw < il:
                if damped:                    
                    damp = int(floor((il - iw) * (1-1.0/(d+1))))
                    ild = il - max(damp - 1, 0)
                    iwd = iw + damp
                    sorted[ild+1:il+1] = sorted[ild:il]
                    sorted[ild] = w
                    sorted[iw:iwd] = sorted[iw+1:iwd+1]
                    sorted[iwd] = l
                else:
                    sorted[il] = w
                    sorted[iw] = l
                nswap += 1
        nchanged = len((previous != sorted).nonzero()[0])        
        #print 'niter = %4i:  nswap = %4i,  nchanged = %4i'%(i, nswap, nchanged)
        if len(numpy.unique(sorted)) != len(sorted):
            print 'NOT UNIQUE!'
    return sorted


def wars_sort_test(fn, wrong=0.0, ntime=5, niter=1, damped=False, progressive_damping=True, dfactor=3.0):
    awin = (a >= b)
    awin = numpy.where(r > wrong, awin, numpy.logical_not(awin))
    winners = numpy.where(awin, a, b)
    losers = numpy.where(awin, b, a)
    correct = numpy.sort(galaxies)
    times = numpy.zeros(ntime, numpy.float)
    mads = numpy.zeros(ntime, numpy.float)
    bias = numpy.zeros(ntime, numpy.float)
    numpy.random.seed(54321)
    for i in range(ntime):
        start = time.clock()
        result = fn(galaxies, winners, losers, niter=niter, damped=damped,
                    progressive_damping=progressive_damping, dfactor=dfactor)
        stop = time.clock()
        times[i] = stop - start
        mads[i] = numpy.absolute(result - correct).mean() / ngal * 100
        bias[i] = ((numpy.median(result[:ngal//2] - correct[:ngal//2]) - 
                    numpy.median(result[ngal//2:] - correct[ngal//2:])) / ngal * 100)
    t = numpy.median(times)
    m = numpy.median(mads)
    s = numpy.median(bias)
    #print 'MAD = %5.2f'%m
    #print 'time = %5.2f'%t
    #pylab.plot(correct, result, '.')
    #pylab.plot([0.0, ngal], [0.0, ngal], '-')
    return m, s, t

wars_sorts = (wars_sort_swap,)

if __name__ == '__main__':
    numpy.random.seed(12345)
    ngal=200
    nwars=2000
    galaxies = numpy.random.permutation(ngal)
    a = galaxies[numpy.random.randint(ngal, size=nwars)]
    b = galaxies[numpy.random.randint(ngal, size=nwars)]
    r = numpy.random.uniform(size=nwars)
    for fn in wars_sorts:
        print fn.__name__
        print '%5s %5s %8s %11s %8s %5s %5s %5s'%('wrong', 'niter', 'damped', 'progressive', 'dfactor', 'mad%', 'bias%', 'time')
        for wrong in (0.02, 0.04, 0.08):
            for niter in (32, 64):
                for damped in (True,):
                    for progressive in (True,):
                        if (not damped) and progressive: continue
                        for dfactor in numpy.arange(0.5, 10.1, 0.5):
                            m, s, t = wars_sort_test(fn, wrong=wrong, niter=niter, damped=damped,
                                                     progressive_damping=progressive, dfactor=dfactor)
                            print '%5.2f %5i %8s %11s %8.2f %5.1f %5.2f %5.2f'%(wrong, niter, damped, progressive, dfactor, m, s, t)
    

def do_wars_sort():
    winners = []
    losers = []
    battle_bins = []
    for l in file('../data/final/wars_battles.csv'):
        ls = l.split(',')
        winners.append(ls[4])
        losers.append(ls[5])
        battle_bins.append(ls[-1])
    winners = numpy.asarray(winners)
    losers = numpy.asarray(losers)
    battle_bins = numpy.asarray(battle_bins)
    battles = numpy.unique(battle_bins)
    for b in battles:
        select = battle_bins == b
        w = winners[select]
        l = losers[select]
        galaxies = numpy.concatenate((w, l))
        galaxies = numpy.unique(galaxies)
        result = wars_sort_swap(galaxies, w, l, niter=8, damped=True,
                                progressive_damping=True, dfactor=5.0)
        
