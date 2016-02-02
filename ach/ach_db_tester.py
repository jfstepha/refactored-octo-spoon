#!/usr/bin/env python
############################################################################
# Copyright (C) 2015 Jon Stephan - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Jon Stephan <jfstepha@gmail.com>, 2015
############################################################################

import unittest
import ach_db
import ach_game 
from _sqlite3 import OperationalError
import logging

############################################################################
class TestStringMethods(unittest.TestCase):
############################################################################
    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

############################################################################
class TestServerTestDB(unittest.TestCase):
    """ Tests a blank but existing database """
############################################################################
    def __init__(self, *args, **kwargs):
        super(TestServerTestDB,self).__init__(*args, **kwargs)
        self.s = ach_db.AchDBServer(database="testdb")
        self.s.logger.level = logging.INFO

    def test_is_connected(self):
        self.assertEqual(self.s.isconnected, True)

    def test_table_notexists(self):
        self.assertEqual( self.s.table_exists("asdf"), False)

    def test_table_delete_notexists(self):
        self.assertEqual( self.s.delete_table( "asdf" ), self.s.FAIL_TABLE_NOTEXISTS )
        
    def test_insert_delete_table(self):
        self.assertEqual( self.s.create_table( "testtable" ), self.s.SUCCESS )
        self.assertEqual( self.s.table_exists( "testtable"), True)
        self.assertEqual( self.s.delete_table( "testtable" ), self.s.SUCCESS )
        self.assertEqual( self.s.table_exists( "testtable"), False)
        
############################################################################
class TestServerTestTable(unittest.TestCase):
    """ tests an existing but blank table"""
############################################################################
    def __init__(self, *args, **kwargs):
        super(TestServerTestTable,self).__init__(*args, **kwargs)
        self.s = ach_db.AchDBServer(database="testdb")
        self.s.logger.level = logging.DEBUG
        self.tablename = "testtable2"
        self.s.create_table( self.tablename )
        
    def __del__(self):
        self.s.delete_table( self.tablename )
        print "DONE"
        
    def test_exists(self):
        self.assertEqual(self.s.table_exists( self.tablename ), True)

    def test_col_exists(self):
        self.assertEqual(self.s.column_exists( self.tablename, "asdf"), False)
        
    def test_add_del_col(self):
        self.assertEqual(self.s.add_column(self.tablename, "testcol", "char(80)"), self.s.SUCCESS)
        self.assertEqual(self.s.column_exists( self.tablename, "testcol"), True)
        self.assertEqual(self.s.del_column(self.tablename, "testcol"), self.s.SUCCESS)
        self.assertEqual(self.s.column_exists( self.tablename, "testcol"), False)
        
    def test_add_row_empty_rowvals(self):
        self.assertEqual(self.s.add_column(self.tablename, "testcol2", "char(80)"), self.s.SUCCESS)
        self.assertEqual(self.s.add_row(self.tablename), self.s.FAIL)
        self.assertEqual(self.s.del_column(self.tablename, "testcol2"), self.s.SUCCESS)

    def test_add_row(self):
        self.assertEqual(self.s.add_column(self.tablename, "testcol3", "char(80)"), self.s.SUCCESS)
        self.assertEqual(self.s.add_row(self.tablename, ["1", "testval"]), self.s.SUCCESS)
        self.assertEqual(self.s.del_row(self.tablename, {"ID":"1"}), self.s.SUCCESS)
        self.assertEqual(self.s.del_column(self.tablename, "testcol3"), self.s.SUCCESS)

    def test_add_row_byname(self):
        self.assertEqual(self.s.add_column(self.tablename, "testcol3", "char(80)"), self.s.SUCCESS)
        self.assertEqual(self.s.add_row(self.tablename, {"testcol3": "testval"}), self.s.SUCCESS)
        self.assertEqual(self.s.del_column(self.tablename, "testcol3"), self.s.SUCCESS)
        
    def test_get_row(self):
        self.assertEqual(self.s.add_column(self.tablename, "testcol3", "char(80)"), self.s.SUCCESS)
        self.assertEqual(self.s.add_row(self.tablename, ["1", "testval"]), self.s.SUCCESS)
        self.assertEqual(self.s.get_row(self.tablename, {"ID":"1"}), (("1","testval"),) )
        self.assertEqual(self.s.del_row(self.tablename, {"ID":"1"}),  self.s.SUCCESS)
        self.assertEqual(self.s.del_column(self.tablename, "testcol3"), self.s.SUCCESS)

    def test_set_val(self):
        self.assertEqual(self.s.add_column(self.tablename, "testcol3", "char(80)"), self.s.SUCCESS)
        self.assertEqual(self.s.add_row(self.tablename, ["1", "testval"]), self.s.SUCCESS)
        self.assertEqual(self.s.set_val(self.tablename, {"testcol3":"newval"}, {"ID":"1"} ), self.s.SUCCESS)
        self.assertEqual(self.s.get_row(self.tablename, {"ID":"1"}), (("1","newval"),) )
        self.assertEqual(self.s.del_row(self.tablename, {"ID":"1"}), self.s.SUCCESS)
        self.assertEqual(self.s.del_column(self.tablename, "testcol3"), self.s.SUCCESS)

    def test_get_val(self):
        self.assertEqual(self.s.add_column(self.tablename, "testcol3", "char(80)"), self.s.SUCCESS)
        self.assertEqual(self.s.add_row(self.tablename, ["1", "testval"]), self.s.SUCCESS)
        self.assertEqual(self.s.get_val(self.tablename, "testcol3", {"ID":"1"}), "testval")
        self.assertEqual(self.s.del_row(self.tablename, {"ID":"1"}), self.s.SUCCESS)
        self.assertEqual(self.s.del_column(self.tablename, "testcol3"), self.s.SUCCESS)

############################################################################
class TestGameAchsTestDB(unittest.TestCase):
    """ Tests the GameAchs object, starting with a blank DB """
###########################################################################
    def __init__(self, *args, **kwargs):
        super(TestGameAchsTestDB,self).__init__(*args, **kwargs)
        self.tablename="testgameach4"
        self.s = ach_db.AchDBServer(database='testdb', gameach_load=False, gameach_table=self.tablename )
        self.s.logger.level = logging.INFO

    def __del__(self):
        self.s.delete_table( tablename = self.tablename )
        print "DONE"

    def test_isloaded(self):
        self.assertEqual( self.s.ga.isloaded, False )
    
    def test_load_notable(self):
        self.s.ga.tablename = "asdf"
        self.assertEqual( self.s.ga.load(), self.s.FAIL_TABLE_NOTEXISTS )
        self.s.ga.tablename = self.tablename
        
    def test_create_table(self):
        self.assertEqual( self.s.ga.create_empty_table(), self.s.SUCCESS)
        self.assertEqual( self.s.ga.create_empty_table(), self.s.FAIL_TABLE_EXISTS )
        self.s.delete_table( tablename = self.tablename )

    def test_add_table_columns(self):
        self.assertEqual( self.s.ga.create_empty_table(), self.s.SUCCESS)
        self.assertEqual( self.s.ga.add_table_columns(), self.s.SUCCESS)
        self.assertEqual( self.s.ga.check_table_columns(), self.s.SUCCESS)
        self.s.delete_table( tablename = self.tablename )

    def test_create_example_table(self):
        self.assertEqual( self.s.ga.create_example_table(), self.s.SUCCESS)
        self.s.delete_table( tablename = self.tablename )

    def test_save_example_table(self):
        self.assertEqual( self.s.ga.create_example_table(), self.s.SUCCESS)
        self.assertEqual( self.s.save_table_to_file( self.tablename, "/home/jfstepha/chessdb/gameach.sql"), self.s.SUCCESS)
        self.s.delete_table( tablename = self.tablename )

    def test_save_example_table_reload(self):
        self.assertEqual( self.s.ga.create_example_table(), self.s.SUCCESS)
        self.assertEqual( self.s.save_table_to_file( self.tablename, "/home/jfstepha/chessdb/gameach.sql", autodate=False, overwrite=True), self.s.SUCCESS)
        self.s.delete_table( tablename = self.tablename )
        self.assertEqual( self.s.load_table_from_file( self.tablename, "/home/jfstepha/chessdb/gameach.sql" ), self.s.SUCCESS) 
        self.s.delete_table( tablename = self.tablename )

############################################################################
class TestGameAchsExampleDB(unittest.TestCase):
    """ Tests the GameAchs object, starting with the example DB """
###########################################################################
    def __init__(self, *args, **kwargs):
        super(TestGameAchsExampleDB,self).__init__(*args, **kwargs)
        self.tablename="testgameach"
        self.s = ach_db.AchDBServer(database='testdb', gameach_load=False, gameach_table=self.tablename )
        self.s.ga.create_example_table()
        self.s.logger.level = logging.INFO

#    def __del__(self):
#        self.s.delete_table( tablename = self.tablename )
        
    def test_add_ach_to_struct(self):
        self.assertEqual( self.s.ga.add_ach_to_struct( {
                            "ach_name":"sample",
                            "description":"just a sample" ,
                            "type":"win",
                            "criteria":"crit",
                            "user_announcement":"Gratz!",
                            "repeating":"0",
                            "XP":"10",
                            "level":"0",
                            "next":"kvk_win"
                            } ) , self.s.SUCCESS)
        self.assertEqual( self.s.ga.get_ach_by_name( "sample" ) , {
                            "ach_name":"sample",
                            "description":"just a sample" ,
                            "type":"win",
                            "criteria":"crit",
                            "user_announcement":"Gratz!",
                            "repeating":"0",
                            "XP":"10",
                            "level":"0",
                            "next":"kvk_win"
                            } )
    def test_load_ach(self):
        self.assertEqual( self.s.ga.add_ach_to_struct( {
                            "ach_name":"sample",
                            "description":"just a sample" ,
                            "type":"win",
                            "criteria":"crit",
                            "user_announcement":"Gratz!",
                            "repeating":"0",
                            "XP":"10",
                            "level":"0",
                            "next":"kvk_win"
                            } ) , self.s.SUCCESS)
        self.assertEqual(self.s.ga.load(), self.s.SUCCESS)
############################################################################
class TestUserTestDB(unittest.TestCase):
    """ Tests the User object, starting with a blank DB """
###########################################################################
    def __init__(self, *args, **kwargs):
        super(TestUserTestDB,self).__init__(*args, **kwargs)
        self.tablename="testusers4"
        self.s = ach_db.AchDBServer(database='testdb', user_load=False, user_table=self.tablename )
        self.s.logger.level = logging.INFO

    def __del__(self):
        self.s.delete_table( tablename = self.tablename )
        print "DONE"

    def test_isloaded(self):
        self.assertEqual( self.s.u.isloaded, False )
    
    def test_load_notable(self):
        self.s.u.tablename = "asdf"
        self.assertEqual( self.s.u.load(), self.s.FAIL_TABLE_NOTEXISTS )
        self.s.u.tablename = self.tablename
        
    def test_create_table(self):
        self.assertEqual( self.s.u.create_empty_table(), self.s.SUCCESS)
        self.assertEqual( self.s.u.create_empty_table(), self.s.FAIL_TABLE_EXISTS )
        self.s.delete_table( tablename = self.tablename )

    def test_add_table_columns(self):
        self.assertEqual( self.s.u.create_empty_table(), self.s.SUCCESS)
        self.assertEqual( self.s.u.add_table_columns(), self.s.SUCCESS)
        self.assertEqual( self.s.u.check_table_columns(), self.s.SUCCESS)
        self.s.delete_table( tablename = self.tablename )

    def test_create_example_table(self):
        self.assertEqual( self.s.u.create_example_table(), self.s.SUCCESS)
        self.s.delete_table( tablename = self.tablename )

    def test_save_example_table(self):
        self.assertEqual( self.s.u.create_example_table(), self.s.SUCCESS)
        self.assertEqual( self.s.save_table_to_file( self.tablename, "/home/jfstepha/chessdb/users.sql"), self.s.SUCCESS)
        self.s.delete_table( tablename = self.tablename )

    def test_save_example_table_reload(self):
        self.assertEqual( self.s.u.create_example_table(), self.s.SUCCESS)
        self.assertEqual( self.s.save_table_to_file( self.tablename, "/home/jfstepha/chessdb/users.sql", autodate=False, overwrite=True), self.s.SUCCESS)
        self.s.delete_table( tablename = self.tablename )
        self.assertEqual( self.s.load_table_from_file( self.tablename, "/home/jfstepha/chessdb/users.sql" ), self.s.SUCCESS) 
        self.s.delete_table( tablename = self.tablename )

############################################################################
class TestUserExampleDB(unittest.TestCase):
    """ Tests the GameAchs object, starting with the example DB """
###########################################################################
    def __init__(self, *args, **kwargs):
        super(TestUserExampleDB,self).__init__(*args, **kwargs)
        self.tablename="testuser"
        self.s = ach_db.AchDBServer(database='testdb', user_load=False, user_table=self.tablename )
        self.s.u.create_example_table()
        self.s.logger.level = logging.DEBUG

#    def __del__(self):
#        self.s.delete_table( tablename = self.tablename )
        
    def test_add_user_to_struct(self):
        self.assertEqual( self.s.u.add_user_to_struct( {
                            "username":"sample",
                            "XP":"0" ,
                            "level":"1"
                            } ) , self.s.SUCCESS)
        self.assertEqual( self.s.u.get_user_by_name( "sample" ) , {
                            "username":"sample",
                            "XP":"0" ,
                            "level":"1",
                            } )
    def test_load_user(self):
        self.assertEqual( self.s.u.add_user_to_struct( {
                            "username":"sample",
                            "XP":"0" ,
                            "level":"1",
                            } ) , self.s.SUCCESS)
        self.assertEqual(self.s.u.load(), self.s.SUCCESS)

    def test_get_user_by_name(self):
        self.assertEqual(self.s.u.load(), self.s.SUCCESS)
        self.assertEqual( self.s.u.get_user_by_name("jfstepha"), {'username': 'jfstepha', 'XP': '0', 'ID': '1', 'level': '1'} )
        
    def test_add_user(self):
        self.assertEqual( self.s.u.add_user_to_table( {
                            "username":"sample",
                            "XP":"0" ,
                            "level":"1",
                            } ) , self.s.SUCCESS)
        
        

        

############################################################################
class TestServer(unittest.TestCase):
############################################################################
    def __init__(self, *args, **kwargs):
        super(TestServer,self).__init__(*args, **kwargs)
        self.s = ach_db.AchDBServer()


    def test_string(self):
        s = 'hello world'
        with self.assertRaises(TypeError):
          s.split(2)
    
    def test_connect_nodb(self):
        self.s.database = "asdf"
        e_num = 0
        try:
            self.s.connect()
        except Exception as e:
            e_num = e[0]
            # print "exception: %s" % str(e)
        self.assertEqual(e_num,1044)

    def test_connect_nouser(self):
        self.s.username = "asdf"
        e_num = 0
        try:
            self.s.connect()
        except Exception as e:
            e_num = e[0]
            # print "exception: %s" % str(e)
        self.assertEqual(e_num,1045)

    def test_connect_nopasswd(self):
        self.s.password = "passwd"
        e_num = 0
        try:
            self.s.connect()
        except Exception as e:
            e_num = e[0]
            # print "exception: %s" % str(e)
        self.assertEqual(e_num,1045)
            
        
############################################################################
if __name__ == '__main__':
    unittest.main()