#!/usr/bin/python

############################################################################
# Copyright (C) 2015 Jon Stephan - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Jon Stephan <jfstepha@gmail.com>, 2015
############################################################################

import sys
import bot_telnet 
import bot_engine 
import time
import string
import chess

##########################################################################
##########################################################################
class Bot:
##########################################################################
##########################################################################
    """ The main bot class """

    ##########################################################################
    def __init__(self, botname="stockfisha"):
    ##########################################################################
        self.botname = botname
        self.seek_rated = "rated"
        self.seek_board = ""
        self.seek_auto = ""
        self.seek_formula = ""
        self.seek_rating = ""
        self.seek_side = ""
        self.exe = "stockfish"
        self.player_goal = ""
        self.startstring = "stockfish"
        
        print "bot %s started" % self.botname

    ##########################################################################
    def serverConnect (self, servername="localhost", username="NA", password="NA"):
    ##########################################################################
        print "connecting to %s" % self.botname
        self.server = bot_telnet.BotTelnet(host=servername)
        if username == "NA":
            username = self.botname + "bot"
        if password == "NA":
            password = self.botname + "bot" + "pass"
        self.server.connect( username, password )

    ##########################################################################
    def startEngine ( self ):
    ##########################################################################
        self.engine = bot_engine.BotEngine(self.exe, self.startstring, self.uci_options)

    ##########################################################################
    def checkGoal(self, fen):
    ##########################################################################
        print "DEBUG bot checkgoal checking goal %s in fen %s" % (self.player_goal, fen)
        sys.stdout.flush()
        if self.player_goal == "":
            return False
        board = chess.Board(fen)
        piece = self.player_goal[0]
        file = self.player_goal[1]
        rank = self.player_goal[2]
        print "DEBUG bot checkgoal piece=%s rank=%s file=%s" % (piece, rank, file)
        sys.stdout.flush()
        if piece == "*":
            raise Exception("checkGoal", "not implemented")
        elif (string.lower(piece) in  ['p','r','b','n','k','q'] ) == False:
            raise Exception("checkGoal", "invalid piece type")
        a = chess.Piece.from_symbol(piece)
        piece_type = a.piece_type
        if piece.isupper():
            color = chess.WHITE
        else:
            color = chess.BLACK
        print "DEBUG bot checkgoal piece type %d color %d " % (piece_type, color)
        sys.stdout.flush()
        squares = board.pieces( piece_type, color )
        rankmatch = False
        filematch = False
        for sq in squares:
            print "DEBUG bot checkgoal piece found at %s (rank %s file %s) " % (chess.SQUARE_NAMES[ sq ], chess.RANK_NAMES[ chess.rank_index( sq ) ], chess.FILE_NAMES[ chess.file_index( sq ) ] )
            sys.stdout.flush()
            if rank == "*":
                rankmatch = True
            else:
                if chess.RANK_NAMES[ chess.rank_index( sq ) ] == rank:
                    rankmatch = True
            if file == "*":
                filematch = True
            else:
                if chess.FILE_NAMES[ chess.file_index( sq ) ] == file:
                    filematch = True
        if rankmatch and filematch:
            return True
        else:
            return False

    ##########################################################################
    def seekLoop( self ):
    ##########################################################################
        print "seeking a game"
        self.startEngine()

        while ( 1 ):
            ## infinite loop, relying on exceptions
            self.server.seek( self.seek_time, self.seek_inc, self.seek_rated, self.seek_side, self.seek_board, 
                            self.seek_auto, self.seek_formula, self.seek_rating)
            leftover_text = self.server.waitForGame()
        
            ### if we got here, we must have a game
            gameinprog = True
            firstMove = True
            print "bot starting engine, playing %s" % self.server.side
            # wait for the first move
            (fen, white_time_left, black_time_left, prev_move, tomove) = self.server.waitForMove( leftover_text )
            leftover_text = ""
            while gameinprog:
                print "bot side: %s tomove: %s, fen:%s" % (self.server.side, tomove, fen)
                if( fen[0:3] == "end" ) :
                        print "game ended: %s" % fen
                        gameinprog = False
                        break
                if self.checkGoal(fen):
                    print "game ended: player reached goal!"
                    self.server.resign()
                    gameinprog = False
                    break

                if self.server.side[0] == string.lower(tomove):
                    print "bot's turn - making a move"
                    time.sleep(2)
                    move = self.engine.makeFirstMove( fen, white_time_left, black_time_left )

                    self.server.sendMove(move)
                    ## wait for confirmation of the move
                    (fen, white_time_left, black_time_left, prev_move, tomove) = self.server.waitForMove( leftover_text )
                    leftover_text = ""

                else:
                    print "player's turn - waiting"
                    (fen, white_time_left, black_time_left, prev_move, tomove) = self.server.waitForMove( leftover_text )
                    leftover_text = ""
                    
        


##########################################################################
##########################################################################
def main():
##########################################################################
##########################################################################
    print "######## starting bot ##############"
    if len(sys.argv) < 2:
        print "no bot specified, using stockfishA"
        botname = "stockfisha"
    else:
        botname = str(sys.argv[1])
    print "Starting bot %s" % botname
    bot = Bot( botname )
    bot.serverConnect()

    if botname == "stockfisha":
        bot.exe = "stockfish"
        bot.startstring = "stockfish"
        bot.seek_time = 15
        bot.seek_inc = 0
        bot.uci_options = "setoption name Skill Level value 0"
    if botname == "random":
        bot.exe = "./randombot.py"
        bot.startstring = "randombot"
        bot.seek_time = 15
        bot.seek_inc = 0
        bot.uci_options = ""
    if botname == "randomkvk":
        bot.exe = "./randombot.py"
        bot.startstring = "randombot"
        bot.seek_time = 2
        bot.seek_inc = 0
        bot.seek_board = "onlyk"
        bot.seek_side = "black"
        bot.player_goal = "K*8"
        bot.uci_options = ""
    bot.seekLoop()
    

##########################################################################
if __name__ == "__main__":
    main()

