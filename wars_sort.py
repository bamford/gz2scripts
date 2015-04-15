#! /usr/bin/env python

import time
import numpy as np
import cProfile as profile
import random
import pylab
from math import floor
pylab.close()

def wars_sort_swap(galaxies, winners, losers, maxniter=32, damped=True, progressive_damping=True, dfactor=1.0):
    ngal = len(galaxies)
    nwars = len(winners)
    sorted = np.random.permutation(galaxies)
    for i in range(maxniter):
        previous = sorted.copy()
        nswap = 0
        if progressive_damping:
            d = dfactor*i
        else:
            d = dfactor
        for battle in np.random.permutation(nwars):
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
        if nchanged == 0:
            break
        #print 'niter = %4i:  nswap = %4i,  nchanged = %4i'%(i, nswap, nchanged)
        if len(np.unique(sorted)) != len(sorted):
            print 'NOT UNIQUE!'
    #print 'niter = %4i:  nswap = %4i,  nchanged = %4i'%(i, nswap, nchanged)
    return sorted, i


def wars_sort_test(fn, wrong=0.0, ntime=3, maxniter=32, damped=False, progressive_damping=True,
                   dfactor=3.0, plots=False):
    awin = (a >= b)
    awin = np.where(r > wrong, awin, np.logical_not(awin))
    winners = np.where(awin, a, b)
    losers = np.where(awin, b, a)
    correct = np.sort(galaxies)
    times = np.zeros(ntime, np.float)
    mads = np.zeros(ntime, np.float)
    bias = np.zeros(ntime, np.float)
    niters = np.zeros(ntime, np.float)
    np.random.seed(54321)
    for i in range(ntime):
        start = time.clock()
        result, n = fn(galaxies, winners, losers, maxniter=maxniter, damped=damped,
                       progressive_damping=progressive_damping, dfactor=dfactor)
        stop = time.clock()
        times[i] = stop - start
        mads[i] = np.absolute(result - correct).mean() / ngal * 100
        bias[i] = ((np.median(result[:ngal//2] - correct[:ngal//2]) - 
                    np.median(result[ngal//2:] - correct[ngal//2:])) / ngal * 100)
        niters[i] = n
    t = np.median(times)
    m = np.median(mads)
    s = np.median(bias)
    n = np.median(niters)
    #print 'MAD = %5.2f'%m
    #print 'time = %5.2f'%t
    if plots:
        pylab.figure()
        pylab.plot(correct, galaxies, 'r.')
        pylab.plot(correct, result, 'g.')
        pylab.plot([0.0, ngal], [0.0, ngal], '-')
    return m, s, t, n

def do_test():
    wars_sorts = (wars_sort_swap,)
    global ngal, nwars, galaxies, a, b, r
    np.random.seed()
    ngal=200
    nwars=2000
    galaxies = np.random.permutation(ngal)
    a = galaxies[np.random.randint(ngal, size=nwars)]
    b = galaxies[np.random.randint(ngal, size=nwars)]
    r = np.random.uniform(size=nwars)
    results = []
    for fn in wars_sorts:
        print fn.__name__
        print '%5s %8s %8s %11s %8s %5s %5s %5s %5s'%('wrong', 'maxniter', 'damped', 'progressive', 'dfactor', 'mad%', 'bias%', 'time', 'niter')
        for wrong in (0.05,):# 0.10, 0.20):
            for maxniter in (32,):# 64, 128):
                for progressive in (False, True):
                    for dfactor in (0.0, 0.5, 1.0, 2.0, 4.0):
                        if (dfactor < 0.000001) and progressive: continue
                        damped = dfactor > 0.000001
                        if not progressive:
                            dfactor *= maxniter//2
                        m, s, t, n = wars_sort_test(fn, wrong=wrong, maxniter=maxniter, damped=damped,
                                                 progressive_damping=progressive, dfactor=dfactor, plots=True)
                        print '%5.2f %8i %8s %11s %8.2f %5.2f %5.2f %5.2f %5i'%(wrong, maxniter, damped, progressive, dfactor, m, s, t, n)
                        pylab.savefig('wars_test_%5.2f_%8i_%8s_%11s_%8.2f.pdf'%(wrong, maxniter, damped, progressive, dfactor))
                        pylab.close('all')
                        results.append([wrong, maxniter, damped, progressive, dfactor, m, s, t, n])
    #plot_test_results(np.array(results))
    results = np.rec.array(results, names=('wrong', 'maxniter', 'damped', 'progressive',
                                          'dfactor', 'mad%', 'bias%', 'time', 'niter'))
    return results

def plot_test_results():
    pass

def do_wars_sort():
    winners = []
    losers = []
    battle_bins = []
    for l in file('../data/final/wars_battles.csv'):
        ls = l.split(',')
        winners.append(ls[4])
        losers.append(ls[5])
        battle_bins.append(ls[-1])
    winners = np.asarray(winners)
    losers = np.asarray(losers)
    battle_bins = np.asarray(battle_bins)
    battles = np.unique(battle_bins)
    for b in battles:
        select = battle_bins == b
        w = winners[select]
        l = losers[select]
        galaxies = np.concatenate((w, l))
        galaxies = np.unique(galaxies)
        result = wars_sort_swap(galaxies, w, l, niter=8, damped=True,
                                progressive_damping=True, dfactor=5.0)
        

def plot_dfactor(niter, dfactor):
    i = np.arange(niter)
    dampi = 1-1.0/(dfactor*i+1)
    pylab.plot(i, dampi)
    pylab.show()

if __name__ == '__main__':
    do_test()

