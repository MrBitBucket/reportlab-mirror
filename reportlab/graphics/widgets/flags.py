#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/widgets/flags.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/widgets/flags.py,v 1.9 2001/09/25 12:54:53 rgbecker Exp $
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
from signsandsymbols import _Symbol

validFlag=OneOf(None,
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
				)

class Star(_Symbol):
	"""This draws a 5-pointed star.

		possible attributes:
		'x', 'y', 'size', 'fillColor', 'strokeColor'

		"""
	_attrMap = AttrMap(BASE=_Symbol,
			angle = AttrMapValue(isNumber, desc='angle'),
			)

	def __init__(self):
		self.x = 0
		self.y = 0
		self.size = 100 
		self.color = colors.yellow
		self.strokeColor = None
		self.angle = 0

	def demo(self):
		D = shapes.Drawing(200, 100)
		et = Star()
		et.x=50
		et.y=0
		D.add(et)
		labelFontSize = 10
		D.add(shapes.String(et.x+(et.size/2),(et.y-(1.2*labelFontSize)),
							et.__class__.__name__, fillColor=colors.black, textAnchor='middle',
							fontSize=labelFontSize))
		return D
	
	def draw(self):
		# general widget bits
		s = float(self.size)  #abbreviate as we will use this a lot 
		g = shapes.Group()

		# star specific bits
		h = s/5
		z = s/2
		star = shapes.Polygon(points = [
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
					fillColor = self.color,
					strokeColor = self.strokeColor,
					strokeWidth=s/50)
		g.rotate(self.angle)
		g.shift(self.x,self.y)
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

	def __init__(self):
		self.x = 0
		self.y = 0
		self.size = 100
		self.fillColor = colors.white
		self.border=1
		self.kind = None

	def availableFlagNames(self):
		'''return a list of the things we can display'''
		return filter(lambda x: x is not None, self._attrMap['kind'].validate._enum)

	def demo(self):
		D = shapes.Drawing(200, 100)
		name = self.availableFlagNames()
		import time
		name = name[int(time.time()) % len(name)]
		fx = Flag()
		fx.kind = name
		fx.x = 0
		fx.y = 0
		D.add(fx)
		labelFontSize = 10
		D.add(shapes.String(fx.x+(fx.size/2),(fx.y-(1.2*labelFontSize)),
							name, fillColor=colors.black, textAnchor='middle',
							fontSize=labelFontSize))
		labelFontSize = int(fx.size/4)
		D.add(shapes.String(fx.x+(fx.size),(fx.y+((fx.size/2))),
							"SAMPLE", fillColor=colors.gold, textAnchor='middle',
							fontSize=labelFontSize, fontName="Helvetica-Bold"))
		return D

	def _Flag_UK(self):
		# general widget bits
		s = self.size  # abbreviate as we will use this a lot 
		g = shapes.Group() 
		
		# flag specific bits
		box = shapes.Rect(self.x, self.y, s*2, s, fillColor = colors.navy, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		whitediag1 = shapes.Line(self.x, self.y, self.x+(s*2), self.y+s, fillColor = colors.mintcream, strokeColor = colors.mintcream, strokeWidth=20)
		g.add(whitediag1)
		
		whitediag2 = shapes.Line(self.x, self.y+s, self.x+(s*2), self.y, fillColor = colors.mintcream, strokeColor = colors.mintcream, strokeWidth=20)
		g.add(whitediag2)

		reddiag1 = shapes.Polygon(points=[self.x, self.y+s-(s/15), self.x+(s-((s/10)*4)), self.y+(s*0.65), self.x+(s-(s/10)*3), self.y+(s*0.65), self.x, self.y+s], fillColor = colors.red, strokeColor = None, strokeWidth=0)
		g.add(reddiag1)

		reddiag2 = shapes.Polygon(points=[self.x, self.y, self.x+(s-((s/10)*3)), self.y+(s*0.35), self.x+(s-((s/10)*2)), self.y+(s*0.35), self.x+(s/10), self.y], fillColor = colors.red, strokeColor = None, strokeWidth=0)
		g.add(reddiag2) 

		reddiag3 = shapes.Polygon(points=[self.x+s*2, self.y+s, self.x+(s+((s/10)*3)), self.y+(s*0.65), self.x+(s+((s/10)*2)), self.y+(s*0.65), self.x+(s*2)-(s/10), self.y+s], fillColor = colors.red, strokeColor = None, strokeWidth=0)
		g.add(reddiag3)

		reddiag4 = shapes.Polygon(points=[self.x+s*2, self.y+(s/15), self.x+(s+((s/10)*4)), self.y+(s*0.35), self.x+(s+((s/10)*3)), self.y+(s*0.35), self.x+(s*2), self.y], fillColor = colors.red, strokeColor = None, strokeWidth=0)
		g.add(reddiag4)   


		whiteline1 = shapes.Rect(self.x+((s*0.42)*2), self.y, width=(0.16*s)*2, height=s, fillColor = colors.mintcream, strokeColor = None, strokeWidth=0)
		g.add(whiteline1)
		
		whiteline2 = shapes.Rect(self.x, self.y+(s*0.35), width=s*2, height=s*0.3, fillColor = colors.mintcream, strokeColor = None, strokeWidth=0)
		g.add(whiteline2)
		

		redline1 = shapes.Rect(self.x+((s*0.45)*2), self.y, width=(0.1*s)*2, height=s, fillColor = colors.red, strokeColor = None, strokeWidth=0)
		g.add(redline1)
		
		redline2 = shapes.Rect(self.x, self.y+(s*0.4), width=s*2, height=s*0.2, fillColor = colors.red, strokeColor = None, strokeWidth=0)
		g.add(redline2)

		g.add(self.borderdraw())
		
		return g

	def _Flag_None(self):
		# general widget bits
		s = self.size  # abbreviate as we will use this a lot 
		g = shapes.Group() 
		
		# flag specific bits
		box = shapes.Rect(self.x, self.y, s*2, s, fillColor = colors.purple, strokeColor = colors.black, strokeWidth=0)
		g.add(box)
		g.add(self.borderdraw())
		return g
			
	def borderdraw(self):
		# general widget bits
		s = self.size  # abbreviate as we will use this a lot 
		g = shapes.Group() 
		g.add(shapes.Rect(self.x-1, self.y-1, width=(s*2)+2, height=s+2,
				fillColor = None, strokeColor = self.fillColor, strokeWidth=0))

		if self.border:
			g.add(shapes.Rect(self.x, self.y, width=s*2, height=s,
				fillColor = None, strokeColor = colors.black, strokeWidth=0))
		return g

	def draw(self):
		kind = self.kind or 'None'
		return getattr(self,'_Flag_'+kind)()

	def _Flag_USA(self):
		# general widget bits
		s = self.size  # abbreviate as we will use this a lot 
		g = shapes.Group() 
		
		# flag specific bits
		box = shapes.Rect(self.x, self.y, s*2, s, fillColor = colors.mintcream, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		for stripecounter in range (13,0, -1):
			stripeheight = s/13.0
			if not (stripecounter%2 == 0):
				stripecolor = colors.red
			else:
				stripecolor = colors.mintcream
			redorwhiteline = shapes.Rect(self.x, self.y+(s-(stripeheight*stripecounter)), width=s*2, height=stripeheight,
				fillColor = stripecolor, strokeColor = None, strokeWidth=20)
			g.add(redorwhiteline)

		bluebox = shapes.Rect(self.x, self.y+(s-(stripeheight*7)), width=0.8*s, height=stripeheight*7,
			fillColor = colors.darkblue, strokeColor = None, strokeWidth=0)
		g.add(bluebox)
		
		for starxcounter in range (0,5):
			for starycounter in range (0,5):
				ls = Star()
				lss = ls.size = s*0.045
				ls.color = colors.mintcream
				ls.x = self.x-(s/22)+lss/2
				ls.x = ls.x+(s/7)+(starxcounter*(s/14))+(starxcounter*(s/14))
				ls.y = (self.y+s-(starycounter*(s/9)))+lss/2
				g.add(ls)

		for starxcounter in range (0,6):
			for starycounter in range (0,6):
				ls = Star()
				lss = ls.size = s*0.045
				ls.color = colors.mintcream
				ls.x = self.x-(s/22)+lss/2
				ls.x = ls.x+(s/14)+((starxcounter*(s/14))+(starxcounter*(s/14)))
				ls.y = (self.y+s-(starycounter*(s/9))+(s/18))+lss/2
				g.add(ls)

		g.add(self.borderdraw())
		
		return g

	def _Flag_Austria(self):
		# general widget bits
		s = self.size  # abbreviate as we will use this a lot 
		g = shapes.Group() 
		
		# flag specific bits
		box = shapes.Rect(self.x, self.y, s*2, s, fillColor = colors.mintcream,
			strokeColor = colors.black, strokeWidth=0)
		g.add(box)


		redbox1 = shapes.Rect(self.x, self.y, width=s*2.0, height=s/3.0,
			fillColor = colors.red, strokeColor = None, strokeWidth=0)
		g.add(redbox1)
		
		redbox2 = shapes.Rect(self.x, self.y+((s/3.0)*2.0), width=s*2.0, height=s/3.0,
			fillColor = colors.red, strokeColor = None, strokeWidth=0)
		g.add(redbox2)

		g.add(self.borderdraw())
		
		return g

	def _Flag_Belgium(self):
		# general widget bits
		s = self.size  # abbreviate as we will use this a lot 
		g = shapes.Group() 
		
		# flag specific bits
		box = shapes.Rect(self.x, self.y, s*2, s,
			fillColor = colors.black, strokeColor = colors.black, strokeWidth=0)
		g.add(box)


		box1 = shapes.Rect(self.x, self.y, width=(s/3.0)*2.0, height=s,
			fillColor = colors.black, strokeColor = None, strokeWidth=0)
		g.add(box1)
		
		box2 = shapes.Rect(self.x+((s/3.0)*2.0), self.y, width=(s/3.0)*2.0, height=s,
			fillColor = colors.gold, strokeColor = None, strokeWidth=0)
		g.add(box2)

		box3 = shapes.Rect(self.x+((s/3.0)*4.0), self.y, width=(s/3.0)*2.0, height=s,
			fillColor = colors.red, strokeColor = None, strokeWidth=0)
		g.add(box3)

		g.add(self.borderdraw())
		
		return g

	def _Flag_Denmark(self):
		# general widget bits
		s = self.size  # abbreviate as we will use this a lot 
		g = shapes.Group()
		self.border = 0
		
		# flag specific bits
		box = shapes.Rect(self.x, self.y, (s*2)*0.70, s,
			fillColor = colors.red, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		whitebox1 = shapes.Rect(self.x+((s/5)*2), self.y, width=s/6, height=s,
			fillColor = colors.mintcream, strokeColor = None, strokeWidth=0)
		g.add(whitebox1)
		
		whitebox2 = shapes.Rect(self.x, self.y+((s/2)-(s/12)), width=(s*2)*0.70, height=s/6,
			fillColor = colors.mintcream, strokeColor = None, strokeWidth=0)
		g.add(whitebox2)

		g.add(self.borderdraw())

		outerbox = shapes.Rect(self.x, self.y, (s*2)*0.70, s,
							fillColor = None, strokeColor = colors.white,
			strokeWidth=0)
		g.add(outerbox)
		outerbox = shapes.Rect(self.x, self.y, (s*2)*0.70, s,
							fillColor = None, strokeColor = colors.black,
			strokeWidth=0)
		g.add(outerbox)
		return g

	def _Flag_Finland(self):
		# general widget bits
		s = self.size  # abbreviate as we will use this a lot 
		g = shapes.Group() 
		
		# crossbox specific bits
		box = shapes.Rect(self.x, self.y, s*2, s,
			fillColor = colors.ghostwhite, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		blueline1 = shapes.Rect(self.x+(s*0.6), self.y, width=0.3*s, height=s,
			fillColor = colors.darkblue, strokeColor = None, strokeWidth=0)
		g.add(blueline1)
		
		blueline2 = shapes.Rect(self.x, self.y+(s*0.4), width=s*2, height=s*0.3,
			fillColor = colors.darkblue, strokeColor = None, strokeWidth=0)
		g.add(blueline2)

		g.add(self.borderdraw())
		
		return g

	def _Flag_France(self):
		# general widget bits
		s = self.size  # abbreviate as we will use this a lot 
		g = shapes.Group() 
		
		# flag specific bits
		box = shapes.Rect(self.x, self.y, s*2, s,
			fillColor = colors.navy, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		bluebox = shapes.Rect(self.x, self.y, width=((s/3.0)*2.0), height=s,
			fillColor = colors.blue, strokeColor = None, strokeWidth=0)
		g.add(bluebox)
		
		whitebox = shapes.Rect(self.x+((s/3.0)*2.0), self.y, width=((s/3.0)*2.0), height=s,
			fillColor = colors.mintcream, strokeColor = None, strokeWidth=0)
		g.add(whitebox)

		redbox = shapes.Rect(self.x+((s/3.0)*4.0), self.y, width=((s/3.0)*2.0), height=s,
			fillColor = colors.red,
			strokeColor = None,
			strokeWidth=0)
		g.add(redbox)

		g.add(self.borderdraw())
		
		return g

	def _Flag_Germany(self):
		# general widget bits
		s = self.size  # abbreviate as we will use this a lot 
		g = shapes.Group() 
		
		# flag specific bits
		box = shapes.Rect(self.x, self.y, s*2, s,
				fillColor = colors.gold, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		blackbox1 = shapes.Rect(self.x, self.y+((s/3.0)*2.0), width=s*2.0, height=s/3.0,
			fillColor = colors.black, strokeColor = None, strokeWidth=0)
		g.add(blackbox1)
		
		redbox1 = shapes.Rect(self.x, self.y+(s/3.0), width=s*2.0, height=s/3.0,
			fillColor = colors.orangered, strokeColor = None, strokeWidth=0)
		g.add(redbox1)

		g.add(self.borderdraw())
		
		return g

	def _Flag_Greece(self):
		# general widget bits
		s = self.size  # abbreviate as we will use this a lot 
		g = shapes.Group() 
		
		# flag specific bits
		box = shapes.Rect(self.x, self.y, s*2, s, fillColor = colors.gold,
						strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		for stripecounter in range (9,0, -1):
			stripeheight = s/9.0
			if not (stripecounter%2 == 0):
				stripecolor = colors.deepskyblue
			else:
				stripecolor = colors.mintcream

			blueorwhiteline = shapes.Rect(self.x, self.y+(s-(stripeheight*stripecounter)), width=s*2, height=stripeheight,
				fillColor = stripecolor, strokeColor = None, strokeWidth=20)
			g.add(blueorwhiteline)	

		bluebox1 = shapes.Rect(self.x, self.y+((s)-stripeheight*5), width=(stripeheight*5), height=stripeheight*5,
			fillColor = colors.deepskyblue, strokeColor = None, strokeWidth=0)
		g.add(bluebox1)
		
		whiteline1 = shapes.Rect(self.x, self.y+((s)-stripeheight*3), width=stripeheight*5, height=stripeheight,
			fillColor = colors.mintcream, strokeColor = None, strokeWidth=0)
		g.add(whiteline1)

		whiteline2 = shapes.Rect(self.x+(stripeheight*2), self.y+((s)-stripeheight*5), width=stripeheight, height=stripeheight*5,
			fillColor = colors.mintcream, strokeColor = None, strokeWidth=0)
		g.add(whiteline2)

		g.add(self.borderdraw())
		
		return g

	def _Flag_Ireland(self):
		# general widget bits
		s = self.size  # abbreviate as we will use this a lot 
		g = shapes.Group() 
		
		# flag specific bits
		box = shapes.Rect(self.x, self.y, s*2, s,
			fillColor = colors.forestgreen, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		whitebox = shapes.Rect(self.x+((s*2.0)/3.0), self.y, width=(2.0*(s*2.0)/3.0), height=s,
				fillColor = colors.mintcream, strokeColor = None, strokeWidth=0)
		g.add(whitebox)
		
		orangebox = shapes.Rect(self.x+((2.0*(s*2.0)/3.0)), self.y, width=(s*2.0)/3.0, height=s,
			fillColor = colors.darkorange, strokeColor = None, strokeWidth=0)
		g.add(orangebox)

		g.add(self.borderdraw())
		
		return g

	def _Flag_Italy(self):
		# general widget bits
		s = self.size  # abbreviate as we will use this a lot 
		g = shapes.Group() 
		
		# flag specific bits
		box = shapes.Rect(self.x, self.y, s*2, s,
				fillColor = colors.forestgreen, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		whitebox = shapes.Rect(self.x+((s*2.0)/3.0), self.y, width=(2.0*(s*2.0)/3.0), height=s,
				fillColor = colors.mintcream, strokeColor = None, strokeWidth=0)
		g.add(whitebox)
		
		redbox = shapes.Rect(self.x+((2.0*(s*2.0)/3.0)), self.y, width=(s*2.0)/3.0, height=s,
				fillColor = colors.red, strokeColor = None, strokeWidth=0)
		g.add(redbox)

		g.add(self.borderdraw())
		
		return g

	def _Flag_Luxembourg(self):
		# general widget bits
		s = self.size  # abbreviate as we will use this a lot 
		g = shapes.Group() 
		
		# flag specific bits
		box = shapes.Rect(self.x, self.y, s*2, s,
			fillColor = colors.mintcream, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		redbox = shapes.Rect(self.x, self.y+((s/3.0)*2.0), width=s*2.0, height=s/3.0,
				fillColor = colors.red, strokeColor = None, strokeWidth=0)
		g.add(redbox)
		
		bluebox = shapes.Rect(self.x, self.y, width=s*2.0, height=s/3.0,
				fillColor = colors.dodgerblue, strokeColor = None, strokeWidth=0)
		g.add(bluebox)

		g.add(self.borderdraw())
		
		return g

	def _Flag_Holland(self):
		# general widget bits
		s = self.size  # abbreviate as we will use this a lot 
		g = shapes.Group() 
		
		# flag specific bits
		box = shapes.Rect(self.x, self.y, s*2, s,
			fillColor = colors.mintcream, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		redbox = shapes.Rect(self.x, self.y+((s/3.0)*2.0), width=s*2.0, height=s/3.0,
				fillColor = colors.red, strokeColor = None, strokeWidth=0)
		g.add(redbox)
		
		bluebox = shapes.Rect(self.x, self.y, width=s*2.0, height=s/3.0,
				fillColor = colors.darkblue, strokeColor = None, strokeWidth=0)
		g.add(bluebox)

		g.add(self.borderdraw())
		
		return g

	def _Flag_Portugal(self):
		return shapes.Group()

	def _Flag_Spain(self):
		# general widget bits
		s = self.size  # abbreviate as we will use this a lot 
		g = shapes.Group() 
		
		# flag specific bits
		box = shapes.Rect(self.x, self.y, s*2, s,
				fillColor = colors.yellow, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		redbox1 = shapes.Rect(self.x, self.y+((s/4)*3), width=s*2, height=s/4,
			fillColor = colors.red, strokeColor = None, strokeWidth=0)
		g.add(redbox1)
		
		redbox2 = shapes.Rect(self.x, self.y, width=s*2, height=s/4,
			fillColor = colors.red,
			strokeColor = None,
			strokeWidth=0)
		g.add(redbox2)

		g.add(self.borderdraw())
		
		return g

	def _Flag_Sweden(self):
		# general widget bits
		s = self.size  # abbreviate as we will use this a lot 
		g = shapes.Group()
		self.border = 0
		
		# flag specific bits
		box = shapes.Rect(self.x, self.y, (s*2)*0.70, s,
			fillColor = colors.dodgerblue, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		box1 = shapes.Rect(self.x+((s/5)*2), self.y, width=s/6, height=s,
				fillColor = colors.gold, strokeColor = None, strokeWidth=0)
		g.add(box1)
		
		box2 = shapes.Rect(self.x, self.y+((s/2)-(s/12)), width=(s*2)*0.70, height=s/6,
			fillColor = colors.gold,
			strokeColor = None,
			strokeWidth=0)
		g.add(box2)

		g.add(self.borderdraw())

		outerbox = shapes.Rect(self.x, self.y, (s*2)*0.70, s,
							fillColor = None,
							strokeColor = colors.black,
			strokeWidth=0)
		g.add(outerbox)
		return g

	def _Flag_Norway(self):
		s = self.size  # abbreviate as we will use this a lot 
		g = shapes.Group()
		self.border = 0
		
		box = shapes.Rect(self.x, self.y, (s*2)*0.7, s,
				fillColor = colors.red, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		box = shapes.Rect(self.x, self.y, (s*2)*0.7, s,
				fillColor = colors.red, strokeColor = colors.black, strokeWidth=0)
		g.add(box)

		whiteline1 = shapes.Rect(self.x+((s*0.2)*2), self.y, width=s*0.2, height=s,
				fillColor = colors.ghostwhite, strokeColor = None, strokeWidth=0)
		g.add(whiteline1)
		
		whiteline2 = shapes.Rect(self.x, self.y+(s*0.4), width=((s*2)*0.70), height=s*0.2,
				fillColor = colors.ghostwhite, strokeColor = None, strokeWidth=0)
		g.add(whiteline2)

		blueline1 = shapes.Rect(self.x+((s*0.225)*2), self.y, width=0.1*s, height=s,
				fillColor = colors.darkblue, strokeColor = None, strokeWidth=0)
		g.add(blueline1)
		
		blueline2 = shapes.Rect(self.x, self.y+(s*0.45), width=(s*2)*0.7, height=s*0.1,
				fillColor = colors.darkblue, strokeColor = None, strokeWidth=0)
		g.add(blueline2)

		outerbox = shapes.Rect(self.x, self.y, (s*2)*0.70, s, fillColor = None,
				strokeColor = colors.black, strokeWidth=0)
		g.add(outerbox)
		return g

	def _Flag_CzechRepublic(self):
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
		
		bluewedge = shapes.Polygon(points = [ self.x, self.y, self.x+s, self.y+(s/2), self.x, self.y+s],
					fillColor = colors.darkblue, strokeColor = None, strokeWidth=0)
		g.add(bluewedge)
		g.add(self.borderdraw())
		return g

	def _Flag_Turkey(self):
		# general widget bits
		s = float(self.size)  # abbreviate as we will use this a lot 
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
	
		ws = Star()
		ws.angle = 15
		ws.size = s/5
		ws.x = self.x+(s*0.5)*2+ws.size/2
		ws.y = self.y+(s*0.5)
		ws.color = colors.mintcream
		ws.strokeColor = None
		g.add(ws)

		g.add(self.borderdraw())
		
		return g

	def _Flag_Switzerland(self):
		# general widget bits
		s = self.size  # abbreviate as we will use this a lot 
		g = shapes.Group() 
		
		# flag specific bits
		box = shapes.Rect(self.x, self.y, s, s, fillColor = colors.red,
						strokeColor = colors.black, strokeWidth=0)
		g.add(box)
		whitebar1 = shapes.Line(self.x+(s/2), self.y+(s/5.5), self.x+(s/2), self.y+(s-(s/5.5)),
				fillColor = colors.mintcream, strokeColor = colors.mintcream, strokeWidth=(s/5))
		g.add(whitebar1)
		whitebar2 = shapes.Line(self.x+(s/5.5), self.y+(s/2), self.x+(s-(s/5.5)), self.y+(s/2),
			fillColor = colors.mintcream, strokeColor = colors.mintcream, strokeWidth=s/5)
		g.add(whitebar2)

		outerbox = shapes.Rect(self.x, self.y, s, s,
							fillColor = None, strokeColor = colors.black, strokeWidth=0)
		g.add(outerbox)		
		return g

	def _Flag_EU(self):
		# general widget bits
		s = float(self.size)  # abbreviate as we will use this a lot 
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
			gs = Star()
			gs.x=pointslist[innercounter]+s/20
			gs.y=pointslist[innercounter+1]+s/20
			gs.size=s/10
			gs.color=colors.gold
			g.add(gs)
			innercounter=innercounter+2
			
		box = shapes.Rect(self.x, self.y, width=s/4, height=s,
				fillColor = self.fillColor, strokeColor = None, strokeWidth=0)
		g.add(box)

		box2 = shapes.Rect(self.x+((s*2)-s/4), self.y, width=s/4, height=s,
				fillColor = self.fillColor, strokeColor = None, strokeWidth=0)
		g.add(box2)

		g.add(self.borderdraw())
		
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
		if not D: D = shapes.Drawing(450,650)
		flag = makeFlag(name)
		i = flags.index(name)
		flag.x = X[i%2]
		flag.y = y
		D.add(flag)
		D.add(shapes.String(flag.x+(flag.size/2),(flag.y-(1.2*labelFontSize)),
				name, fillColor=colors.black, textAnchor='middle', fontSize=labelFontSize))
		if i%2: y = y - 125
		if (i%2 and y<0) or name==flags[-1]:
			renderPDF.drawToFile(D, 'flags%02d.pdf'%f, 'flags.py - Page #%d'%(f+1))
			y = Y0
			f = f+1
			D = None

if __name__=='__main__':
	test()
