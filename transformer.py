class Transformer:

    def __init__(self, world, viewport, rcount):
        a,b,c,d = map(float,world)
        e,f,g,h = map(float,viewport)
        wxc = self.wxc = (a + c)/2
        wyc = self.wyc = (b + d)/2
        vxc, vyc =  (e + g)/2, (f + h)/2
        mf = self.mf = min((g-e) / (c-a) , (h-f) / (d-b))
        self.xc = vxc - mf * wxc
        self.yc = vyc - mf * wyc
        self.x_min,  self.y_min = a, b
        self.x_max, self.y_max = c, d
        self.flip, self.rcount = divmod(rcount,4)

    def twopoints(self, worldcoordinates):
        #unpack and convert from worldcoordinates into viewportcoordinates
        x1,y1,x2,y2 = worldcoordinates
        mf,xc,yc = self.mf, self.xc, self.yc
        if self.rcount == 1:
            y1,y2 = self.mirror("x",y1,y2)
            x1,y1 = self.diagonal("d2",x1,y1)
            x2,y2 = self.diagonal("d2",x2,y2)
        elif self.rcount == 2:
            x1,x2 = self.mirror("y",x1,x2)
            y1,y2 = self.mirror("x",y1,y2)
        elif self.rcount == 3:
            x1,x2 = self.mirror("y",x1,x2)
            x1,y1 = self.diagonal("d2",x1,y1)
            x2,y2 = self.diagonal("d2",x2,y2)
        if self.flip:  x1,x2 = self.mirror("y",x1,x2)            
        X1 = mf * x1 + xc
        Y1 = mf * y1 + yc
        X2 = mf * x2 + xc
        Y2 = mf * y2 + yc
        return X1 , Y1, X2 , Y2
    
    def mirror(self,axis,*vals):
        #mirror vals through one of the world's  axes
        res = []
        if axis == "y":  mm = self.x_min + self.x_max
        elif axis == "x":  mm = self.y_min + self.y_max
        for c in vals:  res.append(mm-c)
        return tuple(res)
    
    def diagonal(self, axis, *point):
        #mirror a point through a diagonal of the world
        x,y = point
        wxc = self.wxc
        wyc = self.wyc
        dx,dy = x-wxc,y-wyc
        if axis == "d1": dy = -dy
        if axis == "d2": dx = -dx
        return wyc + dy, wxc - dx

def test():
    n = 5
    it = iter(range(n*n))
    M = [[it.next() for i in range(n)] for j in range(n)]
    for row in M:
        for j in row:
            print "%02i" %j,
        print
    print
    world = viewport = 0,0,n-1,n-1
    T = Transformer(world,viewport, rcount = 7)
    for i in range(n):
        for j in range(n):
            a,b,c,d = T.twopoints((i,j,i,j))
            print "%02i" %M[int(a)][int(b)],
        print
 
if __name__=='__main__':
    test()
