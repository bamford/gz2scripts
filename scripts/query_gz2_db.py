import numpy as N
import sys, os
import get_gz2_images
from get_gz2_classifications import *
import ppgplot_spb
from ppgplot_spb import *
import time

pgend()

def tutorial_smooth():
    q = 'Is the galaxy simply smooth and rounded, with no sign of a disk?'
    a = 'Smooth'
    return qa_matches(q, a)
# produces:
# 587729158427639937 4
# 588017721177669716 4
# 587733195160616967 4
# 587745539984916647 4
# 587739845382111436 3
# 587736915142574259 3
# 587725040090742995 3
# 587741531705507894 3
# 587726014012391473 3


def tutorial_features():
    q = 'Is the galaxy simply smooth and rounded, with no sign of a disk?'
    a = 'Features or disk'
    return qa_matches(q, a)
# produces:
# 587724197207212141 4
# 587742188829081720 3
# 587738948280189093 3
# 587742014908923912 3
# 587729409685323865 3
# 588017947210350605 3
# 587738947744628797 3
# 587742774030106785 3
# 587731172767498868 3

def get_questions():
    questions, counts = find_unique(qanda.field('question'), count=True)
    s = questions.argsort()
    print s
    questions = questions[s]
    counts = counts[s]
    for i in range(len(questions)):
        print '%-65s %i'%(questions[i], counts[i])
    return questions

questions = [
       'Is the galaxy simply smooth and rounded, with no sign of a disk?',
       'How rounded is it?',
       'Could this be a disk viewed edge-on?',
       'How prominent is the bulge?',
       'Does the galaxy have a bulge at its centre?  If  so, what shape?',
       'Is there any sign of a spiral arm pattern?',
       'How tightly wound do the spiral arms appear?',
       'How many spiral arms are there?',
       'Is there a sign of a bar feature through the centre of the galaxy?',
       'Is there anything odd?',
       'Is the odd feature a ring, or is the galaxy disturbed or irregular?']

def get_answers():
    answers = {}
    for q in questions:
        print q
        select = qanda.field('question') == q
        a, counts = find_unique(qanda.field('answer')[select], count=True)
        s = a.argsort()
        a = a[s]
        counts = counts[s]
        s = N.array([i.strip()[:2] != '58' for i in a])
        a = a[s]
        counts = counts[s]
        answers[q] = a.tolist()
        for i in range(len(a)):
            print '   %40s %i'%(a[i], counts[i])
    return answers

answers = {'Is there anything odd?':
               ['No', 'Yes'],
           'Is the galaxy simply smooth and rounded, with no sign of a disk?':
               ['Features or Disk', 'Smooth', 'Star or Artifact'],
           'Is there any sign of a spiral arm pattern?':
               ['No Spiral', 'Spiral'],
           'How tightly wound do the spiral arms appear?':
               ['Loose', 'Medium', 'Tight'],
         'Is the odd feature a ring, or is the galaxy disturbed or irregular?':
               ['Disturbed', 'Irregular', 'Lens or Arc', 'Merger', 'Ring',
                'Other'],
           'Is there a sign of a bar feature through the centre of the galaxy?':
               ['Bar', 'No Bar'],
           'How many spiral arms are there?':
               ['1', '2', '3', '4', '5', "Can't tell", 'More than 5'],
           'Could this be a disk viewed edge-on?':
               ['No', 'Yes'],
           'How prominent is the bulge?':
               ['Dominant', 'Obvious', 'Just Noticable','No Bulge'],
           'Does the galaxy have a bulge at its centre?  If  so, what shape?':
               ['No Bulge', 'Rounded', 'Boxy'],
           'How rounded is it?':
               ['Cigar Shaped', 'In Between', 'Completely Round']}


def examples_multi(for_public=False):
    if for_public:
        ncol = 8
        n = 80
    else:
        ncol = 2
        n = 80
    imgf = file('../data/imgfiles', 'w')
    for iq, q in enumerate(questions):
        for ia, a in enumerate(answers[q]):
            sys.stderr.write(a+'\n')
            if for_public:
                f = file('../data/for_public/examples_q%i_a%i.html'%(iq, ia), 'w')
            else:
                f = file('../data/for_team/examples_q%i_a%i.html'%(iq, ia), 'w')
            sys.stdout = f
            print('<html>')
            print('<head>')
            print('<title>Examples of Galaxy Zoo 2 beta classifications</title>')
            print('<link rel="stylesheet" href="./examples.css" />')
            print('</head>')
            print('<body>')
            print('<h1>Examples of Galaxy Zoo 2 beta classifications</h1>')
            print('<h2>Q: %s</h2>'%q)
            print('<h3>A: %s</h3>'%a)
            f.flush()
            qa_matches(q, a, n, ncol, for_public, imgf)
            print('<hr />')
            f.flush()
            print('</body></html>')
            sys.stdout = sys.__stdout__
            f.close()
    imgf.close()


def examples(for_public=False):
    if for_public:
        f = file('../data/for_public/examples.html', 'w')
    else:
        f = file('../data/for_team/examples.html', 'w')
    sys.stdout = f
    print '<html>'
    print '<head>'
    print '<title>Examples of Galaxy Zoo 2 beta classifications</title>'
    print '<link rel="stylesheet" href="./examples.css" />'
    print '</head>'
    print '<body>'
    print '<h1>Examples of Galaxy Zoo 2 beta classifications</h1>'
    print '<p>Images with the most classifications for each'
    print '   Q and A combination.</p>' 
    print '<p>The images are half the scale and half the field of view'
    print '   of those used to classify.  Click on an image to see'
    print '   the classification-size version.</p>' 
    if not for_public:
        print '<p>No cleaning has been applied to the dataset yet,'
        print '   e.g. multiple clicks by a single user,',
        print ' unreliable users, etc.</p>'
    if not for_public:
        users, usercounts = find_unique(classifications.field('username'),
                                        count=True, sort_count=True)
        nusers = len(users)
        nc = len(classifications)
        print '<div class="info"><p>In total:<ul>'
        print '<li>%i users</li>'%nusers
        print '<li>%i classifications</li>'%nc
        print '</ul></div>'
    if not for_public:
        maxusercounts = usercounts[0]+1
        x = N.log10(usercounts)
        x, y = bin_array(x, 20, 0, N.log10(maxusercounts))
        N.putmask(y, y < 0.1, 0.01)
        y = N.log10(y)
        plotfile = '../data/for_team/Udist.ps'
        pgopen(plotfile+'/cps')
        global cf
        ppgplot_spb.cf = 1
        pgsetup()
        pgsvp(0.2, 0.9, 0.5, 0.9)
        pgswin(0, N.log10(maxusercounts), -0.5, y.max()*1.1)
        pgbox('BCNLTS', 0, 0, 'BCLNTS', 0, 0)
        pglab('log\d10\u(n classifications)', 'log\d10\u(n users)', '')
        pgxsci('aqua')
        pgslw(2*lw)
        pgbin(x, y)
        pgslw(lw)
        pgsci(1)
        pgclos()
        ps2gif(plotfile)
        print '<div class="plot"><img src="Udist.gif" /></div>'
    if for_public:
        ncol = 8
        n = 24
    else:
        ncol = 2
        n = 10
    for iq, q in enumerate(questions):
        sys.stderr.write(q+'\n')
        print '<h2>Q:', q, '</h2>'
        for ia, a in enumerate(answers[q]):
            sys.stderr.write(a+'\n')
            print '<h3>A:', a, '</h3>'
            print '<p><a href="examples_q%i_a%i.html">more examples...</a></p>'%(iq, ia)
            sys.stdout.flush()
            qa_matches(q, a, n, ncol, for_public)
            print '<hr />'
            sys.stdout.flush()
    print '</body></html>'
    sys.stdout = sys.__stdout__


def qa_matches(q, a, n=10, ncol=2, for_public=False, imgf=None):
    # find specified questions
    #sys.stderr.write('qselect\n')
    qselect = qanda.field('question') == q
    # find specified answers
    #sys.stderr.write('aselect\n')
    aselect = qanda[qselect].field('answer') == a
    # get matching classids
    classindexq = qanda.field('classindex')[qselect]
    classindexqa = classindexq[aselect]
    nq = len(classindexq)
    nqa = len(classindexqa)
    if not for_public:
        print '<div class="info"><ul>'
        print '</li><li>', nq, 'classifications for this question'
        print '</li><li>', nqa, 'classifications match this answer '
    # get objids of objects for which this question was asked
    #sys.stderr.write('cselectq\n')
    objidsq = classifications.field('objid')[classindexq]
    goodobjidsq = objidsq > 1
    objidsq = objidsq[goodobjidsq]
    # get objids of above objects for which this answer was given
    #sys.stderr.write('qselectqa\n')
    objidsqa = classifications.field('objid')[classindexqa]
    goodobjidsqa = objidsqa > 1
    objidsqa = objidsqa[goodobjidsqa]
    objidsqa.sort()
    # get number of times Q asked for each object
    objidsq, countq = find_unique(objidsq, count=True)
    # count number of times answer A given for each object where Q asked
    countqa = (objidsqa.searchsorted(objidsq, 'right') -
               objidsqa.searchsorted(objidsq, 'left'))
    countqa_argsort = N.argsort(countqa)
    objidsq = objidsq[countqa_argsort]
    countq = countq[countqa_argsort]
    countqa = countqa[countqa_argsort]
    nmatch = len(objidsq)
    likelihood = countqa/countq.astype(N.float)
    iq = questions.index(q)
    ia = answers[q].index(a)
    if not for_public:
        # make likelihood histogram
        countq_sorted = N.sort(countq)
        # only work out likelihood using objects with more than
        # a certain number of counts, such that at least 1000
        # objects are used
        minnobj = 1000
        mincountq = N.sort(countq)[-minnobj]
        #mincountq = 4
        l = likelihood[countq >= mincountq]
        nobj = len(l)
        minfrac = 1.0/nobj
        x, y = bin_array(l, mincountq+1, -0.05, 1.05)
        y = y/float(nobj)
        N.putmask(y, y < minfrac, minfrac/2.0)
        y = N.log10(y)
        plotfile = '../data/for_team/Ldist_q%i_a%i.ps'%(iq, ia)
        pgopen(plotfile+'/cps')
        ppgplot_spb.cf = 1
        pgsetup()
        pgsvp(0.2, 0.9, 0.5, 0.9)
        pgswin(-0.05, 1.05, -3.1, 0.1)
        pgbox('BCNTS', 0, 0, 'BCLNTS', 0, 0)
        pglab('P(A|Q)', 'fraction', '')
        pgxsci('aqua')
        pgslw(2*lw)
        pgbin(x, y)
        pgslw(lw)
        pgsci(1)
        pgclos()
        ps2gif(plotfile)
    n = min(n, len(likelihood))
    objidsq = objidsq[-n:]
    countq = countq[-n:]
    countqa = countqa[-n:]
    likelihood = likelihood[-n:]
    bigimages = get_gz2_images.get_jpeg_url(objidsqa, imgsize=424)
    smallimages = get_gz2_images.get_jpeg_url(objidsqa, imgsize=106, scale=2.0)
    if not for_public:
        print '</li><li>', nmatch, 'unique objects match this question'
        print '</li><li>Histogram uses %i objects, each with at least %i classifications for this question'%(nobj, mincountq)
        print '</li><li>The %i objects with the most counts for this answer are:'%n
        print '</li></ul></div>'
        print '<div class="plot"><img class="up" src="Ldist_q%i_a%i.gif" /></div>'%(iq, ia)
        print '<table>'
        print '<tr><th>%s</th><th>%32s</th><th>%8s</th><th>%8s</th><th>%8s</th><th width="48px">&nbsp;</th><th>image</th><th>%32s</th><th>%8s</th><th>%8s</th><th>%8s</th></tr>'%('image', 'objid', 'nA', 'nQ', 'P', 'objid', 'nA', 'nQ', 'P')
    for i in range(n): 
        if i%ncol == 0:
            print '<tr>'
        imgfilesmall = 'img_q%i_a%i_n%i_small.jpg'%(iq, ia, i)
        imgfilebig = 'img_q%i_a%i_n%i.jpg'%(iq, ia, i)
        if imgf is not None:
            imgf.write('%s %s\n'%(imgfilesmall, smallimages[i]))
            imgf.write('%s %s\n'%(imgfilebig, bigimages[i]))
        if for_public:
            print '<td><a href="%s" target="_blank"><img src="%s" width="106px" height="106px"/></a></td>'%(imgfilebig, imgfilesmall)
        else:
            print '<td><a href="%s" target="_blank"><img src="%s" width="106px" height="106px"/></a></td><td>%32s</td><td>%8i</td><td>%8i</td><td>%8.2f</td>'%(imgfilebig, imgfilesmall, objidsqa[i], countqa[i], countq[i], likelihood[i])
        if i%ncol != 0 or i == n-1:
            print '</tr>'
        elif not for_public:
            print '<td>&nbsp;</td>'
    print '</table>'


# Massively sped up by avoiding the need for two find_indexes,
# by adding indexes of classifications into qanda in read_gz2_db.
# and by rewriting code more efficiently

# Now find_indices finds 1000 entries in 100,000 item array
# 25 times faster than previous, naive, version.
def find_indexes(entries, array):
    indexes = []
    n = len(array)
    ids = N.arange(n)
    sortindexes = array.argsort()
    a = array[sortindexes]
    idx = ids[sortindexes]
    ileft = a.searchsorted(entries, 'left')
    iright = a.searchsorted(entries, 'right')
    ok = ileft < n
    ileft = ileft[ok]
    iright = iright[ok]
    indexes = []
    for i in range(len(ileft)):
            indexes.extend(idx[ileft[i]:iright[i]])
    return N.unique(indexes)

def find_indexes_old(entries, array):
    indexes = []
    ids = N.arange(len(array))
    for entry in entries:
        idx = ids[array == entry]
        for i in idx:
            if i not in indexes:
                indexes.append(i)   
    return N.array(indexes)
        
# now finds unique entries in 10000 item array 100 times
# faster than previous, naive, version!
def find_unique(array, count=False, sort_count=False):
    array = N.asarray(array)
    uniq = N.unique(array)
    if count or sort_count:
        a = N.sort(array)
        sys.stdout.flush()
        counts = (a.searchsorted(uniq, 'right') -
                  a.searchsorted(uniq, 'left'))
    if sort_count:
        idx = counts.argsort()[::-1]
        uniq = uniq[idx]
        if count:
            counts = counts[idx]
    if not count:
        return uniq
    else:
        return uniq, counts

def find_unique_old(array, count=False, sort_count=False):
    uniq = []
    counts = {}
    for entry in array:
        if entry not in uniq:
            uniq.append(entry)
            counts[entry] = 1
        else:
            counts[entry] += 1
    uniq = N.array(uniq)
    if sort_count or count:
        c = N.array([counts[u] for u in uniq])
    if sort_count:
        idx = c.argsort()[::-1]
        uniq = uniq[idx]
    if not count:
        return uniq
    else:
        return uniq, c

def ps2gif(f):
    os.system('convert -negate -density 96 -rotate 90 %s %s'%(f, f.replace('.ps', '.gif')))
