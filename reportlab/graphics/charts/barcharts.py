#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/charts/barcharts.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/charts/barcharts.py,v 1.38 2001/09/14 08:29:30 rgbecker Exp $
"""This module defines a variety of Bar Chart components.

The basic flavors are Side-by-side, available in horizontal and
vertical versions.

Stacked and percentile bar charts to follow...
"""

import string, copy
from types import FunctionType, StringType

from reportlab.lib import colors
from reportlab.lib.validators import isNumber, isColor, isColorOrNone, isListOfStrings, SequenceOf
from reportlab.lib.attrmap import *
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.graphics.widgetbase import Widget, TypedPropertyCollection, PropHolder
from reportlab.graphics.shapes import Line, Rect, Group, Drawing
from reportlab.graphics.charts.axes import XCategoryAxis, YValueAxis
from reportlab.graphics.charts.axes import YCategoryAxis, XValueAxis
from reportlab.graphics.charts.textlabels import BarChartLabel
from reportlab.graphics.widgets.grids import ShadedRect


### Helpers (maybe put this into Drawing... or shapes)
##
##def grid(group, x, y, width, height, dist=100):
##	  "Make a rectangular grid given a distance between two adjacent lines."
##
##	  g = group
##
##	  # Vertical lines
##	  for x0 in range(x, x+width, dist):
##		  lineWidth = 0
##		  if x0 % 5 == 0:
##			  lineWidth = 1
##		  g.add(Line(x0, 0, x0, y+height, strokeWidth=lineWidth))
##
##	  # Horizontal lines
##	  for y0 in range(y, y+height, dist):
##		  lineWidth = 0
##		  if y0 % 5 == 0:
##			  lineWidth = 1
##		  g.add(Line(0, y0, x+width, y0, strokeWidth=lineWidth))


class BarChartProperties(PropHolder):
	_attrMap = AttrMap(
		strokeColor = AttrMapValue(isColorOrNone,
			desc='Color of the bar border.'),
		fillColor = AttrMapValue(isColorOrNone,
			desc='Color of the bar interior area.'),
		strokeWidth = AttrMapValue(isNumber,
			desc='Width of the bar border.'),
		symbol = AttrMapValue(None,
			desc='A widget to be used instead of a normal bar.'),
		)

	def __init__(self):
		self.strokeColor = None
		self.fillColor = colors.blue
		self.strokeWidth = 0.5
		self.symbol = None

# Bar chart classes.

class BarChart(Widget):
	"Abstract base class, unusable by itself."

	_attrMap = AttrMap(
		debug = AttrMapValue(isNumber,
			desc='Used only for debugging.'),
		x = AttrMapValue(isNumber,
			desc='X position of the lower-left corner of the chart.'),
		y = AttrMapValue(isNumber,
			desc='Y position of the lower-left corner of the chart.'),
		width = AttrMapValue(isNumber,
			desc='Width of the chart.'),
		height = AttrMapValue(isNumber,
			desc='Height of the chart.'),

		useAbsolute = AttrMapValue(isNumber,
			desc='Flag to use absolute spacing values.'),
		barWidth = AttrMapValue(isNumber,
			desc='The width of an individual bar.'),
		groupSpacing = AttrMapValue(isNumber,
			desc='Width between groups of bars.'),
		barSpacing = AttrMapValue(isNumber,
			desc='Width between individual bars.'),

		strokeColor = AttrMapValue(isColorOrNone,
			desc='Color of the plot area border.'),
		strokeWidth = AttrMapValue(isNumber,
			desc='Width plot area border.'),
		fillColor = AttrMapValue(isColorOrNone,
			desc='Color of the plot area interior.'),

		bars = AttrMapValue(None,
			desc='Handle of the individual bars.'),

		valueAxis = AttrMapValue(None,
			desc='Handle of the value axis.'),
		categoryAxis = AttrMapValue(None,
			desc='Handle of the category axis.'),
		categoryNames = AttrMapValue(isListOfStrings,
			desc='List of category names.'),
		data = AttrMapValue(None,
			desc='Data to be plotted, list of (lists of) numbers.'),
		barLabels = AttrMapValue(None,
			desc='Handle to the list of bar labels.'),
		barLabelFormat = AttrMapValue(None,
			desc='Formatting string or function used for bar labels.'),
		)

	def __init__(self):
		self.debug = 0

		self.barSpacing = 0

		self.x = 0
		self.y = 0
		self.x = 20
		self.y = 10
		self.height = 85
		self.width = 180

		# allow for a bounding rectangle
		self.strokeColor = None
		self.fillColor = None

		# this defines two series of 3 points.	Just an example.
		self.data = [(100,110,120,130),
					 (70, 80, 85, 90)]
		self.categoryNames = ('North','South','East','West')

		# control bar spacing. is useAbsolute = 1 then
		# the next parameters are in points; otherwise
		# they are 'proportions' and are normalized to
		# fit the available space.	Half a barSpacing
		# is allocated at the beginning and end of the
		# chart.
		self.useAbsolute = 0   #- not done yet
		self.barWidth = 10
		self.groupSpacing = 5
		self.barSpacing = 0

		self.barLabels = TypedPropertyCollection(BarChartLabel)
		self.barLabels.boxAnchor = 'c'
		self.barLabels.textAnchor = 'middle'
		self.barLabelFormat = None

		# this says whether the origin is inside or outside
		# the bar - +10 means put the origin ten points
		# above the tip of the bar if value > 0, or ten
		# points inside if bar value < 0.  This is different
		# to label dx/dy which are not dependent on the
		# sign of the data.
		self.barLabels.nudge = 0

		# if you have multiple series, by default they butt
		# together.

		# we really need some well-designed default lists of
		# colors e.g. from Tufte.  These will be used in a
		# cycle to set the fill color of each series.
		self.bars = TypedPropertyCollection(BarChartProperties)
##		  self.bars.symbol = None
		self.bars.strokeWidth = 1
		self.bars.strokeColor = colors.black

		self.bars[0].fillColor = colors.red
		self.bars[1].fillColor = colors.green
		self.bars[2].fillColor = colors.blue


	def _findMinMaxValues(self):
		"Find the minimum and maximum value of the data we have."
		D = map(lambda x: map(lambda x: x is not None and x or 0,x),self.data)
		return min(map(min,D)), max(map(max,D))

	def makeBackground(self):
		g = Group()
		#print 'BarChart.makeBackground(%s, %s, %s, %s)' % (self.x, self.y, self.width, self.height)
		g.add(Rect(self.x, self.y, self.width, self.height,
			strokeColor = self.strokeColor, fillColor= self.fillColor))
		return g


	def demo(self):
		"""Shows basic use of a bar chart"""
		drawing = Drawing(200, 100)
		bc = self.__class__()
		drawing.add(bc)
		return drawing


	def _drawBegin(self,org,length):
		'''Position and configure value axis, return crossing value'''

		self.valueAxis.setPosition(self.x, self.y, length)
		self.valueAxis.configure(self.data)

		# if zero is in chart, put x axis there, otherwise
		# use bottom.
		crossesAt = self.valueAxis.scale(0)
		if crossesAt > org+length or crossesAt<org:
			crossesAt = org

		return crossesAt


	def _drawFinish(self):
		'''finalize the drawing of a barchart'''

		self.categoryAxis.configure(self.data)
		self.calcBarPositions()

		g = Group()

		g.add(self.makeBackground())
		g.add(self.categoryAxis)
		g.add(self.valueAxis)
		g.add(self.makeBars())

		return g


	def calcBarPositions(self):
		"""Works out where they go. default vertical.

		Sets an attribute _barPositions which is a list of
		lists of (x, y, width, height) matching the data.
		"""

		flipXY = self._flipXY
		if flipXY:
			org = self.y
		else:
			org = self.x

		self._seriesCount = len(self.data)
		self._rowLength = len(self.data[0])

		if self.useAbsolute:
			# bar dimensions are absolute
			normFactor = 1.0
		else:
			# bar dimensions are normalized to fit.  How wide
			# notionally is one group of bars?
			normWidth = (self.groupSpacing
						+ (self._seriesCount * self.barWidth)
						+ ((self._seriesCount - 1) * self.barSpacing)
						)
			availWidth = self.categoryAxis.scale(0)[1]
			normFactor = availWidth / normWidth
			if self.debug:
				print '%d series, %d points per series' % (self._seriesCount, self._rowLength)
				print 'width = %d group + (%d bars * %d barWidth) + (%d gaps * %d interBar) = %d total' % (
					self.groupSpacing, self._seriesCount, self.barWidth,
					self._seriesCount - 1, self.barSpacing, normWidth)

		# 'Baseline' correction...
		scale = self.valueAxis.scale
		vm, vM = self.valueAxis.valueMin, self.valueAxis.valueMax
		if None in (vm, vM):
			y = scale(self._findMinMaxValues()[0])
		elif vm <= 0 <= vM:
			y = scale(0)
		elif 0 < vm:
			y = scale(vm)
		elif vM < 0:
			y = scale(vM)
		#print vm, vM, y, scale, self.valueAxis._y, self.valueAxis._valueMin, self._findMinMaxValues()[0]

		self._barPositions = []
		for rowNo in range(len(self.data)):
			barRow = []
			for colNo in range(len(self.data[0])):
				datum = self.data[rowNo][colNo]

				# Ufff...
				if self.useAbsolute:
					g = len(self.data) * self.barWidth + \
							 len(self.data) * self.barSpacing + \
							 self.groupSpacing
					g = g * colNo + 0.5 * self.groupSpacing + org
					x = g + rowNo * (self.barWidth + self.barSpacing)
				else:
					(g, gW) = self.categoryAxis.scale(colNo)
					x = g + normFactor * (0.5 * self.groupSpacing \
											   + rowNo * (self.barWidth + self.barSpacing))
				width = self.barWidth * normFactor

				height = self.valueAxis.scale(datum) - y
				barRow.append(flipXY and (y,x,height,width) or (x, y, width, height))

			self._barPositions.append(barRow)


	def _getLabelText(self, rowNo, colNo):
		'''return formatted label text'''
		labelFmt = self.barLabelFormat
		if labelFmt is None:
			labelText = None
		elif type(labelFmt) is StringType:
			labelText = labelFmt % self.data[rowNo][colNo]
		elif type(labelFmt) is FunctionType:
			labelText = labelFmt(self.data[rowNo][colNo])
		else:
			msg = "Unknown formatter type %s, expected string or function" % labelFmt
			raise Exception, msg
		return labelText

	def _labelXY(self,label,x,y,width,height):
		'Compute x, y for a label'
		if self._flipXY:
			return x + width + (width>=0 and 1 or -1) * label.nudge, y + 0.5*height
		else:
			return x + 0.5*width, y + height + (height>=0 and 1 or -1) * label.nudge

	def _addLabel(self, g, rowNo, colNo, x, y, width, height):
		labelText = self._getLabelText(rowNo,colNo)
		# We currently overwrite the boxAnchor with 'c' and display
		# it at a constant offset to the bar's top/bottom determined
		# by the barLabels.nudge attribute.
		if labelText:
			label = self.barLabels[(rowNo, colNo)]
			if label.visible:
				labelWidth = stringWidth(labelText, label.fontName, label.fontSize)
				x0, y0 = self._labelXY(label,x,y,width,height)
				fixedEnd = getattr(label,'fixedEnd', None)
				if fixedEnd is not None:
					x00, y00 = x0, y0
					if self._flipXY:
						x0 = x+fixedEnd
					else:
						y0 = y+fixedEnd
				else:
					if self._flipXY:
						x00 = x0
						y00 = y+height/2.0
					else:
						x00 = x+width/2.0
						y00 = y0
				fixedStart = getattr(label,'fixedStart', None)
				if fixedStart is not None:
					if self._flipXY:
						x00 = x+fixedStart
					else:
						y00 = y+fixedStart

				label.setOrigin(x0, y0)
				label.setText(labelText)
				sC, sW = label.lineStrokeColor, label.lineStrokeWidth
				if sC and sW: g.insert(0,Line(x00,y00,x0,y0, strokeColor=sC, strokeWidth=sW))
				g.add(label)
				alx = getattr(self,'barLabelCallout',None)
				if alx: alx(g,rowNo,colNo,x,y,width,height,x00,y00,x0,y0)

	def makeBars(self):
		g = Group()

		for rowNo in range(len(self._barPositions)):
			row = self._barPositions[rowNo]
			styleCount = len(self.bars)
			styleIdx = rowNo % styleCount
			rowStyle = self.bars[styleIdx]
			for colNo in range(len(row)):
				barPos = row[colNo]
				(x, y, width, height) = barPos

				# Draw a rectangular symbol for each data item,
				# or a normal colored rectangle.
				symbol = None
				if hasattr(self.bars[styleIdx], 'symbol'):
					symbol = copy.deepcopy(self.bars[styleIdx].symbol)
				elif hasattr(self.bars, 'symbol'):
					symbol = self.bars.symbol

				if symbol:
					symbol.x = x
					symbol.y = y
					symbol.width = width
					symbol.height = height
					g.add(symbol)
				else:
					r = Rect(x, y, width, height)
					r.strokeWidth = rowStyle.strokeWidth ## added line - now actually uses strokeWidth
					r.fillColor = rowStyle.fillColor
					r.strokeColor = rowStyle.strokeColor
					g.add(r)

				self._addLabel(g,rowNo,colNo,x,y,width,height)

		return g


class VerticalBarChart(BarChart):
	"Vertical bar chart with multiple side-by-side bars."

	_flipXY = 0

	def __init__(self):
		BarChart.__init__(self)
		self.categoryAxis = XCategoryAxis()
		self.valueAxis = YValueAxis()

	def draw(self):
		self.categoryAxis.setPosition(self.x, self._drawBegin(self.y,self.height), self.width)
		return self._drawFinish()


class HorizontalBarChart(BarChart):
	"Horizontal bar chart with multiple side-by-side bars."

	_flipXY = 1

	def __init__(self):
		BarChart.__init__(self)
		self.categoryAxis = YCategoryAxis()
		self.valueAxis = XValueAxis()

	def draw(self):
		self.categoryAxis.setPosition(self._drawBegin(self.x,self.width), self.y, self.height)
		return self._drawFinish()


# Vertical samples.

def sampleV0a():
	"A slightly pathologic bar chart with only TWO data items."

	drawing = Drawing(400, 200)

	data = [(13, 20)]

	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data

	bc.strokeColor = colors.black

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'ne'
	bc.categoryAxis.labels.dx = 8
	bc.categoryAxis.labels.dy = -2
	bc.categoryAxis.labels.angle = 30
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


def sampleV0b():
	"A pathologic bar chart with only ONE data item."

	drawing = Drawing(400, 200)

	data = [(42,)]

	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 50
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'ne'
	bc.categoryAxis.labels.dx = 8
	bc.categoryAxis.labels.dy = -2
	bc.categoryAxis.labels.angle = 30
	bc.categoryAxis.categoryNames = ['Jan-99']

	drawing.add(bc)

	return drawing


def sampleV0c():
	"A really pathologic bar chart with NO data items at all!"

	drawing = Drawing(400, 200)

	data = [()]

	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'ne'
	bc.categoryAxis.labels.dx = 8
	bc.categoryAxis.labels.dy = -2
	bc.categoryAxis.categoryNames = []

	drawing.add(bc)

	return drawing


def sampleV1():
	"Sample of multi-series bar chart."

	drawing = Drawing(400, 200)

	data = [
			(13, 5, 20, 22, 37, 45, 19, 4),
			(14, 6, 21, 23, 38, 46, 20, 5)
			]

	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'ne'
	bc.categoryAxis.labels.dx = 8
	bc.categoryAxis.labels.dy = -2
	bc.categoryAxis.labels.angle = 30

	catNames = string.split('Jan Feb Mar Apr May Jun Jul Aug', ' ')
	catNames = map(lambda n:n+'-99', catNames)
	bc.categoryAxis.categoryNames = catNames
	drawing.add(bc)

	return drawing


def sampleV2a():
	"Sample of multi-series bar chart."

	data = [(2.4, -5.7, 2, 5, 9.2),
			(0.6, -4.9, -3, 4, 6.8)
			]

	labels = ("Q3 2000", "Year to Date", "12 months",
			  "Annualised\n3 years", "Since 07.10.99")

	drawing = Drawing(400, 200)

	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 120
	bc.width = 300
	bc.data = data

	bc.barSpacing = 0
	bc.groupSpacing = 10
	bc.barWidth = 10

	bc.valueAxis.valueMin = -15
	bc.valueAxis.valueMax = +15
	bc.valueAxis.valueStep = 5
	bc.valueAxis.labels.fontName = 'Helvetica'
	bc.valueAxis.labels.fontSize = 8
	bc.valueAxis.labels.boxAnchor = 'n'   # irrelevant (becomes 'c')
	bc.valueAxis.labels.textAnchor = 'middle'

	bc.categoryAxis.categoryNames = labels
	bc.categoryAxis.labels.fontName = 'Helvetica'
	bc.categoryAxis.labels.fontSize = 8
	bc.categoryAxis.labels.dy = -60

	drawing.add(bc)

	return drawing


def sampleV2b():
	"Sample of multi-series bar chart."

	data = [(2.4, -5.7, 2, 5, 9.2),
			(0.6, -4.9, -3, 4, 6.8)
			]

	labels = ("Q3 2000", "Year to Date", "12 months",
			  "Annualised\n3 years", "Since 07.10.99")

	drawing = Drawing(400, 200)

	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 120
	bc.width = 300
	bc.data = data

	bc.barSpacing = 5
	bc.groupSpacing = 10
	bc.barWidth = 10

	bc.valueAxis.valueMin = -15
	bc.valueAxis.valueMax = +15
	bc.valueAxis.valueStep = 5
	bc.valueAxis.labels.fontName = 'Helvetica'
	bc.valueAxis.labels.fontSize = 8
	bc.valueAxis.labels.boxAnchor = 'n'   # irrelevant (becomes 'c')
	bc.valueAxis.labels.textAnchor = 'middle'

	bc.categoryAxis.categoryNames = labels
	bc.categoryAxis.labels.fontName = 'Helvetica'
	bc.categoryAxis.labels.fontSize = 8
	bc.categoryAxis.labels.dy = -60

	drawing.add(bc)

	return drawing


def sampleV2c():
	"Sample of multi-series bar chart."

	data = [(2.4, -5.7, 2, 5, 9.99),
			(0.6, -4.9, -3, 4, 9.99)
			]

	labels = ("Q3 2000", "Year to Date", "12 months",
			  "Annualised\n3 years", "Since 07.10.99")

	drawing = Drawing(400, 200)

	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 120
	bc.width = 300
	bc.data = data

	bc.barSpacing = 2
	bc.groupSpacing = 10
	bc.barWidth = 10

	bc.valueAxis.valueMin = -15
	bc.valueAxis.valueMax = +15
	bc.valueAxis.valueStep = 5
	bc.valueAxis.labels.fontName = 'Helvetica'
	bc.valueAxis.labels.fontSize = 8

	bc.categoryAxis.categoryNames = labels
	bc.categoryAxis.labels.fontName = 'Helvetica'
	bc.categoryAxis.labels.fontSize = 8
	bc.valueAxis.labels.boxAnchor = 'n'
	bc.valueAxis.labels.textAnchor = 'middle'
	bc.categoryAxis.labels.dy = -60

	bc.barLabels.nudge = 10

	bc.barLabelFormat = '%0.2f'
	bc.barLabels.dx = 0
	bc.barLabels.dy = 0
	bc.barLabels.boxAnchor = 'n'  # irrelevant (becomes 'c')
	bc.barLabels.fontName = 'Helvetica'
	bc.barLabels.fontSize = 6

	drawing.add(bc)

	return drawing


def sampleV3():
	"Faked horizontal bar chart using a vertical real one (deprecated)."

	names = ("UK Equities", "US Equities", "European Equities", "Japanese Equities",
			  "Pacific (ex Japan) Equities", "Emerging Markets Equities",
			  "UK Bonds", "Overseas Bonds", "UK Index-Linked", "Cash")

	series1 = (-1.5, 0.3, 0.5, 1.0, 0.8, 0.7, 0.4, 0.1, 1.0, 0.3)
	series2 = (0.0, 0.33, 0.55, 1.1, 0.88, 0.77, 0.44, 0.11, 1.10, 0.33)

	assert len(names) == len(series1), "bad data"
	assert len(names) == len(series2), "bad data"

	drawing = Drawing(400, 200)

	bc = VerticalBarChart()
	bc.x = 0
	bc.y = 0
	bc.height = 100
	bc.width = 150
	bc.data = (series1,)
	bc.bars.fillColor = colors.green

	bc.barLabelFormat = '%0.2f'
	bc.barLabels.dx = 0
	bc.barLabels.dy = 0
	bc.barLabels.boxAnchor = 'w' # irrelevant (becomes 'c')
	bc.barLabels.angle = 90
	bc.barLabels.fontName = 'Helvetica'
	bc.barLabels.fontSize = 6
	bc.barLabels.nudge = 10

	bc.valueAxis.visible = 0
	bc.valueAxis.valueMin = -2
	bc.valueAxis.valueMax = +2
	bc.valueAxis.valueStep = 1

	bc.categoryAxis.tickUp = 0
	bc.categoryAxis.tickDown = 0
	bc.categoryAxis.categoryNames = names
	bc.categoryAxis.labels.angle = 90
	bc.categoryAxis.labels.boxAnchor = 'w'
	bc.categoryAxis.labels.dx = 0
	bc.categoryAxis.labels.dy = -125
	bc.categoryAxis.labels.fontName = 'Helvetica'
	bc.categoryAxis.labels.fontSize = 6

	g = Group(bc)
	g.translate(100, 175)
	g.rotate(-90)

	drawing.add(g)

	return drawing


def sampleV4a():
	"A bar chart showing value axis region starting at *exactly* zero."

	drawing = Drawing(400, 200)

	data = [(13, 20)]

	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data

	bc.strokeColor = colors.black

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'n'
	bc.categoryAxis.labels.dy = -5
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


def sampleV4b():
	"A bar chart showing value axis region starting *below* zero."

	drawing = Drawing(400, 200)

	data = [(13, 20)]

	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data

	bc.strokeColor = colors.black

	bc.valueAxis.valueMin = -10
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'n'
	bc.categoryAxis.labels.dy = -5
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


def sampleV4c():
	"A bar chart showing value axis region staring *above* zero."

	drawing = Drawing(400, 200)

	data = [(13, 20)]

	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data

	bc.strokeColor = colors.black

	bc.valueAxis.valueMin = 10
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'n'
	bc.categoryAxis.labels.dy = -5
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


def sampleV4d():
	"A bar chart showing value axis region entirely *below* zero."

	drawing = Drawing(400, 200)

	data = [(-13, -20)]

	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data

	bc.strokeColor = colors.black

	bc.valueAxis.valueMin = -30
	bc.valueAxis.valueMax = -10
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'n'
	bc.categoryAxis.labels.dy = -5
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


###

##dataSample5 = [(10, 20), (20, 30), (30, 40), (40, 50), (50, 60)]
##dataSample5 = [(10, 60), (20, 50), (30, 40), (40, 30), (50, 20)]
dataSample5 = [(10, 60), (20, 50), (30, 40), (40, 30)]

def sampleV5a():
	"A simple bar chart with no expressed spacing attributes."

	drawing = Drawing(400, 200)

	data = dataSample5

	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'n'
	bc.categoryAxis.labels.dy = -5
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


def sampleV5b():
	"A simple bar chart with proportional spacing."

	drawing = Drawing(400, 200)

	data = dataSample5

	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black

	bc.useAbsolute = 0
	bc.barWidth = 40
	bc.groupSpacing = 20
	bc.barSpacing = 10

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'n'
	bc.categoryAxis.labels.dy = -5
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


def sampleV5c1():
	"Make sampe simple bar chart but with absolute spacing."

	drawing = Drawing(400, 200)

	data = dataSample5

	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black

	bc.useAbsolute = 1
	bc.barWidth = 40
	bc.groupSpacing = 0
	bc.barSpacing = 0

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'n'
	bc.categoryAxis.labels.dy = -5
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


def sampleV5c2():
	"Make sampe simple bar chart but with absolute spacing."

	drawing = Drawing(400, 200)

	data = dataSample5

	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black

	bc.useAbsolute = 1
	bc.barWidth = 40
	bc.groupSpacing = 20
	bc.barSpacing = 0

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'n'
	bc.categoryAxis.labels.dy = -5
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


def sampleV5c3():
	"Make sampe simple bar chart but with absolute spacing."

	drawing = Drawing(400, 200)

	data = dataSample5

	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black

	bc.useAbsolute = 1
	bc.barWidth = 40
	bc.groupSpacing = 0
	bc.barSpacing = 10

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'n'
	bc.categoryAxis.labels.dy = -5
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


def sampleV5c4():
	"Make sampe simple bar chart but with absolute spacing."

	drawing = Drawing(400, 200)

	data = dataSample5

	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black

	bc.useAbsolute = 1
	bc.barWidth = 40
	bc.groupSpacing = 20
	bc.barSpacing = 10

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'n'
	bc.categoryAxis.labels.dy = -5
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


# Horizontal samples

def sampleH0a():
	"Make a slightly pathologic bar chart with only TWO data items."

	drawing = Drawing(400, 200)

	data = [(13, 20)]

	bc = HorizontalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data

	bc.strokeColor = colors.black

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'se'
	bc.categoryAxis.labels.angle = 30
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


def sampleH0b():
	"Make a pathologic bar chart with only ONE data item."

	drawing = Drawing(400, 200)

	data = [(42,)]

	bc = HorizontalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 50
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'se'
	bc.categoryAxis.labels.angle = 30
	bc.categoryAxis.categoryNames = ['Jan-99']

	drawing.add(bc)

	return drawing


def sampleH0c():
	"Make a really pathologic bar chart with NO data items at all!"

	drawing = Drawing(400, 200)

	data = [()]

	bc = HorizontalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'se'
	bc.categoryAxis.labels.angle = 30
	bc.categoryAxis.categoryNames = []

	drawing.add(bc)

	return drawing


def sampleH1():
	"Sample of multi-series bar chart."

	drawing = Drawing(400, 200)

	data = [
			(13, 5, 20, 22, 37, 45, 19, 4),
			(14, 6, 21, 23, 38, 46, 20, 5)
			]

	bc = HorizontalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'e'
	catNames = string.split('Jan Feb Mar Apr May Jun Jul Aug', ' ')
	catNames = map(lambda n:n+'-99', catNames)
	bc.categoryAxis.categoryNames = catNames
	drawing.add(bc)

	return drawing


def sampleH2a():
	"Sample of multi-series bar chart."

	data = [(2.4, -5.7, 2, 5, 9.2),
			(0.6, -4.9, -3, 4, 6.8)
			]

	labels = ("Q3 2000", "Year to Date", "12 months",
			  "Annualised\n3 years", "Since 07.10.99")

	drawing = Drawing(400, 200)

	bc = HorizontalBarChart()
	bc.x = 80
	bc.y = 50
	bc.height = 120
	bc.width = 300
	bc.data = data

	bc.barSpacing = 0
	bc.groupSpacing = 10
	bc.barWidth = 10

	bc.valueAxis.valueMin = -15
	bc.valueAxis.valueMax = +15
	bc.valueAxis.valueStep = 5
	bc.valueAxis.labels.fontName = 'Helvetica'
	bc.valueAxis.labels.fontSize = 8
	bc.valueAxis.labels.boxAnchor = 'n'   # irrelevant (becomes 'c')
	bc.valueAxis.labels.textAnchor = 'middle'
	bc.valueAxis.configure(bc.data)

	bc.categoryAxis.categoryNames = labels
	bc.categoryAxis.labels.fontName = 'Helvetica'
	bc.categoryAxis.labels.fontSize = 8
	bc.categoryAxis.labels.dx = -150

	drawing.add(bc)

	return drawing


def sampleH2b():
	"Sample of multi-series bar chart."

	data = [(2.4, -5.7, 2, 5, 9.2),
			(0.6, -4.9, -3, 4, 6.8)
			]

	labels = ("Q3 2000", "Year to Date", "12 months",
			  "Annualised\n3 years", "Since 07.10.99")

	drawing = Drawing(400, 200)

	bc = HorizontalBarChart()
	bc.x = 80
	bc.y = 50
	bc.height = 120
	bc.width = 300
	bc.data = data

	bc.barSpacing = 5
	bc.groupSpacing = 10
	bc.barWidth = 10

	bc.valueAxis.valueMin = -15
	bc.valueAxis.valueMax = +15
	bc.valueAxis.valueStep = 5
	bc.valueAxis.labels.fontName = 'Helvetica'
	bc.valueAxis.labels.fontSize = 8
	bc.valueAxis.labels.boxAnchor = 'n'   # irrelevant (becomes 'c')
	bc.valueAxis.labels.textAnchor = 'middle'

	bc.categoryAxis.categoryNames = labels
	bc.categoryAxis.labels.fontName = 'Helvetica'
	bc.categoryAxis.labels.fontSize = 8
	bc.categoryAxis.labels.dx = -150

	drawing.add(bc)

	return drawing


def sampleH2c():
	"Sample of multi-series bar chart."

	data = [(2.4, -5.7, 2, 5, 9.99),
			(0.6, -4.9, -3, 4, 9.99)
			]

	labels = ("Q3 2000", "Year to Date", "12 months",
			  "Annualised\n3 years", "Since 07.10.99")

	drawing = Drawing(400, 200)

	bc = HorizontalBarChart()
	bc.x = 80
	bc.y = 50
	bc.height = 120
	bc.width = 300
	bc.data = data

	bc.barSpacing = 2
	bc.groupSpacing = 10
	bc.barWidth = 10

	bc.valueAxis.valueMin = -15
	bc.valueAxis.valueMax = +15
	bc.valueAxis.valueStep = 5
	bc.valueAxis.labels.fontName = 'Helvetica'
	bc.valueAxis.labels.fontSize = 8
	bc.valueAxis.labels.boxAnchor = 'n'
	bc.valueAxis.labels.textAnchor = 'middle'

	bc.categoryAxis.categoryNames = labels
	bc.categoryAxis.labels.fontName = 'Helvetica'
	bc.categoryAxis.labels.fontSize = 8
	bc.categoryAxis.labels.dx = -150

	bc.barLabels.nudge = 10

	bc.barLabelFormat = '%0.2f'
	bc.barLabels.dx = 0
	bc.barLabels.dy = 0
	bc.barLabels.boxAnchor = 'n'  # irrelevant (becomes 'c')
	bc.barLabels.fontName = 'Helvetica'
	bc.barLabels.fontSize = 6

	drawing.add(bc)

	return drawing


def sampleH3():
	"A really horizontal bar chart (compared to the equivalent faked one)."

	names = ("UK Equities", "US Equities", "European Equities", "Japanese Equities",
			  "Pacific (ex Japan) Equities", "Emerging Markets Equities",
			  "UK Bonds", "Overseas Bonds", "UK Index-Linked", "Cash")

	series1 = (-1.5, 0.3, 0.5, 1.0, 0.8, 0.7, 0.4, 0.1, 1.0, 0.3)
	series2 = (0.0, 0.33, 0.55, 1.1, 0.88, 0.77, 0.44, 0.11, 1.10, 0.33)

	assert len(names) == len(series1), "bad data"
	assert len(names) == len(series2), "bad data"

	drawing = Drawing(400, 200)

	bc = HorizontalBarChart()
	bc.x = 100
	bc.y = 20
	bc.height = 150
	bc.width = 250
	bc.data = (series1,)
	bc.bars.fillColor = colors.green

	bc.barLabelFormat = '%0.2f'
	bc.barLabels.dx = 0
	bc.barLabels.dy = 0
	bc.barLabels.boxAnchor = 'w' # irrelevant (becomes 'c')
	bc.barLabels.fontName = 'Helvetica'
	bc.barLabels.fontSize = 6
	bc.barLabels.nudge = 10

	bc.valueAxis.visible = 0
	bc.valueAxis.valueMin = -2
	bc.valueAxis.valueMax = +2
	bc.valueAxis.valueStep = 1

	bc.categoryAxis.tickLeft = 0
	bc.categoryAxis.tickRight = 0
	bc.categoryAxis.categoryNames = names
	bc.categoryAxis.labels.boxAnchor = 'w'
	bc.categoryAxis.labels.dx = -170
	bc.categoryAxis.labels.fontName = 'Helvetica'
	bc.categoryAxis.labels.fontSize = 6

	g = Group(bc)
	drawing.add(g)

	return drawing


def sampleH4a():
	"A bar chart showing value axis region starting at *exactly* zero."

	drawing = Drawing(400, 200)

	data = [(13, 20)]

	bc = HorizontalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data

	bc.strokeColor = colors.black

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'e'
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


def sampleH4b():
	"A bar chart showing value axis region starting *below* zero."

	drawing = Drawing(400, 200)

	data = [(13, 20)]

	bc = HorizontalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data

	bc.strokeColor = colors.black

	bc.valueAxis.valueMin = -10
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'e'
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


def sampleH4c():
	"A bar chart showing value axis region starting *above* zero."

	drawing = Drawing(400, 200)

	data = [(13, 20)]

	bc = HorizontalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data

	bc.strokeColor = colors.black

	bc.valueAxis.valueMin = 10
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'e'
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


def sampleH4d():
	"A bar chart showing value axis region entirely *below* zero."

	drawing = Drawing(400, 200)

	data = [(-13, -20)]

	bc = HorizontalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data

	bc.strokeColor = colors.black

	bc.valueAxis.valueMin = -30
	bc.valueAxis.valueMax = -10
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'e'
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


dataSample5 = [(10, 60), (20, 50), (30, 40), (40, 30)]

def sampleH5a():
	"A simple bar chart with no expressed spacing attributes."

	drawing = Drawing(400, 200)

	data = dataSample5

	bc = HorizontalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'e'
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


def sampleH5b():
	"A simple bar chart with proportional spacing."

	drawing = Drawing(400, 200)

	data = dataSample5

	bc = HorizontalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black

	bc.useAbsolute = 0
	bc.barWidth = 40
	bc.groupSpacing = 20
	bc.barSpacing = 10

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'e'
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


def sampleH5c1():
	"A simple bar chart with absolute spacing."

	drawing = Drawing(400, 200)

	data = dataSample5

	bc = HorizontalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black

	bc.useAbsolute = 1
	bc.barWidth = 10
	bc.groupSpacing = 0
	bc.barSpacing = 0

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'e'
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


def sampleH5c2():
	"Simple bar chart with absolute spacing."

	drawing = Drawing(400, 200)

	data = dataSample5

	bc = HorizontalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black

	bc.useAbsolute = 1
	bc.barWidth = 10
	bc.groupSpacing = 20
	bc.barSpacing = 0

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'e'
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


def sampleH5c3():
	"Simple bar chart with absolute spacing."

	drawing = Drawing(400, 200)

	data = dataSample5

	bc = HorizontalBarChart()
	bc.x = 50
	bc.y = 20
	bc.height = 155
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black

	bc.useAbsolute = 1
	bc.barWidth = 10
	bc.groupSpacing = 0
	bc.barSpacing = 2

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'e'
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing


def sampleH5c4():
	"Simple bar chart with absolute spacing."

	drawing = Drawing(400, 200)

	data = dataSample5

	bc = HorizontalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black

	bc.useAbsolute = 1
	bc.barWidth = 10
	bc.groupSpacing = 20
	bc.barSpacing = 10

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'e'
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	drawing.add(bc)

	return drawing

def sampleSymbol1():
	"Simple bar chart using symbol attribute."

	drawing = Drawing(400, 200)

	data = dataSample5

	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 125
	bc.width = 300
	bc.data = data
	bc.strokeColor = colors.black

	bc.barWidth = 10
	bc.groupSpacing = 15
	bc.barSpacing = 3

	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 60
	bc.valueAxis.valueStep = 15

	bc.categoryAxis.labels.boxAnchor = 'e'
	bc.categoryAxis.categoryNames = ['Ying', 'Yang']

	sym1 = ShadedRect()
	sym1.fillColorStart = colors.black
	sym1.fillColorEnd = colors.blue
	sym1.orientation = 'horizontal'
	sym1.strokeWidth = 0

	sym2 = ShadedRect()
	sym2.fillColorStart = colors.black
	sym2.fillColorEnd = colors.pink
	sym2.orientation = 'horizontal'
	sym2.strokeWidth = 0

	bc.bars.symbol = sym1
	bc.bars[2].symbol = sym2

	drawing.add(bc)

	return drawing

#class version of function sampleH5c4 above
class SampleH5c4(Drawing):
	"Simple bar chart with absolute spacing."

	def __init__(self,width=400,height=200,*args,**kw):
		apply(Drawing.__init__,(self,width,height)+args,kw)
		bc = HorizontalBarChart()
		bc.x = 50
		bc.y = 50
		bc.height = 125
		bc.width = 300
		bc.data = dataSample5
		bc.strokeColor = colors.black

		bc.useAbsolute = 1
		bc.barWidth = 10
		bc.groupSpacing = 20
		bc.barSpacing = 10

		bc.valueAxis.valueMin = 0
		bc.valueAxis.valueMax = 60
		bc.valueAxis.valueStep = 15

		bc.categoryAxis.labels.boxAnchor = 'e'
		bc.categoryAxis.categoryNames = ['Ying', 'Yang']

		self.add(bc,name='HBC')
