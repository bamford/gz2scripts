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
    questions = find_unique(qanda.field('question'))
    questions.sort()
    print questions

questions = ['Could this be a disk viewed edge-on?',
             'Does the galaxy have a bulge at its center? If so what shape',
             'How many spiral arms are there?',
             'How prominent is the bulge?',
             'How rounded is it?',
             'How tightly wound do the spiral arms appear?',
             'Is the galaxy simply smooth and rounded, with no sign of a disk?',
          'Is the odd feature a ring, or is the galaxy disturbed or irregular?',
          'Is there a sign of a bar feature through the centre of the galaxy?',
          'Is there any sign of a spiral arm pattern?',
             'Is there anything odd?']

def get_answers():
    answers = {}
    for q in questions:
        select = qanda.field('question') == q
        a = find_unique(qanda.field('answer')[select])
        a.sort()
        answers[q] = a.tolist()
    print answers

answers = {'Is the galaxy simply smooth and rounded, with no sign of a disk?':
               ['Features or disk', 'Smooth', 'Star or artifact'],
           'Does the galaxy have a bulge at its center? If so what shape':
               ['Boxy', 'No Bulge', 'Rounded'],
           'How tightly wound do the spiral arms appear?':
               ['Loose', 'Medium', 'Tight'],
         'Is the odd feature a ring, or is the galaxy disturbed or irregular?':
           ['Disturbed', 'Irregular', 'Lens or arc', 'Merger', 'Other', 'Ring'],
         'Is there a sign of a bar feature through the centre of the galaxy?':
               ['Bar', 'No Bar'],
           'How many spiral arms are there?':
            ['1', '2', '3', '4', '5', 'Cant tell', 'More than 5'],
           'Could this be a disk viewed edge-on?':
               ['No', 'Yes'],
           'Is there any sign of a spiral arm pattern?':
               ['No Spiral', 'Spiral'],
           'How prominent is the bulge?':
              ['Dominant', 'Just Noticable', 'No bulge', 'Obvious'],
           'How rounded is it?':
               ['Cigar shaped', 'Completely round', 'In between']}

def tutorial_examples():
    f = file('../data/tutorial_examples', 'w')
    sys.stdout = f
    for q in answers.keys():
        print "=== Q:", q, "==="
        for a in answers[q]:
            print "==== A:", a, "===="
            qa_matches(q, a)
            print '-'*70
            sys.stdout.flush()
    sys.stdout = sys.__stdout__


def qa_matches(q, a, n=24):
    # find specified questions
    qselect = qanda.field('question') == q
    # find specified answers
    aselect = qanda[qselect].field('answer') == a
    # get matching classids
    print '*', len(classifications), 'classifications in total'
    classids = qanda.field('classid')[qselect]
    print '*', len(classids), 'classifications for the specified Q'
    classids = classids[aselect]
    print '*', len(classids), 'classifications match the specified Q and A'
    # get corresponding objids
    cselect = find_indexes(classids, classifications.field('classid'))
    objids = classifications.field('objid')[cselect]
    objids = objids[objids > 1]
    objids, count = find_unique(objids, count=True, sort_count=True)
    print '*', len(objids), 'unique objects match the specified Q and A'
    print '* The %i objects with the highest matching classification counts are:'%n
    print '**', ', '.join(str(o) for o in objids[:n])
    print '* with counts:'
    print '**', ', '.join(str(o) for o in count[:n])
    print '* Images:'
    for i in range(n):
        url = get_gz2_images.get_jpeg_url(objids[i])
        if url != '':
            print url+'&.jpg'


def find_indexes(entries, array):
    indexes = []
    for entry in entries:
        idx = (array == entry).nonzero()[0]
        for i in idx:
            if i not in indexes:
                indexes.append(i)
    return indexes
        
def find_unique(array, count=False, sort_count=False):
    uniq = []
    counts = {}
    for entry in array:
        if entry not in uniq:
            uniq.append(entry)
            counts[entry] = 1
        else:
            counts[entry] += 1
    uniq = N.array(uniq)
    if sort_count:
        c = N.array([counts[u] for u in uniq])
        idx = c.argsort()[::-1]
        uniq = uniq[idx]
    if not count:
        return uniq
    else:
        return uniq, [counts[u] for u in uniq]
