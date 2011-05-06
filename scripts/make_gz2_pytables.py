import fits2csv
import csv2fits
import pyfits
import tables
import numpy
import sys
import time
import csv
import astrotools
import time
from collections import deque
from h5fromcsv import tablefromcsv

def make_gz2_hdf5():
    filters = tables.Filters(complevel=1, complib='lzo')
    with tables.openFile('../data/final/gz2results.h5', mode = "w",
                         title = "GZ2 raw results", filters=filters) as h5file:
        group = h5file.createGroup('/', 'final', 'Final GZ2 data')
        names = ['objid', 'sample', 'asset_id', 'task_id', 'answer_id',
                   'count', 'weight', 'fraction', 'weighted_fraction']
        dtype = ['i8', 'a16', 'i4', 'i2', 'i2', 'i2', 'f4', 'f4', 'f4']
        # a converter is required to work-around the current bug whereby
        # numpy badly parses long integers and loses their precision!
        tablefromcsv('../data/final/gz2results.csv', h5file, group,
                     "gz2results", "GZ2 raw results GB",
                     names=names, dtype=dtype, converters={0:long})
        #tablefromcsv('../data/final/gz2results_pl_de.csv', h5file, group,
        #             "gz2results_pl_de", "GZ2 raw results PL DE",
        #             names=names, dtype=dtype)
        fin = '../data/final/tasks.csv'
        columns = ['task_id', 'question']
        rec = numpy.recfromcsv(fin, names=columns, usecols=(0, 1))
        table = h5file.createTable(group, "tasks", rec, "GZ2 tasks")
        table.flush()
        fin = '../data/final/answers.csv'
        columns = ['answer_id', 'answer', 'task_id']
        rec = numpy.recfromcsv(fin, names=columns, usecols=(0, 1, 3))
        table = h5file.createTable(group, "answers", rec, "GZ2 answers")
        table.flush()

def add_gz2_clicks():
    with tables.openFile('../data/final/gz2results.h5', mode = "r+") as h5file:
        names = ['asset_id', 'classification_id', 'annotation_id',
                 'task_id', 'answer_id', 'user_id']
        dtype = ['i4', 'i4', 'i4', 'i2', 'i2', 'i4',]
        tablefromcsv('../data/final/clicks.csv', h5file, "/final",
                     "gz2clicks", "GZ2 raw clicks",
                     names=names, dtype=dtype)
        h5file.flush()

def add_gz2_wars():
    with tables.openFile('../data/final/gz2results.h5', mode = "r+") as h5file:
        names = ['classification_id', 'annotation_id', 'task_id',
                 'user_id', 'winner', 'loser', 'weight', 'battle_bin']
        dtype = ['i4', 'i4', 'i2', 'i4', 'i4', 'i4', 'f4', 'i4']
        tablefromcsv('../data/final/wars_battles.csv', h5file, "/final",
                     "gz2wars", "GZ2 galaxy wars results",
                     names=names, dtype=dtype)
        h5file.flush()

def make_gz2_wars():
    with tables.openFile('../data/final/gz2results.h5', mode = "r+") as h5file:
        wars = h5file.root.final.gz2wars
        spiralwars = wars.readWhere('(user_id != 4) & (task_id == 13)')
        try:
            h5file.removeNode('/wars', recursive=True)
        except tables.NodeError:
            pass
        h5file.createTable("/wars", "spiral", spiralwars,
                           "GZ2 spiral wars",
                           expectedrows=0.5*len(wars),
                           createparents=True)
        barwars = wars.readWhere('(user_id != 4) & (task_id == 12)')
        h5file.createTable("/wars", "bar", barwars,
                           "GZ2 bar wars",
                           expectedrows=0.5*len(wars))

def make_gz2_prewars():
    with tables.openFile('../data/final/gz2results.h5', mode = "r+") as h5file:
        clicks = h5file.root.final.gz2clicks
        try:
            h5file.removeNode('/prewars', recursive=True)
        except tables.NodeError:
            pass
        # select has a spiral:
        spiralprewars = clicks.readWhere('(user_id != 4) & (answer_id == 8)',
                                         field=['user_id', 'classification_id',
                                                'asset_id'])
        h5file.createTable("/prewars", "spiral", spiralprewars,
                           "GZ2 prewar spiral standard classifications",
                           expectedrows=0.05*len(clicks),
                           createparents=True)
        # select has a bar:
        barprewars = clicks.readWhere('(user_id != 4) & (answer_id == 6)',
                                      field=['user_id', 'classification_id',
                                             'asset_id'])
        h5file.createTable("/prewars", "bar", barprewars,
                           "GZ2 prewar bar standard classifications",
                           expectedrows=0.05*len(clicks))
        h5file.flush()


def make_gz2_wars_full():
    # TURN ON PYTABLES PRO INDEXING
    try:
        infilename = '../data/final/gz2results.h5'
        rawh5file = tables.openFile(infilename)
        spiralwars = rawh5file.root.wars.spiral
        barwars = rawh5file.root.wars.bar
        spiralprewars = rawh5file.root.prewars.spiral
        barprewars = rawh5file.root.prewars.bar
        outfilename = '../data/final/gz2table.h5'
        h5file = tables.openFile(outfilename, mode = "r+")
        dtype = numpy.dtype([('wars_classification_id', 'i4'),
                            ('match_classification_id', 'i4'),
                            ('annotation_id', 'i4'), ('task_id', 'i2'),
                            ('user_id', 'i4'), ('starter', 'i4'),
                            ('winner', 'i4'), ('loser', 'i4'),
                            ('weight', 'f4'), ('battle_bin', 'i4')])
        try:
            h5file.removeNode('/gz2spiralwars', recursive=True)
        except tables.NodeError:
            pass
        spiraltable = h5file.createTable("/", "gz2spiralwars", dtype,
                "GZ2 bar wars results matched to standard classifications",
                expectedrows=len(spiralwars))
        try:
            h5file.removeNode('/gz2barwars', recursive=True)
        except tables.NodeError:
            pass
        bartable = h5file.createTable("/", "gz2barwars", dtype,
                "GZ2 bar wars results matched to standard classifications",
                expectedrows=len(barwars))
        nomatch = 0
        count = 0
        latest = 0
        for warcombos in [(spiralwars, spiralprewars, spiraltable),
                         (barwars, barprewars, bartable)]:
            wars, prewars, table = warcombos
            nwars = len(wars)
            hwars = nwars / 3600
            print nwars, len(prewars)
            d1 = d2 = d3 = d4 = d5 = 0
            for w in wars:
                if count % 10 == 0:
                    print w['classification_id'], count, len(table), nomatch
                    print 'timings: %.5f %.5f %.5f %.5f %.5f'%(d1*hwars, d2*hwars, d3*hwars, d4*hwars, d5*hwars)
                count += 1
                # Find id of previous war of this type for this user.
                # By restricting our search for prewar clicks to
                # subsequent ids we will fail to get matches for duplicate
                # clicks, as desired.
                t = time.clock()
                prevwarids = wars.where('(user_id == uid)',
                                        {'uid': w['user_id']},
                                        start=0, stop=w.nrow)
                d1 = (time.clock() - t)/count + d1*(count-1)/count
                prevwarid = {'classification_id': 0}
                t = time.clock()
                for prevwarid in prevwarids: pass # get last value from iterator
                d2 = (time.clock() - t)/count + d2*(count-1)/count
                t = time.clock()
                matches = prewars.where('(user_id == uid) & (classification_id < cid) & (classification_id > pid)', {'uid': w['user_id'], 'cid': w['classification_id'], 'pid': prevwarid['classification_id']}, stop=latest+10000)
                #matches = prewars.where('(user_id == uid) & (classification_id > pid)', {'uid': w['user_id'], 'pid': prevwarid['classification_id']})
                d3 = (time.clock() - t)/count + d3*(count-1)/count
                last = None
                t = time.clock()
                mlist = []
                for last in matches:
                    #if last['classification_id'] >= w['classification_id']:
                    #    break
                    #mlist.append(m.nrow)
                    pass # get last value from iterator
                #print mlist
                #if len(mlist) > 0:
                #    last = prewars.read(mlist[-1])
                d4 = (time.clock() - t)/count + d4*(count-1)/count
                t = time.clock()
                if last is not None:
                    latest = max(latest, last.nrow)
                    last = last.fetch_all_fields()
                    row = [(w['classification_id'],
                            last['classification_id'],
                            w['annotation_id'], w['task_id'], w['user_id'],
                            last['asset_id'], w['winner'], w['loser'],
                            w['weight'], w['battle_bin'])]
                    table.append(row)
                else:
                    nomatch += 1
                d5 = (time.clock() - t)/count + d5*(count-1)/count
            print 'No match for:', nomatch
            print 'Match for:', len(table)
            h5file.flush()
    finally:
        rawh5file.close()
        h5file.close()

def add_gz2_info():
    with tables.openFile('../data/final/gz2table.h5', mode = "r+") as h5file:
        rec = pyfits.getdata('../gz2sample_final_wvt.fits')
        table = h5file.createTable("/", "gz2sample", rec, "GZ2 sample")
        table.flush()

def make_gz2_answers():
    # Run this after manually editing answers.csv --> gz2answers.csv
    # to include the task stub, as well as the answer stub and answer id
    with tables.openFile('../data/final/gz2results.h5', mode = "a") as h5file:
        fin = '../data/final/gz2answers.csv'
        rec = numpy.recfromcsv(fin)
        table = h5file.createTable(h5file.root.final, "taskanswers", rec, "GZ2 tasks and answers")

def make_gz2_pytables():
    try:
        infilename = '../data/final/gz2results.h5'
        rawh5file = tables.openFile(infilename)
        answers = rawh5file.root.final.taskanswers
        dall = rawh5file.root.final.gz2results
        outfilename = '../data/final/gz2table.h5'
        filters = tables.Filters(complevel=1, complib='lzo')
        h5file = tables.openFile(outfilename, mode = "w", title = "GZ2 results table",
                                 filters=filters)
        asset_id_list = dall.col('asset_id')
        ids = numpy.unique(asset_id_list)
        nids = len(ids)
        print 'nids:', nids
        columns = []
        tasks = range(1, 12)
        for ti, t in enumerate(tasks):
            task_answers = answers.where('task_id == t')
            if ti == 0:
                for c in ('objid', 'sample', 'asset_id'):
                    columns.append((c, dall.coldtypes[c]))
                columns.append(('objid_str', 'S20'))
                columns.append(('total_count', numpy.int16))
                columns.append(('total_weight', numpy.float32))
            #print answers.description
            for a in task_answers:
                task = a['task']
                answer = a['answer']
                aid =  a['answer_id']
                for c in ('count', 'weight', 'fraction', 'weighted_fraction'):
                    colname = 't%02i_%s_a%02i_%s_%s'%(t, task, aid, answer, c)
                    columns.append((colname, dall.coldtypes[c]))
            columns.append(('t%02i_%s_total_count'%(t, task), numpy.int16))
            columns.append(('t%02i_%s_total_weight'%(t, task), numpy.float32))
        #print numpy.sort([i for i, j in columns])
        table = h5file.createTable("/", "gz2table", numpy.recarray((0,), dtype=columns),
                                   "GZ2 results table", expectedrows=nids)
        row = table.row
        if not (asset_id_list == numpy.sort(asset_id_list)).all():
            print 'Error: asset_id not sorted!'
            return
        ndall = len(dall)
        print 'ndall:', ndall
        # just to add check on fraction > 1 to get rid of few oddities
        # fixed in database creation now
        # dall = dall[dall.fraction <= 1]
        # print len(dall)
        current_index = 0
        tstart = time.clock()
        for iid, assid in enumerate(ids):
            if iid > 0 and iid%5000 == 0:
                print_status(iid, nids, tstart)
            # This is the naive way of getting all rows with matching asset_id
            # but it is slow (at least without PyTables _Pro_, which supports indexes)
            #d_asset = dall.readWhere('asset_id == assid')
            # This approach uses the fact that the table is sorted by asset_id
            # to find the matching rows faster, without having to search the whole table
            start_index = current_index
            while current_index < ndall and asset_id_list[current_index] == assid:
                current_index += 1
            if start_index == current_index:
                print 'Warning! %i not matched'%assid
                continue
            d_asset = dall[start_index:current_index]
            row['total_count'] = numpy.sum(x['count'] for x in d_asset)
            row['total_weight'] = numpy.sum(x['weight'] for x in d_asset)
            first_task = True
            for ti, t in enumerate(tasks):
                task_answers = answers.where('task_id == t')
                d_task = d_asset[d_asset['task_id'] == t]
                #d_task = dall.readWhere('(asset_id == assid) & (task_id == t)')
                first_answer = True
                for ai, a in enumerate(task_answers):
                    task = a['task']
                    aid = a['answer_id']
                    d = d_task[d_task['answer_id'] == aid]
                    n = len(d)
                    if n > 1:
                        raise Exception('More than one row matches selection (%i rows)'%n)
                    if n == 1 and first_answer:
                        first_answer = False
                        if first_task:
                            first_task = False
                            for c in ('objid', 'sample', 'asset_id'):
                                row[c] = d[c][0]
                            row['objid_str'] = str(d['objid'][0])
                        row['t%02i_%s_total_count'%(t, task)] = numpy.sum(x['count']
                                                                          for x in d_task)
                        row['t%02i_%s_total_weight'%(t, task)] = numpy.sum(x['weight']
                                                                           for x in d_task)
                    for c in ('count', 'weight', 'fraction', 'weighted_fraction'):
                        colname = 't%02i_%s_a%02i_%s_%s'%(t, task, aid, a['answer'], c)
                        if n == 1:
                            row[colname] = d[c][0]
                        else:
                            row[colname] = 0
            #print row
            row.append()
        table.flush()
        print
        print iid
    finally:
        rawh5file.close()
        h5file.close()
    #fits2csv.fits2csv_round(outfilename, outfilename.replace('.fits', '.csv.gz'), round=2, gzipped=True)

def update_samples():
    outfilename = '../data/final/gz2table.h5'
    h5file = tables.openFile(outfilename, mode = 'r+')
    table = h5file.root.gz2table
    old = table.where('(sample == "stripe82_coadd") & (asset_id < 325652)')
    for row in old:
        row['sample'] = 'stripe82_coadd_1'
        row.update()
    new = table.where('(sample == "stripe82_coadd") & (asset_id >= 325652)')
    for row in new:
        row['sample'] = 'stripe82_coadd_2'
        row.update()
    h5file.close()


def print_status(iid, nids, tstart):
    telapsed = time.clock() - tstart
    ttot = telapsed * (nids / float(iid))
    trems = int(ttot - telapsed)
    tremh = trems//3600
    trems = trems - tremh*3600
    tremm = trems//60
    trems = trems - tremm*60
    print 'iid: %i (time remaining = %ih %02im %02is)'%(iid, tremh, tremm, trems)

def h5tosplitcsv(n=5000):
    #  CASJobs seems to be limited to 10000 rows at a time
    h5file = tables.openFile('../data/final/gz2table.h5')
    t = len(h5file.root.gz2table)
    for i in range(t//n + 1):
        ii = i*n
        jj = min(ii+n, t)
        f = open('../data/final/gz2table-split%03i.csv'%i, 'wb')
        writer = csv.writer(f)
        writer.writerow(h5file.root.gz2table.colnames)
        writer.writerows(h5file.root.gz2table[ii:jj])
        f.close()
    h5file.close()

def h5tocsv():
    h5file = tables.openFile('../data/final/gz2table.h5')
    writer = csv.writer(open('../data/final/gz2table.csv', 'wb'))
    writer.writerow(h5file.root.gz2table.colnames)
    writer.writerows(h5file.root.gz2table[:])
    h5file.close()

def h5tofits():
    h5file = tables.openFile('../data/final/gz2table.h5')
    pyfits.writeto('../data/final/gz2table.fits', h5file.root.gz2table.read())
    h5file.close()

def upload_to_casjobs():
    import pyCasJobs
    from glob import glob
    import os.path
    cas = pyCasJobs.CasJobs('bamford', 'LilY5eTs')
    fnames = glob('../data/final/gz2table-split*.csv')
    for i, fname in enumerate(fnames):
        print fname
        cas.import_table(fname, 'gz2table_v3', tableexists=(i>0))
        time.sleep(1)
