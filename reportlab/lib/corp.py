#!/bin/env python
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/corp.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/corp.py,v 1.4 2001/08/14 21:18:35 johnprecedo Exp $
""" This module includes some reusable routines for ReportLab's
 'Corporate Image' - the logo, standard page backdrops and
 so on - you are advised to do the same for your own company!"""
__version__=''' $Id: corp.py,v 1.4 2001/08/14 21:18:35 johnprecedo Exp $ '''

from reportlab.lib.units import inch,cm
from reportlab.lib.validators import *
from reportlab.lib.attrmap import *
from reportlab.graphics import shapes
from reportlab.graphics.widgetbase import Widget
from reportlab.lib.colors import Color, black, white, ReportLabBlue
from reportlab.pdfbase.pdfmetrics import stringWidth
from math import sin, pi

class RL_CorpLogo(Widget):
	"""The ReportLab Logo.

	New version created by John Precedo on 7-8 August 2001.
	Based on bitmapped imaged from E-Id.
	Improved by Robin Becker."""

	_attrMap = AttrMap(
		x = AttrMapValue(isNumber),
		y = AttrMapValue(isNumber),
		height = AttrMapValue(isNumberOrNone),
		width = AttrMapValue(isNumberOrNone),
		fillColor = AttrMapValue(isColorOrNone),
		strokeColor = AttrMapValue( isColorOrNone)
		)

	_h = 90.5
	_w = 136.5
	_text='R e p o r t L a b'
	_fontName = 'Helvetica-Bold'
	_fontSize = 16

	def __init__(self):
		self.fillColor = ReportLabBlue
		self.strokeColor = white
		self.x = 0
		self.y = 0
		self.height = self._h
		self.width = self._w

	def demo(self):
		D = shapes.Drawing(self.width, self.height)
		D.add(self)
		return D

	def _getText(self, x=0, y=0, color=None):
		return shapes.String(x,y, self._text, fontName=self._fontName, fontSize=self._fontSize, fillColor=color)

	def _sw(self,f=None,l=None):
		text = self._text
		if f is None: f = 0
		if l is None: l = len(text)
		return stringWidth(text[f:l],self._fontName,self._fontSize)

	def _addPage(self, g, strokeWidth=3, color=None, dx=0, dy=0):
		x1, x2 = 31.85+dx, 80.97+dx
		fL = 10	# fold length
		y1, y2 = dy-34, dy+50.5
		L = [[x1,dy-4,x1,y1, x2, y1, x2, dy-1],
			[x1,dy+11,x1,y2,x2-fL,y2,x2,y2-fL,x2,dy+14],
			[x2-10,y2,x2-10,y2-fL,x2,y2-fL]]

		for l in L:
			g.add(shapes.PolyLine(l, strokeWidth=strokeWidth, strokeColor=color, strokeLineJoin=0))

	def draw(self):
		sx = 0.5
		fillColor = self.fillColor
		strokeColor = self.strokeColor
		shadow = Color(fillColor.red*sx,fillColor.green*sx,fillColor.blue*sx)
		g = shapes.Group()
		g2= shapes.Group()
		g.add(shapes.Rect(fillColor=fillColor, strokeColor=fillColor, x=0, y=0, width=self._w, height=self._h))
		sx = (self._w-2)/self._sw()
		g2.scale(sx,1)
		self._addPage(g2,strokeWidth=3,dx=2,dy=-2.5,color=shadow)
		self._addPage(g2,strokeWidth=3,color=strokeColor)
		g2.scale(1/sx,1)
		g2.add(self._getText(x=1,y=0,color=shadow))
		g2.add(self._getText(x=0,y=1,color=strokeColor))
		g2.scale(sx,1)
		g2.skew(kx=10, ky=0)
		g2.shift(0,38)
		g.add(g2)
		g.scale(self.width/self._w,self.height/self._h)
		g.shift(self.x,self.y)
		return g

class ReportLabLogo:
	"""vector reportlab logo centered in a 250x by 150y rectangle"""
	
	def __init__(self, atx=0, aty=0, width=2.5*inch, height=1.5*inch, powered_by=0):
		self.origin = (atx, aty)
		self.dimensions = (width, height)
		self.powered_by = powered_by
		
	def draw(self, canvas):
		from reportlab.graphics import renderPDF
		canvas.saveState()
		(atx,aty) = self.origin
		(width, height) = self.dimensions
		logo = RL_CorpLogo()
		logo.width, logo.height = width, height
		renderPDF.draw(logo.demo(),canvas,atx,aty,0)
		canvas.restoreState()

class RL_BusinessCard(Widget):
	"""Widget that creates a single business card.
	Uses RL_CorpLogo for the logo.

	For a black border around your card, set self.border to 1.
	To change the details on the card, over-ride the following properties:
	self.name, self.position, self.telephone, self.mobile, self.fax, self.email, self.web
	The office locations are set in self.rh_blurb_top ("London office" etc), and
	self.rh_blurb_bottom ("New York office" etc).
	"""
	# for items where it 'isString' the string can be an empty one...
	_attrMap = AttrMap(
		fillColor = AttrMapValue(isColorOrNone),
		strokeColor = AttrMapValue(isColorOrNone),
		altStrokeColor = AttrMapValue(isColorOrNone), 
		x = AttrMapValue(isNumber),
		y = AttrMapValue(isNumber),
		height = AttrMapValue(isNumber),
		width = AttrMapValue(isNumber),
		borderWidth = AttrMapValue(isNumber),
		bleed=AttrMapValue(isNumberOrNone),
		cropMarks=AttrMapValue(isBoolean),
		border=AttrMapValue(isBoolean),
		name=AttrMapValue(isString),
		position=AttrMapValue(isString),
		telephone=AttrMapValue(isString),
		mobile=AttrMapValue(isString),
		fax=AttrMapValue(isString),
		email=AttrMapValue(isString),
		web=AttrMapValue(isString),
		rh_blurb_top=AttrMapValue(isListOfStringsOrNone),
		rh_blurb_bottom=AttrMapValue(isListOfStringsOrNone)
		)

	_h = 5.35*cm
	_w = 9.25*cm
	_fontName = 'Helvetica-Bold'
	_strapline = "strategic reporting solutions for e-business"


	def __init__(self):
		self.fillColor = ReportLabBlue
		self.strokeColor = black
		self.altStrokeColor = white
		self.x = 0
		self.y = 0
		self.height = self._h
		self.width = self._w
		self.borderWidth = self.width/6.15
		self.bleed=0.2*cm
		self.cropMarks=1
		self.border=0
		#Over-ride these with your own info
		self.name="Joe Cool"
		self.position="Freelance Demonstrator"
		self.telephone="020 8545 7271"
		self.mobile="-"
		self.fax="020 8544 1311"
		self.email="info@reportlab.com"
		self.web="www.reportlab.com"
		self.rh_blurb_top = ["London office:",
					 "ReportLab Europe Ltd",
					 "Lombard Business Park",
					 "8 Lombard Road",
					 "Wimbledon",
					 "London SW19 3TZ",
					 "United Kingdom"]
		self.rh_blurb_bottom = ["New York office:",
					 "ReportLab Inc",
					 "219 Harper Street",
					 "Highland Park",
					 "New Jersey  08904",
					 "USA"]

	def demo(self):
		D = shapes.Drawing(self.width, self.height)
		D.add(self)
		return D

	def draw(self):
		fillColor = self.fillColor
		strokeColor = self.strokeColor

		g = shapes.Group()
		g.add(shapes.Rect(x = 0, y = 0,
						  fillColor = self.fillColor,
						  strokeColor = self.fillColor,
						  width = self.borderWidth,
						  height = self.height))
		g.add(shapes.Rect(x = 0, y = self.height-self.borderWidth,
						  fillColor = self.fillColor,
						  strokeColor = self.fillColor,
						  width = self.width,
						  height = self.borderWidth))

		g2 = shapes.Group()
		rl=RL_CorpLogo()
		rl.height = 1.25*cm
		rl.width = 1.9*cm	
		rl.draw()
		g2.add(rl)
		g.add(g2)
		g2.shift(x=(self.width-(rl.width+(self.width/42))),
				 y=(self.height - (rl.height+(self.height/42))))

		g.add(shapes.String(x = self.borderWidth/5.0,
							y = ((self.height - (rl.height+(self.height/42)))+((38/90.5)*rl.height)),
							fontSize = 6,
							fillColor = self.altStrokeColor,
							fontName = "Helvetica-BoldOblique",
							textAnchor = 'start',
							text = self._strapline))

		leftText=["Tel:", "Mobile:", "Fax:", "Email:", "Web:"]
		leftDetails=[self.telephone,self.mobile,self.fax,self.email,self.web]
		leftText.reverse()
		leftDetails.reverse()
		for f in range(len(leftText),0,-1):
			g.add(shapes.String(x = self.borderWidth+(self.borderWidth/5.0),
							y = (self.borderWidth/5.0)+((f-1)*(5*1.2)),
							fontSize = 5,
							fillColor = self.strokeColor,
							fontName = "Helvetica",
							textAnchor = 'start',
							text = leftText[f-1]))
			g.add(shapes.String(x = self.borderWidth+(self.borderWidth/5.0)+self.borderWidth,
							y = (self.borderWidth/5.0)+((f-1)*(5*1.2)),
							fontSize = 5,
							fillColor = self.strokeColor,
							fontName = "Helvetica",
							textAnchor = 'start',
							text = leftDetails[f-1]))

		rightText=self.rh_blurb_bottom
		rightText.reverse()
		for f in range(len(rightText),0,-1):
			g.add(shapes.String(x = self.width-((self.borderWidth/5.0)),
							y = (self.borderWidth/5.0)+((f-1)*(5*1.2)),
							fontSize = 5,
							fillColor = self.strokeColor,
							fontName = "Helvetica",
							textAnchor = 'end',
							text = rightText[f-1]))

		ty = (self.height-self.borderWidth-(self.borderWidth/5.0)+2)
#		g.add(shapes.Line(self.borderWidth, ty, self.borderWidth+(self.borderWidth/5.0), ty))
#		g.add(shapes.Line(self.borderWidth+(self.borderWidth/5.0), ty, self.borderWidth+(self.borderWidth/5.0),
#						  ty+(self.borderWidth/5.0)))
#		g.add(shapes.Line(self.borderWidth, ty-10,
#						  self.borderWidth+(self.borderWidth/5.0), ty-10))

		rightText=self.rh_blurb_top
		for f in range(1,(len(rightText)+1)):
			g.add(shapes.String(x = self.width-(self.borderWidth/5.0),
							y = ty-((f)*(5*1.2)),
							fontSize = 5,
							fillColor = self.strokeColor,
							fontName = "Helvetica",
							textAnchor = 'end',
							text = rightText[f-1]))

		g.add(shapes.String(x = self.borderWidth+(self.borderWidth/5.0),
							y = ty-10,
							fontSize = 10,
							fillColor = self.strokeColor,
							fontName = "Helvetica",
							textAnchor = 'start',
							text = self.name))

		ty1 = ty-10*1.2 

		g.add(shapes.String(x = self.borderWidth+(self.borderWidth/5.0),
							y = ty1-8,
							fontSize = 8,
							fillColor = self.strokeColor,
							fontName = "Helvetica",
							textAnchor = 'start',
							text = self.position))
		if self.border:
			g.add(shapes.Rect(x = 0, y = 0,
							  fillColor=None,
							  strokeColor = black,
							  width = self.width,
							  height = self.height))
		g.shift(self.x,self.y)
		return g


def test():
	"""This function produces a pdf with examples. """
	from reportlab.graphics import renderPDF, renderPM

	rl = RL_CorpLogo()
	D = shapes.Drawing(rl.width,rl.height)
	D.add(rl)
	renderPDF.drawToFile(D, 'corplogo.pdf', 'corplogo.pdf')
	print 'Wrote corplogo.pdf'

	rl.width = 129
	rl.height = 86
	D = shapes.Drawing(rl.width,rl.height)
	D.add(rl)
	renderPM.drawToFile(D, 'corplogo.gif')
	print 'Wrote corplogo.gif'

	rl = RL_BusinessCard()
	rl.x=25
	rl.y=25
	rl.border=1
#	rl.cropMarks=1 # not implemented yet
	D = shapes.Drawing(rl.width+50,rl.height+50)
	D.add(rl)
	renderPDF.drawToFile(D, 'RL_BusinessCard.pdf', 'RL_BusinessCard.pdf', showBoundary=0)
	print 'Wrote RL_BusinessCard.pdf'

if __name__=='__main__':
	test()
