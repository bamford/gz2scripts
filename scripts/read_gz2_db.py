import MySQLdb
import numpy as N
import sys, os
#import get_gz2_images
#import ppgplot_spb
#from ppgplot_spb import *
import pylab
import time

#pgend()

## To tunnel:
## ssh -L 3307:zooslave.cezuuccr9cw6.us-east-1.rds.amazonaws.com:3306 mt

user = 'root'
#host = 'zooslave.cezuuccr9cw6.us-east-1.rds.amazonaws.com'
host = '127.0.0.1'
port = 3307
passwd = 'ZnspImms'
database = 'production'

db = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=database)
cursor = db.cursor(MySQLdb.cursors.SSCursor)

def hist_classifications():
    query = '''
select count
from gz2results
where sample = %s
and task_id = 1
and answer_id = "all"
'''
    cursor.execute(query, ("original",))
    original = N.transpose(cursor.fetchall())[0]
    cursor.execute(query, ("extra",))
    extra = N.transpose(cursor.fetchall())[0]
    cursor.execute(query, ("stripe82",))
    stripe82 = N.transpose(cursor.fetchall())[0]
    cursor.execute(query, ("stripe82_coadd",))
    coadd = N.transpose(cursor.fetchall())[0]
    return original, extra, stripe82, coadd

def plot_hist_classifications():
     o, e, s, c = hist_classifications()
     for i in [o,e,s,c]:
         pylab.hist(i, 80, (0, 80))
