# This file was modified from the blokus implementation at
# https://digitalcommons.calpoly.edu/cgi/viewcontent.cgi?article=1305&context=cpesp

import math

# Rotate xcoordinate of object by a degree [90 180 270 360]
def rotatex(pt, refpt, deg):
    return (refpt[0] + (math.cos(math.radians(deg)) * (pt[0] - refpt[0])) +
            (math.sin(math.radians(deg)) * (pt[1] - refpt[1])));

# Rotate ycoordinate of object by a degree [90 180 270 360]
def rotatey(pt, refpt, deg):
    return (refpt[1] + (-math.sin(math.radians(deg))*(pt[0] - refpt[0])) +
            (math.cos(math.radians(deg)) * (pt[1] - refpt[1])));

# Rotate coordinates of a point.
def rotatep(pt, refpt, deg):
    return (int(round(rotatex(pt, refpt, deg))),
            int(round(rotatey(pt, refpt, deg))));


# Represents a Blokus Piece. Each piece has a unique ID and remembers its size so
# player score can be easily calculated. 
class Piece:
    def __init__(self):
        self.id = None;
        self.size = 1;

    # This function will use (x,y) and present points and coordinates to fill out shape
    # on the board.
    def set_points(self, x, y):
        self.points = [];
        self.corners = [];

    # Create the object
    def create(self, num, pt):
        self.set_points(0, 0);
        pm = self.points;
        self.pts_map = pm;

        self.refpt = pt;
        x = pt[0] - self.pts_map[num][0];
        y = pt[1] - self.pts_map[num][1];
        self.set_points(x, y);

    # Rotate the object; any rotations are valid for the board.
    def rotate(self, deg):
        self.points = [rotatep(pt, self.refpt, deg) for pt in self.points];
        self.corners = [rotatep(pt, self.refpt, deg) for pt in self.corners];

    # Flip the board; any flip is valid for the board.
    def flip(self, orientation):
        def flip_h(pt):
            x1 = self.refpt[0];
            x2 = pt[0];
            x1 = (x1 - (x2 - x1));
            return (x1, pt[1]);

        if orientation == 'h':
            self.points = [flip_h(pt) for pt in self.points];
            self.corners = [flip_h(pt) for pt in self.corners];


'''
Define all 21 Blokus Pieces. The IDs are meant to help you think of what the shape looks
like, and I tried my best, but I doubt they're actually helpful.

Ultimately, this implementation is pretty slow compared to other blokus implementations I
saw (using a bit board, or using a mix of 2D arrays), but it was more understandable to me
so I prefer it. We're also not too worried about speed, so it's fine. 
'''
class Pole(Piece):
    def __init__(self):
        '''
        Shape:

        []

        '''
        self.id = 'Pole';
        self.size = 1;

    def set_points(self, x, y):
        self.points = [(x, y)];
        self.corners = [(x + 1, y + 1), (x -1, y -1), (x + 1, y -1),(x -1, y + 1)];

class Pole2(Piece):
    def __init__(self):
        '''
        Shape:

        []
        []

        '''
        self.id = 'Pole2';
        self.size = 2;

    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1)];
        self.corners = [(x -1, y -1), (x + 1, y -1),
                        (x + 1, y + 2),(x -1, y + 2)];

class Pole3(Piece):
    def __init__(self):
        '''
        Shape:

        []
        []
        []

        '''
        self.id = 'Pole3';
        self.size = 3;

    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x, y + 2)];
        self.corners = [(x -1, y -1), (x + 1, y -1), (x + 1, y + 3),
                        (x -1, y + 3)];

class Pole4(Piece):
    def __init__(self):
        '''
        Shape:

        []
        []
        []
        []

        '''
        self.id = 'Pole4';
        self.size = 4;

    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x, y + 2), (x, y + 3)];
        self.corners = [(x -1, y -1), (x + 1, y -1), (x + 1, y + 4),
                        (x -1, y + 4)];

class Pole5(Piece):
    def __init__(self):
        '''
        Shape:

        []
        []
        []
        []
        []

        '''
        self.id = 'Pole5';
        self.size = 5;

    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x, y + 2), (x, y + 3), (x, y + 4)];
        self.corners = [(x -1, y -1), (x + 1, y -1), (x + 1, y + 5),
                        (x -1, y + 5)];

class TinyCorner(Piece):
    def __init__(self):
        '''
        Shape:

        []
        [][]

        '''
        self.id = 'TinyCorner';
        self.size = 3;

    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x + 1, y)];
        self.corners = [(x -1, y -1), (x + 2, y -1), (x + 2, y + 1),
                        (x + 1, y + 2), (x -1, y + 2)];

class ShortCorner(Piece):
    def __init__(self):
        '''
        Shape:

        []
        []
        [][]

        '''
        self.id = 'ShortCorner';
        self.size = 4;

    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x, y + 2), (x + 1, y)];
        self.corners = [(x -1, y -1), (x + 2, y -1), (x + 2, y + 1),
                        (x + 1, y + 3), (x -1, y + 3)];

class Stair(Piece):
    def __init__(self):
        '''
        Shape:

          [][]
        [][]

        '''
        self.id = 'Stair';
        self.size = 4;

    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x + 1, y + 1), (x -1, y)];
        self.corners = [(x -2, y -1), (x + 1, y -1), (x + 2, y),
                        (x + 2, y + 2), (x -1, y + 2), (x -2, y + 1)];

class Box(Piece):
    def __init__(self):
        '''
        Shape:

        [][]
        [][]

        '''
        self.id = 'Box';
        self.size = 4;

    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x + 1, y + 1), (x + 1, y)];
        self.corners = [(x -1, y -1), (x + 2, y -1), (x + 2, y + 2),
                        (x -1, y + 2)];

class LongLedge(Piece):
    def __init__(self):
        '''
        Shape:

        []
        [][][][]

        '''
        self.id = 'LongLedge';
        self.size = 5;

    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x + 1, y), (x + 2, y), (x + 3, y)];
        self.corners = [(x -1, y -1), (x + 4, y -1), (x + 4, y + 1),
                        (x + 1, y + 2), (x -1, y + 2)];

class BigHurdle(Piece):
    def __init__(self):
        '''
        Shape:

          []
          []
        [][][]

        '''
        self.id = 'BigHurdle';
        self.size = 5;

    def set_points(self, x, y):
        self.points= [(x, y), (x, y + 1), (x, y + 2), (x -1, y), (x + 1, y)];
        self.corners = [(x + 2, y -1), (x + 2, y + 1), (x + 1, y + 3),
                        (x -1, y + 3), (x -2, y + 1), (x -2, y -1)];

class Corner(Piece):
    def __init__(self):
        '''
        Shape:

        []
        []
        [][][]

        '''
        self.id = 'Corner';
        self.size = 5;

    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x, y + 2), (x + 1, y), (x + 2, y)];
        self.corners = [(x -1, y -1), (x + 3, y -1), (x + 3, y + 1),
                        (x + 1, y + 3), (x -1, y + 3)];

class LongStair(Piece):
    def __init__(self):
        '''
        Shape:

          [][][]
        [][]

        '''
        self.id = 'LongStair';
        self.size = 5;

    def set_points(self, x, y):
        self.points = [(x, y), (x + 1, y), (x + 2, y), (x, y -1), (x -1, y -1)];
        self.corners = [(x + 1, y -2), (x + 3, y -1), (x + 3, y + 1),
                        (x -1, y + 1), (x -2, y), (x -2, y -2)];

class Ledge(Piece):
    def __init__(self):
        '''
        Shape:

            []
        [][][]

        '''
        self.id = 'Ledge';
        self.size = 5;

    def set_points(self, x, y):
        self.points = [(x, y), (x + 1, y), (x + 1, y + 1), (x -1, y),
                       (x -1, y -1)];
        self.corners = [(x + 2, y -1), (x + 2, y + 2), (x, y + 2),
                        (x -2, y + 1), (x -2, y -2), (x, y -2)];

class Hurdle(Piece):
    '''
    Shape:

      []
    [][][]

    '''
    def __init__(self):
        self.id = 'Hurdle';
        self.size = 4;

    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x + 1, y), (x -1, y)];
        self.corners = [(x + 2, y -1), (x + 2, y + 1), (x + 1, y + 2),
                        (x -1, y + 2), (x -2, y + 1), (x -2, y -1)];

class Fist(Piece):
    def __init__(self):
        '''
        Shape:

        [][]
        [][]
        []

        '''
        self.id = 'Fist';
        self.size = 5;

    def set_points(self, x, y):
        self.points = [(x, y), (x + 1, y), (x + 1, y -1), (x, y -1), (x, y -2)];
        self.corners = [(x + 1, y -3), (x + 2, y -2), (x + 2, y + 1),
                        (x -1, y + 1), (x -1, y -3)];

class Zigzag(Piece):
    def __init__(self):
        '''
        Shape:

          [][]
        [][]
        []

        '''
        self.id = 'Zigzag';
        self.size = 5;

    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x + 1, y + 1),
                       (x -1, y),(x -1, y -1)];
        self.corners = [(x + 1, y -1), (x + 2, y), (x + 2, y + 2),
                        (x -1, y + 2), (x -2, y + 1), (x -2, y -2), (x, y -2)];

class Bucket(Piece):
    def __init__(self):
        '''
        Shape:

        [][]
        []
        [][]

        '''
        self.id = 'Bucket';
        self.size = 5;

    def set_points(self, x, y):
        self.points= [(x, y), (x, y + 1), (x + 1, y + 1), (x, y -1),
                      (x + 1, y -1)];
        self.corners = [(x + 2, y -2), (x + 2, y), (x + 2, y + 2),
                        (x -1, y + 2), (x -1, y -2)];

class Tree(Piece):
    def __init__(self):
        '''
        Shape:

          [][]
        [][]
          []

        '''
        self.id = 'Tree';
        self.size = 5;

    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x + 1, y + 1), (x, y -1),
                       (x -1, y)];
        self.corners = [(x + 1, y -2), (x + 2, y), (x + 2, y + 2),
                        (x -1, y + 2), (x -2, y + 1), (x -2, y -1), (x -1, y -2)];

class Cross(Piece):
    def __init__(self):
        '''
        Shape:

          []
        [][][]
          []

        '''
        self.id = 'cross';
        self.size = 5;

    def set_points(self, x, y):
        self.points = [(x,y), (x, y+1), (x+1, y), (x-1, y), (x, y-1)];
        self.corners = [(x+1, y-2), (x+2, y-1), (x+2, y+1), (x+1, y+2),
                        (x-1, y+2), (x-2, y+1), (x-2, y-1), (x-1, y-2)];


class Signpost(Piece):
    def __init__(self):
        '''
        Shape:
        
          []
        [][][][]
        
        '''
        self.id = 'signpost';
        self.size = 5;

    def set_points(self, x, y):
        self.points = [(x, y), (x, y+1), (x+1, y), (x+2, y), (x-1, y)];
        self.corners = [(x+3, y-1), (x+3, y+1), (x+1, y+2), (x-1, y+2),
                        (x-2, y+1), (x-2, y-1)];
