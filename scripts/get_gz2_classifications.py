import MySQLdb

user = 'sciapi'
host = 'scidb.galaxyzoo.org'
password = 'Snsp_Imms'
database = 'juggernaut_production'

class table_helper:
    def __init__(self, table, cursor):
        self.table = table
        self.cursor = cursor
    def field(self, f):
        return table_column(self, f)

class table_column:
    def __init__(self, table, field):
        self.table = table
        self.field = field
    
    def __getitem__(self, i):
        condition = 'id = (' + ','.join(i) + ')'
        self.where(condition)
    
    def select(self, condition=False, distinct=False):
        if condition:
            condition = 'where %s'%condition
        if distinct:
            table.cursor.execute('SELECT %s from %s %s order by id',
                                 (self.field, self.table.table, condition))
            return table.cursor.fetchall()
        else:
            table.cursor.execute('SELECT %(field)s, count(%(field)s) from %(table)s %(condition)s group by %(field)s order by %(field)s',
                                 {'field': self.field, 'table': self.table.table,
                                  'condition': condition})
            return N.transpose(table.cursor.fetchall())

    def distinct(self):
        return self.select(distinct=True)

    def all(self):
        return self.select()

db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=database)
cursor = db.cursor(MySQLdb.cursors.SSCursor)

qanda = table_helper('annotations', cursor)

answers = table_helper('answers', cursor)

# OLD:
# import pyfits

# filename = '/Users/spb/Work/projects/GalaxyZoo2/data/ClassificationGZ2.fits'
# #filename = '/Users/spb/Work/projects/GalaxyZoo2/data/ClassificationGZ2_sample100.fits'
# #filename = '/Users/spb/Work/projects/GalaxyZoo2/data/ClassificationGZ2_sample20.fits'

# classifications = pyfits.getdata(filename, 'CLASSIFICATIONS')
# qanda = pyfits.getdata(filename, 'QANDA')
