# This file has functions modified from the blokus implementation at
# https://digitalcommons.calpoly.edu/cgi/viewcontent.cgi?article=1305&context=cpesp
# Those functions will be marked with a #DC (digital commons) comment. Functions
# that were copied by modified will have a #DC-Claire comment.

'''
Blokus AI
CS 480 Spring 2020
Claire Fuchs, Senay Teclebrhan, Tyler Acosta, Andrew Flynn
'''

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

# cutoff depth for alphabeta minimax search (default 2)
Depth = 2
# number of successor states returned (default 4)
MovesToConsider = 4
# change to adjust the number of games played (defualt 10)
Games = 1

# taken from mancala.py, used for alphabeta search
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
ActualEstimatePairs = []
UselessInit = {
    'signpost': 0,
    'Pole5': 0,
    'LongLedge': 0,
    'BigHurdle': 0,
    'Corner': 0,
    'LongStair': 0,
    'Ledge': 0,
    'Fist': 0,
    'Zigzag': 0,
    'Bucket': 0,
    'Tree': 0,
    'cross': 0,
    'Pole4': 0,
    'ShortCorner': 0,
    'Stair': 0,
    'Box': 0,
    'Hurdle': 0,
    'Pole3': 0,
    'TinyCorner': 0,
    'Pole2': 0,
    'Pole': 0
}
AIUseless = UselessInit
OpponentUseless = UselessInit

# Blokus Board
# DC-Claire
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


# Player Class
# DC-Claire
class Player:
    def __init__(self, id, strategy):
        self.id = id # player's id
        self.pieces = [] # player's unused game piece, list of Pieces
        self.corners = set() # current valid corners on board
        self.strategy = strategy # player's strategy
        self.score = 0 # player's current score
        self.is_blocked = False

    # Add the player's initial pieces for a game
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
    def possible_moves(self, pieces, game):
        # Updates the corners of the player, in case the
        # corners have been covered by another player's pieces.
        self.corners = set([(x, y) for(x, y) in self.corners
                            if game.board.state[y][x] == '_']);

        placements = [] # a list of possible placements
        visited = [] # a list placements (a set of points on board)

        # Check every available corner
        for cr in self.corners:
            # Check every available piece
            for sh in pieces:
                # Check every reference point the piece could have
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
                                    placements.append(candidate);
                                    visited.append(set(candidate.points));
        return placements;

    # Tyler - AI implementation
    # variant of possible_moves used when calling from winner
    # this updates global dicts of useless corner counts for each piece
    def possible_moves_winner(self, pieces, game, pid):
        global AIUseless
        global OpponentUseless
        reset = {
            'signpost': 0,
            'Pole5': 0,
            'LongLedge': 0,
            'BigHurdle': 0,
            'Corner': 0,
            'LongStair': 0,
            'Ledge': 0,
            'Fist': 0,
            'Zigzag': 0,
            'Bucket': 0,
            'Tree': 0,
            'cross': 0,
            'Pole4': 0,
            'ShortCorner': 0,
            'Stair': 0,
            'Box': 0,
            'Hurdle': 0,
            'Pole3': 0,
            'TinyCorner': 0,
            'Pole2': 0,
            'Pole': 0
        }
        # if this is being called for opponent
        if pid == 1:
            # reset previous useless values to 0
            OpponentUseless = reset
            # Updates the corners of the player, in case the
            # corners have been covered by another player's pieces.
            self.corners = set([(x, y) for(x, y) in self.corners
                                if game.board.state[y][x] == '_']);

            placements = [] # a list of possible placements
            visited = [] # a list placements (a set of points on board)

            # Check every available corner
            for cr in self.corners:
                # Check every available piece
                for sh in pieces:
                    corner_is_useless = True
                    # Check every reference point the piece could have
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
                                        corner_is_useless = False
                                        placements.append(candidate);
                                        visited.append(set(candidate.points));
                    if corner_is_useless:
                        OpponentUseless[sh.id] += 1
            return placements;
        # if this is being called for AI player
        elif pid == 2:
            # reset previous useless values to 0
            AIUseless = reset
            # Updates the corners of the player, in case the
            # corners have been covered by another player's pieces.
            self.corners = set([(x, y) for(x, y) in self.corners
                                if game.board.state[y][x] == '_']);

            placements = [] # a list of possible placements
            visited = [] # a list placements (a set of points on board)

            # Check every available corner
            for cr in self.corners:
                # Check every available piece
                for sh in pieces:
                    corner_is_useless = True
                    # Check every reference point the piece could have
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
                                        corner_is_useless = False
                                        placements.append(candidate);
                                        visited.append(set(candidate.points));
                    if corner_is_useless:
                        AIUseless[sh.id] += 1
            return placements;

    # Tyler - AI implementation
    # return the number of all possible placements
    # used when the actual objects aren't needed, faster than possible_moves
    def possible_count(self, pieces, game):
        # Updates the corners of the player, in case the
        # corners have been covered by another player's pieces.
        self.corners = set([(x, y) for(x, y) in self.corners
                            if game.board.state[y][x] == '_']);
        counter = 0
        visited = [] # a list placements (a set of points on board)

        # Check every available corner
        for cr in self.corners:
            # Check every available piece
            for sh in pieces:
                # Check every reference point the piece could have
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

    # Tyler - AI implementation
    # Get a list of up to cutoff plausible placements
    # faster than calculating all possible_moves and then selecting a few
    def plausible_moves(self, pieces, game, cutoff, pid):
        placements = []
        for piece in pieces:
            possibles = self.possible_moves([piece], game)
            if possibles != []:
                for possible in possibles:
                    placements.append(possible)
                    if len(placements) == cutoff:
                        return placements
        return placements

    # Get the next move based off of the player's strategy
    def next_move(self, game):
        return self.strategy(self, game);

# Blokus Game class
# DC-Claire
class Blokus:
    def __init__(self, players, board, all_pieces):
        self.players = players; 
        self.rounds = 0; 
        self.board = board; 
        self.all_pieces = all_pieces; 
        self.previous = 0;
        # counter for how many times the total available moves are the same by checking previous round
        self.repeat = 0; 
        self.win_player = 0; # winner

    # Check for the winner (or a tie) in the game + return the winner's id.
    # Or return nothing if the game can still progress
    def winner(self):
        # calculate possible moves for both players
        moves = []
        # Tyler - AI implementation (following loop)
        for p in self.players:
            possibles = p.possible_moves_winner(p.pieces, self, p.id)
            # update flag if a player is completely blocked
            if len(possibles) == 0:
                p.is_blocked = True
            moves.append(possibles)

        # check how many rounds the total available moves from all players
        # are the same and increment the counter if so
        if self.previous == sum([len(mv) for mv in moves]):
            self.repeat += 1;
        else:
            self.repeat = 0;

        # if there are still moves possible or total available moves remain
        # static for too many rounds (repeat reaches over a certain threshold)
        if False in[len(mv) == 0 for mv in moves] and self.repeat < 4:
            self.previous = sum([len(mv) for mv in moves]);
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
                # 1 represents an AI win
                if winner[0] == 2:
                    Outcomes.append(1)
                # -1 represents an opponent win
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

    # Tyler - AI implementation, abstract method from mancala.py ab search
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

    # Tyler - AI implementation, abstract method from mancala.py ab search
    def successors(self, state):
        "Return a list of legal (move, state) pairs."
        # find and return up to MovesToConsider possible moves as successors
        m = [(move, self.make_move(move, state))
                for move in state.to_move.plausible_moves(state.to_move.pieces, state.game, MovesToConsider, state.to_move.id)]
        return m

    # Tyler - AI implementation, abstract method from mancala.py ab search
    def terminal_test(self, state):
        "Return True if this is a final state for the game."
        # if we have no moves left, it's effectively a final state
        return not state.to_move.plausible_moves(state.to_move.pieces, state.game, 1, state.to_move.id)

    # Tyler - AI implementation, abstract method from mancala.py ab search
    # gets called in ab search on new states
    def utility(self, state, actual_turn_number):
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
            # turn number in this successor state is calculated by taking 21 - number of pieces + 1 (offset)
            ai_piece_count = len(ai_player.pieces)
            ai_turn_number = (TotalStartingPieces - ai_piece_count + 1)
            ai_corners = len(ai_player.corners)

            # estimate how many possible moves we have
            ai_estimate = 0
            for piece in ai_player.pieces:
                estimate = int(piece.uniques * (ai_corners - AIUseless[piece.id]) * ((ai_corners - AIUseless[piece.id]) / ai_corners))
                ai_estimate += estimate


            # add a point for every possible move we have
            total += ai_estimate

            # if opponent has possible moves
            if not opponent.is_blocked:
                # turn number in this successor state is calculated by taking 21 - number of pieces + 1 (offset)
                opponent_piece_count = len(opponent.pieces)
                opponent_turn_number = (TotalStartingPieces - opponent_piece_count + 1)
                opponent_corners = len(opponent.corners)

                # estimate how many possible moves opponent has
                opponent_estimate = 0
                for piece in opponent.pieces:
                    estimate = int(piece.uniques * (opponent_corners - OpponentUseless[piece.id]) * ((opponent_corners - OpponentUseless[piece.id]) / opponent_corners))
                    opponent_estimate += estimate

                # subtract a point for every possible move our opponent has
                total -= opponent_estimate
            # skip endgame calculations if more than 1 piece
            if ai_piece_count > 1:
                return total
            # if the monomino is the last one, add 500 bonus points
            elif ai_piece_count == 1:
                if ai_player.pieces[0].size == 1:
                    total += 500
            # if no pieces are left, add 1500 bonus points
            elif ai_piece_count == 0:
                total += 1500
        return total

    # This function will prompt the user for their piece
def piece_prompt(options):
    # Create an array with the valid piece names
    option_names = [str(x.id) for x in options];

    # Prompt the user for their choice
    print("\nIt's your turn! Select one of the following options:");
    choice = 0;
    
    # While they haven't chosen a valid piece...
    while (choice != 2):
        print("     1 - See available pieces.");
        print("     2 - Choose a piece.");

        # Get their choice. If they don't enter an integer, handle the exception
        try:
            choice = int(input("Choice: "));
        except:
            # Do nothing; choice = 0, so the user will be prompted again
            pass;

        # Once they've entered a choice, perform the desired actions
        print("");
        if (choice == 1): # Print the available pieces
            for x in option_names:
                print(x);
            print("\nSelect one of the following options:");

        elif (choice == 2): # Request the user's piece
            piece = input("Choose a piece: ");
            print("");
            if piece in option_names:  # If the piece name is valid, retrieve the piece object
                if (len(options) == 21 and piece == "cross"): # They can't open with a cross
                    print("INVALID PIECE (You can't open with a cross...). Please try again:");
                    choice = 0;
                else:
                    i = option_names.index(piece);
                    piece = options[i];
            else:
                print("INVALID PIECE. Please try again:");
                choice = 0;

        else: # If the user doesn't request the list of pieces or choose a piece
            print("INVALID CHOICE. Please try again:");

    # Once they've chosen a piece...
    return piece;

# This function will prompt the user for their placement
def placement_prompt(possibles):
    choice = -1; # An invalid "choice" to start the following loop

    # While the user hasn't chosen a valid placment...
    while (choice < 1 or choice > len(possibles)):
        count = 1; # Used to index each placement; initialized to 1
        # Prompt the user for their placement
        print("Select one of the following placements:")
        for x in possibles:
            print("     " + str(count) + " - " + str(x.points));
            count += 1;

        # See if the user enters an integer; if they don't, handle the exception
        try:
            choice = int(input("Choose a placement: "));
        except:
            # Do nothing; if the user doesn't enter an integer, they will be prompted again
            pass;
        print("");

    # Once they've made a valid placement...
    placement = possibles[choice - 1];
    return placement;    

# Random Strategy: choose an available piece randomly
# DC
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

# Tyler - AI implementation, created a better opponent to test against
# Largest Strategy: play a random available move for the largest piece possible
def Largest_Player(player, game):
    # pieces are already in order from largest to smallest
    # iterate through and make the first possible move
    for p in player.pieces:
        possibles = player.possible_moves([p], game)
        if len(possibles) != 0: # if there is possible moves
            return random.choice(possibles);
    # if no possible moves are found, return None
    return None

# Human Strategy: choose an available piece and placement based on user input
def Human_Player(player, game):
    options = [p for p in player.pieces];
    while len(options) > 0: # if there are still possible moves
        piece = piece_prompt(options);
        possibles = player.possible_moves([piece], game);
        if len(possibles) != 0: # if there is possible moves
            return placement_prompt(possibles);
        else: # no possible move for that piece
            options.remove(piece); # remove it from the options
    return None; # no possible move left

# Tyler - AI implementation
# AI Strategy: choose a move based on utility using alphabeta minimax search
# named after Jeff Barasona, creator of the Barasona opening our AI uses
def Jeffbot(player, game):
    # track start time for use in post-game move time analysis
    start_time = time.time()
    # determine what turn we're on
    turn_number = (TotalStartingPieces - len(player.pieces) + 1)
    # the mighty Barasona
    if turn_number == 1:
        tree = piece.Tree()
        tree.points = [(12, 12), (12, 13), (13, 13), (12, 11), (11, 12)]
        tree.corners = [(13, 10), (14, 12), (14, 14), (11, 14), (10, 13), (10, 11), (11, 10)]
        tree.pts_map = [(0, 0), (0, 1), (1, 1), (0, -1), (-1, 0)]
        tree.refpt = (13, 13)
        return tree
    elif turn_number == 2:
        cross = piece.Cross()
        cross.points = [(10, 10), (11, 10), (10, 11), (10, 9), (9, 10)]
        cross.corners = [(8, 11), (9, 12), (11, 12), (12, 11), (12, 9), (11, 8), (9, 8), (8, 9)]
        cross.pts_map = [(0, 0), (0, 1), (1, 0), (-1, 0), (0, -1)]
        cross.refpt = (11, 10)
        return cross
    # include valid move checks for the next two moves
    elif turn_number == 3:
        zigzag = piece.Zigzag()
        zigzag.points = [(8, 8), (8, 9), (7, 9), (9, 8), (9, 7)]
        zigzag.corners = [(7, 7), (6, 8), (6, 10), (9, 10), (10, 9), (10, 6), (8, 6)]
        zigzag.pts_map = [(0, 0), (0, 1), (1, 1), (-1, 0), (-1, -1)]
        zigzag.refpt = (8, 9)
        if game.valid_move(player, zigzag.points):
            return zigzag
    elif turn_number == 4:
        signpost = piece.Signpost()
        signpost.points = [(7, 6), (7, 7), (6, 6), (5, 6), (8, 6)]
        signpost.corners = [(4, 5), (4, 7), (6, 8), (8, 8), (9, 7), (9, 5)]
        signpost.pts_map = [(0, 0), (0, 1), (1, 0), (2, 0), (-1, 0)]
        signpost.refpt = (7, 7)
        if game.valid_move(player, signpost.points):
            return signpost

    # if no possible moves in this state, return None
    # plausible_moves returns a possible move (if any) faster than possble_moves
    if not player.plausible_moves(player.pieces, game, 1, player.id):
        return None; # no possible move left

    # copy current game info into a BoardState to be used within ab search
    game_copy = copy.deepcopy(game)
    state = BoardState(game_copy)
    # perform alphabeta search and return a useful move
    return alphabeta_search(state, Depth, None, None, start_time, turn_number)

# Tyler - AI implementation, taken from mancala.py
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

    def argmin(seq, fn):
        """Return an element with lowest fn(seq[i]) score; tie goes to first one.
        >>> argmin(['one', 'to', 'three'], len)
        'to'
        """
        best = seq[0]; best_score = fn(best)
        for x in seq:
            x_score = fn(x)
            if x_score < best_score:
                best, best_score = x, x_score
        return best

    def argmax(seq, fn):
        """Return an element with highest fn(seq[i]) score; tie goes to first one.
        >>> argmax(['one', 'to', 'three'], len)
        'three'
        """
        return argmin(seq, lambda x: -fn(x))

    # Body of alphabeta_search starts here:
    cutoff_test = (cutoff_test or
                   (lambda state,depth: depth>d or state.game.terminal_test(state)))
    eval_fn = eval_fn or (lambda state: state.game.utility(state, turn_number))
    action, state = argmax(state.game.successors(state),
                            lambda a_s: right_value(a_s[1], -BigInitialValue, BigInitialValue, 0))

    # calculate move time, round to 2 decimal places, store for analysis
    MoveTimes.append(round(time.time() - start_time, 2))
    return action

# Tyler - AI implementation, based off of BoardState from mancala.py
class BoardState:
    """Holds one state of the Blokus board, used to generate successors."""
    def __init__(self, game=None):
        self.game = game
        self.p1 = [p for p in game.players if p.id == 1][0]
        self.p2 = [p for p in game.players if p.id == 2][0]
        # to_move keeps track of the player whose turn it is to move
        self.to_move = game.players[0]
        self._board = game.board

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
# DC-Claire
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
        
        # Tyler - AI implementation
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
        blokus.play();
        plist = sorted(blokus.players, key = lambda p: p.id);
        for player in plist:
            print("Player "+ str(player.id) + ": "+ str(player.score));
        print("Game end.");
        clearGUI()
        TotalMoveTimes.append(MoveTimes)

    # Tyler - AI implementation, calculate stats to evaluate AI performance
    # used to calculate game stats
    averages = []
    averages_after_two = []
    slowests = []
    fastests = []
    outcome_switcher = {
        1: "W",
        0: "T",
        -1: "L"
    }

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
            print("    After 2 Moves:   ", average_after_two)
            slowest = np.amax(game)
            slowests.append(slowest)
            print("Slowest Move:      ", slowest)
            fastest = np.amin(game)
            fastests.append(fastest)
            print("Fastest Move:      ", fastest)

    # print stats across all games
    print("\n================== STATISTICS ACROSS ALL GAMES ==================\n")
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
    print("  After 2 Moves:   ", round(np.mean(averages_after_two), 2))
    print("Slowest Move:      ", np.amax(slowests))
    print("  Average Slowest: ", round(np.mean(slowests), 2))
    print("Fastest Move:      ", np.amin(fastests))
    print("  Average Fastest: ", round(np.mean(fastests), 2), "\n")

def main():
    # NOTE: Jeffbot allows the other (human) player to move first because he
    # is polite (and hard-coded that way)
    multi_run(Games, Human_Player, Jeffbot);

if __name__ == '__main__':
    main();


