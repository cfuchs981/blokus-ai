# Some functions are modified from the source listed in piece.py
# (the functions that handle the Piece objects).

from utils import *
import sys
import math
import random
import copy
import piece
from gui import *
import copy
import operator
import time
import numpy as np

# PERFORMANCE PARAMETERS: edit these to play with AI performance
# change to adjust the cutoff depth for alphabeta search
Depth = 2
# change to adjust the number of successor states returned
MovesToConsider = 2
# change to adjust the number of games played
Games = 10

# used for alphabeta search
count = 0
testing = 0
BigInitialValue = 1000000

# number of total squares amongst all of a player's starting pieces
TotalStartingSize = 89
# number of pieces per player at the start of the game
TotalStartingPieces = 21

# used for analyzing AI performance
MoveTimes = []
Outcomes = []
Scores = []
EstimateData = []

# Blokus Board
class Board:
    def __init__(self, nrow, ncol):
        self.nrow = nrow; # total rows
        self.ncol = ncol; # total columns

        self.state = [['_'] * ncol for i in range(nrow)];

    def update(self, player_id, placement):
        for row in range(self.nrow):
            for col in range(self.ncol):
                if(col, row) in placement:
                    self.state[row][col] = player_id;

    # Check if the point (y, x) is within the board's bound
    def in_bounds(self, point):
        return 0<= point[0] < self.ncol and 0<= point[1] < self.nrow;

    # Check if a piece placement overlap another piece on the board
    def overlap(self, placement):
        return False in[(self.state[y][x] == '_') for x, y in placement]

    # Checks if a piece placement is adjacent to any square on
    # the board which are occupied by the player proposing the move.
    def adj(self, player_id, placement):
        adjacents = [];
        # Check left, right, up, down for adjacent square
        for x, y in placement:
            if self.in_bounds((x + 1, y)):
                adjacents += [self.state[y][x + 1] == player_id];
            if self.in_bounds((x -1, y)):
                adjacents += [self.state[y][x - 1] == player_id];
            if self.in_bounds((x, y -1)):
                adjacents += [self.state[y - 1][x] == player_id];
            if self.in_bounds((x, y + 1)):
                adjacents += [self.state[y + 1][x] == player_id];

        return True in adjacents;

    # Check if a piece placement is cornering
    # any pieces of the player proposing the move.
    def corner(self, player_id, placement):
        corners = [];
        # check the corner square from the placement
        for x, y in placement:
            if self.in_bounds((x + 1, y + 1)):
                corners += [self.state[y + 1][x + 1] == player_id];
            if self.in_bounds((x - 1, y -1)):
                corners += [self.state[y - 1][x - 1] == player_id];
            if self.in_bounds((x + 1, y - 1)):
                corners += [self.state[y - 1][x + 1] == player_id];
            if self.in_bounds((x - 1, y + 1)):
                corners += [self.state[y + 1][x - 1] == player_id];

        return True in corners;

    
    '''
    # Print the current board layout
    # TODO(UI) we don't want this. This is lazy testing UI, route it into
    # something better & with colors. 
    
    def print_board(self):
        print("Current Board Layout:");
        for row in range(len(self.state)):
            for col in range(len(self.state[0])):
                print(" "+ str(self.state[row][col]), end = '')
            print()
    '''
    

# Player Class
class Player:
    def __init__(self, id, strategy):
        self.id = id # player's id
        self.pieces = [] # player's unused game piece, list of Pieces
        self.corners = set() # current valid corners on board
        self.strategy = strategy # player's strategy
        self.score = 0 # player's current score
        self.is_blocked = False

    #Add the player's initial pieces for a game
    def add_pieces(self, pieces):
        self.pieces = pieces;

    # Remove a player's Piece
    def remove_piece(self, piece):
        self.pieces = [p for p in self.pieces if p.id != piece.id];

    # Set the available starting corners for players
    def start_corner(self, p):
        self.corners = set([p])

    # Updates player information after placing a board Piece
    def update_player(self, piece, board):
        self.score += piece.size;
        # If you're placing your last piece, you get +15 bonus
        if len(self.pieces) == 1:
            self.score += 15;
            if piece.id == 'Pole': # +5 extra if its the [] piece
                self.score += 5;
        for c in piece.corners:
            # Add the player's available corners
            if board.in_bounds(c) and not board.overlap([c]):
                self.corners.add(c);

    # Get a unique list of all possible placements
    # NOTE: this takes a while to run
    def possible_moves(self, pieces, game):
        # Updates the corners of the player, in case the
        # corners have been covered by another player's pieces.
        self.corners = set([(x, y) for(x, y) in self.corners
                            if game.board.state[y][x] == '_']);

        placements = [] # a list of possible placements
        visited = [] # a list placements (a set of points on board)

        # Check every available corners
        for cr in self.corners:
            # Check every available pieces
            for sh in pieces:
                # print("size:", sh.size)
                # test_count = 0
                # Check every reference point the piece could have.
                for num in range(sh.size):
                    # Check every flip
                    for flip in ["h", "v"]:
                        # Check every rotation
                        for rot in [0, 90, 180, 270]:
                            # Create a copy to prevent an overwrite on the original
                            candidate = copy.deepcopy(sh);
                            candidate.create(num, cr);
                            candidate.flip(flip);
                            candidate.rotate(rot);
                            # If the placement is valid and new
                            if game.valid_move(self, candidate.points):
                                if not set(candidate.points) in visited:
                                    # test_count += 1
                                    placements.append(candidate);
                                    visited.append(set(candidate.points));
                # print("test_count", test_count)
        return placements;

    # return the number of all possible placements
    def possible_count(self, pieces, game):
        # Updates the corners of the player, in case the
        # corners have been covered by another player's pieces.
        self.corners = set([(x, y) for(x, y) in self.corners
                            if game.board.state[y][x] == '_']);
        counter = 0
        visited = [] # a list placements (a set of points on board)

        # Check every available corners
        for cr in self.corners:
            # Check every available pieces
            for sh in pieces:
                # Check every reference point the piece could have.
                for num in range(sh.size):
                    # Check every flip
                    for flip in ["h", "v"]:
                        # Check every rotation
                        for rot in [0, 90, 180, 270]:
                            # Create a copy to prevent an overwrite on the original
                            sh.create(num, cr);
                            sh.flip(flip);
                            sh.rotate(rot);
                            # If the placement is valid and new
                            if game.valid_move(self, sh.points):
                                if not set(sh.points) in visited:
                                    counter += 1;
                                    visited.append(set(sh.points));
        return counter;

    # Get a list of up to cutoff plausible placements
    def plausible_moves(self, pieces, game, cutoff):
        # why not just use possible_moves on individual pieces?
        placements = []
        for piece in pieces:
            possibles = self.possible_moves([piece], game)
            # print(" Possibles: ", possibles)
            # print(possibles != [])
            if possibles != []:
                for possible in possibles:
                    placements.append(possible)
                    if len(placements) == cutoff:
                        # MARKER uncomment this to see pieces
                        # print("cutoff reached! returning ", placements)
                        return placements
        # MARKER uncomment this to see pieces
        # print("cutoff NOT reached! returning ", placements)
        return placements

    # Get the next move based off of the player's strategy
    def next_move(self, game):
        return self.strategy(self, game);

# Blokus Game class
class Blokus:
    def __init__(self, players, board, all_pieces):
        self.players = players; 
        self.rounds = 0; 
        self.board = board; 
        self.all_pieces = all_pieces; 
        self.previous = 0; 
        self.repeat = 0; # counter for how many times the total available moves are
                         # the same by checking previous round
        self.win_player = 0; # winner

    # Check for the winner (or tied) in the game and return the winner's id.
    # Or return nothing if the game can still progress
    def winner(self):
        moves = []
        for p in self.players:
            possibles = p.possible_count(p.pieces, self)
            if possibles == 0:
                p.is_blocked = True
            moves.append(possibles)

        # check how many rounds the total available moves from all players
        # are the same and increment the counter if so
        if self.previous == sum([mv for mv in moves]):
            self.repeat += 1;
        else:
            self.repeat = 0;

        # if there are still moves possible or total available moves remain
        # static for too many rounds (repeat reaches over a certain threshold)
        if False in[mv == 0 for mv in moves] and self.repeat < 4:
            self.previous = sum([mv for mv in moves]);
            return None; # Nothing to return to continue the game
        else: # No more move available, the game ends
            # order the players by highest score first
            candidates = [(p.score, p.id) for p in self.players];
            candidates.sort(key = lambda x: x[0], reverse = True);
            highest = candidates[0][0];
            result = [candidates[0][1]];
            for candidate in candidates[1:]: # check for tied score
                if highest == candidate[0]:
                    result += [candidate[1]];
            return result # get all the highest score players

    # Check if a player's move is valid, including board bounds, pieces' overlap, adjacency, and corners.
    def valid_move(self, player, placement):
        if self.rounds < len(self.players):
            # Check for starting corner
            return not ((False in [self.board.in_bounds(pt) for pt in placement])
                        or self.board.overlap(placement)
                        or not (True in[(pt in player.corners) for pt in placement]));
        return not ((False in[self.board.in_bounds(pt) for pt in placement])
                    or self.board.overlap(placement)
                    or self.board.adj(player.id, placement)
                    or not self.board.corner(player.id, placement));

    # Play the game with the list of players sequentially until the
    # game ends (no more pieces can be placed for any player)
    def play(self):
        global Outcomes
        # At the beginning of the game, it should
        # give the players their pieces and a corner to start.
        if self.rounds == 0: # set up starting corners and players' initial pieces
            max_x = self.board.ncol -1;
            max_y = self.board.nrow -1;
            starts = [(0, 0), (max_x, max_y), (0, max_y), (max_x, 0)];
            for i in range(len(self.players)):
                self.players[i].add_pieces(list(self.all_pieces));
                self.players[i].start_corner(starts[i]);
        winner = self.winner(); # get game status
        if winner is None: # no winner, the game continues
            current = self.players[0]; # get current player
            proposal = current.next_move(self); # get the next move based on
                                                # the player's strategy

            if proposal is not None: # if there a possible proposed move
                # check if the move is valid
                if self.valid_move(current, proposal.points):
                    # update the board and the player status
                    self.board.update(current.id, proposal.points);
                    current.update_player(proposal, self.board);
                    render(self.board.state)
                    current.remove_piece(proposal); # remove used piece
                else: # end the game if an invalid move is proposed
                    raise Exception("Invalid move by player "+ str(current.id));
            # put the current player to the back of the queue
            first = self.players.pop(0);
            self.players += [first];
            self.rounds += 1; # update game round
        else: # a winner (or a tie) is found
            if len(winner) == 1: # if the game results in a winner
                self.win_player = winner[0];
                # below keeps track of data for analytics
                # hard-coded such that AI is P2
                # this is bad. I'm doing it anyways
                # 1 represents an AI win
                if winner[0] == 2:
                    Outcomes.append(1)
                # -1 represents a human win
                else:
                    Outcomes.append(-1)
                # score
                for player in self.players:
                    if player.id == 2:
                        Scores.append(player.score)
                print('Game over! The winner is: '+ str(winner[0]));
            else: # if the game results in a tie
                # score
                for player in self.players:
                    if player.id == 2:
                        Scores.append(player.score)
                # 0 represents a tie
                Outcomes.append(0)
                print('Game over! Tied between players: '+ ', '.join(map(str, winner)));

    def make_move(self, move, state):
        "Return a new BoardState reflecting move made from given board state."
        # make a copy of the given state to be updated
        newboard = copy.deepcopy(state)
        # get current player
        current = newboard.to_move;
        # update the board and the player status
        newboard._board.update(current.id, move.points);
        current.update_player(move, newboard._board);
        current.remove_piece(move); # remove used piece
        # put the current player to the back of the queue
        first = newboard.game.players.pop(0);
        newboard.game.players += [first];
        newboard.game.rounds += 1; # update game round
        # update newboard to_move
        newboard.to_move = newboard.game.players[0]
        return newboard

    def successors(self, state):
        "Return a list of legal (move, state) pairs."
        # find and return up to MovesToConsider possible moves as successors
        m = [(move, self.make_move(move, state))
                for move in state.to_move.plausible_moves(state.to_move.pieces, state.game, MovesToConsider)]
        return m

    def terminal_test(self, state):
        "Return True if this is a final state for the game."
        # if we have no moves left, it's apparently (effectively) a final state
        return not state.to_move.plausible_moves(state.to_move.pieces, state.game, 1)

    # gets called in ab search on new states
    def utility(self, state, actual_turn_number):
        # print("starting utility")
        # this is hard-coded and bad. I'm doing it anyways
        # get current player
        ai_player = state.p2
        opponent = state.p1

        # start total at 89
        total = TotalStartingSize
        # count the number of squares in all remaining pieces
        for p in ai_player.pieces:
            # subtract current remaining squares from initial 89
            # less pieces in hand => higher utility
            # motivates playing largest pieces first
            total -= p.size

        # blocking and finishing are impossible within the first two moves
        # skip blocking and endgame calculations on first two moves

        # if we're past the first two moves
        if actual_turn_number > 2:
            # print("past first two moves")
            # turn number in this successor state is calculated by taking 21 - number of pieces + 1 (offset)
            # print("GETTING AI ESTIMATE")
            ai_piece_count = len(ai_player.pieces)
            ai_turn_number = (TotalStartingPieces - ai_piece_count + 1)
            # determine how many possible moves we have
            ai_player_possibles = ai_player.possible_count(ai_player.pieces, state.game)
            # data for estimation stats
            ai_player_data = {
                "turn": ai_turn_number,
                "possibles": ai_player_possibles,
                "corners": len(ai_player.corners),
                "pieces": len(ai_player.pieces),
                "player": ai_player.id
            }
            EstimateData.append(ai_player_data)

            # add a point for every possible move we have
            total += ai_player_possibles

            # if opponent has possible moves
            if not opponent.is_blocked:
                # print("opponent not blocked")
                # print("GETTING OPPONENT ESTIMATE")
                # turn number in this successor state is calculated by taking 21 - number of pieces + 1 (offset)
                opponent_piece_count = len(opponent.pieces)
                opponent_turn_number = (TotalStartingPieces - opponent_piece_count + 1)

                # determine how many possible moves opponent has
                opponent_possibles = opponent.possible_count(opponent.pieces, state.game)
                # data for estimation stats
                opponent_data = {
                    "turn": opponent_turn_number,
                    "possibles": opponent_possibles,
                    "corners": len(opponent.corners),
                    "pieces": len(opponent.pieces),
                    "player": opponent.id
                }
                EstimateData.append(opponent_data)

                # subtract a point for every possible move our opponent has
                total -= opponent_possibles
            # TODO get rid of this else clause, only for collection of data
            # collect opponent data in case opponent is blockeds
            else:
                # print("opponent blocked")
                # turn number in this successor state is calculated by taking 21 - number of pieces + 1 (offset)
                # print("GETTING OPPONENT ESTIMATE")
                opponent_piece_count = len(opponent.pieces)
                opponent_turn_number = (TotalStartingPieces - opponent_piece_count + 1)

                # determine how many possible moves opponent has
                opponent_possibles = opponent.possible_count(opponent.pieces, state.game)
                # data for estimation stats
                opponent_data = {
                    "turn": opponent_turn_number,
                    "possibles": opponent_possibles,
                    "corners": len(opponent.corners),
                    "pieces": len(opponent.pieces),
                    "player": opponent.id
                }
                EstimateData.append(opponent_data)
            # skip endgame calculations if more than 1 piece
            if ai_piece_count > 1:
                # print("no endgame, more than one piece")
                # print("returning utility\n")
                return total
            # if the monomino is the last one, add 500 bonus points
            elif ai_piece_count == 1:
                # print("one piece left")
                if ai_player.pieces[0].size == 1:
                    # print("it's the monomino")
                    total += 500
            # if no pieces are left, add 1500 bonus points
            elif ai_piece_count == 0:
                # print("no pieces left")
                # NOTE tone down these values if we use possible_count and not estimates
                total += 1500
        # TODO get rid of this else clause, only for collection of data
        # collect data for both players on first two moves
        else:
            # print("not past first two moves")
            # DON'T MESS WITH TOTAL
            # turn number in this successor state is calculated by taking 21 - number of pieces + 1 (offset)
            # print("GETTING AI ESTIMATE")
            ai_piece_count = len(ai_player.pieces)
            ai_turn_number = (TotalStartingPieces - ai_piece_count + 1)
            # determine how many possible moves we have
            ai_player_possibles = ai_player.possible_count(ai_player.pieces, state.game)
            # data for estimation stats
            ai_player_data = {
                "turn": ai_turn_number,
                "possibles": ai_player_possibles,
                "corners": len(ai_player.corners),
                "pieces": len(ai_player.pieces),
                "player": ai_player.id
            }
            EstimateData.append(ai_player_data)
            # turn number in this successor state is calculated by taking 21 - number of pieces + 1 (offset)
            # print("GETTING OPPONENT ESTIMATE")
            opponent_piece_count = len(opponent.pieces)
            opponent_turn_number = (TotalStartingPieces - opponent_piece_count + 1)

            # determine how many possible moves opponent has
            opponent_possibles = opponent.possible_count(opponent.pieces, state.game)
            # data for estimation stats
            opponent_data = {
                "turn": opponent_turn_number,
                "possibles": opponent_possibles,
                "corners": len(opponent.corners),
                "pieces": len(opponent.pieces),
                "player": opponent.id
            }
            EstimateData.append(opponent_data)
        # print("returning utility\n")
        return total

# Random Strategy: choose an available piece randomly
def Random_Player(player, game):
    options = [p for p in player.pieces];
    while len(options) > 0: # if there are still possible moves
        piece = random.choice(options);
        possibles = player.possible_moves([piece], game);
        if len(possibles) != 0: # if there is possible moves
            return random.choice(possibles);
        else: # no possible move for that piece
            options.remove(piece); # remove it from the options
    return None; # no possible move left

# Largest Strategy: play a random available move for the largest piece possible
# NOTE: this random choice thing might be helpful for implementing intelligent selection?
def Largest_Player(player, game):
    # pieces are already in order from largest to smallest
    # iterate through and make the first possible move
    for p in player.pieces:
        possibles = player.possible_moves([p], game)
        if len(possibles) != 0: # if there is possible moves
            return random.choice(possibles);
    # if no possible moves are found, return None
    return None

# AI Strategy: choose a move based on utility
def AI_Player(player, game):
    start_time = time.time()
    # determine what turn we're on
    turn_number = (TotalStartingPieces - len(player.pieces) + 1)
    # if no possible moves in this state, return None
    if not player.plausible_moves(player.pieces, game, 1):
        # print("WE'RE OUTTA MOVES")
        return None; # no possible move left
    # copy current game info into a BoardState to be used within ab search
    game_copy = copy.deepcopy(game)
    state = BoardState(game_copy)
    # perform alphabeta search and return a useful move
    return alphabeta_search(state, Depth, None, None, start_time, turn_number)

def alphabeta_search(state, d=1, cutoff_test=None, eval_fn=None, start_time=None, turn_number=None):
    """Search game to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""
    global count
    global testing
    global BigInitialValue
    global MoveTimes

    player = state.to_move
    count = 0

    def max_value(state, alpha, beta, depth):
        global count, testing
        if testing:
            print("  "* depth, "Max  alpha: ", alpha, " beta: ", beta, " depth: ", depth)
        if cutoff_test(state, depth):
            if testing:
                print("  "* depth, "Max cutoff returning ", eval_fn(state))
            return eval_fn(state)
        v = -BigInitialValue
        succ = state.game.successors(state)
        count = count + len(succ)
        if testing:
            print("  "*depth, "maxDepth: ", depth, "Total:", count, "Successors: ", len(succ))
        for (a, s) in succ:
            # Decide whether to call max_value or min_value, depending on whose move it is next.
            # A player can move repeatedly if opponent is completely blocked
            if state.to_move == s.to_move:
                v = max(v, max_value(s, alpha, beta, depth+1))
            else:
                v = max(v, min_value(s, alpha, beta, depth+1))
            if testing:
                print("  "* depth, "max best value:", v)
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(state, alpha, beta, depth):
        global count
        if testing:
            print("  "*depth, "Min  alpha: ", alpha, " beta: ", beta, " depth: ", depth)
        if cutoff_test(state, depth):
            if testing:
                print("  "*depth, "Min cutoff returning ", eval_fn(state))
            return eval_fn(state)
        v = BigInitialValue
        succ = state.game.successors(state)
        count = count + len(succ)
        if testing:
            print("  "*depth, "minDepth: ", depth, "Total:", count, "Successors: ", len(succ))
        for (a, s) in succ:
            # Decide whether to call max_value or min_value, depending on whose move it is next.
            # A player can move repeatedly if opponent is completely blocked
            if state.to_move == s.to_move:
                v = min(v, min_value(s, alpha, beta, depth+1))
            else:
                v = min(v, max_value(s, alpha, beta, depth+1))
            if testing:
                print("  "*depth, "min best value:", v)
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    def right_value(s, alpha, beta, depth):
        if s.to_move.id == state.to_move.id:
            return max_value(s, -BigInitialValue, BigInitialValue, 0)
        else:
            return min_value(s, -BigInitialValue, BigInitialValue, 0)

    # Body of alphabeta_search starts here:
    cutoff_test = (cutoff_test or
                   (lambda state,depth: depth>d or state.game.terminal_test(state)))
    eval_fn = eval_fn or (lambda state: state.game.utility(state, turn_number))
    action, state = argmax(state.game.successors(state),
                           # lambda ((a, s)): right_value(s, -BigInitialValue, BigInitialValue, 0))
                            lambda a_s: right_value(a_s[1], -BigInitialValue, BigInitialValue, 0))
    # calculate move time, round to 2 decimal places, store for analysis
    MoveTimes.append(round(time.time() - start_time, 2))
    return action

class BoardState:
    """Holds one state of the Mancala board."""
    def __init__(self, game=None):
        self.game = game
        self.p1 = [p for p in game.players if p.id == 1][0]
        self.p2 = [p for p in game.players if p.id == 2][0]
        self.to_move = game.players[0]
        self._board = game.board

'''
TODO(AI): tyler
The above snippet just plays a random piece. This is where you should implement
whatever other AI strategies we want, and call them from main() instead of
Random_Player.
'''

# Play a round of blokus (all players move), then print board.
def play_blokus(blokus):
    # Make one premature call to blokus.play(), initializes board.
    blokus.play();
    
    while blokus.winner() is None:
        blokus.play()
        for player in blokus.players:
            print("Player "+ str(player.id) + " score "+ str(player.score) + ": "
                  + str([sh.id for sh in player.pieces]));
        print('=================================================================');


# Run a blokus game with two players.
# TODO(claire) might want to extend for 2-4 players.
def multi_run(repeat, one, two):
    # Scores for each player
    winner = {1: 0, 2: 0};
    TotalMoveTimes = []

    # Play as many games as indicated by param repeat
    for i in range(repeat):
        print("\nGame", (i + 1), ": Begin!\n")
        global MoveTimes
        MoveTimes = [] # Reset
        order = []; # Reset
        P1 = Player(1, one) # first player
        P2 = Player(2, two) # second player
        
        # add pieces in order from largest to smallest
        all_pieces = [piece.Signpost(), piece.Pole5(), piece.LongLedge(),
            piece.BigHurdle(), piece.Corner(), piece.LongStair(),
            piece.Ledge(),  piece.Fist(), piece.Zigzag(), piece.Bucket(),piece.Tree(), piece.Cross(), piece.Pole4(), piece.ShortCorner(),piece.Stair(), piece.Box(), piece.Hurdle(), piece.Pole3(), piece.TinyCorner(), piece.Pole2(), piece.Pole()];

        board = Board(14, 14);
        order = [P1, P2];
        blokus = Blokus(order, board, all_pieces);
        play_blokus(blokus);

        # End of game display.
        render(blokus.board.state)
        #blokus.board.print_board();
        blokus.play();
        plist = sorted(blokus.players, key = lambda p: p.id);
        for player in plist:
            print("Player "+ str(player.id) + ": "+ str(player.score));
        print("Game end.");
        clearGUI()
        TotalMoveTimes.append(MoveTimes)

    # comment out everything below this if only using non-AI players
    # these are used to calculate stats across all games
    averages = []
    averages_after_two = []
    slowests = []
    fastests = []
    outcome_switcher = {
        1: "W",
        0: "T",
        -1: "L"
    }
    errors = []
    estimate_pairs = []

    # use this loop to try different estimate functions
    for data in EstimateData:
        # corners * pieces
        estimate = data["corners"] * data["pieces"]
        estimate_pairs.append((data["possibles"], estimate))
        if data["possibles"] != 0 and estimate != 0:
            errors.append(abs(data["possibles"] - estimate)/data["possibles"])

    if len(TotalMoveTimes) > 0:
        # print each individual game's stats
        print("\n========================= TIME ANALYSIS =========================")
        for game in TotalMoveTimes:
            # this line should include the outcome
            game_index = TotalMoveTimes.index(game)
            outcome_number = Outcomes[game_index]
            outcome_letter = outcome_switcher.get(outcome_number)
            score = Scores[game_index]
            print("\nGame " + str(game_index + 1) + " (" + outcome_letter + ", " + str(score) + ")")
            print("Move Times:", game)
            average = round(np.mean(game), 2)
            averages.append(average)
            print("Average Move Time: ", average)
            average_after_two = round(np.mean(game[2:]), 2)
            averages_after_two.append(average_after_two)
            print("    After 2 Moves: ", average_after_two)
            slowest = np.amax(game)
            slowests.append(slowest)
            print("Slowest Move:      ", slowest)
            fastest = np.amin(game)
            fastests.append(fastest)
            print("Fastest Move:      ", fastest)

    # print stats over all games
    # include infor about depth, MTC
    # DON'T FORGET TO NOTE OUTCOMES
    print("\n================== STATISTICS ACROSS ALL GAMES ==================\n")
    # print(TotalMoveTimes)
    # print("Game", (TotalMoveTimes.index(game) + 1))
    # print("Move Times:", game)
    print("Depth:             ", Depth)
    print("MovesToConsider:   ", MovesToConsider, "\n")

    games_played = len(Outcomes)
    print("Games Played:      ", games_played)
    games_won = Outcomes.count(1)
    print("Games Won:         ", games_won)
    print("Games Lost:        ", Outcomes.count(-1))
    print("Games Tied:        ", Outcomes.count(0))
    print("Win Rate:          " + str(round((games_won / games_played * 100), 2)) + "%\n")

    print("Average Score:     " + str(round(np.mean(Scores))))
    print("Highest Score:    ", np.amax(Scores))
    print("Lowest Score:     ", np.amin(Scores), "\n")

    print("Average Move Time: ", round(np.mean(averages), 2))
    print("    After 2 Moves: ", round(np.mean(averages_after_two), 2))
    print("Slowest Move:      ", np.amax(slowests))
    print("  Average Slowest: ", round(np.mean(slowests), 2))
    print("Fastest Move:      ", np.amin(fastests))
    print("  Average Fastest: ", round(np.mean(fastests), 2), "\n")

    print("Average Estimate Error:   " + str(round(np.mean(errors), 4)) + "%")
    print("Largest Estimate Error:  " + str(round(np.amax(errors), 4)) + "%")
    print("Smallest Estimate Error:  " + str(round(np.amin(errors), 4)) + "%\n")

    # print("EstimateData:")
    SortedEstimateData = sorted(EstimateData, key=lambda k: k['turn'])
    # for data in SortedEstimateData:
    #     print(data)

    AIEstimatesByTurn = []
    OpponentEstimatesByTurn = []
    smallest_turn = SortedEstimateData[0]["turn"]
    largest_turn = SortedEstimateData[-1]["turn"]

    for i in range(smallest_turn, (largest_turn + 1)):
        possibles = []
        corners = []
        pieces = 0
        estimate = {}
        for data in SortedEstimateData:
            if data["turn"] == i and data["player"] == 2:
                possibles.append(data["possibles"])
                corners.append(data["corners"])
                pieces = data["pieces"]
            elif data["turn"] > i:
                break
        estimate = {
            "turn": i,
            "average possibles": round(np.mean(possibles), 2),
            "average corners": round(np.mean(corners), 2),
            "pieces": pieces
        }
        AIEstimatesByTurn.append(estimate)
    
    for i in range(smallest_turn, (largest_turn + 1)):
        possibles = []
        corners = []
        pieces = 0
        estimate = {}
        for data in SortedEstimateData:
            if data["turn"] == i and data["player"] == 1:
                possibles.append(data["possibles"])
                corners.append(data["corners"])
                pieces = data["pieces"]
            elif data["turn"] > i:
                break
        estimate = {
            "turn": i,
            "average possibles": round(np.mean(possibles), 2),
            "average corners": round(np.mean(corners), 2),
            "pieces": pieces
        }
        OpponentEstimatesByTurn.append(estimate)

    print("AI (P2) Estimate Data")
    for estimate in AIEstimatesByTurn:
        print(estimate)

    print("\nOpponent (P1) Estimate Data")
    for estimate in OpponentEstimatesByTurn:
        print(estimate)

    
    # print("Estimate Pairs:")
    # print(estimate_pairs)
    # print("errors")
    # print(errors)

def main():
    # multi_run(1, Random_Player, Random_Player);
    multi_run(Games, Random_Player, AI_Player);
    # TODO(blokusUI) You need to change this a lot. The player needs to have
    # some sort of while loop here controlling their play. I'd
    # recommend printing out their available pieces, their available corners
    # and just let them select from those arrays. Then you can reuse the print
    # board logic.
    # Actually, what I'd recommend is following the layout of Random_Player.
    # Just do a lot of input prompts there and you only really need to let the
    # player act when they're choosing their piece anyways.

if __name__ == '__main__':
    main();


