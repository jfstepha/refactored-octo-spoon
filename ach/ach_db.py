#!/usr/bin/python

############################################################################
# Copyright (C) 2015 Jon Stephan - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Jon Stephan <jfstepha@gmail.com>, 2015
############################################################################

import SocketServer
import logging
import _mysql
from json.decoder import WHITESPACE
import datetime
import os
import subprocess
import ach_game
import ach_user

#from msilib import Table
##########################################################################
##########################################################################
class AchDBServer():
##########################################################################
    def __init__(self, server='localhost', database='whfchess', username='chess', password='chess_pwd',
                 gameach_load=True, gameach_table='gameach',
                 user_load=False, user_table='users'):
        ### constants ###
        self.SUCCESS = 0
        self.ERROR = 1                # geric error, where something unexpected happend
        self.FAIL = 2                 # table operation failed
        self.FAIL_TABLE_NOTEXISTS = 3 # the table does not exist
        self.FAIL_TABLE_EXISTS = 4    # if you try to create a table that already exists
        self.FAIL_COLUMN_NOTEXISTS = 5 # if the column doesn't exist
        self.FAIL_COLUMN_EXISTS = 6    #

        FORMAT = '%(asctime)-15s - %(levelname)-8s-%(funcName)s - %(message)s'
        logging.basicConfig(format=FORMAT, level=logging.DEBUG)
        self.logger = logging.getLogger()
        self.logger.debug("AchDBServer starting up")
        
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        
        self.isconnected = False
        self.con = []
        self.connect()
        self.ga = ach_game.GameAchs(self, tablename=gameach_table, doload=gameach_load)
        self.u = ach_user.User(self, tablename=user_table, doload=user_load)
        
    ################################################################
    def connect(self):
    ################################################################
        self.con = _mysql.connect(self.server,self.username,self.password,self.database)
#        print("self.con: %s" % self.con)
        self.isconnected = True

    ################################################################
    def load_tables(self):
    ################################################################
        pass
        
    ################################################################
    def submit_query(self, query_str):
    ################################################################
        self.logger.debug("query %s", query_str)
        self.con.query(query_str)
        result = self.con.store_result()
        if result:
            result_rows = result.fetch_row(0)
            self.logger.debug( "returned:%s" % str(result_rows))
            if len(result_rows) <= 0:
                self.logger.debug("query came up empty")
                return ""
            else:
                return(result_rows)
        else:
            return ""

        
    ################################################################
    def table_exists(self, tablename):
    ################################################################
        result = self.submit_query("show tables like '%s';" % tablename)
        if len(result) <= 0:
            self.logger.debug("username ach query came up empty")
            return False
        return True
    
    ################################################################
    def create_table(self, tablename):
    ################################################################
        if self.table_exists(tablename):
            self.logger.error("Table %s exists" % tablename)
            return self.FAIL_TABLE_EXISTS
        self.submit_query("create table %s (ID int AUTO_INCREMENT, PRIMARY KEY (ID));" % tablename) ## add the user achievement table
        result=self.submit_query("show tables like '%s';" % tablename) ## check to make sure the table was created
        if len(result) == 0:
            self.logger.debug("table creation failed")
            return self.FAIL
        return self.SUCCESS

    ################################################################
    def delete_table(self, tablename):
    ################################################################
        if self.table_exists( tablename ) == False:
            self.logger.debug("Table %s does not exist" % tablename)
            return self.FAIL_TABLE_NOTEXISTS
        self.submit_query("DROP TABLE %s;" % tablename) 
        result = self.submit_query("show tables like '%s';" % tablename)
        if len(result) > 0:
            self.logger.error("username ach table still exists after deleting")
            return self.FAIL
        return self.SUCCESS
    ################################################################
    def column_exists(self, tablename, colname):
    ################################################################
        if self.table_exists( tablename ) == False:
            self.logger.debug("Table %s does not exist" % tablename)
            return self.FAIL_TABLE_NOTEXISTS
        retval = self.submit_query( "SELECT * FROM information_schema.COLUMNS " +
                                      "WHERE TABLE_SCHEMA = '%s' " % self.database + 
                                       " AND TABLE_NAME = '%s' " % tablename +
                                       " AND COLUMN_NAME = '%s';" % colname)
        if retval == "":
            return False
        else:
            return True

        return self.FAIL 
        
    
    ################################################################
    def add_column(self, tablename, colname, coltype):
    ################################################################
        if self.table_exists(tablename) == False:
            self.logger.debug("Table %s does not exist" % tablename)
            return self.FAIL_TABLE_NOTEXISTS
        retval = self.submit_query("ALTER TABLE %s ADD %s %s ;" %(tablename, colname, coltype))
        if self.table_exists(tablename):
            return self.SUCCESS
        return self.FAIL

    ################################################################
    def del_column(self, tablename, colname):
    ################################################################
        if self.table_exists(tablename) == False:
            self.logger.debug("Table %s does not exist" % tablename)
            return self.FAIL_TABLE_NOTEXISTS
        if self.column_exists(tablename, colname) == False:
            self.logger.debug("Column %s does not exist" % colname)
            return self.FAIL_COLUMN_NOTEXISTS
        retval = self.submit_query("ALTER TABLE %s DROP COLUMN %s; " % (tablename, colname))
        if retval == "":
            return self.SUCCESS
        return self.FAIL

    ################################################################
    def add_row(self, tablename, rowvals=[]):
    ################################################################
        if rowvals == []:
            self.logger.error("rowvalues must be specified")
            return self.FAIL
        self.logger.debug("rowvals type: %s " % type(rowvals))
        if type( rowvals ) == type( {'a':'1'} ):
            qstring = "INSERT INTO %s (" % tablename
            qstring += " , " . join( "%s" % key for key,value in rowvals.iteritems())
            qstring += ") VALUES ("
            qstring += ','.join( "'%s'" % value for key,value in rowvals.iteritems())
            qstring += ");"
        else:
            qstring = "INSERT INTO %s VALUES (" % tablename
            qstring = qstring + ','.join( "'%s'" % str(it) for it in rowvals)
            qstring = qstring + ");"
        self.logger.debug("query string: %s" % qstring)
            
        retval = self.submit_query(qstring)
        if retval == "":
            return self.SUCCESS
            
        return self.FAIL
    ################################################################
    def del_row(self, tablename, matches):
    ################################################################
        qstring = "DELETE FROM %s WHERE " % tablename
        qstring += " AND ".join( "%s='%s'" % (key,value) for key,value in matches.iteritems() )
        qstring += ";"
        retval = self.submit_query(qstring)
        if retval == "":
            return self.SUCCESS
        return self.FAIL

    ################################################################
    def get_row(self, tablename, matches):
    ################################################################
        qstring = "SELECT * FROM %s WHERE " % tablename
        qstring += " AND ".join( "%s='%s'" %(key,value) for key, value in  matches.iteritems() )
        qstring += ";"
        retval = self.submit_query(qstring)
        if retval == "":
            return self.FAIL
        return retval

    ################################################################
    def set_val(self, tablename, values, matches):
    ################################################################
        qstring = "UPDATE %s SET " % tablename
        qstring += " AND ".join( "%s='%s'" %(key,value) for key,value in values.iteritems())
        qstring += " WHERE "
        qstring += " AND ".join( "%s='%s'" %(key,value) for key,value in matches.iteritems())
        qstring += ";"
        retval = self.submit_query(qstring)
        if retval == "":
            return self.SUCCESS
        return self.FAIL
            
    ################################################################
    def get_val(self, tablename, colname, matches):
    ################################################################
        qstring = "SELECT %s FROM %s" % (colname, tablename)
        qstring += " WHERE "
        qstring += " AND ".join( "%s='%s'" % (key,value) for key,value in matches.iteritems() )
        qstring += ";"
        retval = self.submit_query(qstring)
        if retval == "":
            return self.FAIL
        return retval[0][0]

    ################################################################
    def save_table_to_csv(self, tablename, filename, autodate=True, overwrite=False):
    ################################################################
        filename2=filename
        if autodate:
            filename2 = filename + "_%s" % datetime.datetime.now().strftime("%Y_%m_%d_%I_%M_%s")
        if overwrite:
            if os.path.isfile( filename2 ):
                os.remove( filename2 )
        qstring = "SELECT * FROM %s INTO OUTFILE '%s' " % (tablename, filename2)
        qstring += " FIELDS TERMINATED BY ','"
        qstring += ";"
        retval = self.submit_query(qstring)
        if retval == "":
            return self.SUCCESS 
        return self.FAIL

    ################################################################
    def save_table_to_file(self, tablename, filename, autodate=True, overwrite=False):
    ################################################################
        filename2=filename
        if autodate:
            filename2 = filename + "_%s" % datetime.datetime.now().strftime("%Y_%m_%d_%I_%M_%s")
        if overwrite:
            if os.path.isfile( filename2 ):
                os.remove( filename2 )
        qstring = "/usr/bin/mysqldump -u %s -p%s %s %s > %s" % (self.username, self.password, self.database, tablename, filename2)
        self.logger.debug("command:%s" % qstring)
        retval = os.system( qstring )
        if retval == 0:
            return self.SUCCESS
        self.logger.error("os dump returned %s" % retval)
        return self.FAIL

    ################################################################
    def load_table_from_file(self, tablename, filename):
    ################################################################
        qstring = "/usr/bin/mysql -h %s" % self.server
        qstring += " -u %s" % self.username
        qstring += " -p%s" % self.password
        qstring += " %s" % self.database
        qstring += " < %s" % filename
        retval = os.system( qstring )
        if retval == 0:
            return self.SUCCESS
        return self.FAIL
        
            
             

    ################################################################
    def __exit__(self, exc_type, exc_value, traceback):
    ################################################################
        self.con.close()
       