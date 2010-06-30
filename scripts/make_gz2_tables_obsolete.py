import fits2csv
import csv2fits
import pyfits
import numpy
import sys
import time

def make_gz2_fits():
    fin = '../data/final/gz2results.csv'
    columns = ['objid', 'sample', 'asset_id', 'task_id', 'answer_id',
               'count', 'weight', 'fraction', 'weighted_fraction']
    fout = fin.replace('.csv', '.fits')
    csv2fits.csv2fits(fin, fout, columns=columns)
    fin = '../data/final/tasks.csv'
    columns = ['task_id', 'question']
    fout = fin.replace('.csv', '.fits')
    csv2fits.csv2fits(fin, fout, columns=columns)
    fin = '../data/final/answers.csv'
    columns = ['answer_id', 'answer', 'null', 'task_id']
    fout = fin.replace('.csv', '.fits')
    csv2fits.csv2fits(fin, fout, columns=columns)
    fits2csv.fits2csv(fout, '../data/final/gz2answers.csv',
                      selectednames=('task_id', 'answer_id', 'answer'), keeporder=False)

def make_gz2_answers():
    fin = '../data/final/gz2answers.csv'
    fout = fin.replace('.csv', '.fits')
    csv2fits.csv2fits(fin, fout)
    
def make_gz2_tables():
    answers = pyfits.getdata('../data/final/gz2answers.fits')
    p = pyfits.open('../data/final/gz2results.fits')
    dformats = {}
    for c in p[1].columns:
        dformats[c.name] = c.format
    dall = p[1].data[:2000]
    outfilename = '../data/final/gz2table.fits'
    ids = numpy.unique(dall.asset_id)
    nids = len(ids)
    print nids
    columns = {}
    formats = {}
    tasks = range(1, 12)
    for ti, t in enumerate(tasks):
        task_answers = answers[answers.task_id == t]
        if ti == 0:
            for c in ('objid', 'sample', 'asset_id'):
                columns[c] = numpy.zeros(nids, dtype=dall.field(c).dtype)
                formats[c] = dformats[c]
        columns['total_count'] = numpy.zeros(nids, dtype=numpy.int)
        formats['total_count'] = 'I'
        columns['total_weight'] = numpy.zeros(nids, dtype=numpy.float)
        formats['total_weight'] = 'E'
        for a in task_answers:
            task = a.field('task')
            answer = a.field('answer')
            aid = a.field('answer_id')
            for c in ('count', 'weight', 'fraction', 'weighted_fraction'):
                colname = 't%02i_%s_a%02i_%s_%s'%(t, task, aid, answer, c)
                columns[colname] = numpy.zeros(nids, dtype=dall.field(c).dtype)
                formats[colname] = dformats[c]
        columns['t%02i_%s_total_count'%(t, task)] = numpy.zeros(nids, dtype=numpy.int)
        formats['t%02i_%s_total_count'%(t, task)] = 'I'
        columns['t%02i_%s_total_weight'%(t, task)] = numpy.zeros(nids, dtype=numpy.float)
        formats['t%02i_%s_total_weight'%(t, task)] = 'E'
    print numpy.sort(columns.keys())
    cols = []
    for c in numpy.sort(columns.keys()):
        cols.append(pyfits.Column(name=c, format=formats[c], array=columns[c]))
    tbhdu = pyfits.new_table(cols)
    tbhdu.writeto(outfilename, clobber=True)
    del tbhdu, cols, columns, formats
    q = pyfits.open(outfilename, mode='update') #, memmap=1)  # memmap flaky!
    columns = q[1].data
    if not (dall.asset_id == numpy.sort(dall.asset_id)).all():
        print 'Error: asset_id not sorted!'
        return
    ndall = len(dall)
    print ndall
    # just to add check on fraction > 1 to get rid of few oddities
    # fixed in database creation now
    # dall = dall[dall.fraction <= 1]
    # print len(dall)
    current_index = 0
    asset_id_list = dall.asset_id
    for iid, assid in enumerate(ids):
        q.flush()
        if iid%100 == 0:
            print iid,
            sys.stdout.flush()
        #asset_selection = (dall.asset_id == assid).nonzero()[0]
        #d_asset = dall[asset_selection]
        start_index = current_index
        while current_index < ndall and asset_id_list[current_index] == assid:
            current_index += 1
        d_asset = dall[start_index:current_index]
        columns.field('total_count')[iid] = d_asset.field('count').sum()
        columns.field('total_weight')[iid] = d_asset.field('weight').sum()
        for ti, t in enumerate(tasks):
            task_answers = answers[answers.task_id == t]
            task_selection = d_asset.field('task_id') == t
            d_task = d_asset[task_selection]
            d_task_answer_id = d_task.field('answer_id')
            first_answer = True
            for ai, a in enumerate(task_answers):
                task = a.field('task')
                aid = a.field('answer_id')
                answer_selection = (d_task_answer_id == aid).nonzero()[0]
                n = len(answer_selection)
                if n > 1:
                    raise Exception('More than one row matches selection (%i rows)'%n)
                if n == 1:
                    d = d_task[answer_selection]
                if n == 1 and first_answer:
                    first_answer = False
                    for c in ('objid', 'sample', 'asset_id'):
                            columns.field(c)[iid] = d.field(c)[0]
                    columns.field('t%02i_%s_total_count'%(t, task))[iid] = d_task.field('count').sum()
                    columns.field('t%02i_%s_total_weight'%(t, task))[iid] = d_task.field('weight').sum()
                for c in ('count', 'weight', 'fraction', 'weighted_fraction'):
                    colname = 't%02i_%s_a%02i_%s_%s'%(t, task, aid, a.field('answer'), c)
                    if n == 1:
                        columns.field(colname)[iid] = d.field(c)[0]
                    else:
                        columns.field(colname)[iid] = 0
    print
    print iid
    q.close()
    #columns.writeto(outfilename, clobber=True)
    #fits2csv.fits2csv_round(outfilename, outfilename.replace('.fits', '.csv.gz'), round=2, gzipped=True)
