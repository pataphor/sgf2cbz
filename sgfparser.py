import string

class Sgfparser:

    def __init__(self, filename):
        self.data = file(filename).read()
        self.markers = '()[]'
        self.markerdict = self.getmarkerdict()
        self.whitespace = ' \a\b\f\n\r\t\v'
        self.coordinates = dict(zip(string.ascii_letters,  range(1,53)))
        self.boardsize = self.getboardsize()
        self.players = self.getplayers()
        self.vara = self.getvariationA()
        self.gameinfo = self.getgameinfo(linelen = 25)
    
    def getmarkerdict(self):
        markers = self.markers
        m = dict([(x,[])  for x in markers])
        it = iter(self.data)
        prev = it.next()
        if prev in markers:  
            m[prev].append(0)
        #ln:  left '[' counter and rn:  right ']' counter
        ln,rn = 0,0
        for i,x in enumerate(it):
            if not prev == '\\' or x  == ']':
                if x in markers:
                    if x == '[':  
                        ln +=1
                    elif  x == ']': 
                        rn +=1
                    #if we are inside ' ['  and ']' ignore unescaped '(' and ')'
                    elif ln > rn:
                        continue
                    m[x].append(i+1)
            prev = x
        return m
    
    def previous(self,i):
        j = i -1
        while j and self.data[j] in self.whitespace:
            j -=1
        return j

    def hasprop1(self,i,p1):
        while i:
            i = self.previous(i)
            if self.data[i] == p1:
                if self.data[self.previous(i)] in ';]':
                    return True
            else: 
                return False
        return False

    def hasprop2(self,i,p2):
        b,a = p2
        while i:
            i = self.previous(i)
            if self.data[i] == a:
                if self.data[i-1] == b:
                    if self.data[self.previous(i-1)] in ';]':
                        return True
            else:
                return False
        return False
        
    def hasBorW(self,i):
        return self.hasprop1(i,'B') or self.hasprop1(i,'W')

    def getcoordinates(self,i):
        while i:
            i = self.previous(i)
            d = self.data[i]
            if d in self.coordinates:
                y = self.coordinates[d]
                d = self.data[self.previous(i)]
                if d in self.coordinates:
                    x = self.coordinates[d]
                    return x,y
            else:
                return self.boardsize+1,self.boardsize+1
        return None
    
    def getvariationA(self):
        res = []
        lnodes = self.markerdict['[']
        rnodes = self.markerdict[']']
        end = self.markerdict[')'][0]
        first =  1
        for i in lnodes:
            if i > end:
                break
            if self.hasBorW(i):
                if first:
                    first = 0
                    self.endinfo = self.previous(i)
                j = lnodes.index(i)
                res.append(self.getcoordinates(rnodes[j]))
        return res
    
    def getgameinfo(self,linelen=40):
        start = self.markerdict['('][0]+1
        while self.data[start] <> ';':   
            start += 1
        info = []
        i = 0
        for c in self.data[start + 1 : self.endinfo]:
            if c == '\n' or  i == linelen:
                if i == linelen: 
                    info.append('\n')
                i = 0
            info.append(c)
            i+=1
        return ''.join(info)

    def getboardsize(self,size=19):
        lnodes = self.markerdict['[']
        rnodes = self.markerdict[']']
        for i in lnodes:
            if self.hasprop2(i,'SZ'):
                j = lnodes.index(i)
                return int(self.data[i+1: rnodes[j]])
            if self.hasBorW(i): 
                break
        return size

    def getplayers(self):
        res = {'PB': 'Unknown', 'PW': 'Unknown'}
        data = self.data
        m = self.markerdict
        lnodes = m['[']
        rnodes = m[']']
        hp2 = self.hasprop2
        hBW = self.hasBorW
        for i in lnodes:
            if hp2(i,'PB'):
                j = lnodes.index(i)
                res['PB'] = data[i+1: rnodes[j]]
            if hp2(i,'PW'):
                j = lnodes.index(i)
                res['PW'] = data[i+1: rnodes[j]]
            if hBW(i):  break
        return res
        
def test():
    filename = './test13x13.sgf'
    s = Sgfparser(filename)
    print s.gameinfo
    print
    print s.players['PB']
    print s.players['PW']
    print
    print s.boardsize
    print
    for x,y in s.vara:  print x,y
    print
        
if __name__=='__main__':
    test()
