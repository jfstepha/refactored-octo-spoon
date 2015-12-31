 

##########################################################################
##########################################################################
class User( ):
    ''' This is the main user database
    it contains the list of users, and summary data
    there is another table that keeps track of which 
    achs they have'''
##########################################################################
##########################################################################
    def __init__(self, parent, tablename, doload=True):
        self.s = parent
        self.isloaded = False
        self.tablename = tablename
        self.table_col_names = [ 'ID', 'username', 'XP', 'level']
        self.table_col_types = { "ID":"int",
                            "username":"char(80)",
                            "XP":"int",
                            "level":"int"
                            }
        self.user_defaults = { 
                            "username":"myname",
                            "XP":"0",
                            "level":"1"
                            }
        self.user_ary = []
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
            retval = self.add_user_to_struct( t )
            if retval != self.s.SUCCESS:
                return retval
        return self.s.SUCCESS

    ################################################################
    def add_table_columns(self):
    ################################################################
        for colname in self.table_col_names:
            if colname == "ID":
                continue
            coltype = self.table_col_types[ colname ]
            retval = self.s.add_column( self.tablename, colname, coltype )
            if retval != self.s.SUCCESS:
                return retval
        self.db_in_sync = False
        return self.s.SUCCESS

    ################################################################
    def check_table_columns(self):
    ################################################################
        for colname in self.table_col_names:
            retval = self.s.column_exists( self.tablename, colname)
            if retval != True:
                self.s.logger.error("Column %s does not exist" % colname)
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
    def add_user_to_struct(self, values):
    ################################################################
        self.db_in_sync = False
        if type( values ) == type( {'a':1} ):
            # set defaults
            v = {}
            for key,value in self.user_defaults.iteritems():
                if key not in self.table_col_names:
                    self.s.logger("unrecognized value: %s" %key)
                    return self.s.FAIL
                v[key] = value
            # now set passed in values
            for key,value in values.iteritems():
                if key not in self.table_col_names:
                    self.s.logger("unrecognized value: %s" %key)
                    return self.s.FAIL
                v[key] = value
            self.user_ary.append( v )
            return self.s.SUCCESS
        elif type( values ) == type( (0,1,2) ):
            i = 0
            v = self.user_defaults
            for colname in self.table_col_names:
                v[colname] = values[i]
                i += 1
            self.user_ary.append( v )
            return self.s.SUCCESS
        else:
            self.s.logger("incorrect type: need a dict")
            return self.s.FAIL

    ################################################################
    def add_user_to_table(self, values):
    ################################################################
        self.db_in_sync = False
        if type( values ) == type( {'a':1} ):
            v = {}
            # set defaults
            for key,value in self.user_defaults.iteritems():
                if key not in self.table_col_names:
                    self.s.logger("unrecognized value: %s" %key)
                    return self.s.FAIL
                v[key] = value
            # now set passed in values
            for key,value in values.iteritems():
                if key not in self.table_col_names:
                    self.s.logger("unrecognized value: %s" %key)
                    return self.s.FAIL
            v[key] = value
            status = self.s.add_row( self.tablename, v)
            return status
        elif type( values ) == type( (0,1,2) ):
            i = 0
            v = {}
            for colname in self.table_col_names:
                v[colname] = values[i]
                i += 1
            status = self.s.add_row( self.tablename, v)
            return status
        else:
            self.s.logger("incorrect type: need a dict or array")
            return self.s.FAIL

    ################################################################
    def get_user_by_name(self, name):
    ################################################################
        self.s.logger.debug("looking up %s. user name array is %d long" % (name,len(self.user_ary) ) )
        for user in self.user_ary:
            self.s.logger.debug("   user: %s" % str(user))
            if "username" not in user.keys():
                self.s.logger.error("name not in array %s" % str(user) )
                return self.s.FAIL 
            self.s.logger.debug("checking %s" % user['username'])
            if user['username'] == name:
                return user
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
                            "username":"jfstepha",
                            "XP":"0",
                            "level":"1"
                            } )
        if status != self.s.SUCCESS:
            return status
        status = self.s.add_row( self.tablename, { 
                            "username":"randomkvkbot",
                            "XP":"0",
                            "level":"1"
                            })
        if status != self.s.SUCCESS:
            return status
        status = self.s.add_row( self.tablename, { 
                            "username":"testuser",
                            "XP":"0",
                            "level":"1"
                            })
        if status != self.s.SUCCESS:
            return status
        
        return self.s.SUCCESS


    
    