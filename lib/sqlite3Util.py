

#author: june


import sqlite3
import globals as G


########################################################################
class Sqlite3Util:
    """"""

    #----------------------------------------------------------------------
    def __init__(self, path):
        """Constructor"""
        #db path
        self.db_path = path
        #conn obj
        self.conn = sqlite3.connect(self.db_path)
        #cursor obj
        self.c = self.conn.cursor()
        
        
        
    #----------------------------------------------------------------------
    def list_tables(self):
        """"""
        cmd = "select name from sqlite_master where type = 'table'"
        try:
            self.c.execute(cmd)
        except:
            G.log(G.INFO, 'Select \'{}\' failed!File maybe encrypt.'.format(self.db_path))
            return None
        
        
        return self.c.fetchall()
    
    
    
    #----------------------------------------------------------------------
    def select_all(self, tablename):
        """"""
        
        cmd = "select * from {} ".format(tablename)
        field = []
        records = []
        try:
            self.c.execute(cmd)
            records = self.c.fetchall()
            field = [i[0] for i in self.c.description]
        except:
            idx = self.db_path.rfind('/') + 1
            G.log(G.ERROR, 'Fail to check db_file:\'{}\' on table: \'{}\''.format(self.db_path[idx:], tablename))
        
        s = "({})".format(", ".join(field))
        #records2 = [dict(zip(field,i)) for i in records]
        
        result = list()
        result.append(s)
        result.extend(records)
        
        return result#self.c.fetchall()
    

    #----------------------------------------------------------------------
    def select_pattern_in_tablename(self, tablename, pattern):
        """"""
        cmd = "select * from {} where "
    
    
    #----------------------------------------------------------------------
    def dump_db(self):
        """"""
        return self.conn.iterdump()
    
    
    #----------------------------------------------------------------------
    def close(self):
        """"""
        self.conn.close()
    
    
    