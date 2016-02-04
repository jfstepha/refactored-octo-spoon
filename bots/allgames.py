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

MAX_GAME_LEN = 5
MAX_TREE_DEPTH = 5
MAX_TREE_PRINT = 10
TREE_PAUSE = 0.5

SCR_ENGINE_Y = 25
SCR_ENGINE_X = 1
SCR_ENGINE_LEN = 5
SCR_BOARD_Y = 0
SCR_BOARD_X = 0
SCR_STATUS_Y = 28
SCR_STATUS_X = 0
SCR_GAMESTAT_Y = 12
SCR_GAMESTAT_X = 0
SCR_TREE_X = 50
SCR_TREE_Y = 0
SCR_GAMESUM_X = 110
SCR_GAMESUM_Y = 0
SCR_PGN_FEN_X = 0
SCR_PGN_FEN_Y = 20

games_list = []
game_no = 0
##########################################################################
##########################################################################
class GameSum:
##########################################################################
##########################################################################
    ##########################################################################
    def __init__( self ):
    ##########################################################################
        self.mean_deltas = []
        self.mean_mean = 0
        self.mean_min = 999999
        self.mean_max = -999999
        self.total_games = 0
        self.stdscr = []
        self.histobuckets = 20
        self.histostep = 0
        self.histocounts = []
        self.barchars = 10
        self.countperchar = 1
        self.unique_games = 0
        self.uniqueness = []
        self.db_positions = []
        self.db_unique_pos = []

    ##########################################################################
    def appendDelta( self, mean_delta, db_unique_poss, db_total_poss ):
    ##########################################################################
        self.mean_deltas.append( mean_delta )
        self.db_unique_pos.append( db_unique_poss )
        self.db_positions.append( db_total_poss )

    ##########################################################################
    def calcGameSum( self ):
    ##########################################################################
        self.mean_mean = reduce( lambda x, y: x + y, self.mean_deltas) / len( self.mean_deltas )
        self.total_games = len( self.mean_deltas )
        self.mean_min = min( self.mean_deltas )
        self.mean_max = max( self.mean_deltas )
        self.histostep = ( self.mean_max - self.mean_min ) / (self.histobuckets-1)
        self.histocounts = [0] *  self.histobuckets
        for mean_delta in self.mean_deltas:
            for i in range( 0, self.histobuckets ):
                if mean_delta <= self.mean_min + self.histostep * (i+1):
                    self.histocounts[i] += 1
                    break
        self.histocount_max = max( self.histocounts )
        if self.histocount_max > self.barchars:
            self.countperchar = self.histocount_max / self.barchars
        self.writeMeans()

    ##########################################################################
    def printGameSum( self ):
    ##########################################################################
        if self.total_games == 0:
           gp = 0
        else: 
           gp = self.unique_games  * 100 / self.total_games
        self.stdscr.addstr( SCR_GAMESUM_Y, SCR_GAMESUM_X, "total games: %d  " % self.total_games, curses.color_pair(4) ) 
        self.stdscr.addstr( SCR_GAMESUM_Y+1, SCR_GAMESUM_X, "unique games: %d (%0.0f%%) " % (self.unique_games, gp), curses.color_pair(4) )
        self.stdscr.addstr( SCR_GAMESUM_Y+2, SCR_GAMESUM_X, "mean_delta mean: %d  " % self.mean_mean, curses.color_pair(4))
        self.stdscr.addstr( SCR_GAMESUM_Y+3, SCR_GAMESUM_X, "mean_delta range: %d-%d  " % (self.mean_min, self.mean_max), curses.color_pair(4))
        for i in range( 0, len(self.histocounts) ):
            bucketmin = self.mean_min + i * self.histostep
            bucketmax = bucketmin + self.histostep
            self.stdscr.addstr( SCR_GAMESUM_Y+4+i, SCR_GAMESUM_X, " bucket %2d (%-4d-%4d) = %4d " % (i, bucketmin, bucketmax,self.histocounts[i]), curses.color_pair(3))
            barlen = self.histocounts[i] / self.countperchar
            for j in range( 0, int(barlen)):
                self.stdscr.addstr( "#", curses.color_pair(2) )

        self.stdscr.refresh()

    ##########################################################################
    def writeMeans( self ):
    ##########################################################################
        f = open('games.csv', 'w')
        f.write("mean_delta, unique, db_positions, db_unique_positions\n")
        for i in range( 0, len( self.mean_deltas ) ):
            f.write( "%d, %d, %d, %d\n" % ( self.mean_deltas[i], self.uniqueness[i], self.db_positions[i], self.db_unique_pos[i] ) )
        f.close()

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
        self.unique = 1

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
        self.print_tree_delay = 0.1
        self.unique_game = 0
        self.unique_poss = 0

    ##########################################################################
    def addGame( self, game, game_no, mean_delta, result ):
    ##########################################################################
        g = game
        more_moves = True
        move_no = 1
        unique_game = 0
        while more_moves:
           fen = str( g.board().fen() )
           self.stdscr.addstr(SCR_PGN_FEN_Y, SCR_PGN_FEN_X, "adding game %d move %d: %s\n" % (game_no, move_no, fen))
           #self.stdscr.refresh()
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

           # self.all_pos_list.append( an )
           self.addSumPos( an )

           if g.variations == []:
               break 
           if move_no >= MAX_TREE_DEPTH:
               break
           move_no += 1
           g = g.variations[0]
        gameSum.unique_games += self.unique_game
        gameSum.uniqueness.append( unique_game )
        gameSum.appendDelta( mean_delta, self.unique_poss, len( self.sum_pos_list )  ) 
        gameSum.calcGameSum( )
        gameSum.printGameSum( )

    ##########################################################################
    def addSumPos( self, an ):
    ##########################################################################
        n = self.isPosInSum( an.fen)
        if n == []:
            # print "  new"
            self.addNewSumPos( an )
            self.stdscr.addstr(SCR_PGN_FEN_Y+1, SCR_PGN_FEN_X, "\n")
            #self.stdscr.addstr(SCR_PGN_FEN_Y+1, SCR_PGN_FEN_X, "                                                                                                                                ")
            self.stdscr.refresh()
            self.clearTree()
            self.unique_game = 1
            self.unique_poss += 1

        else:
            n.games += 1
            n.wins += an.result
            n.mean_delta.append( an.mean_delta )
            n.nextfens.append( an.nextfen )
            n.nextmoves.append( an.nextmove)
            if n.unique == 1:
                self.unique_poss -= 1
            n.unique = 0
            #self.stdscr.addstr(SCR_PGN_FEN_Y+1, SCR_PGN_FEN_X, "  found games:%d wins=%0.1f meandeltas:%s" % (n.games, n.wins, str(n.mean_delta)) )
            self.stdscr.refresh()
            self.clearTree()
            self.printTree(n)
            self.unique_game = 0
            

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
        sn.unique = 1
        self.sum_pos_list.append(sn)
    ##########################################################################
    def printTree( self, n ):
    ##########################################################################
        up = self.unique_poss * 100 / len(self.sum_pos_list) 
        self.stdscr.addstr(SCR_TREE_Y, SCR_TREE_X, "            TREE             ", curses.color_pair(2))
        self.stdscr.addstr(SCR_TREE_Y+1, SCR_TREE_X, "  fen: %s\n" % n.fen)
        self.stdscr.addstr(SCR_TREE_Y+2, SCR_TREE_X, "  wins: %d\n" % n.wins)
        self.stdscr.addstr(SCR_TREE_Y+3, SCR_TREE_X, "  moves: %d\n" % len(n.nextmoves))
        self.stdscr.addstr(SCR_TREE_Y+4, SCR_TREE_X, "  visits: %d\n" % n.games )
        self.stdscr.addstr(SCR_TREE_Y+5, SCR_TREE_X, "  %d positions (%d unique %0.0f%%) \n" % (len(self.sum_pos_list), self.unique_poss, up) )
        unique_moves = list(set(n.nextmoves))
        i=1
        for move in unique_moves:
            if i > MAX_TREE_PRINT:
                break
            visits = n.nextmoves.count(move)
            self.stdscr.addstr(SCR_TREE_Y+5+i, SCR_TREE_X, "    move %-6s v %-6d      " % (move, visits), curses.color_pair(4))
            i += 1
        for j in range(i,MAX_TREE_PRINT+1):
            self.stdscr.addstr(SCR_TREE_Y+5+j, SCR_TREE_X, "\n", curses.color_pair(1))
        gameSum.printGameSum()
        self.stdscr.refresh()
        time.sleep(self.print_tree_delay)
    ##########################################################################
    def clearTree( self ):
    ##########################################################################
        if len(self.sum_pos_list) == 0:
            up = 0
        else:
            up = self.unique_poss * 100 / len(self.sum_pos_list) 
        self.stdscr.addstr(SCR_TREE_Y, SCR_TREE_X, "\n")
        self.stdscr.addstr(SCR_TREE_Y+1, SCR_TREE_X, "\n")
        self.stdscr.addstr(SCR_TREE_Y+2, SCR_TREE_X, "\n")
        self.stdscr.addstr(SCR_TREE_Y+3, SCR_TREE_X, "\n")
        self.stdscr.addstr(SCR_TREE_Y+4, SCR_TREE_X, "offbook\n", curses.color_pair(1))
        self.stdscr.addstr(SCR_TREE_Y+5, SCR_TREE_X, "  %d positions (%d unique %0.0f%%) \n" % (len(self.sum_pos_list), self.unique_poss, up) )
        for i in range(1,MAX_TREE_PRINT+1):
            self.stdscr.addstr(SCR_TREE_Y+5+i, SCR_TREE_X, "\n", curses.color_pair(1))
        gameSum.printGameSum()
            
       
 

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
    tmp = posDB.print_tree_delay
    posDB.print_tree_delay = 0.1
    f = open('all_games.pgn', 'a')
    game = chess.pgn.Game.from_board(board)
    game.headers['MeanDelta'] = str(mean_delta)
    game.headers['WhiteElo'] = str(mean_delta)
    game.headers['Round'] = str(game_no)
    f.write( str(game) )
    f.write( "\n\n" )
    f.close()
    g = chess.pgn.Game.from_board( board )
    posDB.addGame(g, game_no, mean_delta, g.headers['Result'])
    posDB.print_tree_delay = tmp

##########################################################################
def mystatus(stdscr, printstr):
##########################################################################
    stdscr.addstr(SCR_STATUS_Y,SCR_STATUS_X, printstr + "\n")
    stdscr.addstr(SCR_ENGINE_Y,SCR_ENGINE_X, mystdout.get_text(0,SCR_ENGINE_LEN) + "\n")
    stdscr.refresh()


##########################################################################
def do_a_game(stdscr, rbot, sbot, gameno):
##########################################################################
    #print "##### do_a_game ####"
    global posDB
    posDB.stdscr = stdscr
    posDB.print_tree_delay = TREE_PAUSE
    game_over = False
    board = chess.Board()
    game_evals = []
    eval_deltas = []
    side_to_move = "white"
    prev_eval = 0
    moveno=0
    eval_white = 0
    mate_in_count = 0
    stdscr.clear()
    while board.is_game_over() != True:
        #print "##### board loop ####"
        stdscr.addstr(SCR_ENGINE_Y,SCR_ENGINE_X, mystdout.get_text())
        stdscr.refresh()
        mystdout.clear_text()
        fen = board.fen()
        mystatus(stdscr, "making a move")
        move = rbot.makeFirstMove( fen, 1,1)
        move_uci = board.parse_san(move)
        board.push(move_uci)
        mystatus(stdscr,"Done with move: %s" % move )
        mystatus(stdscr,"evaluating move")
        #print "##### evaluating move  ####"
        pos_eval = int( sbot.evalPos( fen,100))
        if pos_eval == 10000:
            mate_in_count += 1
            if mate_in_count > 10:
                eval_deltas.append( 10000 )
                next
            eval_deltas.append( 0 )
            next
        elif mate_in_count > 0:
            # was a mate in N, but now is not
            eval_deltas.append( 10000 )
            mate_in_count = 0
            next
     
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
        

        mystatus(stdscr, "checking db")
        if moveno < MAX_TREE_DEPTH:
            n = posDB.isPosInSum( str(board.fen() ) )
            mystatus(stdscr,"drawing tree")
        
            if n == []:
                 posDB.clearTree()
            else:
                 posDB.printTree(n)
        else:
            posDB.clearTree()
        stdscr.refresh()
        if moveno >= MAX_GAME_LEN:
            break 
        #time.sleep(1)
    mystatus(stdscr,"doing end of game")
    end_of_game( board, mean_delta, game_no )


##########################################################################
##########################################################################
def main(stdscr):
##########################################################################
##########################################################################
    global game_no
    toppos=1
    leftpos=1
    init_colors()
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
        #print "##### starting a new game ######"
        do_a_game(stdscr, rbot, sbot, game_no)
        #print "game finished"
        
        game_no += 1
        time.sleep(1)
##########################################################################
def init_colors():
##########################################################################
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)

##########################################################################
def read_pgn(stdscr):
##########################################################################
    global games_list
    global posDB
    global gameSum
    global game_no
    stdscr.clear()
    posDB = PositionDatabase()
    posDB.stdscr = stdscr
    init_colors()
    gameSum = GameSum()
    gameSum.stdscr = stdscr
    pgn = open("all_games.pgn")
    more_games = True
    game_no=1
    while more_games:
        g = chess.pgn.read_game(pgn)
        if g == None:
            more_games = False
            break
        if 'MeanDelta' in g.headers:
            mean_delta = int(g.headers['MeanDelta'])
        else:
            mean_delta = -1
        result = g.headers['Result']        
        games_list.append(g)
        stdscr.clear()
        stdscr.addstr(0,0, "read game: %s" % str(g)[0:1000])
        stdscr.refresh()
        posDB.addGame(g, game_no, mean_delta, result)
        gameSum.printGameSum( )
        game_no += 1



##########################################################################
if __name__ == "__main__":

#if False:

    mystdout = StdOutWrapper()
    sys.stdout = mystdout
#    sys.stderr = mystdout

    wrapper(read_pgn)
    wrapper(main)

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    sys.stdout.write(mystdout.get_text())

