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

# necessary?
count = 0
testing = 0
BigInitialValue = 1000000
P1 = 1
P2 = 2
TotalStartingSize = 89

def opponent(player):
    if player == 1:
        return 2
    elif player == 2:
        return 1
    else:
        print("Oooooooooooooooops")

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
            # MARKER
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
        # print("Winner has found ", moves)

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

    def make_move(self, move, state):
        "Return a new BoardState reflecting move made from given board state."
        # we don't want to adjust the prime BoardState copy here, but we need to update board, game, and player info

        # SOLUTION: copy everything again into a newboard that starts off as a copy but gets updated with post-move new state stats

        # need to update board with move, whose turn it is, and current player's new stats

        # at this point, at least one move has been made, winner is known to be None, and a vaild move has been passed in

        newboard = copy.deepcopy(state)

        current = newboard.to_move; # get current player
        proposal = move; # get the next move based on
                                            # the player's strategy

        # update the board and the player status
        newboard._board.update(current.id, proposal.points);
        current.update_player(proposal, newboard._board);
        current.remove_piece(proposal); # remove used piece
        # put the current player to the back of the queue
        # this may result in some references to copies?
        first = newboard.game.players.pop(0);
        newboard.game.players += [first];
        newboard.game.rounds += 1; # update game round
        newboard._moves = newboard.game.players[0].possible_moves(newboard.game.players[0].pieces, newboard.game)
        return newboard
    
    def to_move(self, state):
        "Return the player whose move it is in this state."
        return state.to_move

    def successors(self, state):
        "Return a list of legal (move, state) pairs."
        m = [(move, self.make_move(move, state))
                for move in self.legal_moves(state)]
        return m
    
    def legal_moves(self, boardstate):
        return boardstate.legal_moves()

    def terminal_test(self, state):
        "Return True if this is a final state for the game."
        return not self.legal_moves(state)

    # gets called in ab on new states
    def calculate_utility(self):
        current = self.players[0]
        sum = 0
        # count the number of squares in all remaining pieces
        for p in current.pieces:
            sum += p.size
        # small sum => high utility
        return TotalStartingSize - sum

    def utility(self, boardstate, player):
        "This is where your utility function gets called."
        return self.calculate_utility()

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

# should resemble MyPlayer and use fxns from ai_helper, may need to adjust params. seems like a new obj will need to be created just for each special state
def AI_Player(player, game):
    opponent = None
    for p in game.players:
        if player.id != p.id:
            opponent = p
    p1_copy = copy.deepcopy(opponent)
    p2_copy = copy.deepcopy(player)
    game_copy = copy.deepcopy(game)
    # let's say AI is always P2 (so P2 in code)

    # player.id is an int
    # calculate_utility returns an int (0, 89)
    # game.state.board returns the board array thing
    # possible_moves is an array of Piece objs that represent moves

    #every time it's my turn, transform current info into appropriate state and game to be used only within ab search:
    # old: boardstate = BoardState(player.id, calculate_utility(player, game), game.state.board, player.possible_moves(player.pieces, game))
    boardstate = BoardState(game_copy, p1_copy, p2_copy, game.calculate_utility())

    #this is called to do the following for every move:
    #perform alphabeta search and return the output, which should be in the form of a Piece with move info
    return alphabeta_search(boardstate, game_copy, 4, None, None)
    #note: other code already takes care of making the actual move ingame

def alphabeta_search(state, game, d=4, cutoff_test=None, eval_fn=None):
    """Search game to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""
    global count
    global testing
    global BigInitialValue
    
    player = game.to_move(state)
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
        succ = game.successors(state)
        count = count + len(succ)
        if testing:
            print("  "*depth, "maxDepth: ", depth, "Total:", count, "Successors: ", len(game.successors(state)))
        for (a, s) in succ:
            # Decide whether to call max_value or min_value, depending on whose move it is next.
            # Some games, such as Mancala, sometimes allow the same player to make multiple moves.
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
        succ = game.successors(state)
        count = count + len(succ)
        if testing:
            print("  "*depth, "minDepth: ", depth, "Total:", count, "Successors: ", len(game.successors(state)))
        for (a, s) in succ:
            # Decide whether to call max_value or min_value, depending on whose move it is next.
            # Some games, such as Mancala, sometimes allow the same player to make multiple moves.
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
        if s.to_move == state.to_move:
            return max_value(s, -BigInitialValue, BigInitialValue, 0)
        else:
            return min_value(s, -BigInitialValue, BigInitialValue, 0)

    # Body of alphabeta_search starts here:
    # The default test cuts off at depth d or at a terminal state
    cutoff_test = (cutoff_test or
                   (lambda state,depth: depth>d or game.terminal_test(state)))
    eval_fn = eval_fn or (lambda state: game.utility(state, player.id))
    # MARKER things should work up to here
    action, state = argmax(game.successors(state),
                           # lambda ((a, s)): right_value(s, -BigInitialValue, BigInitialValue, 0))
                            lambda a_s: right_value(a_s[1], -BigInitialValue, BigInitialValue, 0))
    print("Final count: ", count)
    return action

class BoardState:
    """Holds one state of the Mancala board."""
    def __init__(self, game=None, p1=None, p2=None, utility=None):
        self.game = game
        self.p1 = p1
        self.p2 = p2
        # current player should be known as game.players[0]
        self.to_move = game.players[0]
        self._utility =  utility
        self._board = game.board
        self._moves = game.players[0].possible_moves(game.players[0].pieces, game)

    def getPlayer(self):
        return self.to_move

    def legal_p(self, move):
        "A legal move must involve a position with pieces."
        if self._board[move] > 0:
            return True
        else:
            return None

    def legal_moves(self):
        "Return a list of legal moves for player."
        return self._moves

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
        render(blokus.board.state)
        #blokus.board.print_board();
        for player in blokus.players:
            print("Player "+ str(player.id) + " score "+ str(player.score) + ": "
                  + str([sh.id for sh in player.pieces]));
        print('=================================================================');


# Run a blokus game with two players.
# TODO(claire) might want to extend for 2-4 players.
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

def main():
    # multi_run(1, Random_Player, Random_Player);
    multi_run(1, Random_Player, AI_Player);
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


