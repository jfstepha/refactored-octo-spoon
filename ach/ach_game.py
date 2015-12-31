 

##########################################################################
##########################################################################
class GameAchs( ):
    ''' This is the man Game Achievements object
    it contains the entire list of types of game achievements
    and mirrors the gameach table'''
##########################################################################
##########################################################################
    def __init__(self, parent, tablename, doload=True):
        self.s = parent
        self.isloaded = False
        self.tablename = tablename
        self.table_cols = { "ID":"int",
                            "ach_name":"char(80)",
                            "description":"varchar(255)",
                            "type":"char(80)",
                            "criteria":"varchar(255)",
                            "user_announcement":"varchar(255)",
                            "repeating":"binary(1)",
                            "XP":"int",
                            "level":"int",
                            "next":"char(80)"
                            }
        self.ach_ary = []
        if doload:
            self.load()
    
    ################################################################
    def load(self): 
        ''' loads the structure from the database '''
    ################################################################
        if self.s.table_exists( self.tablename ) == False:
            self.s.logger.error("ERROR: %s table does not exist in %s" %( self.tablename, self.s.database ))
            return self.s.FAIL_TABLE_NOTEXISTS
        qstring = "SELECT * FROM %s ;" % self.tablename
        r = self.s.submit_query( qstring )
        self.s.logger.debug( "query returned: %s" % str(r))
        for t in r:
            retval = self.add_ach_to_struct( t )
            if retval != self.s.SUCCESS:
                return retval
        return self.s.SUCCESS

    ################################################################
    def add_table_columns(self):
    ################################################################
        for key,value in self.table_cols.iteritems():
            if key == "ID":
                continue
            retval = self.s.add_column( self.tablename, key, value)
            if retval != self.s.SUCCESS:
                return retval
        self.db_in_sync = False
        return self.s.SUCCESS

    ################################################################
    def check_table_columns(self):
    ################################################################
        for key,value in self.table_cols.iteritems():
            retval = self.s.column_exists( self.tablename, key)
            if retval != True:
                self.s.logger.error("Column %s does not exist" % key)
        return self.s.SUCCESS

    ################################################################
    def create_empty_table(self):
    ################################################################
        if self.s.table_exists( self.tablename ):
            self.s.logger.error("Trying to create a table that already exsists")
            return self.s.FAIL_TABLE_EXISTS 
        status = self.s.create_table( self.tablename ) 
        if status != self.s.SUCCESS:
            self.s.logger.error("Create table returned %d" % status)
            return status
        self.db_in_sync = False
        return status

    ################################################################
    def add_ach_to_struct(self, values):
    ################################################################
        self.db_in_sync = False
        if type( values ) == type( {'a':1} ):
            for key,value in values.iteritems():
                if key not in self.table_cols:
                    self.s.logger("unrecognized value: %s" %key)
                    return self.s.FAIL
            self.ach_ary.append( values )
            return self.s.SUCCESS
        elif type( values ) == type( (0,1,2) ):
            i = 0
            v = {}
            for key in self.table_cols:
                v[key] = values[i]
                i += 1
            self.ach_ary.append( values )
            return self.s.SUCCESS
        else:
            self.s.logger("incorrect type: need a dict")
            return self.s.FAIL

    ################################################################
    def get_ach_by_name(self, name):
    ################################################################
        for ach in self.ach_ary:
            if "ach_name" not in ach.keys():
                self.s.logger.error("name not in ach %s" % ach)
                return self.s.FAIL 
            if ach['ach_name'] == name:
                return ach
        return self.s.FAIL
    
    ################################################################
    def create_example_table(self):
    ################################################################
        if self.s.table_exists( self.tablename ):
            self.s.logger.error("Trying to create a table that already exsists")
            return self.s.FAIL_TABLE_EXISTS 
        status = self.s.create_table( self.tablename ) 
        self.db_in_sync = False
        if status != self.s.SUCCESS:
            self.s.logger.error("Create table returned %d" % status)
            return status
        
        status = self.add_table_columns()
        if status != self.s.SUCCESS:
            self.s.logger.error("Add table columns returned %d" % status)
            return status
        
        status = self.s.add_row( self.tablename, { 
                            "ach_name":"first login",
                            "description":"Login to this server for the first time",
                            "type":"login" ,
                            "criteria":"",
                            "user_announcement":"Welcome to the server!",
                            "repeating":"0",
                            "XP":"10",
                            "level":"0",
                            "next":"kvk_win"
                            } )
        if status != self.s.SUCCESS:
            return status
        status = self.s.add_row( self.tablename, { 
                            "ach_name": "kvk_win",
                            "description":"Win a king vs. king game" ,
                            "type":"win",
                            "criteria":"onlyk",
                            "user_announcement":"Congratulations on wining your first game!",
                            "repeating":"0",
                            "XP":"10",
                            "level":"0",
                            "next":""
                            })
        if status != self.s.SUCCESS:
            return status
        
        return self.s.SUCCESS


    
    