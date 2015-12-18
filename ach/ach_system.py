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
#from msilib import Table

PORT=5011

##########################################################################
##########################################################################
class AchServer( ):
    """ The  acheivement server class """
##########################################################################
##########################################################################
    def __init__(self):
        FORMAT = '%(asctime)-15s - %(levelname)-8s-%(funcName)s - %(message)s'
        logging.basicConfig(format=FORMAT, level=logging.DEBUG)
        self.logger = logging.getLogger()
        self.logger.debug("AchServer starting up")
        self.con=[]
        self.connect_to_mysql()
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.con.close()

    ################################################################
    def connect_to_mysql(self):
    ################################################################
        self.con = _mysql.connect('localhost','chess','chess_pwd','whfchess')
    ################################################################
    def get_login_string(self, username):
    ################################################################
        return "Welcome back %s" % username
        pass
    ################################################################
    def submit_query(self, query_str):
    ################################################################
        self.logger.debug("query %s", query_str)
        self.con.query(query_str)
        result = self.con.use_result()
        if result:
            result_rows = result.fetch_row()
            self.logger.debug( "returned:%s" % str(result_rows))
            if len(result_rows) <= 0:
                self.logger.debug("query came up empty")
                return ""
            else:
                return(result_rows)
        else:
            return ""

    ################################################################
    def user_exists(self,username):
    ################################################################
        self.logger.debug("username searching for %s"%username)
        result = self.submit_query("select * from users where username='%s'" % username)
        if len(result) == 0:
            self.logger.debug("username query came up empty")
            return False
        
        # check for the user achievement table
        result = self.submit_query("show tables like 'ach_%s'" % username)
        if len(result) <= 0:
            self.logger.debug("username ach query came up empty")
            return False
        
        return True

    ################################################################
    def new_user(self,username):
    ################################################################
        self.logger.info("adding user %s" % username)
        
        self.submit_query("insert into users ( username,xp,level) values( '%s', 0, 1);" % username)  ## add user to the main user table 
        result = self.submit_query("select * from users where username='%s'" % username) ## check to make sure it was successful
        if len(result) == 0:
            self.logger.debug("username query came up empty")
            return ""
        
        
        self.submit_query("create table ach_%s (ach_name char(80), ach_no int);" % username) ## add the user achievement table
        result=self.submit_query("show tables like 'ach_%s'" % username) ## check to make sure the table was created
        if len(result) == 0:
            self.logger.debug("username query came up empty")
            return ""
        
        
        self.submit_query("insert into ach_%s (ach_name, ach_no) values ('first login', 1);" % username) ## add the first achievement
        result = self.submit_query("select * from ach_%s ;" % username) ## check to make sure the rows were added
        if len(result) == 0:
            self.logger.debug("ach row query came up empty")
            return ""
        
        return "Hello new user %s\n" % username
    
    ################################################################
    def delete_user(self,username):
    ################################################################
        self.logger.info("deleting user %s" % username)
        
        self.submit_query("DELETE FROM users WHERE username='%s';" % username) # delete the user from te user Table
        result = self.submit_query("SELECT * FROM users WHERE username='%s';" % username) # check to make sure user has actually been deleted
        if len(result) > 0:
            self.logger.error("username still exists in user table;")
            return "fail: user still in user table after delete"
        
        self.submit_query("DROP TABLE ach_%s;" % username) 
        result = self.submit_query("show tables like 'ach%s';" % username)
        if len(result) > 0:
            self.logger.error("username ach table still exists after deleting")
            return "fail: user ach table still exists after delete"
        
        return "user %s deleted<end>" % username

    ################################################################
    def check_seek(self,seekstr):
        self.logger.info("checking seek %s" % seekstr)
        seek_ary = seekstr.split()

        #### find username #####
        username = ""
        for index, item in enumerate(seek_ary):
            if item[0:2] == "w=":
                username = item[2:]
                break
            
        if username == "":
            return ("seek:username not found in seek string")
        
        #### find game type #####
        board = ""
        for index, item in enumerate( seek_ary ):
            if item[0:3] == "tp=":
                board = item[3:]
        if board == "":
            return("seek:board not found in seek string")
        
        #### look up the game in the gametypes table ####
        result = self.submit_query("SELECT * FROM gametypes WHERE name='%s';" % board)
        if len(result) == 0:
            return("unknown_game<end>")
        
        unlocked_by = result[0][2]
        self.logger.debug("board %s is unlocked by %s" % (board, unlocked_by))
        
        #### look up to see if the user has that ach
        result = self.submit_query("SELECT * FROM ach_%s WHERE ach_name='%s';" % (username, unlocked_by))
        if len(result) == 0:
            return ("seek:not_ach %s<end>" % unlocked_by)

        return( "seek_ok<end>" )


            
        
        

ach_server = AchServer()

##########################################################################
##########################################################################
class MySocketServer( SocketServer.StreamRequestHandler ):
    """ The  acheivement server class """
##########################################################################
##########################################################################
    def handle(self):
        global ach_server
        input= self.request.recv(1024)
        ach_server.logger.debug("Received: %r" % ( input, ) )

        ###########################################
        if input.find("FICS_startup") > -1:
            ach_server.logger.info( "recieved FICS startup %r" % ( input, ) )
            self.request.send("FICS_startup_rcok")
            return

        ###########################################
        if input.find("user_login:") == 0:
            (token, username) = input.split( )
            ach_server.logger.info( "recieved user login %r" % ( username ) )
            if ach_server.user_exists( username  ):
                ach_server.logger.debug( "user exists, getting login string")
                msg = ach_server.get_login_string( username )
            else:
                ach_server.logger.debug( "user %s does not exist, creating" % username )
                msg = ach_server.new_user( username )
            self.request.send(msg)
            return

        ###########################################
        if input.find("delete_user:") == 0:
            (token, username) = input.split( )
            ach_server.logger.info( "recieved delete user %r" % ( username ) )
            if ach_server.user_exists( username  ):
                ach_server.logger.debug( "user exists, deleting him")
                msg = ach_server.delete_user( username )
            else:
                ach_server.logger.debug( "user %s does not exist" % username )
                msg = "unknown user %s<end>" % username
            self.request.send(msg)
            return

        ###########################################
        if input.find("seek:") == 0:
            ach_server.logger.info("recived seek: %s" % input )
            ret = ach_server.check_seek( input )
            if ret == "seek_ok":
                ach_server.logger.debug("seek OK")
                msg = "seek_ok<end>"
            else:
                ach_server.logger.info("seek not OK: %s" % ret)
                msg = ret;
                
            self.request.send( msg )
            return
                

        self.request.send("unknown command<end>")
            



##########################################################################
def main():
##########################################################################
    server= SocketServer.TCPServer( ("",PORT), MySocketServer)
    print "Starting Server"
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    print "ctrl-c, shutting down"
    server.server_close()

##########################################################################
if __name__ == "__main__":
    main()
