import boards
import transformer
import Image, ImageDraw
import operator 
import zipfile
import time
import StringIO
import sys
import os

class Converter:
    
    def __init__(self,filename,image_size,rcount):
        B = self.B = boards.Boards(filename)
        self.image_size = image_size
        size = self.size = B.game.boardsize
        w,h = image_size
        viewport = self.viewport= 0,0,w,h
        self.squareboardflag = False
        self.tx=2.2
        self.ty=2.4
        world = self.tilt((0.5, 0.5, size+0.5,size+0.5))
        self.T = transformer.Transformer(world,viewport,rcount)
        self.handicap = {19 :[[4,4],[10,4],[16,4],[4,10],[10,10],
                                            [16,10],[4,16],[10,16],[16,16]],
                                13 :[[4,4],[10,4],[4,10],[10,10]]}
        self.gradients = {'B': 32, 'W': 223}
        self.background = 255
        self.boardcolor = 127
        self.markcolor = {'W': 32, 'B': 223}
        self.stonesize = .49
        self.handicappointsize = 0.2
        self.hps = self.handicappointsize / 2.0 * min(self.tx,self.ty)
        self.ss = self.stonesize / 2.0 * min(self.tx,self.ty)
        self.ms = self.ss / 1.8
        self.pad = 10
        self.world = self.tilt((0.5, 0.5, size+0.5,size+0.5))
        self.image = self.new_image()
        self.draw = self.new_draw()
    
    def new_image(self):
        return Image.new("L",self.image_size,0)
        
    def new_draw(self):
        return  ImageDraw.Draw(self.image)
        
    def line(self,args, fill): 
        pos = self.tilt(args)
        self.draw.line(self.T.twopoints(pos), fill=fill,width = 2)

    def circle(self,args, fill): 
        pos = self.tilt(args)
        a,b,c,d = self.T.twopoints(pos)
        w,h = c-a,d-b
        if w > h:
            e = (w-h)/2
            a,b,c,d =a+e,b,c-e,d
        elif h > w:
            e = (h-w)/2
            a,b,c,d =a,b+e,c,d-e
        self.draw.ellipse((a,b,c,d),fill=fill, 
            outline = self.boardcolor)

    def rectangle(self,args, fill): 
        pos = self.tilt(args)
        self.draw.rectangle(self.T.twopoints(pos),fill)

    def tilt(self,args):
        #to make the board rectangular but not square
        x1,y1,x2,y2 = args
        if not self.squareboardflag:
            tx, ty = self.tx, self.ty
        else:
            m = min(self.tx, self.ty)        
            tx, ty = m, m 
        hs = 0.5 * (self.size+1)
        def scale(x,t):  
            return (x - hs) * t * 0.5
        a,c = scale(x1,tx),scale(x2,tx)
        b,d = scale(y1,ty),scale(y2,ty)
        return a,b,c,d

    def draw_board(self,index):
        self.draw.rectangle(self.viewport,fill=self.background)
        size = self.size
        self.rectangle((1,1,size,size),fill=self.boardcolor)
        self.draw_grid()
        self.draw_handicappoints()
        self.draw_stones(index)
        if index not in [0,len(self.B.boards)-1]:
            self.mark_stone(index)

    def draw_grid(self):
        #draws the lines of the goboard
        size = self.size
        for i in range(1,size+1):
            pos = 1,i,size,i
            self.line(pos, fill=256)
            pos = i,1,i,size
            self.line(pos, fill=255)
        
    def draw_handicappoints(self):
        #paints the starpoints of the goboard
        for x,y in self.handicap.get(self.size,[]):
            box = x-self.hps,y-self.hps,x+self.hps,y+self.hps
            self.circle(box, 255)

    def draw_stones(self,index):
        #paint all stones
        D = self.B.boards[index]
        ss = self.stonesize
        for (x,y),color in D.items():
            if color:
                box = x-ss,y-ss,x+ss,y+ss
                self.circle(box, self.gradients[color])        

    def mark_stone(self,index):
        #marks a stone with two crossed lines
        pos = self.B.game.vara[index-1]
        b = self.B.boards[index]
        color = self.markcolor[b[pos]]
        ms = self.ms
        if not self.squareboardflag:  
            f = self.ty / self.tx
        else: 
            f = 1
        x,y = pos
        a,b,c,d = x-ms,y,x+ms*f,y
        e,f,g,h = x,y-ms,x,y+ms*f
        self.line((e,f,c,d), color)
        self.line((a,b,g,h), color)
        self.line((a,b,c,d), color)
        self.line((e,f,g,h), color)

def sgf2cbz(infile,outfile,size,rcount):
    C = Converter(infile,size,rcount)
    n = len(C.B.boards)
    out = zipfile.ZipFile(outfile, "w")
    now = time.localtime(time.time())[:6]
    for i in range(1,n):
        name = "./sgfpng/%03i.png" %i
        info = zipfile.ZipInfo(name)
        info.date_time = now
        info.compress_type = zipfile.ZIP_DEFLATED
        C.draw_board(i)
        buf = StringIO.StringIO()
        C.image.save(buf, format = "PNG")
        out.writestr(info,buf.getvalue())
        buf.close()
    out.close()

def main():
    infile = sys.argv[1]
    base,ext = os.path.splitext(infile)
    if ext !='.sgf':
        print "I need an .sgf file"
    else:
        outfile = base+'.cbz'
        #width,height of the PNG image
        size = 600, 800
        # 8 possible ways to rotatate or mirror the go board
        rcount = 0
        sgf2cbz(infile,outfile,size,rcount)
         
if __name__=='__main__':
    main()
