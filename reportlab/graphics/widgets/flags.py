#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/widgets/flags.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/widgets/flags.py,v 1.14 2001/10/05 16:32:20 rgbecker Exp $
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
from reportlab.graphics.shapes import Line, Rect, Polygon, Drawing, Group, String, Circle
from reportlab.graphics.widgetbase import Widget
from reportlab.graphics import renderPDF
from signsandsymbols import _Symbol
import copy
from math import sin, cos, pi

validFlag=OneOf(None,
				'UK',
				'USA',
				'Austria',
				'Belgium',
				'China',
				'Denmark',
				'Finland',
				'France',
				'Germany',
				'Greece',
				'Ireland',
				'Italy',
				'Japan',
				'Luxembourg',
				'Holland',
				'Portugal',
				'Russia',
				'Spain',
				'Sweden',
				'Norway',
				'CzechRepublic',
				'Turkey',
				'Switzerland',
				'EU',
				)

_size = 100.

class Star(_Symbol):
	"""This draws a 5-pointed star.

		possible attributes:
		'x', 'y', 'size', 'fillColor', 'strokeColor'

		"""
	_attrMap = AttrMap(BASE=_Symbol,
			angle = AttrMapValue(isNumber, desc='angle in degrees'),
			)
	_size = 100.

	def __init__(self):
		_Symbol.__init__(self)
		self.size = 100
		self.fillColor = colors.yellow
		self.strokeColor = None
		self.angle = 0

	def demo(self):
		D = Drawing(200, 100)
		et = Star()
		et.x=50
		et.y=0
		D.add(et)
		labelFontSize = 10
		D.add(String(et.x+(et.size/2),(et.y-(1.2*labelFontSize)),
							et.__class__.__name__, fillColor=colors.black, textAnchor='middle',
							fontSize=labelFontSize))
		return D

	def draw(self):
		s = float(self.size)  #abbreviate as we will use this a lot
		g = Group()

		# star specific bits
		h = s/5
		z = s/2
		star = Polygon(points = [
					h-z,		0-z,
					h*1.5-z,	h*2.05-z,
					0-z,		h*3-z,
					h*1.95-z,	h*3-z,
					z-z,		s-z,
					h*3.25-z,	h*3-z,
					s-z,		h*3-z,
					s-h*1.5-z,	h*2.05-z,
					s-h-z,		0-z,
					z-z,		h-z,
					],
					fillColor = self.fillColor,
					strokeColor = self.strokeColor,
					strokeWidth=s/50)
		g.rotate(self.angle)
		g.shift(self.x+self.dx,self.y+self.dy)
		g.add(star)

		return g

class Flag(_Symbol):
	"""This is a generic flag class that all the flags in this file use as a basis.

		This class basically provides edges and a tidy-up routine to hide any bits of
		line that overlap the 'outside' of the flag

		possible attributes:
		'x', 'y', 'size', 'fillColor'
	"""

	_attrMap = AttrMap(BASE=_Symbol,
			fillColor = AttrMapValue(isColor, desc='Background color'),
			border = AttrMapValue(isBoolean, 'Whether a background is drawn'),
			kind = AttrMapValue(validFlag, desc='Which flag'),
			)

	_cache = {}

	def __init__(self):
		_Symbol.__init__(self)
		self.kind = None
		self.size = 100
		self.fillColor = colors.white
		self.border=1

	def availableFlagNames(self):
		'''return a list of the things we can display'''
		return filter(lambda x: x is not None, self._attrMap['kind'].validate._enum)

	def _Flag_None(self):
		s = _size  # abbreviate as we will use this a lot
		g = Group()
		g.add(Rect(0, 0, s*2, s, fillColor = colors.purple, strokeColor = colors.black, strokeWidth=0))
		return g

	def _borderDraw(self,f):
		s = self.size  # abbreviate as we will use this a lot
		g = Group()
		g.add(f)
		x, y, sW = self.x+self.dx, self.y+self.dy, self.strokeWidth/2.
		g.insert(0,Rect(-sW, -sW, width=getattr(self,'_width',2*s)+3*sW, height=getattr(self,'_height',s)+2*sW,
				fillColor = None, strokeColor = self.strokeColor, strokeWidth=sW*2))
		g.shift(x,y)
		g.scale(s/_size, s/_size)
		return g

	def draw(self):
		kind = self.kind or 'None'
		f = self._cache.get(kind)
		if not f:
			f = getattr(self,'_Flag_'+kind)()
			self._cache[kind] = f
		return self._borderDraw(f)

	def clone(self):
		return copy.copy(self)

	def demo(self):
		D = Drawing(200, 100)
		name = self.availableFlagNames()
		import time
		name = name[int(time.time()) % len(name)]
		fx = Flag()
		fx.kind = name
		fx.x = 0
		fx.y = 0
		D.add(fx)
		labelFontSize = 10
		D.add(String(fx.x+(fx.size/2),(fx.y-(1.2*labelFontSize)),
							name, fillColor=colors.black, textAnchor='middle',
							fontSize=labelFontSize))
		labelFontSize = int(fx.size/4)
		D.add(String(fx.x+(fx.size),(fx.y+((fx.size/2))),
							"SAMPLE", fillColor=colors.gold, textAnchor='middle',
							fontSize=labelFontSize, fontName="Helvetica-Bold"))
		return D

	def _Flag_UK(self):
		s = _size
		g = Group()
		w = s*2
		g.add(Rect(0, 0, w, s, fillColor = colors.navy, strokeColor = colors.black, strokeWidth=0))
		g.add(Polygon([0,0, s*.225,0, w,s*(1-.1125), w,s, w-s*.225,s, 0, s*.1125], fillColor = colors.mintcream, strokeColor=None, strokeWidth=0))
		g.add(Polygon([0,s*(1-.1125), 0, s, s*.225,s, w, s*.1125, w,0, w-s*.225,0], fillColor = colors.mintcream, strokeColor=None, strokeWidth=0))
		g.add(Polygon([0, s-(s/15), (s-((s/10)*4)), (s*0.65), (s-(s/10)*3), (s*0.65), 0, s], fillColor = colors.red, strokeColor = None, strokeWidth=0))
		g.add(Polygon([0, 0, (s-((s/10)*3)), (s*0.35), (s-((s/10)*2)), (s*0.35), (s/10), 0], fillColor = colors.red, strokeColor = None, strokeWidth=0))
		g.add(Polygon([w, s, (s+((s/10)*3)), (s*0.65), (s+((s/10)*2)), (s*0.65), w-(s/10), s], fillColor = colors.red, strokeColor = None, strokeWidth=0))
		g.add(Polygon([w, (s/15), (s+((s/10)*4)), (s*0.35), (s+((s/10)*3)), (s*0.35), w, 0], fillColor = colors.red, strokeColor = None, strokeWidth=0))
		g.add(Rect(((s*0.42)*2), 0, width=(0.16*s)*2, height=s, fillColor = colors.mintcream, strokeColor = None, strokeWidth=0))
		g.add(Rect(0, (s*0.35), width=w, height=s*0.3, fillColor = colors.mintcream, strokeColor = None, strokeWidth=0))
		g.add(Rect(((s*0.45)*2), 0, width=(0.1*s)*2, height=s, fillColor = colors.red, strokeColor = None, strokeWidth=0))
		g.add(Rect(0, (s*0.4), width=w, height=s*0.2, fillColor = colors.red, strokeColor = None, strokeWidth=0))
		return g

	def _Flag_USA(self):
		s = _size  # abbreviate as we will use this a lot
		g = Group()

		box = Rect(0, 0, s*2, s, fillColor = colors.mintcream, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		for stripecounter in range (13,0, -1):
			stripeheight = s/13.0
			if not (stripecounter%2 == 0):
				stripecolor = colors.red
			else:
				stripecolor = colors.mintcream
			redorwhiteline = Rect(0, (s-(stripeheight*stripecounter)), width=s*2, height=stripeheight,
				fillColor = stripecolor, strokeColor = None, strokeWidth=20)
			g.add(redorwhiteline)

		bluebox = Rect(0, (s-(stripeheight*7)), width=0.8*s, height=stripeheight*7,
			fillColor = colors.darkblue, strokeColor = None, strokeWidth=0)
		g.add(bluebox)

		lss = s*0.045
		lss2 = lss/2
		s9 = s/9
		s7 = s/7
		for starxcounter in range(5):
			for starycounter in range(4):
				ls = Star()
				ls.size = lss
				ls.x = 0-s/22+lss/2+s7+starxcounter*s7
				ls.fillColor = colors.mintcream
				ls.y = s-(starycounter+1)*s9+lss2
				g.add(ls)

		for starxcounter in range(6):
			for starycounter in range(5):
				ls = Star()
				ls.size = lss
				ls.x = 0-(s/22)+lss/2+s/14+starxcounter*s7
				ls.fillColor = colors.mintcream
				ls.y = s-(starycounter+1)*s9+(s/18)+lss2
				g.add(ls)
		return g

	def _Flag_Austria(self):
		s = _size  # abbreviate as we will use this a lot
		g = Group()

		box = Rect(0, 0, s*2, s, fillColor = colors.mintcream,
			strokeColor = colors.black, strokeWidth=0)
		g.add(box)


		redbox1 = Rect(0, 0, width=s*2.0, height=s/3.0,
			fillColor = colors.red, strokeColor = None, strokeWidth=0)
		g.add(redbox1)

		redbox2 = Rect(0, ((s/3.0)*2.0), width=s*2.0, height=s/3.0,
			fillColor = colors.red, strokeColor = None, strokeWidth=0)
		g.add(redbox2)
		return g

	def _Flag_Belgium(self):
		s = _size
		g = Group()

		box = Rect(0, 0, s*2, s,
			fillColor = colors.black, strokeColor = colors.black, strokeWidth=0)
		g.add(box)


		box1 = Rect(0, 0, width=(s/3.0)*2.0, height=s,
			fillColor = colors.black, strokeColor = None, strokeWidth=0)
		g.add(box1)

		box2 = Rect(((s/3.0)*2.0), 0, width=(s/3.0)*2.0, height=s,
			fillColor = colors.gold, strokeColor = None, strokeWidth=0)
		g.add(box2)

		box3 = Rect(((s/3.0)*4.0), 0, width=(s/3.0)*2.0, height=s,
			fillColor = colors.red, strokeColor = None, strokeWidth=0)
		g.add(box3)
		return g

	def _Flag_China(self):
		s = _size
		g = Group()
		self._width = w = s*1.5
		g.add(Rect(0, 0, w, s, fillColor=colors.red, strokeColor=None, strokeWidth=0))

		def addStar(x,y,size,angle,g=g,w=s/20,x0=0,y0=s/2):
			s = Star()
			s.fillColor=colors.yellow
			s.angle = angle
			s.size = size*w*2
			s.x = x*w+x0
			s.y = y*w+y0
			g.add(s)

		addStar(5,5,3, 0)
		addStar(10,1,1,36.86989765)
		addStar(12,3,1,8.213210702)
		addStar(12,6,1,16.60154960)
		addStar(10,8,1,53.13010235)
		return g

	def _Flag_Denmark(self):
		s = _size
		g = Group()
		self._width = w = s*1.4

		box = Rect(0, 0, w, s,
			fillColor = colors.red, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		whitebox1 = Rect(((s/5)*2), 0, width=s/6, height=s,
			fillColor = colors.mintcream, strokeColor = None, strokeWidth=0)
		g.add(whitebox1)

		whitebox2 = Rect(0, ((s/2)-(s/12)), width=w, height=s/6,
			fillColor = colors.mintcream, strokeColor = None, strokeWidth=0)
		g.add(whitebox2)
		return g

	def _Flag_Finland(self):
		s = _size
		g = Group()

		# crossbox specific bits
		box = Rect(0, 0, s*2, s,
			fillColor = colors.ghostwhite, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		blueline1 = Rect((s*0.6), 0, width=0.3*s, height=s,
			fillColor = colors.darkblue, strokeColor = None, strokeWidth=0)
		g.add(blueline1)

		blueline2 = Rect(0, (s*0.4), width=s*2, height=s*0.3,
			fillColor = colors.darkblue, strokeColor = None, strokeWidth=0)
		g.add(blueline2)
		return g

	def _Flag_France(self):
		s = _size
		g = Group()

		box = Rect(0, 0, s*2, s, fillColor = colors.navy, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		bluebox = Rect(0, 0, width=((s/3.0)*2.0), height=s,
			fillColor = colors.blue, strokeColor = None, strokeWidth=0)
		g.add(bluebox)

		whitebox = Rect(((s/3.0)*2.0), 0, width=((s/3.0)*2.0), height=s,
			fillColor = colors.mintcream, strokeColor = None, strokeWidth=0)
		g.add(whitebox)

		redbox = Rect(((s/3.0)*4.0), 0, width=((s/3.0)*2.0), height=s,
			fillColor = colors.red,
			strokeColor = None,
			strokeWidth=0)
		g.add(redbox)
		return g

	def _Flag_Germany(self):
		s = _size
		g = Group()

		box = Rect(0, 0, s*2, s,
				fillColor = colors.gold, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		blackbox1 = Rect(0, ((s/3.0)*2.0), width=s*2.0, height=s/3.0,
			fillColor = colors.black, strokeColor = None, strokeWidth=0)
		g.add(blackbox1)

		redbox1 = Rect(0, (s/3.0), width=s*2.0, height=s/3.0,
			fillColor = colors.orangered, strokeColor = None, strokeWidth=0)
		g.add(redbox1)
		return g

	def _Flag_Greece(self):
		s = _size
		g = Group()

		box = Rect(0, 0, s*2, s, fillColor = colors.gold,
						strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		for stripecounter in range (9,0, -1):
			stripeheight = s/9.0
			if not (stripecounter%2 == 0):
				stripecolor = colors.deepskyblue
			else:
				stripecolor = colors.mintcream

			blueorwhiteline = Rect(0, (s-(stripeheight*stripecounter)), width=s*2, height=stripeheight,
				fillColor = stripecolor, strokeColor = None, strokeWidth=20)
			g.add(blueorwhiteline)

		bluebox1 = Rect(0, ((s)-stripeheight*5), width=(stripeheight*5), height=stripeheight*5,
			fillColor = colors.deepskyblue, strokeColor = None, strokeWidth=0)
		g.add(bluebox1)

		whiteline1 = Rect(0, ((s)-stripeheight*3), width=stripeheight*5, height=stripeheight,
			fillColor = colors.mintcream, strokeColor = None, strokeWidth=0)
		g.add(whiteline1)

		whiteline2 = Rect((stripeheight*2), ((s)-stripeheight*5), width=stripeheight, height=stripeheight*5,
			fillColor = colors.mintcream, strokeColor = None, strokeWidth=0)
		g.add(whiteline2)

		return g

	def _Flag_Ireland(self):
		s = _size
		g = Group()

		box = Rect(0, 0, s*2, s,
			fillColor = colors.forestgreen, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		whitebox = Rect(((s*2.0)/3.0), 0, width=(2.0*(s*2.0)/3.0), height=s,
				fillColor = colors.mintcream, strokeColor = None, strokeWidth=0)
		g.add(whitebox)

		orangebox = Rect(((2.0*(s*2.0)/3.0)), 0, width=(s*2.0)/3.0, height=s,
			fillColor = colors.darkorange, strokeColor = None, strokeWidth=0)
		g.add(orangebox)
		return g

	def _Flag_Italy(self):
		s = _size
		g = Group()
		g.add(Rect(0,0,s*2,s,fillColor=colors.forestgreen,strokeColor=None, strokeWidth=0))
		g.add(Rect((2*s)/3, 0, width=(s*4)/3, height=s, fillColor = colors.mintcream, strokeColor = None, strokeWidth=0))
		g.add(Rect((4*s)/3, 0, width=(s*2)/3, height=s, fillColor = colors.red, strokeColor = None, strokeWidth=0))
		return g

	def _Flag_Japan(self):
		s = _size
		g = Group()
		w = self._width = s*1.5
		g.add(Rect(0,0,w,s,fillColor=colors.mintcream,strokeColor=None, strokeWidth=0))
		g.add(Circle(cx=w/2,cy=s/2,r=0.3*w,fillColor=colors.red,strokeColor=None, strokeWidth=0))
		return g

	def _Flag_Luxembourg(self):
		s = _size
		g = Group()

		box = Rect(0, 0, s*2, s,
			fillColor = colors.mintcream, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		redbox = Rect(0, ((s/3.0)*2.0), width=s*2.0, height=s/3.0,
				fillColor = colors.red, strokeColor = None, strokeWidth=0)
		g.add(redbox)

		bluebox = Rect(0, 0, width=s*2.0, height=s/3.0,
				fillColor = colors.dodgerblue, strokeColor = None, strokeWidth=0)
		g.add(bluebox)
		return g

	def _Flag_Holland(self):
		s = _size
		g = Group()

		box = Rect(0, 0, s*2, s,
			fillColor = colors.mintcream, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		redbox = Rect(0, ((s/3.0)*2.0), width=s*2.0, height=s/3.0,
				fillColor = colors.red, strokeColor = None, strokeWidth=0)
		g.add(redbox)

		bluebox = Rect(0, 0, width=s*2.0, height=s/3.0,
				fillColor = colors.darkblue, strokeColor = None, strokeWidth=0)
		g.add(bluebox)
		return g

	def _Flag_Portugal(self):
		return Group()

	def _Flag_Russia(self):
		s = _size
		g = Group()
		w = self._width = s*1.5
		t = s/3
		g.add(Rect(0, 0, width=w, height=t, fillColor = colors.red, strokeColor = None, strokeWidth=0))
		g.add(Rect(0, t, width=w, height=t, fillColor = colors.blue, strokeColor = None, strokeWidth=0))
		g.add(Rect(0, 2*t, width=w, height=t, fillColor = colors.mintcream, strokeColor = None, strokeWidth=0))
		return g

	def _Flag_Spain(self):
		s = _size
		g = Group()
		w = self._width = s*1.5
		g.add(Rect(0, 0, width=w, height=s, fillColor = colors.red, strokeColor = None, strokeWidth=0))
		g.add(Rect(0, (s/4), width=w, height=s/2, fillColor = colors.yellow, strokeColor = None, strokeWidth=0))
		return g

	def _Flag_Sweden(self):
		s = _size
		g = Group()
		self._width = s*1.4
		box = Rect(0, 0, self._width, s,
			fillColor = colors.dodgerblue, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		box1 = Rect(((s/5)*2), 0, width=s/6, height=s,
				fillColor = colors.gold, strokeColor = None, strokeWidth=0)
		g.add(box1)

		box2 = Rect(0, ((s/2)-(s/12)), width=self._width, height=s/6,
			fillColor = colors.gold,
			strokeColor = None,
			strokeWidth=0)
		g.add(box2)
		return g

	def _Flag_Norway(self):
		s = _size
		g = Group()
		self._width = s*1.4

		box = Rect(0, 0, self._width, s,
				fillColor = colors.red, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		box = Rect(0, 0, self._width, s,
				fillColor = colors.red, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		whiteline1 = Rect(((s*0.2)*2), 0, width=s*0.2, height=s,
				fillColor = colors.ghostwhite, strokeColor = None, strokeWidth=0)
		g.add(whiteline1)

		whiteline2 = Rect(0, (s*0.4), width=self._width, height=s*0.2,
				fillColor = colors.ghostwhite, strokeColor = None, strokeWidth=0)
		g.add(whiteline2)

		blueline1 = Rect(((s*0.225)*2), 0, width=0.1*s, height=s,
				fillColor = colors.darkblue, strokeColor = None, strokeWidth=0)
		g.add(blueline1)

		blueline2 = Rect(0, (s*0.45), width=self._width, height=s*0.1,
				fillColor = colors.darkblue, strokeColor = None, strokeWidth=0)
		g.add(blueline2)
		return g

	def _Flag_CzechRepublic(self):
		s = _size
		g = Group()
		box = Rect(0, 0, s*2, s,
			fillColor = colors.mintcream,
						strokeColor = colors.black,
			strokeWidth=0)
		g.add(box)

		redbox = Rect(0, 0, width=s*2, height=s/2,
			fillColor = colors.red,
			strokeColor = None,
			strokeWidth=0)
		g.add(redbox)

		bluewedge = Polygon(points = [ 0, 0, s, (s/2), 0, s],
					fillColor = colors.darkblue, strokeColor = None, strokeWidth=0)
		g.add(bluewedge)
		return g

	def _Flag_Turkey(self):
		s = _size
		g = Group()

		box = Rect(0, 0, s*2, s,
			fillColor = colors.red,
						strokeColor = colors.black,
			strokeWidth=0)
		g.add(box)

		whitecircle = Circle(cx=((s*0.35)*2), cy=s/2, r=s*0.3,
			fillColor = colors.mintcream,
			strokeColor = None,
			strokeWidth=0)
		g.add(whitecircle)

		redcircle = Circle(cx=((s*0.39)*2), cy=s/2, r=s*0.24,
			fillColor = colors.red,
			strokeColor = None,
			strokeWidth=0)
		g.add(redcircle)

		ws = Star()
		ws.angle = 15
		ws.size = s/5
		ws.x = (s*0.5)*2+ws.size/2
		ws.y = (s*0.5)
		ws.fillColor = colors.mintcream
		ws.strokeColor = None
		g.add(ws)
		return g

	def _Flag_Switzerland(self):
		s = _size
		g = Group()
		self._width = s

		g.add(Rect(0, 0, s, s, fillColor = colors.red, strokeColor = colors.black, strokeWidth=0))
		g.add(Line((s/2), (s/5.5), (s/2), (s-(s/5.5)),
			fillColor = colors.mintcream, strokeColor = colors.mintcream, strokeWidth=(s/5)))
		g.add(Line((s/5.5), (s/2), (s-(s/5.5)), (s/2),
			fillColor = colors.mintcream, strokeColor = colors.mintcream, strokeWidth=s/5))
		return g

	def _Flag_EU(self):
		s = _size
		g = Group()
		w = self._width = 1.5*s

		g.add(Rect(0, 0, w, s, fillColor = colors.darkblue, strokeColor = None, strokeWidth=0))
		centerx=w/2
		centery=s/2
		radius=s/3
		yradius = radius
		xradius = radius
		nStars = 12
		delta = 2*pi/nStars
		for i in range(nStars):
			rad = i*delta
			gs = Star()
			gs.x=cos(rad)*radius+centerx
			gs.y=sin(rad)*radius+centery
			gs.size=s/10
			gs.fillColor=colors.gold
			g.add(gs)
		return g

def makeFlag(name):
	flag = Flag()
	flag.kind = name
	return flag

def test():
	"""This function produces two pdf files with examples of all the signs and symbols from this file.
	"""
# page 1

	labelFontSize = 10

	X = (20,245)

	flags = [
			'UK',
			'USA',
			'Austria',
			'Belgium',
			'Denmark',
			'Finland',
			'France',
			'Germany',
			'Greece',
			'Ireland',
			'Italy',
			'Luxembourg',
			'Holland',
			'Portugal',
			'Spain',
			'Sweden',
			'Norway',
			'CzechRepublic',
			'Turkey',
			'Switzerland',
			'EU',
			]
	y = Y0 = 530
	f = 0
	D = None
	for name in flags:
		if not D: D = Drawing(450,650)
		flag = makeFlag(name)
		i = flags.index(name)
		flag.x = X[i%2]
		flag.y = y
		D.add(flag)
		D.add(String(flag.x+(flag.size/2),(flag.y-(1.2*labelFontSize)),
				name, fillColor=colors.black, textAnchor='middle', fontSize=labelFontSize))
		if i%2: y = y - 125
		if (i%2 and y<0) or name==flags[-1]:
			renderPDF.drawToFile(D, 'flags%02d.pdf'%f, 'flags.py - Page #%d'%(f+1))
			y = Y0
			f = f+1
			D = None

if __name__=='__main__':
	test()
