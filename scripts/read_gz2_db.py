import pyfits
import xml.parsers.expat
import os
import time
import string

from get_gz2_data import *

dbfilename = '/Users/spb/Work/projects/GalaxyZoo2/data/ClassificationGZ2.csv'
fitsfilename = dbfilename.replace('.csv', '.fits')
    
def read_gz2_db():
    # Set up XML parser
    print 'Setting up XML parser'
    class XMLParserFuncs:
        def __init__(self):
            self._current = {}
            self.questiontext = None
            self.answertext = None
            self.compobjid = None
        def inelement(self, name):
            if name in self._current.keys():
                return self._current[name]
            else:
                return False
        def start_element(self, name, attrs):
            self._current[name] = True
            if name == 'xml':
                self.questiontext = None
                self.answertext = None
                self.compobjid = None
        def end_element(self, name):
            self._current[name] = False
        def char_data(self, data):
            if self.inelement('question') or self.inelement('compquestion'):
                self.questiontext = data
                self.answertext = None
            elif self.inelement('comparisongalaxyid'):
                self.compobjid = data
            elif self.inelement('answer') or self.inelement('companswer'):
                self.answertext = data
                qaclassid.append(id)
                questions.append(self.questiontext)
                answers.append(self.answertext)
                self.questiontext = None
                self.answertext = None
 
    xp = XMLParserFuncs()

    # Read database dump file
    print 'Reading database dump file'
    f = file(dbfilename)
    classid = []
    objid = []
    username = []
    expertise = []
    date = []
    transformation = []
    compobjid = []
    qaclassid = []
    questions = []
    answers = []
    for l in f:
        l = l.decode('windows-1252')
        l = l.encode('utf-8', 'ignore')
        l = l.replace('\x00', '')
        l = l.strip()
        if len(l) < 1:
            continue
        if not l.startswith('<'):
            #print 'Before: ', l
            l = l[l.find('<'):]
            #print 'After:  ', l
        s = l.rfind('>') + 1
        c = l[:s].strip()
        ls = l[s+1:].split(',')
        if ls[0] == '':
            continue
        objid.append(long(ls[0]))
        username.append(ls[1])
        date.append(ls[3])
        expertise.append(int(ls[2]))
        transformation.append(ls[6])
        id = long(ls[4])
        classid.append(id)
        if int(id)%1000 == 0:
            print id
        p = xml.parsers.expat.ParserCreate()
        p.StartElementHandler = xp.start_element
        p.EndElementHandler = xp.end_element
        p.CharacterDataHandler = xp.char_data
        p.Parse(c)
        if xp.compobjid is None:
            compobjid.append(0)
        else:
            compobjid.append(long(xp.compobjid))
    # Close file
    f.close()

    # Create fits file
    p = pyfits.HDUList()
    p.append(pyfits.PrimaryHDU())

    # Create Classifications table
    cols = [pyfits.Column(name='classid', format='J', array=classid),
            pyfits.Column(name='objid', format='K', array=objid),
            pyfits.Column(name='username', format='128A', array=username),
            pyfits.Column(name='expertise', format='I', array=expertise),
            pyfits.Column(name='date', format='32A', array=date),
            pyfits.Column(name='transformation', format='32A',
                          array=transformation),
            pyfits.Column(name='compobjid', format='K', array=compobjid)]
    classifications = pyfits.new_table(cols)
    classifications.name = 'Classifications'
    p.append(classifications)

    # Get QandA table, or create if not present
    cols = [pyfits.Column(name='classid', format='J', array=qaclassid),
            pyfits.Column(name='question', format='128A', array=questions),
            pyfits.Column(name='answer', format='128A', array=answers)]
    qanda = pyfits.new_table(cols)
    qanda.name = 'QandA'
    p.append(qanda)

    # Write file
    if os.path.exists(fitsfilename):
        os.remove(fitsfilename)
    p.writeto(fitsfilename)
