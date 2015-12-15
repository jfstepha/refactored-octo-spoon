#!/usr/bin/python

############################################################################
# Copyright (C) 2015 Jon Stephan - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Jon Stephan <jfstepha@gmail.com>, 2015
############################################################################

import getpass
import sys
import telnetlib
import string
import time

#####################################################
#####################################################
class BotTelnet:
#####################################################
#####################################################

    ################################################
    def __init__(self, host):
    ################################################
        print "initializing BotTelnt"
        self.host=host
        self.prompt = 'fics% '
        self.timeout = 2

    ################################################
    def connect(self, username, password):
    ################################################
        self.username = username
        print "connecting to server %s username:%s" % (self.host, username)
        self.tn = telnetlib.Telnet( self.host, 5000 )
        # self.tn.write("vt100\n")
        print "  wating for login prompt..."
        rec = self.tn.read_until( "login: ", 5 )
        print "  recieved: %s" % rec
        print "  sending username... %s" % username
        self.tn.write( username + "\n" )
        print "  waiting for password prompt..."
        rec = self.tn.read_until( "password:", self.timeout)
        print "  received: %s" % rec
        if rec.find(" is a registered name") == -1:
            print "  unknown username"
            raise Exception("tenet_login","bad username")
        print "  sending password %s ..." % password
        self.tn.write( password + "\n" )
        rec = self.tn.read_until( self.prompt, self.timeout)
        print "  received: %s" % rec
        if rec.find( self.prompt ) > -1:
            print "  logged in"
        else:
            print "  loggin unsuccessful"
            raise Exception("telnet_login","unsuccessful")
        print "  setting style"
        self.tn.write("set style 12\n")
        rec = self.tn.read_until( self.prompt, self.timeout )
        if rec.find( "Style 12 set" ) == -1:
            print "    style set unsuccessful"
            raise Exception("telnet_login", "style set unsuccessful")
            

    ################################################
    def seek( self, seek_time, seek_inc, seek_rated, seek_board,
              seek_auto, seek_formula, seek_rating):
    ################################################
        print "BotTelnet seeking game..."
        self.tn.read_until("neverfind",1)
        self.tn.write( "seek " + str(seek_time) + " " + str(seek_inc) + " " + seek_rated + " " +
                        seek_board + " " + seek_auto + " " + seek_formula + " " + seek_rating + "\n" )
        rec = self.tn.read_until( self.prompt, self.timeout )
        print "  received: %s" % rec
        if rec.find( self.username) == -1 or rec.find( str(seek_time) ) == -1 or rec.find( str( seek_inc ) ) == -1 or rec.find( seek_rated) == -1 :
            print "   failed to find seek confirmation"
            raise Exception("telent_seek", "seek unsuccessful")
        if rec.find( self.prompt ) == -1:
            print "   did not return to prompt"
            raise Exception("telnet_seek", "noprompt")
        print "  seek submitted successfully"

    ################################################
    def waitForGame( self ):
    ################################################
        print "BotTenet waiting for game..."
        rec = ""
        while rec.find( "accepts your challenge" ) < 0: 
            rec = self.tn.read_until( self.prompt, self.timeout )
            if len(rec) > 0:
                print "  recieved: %s" % rec
        if rec.find( "accepts your challenge" ) < 0:
            print "Loop ended, but challenge not accepted"
            raise Exception("telnet_wait_for_game","not_accepted")
        
        print "   waiting for creating line"
        while rec.find( "Creating:") < 0:
            rec = self.tn.read_until( self.prompt, self.timeout )
            if len(rec) > 0:
                print "  recieved: %s" % rec
                
        if rec.find("Creating:") < 0:
            print "Loop ended, but creating line not found"
            raise Exception("telnet_wait_for_game","not created")
       
        unameloc = rec.find(" "+self.username+" ") 
        createloc = rec.find("Creating:")
        print " found username at %d and creating at %d" % ( unameloc, createloc )

        if unameloc - createloc > 9:
            self.side = "black"
            self.myturn = False
        else:
            self.side = "white"
            self.myturn = True
        startofleftover = rec.find( "\n", createloc)
        print "  bot playing %s" % self.side
        return( rec[startofleftover:len(rec)])
    ################################################
    def chompFenDashes(self, r):
    ################################################
        while r.find("-") > -1:
                #print "while r.find, r=%s"%r
                # find the first non-space
                first_space = r.find("-")
                l = len(r)
                j = first_space + 1
                while j < l and r[j] == "-":
                    #print "while j < 8, j=%d" % j
                    j = j + 1
                spaces = j - first_space
                
                r_tmp = ""
                if first_space > 0:
                    r_tmp = r[0:first_space]
                r_tmp = r_tmp + str(spaces)
                if j < l:
                    r_tmp = r_tmp + r[j:l]
                #print "r_tmp=%s" % r_tmp
                r = r_tmp
        return(r)

    ################################################
    def chompFenSpaces(self, r):
    ################################################
        while r.find(" ") > -1:
                #print "while r.find, r=%s"%r
                # find the first non-space
                first_space = r.find(" ")
                l = len(r)
                j = first_space + 1
                while j < l and r[j] == " ":
                    #print "while j < 8, j=%d" % j
                    j = j + 1
                spaces = j - first_space
                
                r_tmp = ""
                if first_space > 0:
                    r_tmp = r[0:first_space]
                r_tmp = r_tmp + str(spaces)
                if j < l:
                    r_tmp = r_tmp + r[j:l]
                #print "r_tmp=%s" % r_tmp
                r = r_tmp
        return(r)
        
            
    ################################################
    def txtToFen_8(self, rec, side):
        ''' this is for stlye 8 '''
    ################################################
        print "converting %s to fen:" % rec
        if len(rec) < 138:
            print "improperly formatted string to convert to fen (len %d): %s" % (len(rec), rec)
            raise Exception("txtToFen","improperly formatted string")
        r = []
        for i in range(0,8):
            r.append( rec[40+i*8:48+i*8])
        white_time_left = int(rec[112:117])
        black_time_left = int(rec[117:122])
        prev_move = rec[122:129]

        #print "extracted r:" + str(r)

        ret = ""
        for i in range(7,-1,-1):
            r[i] = self.chompFenSpaces(r[i])
            ret = ret+r[i]
            if i > 0:
                ret = ret + "/"
        ret = ret + " " + side[0] + " KQkq - 0 1"
        print ret
        return (ret, white_time_left, black_time_left, prev_move)

    ################################################
    def txtToFen(self, rec, side):
        ''' this is for stlye 12 '''
    ################################################
        print "converting %s to fen:" % rec
        a = rec.split()
        if len(a) < 32:
            print "improperly formatted string to convert to fen (len %d): %s" % (len(rec), rec)
            raise Exception("txtToFen","improperly formatted string")
        if a[0] != "<12>":
            print "improperly formatted string to convert to fen (len %d): %s" % (len(rec), rec)
            raise Exception("txtToFen","improperly formatted string")
        
        # the board is in elements 1 to 8
        ret = ""
        r=[]
        for i in range(0,8):
            r.append( a[i+1] )
        for i in range(0,8):
            r[i] = self.chompFenDashes(r[i])
            ret = ret+r[i]
            if i < 7:
                ret = ret + "/"

        # element 9 is side to move
        to_move = a[9]
        ret = ret + " " + string.lower( a[9] )
       
        
        wk = int(a[11])   # can white castle king side?
        wq = int(a[12])
        bk = int(a[13])
        bq = int(a[14])
        if( wk + wq + bk + bq == 0):
            ret = ret + " -"
        else:
            ret= ret + " "
            ret = ret + "K" if wk else ""
            ret = ret + "Q" if wq else ""
            ret = ret + "k" if bk else ""
            ret = ret + "q" if bq else ""
        
        # element 10 is doubledPawn 
        ret = ret + " "
        if a[10] == "-1" or a[10] == "0":
            ret = ret + "-"
        else:
            mv = a[27]
            print "mv=" + mv
            x = string.find(mv,"/") + 1
            mv_file = mv[x]
            print "mv_file="+mv_file
            mv_from = int( mv[x+1] )
            print "mv_from="+mv[x+1]
            mv_to = int( mv[x+4] )
            print "mv_to="+str(mv_to)
            mv_rank = str( ( mv_from + mv_to ) / 2)
            ret = ret + mv_file + str(mv_rank)
            
        ret = ret + " " + a[15] # halfmoves since capture 
        ret = ret + " " + a[26] # full move number   
        
        white_time_left = int(a[24])
        black_time_left = int(a[25])
        prev_move = a[29]
                
        print ret
            
        return (ret, white_time_left, black_time_left, prev_move, to_move)
            
    ################################################
    def waitForMove ( self, leftover_text ):
    ################################################
        print "BotTenet waiting for move..."
        rec = leftover_text
        while 1:
            if rec.find('<12>') > -1:
                break
            if (rec.find('{Game') > -1 and rec.find('resigns}') > -1) :
                return( "end:resign", 0,0,"none","n")
            if (rec.find('{Game') > -1 and rec.find('checkmated}') > -1) :
                return( "end:checkmate", 0,0,"none","n")
            if (rec.find('{Game') > -1 and rec.find('adjourned}') > -1) :
                return( "end:adjourned", 0,0,"none","n")
            rec = self.tn.read_until( self.prompt, self.timeout )
            if len(rec) > 0:
                print "  recieved: %s" % rec
        rec_start = rec.find('<12>')
        rec_end = rec.find("\n", rec_start+1) 
        rec_trimmed = rec[rec_start:rec_end]
        print "sending this to txtToFen (%d to %d):%s" % (rec_start, rec_end, rec_trimmed)
        (fen, white_time_left, black_time_left,prev_move, to_move) = self.txtToFen( rec_trimmed, self.side )
        return (fen, white_time_left, black_time_left, prev_move, to_move)
    ################################################
    def sendMove(self, move):
    ################################################
        print "BotTelnet sending move %s" % move
        self.tn.write(move + "\n")
