"""
This modules defines a collection of markers used in charts.
"""
from reportlab.graphics.shapes import Rect, Line, Circle, Polygon, Drawing, Group
from reportlab.graphics.widgets.signsandsymbols import SmileyFace
from reportlab.graphics.widgetbase import Widget
from reportlab.lib.validators import isNumber, isColorOrNone, OneOf
from reportlab.lib.attrmap import AttrMap, AttrMapValue
from reportlab.lib.colors import black

class Marker(Widget):
	'''A polymorphic class of markers'''
	_attrMap = AttrMap(BASE=Widget,
					kind = AttrMapValue(
							OneOf(None, 'Square', 'Diamond', 'Circle', 'Cross', 'Smiley',
								'FilledSquare', 'FilledCircle', 'FilledDiamond', 'FilledCross'),
							desc='marker type name'),
					size = AttrMapValue(isNumber,desc='marker size'),
					x = AttrMapValue(isNumber,desc='marker x coordinate'),
					y = AttrMapValue(isNumber,desc='marker y coordinate'),
					dx = AttrMapValue(isNumber,desc='marker x coordinate adjustment'),
					dy = AttrMapValue(isNumber,desc='marker y coordinate adjustment'),
					fillColor = AttrMapValue(isColorOrNone, desc='marker fill colour'),
					strokeColor = AttrMapValue(isColorOrNone, desc='marker stroke colour'),
					strokeWidth = AttrMapValue(isNumber, desc='marker stroke width'),
					)

	def __init__(self,*args,**kw):
		self.kind = None
		self.strokeColor = black
		self.strokeWidth = 0.1
		self.fillColor = None
		self.size = 5
		self.x = self.y = self.dx = self.dy = 0

	def _Smiley(self):
		d = self.size
		s = SmileyFace()
		s.fillColor = self.fillColor
		s.strokeWidth = self.strokeWidth
		s.strokeColor = self.strokeColor
		s.x = self.x+self.dx-d
		s.y = self.y+self.dy-d
		s.size = d*2
		return s

	def _Square(self):
		d = self.size/2.0
		s = Rect(self.x+self.dx-d, self.y+self.dy-d, 2*d, 2*d)
		s.fillColor = self.fillColor
		s.strokeColor = self.strokeColor
		s.strokeWidth = self.strokeWidth
		return s

	def _Diamond(self):
		d = self.size/2.0
		x, y = self.x+self.dx, self.y+self.dy
		s = Polygon((x-d, y, x,y+d, x+d,y, x, y-d))
		s.fillColor = self.fillColor
		s.strokeColor = self.strokeColor
		s.strokeWidth = self.strokeWidth
		return s

	def _Circle(self):
		s = Circle(self.x+self.dx, self.y+self.dy, self.size/2.0)
		s.fillColor = self.fillColor
		s.strokeColor = self.strokeColor
		s.strokeWidth = self.strokeWidth
		return s

	def _Cross(self):
		s = float(self.size)
		h, s = s/2, s/6
		x, y = self.x+self.dx, self.y+self.dy
		return Polygon([x-s,y-h,x-s,y-s,x-h,y-s,x-h,y+s,x-s,y+s,x-s,y+h,
						x+s,y+h,x+s,y+s,x+h,y+s,x+h,y-s,x+s,y-s,x+s,y-h],
						strokeWidth = self.strokeWidth, strokeColor= self.strokeColor,
						fillColor=self.fillColor)


	def _doFill(self):
		old = self.fillColor
		if old is None:
			self.fillColor = self.strokeColor
		r = (self.kind and getattr(self,'_'+self.kind[6:]) or Group)()
		self.fillColor = old
		return r

	_FilledCircle = _doFill
	_FilledSquare = _doFill
	_FilledDiamond = _doFill
	_FilledCross = _doFill

	def draw(self):
		return (self.kind and getattr(self,'_'+self.kind) or Group)()

if __name__=='__main__':
	D = Drawing()
	D.add(Marker())
	D.save(fnRoot='Marker',formats=['pdf'], outDir='/tmp')
