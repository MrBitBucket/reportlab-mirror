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
							OneOf(None, 'Square', 'Diamond', 'Circle', 'Smiley'),
							desc='marker type name'),
					size = AttrMapValue(isNumber,desc='marker size'),
					x = AttrMapValue(isNumber,desc='marker x coordinate'),
					y = AttrMapValue(isNumber,desc='marker y coordinate'),
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
		self.x = self.y = 0

	def _Smiley(self):
		d = self.size
		s = SmileyFace()
		s.color = self.fillColor
		s.strokeWidth = self.strokeWidth
		s.strokeColor = self.strokeColor
		s.x = self.x-d
		s.y = self.y-d
		s.size = d*2
		return s

	def _Square(self):
		d = self.size/2.0
		s = Rect(self.x-d, self.y-d, 2*d, 2*d)
		s.fillColor = self.fillColor
		s.strokeColor = self.strokeColor
		s.strokeWidth = self.strokeWidth
		return s

	def _Diamond(self):
		d = self.size/2.0
		x, y = self.x, self.y
		s = Polygon((x-d, y, x,y+d, x+d,y, x, y-d))
		s.fillColor = self.fillColor
		s.strokeColor = self.strokeColor
		s.strokeWidth = self.strokeWidth
		return s

	def _Circle(self):
		s = Circle(self.x, self.y, self.size/2.0)
		s.fillColor = self.fillColor
		s.strokeColor = self.strokeColor
		s.strokeWidth = self.strokeWidth
		return s

	def draw(self):
		return (self.kind and getattr(self,'_'+self.kind) or Group)()

if __name__=='__main__':
	D = Drawing()
	D.add(Marker())
	D.save(fnRoot='Marker',formats=['pdf'], outDir='/tmp')
