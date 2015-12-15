#!/usr/bin/python

############################################################################
# Copyright (C) 2015 Jon Stephan - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Jon Stephan <jfstepha@gmail.com>, 2015
############################################################################

import fileinput
import time
import sys
import chess
import random

##########################################################################
##########################################################################
class Bot:
##########################################################################
##########################################################################

    """ The main bot class """

    ##########################################################################
    def __init__(self):
    #########################################################################
        self.state = "init"

    #########################################################################
    def init_game(self):
    #########################################################################
        self.state = "init"

    #########################################################################
    def generate_move(self, line):
    #########################################################################
        lm_obj = self.board.legal_moves
        lm_str = str( lm_obj )
        lm_ary = lm_str.split()
        print "D: randombot legal moves:" + str(lm_ary)
        random.seed()
        x = random.randint(3,len(lm_ary)-1)
        print "D: randombot picked #%d" % x 
        sys.stdout.flush()
        move_str = lm_ary[x]
        move_str = move_str.replace("(","")
        move_str = move_str.replace(",","")
        move_str = move_str.replace(")","")
        move_str = move_str.replace(">","")
        print "D: randombot picked:" + move_str
        print "bestmove " + move_str + "\n"
        sys.stdout.flush()

    #########################################################################
    def setup_board(self, line):
    #########################################################################
        x = line.find("fen")
        fenstring = line[x+4:]
        self.board = chess.Board(fenstring)
        
        
    #########################################################################
    def main_loop(self):
    #########################################################################
        while(1):
            line =raw_input()
            print "recieved:" + line
            sys.stdout.flush()
            if line.find("uci") == 0:
                self.init_game()
                print "uciok"
                sys.stdout.flush()
            if line.find("ucinewgame") == 0:
                self.init_game()
            if line.find("isready") == 0:
                print "readyok"
                sys.stdout.flush()
            if line.find("position fen") == 0:
                self.setup_board(line)
            if line.find("go") == 0:
                print "randombot generating move"
                sys.stdout.flush()
                self.generate_move(line)
             
                    
            
        
        
        
##########################################################################
##########################################################################
def main():
##########################################################################
##########################################################################
    print "######## starting bot ##############"
    print "randombot (C) 2015 Jon Stephan"
    sys.stdout.flush()
    bot = Bot()
    bot.main_loop()
    
    

##########################################################################
if __name__ == "__main__":
    main()
   
