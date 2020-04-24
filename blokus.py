# Some functions are modified from the source listed in piece.py
# (the functions that handle the Piece objects).

import sys
import math
import random
import copy
import piece
from gui import *

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

    #Add the player's initial pieces for a game
    def add_pieces(self, pieces):
        random.shuffle(pieces);
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

    # Get the next movebased off of the player's strategy
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
        # get all possible moves for all players
        moves = [p.possible_moves(p.pieces, self) for p in self.players];

        # check how many rounds the total available moves from all players
        # are the same and increment the counter if so
        if self.previous == sum([len(mv) for mv in moves]):
            self.repeat += 1;
        else:
            self.repeat = 0;

        # if there is still moves possible or total available moves remain
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

    # Check if a player's move is valid, including board bounds, pieces' overlap,
    # adjacency, and corners.
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

    # Play the game with the list of player sequentially until the
    # game ended (no more pieces can be placed for any player)
    def play(self):
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
        else: # a winner (or tied) is found
            if len(winner) == 1: # if the game results in a winner
                self.win_player = winner[0];
                print('Game over! The winner is: '+ str(winner[0]));
            else: # if the game results in a tie
                print('Game over! Tied between players: '+ ', '.join(map(str, winner)));

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
    #clearGUI()


# Run a blokus game with two players.
def multi_run(repeat, one, two):
    # Scores for each player
    winner = {1: 0, 2: 0};

    # Play as many games as indicated by param repeat
    for i in range(repeat):
        order = []; # Reset
        P1 = Player(1, one) # first player
        P2 = Player(2, two) # second player
        
        all_pieces = [piece.Signpost(), piece.Pole(), piece.Pole2(), piece.Pole3(),
                      piece.Pole4(), piece.Pole5(), piece.TinyCorner(),
                      piece.ShortCorner(), piece.Stair(), piece.Box(),
                      piece.LongLedge(), piece.BigHurdle(), piece.Corner(),
                      piece.LongStair(), piece.Ledge(), piece.Hurdle(),
                      piece.Fist(), piece.Zigzag(), piece.Bucket(),
                      piece.Tree(), piece.Cross()];

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

def main():
    multi_run(1, Random_Player, Random_Player);
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


