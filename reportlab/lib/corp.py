#!/bin/env python
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/corp.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/corp.py,v 1.3 2001/08/08 19:17:23 rgbecker Exp $
""" This module includes some reusable routines for ReportLab's
 'Corporate Image' - the logo, standard page backdrops and
 so on - you are advised to do the same for your own company!"""
__version__=''' $Id: corp.py,v 1.3 2001/08/08 19:17:23 rgbecker Exp $ '''

from reportlab.lib.units import inch
from reportlab.lib.validators import *
from reportlab.lib.attrmap import *
from reportlab.graphics import shapes
from reportlab.graphics.widgetbase import Widget
from reportlab.lib.colors import Color, white, ReportLabBlue
from reportlab.pdfbase.pdfmetrics import stringWidth
from math import sin, pi

class RL_CorpLogo(Widget):
	"""The ReportLab Logo.

	New version created by John Precedo on 7-8 August 2001.
	Based on bitmapped imaged from E-Id.
	Possible attributes"""

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

if __name__=='__main__':
	test()
