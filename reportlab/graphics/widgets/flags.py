#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/widgets/flags.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/widgets/flags.py,v 1.5 2001/05/17 16:21:33 rgbecker Exp $
# Flag Widgets - a collection of flags as widgets
# author: John Precedo (johnp@reportlab.com)

"""This file is a collection of flag graphics as widgets.

All flags are represented at the ratio of 1:2, even where the official ratio for the flag is something else
(such as 3:5 for the German national flag). The only exceptions are for where this would look _very_ wrong,
such as the Danish flag whose (ratio is 28:37), or the Swiss flag (which is square).

Unless otherwise stated, these flags are all the 'national flags' of the countries, rather than their
state flags, naval flags, ensigns or any other variants. (National flags are the flag flown by civilians
of a country and the ones usually used to represent a country abroad. State flags are the variants used by
the government and by diplomatic missions overseas).

To check on how close these are to the 'official' representations of flags, check the World Flag Database at 
http://www.flags.ndirect.co.uk/

The flags this file contains are:

EU Members:
United Kingdom, Austria, Belgium, Denmark, Finland, France, Germany, Greece, Ireland, Italy, Luxembourg,
Holland (The Netherlands), Spain, Sweden

Others:
USA, Czech Republic, European Union, Switzerland, Turkey
"""

from reportlab.lib import colors
from reportlab.lib.validators import *
from reportlab.lib.attrmap import *
from reportlab.graphics import shapes
from reportlab.graphics.widgetbase import Widget
from reportlab.graphics import renderPDF
from signsandsymbols import ETriangle0


class Star0(ETriangle0):
    """This draws a 5-pointed star.

        possible attributes:
        'x', 'y', 'size', 'color', 'strokecolor'

        """

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.color = colors.yellow
        self.strokecolor = None

    def demo(self):
        D = shapes.Drawing(200, 100)
        et = Star0()
        et.x=50
        et.y=0
        et.draw()
        D.add(et)
        labelFontSize = 10
        D.add(shapes.String(et.x+(et.size/2),(et.y-(1.2*labelFontSize)),
                            et.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group()
        
        # star specific bits
        star = shapes.Polygon(points = [
            self.x+(s/5), self.y,
            self.x+((s/5)*1.5), self.y+((s/5)*2.05),
            self.x,self.y+((s/5)*3),
            self.x+((s/5)*1.95),self.y+((s/5)*3),
#            self.x+((s/5)*2.05),self.y+((s/5)*3),
            self.x+(s/2), self.y+s,
            self.x+((s/5)*3.25),self.y+((s/5)*3),
            self.x+s,self.y+((s/5)*3),
            self.x+(s-((s/5)*1.5)), self.y+((s/5)*2.05),
            self.x+s-(s/5), self.y,
            self.x+(s/2), self.y+(s/5),
            ],
               fillColor = self.color,
               strokeColor = self.strokecolor,
               strokeWidth=s/50)
        g.add(star)
        
        return g



class Flag0(ETriangle0):
    """This is a generic flag class that all the flags in this file use as a basis.
    
        This class basically provides edges and a tidy-up routine to hide any bits of
        line that overlap the 'outside' of the flag

        possible attributes:
        'x', 'y', 'size', 'background'
    """ 

    _attrMap = AttrMap(BASE=ETriangle0, UNWANTED=('strokeColor', 'color'),
        background = AttrMapValue(isColor),
        border = AttrMapValue(isBoolean),
        )

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1

    def demo(self):
        D = shapes.Drawing(200, 100)
        fx = Flag0()
        fx.x = 0
        fx.y = 0
        fx.draw()
        D.add(fx)
        labelFontSize = 10
        D.add(shapes.String(fx.x+(fx.size/2),(fx.y-(1.2*labelFontSize)),
                            fx.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        labelFontSize = int(fx.size/4)
#        D.add(shapes.String(fx.x+(fx.size),(fx.y+((fx.size/2)-1.2*labelFontSize)),
#                            "SAMPLE", fillColor=colors.gold, textAnchor='middle',
#                            fontSize=labelFontSize))
        D.add(shapes.String(fx.x+(fx.size),(fx.y+((fx.size/2))),
                            "SAMPLE", fillColor=colors.gold, textAnchor='middle',
                            fontSize=labelFontSize, fontName="Helvetica-Bold"))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # flag specific bits
        box = shapes.Rect(self.x, self.y, s*2, s,
               fillColor = colors.purple,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        g.add(self.borderdraw())
        
        return g
             
    def borderdraw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        outerborder = shapes.Rect(self.x-1, self.y-1, width=(s*2)+2, height=s+2,
               fillColor = None,
               strokeColor = self.background,
               strokeWidth=1)
        g.add(outerborder)

        if self.border:
            innerborder = shapes.Rect(self.x, self.y, width=s*2, height=s,
               fillColor = None,
               strokeColor = colors.black,
               strokeWidth=0)
            g.add(innerborder)
        return g


class FlagUK0(Flag0):
    """This draws the Union Flag, as used by the United Kingdom.

        possible attributes:
        'x', 'y', 'size', 'background', , border
    """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        gbr = FlagUK0()
        gbr.x = 0
        gbr.y = 0
        gbr.draw()
        D.add(gbr)
        labelFontSize = 10
        D.add(shapes.String(gbr.x+(gbr.size/2),(gbr.y-(1.2*labelFontSize)),
                            gbr.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # flag specific bits
        box = shapes.Rect(self.x, self.y, s*2, s,
               fillColor = colors.navy,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        whitediag1 = shapes.Line(self.x, self.y, self.x+(s*2), self.y+s,
               fillColor = colors.mintcream,
               strokeColor = colors.mintcream,
               strokeWidth=20)
        g.add(whitediag1)
        
        whitediag2 = shapes.Line(self.x, self.y+s, self.x+(s*2), self.y,
               fillColor = colors.mintcream,
               strokeColor = colors.mintcream,
               strokeWidth=20)
        g.add(whitediag2)


        reddiag1 = shapes.Polygon(points=[self.x, self.y+s-(s/15),
                                  self.x+(s-((s/10)*4)), self.y+(s*0.65),
                                  self.x+(s-(s/10)*3), self.y+(s*0.65),
                                  self.x, self.y+s],
               fillColor = colors.red,
               strokeColor = None,
               strokeWidth=0)
        g.add(reddiag1)        

        reddiag2 = shapes.Polygon(points=[self.x, self.y,
                                  self.x+(s-((s/10)*3)), self.y+(s*0.35),
                                  self.x+(s-((s/10)*2)), self.y+(s*0.35),
                                  self.x+(s/10), self.y],
               fillColor = colors.red,
               strokeColor = None,
               strokeWidth=0)
        g.add(reddiag2)            

        reddiag3 = shapes.Polygon(points=[self.x+s*2, self.y+s,
                                  self.x+(s+((s/10)*3)), self.y+(s*0.65),
                                  self.x+(s+((s/10)*2)), self.y+(s*0.65),
                                  self.x+(s*2)-(s/10), self.y+s],
               fillColor = colors.red,
               strokeColor = None,
               strokeWidth=0)
        g.add(reddiag3)          

        reddiag4 = shapes.Polygon(points=[self.x+s*2, self.y+(s/15),
                                  self.x+(s+((s/10)*4)), self.y+(s*0.35),
                                  self.x+(s+((s/10)*3)), self.y+(s*0.35),
                                  self.x+(s*2), self.y],
               fillColor = colors.red,
               strokeColor = None,
               strokeWidth=0)
        g.add(reddiag4)   


        whiteline1 = shapes.Rect(self.x+((s*0.42)*2), self.y, width=(0.16*s)*2, height=s,
               fillColor = colors.mintcream,
               strokeColor = None,
               strokeWidth=0)
        g.add(whiteline1)
        
        whiteline2 = shapes.Rect(self.x, self.y+(s*0.35), width=s*2, height=s*0.3,
               fillColor = colors.mintcream,
               strokeColor = None,
               strokeWidth=0)
        g.add(whiteline2)
        

        redline1 = shapes.Rect(self.x+((s*0.45)*2), self.y, width=(0.1*s)*2, height=s,
               fillColor = colors.red,
               strokeColor = None,
               strokeWidth=0)
        g.add(redline1)
        
        redline2 = shapes.Rect(self.x, self.y+(s*0.4), width=s*2, height=s*0.2,
               fillColor = colors.red,
               strokeColor = None,
               strokeWidth=0)
        g.add(redline2)

        g.add(self.borderdraw())
        
        return g


class FlagUSA0(Flag0):
    """This draws the Stars and Stripes, as used by the United States of America.

        possible attributes:
        'x', 'y', 'size', 'background', , border
    """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        usa = FlagUSA0()
        usa.x = 0
        usa.y = 0
        usa.draw()
        D.add(usa)
        labelFontSize = 10
        D.add(shapes.String(usa.x+(usa.size/2),(usa.y-(1.2*labelFontSize)),
                            usa.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # flag specific bits
        box = shapes.Rect(self.x, self.y, s*2, s,
               fillColor = colors.mintcream,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        for stripecounter in range (13,0, -1):
            stripeheight = s/13.0
            if not (stripecounter%2 == 0):
                stripecolor = colors.red
            else:
                stripecolor = colors.mintcream


            redorwhiteline = shapes.Rect(self.x, self.y+(s-(stripeheight*stripecounter)), width=s*2, height=stripeheight,
                   fillColor = stripecolor,
                   strokeColor = None,
                   strokeWidth=20)
            g.add(redorwhiteline)            

        bluebox = shapes.Rect(self.x, self.y+(s-(stripeheight*7)), width=0.8*s, height=stripeheight*7,
               fillColor = colors.darkblue,
               strokeColor = None,
               strokeWidth=0)
        g.add(bluebox)
        
        for starxcounter in range (0,5):
            for starycounter in range (0,5):
                littlestar = Star0()
                littlestar.size = s*0.045
                littlestar.color = colors.mintcream
                littlestar.x = self.x-(s/22)
                littlestar.x = littlestar.x+(s/7)+(starxcounter*(s/14))+(starxcounter*(s/14))
                littlestar.y = (self.y+s-(starycounter*(s/9)))
                littlestar.draw()
                g.add(littlestar)

        for starxcounter in range (0,6):
            for starycounter in range (0,6):
                littlestar = Star0()
                littlestar.size = s*0.045
                littlestar.color = colors.mintcream
                littlestar.x = self.x-(s/22)
                littlestar.x = littlestar.x+(s/14)+((starxcounter*(s/14))+(starxcounter*(s/14)))
#                littlestar.x = self.x+((starxcounter*(s/16))+(s/7))
                littlestar.y = (self.y+s-(starycounter*(s/9))+(s/18))
                littlestar.draw()
                g.add(littlestar)        

        g.add(self.borderdraw())
        
        return g


class FlagAustria0(Flag0):
    """This draws the Austrian national flag.

        possible attributes:
        'x', 'y', 'size', 'background', border
    """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        aut = FlagAustria0()
        aut.x = 0
        aut.y = 0
        aut.draw()
        D.add(aut)
        labelFontSize = 10
        D.add(shapes.String(aut.x+(aut.size/2),(aut.y-(1.2*labelFontSize)),
                            aut.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # flag specific bits
        box = shapes.Rect(self.x, self.y, s*2, s,
               fillColor = colors.mintcream,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)


        redbox1 = shapes.Rect(self.x, self.y, width=s*2.0, height=s/3.0,
               fillColor = colors.red,
               strokeColor = None,
               strokeWidth=0)
        g.add(redbox1)
        
        redbox2 = shapes.Rect(self.x, self.y+((s/3.0)*2.0), width=s*2.0, height=s/3.0,
               fillColor = colors.red,
               strokeColor = None,
               strokeWidth=0)
        g.add(redbox2)

        g.add(self.borderdraw())
        
        return g


class FlagBelgium0(Flag0):
    """This draws the Belgian national flag.

        possible attributes:
        'x', 'y', 'size', 'background', border
    """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        bel = FlagBelgium0()
        bel.x = 0
        bel.y = 0
        bel.draw()
        D.add(bel)
        labelFontSize = 10
        D.add(shapes.String(bel.x+(bel.size/2),(bel.y-(1.2*labelFontSize)),
                            bel.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # flag specific bits
        box = shapes.Rect(self.x, self.y, s*2, s,
               fillColor = colors.black,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)


        box1 = shapes.Rect(self.x, self.y, width=(s/3.0)*2.0, height=s,
               fillColor = colors.black,
               strokeColor = None,
               strokeWidth=0)
        g.add(box1)
        
        box2 = shapes.Rect(self.x+((s/3.0)*2.0), self.y, width=(s/3.0)*2.0, height=s,
               fillColor = colors.gold,
               strokeColor = None,
               strokeWidth=0)
        g.add(box2)

        box3 = shapes.Rect(self.x+((s/3.0)*4.0), self.y, width=(s/3.0)*2.0, height=s,
               fillColor = colors.red,
               strokeColor = None,
               strokeWidth=0)
        g.add(box3)

        g.add(self.borderdraw())
        
        return g


class FlagDenmark0(Flag0):
    """This draws the Danish national flag.

        possible attributes:
        'x', 'y', 'size', 'background', border
    """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        dnk = FlagDenmark0()
        dnk.x = 0
        dnk.y = 0
        dnk.draw()
        D.add(dnk)
        labelFontSize = 10
        D.add(shapes.String(dnk.x+(dnk.size/2),(dnk.y-(1.2*labelFontSize)),
                            dnk.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group()
        self.border = 0
        
        # flag specific bits
        box = shapes.Rect(self.x, self.y, (s*2)*0.70, s,
               fillColor = colors.red,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        whitebox1 = shapes.Rect(self.x+((s/5)*2), self.y, width=s/6, height=s,
               fillColor = colors.mintcream,
               strokeColor = None,
               strokeWidth=0)
        g.add(whitebox1)
        
        whitebox2 = shapes.Rect(self.x, self.y+((s/2)-(s/12)), width=(s*2)*0.70, height=s/6,
               fillColor = colors.mintcream,
               strokeColor = None,
               strokeWidth=0)
        g.add(whitebox2)

        g.add(self.borderdraw())

        outerbox = shapes.Rect(self.x, self.y, (s*2)*0.70, s,
                               fillColor = None,
                               strokeColor = colors.white,
               strokeWidth=0)
        g.add(outerbox)
        outerbox = shapes.Rect(self.x, self.y, (s*2)*0.70, s,
                               fillColor = None,
                               strokeColor = colors.black,
               strokeWidth=0)
        g.add(outerbox)
        return g


class FlagFinland0(Flag0):
    """This draws the Finnish flag.
    
        possible attributes:
        'x', 'y', 'size', 'background', border

    """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        fin = FlagFinland0()
        fin.x = 0
        fin.y = 0
        fin.draw()
        D.add(fin)
        labelFontSize = 10
        D.add(shapes.String(fin.x+(fin.size/2),(fin.y-(1.2*labelFontSize)),
                            fin.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # crossbox specific bits
        box = shapes.Rect(self.x, self.y, s*2, s,
               fillColor = colors.ghostwhite,
               strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        blueline1 = shapes.Rect(self.x+(s*0.6), self.y, width=0.3*s, height=s,
               fillColor = colors.darkblue,
               strokeColor = None,
               strokeWidth=0)
        g.add(blueline1)
        
        blueline2 = shapes.Rect(self.x, self.y+(s*0.4), width=s*2, height=s*0.3,
               fillColor = colors.darkblue,
               strokeColor = None,
               strokeWidth=0)
        g.add(blueline2)

        g.add(self.borderdraw())
        
        return g


class FlagFrance0(Flag0):
    """This draws the French tricolor.

        possible attributes:
        'x', 'y', 'size', 'background', border
    """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        fra = FlagFrance0()
        fra.x = 0
        fra.y = 0
        fra.draw()
        D.add(fra)
        labelFontSize = 10
        D.add(shapes.String(fra.x+(fra.size/2),(fra.y-(1.2*labelFontSize)),
                            fra.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # flag specific bits
        box = shapes.Rect(self.x, self.y, s*2, s,
               fillColor = colors.navy,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        bluebox = shapes.Rect(self.x, self.y, width=((s/3.0)*2.0), height=s,
               fillColor = colors.blue,
               strokeColor = None,
               strokeWidth=0)
        g.add(bluebox)
        
        whitebox = shapes.Rect(self.x+((s/3.0)*2.0), self.y, width=((s/3.0)*2.0), height=s,
               fillColor = colors.mintcream,
               strokeColor = None,
               strokeWidth=0)
        g.add(whitebox)

        redbox = shapes.Rect(self.x+((s/3.0)*4.0), self.y, width=((s/3.0)*2.0), height=s,
               fillColor = colors.red,
               strokeColor = None,
               strokeWidth=0)
        g.add(redbox)

        g.add(self.borderdraw())
        
        return g


class FlagGermany0(Flag0):
    """This draws the national flag of Germany.

        possible attributes:
        'x', 'y', 'size', 'background', border
    """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        deu = FlagGermany0()
        deu.x = 0
        deu.y = 0
        deu.draw()
        D.add(deu)
        labelFontSize = 10
        D.add(shapes.String(deu.x+(deu.size/2),(deu.y-(1.2*labelFontSize)),
                            deu.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # flag specific bits
        box = shapes.Rect(self.x, self.y, s*2, s,
               fillColor = colors.gold,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        blackbox1 = shapes.Rect(self.x, self.y+((s/3.0)*2.0), width=s*2.0, height=s/3.0,
               fillColor = colors.black,
               strokeColor = None,
               strokeWidth=0)
        g.add(blackbox1)
        
        redbox1 = shapes.Rect(self.x, self.y+(s/3.0), width=s*2.0, height=s/3.0,
               fillColor = colors.orangered,
               strokeColor = None,
               strokeWidth=0)
        g.add(redbox1)

        g.add(self.borderdraw())
        
        return g


class FlagGreece0(Flag0):
    """This draws the national flag of Greece.

        possible attributes:
        'x', 'y', 'size', 'background', border
    """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        grc = FlagGreece0()
        grc.x = 0
        grc.y = 0
        grc.draw()
        D.add(grc)
        labelFontSize = 10
        D.add(shapes.String(grc.x+(grc.size/2),(grc.y-(1.2*labelFontSize)),
                            grc.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # flag specific bits
        box = shapes.Rect(self.x, self.y, s*2, s,
               fillColor = colors.gold,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        for stripecounter in range (9,0, -1):
            stripeheight = s/9.0
            if not (stripecounter%2 == 0):
                stripecolor = colors.deepskyblue
            else:
                stripecolor = colors.mintcream

            blueorwhiteline = shapes.Rect(self.x, self.y+(s-(stripeheight*stripecounter)), width=s*2, height=stripeheight,
                   fillColor = stripecolor,
                   strokeColor = None,
                   strokeWidth=20)
            g.add(blueorwhiteline)   

        bluebox1 = shapes.Rect(self.x, self.y+((s)-stripeheight*5), width=(stripeheight*5), height=stripeheight*5,
               fillColor = colors.deepskyblue,
               strokeColor = None,
               strokeWidth=0)
        g.add(bluebox1)
        
        whiteline1 = shapes.Rect(self.x, self.y+((s)-stripeheight*3), width=stripeheight*5, height=stripeheight,
               fillColor = colors.mintcream,
               strokeColor = None,
               strokeWidth=0)
        g.add(whiteline1)

        whiteline2 = shapes.Rect(self.x+(stripeheight*2), self.y+((s)-stripeheight*5), width=stripeheight, height=stripeheight*5,
               fillColor = colors.mintcream,
               strokeColor = None,
               strokeWidth=0)
        g.add(whiteline2)

        g.add(self.borderdraw())
        
        return g


class FlagIreland0(Flag0):
    """This draws the national flag of Ireland.

        possible attributes:
        'x', 'y', 'size', 'background', border
    """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        irl = FlagIreland0()
        irl.x = 0
        irl.y = 0
        irl.draw()
        D.add(irl)
        labelFontSize = 10
        D.add(shapes.String(irl.x+(irl.size/2),(irl.y-(1.2*labelFontSize)),
                            irl.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # flag specific bits
        box = shapes.Rect(self.x, self.y, s*2, s,
               fillColor = colors.forestgreen,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        whitebox = shapes.Rect(self.x+((s*2.0)/3.0), self.y, width=(2.0*(s*2.0)/3.0), height=s,
               fillColor = colors.mintcream,
               strokeColor = None,
               strokeWidth=0)
        g.add(whitebox)
        
        orangebox = shapes.Rect(self.x+((2.0*(s*2.0)/3.0)), self.y, width=(s*2.0)/3.0, height=s,
               fillColor = colors.darkorange,
               strokeColor = None,
               strokeWidth=0)
        g.add(orangebox)

        g.add(self.borderdraw())
        
        return g


class FlagItaly0(Flag0):
    """This draws the national flag of Italy.

        possible attributes:
        'x', 'y', 'size', 'background', border
    """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        ita = FlagItaly0()
        ita.x = 0
        ita.y = 0
        ita.draw()
        D.add(ita)
        labelFontSize = 10
        D.add(shapes.String(ita.x+(ita.size/2),(ita.y-(1.2*labelFontSize)),
                            ita.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # flag specific bits
        box = shapes.Rect(self.x, self.y, s*2, s,
               fillColor = colors.forestgreen,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        whitebox = shapes.Rect(self.x+((s*2.0)/3.0), self.y, width=(2.0*(s*2.0)/3.0), height=s,
               fillColor = colors.mintcream,
               strokeColor = None,
               strokeWidth=0)
        g.add(whitebox)
        
        redbox = shapes.Rect(self.x+((2.0*(s*2.0)/3.0)), self.y, width=(s*2.0)/3.0, height=s,
               fillColor = colors.red,
               strokeColor = None,
               strokeWidth=0)
        g.add(redbox)

        g.add(self.borderdraw())
        
        return g


class FlagLuxembourg0(Flag0):
    """This draws the national flag of the Grand Duchy of Luxembourg.

        possible attributes:
        'x', 'y', 'size', 'background', border
    """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        lux = FlagLuxembourg0()
        lux.x = 0
        lux.y = 0
        lux.draw()
        D.add(lux)
        labelFontSize = 10
        D.add(shapes.String(lux.x+(lux.size/2),(lux.y-(1.2*labelFontSize)),
                            lux.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # flag specific bits
        box = shapes.Rect(self.x, self.y, s*2, s,
               fillColor = colors.mintcream,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        redbox = shapes.Rect(self.x, self.y+((s/3.0)*2.0), width=s*2.0, height=s/3.0,
               fillColor = colors.red,
               strokeColor = None,
               strokeWidth=0)
        g.add(redbox)
        
        bluebox = shapes.Rect(self.x, self.y, width=s*2.0, height=s/3.0,
               fillColor = colors.dodgerblue,
               strokeColor = None,
               strokeWidth=0)
        g.add(bluebox)

        g.add(self.borderdraw())
        
        return g


class FlagHolland0(Flag0):
    """This draws the national flag of the Netherlands.

        possible attributes:
        'x', 'y', 'size', 'background', border
    """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        nld = FlagHolland0()
        nld.x = 0
        nld.y = 0
        nld.draw()
        D.add(nld)
        labelFontSize = 10
        D.add(shapes.String(nld.x+(nld.size/2),(nld.y-(1.2*labelFontSize)),
                            nld.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # flag specific bits
        box = shapes.Rect(self.x, self.y, s*2, s,
               fillColor = colors.mintcream,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        redbox = shapes.Rect(self.x, self.y+((s/3.0)*2.0), width=s*2.0, height=s/3.0,
               fillColor = colors.red,
               strokeColor = None,
               strokeWidth=0)
        g.add(redbox)
        
        bluebox = shapes.Rect(self.x, self.y, width=s*2.0, height=s/3.0,
               fillColor = colors.darkblue,
               strokeColor = None,
               strokeWidth=0)
        g.add(bluebox)

        g.add(self.borderdraw())
        
        return g


class FlagPortugal0(Flag0):
    """For PORTUGAL, the national flag contains a complex coat of arms -
    for most countries this just appears on the "state" flag. Since this
    is more difficult than the majority of flags, providing an adequate
    representation of it is "left as an exercise for the reader". """

    def __init__(self):
        pass
    
    def demo(self):
        pass


class FlagSpain0(Flag0):
    """This draws the Spanish national flag.

        possible attributes:
        'x', 'y', 'size', 'background', border
    """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        esp = FlagSpain0()
        esp.x = 0
        esp.y = 0
        esp.draw()
        D.add(esp)
        labelFontSize = 10
        D.add(shapes.String(esp.x+(esp.size/2),(esp.y-(1.2*labelFontSize)),
                            esp.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # flag specific bits
        box = shapes.Rect(self.x, self.y, s*2, s,
               fillColor = colors.yellow,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        redbox1 = shapes.Rect(self.x, self.y+((s/4)*3), width=s*2, height=s/4,
               fillColor = colors.red,
               strokeColor = None,
               strokeWidth=0)
        g.add(redbox1)
        
        redbox2 = shapes.Rect(self.x, self.y, width=s*2, height=s/4,
               fillColor = colors.red,
               strokeColor = None,
               strokeWidth=0)
        g.add(redbox2)

        g.add(self.borderdraw())
        
        return g


class FlagSweden0(Flag0):
    """This draws the national flag of Sweden.

        possible attributes:
        'x', 'y', 'size', 'background', border
    """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        swe = FlagSweden0()
        swe.x = 0
        swe.y = 0
        swe.draw()
        D.add(swe)
        labelFontSize = 10
        D.add(shapes.String(swe.x+(swe.size/2),(swe.y-(1.2*labelFontSize)),
                            swe.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group()
        self.border = 0
        
        # flag specific bits
        box = shapes.Rect(self.x, self.y, (s*2)*0.70, s,
               fillColor = colors.dodgerblue,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        box1 = shapes.Rect(self.x+((s/5)*2), self.y, width=s/6, height=s,
               fillColor = colors.gold,
               strokeColor = None,
               strokeWidth=0)
        g.add(box1)
        
        box2 = shapes.Rect(self.x, self.y+((s/2)-(s/12)), width=(s*2)*0.70, height=s/6,
               fillColor = colors.gold,
               strokeColor = None,
               strokeWidth=0)
        g.add(box2)

        g.add(self.borderdraw())

#        outerbox = shapes.Rect(self.x, self.y, (s*2)*0.70, s,
#                               fillColor = None,
#                               strokeColor = colors.white,
#               strokeWidth=1)
#        g.add(outerbox)
        outerbox = shapes.Rect(self.x, self.y, (s*2)*0.70, s,
                               fillColor = None,
                               strokeColor = colors.black,
               strokeWidth=0)
        g.add(outerbox)
        return g


class FlagNorway0(Flag0):
    """This draws the Norgegian national flag.

        possible attributes:
        'x', 'y', 'size', 'background', 'border'
        """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100 
        self.background = colors.white
        self.border = 0

    def demo(self):
        D = shapes.Drawing(200, 100)
        nor = FlagNorway0()
        nor.border = 0
        nor.x = 0
        nor.y = 0
        nor.draw()
        D.add(nor)
        labelFontSize = 10
        D.add(shapes.String(nor.x+(nor.size/2),(nor.y-(1.2*labelFontSize)),
                            nor.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group()
        self.border = 0
        
        # crossbox specific bits
        box = shapes.Rect(self.x, self.y, (s*2)*0.7, s,
               fillColor = colors.red,
               strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        # flag specific bits
        box = shapes.Rect(self.x, self.y, (s*2)*0.7, s,
               fillColor = colors.red,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        whiteline1 = shapes.Rect(self.x+((s*0.2)*2), self.y, width=s*0.2, height=s,
               fillColor = colors.ghostwhite,
               strokeColor = None,
               strokeWidth=0)
        g.add(whiteline1)
        
        whiteline2 = shapes.Rect(self.x, self.y+(s*0.4), width=((s*2)*0.70), height=s*0.2,
               fillColor = colors.ghostwhite,
               strokeColor = None,
               strokeWidth=0)
        g.add(whiteline2)

        blueline1 = shapes.Rect(self.x+((s*0.225)*2), self.y, width=0.1*s, height=s,
               fillColor = colors.darkblue,
               strokeColor = None,
               strokeWidth=0)
        g.add(blueline1)
        
        blueline2 = shapes.Rect(self.x, self.y+(s*0.45), width=(s*2)*0.7, height=s*0.1,
               fillColor = colors.darkblue,
               strokeColor = None,
               strokeWidth=0)
        g.add(blueline2)
        
#        outerbox = shapes.Rect(self.x, self.y, (s*2)*0.70, s,
#                               fillColor = None,
#                               strokeColor = colors.white,
#               strokeWidth=1)
#        g.add(outerbox)
        
        outerbox = shapes.Rect(self.x, self.y, (s*2)*0.70, s,
                               fillColor = None,
                               strokeColor = colors.black,
               strokeWidth=0)
        g.add(outerbox)
        return g


class FlagCzechRepublic0(Flag0):
    """This draws the national flag of The Czech Republic.

        possible attributes:
        'x', 'y', 'size', 'background', border
    """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        cze = FlagCzechRepublic0()
        cze.x = 0
        cze.y = 0
        cze.draw()
        D.add(cze)
        labelFontSize = 10
        D.add(shapes.String(cze.x+(cze.size/2),(cze.y-(1.2*labelFontSize)),
                            cze.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # flag specific bits
        box = shapes.Rect(self.x, self.y, s*2, s,
               fillColor = colors.mintcream,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        redbox = shapes.Rect(self.x, self.y, width=s*2, height=s/2,
               fillColor = colors.red,
               strokeColor = None,
               strokeWidth=0)
        g.add(redbox)
        
        bluewedge = shapes.Polygon(points = [
                                   self.x, self.y,
                                   self.x+s, self.y+(s/2),
                                   self.x, self.y+s],
               fillColor = colors.darkblue,
               strokeColor = None,
               strokeWidth=0)
        g.add(bluewedge)

        g.add(self.borderdraw())
        
        return g


class FlagTurkey0(Flag0):
    """This draws the national flag of the Republic of Turkey.

        possible attributes:
        'x', 'y', 'size', 'background', border
    """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        tur = FlagTurkey0()
        tur.x = 0
        tur.y = 0
        tur.draw()
        D.add(tur)
        labelFontSize = 10
        D.add(shapes.String(tur.x+(tur.size/2),(tur.y-(1.2*labelFontSize)),
                            tur.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # flag specific bits
        box = shapes.Rect(self.x, self.y, s*2, s,
               fillColor = colors.red,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        whitecircle = shapes.Circle(cx=self.x+((s*0.35)*2), cy=self.y+s/2, r=s*0.3,
               fillColor = colors.mintcream,
               strokeColor = None,
               strokeWidth=0)
        g.add(whitecircle)

        redcircle = shapes.Circle(cx=self.x+((s*0.39)*2), cy=self.y+s/2, r=s*0.24,
               fillColor = colors.red,
               strokeColor = None,
               strokeWidth=0)
        g.add(redcircle)
       
        ws = shapes.Group()
        whitestar = Star0()
        whitestar.size = s/5
        whitestar.x = self.x+(s*0.5)*2
        whitestar.y = self.y+(s*0.35)
        whitestar.color = colors.mintcream
        whitestar.strokecolor = None
        whitestar.draw()
        ws.add(whitestar)
        # This star should really be rotated...
        #shapes.Group.rotate(ws,30)
        whitestar.draw()
        g.add(ws)

        g.add(self.borderdraw())
        
        return g


class FlagSwitzerland0(Flag0):
    """This draws the Swiss Flag, as used by the Switzerland.
    (This flag has a ratio of 1:1 - ie it is square. It's meant to be that way)

        possible attributes:
        'x', 'y', 'size', 'background', , border
    """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        che = FlagSwitzerland0()
        che.x = 50
        che.y = 0
        che.draw()
        D.add(che)
        labelFontSize = 10
        D.add(shapes.String(che.x+(che.size/2),(che.y-(1.2*labelFontSize)),
                            che.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # flag specific bits
        box = shapes.Rect(self.x, self.y, s, s,
               fillColor = colors.red,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        whitebar1 = shapes.Line(self.x+(s/2), self.y+(s/5.5), self.x+(s/2), self.y+(s-(s/5.5)),
               fillColor = colors.mintcream,
               strokeColor = colors.mintcream,
               strokeWidth=(s/5))
        g.add(whitebar1)
        
        whitebar2 = shapes.Line(self.x+(s/5.5), self.y+(s/2), self.x+(s-(s/5.5)), self.y+(s/2),
               fillColor = colors.mintcream,
               strokeColor = colors.mintcream,
               strokeWidth=s/5)
        g.add(whitebar2)

        outerbox = shapes.Rect(self.x, self.y, s, s,
                               fillColor = None,
                               strokeColor = colors.black,
               strokeWidth=0)

 #       g.add(self.borderdraw())
        g.add(outerbox)        
        
        return g


class FlagEU0(Flag0):
    """This draws the flag of the European Union.

        possible attributes:
        'x', 'y', 'size', 'background', border
    """ 

    def __init__(self):
        self.x = 0
        self.y = 0
        self.size = 100
        self.background = colors.white
        self.border=1
        
    def demo(self):
        D = shapes.Drawing(200, 100)
        eu = FlagEU0()
        eu.x = 0
        eu.y = 0
        eu.draw()
        D.add(eu)
        labelFontSize = 10
        D.add(shapes.String(eu.x+(eu.size/2),(eu.y-(1.2*labelFontSize)),
                            eu.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))
        return D
     
    def draw(self):
        # general widget bits
        s = self.size  # abbreviate as we will use this a lot 
        g = shapes.Group() 
        
        # flag specific bits
        box = shapes.Rect(self.x, self.y, s*2, s,
               fillColor = colors.darkblue,
                          strokeColor = colors.black,
               strokeWidth=0)
        g.add(box)

        centerx=self.x+(s*0.95)
        centery=self.y+(s/2.1)
        radius=(s/2.75)
        yradius = radius
        xradius = radius
        startangledegrees=0
        endangledegrees=360
        degreedelta = 30
        pointslist = []
        a = pointslist.append
        from math import sin, cos, pi
        degreestoradians = pi/180.0
        radiansdelta = degreedelta*degreestoradians
        startangle = startangledegrees*degreestoradians
        endangle = endangledegrees*degreestoradians
        while endangle<startangle:
              endangle = endangle+2*pi
        angle = startangle
        while angle<endangle:
            x = centerx + cos(angle)*radius
            y = centery + sin(angle)*yradius
            a(x); a(y)
            angle = angle+radiansdelta

        innercounter = 0
        for stars in range (0,12):
            goldstar = Star0()
            goldstar.x=pointslist[innercounter]
            goldstar.y=pointslist[innercounter+1]
            goldstar.size=s/10
            goldstar.color=colors.gold
            goldstar.draw()
            g.add(goldstar)
            innercounter=innercounter+2
            
        box = shapes.Rect(self.x, self.y, width=s/4, height=s,
               fillColor = self.background,
                          strokeColor = None,
               strokeWidth=0)
        g.add(box)

        box2 = shapes.Rect(self.x+((s*2)-s/4), self.y, width=s/4, height=s,
               fillColor = self.background,
                          strokeColor = None,
               strokeWidth=0)
        g.add(box2)

        g.add(self.borderdraw())
        
        return g


def test():
    """This function produces two pdf files with examples of all the signs and symbols from this file.
    """
# page 1

    labelFontSize = 10
    D = shapes.Drawing(450,650)

    gbr = FlagUK0()
    gbr.x = 20
    gbr.y = 530
    gbr.draw()
    D.add(gbr)
    D.add(shapes.String(gbr.x+(gbr.size/2),(gbr.y-(1.2*labelFontSize)),
                            gbr.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))

    usa = FlagUSA0()
    usa.x=245
    usa.y=530
    usa.draw()
    D.add(usa)
    labelFontSize = 10
    D.add(shapes.String(usa.x+(usa.size/2),(usa.y-(1.2*labelFontSize)),
                        usa.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                        fontSize=labelFontSize))

    aut = FlagAustria0()
    aut.x = 20
    aut.y = 400
    aut.draw()
    D.add(aut)
    D.add(shapes.String(aut.x+(aut.size/2),(aut.y-(1.2*labelFontSize)),
                            aut.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))

    bel = FlagBelgium0()
    bel.x = 245
    bel.y = 400
    bel.draw()
    D.add(bel)
    D.add(shapes.String(bel.x+(bel.size/2),(bel.y-(1.2*labelFontSize)),
                            bel.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))

    dnk = FlagDenmark0()
    dnk.x = 20
    dnk.y = 270
    dnk.draw()
    D.add(dnk)
    D.add(shapes.String(dnk.x+(dnk.size/2),(dnk.y-(1.2*labelFontSize)),
                            dnk.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))

    fin = FlagFinland0()
    fin.x=245
    fin.y=270
    fin.draw()
    D.add(fin)
    labelFontSize = 10
    D.add(shapes.String(fin.x+(fin.size/2),(fin.y-(1.2*labelFontSize)),
                        fin.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                        fontSize=labelFontSize))

    fra = FlagFrance0()
    fra.x=20
    fra.y=140
    fra.draw()
    D.add(fra)
    labelFontSize = 10
    D.add(shapes.String(fra.x+(fra.size/2),(fra.y-(1.2*labelFontSize)),
                        fra.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                        fontSize=labelFontSize))

    deu = FlagGermany0()
    deu.x=245
    deu.y=140
    deu.draw()
    D.add(deu)
    labelFontSize = 10
    D.add(shapes.String(deu.x+(deu.size/2),(deu.y-(1.2*labelFontSize)),
                        deu.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                        fontSize=labelFontSize))

    grc = FlagGreece0()
    grc.x = 20
    grc.y = 20
    grc.draw()
    D.add(grc)
    labelFontSize = 10
    D.add(shapes.String(grc.x+(grc.size/2),(grc.y-(1.2*labelFontSize)),
                        grc.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                        fontSize=labelFontSize))

    irl = FlagIreland0()
    irl.x = 245
    irl.y = 20
    irl.draw()
    D.add(irl)
    labelFontSize = 10
    D.add(shapes.String(irl.x+(irl.size/2),(irl.y-(1.2*labelFontSize)),
                        irl.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                        fontSize=labelFontSize))    

    renderPDF.drawToFile(D, 'flags0_1.pdf', 'flags0.py - Page #1')
    print 'wrote file: flags0_1.pdf'


# page 2

    labelFontSize = 10
    D = shapes.Drawing(450,650)

    ita = FlagItaly0()
    ita.x = 20
    ita.y = 530
    ita.draw()
    D.add(ita)
    D.add(shapes.String(ita.x+(ita.size/2),(ita.y-(1.2*labelFontSize)),
                            ita.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))

    lux = FlagLuxembourg0()
    lux.x=245
    lux.y=530
    lux.draw()
    D.add(lux)
    labelFontSize = 10
    D.add(shapes.String(lux.x+(lux.size/2),(lux.y-(1.2*labelFontSize)),
                        lux.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                        fontSize=labelFontSize))

    nld = FlagHolland0()
    nld.x=20
    nld.y=400
    nld.draw()
    D.add(nld)
    labelFontSize = 10
    D.add(shapes.String(nld.x+(nld.size/2),(nld.y-(1.2*labelFontSize)),
                        nld.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                        fontSize=labelFontSize))

    esp = FlagSpain0()
    esp.x=245
    esp.y=400
    esp.draw()
    D.add(esp)
    labelFontSize = 10
    D.add(shapes.String(esp.x+(esp.size/2),(esp.y-(1.2*labelFontSize)),
                        esp.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                        fontSize=labelFontSize))

    swe = FlagSweden0()
    swe.x = 20
    swe.y = 270
    swe.draw()
    D.add(swe)
    labelFontSize = 10
    D.add(shapes.String(swe.x+(swe.size/2),(swe.y-(1.2*labelFontSize)),
                        swe.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                        fontSize=labelFontSize))

    nor = FlagNorway0()
    nor.x = 245
    nor.y = 270
    nor.draw()
    D.add(nor)
    labelFontSize = 10
    D.add(shapes.String(nor.x+(nor.size/2),(nor.y-(1.2*labelFontSize)),
                        nor.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                        fontSize=labelFontSize))

    cze = FlagCzechRepublic0()
    cze.x = 20
    cze.y = 140
    cze.draw()
    D.add(cze)
    labelFontSize = 10
    D.add(shapes.String(cze.x+(cze.size/2),(cze.y-(1.2*labelFontSize)),
                        cze.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                        fontSize=labelFontSize))

    tur = FlagTurkey0()
    tur.x = 245
    tur.y = 140
    tur.draw()
    D.add(tur)
    labelFontSize = 10
    D.add(shapes.String(tur.x+(tur.size/2),(tur.y-(1.2*labelFontSize)),
                        tur.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                        fontSize=labelFontSize))
    
    eu = FlagEU0()
    eu.border=0
    eu.x = 20
    eu.y = 20
    eu.draw()
    D.add(eu)
    labelFontSize = 10
    D.add(shapes.String(eu.x+(eu.size/2),(eu.y-(1.2*labelFontSize)),
                            eu.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))

    che = FlagSwitzerland0()
    che.border=0
    che.x = 295
    che.y = 20
    che.draw()
    D.add(che)
    labelFontSize = 10
    D.add(shapes.String(che.x+(che.size/2),(che.y-(1.2*labelFontSize)),
                            che.__class__.__name__, fillColor=colors.black, textAnchor='middle',
                            fontSize=labelFontSize))

    renderPDF.drawToFile(D, 'flags0_2.pdf', 'flags0.py - Page #2')
    print 'wrote file: flags0_2.pdf'        

    
if __name__=='__main__':
    test()
