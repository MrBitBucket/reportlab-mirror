"""
This modules defines a collection of markers used in charts.
"""
from types import FunctionType, ClassType
from reportlab.graphics.shapes import Rect, Line, Circle, Polygon, Drawing, Group
from reportlab.graphics.widgets.signsandsymbols import SmileyFace
from reportlab.graphics.widgetbase import Widget
from reportlab.lib.validators import isNumber, isColorOrNone, OneOf, Validator
from reportlab.lib.attrmap import AttrMap, AttrMapValue
from reportlab.lib.colors import black
from reportlab.graphics.widgets.flags import Flag
from math import sin, cos, pi
import copy
_toradians = pi/180.0

class Marker(Widget):
	'''A polymorphic class of markers'''
	_attrMap = AttrMap(BASE=Widget,
					kind = AttrMapValue(
							OneOf(None, 'Square', 'Diamond', 'Circle', 'Cross', 'Triangle', 'StarSix',
								'Pentagon', 'Hexagon', 'Heptagon', 'Octagon',
								'FilledSquare', 'FilledCircle', 'FilledDiamond', 'FilledCross',
								'FilledTriangle','FilledStarSix', 'FilledPentagon', 'FilledHexagon',
								'FilledHeptagon', 'FilledOctagon',
								'Smiley'),
							desc='marker type name'),
					size = AttrMapValue(isNumber,desc='marker size'),
					x = AttrMapValue(isNumber,desc='marker x coordinate'),
					y = AttrMapValue(isNumber,desc='marker y coordinate'),
					dx = AttrMapValue(isNumber,desc='marker x coordinate adjustment'),
					dy = AttrMapValue(isNumber,desc='marker y coordinate adjustment'),
					angle = AttrMapValue(isNumber,desc='marker rotation'),
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
		self.x = self.y = self.dx = self.dy = self.angle = 0

	def clone(self):
		return copy.copy(self)

	def _Smiley(self):
		d = self.size/2.0
		s = SmileyFace()
		s.fillColor = self.fillColor
		s.strokeWidth = self.strokeWidth
		s.strokeColor = self.strokeColor
		s.x = -d
		s.y = -d
		s.size = d*2
		return s

	def _Square(self):
		d = self.size/2.0
		s = Rect(-d, -d, 2*d, 2*d)
		s.fillColor = self.fillColor
		s.strokeColor = self.strokeColor
		s.strokeWidth = self.strokeWidth
		return s

	def _Diamond(self):
		d = self.size/2.0
		return self._doPolygon((-d,0,0,d,d,0,0,-d))

	def _Circle(self):
		s = Circle(0, 0, self.size/2.0)
		s.fillColor = self.fillColor
		s.strokeColor = self.strokeColor
		s.strokeWidth = self.strokeWidth
		return s

	def _Cross(self):
		s = float(self.size)
		h, s = s/2, s/6
		return self._doPolygon((-s,-h,-s,-s,-h,-s,-h,s,-s,s,-s,h,s,h,s,s,h,s,h,-s,s,-s,s,-h))

	def _Triangle(self):
		r = float(self.size)/2
		c = 30*_toradians
		s = sin(30*_toradians)*r
		c = cos(c)*r
		return self._doPolygon((0,r,-c,-s,c,-s))

	def _StarSix(self):
		r = float(self.size)/2
		c = 30*_toradians
		s = sin(30*_toradians)*r
		c = cos(c)*r
		z = s/2
		g = c/2
		x, y = self.x+self.dx, self.y+self.dy
		return self._doPolygon((0,r,-z,s,-c,s,-s,0,-c,-s,-z,-s,0,-r,z,-s,c,-s,s,0,c,s,z,s))

	def _Pentagon(self):
		return self._doNgon(5)

	def _Hexagon(self):
		return self._doNgon(6)

	def _Heptagon(self):
		return self._doNgon(7)

	def _Octagon(self):
		return self._doNgon(8)

	def _doPolygon(self,P):
		return Polygon(P, strokeWidth = self.strokeWidth, strokeColor= self.strokeColor, fillColor=self.fillColor)

	def _doFill(self):
		old = self.fillColor
		if old is None:
			self.fillColor = self.strokeColor
		r = (self.kind and getattr(self,'_'+self.kind[6:]) or Group)()
		self.fillColor = old
		return r

	def _doNgon(self,n):
		P = []
		size = float(self.size)/2
		for i in xrange(n):
			r = (2.*i/n+0.5)*pi
			P.append(size*cos(r))
			P.append(size*sin(r))
		return self._doPolygon(P)
			
	_FilledCircle = _doFill
	_FilledSquare = _doFill
	_FilledDiamond = _doFill
	_FilledCross = _doFill
	_FilledTriangle = _doFill
	_FilledStarSix = _doFill
	_FilledPentagon = _doFill
	_FilledHexagon = _doFill
	_FilledHeptagon = _doFill
	_FilledOctagon = _doFill

	def draw(self):
		if self.kind:
			m = getattr(self,'_'+self.kind)()
			x, y, angle = self.x+self.dx, self.y+self.dy, self.angle
			if x or y or angle:
				if not isinstance(m,Group):
					_m, m = m, Group()
					m.add(_m)
				if angle: m.rotate(angle)
				if x or y: m.shift(x,y)
		else:
			m = Group()
		return m

def uSymbol2Symbol(uSymbol,x,y,color):
	if type(uSymbol) == FunctionType:
		symbol = uSymbol(x, y, 5, color)
	elif type(uSymbol) == ClassType and issubclass(uSymbol,Widget):
		size = 10.
		symbol = uSymbol()
		symbol.x = x - (size/2)
		symbol.y = y - (size/2)
		try:
			symbol.size = size
			symbol.color = color
		except:
			pass
	elif isinstance(uSymbol,Marker) or isinstance(uSymbol,Flag):
		symbol = uSymbol.clone()
		if isinstance(uSymbol,Marker): symbol.fillColor = symbol.fillColor or color
		symbol.x, symbol.y = x, y
	else:
		symbol = None
	return symbol

class _isSymbol(Validator):
	def test(self,x):
		return callable(x) or isinstance(x,Marker) or isinstance(x,Flag) \
				or (type(uSymbol)==ClassType and issubclass(uSymbol,Widget))

isSymbol = _isSymbol()

def makeMarker(name):
	if Marker._attrMap['kind'].validate(name):
		m = Marker()
		m.kind = name
	elif Flag._attrMap['kind'].validate(name):
		m = Flag()
		m.kind = name
		m.size = 10
	else:
		raise ValueError, "Invalid marker name %s" % name
	return m

if __name__=='__main__':
	D = Drawing()
	D.add(Marker())
	D.save(fnRoot='Marker',formats=['pdf'], outDir='/tmp')
