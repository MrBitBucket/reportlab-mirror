#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/charts/textlabels.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/charts/textlabels.py,v 1.13 2001/09/11 18:35:50 rgbecker Exp $
import string

from reportlab.lib import colors
from reportlab.lib.validators import isNumber, isNumberOrNone, OneOf, isColorOrNone, isString, isTextAnchor, isBoxAnchor, isBoolean
from reportlab.lib.attrmap import *
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.graphics.shapes import Drawing, Group, Circle, Rect, String, STATE_DEFAULTS
from reportlab.graphics.widgetbase import Widget


class Label(Widget):
	"""A text label to attach to something else, such as a chart axis.

	This allows you to specify an offset, angle and many anchor
	properties relative to the label's origin.	It allows, for example,
	angled multiline axis labels.
	"""
	# fairly straight port of Robin Becker's textbox.py to new widgets
	# framework.

	_attrMap = AttrMap(
        x = AttrMapValue(isNumber),
        y = AttrMapValue(isNumber),
		dx = AttrMapValue(isNumber),
		dy = AttrMapValue(isNumber),
		angle = AttrMapValue(isNumber),
		boxAnchor = AttrMapValue(isBoxAnchor),
		boxStrokeColor = AttrMapValue(isColorOrNone),
		boxStrokeWidth = AttrMapValue(isNumber),
		boxFillColor = AttrMapValue(isColorOrNone),
		fillColor = AttrMapValue(isColorOrNone),
		text = AttrMapValue(isString),
		fontName = AttrMapValue(isString),
		fontSize = AttrMapValue(isNumber),
		leading = AttrMapValue(isNumberOrNone),
		width = AttrMapValue(isNumberOrNone),
		height = AttrMapValue(isNumberOrNone),
		textAnchor = AttrMapValue(isTextAnchor),
		visible = AttrMapValue(isBoolean,desc="True if the label is to be drawn"),
		lineStrokeWidth = AttrMapValue(isNumberOrNone, desc="Non-zero for a drawn line"),
		lineStrokeColor = AttrMapValue(isColorOrNone, desc="Color for a drawn line"),
		)

	def __init__(self):
		self.x = 0
		self.y = 0
		self._text = 'Multi-Line\nString' 

		self.dx = 0
		self.dy = 0
		self.angle = 0
		self.boxAnchor = 'c'
		self.boxStrokeColor = None	#boxStroke
		self.boxStrokeWidth = 0.5 #boxStrokeWidth
		self.boxFillColor = None
		self.fillColor = STATE_DEFAULTS['fillColor']
		self.fontName = STATE_DEFAULTS['fontName']
		self.fontSize = STATE_DEFAULTS['fontSize']
		self.leading = None
		self.width = None
		self.height = None
		self.textAnchor = 'start'
		self.visible = 1
		self.lineStrokeWidth = 0
		self.lineStrokeColor = None

	def setText(self, text):
		"""Set the text property.  May contain embedded newline characters.
		Called by the containing chart or axis."""
		self._text = text


	def setOrigin(self, x, y):
		"""Set the origin.	This would be the tick mark or bar top relative to
		which it is defined.  Called by the containing chart or axis."""
		self.x = x
		self.y = y


	def demo(self):
		"""This shows a label positioned with its top right corner
		at the top centre of the drawing, and rotated 45 degrees."""

		d = Drawing(200, 100)

		# mark the origin of the label
		d.add(Circle(100,90, 5, fillColor=colors.green))

		lab = Label()
		lab.setOrigin(100,90)
		lab.boxAnchor = 'ne'
		lab.angle = 45
		lab.dx = 0
		lab.dy = -20
		lab.boxStrokeColor = colors.green
		lab.setText('Another\nMulti-Line\nString')
		d.add(lab)

		return d


	def computeSize(self):
		# the thing will draw in its own coordinate system
		self._lines = string.split(self._text, '\n')
		self._lineWidths = []
		if not self.width:
			w = 0
			for line in self._lines:
				thisWidth = stringWidth(line, self.fontName, self.fontSize)
				self._lineWidths.append(thisWidth)
				w = max(w,thisWidth)
			self._width = w
		else:
			self._width = self.width
		self._height = self.height or (self.leading or 1.2*self.fontSize) * len(self._lines)

		if self.boxAnchor in ['n','ne','nw']:
			self._top = 0
		elif self.boxAnchor in ['s','sw','se']:
			self._top = self._height
		else: 
			self._top = 0.5 * self._height
		self._bottom = self._top - self._height

		if self.boxAnchor in ['ne','e','se']:
			self._left = - self._width
		elif self.boxAnchor in ['nw','w','sw']:
			self._left = 0
		else:
			self._left = - self._width * 0.5
		self._right = self._left + self._width


	def draw(self):
		_text = self._text
		self._text = _text or ''
		self.computeSize()
		self._text = _text
		g = Group()
		g.translate(self.x + self.dx, self.y + self.dy)
		g.rotate(self.angle)

		y = self._top - self.fontSize
		if self.textAnchor == 'start':
			x = self._left
		elif self.textAnchor == 'middle':
			x = self._left + 0.5 * self._width
		else:
			x = self._left + self._width

		# paint box behind text just in case they
		# fill it
		if self.boxStrokeColor is not None:
			g.add(Rect(	self._left,
						self._bottom,
						self._width,
						self._height,
						strokeColor=self.boxStrokeColor,
						strokeWidth=self.boxStrokeWidth,
						fillColor=self.boxFillColor)
						)

		for line in self._lines:
			s = String(x, y, line)
			s.textAnchor = self.textAnchor
			s.fontName = self.fontName
			s.fontSize = self.fontSize
			s.fillColor = self.fillColor
			g.add(s)
			y = y - (self.leading or 1.2*self.fontSize)

		return g
