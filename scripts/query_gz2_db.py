import numpy as N
import sys
import get_gz2_images
from get_gz2_classifications import *

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
               ['Disturbed', 'Irregular', 'Lens or Arc', 'Merger',
                'Other', 'Ring'],
           'Is there a sign of a bar feature through the centre of the galaxy?':
               ['Bar', 'No Bar'],
           'How many spiral arms are there?':
               ['1', '2', '3', '4', '5', "Can't tell", 'More than 5'],
           'Could this be a disk viewed edge-on?':
               ['No', 'Yes'],
           'How prominent is the bulge?':
               ['Dominant', 'Just Noticable','No Bulge', 'Obvious'],
           'Does the galaxy have a bulge at its centre?  If  so, what shape?':
               ['Boxy', 'No Bulge', 'Rounded'],
           'How rounded is it?':
               ['Cigar Shaped', 'Completely Round', 'In Between']}


def examples():
    f = file('../data/examples', 'w')
    sys.stdout = f
    print '<html>'
    print '<head>'
    print '<title>Examples of Galaxy Zoo 2 beta classifications</title>'
    print '<link rel="stylesheet" href="./examples.css" />'
    print '</head>'
    print '<body>'
    print '<h1>Examples of Galaxy Zoo 2 beta classifications</h1>'
    for q in questions:
        sys.stderr.write(q+'\n')
        print '<h2>Q:', q, '</h2>'
        for a in answers[q]:
            sys.stderr.write(a+'\n')
            print '<h3>A:', a, '</h3>'
            sys.stdout.flush()
            qa_matches(q, a)
            print '<hr />'
            sys.stdout.flush()
    print '</body></html>'
    sys.stdout = sys.__stdout__


def qa_matches(q, a, n=10):
    # find specified questions
    #sys.stderr.write('qselect\n')
    qselect = qanda.field('question') == q
    # find specified answers
    #sys.stderr.write('aselect\n')
    aselect = qanda[qselect].field('answer') == a
    # get matching classids
    print '<ul>'
    print '<li>', len(classifications), 'classifications in total'
    classindexq = qanda.field('classindex')[qselect]
    print '</li><li>', len(classindexq), 'classifications for the specified Q'
    classindexqa = classindexq[aselect]
    print '</li><li>', len(classindexqa), 'classifications match the specified Q and A'
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
    # get number of times Q asked and A given for each object
    objidsq, countq = find_unique(objidsq, count=True, sort_count=True)
    objidsqa, countqa = find_unique(objidsqa, count=True, sort_count=True)
    qselectqa = find_indexes(objidsqa, objidsq)
    objidsq = objidsq[qselectqa]
    countq = countq[qselectqa]
    nmatch = len(objidsqa)
    likelihood = countqa/countq.astype(N.float)
    n = min(n, len(likelihood))
    s = countqa.argsort()[-n:][::-1]
    objidsq = objidsq[s]
    countq = countq[s]
    objidsqa = objidsqa[s]
    countqa = countqa[s]
    likelihood = likelihood[s]
    print '</li><li>', nmatch, 'unique objects match the specified Q and A'
    print '</li><li>The %i objects with the most counts for this Q and A are:'%n
    print
    print '</li></ul><table>'
    print '<tr><th>image</th><th>%32s</th><th>%8s</th><th>%8s</th><th>%8s</th><th>%nbsp;</th><th>image</th><th>%32s</th><th>%8s</th><th>%8s</th><th>%8s</th></tr>'%('objid', 'nanswer', 'nquestion', 'likelihood')
    for i in range(n):
        print '<tr><td><a href="%s" target="_blank"><img src="%s" width="106px" height="106px"/></a></td><td>%32s</td><td>%8i</td><td>%8i</td><td>%8.2f</td>'%(get_gz2_images.get_jpeg_url(objidsqa[i], imgsize=424), get_gz2_images.get_jpeg_url(objidsqa[i], imgsize=106, scale=2.0), objidsqa[i], countqa[i], countq[i], likelihood[i])
        if i%2 != 0 or i == n-1:
            print '</tr>'
        else:
            print '<td>%nbsp;</td>'
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
    uniq = N.unique(array)
    if count or sort_count:
        a = N.sort(array)
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
