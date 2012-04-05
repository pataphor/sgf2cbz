import sgfparser
import itertools
import collections
import copy

class Boards:

    def __init__(self, filename):
        self.game = sgfparser.Sgfparser(filename)
        self.boards = [collections.defaultdict(str)]
        self.color = itertools.cycle('BW')
        self.captured = {'B': [],'W': []}
        for move in self.game.vara:
            D = copy.copy(self.boards[-1])
            D[move] = self.color.next()
            self.boards.append(D)
            other = self.color.next()
            self.color.next()
            for pos in  dead(D,other):
                self.captured[other].append(pos)
                D[pos] = ''
    
def find_liberty(D,pos,color,seen = set()):
    x,y = pos
    adjacent = set([(x-1,y), (x+1,y),(x,y-1),(x,y+1)]) - seen
    for p in adjacent:
        c = D[p]
        if not c:
            return True
        elif c == color:
            seen.add(p)
            if find_liberty(D,p,color,seen):
                return True
    return False
            
def dead(D,color):
    for pos,c in D.items():
        if c == color and not find_liberty(D,pos,color,set()):
            yield pos
            
def test():
    filename = './test13x13.sgf'
    B = Boards(filename)
    size = B.game.boardsize
    endposition = B.boards[-1]
    for i in range(size):
        for j in range(size):
            print endposition[i,j],
        print

if __name__=='__main__':
    test()
