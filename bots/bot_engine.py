#!/usr/bin/python

############################################################################
# Copyright (C) 2015 Jon Stephan - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Jon Stephan <jfstepha@gmail.com>, 2015
############################################################################

from subprocess import PIPE, Popen
import sys
import time
from threading import Thread

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names

############################################################
############################################################
class BotEngine:
############################################################
############################################################
    
    #############################################
    def myprint(self, printstr):
    #############################################
        if self.curses == True:
            self.stdscr.addstr(self.SCR_ENGINE_Y, self.SCR_ENGINE_X, printstr[0:self.SCR_ENGINE_WIDTH])
            self.stdscr.refresh()
        else:
            print(printstr)
 

    #############################################
    def enqueue_output(self, stdout, stderr, queue):
    #############################################

        for line in iter(stdout.readline, b''):
            queue.put(line)
        for line in iter(stderr.readline, b''):
            queue.put(line)
        out.close()

    #############################################
    def __init__( self, exe, startstring, uci_options, stdscr=[] ):
    #############################################
        print("Engine starting...")
        self.curses = False
        self.stdscr = stdscr
        self.SCR_ENGINE_WIDTH=180
        self.startEngine( exe, startstring, uci_options)

    #############################################
    def readRetVal( self, timeout=1 ):
    #############################################
        rcv_str = "init"
        ret = ""
        self.stdscr.addstr(self.SCR_ENGINE_Y+i, self.SCR_ENGINE_X, line)
        while len( rcv_str ) > 0:
            try: rcv_str = self.q.get(timeout=timeout)
            except Empty:
                print "no more output"
                break
            else:
                if self.curses == True:
                    #self.stdscr.addstr(self.SCR_ENGINE_Y, self.SCR_ENGINE_X, "(C):engine returned %s" % rcv_str.rstrip())
                    self.myprint("(C):engine returned %s" % rcv_str.rstrip())
                else:
                    # print "  engine returned:%s" % rcv_str.rstrip()
                    pass
                ret = ret + rcv_str
        return ret
    #############################################
    def searchRetVal( self, search_val, timeout=10 ):
    #############################################
        rcv_str = "init"
        ret = ""
        start_time = time.time()
        time.time()
        #while time.time() - start_time < timeout:
        while 1:
            #print " searching for %s..." % search_val
            try: rcv_str = self.q.get(timeout=0.1)
            except Empty:
                a=1
            else:
                self.myprint("(C):engine returned %s" % rcv_str.rstrip())
                ret = ret + rcv_str
                if rcv_str.find(search_val) > -1 :
                    return ret
        return "timeout"
        

    #############################################
    def startEngine( self, exe, startstring, uci_options ):
    #############################################
        self.myprint("startEngine")
        self.p = Popen( exe, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1, close_fds=ON_POSIX)
        self.q = Queue()
        self.t = Thread( target=self.enqueue_output, args=( self.p.stdout, self.p.stderr, self.q ) )
        self.t.daemon = True
        self.t.start()
        
        #### see if the engine actually started 
        print "    checking for engine start"
        ret = self.searchRetVal( startstring, timeout=5 )
        if ret == "timeout":
            print "engine start didn't return anything"
            raise Exception( "start engine", "no initial string" )

        #### initialize UCI mode
        print "   initializing UCI mode"
        self.p.stdin.write("uci\n");
        ret = self.searchRetVal("uciok")
        if ret == "timeout":
            print "UCI engine was not OK!"
            raise Exception( "start engine", "UCI not OK" )

        #### set UCI options
        print "    setting UCI options"
        if uci_options != "":
            self.p.stdin.write(uci_options + "\n")
        self.p.stdin.write("ucinewgame\n")
        self.p.stdin.write("isready\n")
        ret = self.searchRetVal("readyok")
        if ret == "timeout":
            print "UCI engine was not ready!"
            raise Exception("start engine", "UCI not ready")
    #############################################
    def evalPos( self, fen, movetime ):
    #############################################
        s1 = "position fen "+ fen 
        print " sending %s to the engine" % s1
        self.p.stdin.write(s1 + "\n")

        s2 = "go movetime %d" %( movetime ) 
        print " sending %s to the engine" % s2 
        self.p.stdin.write( s2 + "\n" )
        ret = self.searchRetVal("bestmove")
        if ret == "timeout":
            raise Exception("make move", "engine timed out")
          
        evalstart = ret.rfind("score cp") +9
        evalend = ret.find(" ", evalstart)
        retval = ret[evalstart:evalend]
        if ret.rfind("score mate") > evalstart:
            print "### mate in the future ###"
            retval = 10000
        print "evaluation:%s" % retval
        return(retval)
    #############################################
    def makeFirstMove( self, fen, white_time_left, black_time_left ):
    #############################################
        s1 = "position fen "+ fen 
        print " sending %s to the engine" % s1
        self.p.stdin.write(s1 + "\n")

        s2 = "go wtime %d btime %d" %( white_time_left, black_time_left) 
        print " sending %s to the engine" % s2 
        self.p.stdin.write( s2 + "\n" )
        ret = self.searchRetVal("bestmove")
        if ret == "timeout":
            raise Exception("make move", "engine timed out")
        
        movestart = ret.find("bestmove") + 9
        moveend = ret.find(" ", movestart)
        move = ret[movestart:moveend]
        print "make move %s" % move
        return(move)
    #############################################
    def makeMove( self, prev_move, white_time_left, black_time_left ):
    #############################################
        print "sending move %s to engine" % prev_move
        self.p.stdin.write("position moves "+ prev_move + "\n")
        self.p.stdin.write("go wtime %d btime %d" %( white_time_left, black_time_left) + "\n" )
        ret = self.searchRetVal("bestmove")
        if ret == "timeout":
            raise Exception("make move", "engine timed out")
        
        movestart = ret.find("bestmove") + 9
        moveend = ret.find(" ", movestart)
        move = ret[movestart:moveend]
        print "make move %s" % move
        return(move)
        




if __name__ == "__main__":
    print "Testing engine..."
    e = BotEngine()
