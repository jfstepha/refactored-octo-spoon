#!/usr/bin/python

############################################################################
# Copyright (C) 2015 Jon Stephan - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Jon Stephan <jfstepha@gmail.com>, 2015
############################################################################
import sys
import time
import string
import chess
import chess.pgn
from curses import wrapper
import curses

import bot_engine
import sys

SCR_ENGINE_Y = 13
SCR_ENGINE_X = 1
SCR_ENGINE_LEN = 5
SCR_BOARD_Y = 0
SCR_BOARD_X = 0
SCR_STATUS_Y = 28
SCR_STATUS_X = 0
SCR_GAMESTAT_Y = 9
SCR_GAMESTAT_X = 0
SCR_TREE_X = 18
SCR_TREE_Y = 0

games_list = []
game_no = 0
##########################################################################
##########################################################################
class AllPositionNode:
##########################################################################
##########################################################################
    ##########################################################################
    def __init__( self ):
    ##########################################################################
        self.stupid = False

##########################################################################
##########################################################################
class SumPositionNode:
##########################################################################
##########################################################################
    ##########################################################################
    def __init__( self ):
    ##########################################################################
        self.stupid = False

##########################################################################
##########################################################################
class PositionDatabase:
##########################################################################
##########################################################################
    ##########################################################################
    def __init__( self ):
    ##########################################################################
        self.all_pos_list = []
        self.sum_pos_list = []

    ##########################################################################
    def addGame( self, game, game_no, mean_delta, result ):
    ##########################################################################
        g = game
        more_moves = True
        while more_moves:
           fen = str( g.board().fen )
           print "adding %s " % fen
           an = AllPositionNode()
           an.fen = fen
           an.game_no = game_no
           an.mean_delta = int( mean_delta )
           if result == '1':
               iresult = 1
           elif result == '0':
               iresult = 0
           else:
               iresult = 0.5
           an.result = iresult
           if g.variations != []:
               an.nextfen = g.variations[0].board().fen()
               an.nextmove = g.variations[0].san()
           else:
               an.nextfen = ""
               an.nextmove = ""

           self.all_pos_list.append( an )
           self.addSumPos( an )

           if g.variations == []:
               break 
           g = g.variations[0]

    ##########################################################################
    def addSumPos( self, an ):
    ##########################################################################
        n = self.isPosInSum( an.fen)
        if n == []:
            # print "  new"
            self.addNewSumPos( an )

        else:
            n.games += 1
            n.wins += an.result
            n.mean_delta.append( an.mean_delta )
            n.nextfens.append( an.nextfen )
            n.nextmoves.append( an.nextmove)
            print "  found games:%d wins=%0.1f meandeltas:%s" % (n.games, n.wins, str(n.mean_delta))
            

    ##########################################################################
    def isPosInSum( self, fen ):
    ##########################################################################
        for n in self.sum_pos_list:
            if n.fen == fen:
                return n
        return []

    ##########################################################################
    def addNewSumPos( self, an ):
    ##########################################################################
        sn = SumPositionNode()
        sn.fen = an.fen
        sn.games = 1
        sn.wins = an.result
        sn.mean_delta = [an.mean_delta]
        sn.nextfens = [an.nextfen]
        sn.nextmoves = [an.nextmove]
        self.sum_pos_list.append(sn)
 

##########################################################################
##########################################################################
class StdOutWrapper:
##########################################################################
##########################################################################
    text = ""
    def write(self,txt):
        self.text += txt
        self.text = '\n'.join(self.text.split('\n')[-30:])
    def get_text(self,beg=0,end=10):
        return '\n'.join(self.text.split('\n')[beg:end])
    def clear_text(self):
        self.text = ""



##########################################################################
def end_of_game(board, mean_delta, game_no):
##########################################################################
    #sys.stdout = sys.__stdout__
    #sys.stderr = sys.__stderr__
    global posDB
    f = open('all_games.pgn', 'a')
    game = chess.pgn.Game.from_board(board)
    game.headers['MeanDelta'] = str(mean_delta)
    f.write( str(game) )
    f.write( "\n\n" )
    f.close()
    g = chess.pgn.Game.from_board( board )
    posDB.addGame(g, game_no, mean_delta, g.headers['Result'])
    print "#### done adding game to DB ####"

##########################################################################
def mystatus(stdscr, printstr):
##########################################################################
    stdscr.addstr(SCR_STATUS_Y,SCR_STATUS_X, printstr)
    stdscr.addstr(SCR_ENGINE_Y,SCR_ENGINE_X, mystdout.get_text(0,SCR_ENGINE_LEN))
    stdscr.refresh()


##########################################################################
def do_a_game(stdscr, rbot, sbot, gameno):
##########################################################################
    print "##### do_a_game ####"
    game_over = False
    board = chess.Board()
    game_evals = []
    eval_deltas = []
    side_to_move = "white"
    prev_eval = 0
    moveno=0
    eval_white = 0
    while board.is_game_over() != True:
        print "##### board loop ####"
        stdscr.addstr(SCR_ENGINE_Y,SCR_ENGINE_X, mystdout.get_text())
        stdscr.refresh()
        mystdout.clear_text()
        fen = board.fen()
        mystatus(stdscr, "making a move")
        move = rbot.makeFirstMove( fen, 1,1)
        move_uci = board.parse_san(move)
        board.push(move_uci)
        mystatus(stdscr, "Done with move: %s" % move )
        mystatus(stdscr, "evaluating move:")
        print "##### evaluating move  ####"
        pos_eval = int( sbot.evalPos( fen,100))
        if side_to_move == "white":
            side_to_move = "black"
            game_evals.append(pos_eval)
            eval_deltas.append(pos_eval - prev_eval)
            prev_eval = pos_eval
            eval_white = -pos_eval
        else:
            side_to_move = "white"
            game_evals.append(-pos_eval)
            eval_deltas.append(-pos_eval - prev_eval)
            prev_eval = -pos_eval
            eval_white = pos_eval
        mean_delta = reduce(lambda x,y: abs(x) + abs(y), eval_deltas) / len(eval_deltas)
        moveno += 1
            
            
        #mystatus(stdscr, "evals: %s" % str(game_evals) )
        #mystatus(stdscr, "deltas: %s" % str(eval_deltas) )

        stdscr.addstr(0,0,str(board))
        stdscr.addstr(SCR_GAMESTAT_Y, SCR_GAMESTAT_X, "#### game number %d move %d #####" %(gameno, moveno), curses.color_pair(2))
        stdscr.addstr(SCR_GAMESTAT_Y+1, SCR_GAMESTAT_X, "mean_delta: %d" % mean_delta)
        stdscr.addstr(SCR_GAMESTAT_Y+2, SCR_GAMESTAT_X, "evaluation: %d         " % eval_white)
        
        n = posDB.isPosInSum( str(board.fen() ) )
        if n == []:
             stdscr.addstr(SCR_TREE_Y+3, SCR_TREE_X, "offbook", curses.color_pair(1))
        else:
             stdscr.addstr(SCR_TREE_Y, SCR_TREE_X, "            TREE             ", curses.color_pair(2))
        stdscr.refresh()
        time.sleep(1)
    end_of_game( board, mean_delta, game_no )


##########################################################################
##########################################################################
def main(stdscr):
##########################################################################
##########################################################################
    global game_no
    toppos=1
    leftpos=1
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    stdscr.clear()
    stdscr.addstr(toppos,leftpos, "######## starting ##############")
    rbot = bot_engine.BotEngine("./randombot.py", "randombot", "", stdscr)
    rbot.stdscr = stdscr
    rbot.curses = True
    rbot.SCR_ENGINE_X = SCR_ENGINE_X + 10
    rbot.SCR_ENGINE_Y = SCR_ENGINE_Y
    print "D: randombot started"
    print "D: starting stockfish"
    sbot = bot_engine.BotEngine("/usr/games/stockfish","Stockfish","", stdscr)
    sbot.curses = True
    sbot.SCR_ENGINE_X = SCR_ENGINE_X + 10
    sbot.SCR_ENGINE_Y = SCR_ENGINE_Y
    print "D: stockfish started"
    
    #### for each game
    while 1:
        print "##### starting a new game ######"
        do_a_game(stdscr, rbot, sbot, game_no)
        print "game finished"
        print "adding to db"
        
        game_no += 1
        time.sleep(1)

##########################################################################
def read_pgn():
##########################################################################
    global games_list
    global posDB
    global game_no
    posDB = PositionDatabase()
    pgn = open("all_games.pgn")
    more_games = True
    game_no=1
    while more_games:
        g = chess.pgn.read_game(pgn)
        if g == None:
            more_games = False
            break
        mean_delta = int(g.headers['MeanDelta'])
        result = g.headers['Result']        
        games_list.append(g)
        print "read game: %s" % str(g)
        posDB.addGame(g, game_no, mean_delta, result)
        game_no += 1



##########################################################################
if __name__ == "__main__":
    read_pgn()

#if False:

    mystdout = StdOutWrapper()
    sys.stdout = mystdout
    sys.stderr = mystdout

    wrapper(main)

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    sys.stdout.write(mystdout.get_text())

