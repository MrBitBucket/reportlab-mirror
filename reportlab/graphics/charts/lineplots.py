#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/charts/lineplots.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/charts/lineplots.py,v 1.31 2002/05/24 15:47:19 rgbecker Exp $
"""This module defines a very preliminary Line Plot example.
"""
__version__=''' $Id: lineplots.py,v 1.31 2002/05/24 15:47:19 rgbecker Exp $ '''

import string, time
from types import FunctionType

from reportlab.lib import colors 
from reportlab.lib.validators import * 
from reportlab.lib.attrmap import *
from reportlab.graphics.shapes import Drawing, Group, Rect, Line, PolyLine
from reportlab.graphics.widgetbase import Widget, TypedPropertyCollection, PropHolder
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.charts.axes import XValueAxis, YValueAxis, AdjYValueAxis, NormalDateXValueAxis
from reportlab.graphics.charts.utils import *
from reportlab.graphics.widgets.markers import uSymbol2Symbol, isSymbol, makeMarker
from reportlab.graphics.widgets.grids import Grid, DoubleGrid, ShadedRect
from reportlab.pdfbase.pdfmetrics import stringWidth, getFont

# This might be moved again from here...
class LinePlotProperties(PropHolder):
	_attrMap = AttrMap(
		strokeWidth = AttrMapValue(isNumber,
			desc='Width of a line.'),
		strokeColor = AttrMapValue(isColorOrNone,
			desc='Color of a line.'),
		strokeDashArray = AttrMapValue(isListOfNumbersOrNone,
			desc='Dash array of a line.'),
		symbol = AttrMapValue(None,
			desc='Widget placed at data points.'),
		)


class LinePlot(Widget):
	"""Line plot with multiple lines.

	Both x- and y-axis are value axis (so there are no seperate
	X and Y versions of this class).
	"""

	_attrMap = AttrMap(
		debug = AttrMapValue(isNumber,
			desc='Used only for debugging.'),
		x = AttrMapValue(isNumber, desc='X position of the lower-left corner of the chart.'),
		y = AttrMapValue(isNumber, desc='Y position of the lower-left corner of the chart.'),
		reversePlotOrder = AttrMapValue(isBoolean, desc='If true reverse plot order.'),
		width = AttrMapValue(isNumber, desc='Width of the chart.'),
		height = AttrMapValue(isNumber, desc='Height of the chart.'),
		lineLabelNudge = AttrMapValue(isNumber,
			desc='Distance between a data point and its label.'),
		lineLabels = AttrMapValue(None,
			desc='Handle to the list of data point labels.'),
		lineLabelFormat = AttrMapValue(None,
			desc='Formatting string or function used for data point labels.'),
		joinedLines = AttrMapValue(isNumber,
			desc='Display data points joined with lines if true.'),
		strokeColor = AttrMapValue(isColorOrNone,
			desc='Color used for background border of plot area.'),
		fillColor = AttrMapValue(isColorOrNone,
			desc='Color used for background interior of plot area.'),
		lines = AttrMapValue(None,
			desc='Handle of the lines.'),
		xValueAxis = AttrMapValue(None,
			desc='Handle of the x axis.'),
		yValueAxis = AttrMapValue(None,
			desc='Handle of the y axis.'),
		data = AttrMapValue(None,
			desc='Data to be plotted, list of (lists of) x/y tuples.'),
		)

	def __init__(self):
		self.debug = 0

		self.x = 0
		self.y = 0
		self.reversePlotOrder = 0
		self.width = 200
		self.height = 100

		# allow for a bounding rectangle
		self.strokeColor = None
		self.fillColor = None

		self.xValueAxis = XValueAxis()
		self.yValueAxis = YValueAxis()

		# this defines two series of 3 points.	Just an example.
		self.data = [
			((1,1), (2,2), (2.5,1), (3,3), (4,5)),
			((1,2), (2,3), (2.5,2), (3,4), (4,6))
			]

		self.lines = TypedPropertyCollection(LinePlotProperties)
		self.lines.strokeWidth = 1
		self.lines[0].strokeColor = colors.red
		self.lines[1].strokeColor = colors.blue

		self.lineLabels = TypedPropertyCollection(Label)
		self.lineLabelFormat = None

		# this says whether the origin is inside or outside
		# the bar - +10 means put the origin ten points
		# above the tip of the bar if value > 0, or ten
		# points inside if bar value < 0.  This is different
		# to label dx/dy which are not dependent on the
		# sign of the data.
		self.lineLabelNudge = 10
		# if you have multiple series, by default they butt
		# together.

		# New line chart attributes.
		self.joinedLines = 1 # Connect items with straight lines.

	def demo(self):
		"""Shows basic use of a line chart."""

		drawing = Drawing(400, 200)

		data = [
			((1,1), (2,2), (2.5,1), (3,3), (4,5)),
			((1,2), (2,3), (2.5,2), (3.5,5), (4,6))
			]

		lp = LinePlot()

		lp.x = 50
		lp.y = 50
		lp.height = 125
		lp.width = 300
		lp.data = data
		lp.joinedLines = 1
		lp.lineLabelFormat = '%2.0f'
		lp.strokeColor = colors.black

		lp.lines[0].strokeColor = colors.red
		lp.lines[0].symbol = makeMarker('FilledCircle')
		lp.lines[1].strokeColor = colors.blue
		lp.lines[1].symbol = makeMarker('FilledDiamond')

		lp.xValueAxis.valueMin = 0
		lp.xValueAxis.valueMax = 5
		lp.xValueAxis.valueStep = 1

		lp.yValueAxis.valueMin = 0
		lp.yValueAxis.valueMax = 7
		lp.yValueAxis.valueStep = 1

		drawing.add(lp)

		return drawing


	def calcPositions(self):
		"""Works out where they go.

		Sets an attribute _positions which is a list of
		lists of (x, y) matching the data.
		"""

		self._seriesCount = len(self.data)
		self._rowLength = max(map(len,self.data))

		self._positions = []
		for rowNo in range(len(self.data)):
			line = []
			for colNo in range(len(self.data[rowNo])):
				datum = self.data[rowNo][colNo] # x,y value
				if type(datum[0]) == type(''):
					x = self.xValueAxis.scale(mktime(mkTimeTuple(datum[0])))
				else:
					x = self.xValueAxis.scale(datum[0])
				y = self.yValueAxis.scale(datum[1])
				line.append((x, y))
			self._positions.append(line)


	def makeBackground(self):
		g = Group()

		g.add(Rect(self.x, self.y,
				   self.width, self.height,
				   strokeColor = self.strokeColor,
				   fillColor= self.fillColor))

		return g


	def drawLabel(self, group, rowNo, colNo, x, y):
		"Draw a label for a given item in the list."

		labelFmt = self.lineLabelFormat
		labelValue = self.data[rowNo][colNo][1] ###

		if labelFmt is None:
			labelText = None
		elif type(labelFmt) is StringType:
			labelText = labelFmt % labelValue
		elif type(labelFmt) is FunctionType:
			labelText = labelFmt(labelValue)
		elif isinstance(labelFmt, Formatter):
			labelText = labelFmt(labelValue)
		else:
			msg = "Unknown formatter type %s, expected string or function"
			raise Exception, msg % labelFmt

		if labelText:
			label = self.lineLabels[(rowNo, colNo)]
			#hack to make sure labels are outside the bar
			if y > 0:
				label.setOrigin(x, y + self.lineLabelNudge)
			else:
				label.setOrigin(x, y - self.lineLabelNudge)
			label.setText(labelText)
			group.add(label)


	def makeLines(self):
		g = Group()

		labelFmt = self.lineLabelFormat

		P = range(len(self._positions))
		if self.reversePlotOrder: P.reverse()
		# Iterate over data rows.
		for rowNo in P:
			row = self._positions[rowNo]

			styleCount = len(self.lines)
			styleIdx = rowNo % styleCount
			rowColor = self.lines[styleIdx].strokeColor
			dash = getattr(self.lines[styleIdx], 'strokeDashArray', None)

			# width = getattr(self.lines[styleIdx], 'strokeWidth', None)
			if hasattr(self.lines[styleIdx], 'strokeWidth'):
				width = self.lines[styleIdx].strokeWidth
			elif hasattr(self.lines, 'strokeWidth'):
				width = self.lines.strokeWidth
			else:
				width = None

			# Iterate over data columns.
			if self.joinedLines:
				points = []
				for xy in row:
					points = points + [xy[0], xy[1]]
				line = PolyLine(points,strokeColor=rowColor,strokeLineCap=0,strokeLineJoin=1)
				if width:
					line.strokeWidth = width
				if dash:
					line.strokeDashArray = dash
				g.add(line)
			else:
				for colNo in range(len(row)):
					x1, y1 = row[colNo]
					if self.joinedLines == 1:
						if colNo > 0:
							# Draw lines between adjacent items.
							x2, y2 = row[colNo-1]
							line = Line(x1, y1, x2, y2,
										strokeColor=rowColor,
										strokeLineCap=1)
							if width:
								line.strokeWidth = width
							if dash:
								line.strokeDashArray = dash
							g.add(line)

			if hasattr(self.lines[styleIdx], 'symbol'):
				uSymbol = self.lines[styleIdx].symbol
			elif hasattr(self.lines, 'symbol'):
				uSymbol = self.lines.symbol
			else:
				uSymbol = None

			if uSymbol:
				for colNo in range(len(row)):
					x1, y1 = row[colNo]
					symbol = uSymbol2Symbol(uSymbol,x1,y1,rowColor)
					if symbol: g.add(symbol)

			# Draw item (bar) labels.
			for colNo in range(len(row)):
				x1, y1 = row[colNo]
				self.drawLabel(g, rowNo, colNo, x1, y1)

		return g


	def draw(self):
		self.yValueAxis.setPosition(self.x, self.y, self.height)
		self.yValueAxis.configure(self.data)

		# if zero is in chart, put x axis there, otherwise
		# use bottom.
		xAxisCrossesAt = self.yValueAxis.scale(0)
		if ((xAxisCrossesAt > self.y + self.height) or (xAxisCrossesAt < self.y)):
			y = self.y
		else:
			y = xAxisCrossesAt

		self.xValueAxis.setPosition(self.x, y, self.width)
		self.xValueAxis.configure(self.data)

		self.calcPositions()

		g = Group()

		g.add(self.makeBackground())
		g.add(self.xValueAxis)
		g.add(self.yValueAxis)
		g.add(self.makeLines())

		return g

_monthlyIndexData = [[(19971202, 100.0),
  (19971231, 100.1704367),
  (19980131, 101.5639577),
  (19980228, 102.1879927),
  (19980331, 101.6337257),
  (19980430, 102.7640446),
  (19980531, 102.9198038),
  (19980630, 103.25938789999999),
  (19980731, 103.2516421),
  (19980831, 105.4744329),
  (19980930, 109.3242705),
  (19981031, 111.9859291),
  (19981130, 110.9184642),
  (19981231, 110.9184642),
  (19990131, 111.9882532),
  (19990228, 109.7912614),
  (19990331, 110.24189629999999),
  (19990430, 110.4279321),
  (19990531, 109.33955469999999),
  (19990630, 108.2341748),
  (19990731, 110.21294469999999),
  (19990831, 110.9683062),
  (19990930, 112.4425371),
  (19991031, 112.7314032),
  (19991130, 112.3509645),
  (19991231, 112.3660659),
  (20000131, 110.9255248),
  (20000229, 110.5266306),
  (20000331, 113.3116101),
  (20000430, 111.0449133),
  (20000531, 111.702717),
  (20000630, 113.5832178)],
 [(19971202, 100.0),
  (19971231, 100.0),
  (19980131, 100.8),
  (19980228, 102.0),
  (19980331, 101.9),
  (19980430, 103.0),
  (19980531, 103.0),
  (19980630, 103.1),
  (19980731, 103.1),
  (19980831, 102.8),
  (19980930, 105.6),
  (19981031, 108.3),
  (19981130, 108.1),
  (19981231, 111.9),
  (19990131, 113.1),
  (19990228, 110.2),
  (19990331, 111.8),
  (19990430, 112.3),
  (19990531, 110.1),
  (19990630, 109.3),
  (19990731, 111.2),
  (19990831, 111.7),
  (19990930, 112.6),
  (19991031, 113.2),
  (19991130, 113.9),
  (19991231, 115.4),
  (20000131, 112.7),
  (20000229, 113.9),
  (20000331, 115.8),
  (20000430, 112.2),
  (20000531, 112.6),
  (20000630, 114.6)]]

class GridLinePlot(LinePlot):
	"""A customized version of LinePlot.
	It uses NormalDateXValueAxis() and AdjYValueAxis() for the X and Y axes.
	The chart has a default grid background with thin horizontal lines
	aligned with the tickmarks (and labels). You can change the back-
	ground to be any Grid or ShadedRect, or scale the whole chart.
	If you do provide a background, you can specify the colours of the
	stripes with 'background.stripeColors'.
	"""

	_attrMap = AttrMap(BASE=LinePlot,
		background = AttrMapValue(None, desc='Background for chart area (now Grid or ShadedRect).'),
		scaleFactor = AttrMapValue(isNumberOrNone, desc='Scalefactor to apply to whole drawing.'),
		)

	def __init__(self):
		from reportlab.lib import colors
		LinePlot.__init__(self)
		self.xValueAxis = NormalDateXValueAxis()
		self.yValueAxis = AdjYValueAxis()
		self.scaleFactor = None
		self.background = Grid()
		self.background.orientation = 'horizontal'
		self.background.useRects = 0
		self.background.useLines = 1
		self.background.strokeWidth = 0.5
		self.background.strokeColor = colors.black
		self.data = _monthlyIndexData

	def demo(self,drawing=None):
		from reportlab.lib import colors
		if not drawing:
			drawing = Drawing(400, 200)
		lp = AdjLinePlot()
		lp.x = 50
		lp.y = 50
		lp.height = 125
		lp.width = 300
		lp.data = _monthlyIndexData
		lp.joinedLines = 1
		lp.strokeColor = colors.black
		c0 = colors.PCMYKColor(100,65,0,30, spotName='PANTONE 288 CV', density=100)
		lp.lines[0].strokeColor = c0
		lp.lines[0].strokeWidth = 2
		lp.lines[0].strokeDashArray = None
		c1 = colors.PCMYKColor(0,79,91,0, spotName='PANTONE Wm Red CV', density=100)
		lp.lines[1].strokeColor = c1
		lp.lines[1].strokeWidth = 1
		lp.lines[1].strokeDashArray = [3,1]
		lp.xValueAxis.labels.fontSize = 10
		lp.xValueAxis.labels.textAnchor = 'start'
		lp.xValueAxis.labels.boxAnchor = 'w'
		lp.xValueAxis.labels.angle = -45
		lp.xValueAxis.labels.dx = 0
		lp.xValueAxis.labels.dy = -8
		lp.xValueAxis.xLabelFormat = '{mm}/{yy}'
		lp.yValueAxis.labelTextFormat = '%5d%% '
		lp.yValueAxis.tickLeft = 5
		lp.yValueAxis.labels.fontSize = 10
		lp.background = Grid()
		lp.background.stripeColors = [colors.pink, colors.lightblue]
		lp.background.orientation = 'vertical'
		drawing.add(lp,'plot')
		return drawing

	def makeBackground(self):
		"Make a background grid or fall back on chart's default."

		# If no background set, fall back to default behaviour.
		if not self.background:
			return LinePlot.makeBackground(self)

		g = Group()

		back = self.background
		back.x = self.x
		back.y = self.y
		back.width = self.width
		back.height = self.height

		g.add(self.background)

		return g

	def draw(self):
		xva, yva = self.xValueAxis, self.yValueAxis

		yva.setPosition(self.x, self.y, self.height)
		yva.configure(self.data)

		# if zero is in chart, put x axis there, otherwise
		# use bottom.
		xAxisCrossesAt = yva.scale(0)
		if ((xAxisCrossesAt > self.y + self.height) or (xAxisCrossesAt < self.y)):
			y = self.y
		else:
			y = xAxisCrossesAt

		xva.setPosition(self.x, y, self.width)
		xva.configure(self.data)

		back = self.background
		if isinstance(back, Grid):
			if back.orientation == 'vertical' and xva.valueSteps:
				xpos = map(xva.scale, [xva._valueMin] + xva.valueSteps)
				steps = []
				for i in range(len(xpos)-1):
					steps.append(xpos[i+1] - xpos[i])
				back.deltaSteps = steps
			elif back.orientation == 'horizontal' and yva.valueSteps:
				ypos = map(yva.scale, [yva._valueMin] + yva.valueSteps)
				steps = []
				for i in range(len(ypos)-1):
					steps.append(ypos[i+1] - ypos[i])
				back.deltaSteps = steps
		elif isinstance(back, DoubleGrid):
			# Ideally, these lines would not be needed...
			back.grid0.x = self.x
			back.grid0.y = self.y
			back.grid0.width = self.width
			back.grid0.height = self.height
			back.grid1.x = self.x
			back.grid1.y = self.y
			back.grid1.width = self.width
			back.grid1.height = self.height

			# some room left for optimization...
			if back.grid0.orientation == 'vertical' and xva.valueSteps:
				xpos = map(xva.scale, [xva._valueMin] + xva.valueSteps)
				steps = []
				for i in range(len(xpos)-1):
					steps.append(xpos[i+1] - xpos[i])
				back.grid0.deltaSteps = steps
			elif back.grid0.orientation == 'horizontal' and yva.valueSteps:
				ypos = map(yva.scale, [yva._valueMin] + yva.valueSteps)
				steps = []
				for i in range(len(ypos)-1):
					steps.append(ypos[i+1] - ypos[i])
				back.grid0.deltaSteps = steps
			if back.grid1.orientation == 'vertical' and xva.valueSteps:
				xpos = map(xva.scale, [xva._valueMin] + xva.valueSteps)
				steps = []
				for i in range(len(xpos)-1):
					steps.append(xpos[i+1] - xpos[i])
				back.grid1.deltaSteps = steps
			elif back.grid1.orientation == 'horizontal' and yva.valueSteps:
				ypos = map(yva.scale, [yva._valueMin] + yva.valueSteps)
				steps = []
				for i in range(len(ypos)-1):
					steps.append(ypos[i+1] - ypos[i])
				back.grid1.deltaSteps = steps

		self.calcPositions()

		width, height, scaleFactor = self.width, self.height, self.scaleFactor
		if scaleFactor and scaleFactor!=1:
			#g = Drawing(scaleFactor*width, scaleFactor*height)
			g.transform = (scaleFactor, 0, 0, scaleFactor,0,0)
		else:
			g = Group()

		g.add(self.makeBackground())
		g.add(self.xValueAxis)
		g.add(self.yValueAxis)
		g.add(self.makeLines())

		return g

def _maxWidth(T, fontName, fontSize):
	'''return max stringWidth for the list of strings T'''
	if type(T) not in (type(()),type([])): T = (T,)
	T = filter(None,T)
	return T and max(map(lambda t,sW=stringWidth,fN=fontName, fS=fontSize: sW(t,fN,fS),T)) or 0

class ScatterPlot(LinePlot):
	"""A scatter plot widget"""

	_attrMap = AttrMap(BASE=LinePlot,
					width = AttrMapValue(isNumber, desc="Width of the area inside the axes"),
					height = AttrMapValue(isNumber, desc="Height of the area inside the axes"),
					outerBorderOn = AttrMapValue(isBoolean, desc="Is there an outer border (continuation of axes)"),
					outerBorderColor = AttrMapValue(isColorOrNone, desc="Color of outer border (if any)"),
					background = AttrMapValue(isColorOrNone, desc="Background color (if any)"),
					labelOffset = AttrMapValue(isNumber, desc="Space between label and Axis (or other labels)"),
					axisTickLengths = AttrMapValue(isNumber, desc="Lenth of the ticks on both axes"),
					axisStrokeWidth = AttrMapValue(isNumber, desc="Stroke width for both axes"),
					xLabel = AttrMapValue(isString, desc="Label for the whole X-Axis"),
					yLabel = AttrMapValue(isString, desc="Label for the whole Y-Axis"),
					data = AttrMapValue(isAnything, desc='Data points - a list of x/y tuples.'),
					strokeColor = AttrMapValue(isColorOrNone, desc='Color used for border of plot area.'),
					fillColor = AttrMapValue(isColorOrNone, desc='Color used for background interior of plot area.'),
					leftPadding = AttrMapValue(isNumber, desc='Padding on left of drawing'),
					rightPadding = AttrMapValue(isNumber, desc='Padding on right of drawing'),
					topPadding = AttrMapValue(isNumber, desc='Padding at top of drawing'),
					bottomPadding = AttrMapValue(isNumber, desc='Padding at bottom of drawing'),
					)

	def __init__(self):
		LinePlot.__init__(self)
		self.width = 142
		self.height = 77
		self.outerBorderOn = 1
		self.outerBorderColor = colors.black
		self.background = None

		_labelOffset = 3
		_axisTickLengths = 2
		_axisStrokeWidth = 0.5

		self.yValueAxis.valueMin = None
		self.yValueAxis.valueMax = None
		self.yValueAxis.valueStep = None
		self.yValueAxis.labelTextFormat  = '%s'

		self.xLabel="X Lable"
		self.xValueAxis.labels.fontSize = 6

		self.yLabel="Y Lable"
		self.yValueAxis.labels.fontSize = 6

		self.data =[((0.030, 62.73),
					 (0.074, 54.363),
					 (1.216, 17.964)),

					 ((1.360, 11.621),
					 (1.387, 50.011),
					 (1.428, 68.953)),

					 ((1.444, 86.888),
					 (1.754, 35.58),
					 (1.766, 36.05))]

		#values for lineplot
		self.joinedLines = 0
		self.fillColor = self.background

		self.leftPadding=5
		self.rightPadding=10
		self.topPadding=5
		self.bottomPadding=5

		self.x = self.leftPadding+_axisTickLengths+(_labelOffset*2)
		self.x=self.x+_maxWidth(str(self.yValueAxis.valueMax), self.yValueAxis.labels.fontName, self.yValueAxis.labels.fontSize)
		self.y = self.bottomPadding+_axisTickLengths+_labelOffset+self.xValueAxis.labels.fontSize

		self.xValueAxis.labels.dy = -_labelOffset 
		self.xValueAxis.tickDown = _axisTickLengths
		self.xValueAxis.strokeWidth = _axisStrokeWidth
		self.xValueAxis.rangeRound='both'
		self.yValueAxis.labels.dx = -_labelOffset 
		self.yValueAxis.tickLeft = _axisTickLengths
		self.yValueAxis.strokeWidth = _axisStrokeWidth
		self.yValueAxis.rangeRound='both'

		self.lineLabelFormat="%.2f"
		self.lineLabels.fontSize = 5
		self.lineLabels.boxAnchor = 'e'
		self.lineLabels.dx             = -2
		self.lineLabelNudge = 0
		self.lines.symbol=makeMarker('FilledCircle',size=3)
		self.lines[1].symbol=makeMarker('FilledDiamond',size=3)
		self.lines[2].symbol=makeMarker('FilledSquare',size=3)
		self.lines[2].strokeColor = colors.green

	def _getDrawingDimensions(self):
		tx = self.leftPadding+self.yValueAxis.tickLeft+(self.yValueAxis.labels.dx*2)+self.xValueAxis.labels.fontSize
		tx=tx+(5*_maxWidth(str(self.yValueAxis.valueMax), self.yValueAxis.labels.fontName, self.yValueAxis.labels.fontSize))
		tx=tx+self.width+self.rightPadding
		t=('%.2f%%'%self.xValueAxis.valueMax)
		tx=tx+(_maxWidth(t, self.yValueAxis.labels.fontName, self.yValueAxis.labels.fontSize))
		ty = self.bottomPadding+self.xValueAxis.tickDown+(self.xValueAxis.labels.dy*2)+(self.xValueAxis.labels.fontSize*2)
		ty=ty+self.yValueAxis.labels.fontSize+self.height+self.topPadding
		#print (tx, ty)
		return (tx,ty)

	def demo(self,drawing=None):
		if not drawing:
			tx,ty=self._getDrawingDimensions()
			drawing = Drawing(tx,ty)
		drawing.add(self.draw())
		return drawing

	def draw(self):
		ascent=getFont(self.xValueAxis.labels.fontName).face.ascent
		if ascent==0:
			ascent=0.718 # default (from helvetica)
		ascent=ascent*self.xValueAxis.labels.fontSize # normalize

		#basic LinePlot - does the Axes, Ticks etc
		lp = LinePlot.draw(self)

		xLabel = self.xLabel
		if xLabel: #Overall label for the X-axis
			xl=Label()
			xl.x = (self.x+self.width)/2.0
			xl.y = 0
			xl.fontName = self.xValueAxis.labels.fontName
			xl.fontSize = self.xValueAxis.labels.fontSize
			xl.setText(xLabel)
			lp.add(xl)

		yLabel = self.yLabel
		if yLabel: #Overall label for the Y-axis
			yl=Label()
			yl.angle = 90
			yl.x = 0
			yl.y = (self.y+self.height/2.0)
			yl.fontName = self.yValueAxis.labels.fontName
			yl.fontSize = self.yValueAxis.labels.fontSize
			yl.setText(yLabel)
			lp.add(yl)

		# do a bounding box - in the same style as the axes
		if self.outerBorderOn:
			lp.add(Rect(self.x, self.y, self.width, self.height,
					   strokeColor = self.outerBorderColor,
					   strokeWidth = self.yValueAxis.strokeWidth,
					   fillColor = None))

		lp.shift(self.leftPadding, self.bottomPadding)

		return lp

def sample1a():
	"A line plot with non-equidistant points in x-axis."

	drawing = Drawing(400, 200)

	data = [
			((1,1), (2,2), (2.5,1), (3,3), (4,5)),
			((1,2), (2,3), (2.5,2), (3.5,5), (4,6))
		]

	lp = LinePlot()

	lp.x = 50
	lp.y = 50
	lp.height = 125
	lp.width = 300
	lp.data = data
	lp.joinedLines = 1
	lp.strokeColor = colors.black

	lp.lines.symbol = makeMarker('UK_Flag')

	lp.lines[0].strokeWidth = 2
	lp.lines[1].strokeWidth = 4

	lp.xValueAxis.valueMin = 0
	lp.xValueAxis.valueMax = 5
	lp.xValueAxis.valueStep = 1

	lp.yValueAxis.valueMin = 0
	lp.yValueAxis.valueMax = 7
	lp.yValueAxis.valueStep = 1

	drawing.add(lp)

	return drawing


def sample1b():
	"A line plot with non-equidistant points in x-axis."

	drawing = Drawing(400, 200)

	data = [
			((1,1), (2,2), (2.5,1), (3,3), (4,5)),
			((1,2), (2,3), (2.5,2), (3.5,5), (4,6))
		]

	lp = LinePlot()

	lp.x = 50
	lp.y = 50
	lp.height = 125
	lp.width = 300
	lp.data = data
	lp.joinedLines = 1
	lp.lines.symbol = makeMarker('Circle')
	lp.lineLabelFormat = '%2.0f'
	lp.strokeColor = colors.black

	lp.xValueAxis.valueMin = 0
	lp.xValueAxis.valueMax = 5
	lp.xValueAxis.valueSteps = [1, 2, 2.5, 3, 4, 5]
	lp.xValueAxis.labelTextFormat = '%2.1f'

	lp.yValueAxis.valueMin = 0
	lp.yValueAxis.valueMax = 7
	lp.yValueAxis.valueStep = 1

	drawing.add(lp)

	return drawing


def sample1c():
	"A line plot with non-equidistant points in x-axis."

	drawing = Drawing(400, 200)

	data = [
			((1,1), (2,2), (2.5,1), (3,3), (4,5)),
			((1,2), (2,3), (2.5,2), (3.5,5), (4,6))
		]

	lp = LinePlot()

	lp.x = 50
	lp.y = 50
	lp.height = 125
	lp.width = 300
	lp.data = data
	lp.joinedLines = 1
	lp.lines[0].symbol = makeMarker('FilledCircle')
	lp.lines[1].symbol = makeMarker('Circle')
	lp.lineLabelFormat = '%2.0f'
	lp.strokeColor = colors.black

	lp.xValueAxis.valueMin = 0
	lp.xValueAxis.valueMax = 5
	lp.xValueAxis.valueSteps = [1, 2, 2.5, 3, 4, 5]
	lp.xValueAxis.labelTextFormat = '%2.1f'

	lp.yValueAxis.valueMin = 0
	lp.yValueAxis.valueMax = 7
	lp.yValueAxis.valueSteps = [1, 2, 3, 5, 6]

	drawing.add(lp)

	return drawing


def preprocessData(series):
	"Convert date strings into seconds and multiply values by 100."

	return map(lambda x: (str2seconds(x[0]), x[1]*100), series)


def sample2():
	"A line plot with non-equidistant points in x-axis."

	drawing = Drawing(400, 200)

	data = [
		(('25/11/1991',1),
		 ('30/11/1991',1.000933333),
		 ('31/12/1991',1.0062),
		 ('31/01/1992',1.0112),
		 ('29/02/1992',1.0158),
		 ('31/03/1992',1.020733333),
		 ('30/04/1992',1.026133333),
		 ('31/05/1992',1.030266667),
		 ('30/06/1992',1.034466667),
		 ('31/07/1992',1.038733333),
		 ('31/08/1992',1.0422),
		 ('30/09/1992',1.045533333),
		 ('31/10/1992',1.049866667),
		 ('30/11/1992',1.054733333),
		 ('31/12/1992',1.061),
		 ),
		]

	data[0] = preprocessData(data[0])

	lp = LinePlot()

	lp.x = 50
	lp.y = 50
	lp.height = 125
	lp.width = 300
	lp.data = data
	lp.joinedLines = 1
	lp.lines.symbol = makeMarker('FilledDiamond')
	lp.strokeColor = colors.black

	start = mktime(mkTimeTuple('25/11/1991'))
	t0 = mktime(mkTimeTuple('30/11/1991'))
	t1 = mktime(mkTimeTuple('31/12/1991'))
	t2 = mktime(mkTimeTuple('31/03/1992'))
	t3 = mktime(mkTimeTuple('30/06/1992'))
	t4 = mktime(mkTimeTuple('30/09/1992'))
	end = mktime(mkTimeTuple('31/12/1992'))
	lp.xValueAxis.valueMin = start
	lp.xValueAxis.valueMax = end
	lp.xValueAxis.valueSteps = [start, t0, t1, t2, t3, t4, end]
	lp.xValueAxis.labelTextFormat = seconds2str
	lp.xValueAxis.labels[1].dy = -20
	lp.xValueAxis.labels[2].dy = -35

	lp.yValueAxis.labelTextFormat = '%4.2f'
	lp.yValueAxis.valueMin = 100
	lp.yValueAxis.valueMax = 110
	lp.yValueAxis.valueStep = 2

	drawing.add(lp)

	return drawing
