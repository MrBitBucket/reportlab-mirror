
"test canvas coordinate tracking figures should line up"

from reportlab.lib.units import inch

class test0:
    coords = [(1*inch, 1*inch), (3*inch,6*inch), (2*inch, 7*inch), (1*inch, 6*inch), (1.5*inch, 3*inch)]
    def run(self, canv, name, names):
        canv.saveState()
        c.setFillColorRGB(0.7,0.7,1)
        c.setStrokeColorRGB(1,0,1)
        c.drawCentredString(4*inch, 10*inch, "hello world")
        canv.setLineWidth(6)
        coords = self.coords # untransformed coords
        tcoords = [] # transformed coords
        for trans in (1,0):
            canv.saveState()
            if not trans:
                #print "coords", coords
                #print "tcoords", tcoords
                coords = tcoords # trace transformed
                canv.setLineWidth(1)
                canv.setStrokeColorRGB(0.5, 0.5, 0)
            else:
                self.transform(canv)
                # put annotations and links
                canv.bookmarkHorizontal(name, inch, 7*inch)
                canv.drawString(inch, 7*inch, "-- bookmark here --")
                count = 0
                for name in names:
                    thisname = names[count]
                    (x,y) = (3*inch, (8-count)*inch)
                    canv.linkRect(thisname, thisname, Rect=(x,y,x+inch/4,y+inch/4))
                    canv.rect(x,y,inch/4,inch/4)
                    canv.drawString(x,y,"link to "+thisname)
                    count = count+1
            p = canv.beginPath()
            (x0,y0) = coords[0]
            if trans:
                tcoords.append(canv.absolutePosition(x0,y0))
            p.moveTo(x0,y0)
            for (x,y) in coords[1:]:
                p.lineTo(x,y)
                if trans:
                    tcoords.append(canv.absolutePosition(x,y))
            p.close()
            canv.drawPath(p, stroke=1, fill=trans)
            canv.restoreState()
        canv.restoreState()

    def transform(self, canv):
        pass # no transform...

class test1(test0):
    def transform(self, canv):
        canv.translate(inch, 4*inch)
        
class test2(test0):
    def transform(self, canv):
        canv.rotate(-30)
        
class test3(test0):
    def transform(self, canv):
        canv.scale(1.5, 0.75)
        
class test4(test0):
    def transform(self, canv):
        canv.translate(inch, 4*inch)
        canv.rotate(-30)
        canv.scale(1.5, 0.75)
        
class test5(test0):
    def transform(self, canv):
        canv.translate(-2*inch, inch)
        canv.rotate(-30)
        canv.translate(inch, 0)
        canv.skew(10, 10)
        
class test6(test0):
    def transform(self, canv):
        canv.translate(-2*inch, inch)
        canv.rotate(-30)
        canv.translate(inch, 0)
        canv.skew(10, 10)
        canv.resetTransforms() # should return to normal (same as 0)
        
from reportlab.pdfgen import canvas

c = canvas.Canvas("transform_test.pdf")
names = "abcdefg"
count = 0
for test in (test0, test1, test2, test3, test4, test5, test6):
    name = names[count]
    test().run(c, name, names)
    c.showPage()
    count = count+1
c.save()
print "wrote transform_test.pdf"