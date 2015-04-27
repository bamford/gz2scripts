import numpy as np
from math import floor
import time
from astropy.io import fits as pyfits
import os

# The damping procedure was been extensively tested, and the default parameters
# are those found to demonstrate most efficient convergence with realistic simulations

class WarsSort:
    def __init__(self, galaxies=None, winners=None, losers=None, maxniter=10,
                 progressive=True, damping_factor=1.0,
                 progress_figure=False, truth=None):

        self.galaxies = self._asarray(galaxies)
        self.winners = self._asarray(winners)
        self.losers = self._asarray(losers)
        self.maxniter = maxniter
        self.progressive = progressive
        self.initial_damping_factor = damping_factor
        self.damping_factor = damping_factor
        self.progress_figure = progress_figure
        self.truth = truth

        self._consistency_check()

        self._setup_internal_variables()
        
        if self.truth is not None:
            self._setup_progress_figure()

    def _asarray(self, x):
        return np.asarray(x) if (x is not None) else np.zeros(1)
            
    def _consistency_check(self):
        if self.winners.shape != self.losers.shape:
            raise ValueError("Winners and losers arrays are not"
                             "the same shape")

        if self.winners.ndim != 1:
            raise ValueError("Winners and losers arrays are not"
                             "the correct shape")

        if self.galaxies.ndim != 1:
            raise ValueError("Winners and losers arrays are not"
                             "the correct shape")

        if self.progress_figure and (self.truth is None):
            raise ValueError("To create progress figure you must"
                             "supply a 'truth' ranking")

        if not set(self.winners).issubset(self.galaxies):
            raise ValueError("Some winners are not in galaxies array")

        if not set(self.losers).issubset(self.galaxies):
            raise ValueError("Some losers are not in galaxies array")

    def _setup_internal_variables(self):
        self.ngal = self.galaxies.shape[0]
        self.nwars = self.winners.shape[0]
        self.niter = 0
        self.nbattle = 0
        self.nswap = 0
        self.ranking = np.random.permutation(self.galaxies)
        self.progress_figure_points = None
        self.progress_figure_previter_points = None
        self.progress_figure_label = None
        self.progress_figure_line = None
        self.progress_figure_fig = None
        self.mad = None
        self.madlist = []
        self.bias = None
        self.biaslist = []

    def _update_damping_factor(self):
        if self.progressive:
            #self.damping_factor = self.initial_damping_factor * self.niter
            self.damping_factor = 1 - np.exp(-(self.niter*self.initial_damping_factor))
        else:
            self.damping_factor = self.initial_damping_factor

    def _mad(self):
        return np.absolute(self.ranking - self.truth).mean() / self.ngal * 100

    def _bias(self):
        mid = self.ngal//2
        r = self.ranking
        t = self.truth
        return ((np.median(r[:mid] - t[:mid]) - np.median(r[mid:] - t[mid:]))
                / float(self.ngal) * 100)

    def _setup_progress_figure(self):
        global plt
        import matplotlib
        matplotlib.use('TkAgg')
        from matplotlib import pyplot as plt
        import matplotlib.gridspec as gridspec
        if self.progress_figure:
            plt.ion()
        if self.progress_figure_fig is None:
            self.progress_figure_fig = plt.figure(figsize=(8,12))
        else:
            self.progress_figure_fig.clear()
        gs = gridspec.GridSpec(4, 3)
        ax = plt.subplot(gs[:3, :], aspect=1.0)
        plt.xlabel('true rank')
        plt.ylabel('estimated rank')
        title = ''
        if self.initial_damping_factor > 0:
            title += 'damped'
            if self.progressive:
                title += ' progressive'
        plt.title(title)
        plt.plot([0.0, self.ngal], [0.0, self.ngal], 'k-')
        ax.scatter(self.truth, self.ranking, c='b', zorder=1, alpha=0.2)
        self.progress_figure_previter_points = ax.scatter([], [], c='r',
                                                          zorder=2, alpha=0.4)
        self.progress_figure_points = ax.scatter(self.truth, self.ranking, c='g',
                                                 zorder=3, alpha=0.8)
        self.progress_figure_label = ax.text(self.ngal*0.05, self.ngal*0.8,
                                    '%4i %5i %5i\n%5.2f %5.2f %5.2f'%(0, 0, 0, 0, 0, 0),
                                    backgroundcolor='w', fontsize='small')
        self.progress_figure_label.set_bbox(dict(alpha=0.5, color='w',
                                                 edgecolor='w'))
        color='red',
        plt.axis((0, self.ngal, 0, self.ngal))
        
        ax = plt.subplot(gs[3:, :])
        plt.axis((0, self.nwars*self.maxniter, 0, 30))
        plt.hlines([5,10,15,20,25], 0, self.nwars*self.maxniter, linestyles='dotted')
        plt.hlines(self.nwars*np.arange(1, self.maxniter), 0, 30, linestyles='dotted')
        plt.xlabel('battle number')
        plt.ylabel('scatter')
        self.progress_figure_line = ax.plot([0],[0])[0]
        plt.tight_layout()
        if self.progress_figure:
            plt.draw()

    def _update_progress_figure(self):
        if self.progress_figure_fig is None:
            self._setup_progress_figure()
        self.progress_figure_previter_points.set_offsets(
            np.transpose([self.truth, self.previous_ranking]))
        self.progress_figure_points.set_offsets(
            np.transpose([self.truth, self.ranking]))
        status = '%4i %5i %5i\n%5.2f %5.2f %5.2f'%(self.niter, self.nbattle,
                                self.nswap, self.damping_factor, self.mad, self.bias)
        self.progress_figure_label.set_text(status)
        x, y = self.progress_figure_line.get_data()
        x = np.concatenate((x, [self.nwars*self.niter + self.nbattle]))
        y = np.concatenate((y, [self.mad]))
        self.progress_figure_line.set_data(x, y)
        if self.progress_figure:
            plt.draw()

    def _update_progress(self):
        if self.truth is not None:
            self.mad = self._mad()
            self.bias = self._bias()
            self._update_progress_figure()
    
    def iteration(self):
        self._update_damping_factor()
        self.nbattle = 0
        self.nswap = 0
        self.previous_ranking = self.ranking.copy()
        for b, battle in enumerate(np.random.permutation(self.nwars)):
            self.nbattle += 1
            w = self.winners[battle]
            l = self.losers[battle]
            iw = (self.ranking == w).nonzero()[0][0]
            il = (self.ranking == l).nonzero()[0][0]
            if iw < il:
                if self.initial_damping_factor > 0:
                    damp = int(floor((il - iw) * self.damping_factor))
                    ild = il - max(damp, 0)
                    iwd = iw + damp
                    self.ranking[ild+1:il+1] = self.ranking[ild:il]
                    self.ranking[ild] = w
                    self.ranking[iw:iwd] = self.ranking[iw+1:iwd+1]
                    self.ranking[iwd] = l
                else:
                    self.ranking[il] = w
                    self.ranking[iw] = l
                self.nswap += 1
                self._update_progress()
        self.niter += 1
        self.madlist.append(self.mad)
        self.biaslist.append(self.bias)
                
    def iterate(self, maxniter=None):
        if maxniter is None:
            maxniter = self.maxniter
        for i in range(maxniter):
            self.iteration()
        return self.ranking

    def close(self):
        if not self.progress_figure_fig is None:
            plt.close(self.progress_figure_fig)

    def save_progress_figure(self, figname):
        self._update_progress_figure()
        self.progress_figure_fig.savefig(figname)

    def sort_battles(self, filename='../data/final/gz2spiralwars.fits.gz', label='spiral'):
        p = pyfits.getdata('../gz2sample_final_wvt.fits')
        objid = p.field('OBJID')
        magsize_bin = p.field('WVT_BIN')
        redshift_bin = p.field('REDSHIFT_SIMPLE_BIN')
        rank = np.zeros(objid.shape, np.int) - 1
        fracrank = np.zeros(objid.shape) - 1
        battle_bin = np.zeros(objid.shape) - 1
        data = pyfits.getdata(filename)
        #data = np.recfromcsv(filename.replace('.fits', '.csv'))
        battles = np.unique(data.battle_bin)
        print('Total number of battles = %i'%len(battles))
        for b in battles:
            select = data.battle_bin == b
            w = data.winner_objid[select]
            l = data.loser_objid[select]
            galaxies = np.unique(np.concatenate((w, l)))
            self.galaxies = self._asarray(galaxies)
            self.winners = self._asarray(w)
            self.losers = self._asarray(l)
            self._consistency_check()
            self._setup_internal_variables()
            print('Battle %i, ngal = %i, nwars = %i'%(b, self.ngal, self.nwars))
            self.iterate()
            for r, id in enumerate(self.ranking):
                idx = (objid == id).nonzero()[0][0]
                rank[idx] = r
                fracrank[idx] = float(r) / self.ngal
                battle_bin[idx] = b

        cols = [pyfits.Column(name='objid', format='K', array=objid),
                pyfits.Column(name='redshift_bin', format='J', array=redshift_bin),
                pyfits.Column(name='magsize_bin', format='J', array=magsize_bin),
                pyfits.Column(name='battle_bin', format='J', array=battle_bin),
                pyfits.Column(name='rank', format='J', array=rank),
                pyfits.Column(name='fracrank', format='E', array=fracrank)]
        tbhdu=pyfits.BinTableHDU.from_columns(cols)
        tbhdu.name = 'gz2%swarsrank'%label
        outfile = '../gz2%swarsrank.fits'%label
        file_exists = os.path.isfile(outfile)
        if file_exists:
            os.remove(outfile)
        tbhdu.writeto(outfile)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


if __name__ == '__main__':
    wars_sort = WarsSort()
    wars_sort.sort_battles('../data/final/gz2spiralwars.fits.gz', 'spiral')
    wars_sort.sort_battles('../data/final/gz2barwars.fits.gz', 'bar')
