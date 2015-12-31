#!/usr/bin/env python
############################################################################
# Copyright (C) 2015 Jon Stephan - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Jon Stephan <jfstepha@gmail.com>, 2015
############################################################################

import socket
import sys

import unittest
import time

PORT=5011
ADDRESS = "localhost"



class Client( object ):
    rbufsize= -1
    wbufsize= 0

    def makeRequest( self, text ):
        """send a message and get a 1-line reply"""
        self.server=socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.server.connect( (ADDRESS, PORT) )
        self.rfile = self.server.makefile('rb', self.rbufsize)
        self.wfile = self.server.makefile('wb', self.wbufsize)
        self.wfile.write( text + '\n' )
        data= self.rfile.read()
        self.server.close()
        return data
    
############################################################################
class TestStringMethods(unittest.TestCase):
############################################################################
    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')
        

############################################################################
class TestClient(unittest.TestCase):
############################################################################
    def __init__(self, *args, **kwargs):
        super(TestClient,self).__init__(*args, **kwargs)
        self.c=Client()

    def test_connect(self):
        response= self.c.makeRequest( "FICS_startup")
        self.assertEqual(response, "FICS_startup_rcok")

    def test_unknown_user(self):
        response = self.c.makeRequest("user_login: testuser")
        self.assertEqual(response, "Hello new user testuser\n");
        response = self.c.makeRequest("user_login: testuser")
        self.assertEqual(response, "Welcome back testuser")
        response = self.c.makeRequest("delete_user: testuser")
        self.assertEqual(response, "user testuser deleted<end>");
        response = self.c.makeRequest("user_login: testuser")
        self.assertEqual(response, "Hello new user testuser\n");
        response = self.c.makeRequest("delete_user: testuser")
        self.assertEqual(response, "user testuser deleted<end>");

    def test_known_user(self):
        response = self.c.makeRequest("user_login: jfstepha")
        self.assertEqual(response, "Welcome back jfstepha")

    def test_unknown_command(self):
        response = self.c.makeRequest("test\n")
        self.assertEqual(response, "unknown command<end>")

    def test_del_unknown_user(self):
        response = self.c.makeRequest("delete_user: stupid")
        self.assertEqual(response, "unknown user stupid<end>")

    def test_check_seek_invalid_game(self):
        response = self.c.makeRequest("seek: \n<s> 0 w=jfstepha ti=00 rt=0 t=2 i=12 r=r tp=stupid c=W rr=0-9999 a=t f=f\n\n'")
        self.assertEqual(response,"unknown_game<end>")

    def test_check_seek_locked_game(self):
        response = self.c.makeRequest("seek: \n<s> 0 w=jfstepha ti=00 rt=0 t=2 i=12 r=r tp=blitz c=W rr=0-9999 a=t f=f\n\n'")
        self.assertEqual(response, "seek:not_ach something<end>")

    def test_check_seek_unlocked_game(self):
        response = self.c.makeRequest("seek: \n<s> 0 w=jfstepha ti=00 rt=0 t=2 i=12 r=r tp=konly c=W rr=0-9999 a=t f=f\n\n'")
        self.assertEqual(response, "seek_ok<end>")
        
    def test_check_ach_get(self):
        response = self.c.makeRequest("user_login: testuser")
        self.assertEqual(response, "Hello new user testuser\n");
        response = self.c.makeRequest("game_end_white: \n{Game 1 (testuser vs. randomkvkbot) ranndomkvkbot resigns} 1-0\n\n")
        self.assertEqual(response,"ach_get:")
        response = self.c.makeRequest("delete_user: testuser")
        self.assertEqual(response, "user testuser deleted<end>");

if __name__ == '__main__':
    unittest.main()