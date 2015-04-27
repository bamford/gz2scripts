#! /usr/bin/env python

import time
import numpy as np

from wars_sort import WarsSort

class WarsSortTest:

    def __init__(self, wrong=0.0, ntime=3, maxniter=32, progressive=True,
                 damping_factor=3.0, ngal=200, nwars=2000,
                 progress_figure=False, plots=False):
        self.wrong = wrong
        self.ntime = ntime
        self.maxniter = maxniter
        self.progressive = progressive
        self.damping_factor = damping_factor
        self.ngal = ngal
        self.nwars = nwars
        self.progress_figure = progress_figure
        self.plots = plots
        self.setup()

    def test(self):
        times, mads, bias, niters = np.zeros((4, self.ntime), np.float)
        np.random.seed(89345)
        
        for i in range(self.ntime):
            wars_sort = WarsSort(self.galaxies, self.winners, self.losers,
                                 maxniter=self.maxniter,
                                 progressive=self.progressive,
                                 damping_factor=self.damping_factor,
                                 truth=self.truth,
                                 progress_figure=self.progress_figure)
            start = time.clock()
            result = wars_sort.iterate()
            stop = time.clock()
            times[i] = stop - start
            mads[i] = np.mean(wars_sort.madlist[-self.maxniter//2:])
            bias[i] = np.mean(wars_sort.biaslist[-self.maxniter//2:])
            niters[i] = wars_sort.niter
        t, m, b, n = map(np.median, (times, mads, bias, niters))
        if self.plots:
            figname = 'wars_test_%.2f_%i_%s_%.2f.pdf'%(self.wrong,
                                    self.maxniter, self.progressive,
                                    self.damping_factor)
            wars_sort.save_progress_figure(figname)
        wars_sort.close()
        return t, m, b, n

    def setup(self):
        np.random.seed(1237891364)
        self.galaxies = np.random.permutation(self.ngal)
        a = self.galaxies[np.random.randint(self.ngal, size=self.nwars)]
        b = self.galaxies[np.random.randint(self.ngal, size=self.nwars)]
        r = np.random.uniform(size=self.nwars)
        awin = (a >= b)
        awin = np.where(r > self.wrong, awin, np.logical_not(awin))
        self.winners = np.where(awin, a, b)
        self.losers = np.where(awin, b, a)
        self.truth = np.sort(self.galaxies)

    def do_test(self, wrong=(0.05, 0.1, 0.15, 0.2, 0.25, 0.3), maxniter=(16,), progressive=(True,),
                damping_factor=(0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8)):
        results = []
        print '%5s %8s %11s %8s %5s %5s %5s %5s'%('wrong', 'maxniter', 'progressive',
                                                  'dfactor', 'mad%', 'bias%', 'time', 'niter')        
        for self.wrong in wrong:
            self.setup()
            for self.maxniter in maxniter:
                for self.progressive in progressive:
                    for self.damping_factor in damping_factor:
                        #if (self.damping_factor == 0) and self.progressive: continue
                        t, m, b, n = self.test()
                        print '%5.2f %8s %11s %8.2f %5.2f %5.2f %5.2f %5i'%(self.wrong, self.maxniter,
                                            self.progressive, self.damping_factor, m, b, t, n)
                        results.append([self.wrong, self.maxniter, self.progressive, self.damping_factor, m, b, t, n])
        #plot_test_results(np.array(results))
        results = np.rec.array(results, names=('wrong', 'maxniter', 'progressive',
                                              'dfactor', 'mad%', 'bias%', 'time', 'niter'))
        return results

    
def plot_dfactor(niter, dfactor):
    i = np.arange(niter)
    dampi = 1-1.0/(dfactor*i+1)
    plt.plot(i, dampi)
    plt.show()

    
if __name__ == '__main__':
    wars_sort_test = WarsSortTest(ntime=5, progress_figure=False, plots=True)
    wars_sort_test.do_test()
