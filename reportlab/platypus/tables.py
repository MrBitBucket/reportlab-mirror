###############################################################################
#
#	ReportLab Public License Version 1.0
#
#	Except for the change of names the spirit and intention of this
#	license is the same as that of Python
#
#	(C) Copyright ReportLab Inc. 1998-2000.
#
#
# All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted, provided
# that the above copyright notice appear in all copies and that both that
# copyright notice and this permission notice appear in supporting
# documentation, and that the name of ReportLab not be used
# in advertising or publicity pertaining to distribution of the software
# without specific, written prior permission. 
# 
#
# Disclaimer
#
# ReportLab Inc. DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS,
# IN NO EVENT SHALL ReportLab BE LIABLE FOR ANY SPECIAL, INDIRECT
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#
###############################################################################
#	$Log: tables.py,v $
#	Revision 1.20  2000/07/11 14:29:45  rgbecker
#	Table splitting start
#
#	Revision 1.19  2000/07/10 15:25:47  andy_robinson
#	Added tables to PythonPoint
#	
#	Revision 1.18  2000/07/08 15:30:04  rgbecker
#	Cosmetics and error testing
#	
#	Revision 1.17  2000/07/07 16:22:10  rgbecker
#	Fix auto hieght stuff
#	
#	Revision 1.16  2000/07/07 10:23:36  rgbecker
#	First attempt at VALIGN
#	
#	Revision 1.15  2000/07/06 14:05:55	rgbecker
#	Adjusted doc string
#	
#	Revision 1.14  2000/07/06 12:41:47	rgbecker
#	First try at auto sizing
#	
#	Revision 1.13  2000/06/29 17:55:19	aaron_watters
#	support explicit \n line splitting in cells
#	
#	Revision 1.12  2000/06/13 13:03:31	aaron_watters
#	more documentation changes
#	
#	Revision 1.11  2000/06/01 15:23:06	rgbecker
#	Platypus re-organisation
#	
#	Revision 1.10  2000/05/26 09:49:23	rgbecker
#	Color fixes; thanks to J Alet
#	
#	Revision 1.9  2000/05/16 16:15:16  rgbecker
#	Changes related to removal of SimpleFlowDocument
#	
#	Revision 1.8  2000/04/26 11:07:15  andy_robinson
#	Tables changed to use reportlab.lib.colors instead of
#	the six hard-coded color strings there previously.
#	
#	Revision 1.7  2000/04/14 12:17:05  rgbecker
#	Splitting layout.py
#	
#	Revision 1.6  2000/04/14 11:54:57  rgbecker
#	Splitting layout.py
#	
#	Revision 1.5  2000/04/14 08:56:20  rgbecker
#	Drawable ==> Flowable
#	
#	Revision 1.4  2000/02/17 02:09:05  rgbecker
#	Docstring & other fixes
#	
#	Revision 1.3  2000/02/15 17:55:59  rgbecker
#	License text fixes
#	
#	Revision 1.2  2000/02/15 15:47:09  rgbecker
#	Added license, __version__ and Logi comment
#	
__version__=''' $Id: tables.py,v 1.20 2000/07/11 14:29:45 rgbecker Exp $ '''
__doc__="""
Tables are created by passing the constructor a tuple of column widths, a tuple of row heights and the data in
row order. Drawing of the table can be controlled by using a TableStyle instance. This allows control of the
color and weight of the lines (if any), and the font, alignment and padding of the text.

None values in the sequence of row heights or column widths, mean that the corresponding rows
or columns should be automatically sized.

All the cell values should be convertible to strings; embedded newline '\\n' characters
cause the value to wrap (ie are like a traditional linefeed).

See the test output from running this module as a script for a discussion of the method for constructing
tables and table styles.
"""
from reportlab.platypus import *
from reportlab.lib.styles import PropertySet, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import DEFAULT_PAGE_SIZE
import operator, string

_stringtype = type('')

class CellStyle(PropertySet):
	defaults = {
		'fontname':'Times-Roman',
		'fontsize':10,
		'leading':12,
		'leftPadding':6,
		'rightPadding':6,
		'topPadding':3,
		'bottomPadding':3,
		'firstLineIndent':0,
		'color':colors.black,
		'alignment': 'LEFT',
		'background': (1,1,1),
		'valign': 'BOTTOM',
		}

class TableStyle:
	def __init__(self, cmds=None):
		self._cmds = cmds
		if cmds is None:
			self._cmds = []
	def add(self, *cmd):
		self._cmds.append(cmd)
	def getCommands(self):
		return self._cmds

TableStyleType = type(TableStyle())
		
class Table(Flowable):
	def __init__(self, colWidths, rowHeights, data, style=None,
				repeatRows=0, repeatCols=0, splitByRow=1):
		if not colWidths:
			raise ValueError, "Table must have at least 1 column"
		if not rowHeights:
			raise ValueError, "Table must have at least 1 row"
		nrows = self._nrows = len(rowHeights)
		if len(data) != nrows:
			raise ValueError, "Data error - %d rows in data but %d in grid" % (len(data), nrows)
		ncols = self._ncols = len(colWidths)
		for i in range(nrows):
			if len(data[i]) != ncols:
				raise ValueError, "Not enough data points in row %d!" % i
		self._rowHeights = self._argH = rowHeights
		self._colWidths = self._argW = colWidths
		self._cellvalues = data
		dflt = CellStyle('<default>')

		self._cellStyles = [None]*nrows
		for i in range(nrows):
			self._cellStyles[i] = [dflt]*ncols

		self._bkgrndcmds = []
		self._linecmds = []
		self._curweight = self._curcolor = self._curcellstyle = None
		self.repeatRows = repeatRows
		self.repeatCols = repeatCols
		self.splitByRow = splitByRow

		if style:
			self.setStyle(style)

	def _calc(self):

		H = self._argH
		W = self._argW

		if None in H:
			H = H[:]	#make a copy as we'll change it
			self._rowHeights = H
			while None in H:
				i = H.index(None)
				V = self._cellvalues[i]
				S = self._cellStyles[i]
				h = 0
				for v, s in map(None, V, S):
					if type(v) is not _stringtype: v = str(v)
					v = string.split(v, "\n")
					t = s.leading*len(v)+s.bottomPadding+s.topPadding
					if t>h: h = t	#record a new maximum
				H[i] = h

		if None in W:
			W = W[:]
			self._colWidths = W
			while None in W:
				i = W.index(None)
				f = lambda x,i=i: operator.getitem(x,i)
				V = map(f,self._cellvalues)
				S = map(f,self._cellStyles)
				w = 0
				for v, s in map(None, V, S):
					if type(v) is not _stringtype: v = str(v)
					v = string.split(v, "\n")
					t = s.leftPadding+s.rightPadding + max(map(lambda a, b=s.fontname,
								c=s.fontsize,d=self.canv: d.stringWidth(a,b,c), v))
					if t>w: w = t	#record a new maximum
				W[i] = w


		height = self._height = reduce(operator.add, H, 0)
		self._rowpositions = [height]	 # index 0 is actually topline; we skip when processing cells
		for h in H:
			height = height - h
			self._rowpositions.append(height)
		assert abs(height)<1e-8, 'Internal height error'
		width = 0
		self._colpositions = [0]		#index -1 is right side boundary; we skip when processing cells
		for w in W:
			width = width + w
			self._colpositions.append(width)
		self._width = width

	def setStyle(self, tblstyle):
		if type(tblstyle) is not TableStyleType:
			tblstyle = TableStyle(tblstyle)
		for cmd in tblstyle.getCommands():
			self._addCommand(cmd)

	def _addCommand(self,cmd):
		if cmd[0] == 'BACKGROUND':
			self._bkgrndcmds.append(cmd)
		elif _isLineCommand(cmd):
			self._linecmds.append(cmd)
		else:
			(op, (sc, sr), (ec, er)), values = cmd[:3] , cmd[3:]
			if sc < 0: sc = sc + self._ncols
			if ec < 0: ec = ec + self._ncols
			if sr < 0: sr = sr + self._nrows
			if er < 0: er = er + self._nrows
			for i in range(sr, er+1):
				for j in range(sc, ec+1):
					_setCellStyle(self._cellStyles, i, j, op, values)

	def _drawLines(self):
		for op, (sc, sr), (ec, er), weight, color in self._linecmds:
			if sc < 0: sc = sc + self._ncols
			if ec < 0: ec = ec + self._ncols
			if sr < 0: sr = sr + self._nrows
			if er < 0: er = er + self._nrows
			if op == 'GRID':
				self._drawBox( (sc, sr), (ec, er), weight, color)
				self._drawInnerGrid( (sc, sr), (ec, er), weight, color)
			elif op in ('BOX',	'OUTLINE',):
				self._drawBox( (sc, sr), (ec, er), weight, color)
			elif op == 'INNERGRID':
				self._drawInnerGrid( (sc, sr), (ec, er), weight, color)
			elif op == 'LINEBELOW':
				self._drawHLines((sc, sr+1), (ec, er+1), weight, color)
			elif op == 'LINEABOVE':
				self._drawHLines((sc, sr), (ec, er), weight, color)
			elif op == 'LINEBEFORE':
				self._drawVLines((sc, sr), (ec, er), weight, color)
			elif op == 'LINEAFTER':
				self._drawVLines((sc+1, sr), (ec+1, er), weight, color)
			else:
				raise ValueError, "Unknown line style %s" % op
		self._curcolor = None

	def _drawBox(self,	(sc, sr), (ec, er), weight, color):
		self._drawHLines((sc, sr), (ec, sr), weight, color)
		self._drawHLines((sc, er+1), (ec, er+1), weight, color)
		self._drawVLines((sc, sr), (sc, er), weight, color)
		self._drawVLines((ec+1, sr), (ec+1, er), weight, color)

	def _drawInnerGrid(self, (sc, sr), (ec, er), weight, color):
		self._drawHLines((sc, sr+1), (ec, er), weight, color)
		self._drawVLines((sc+1, sr), (ec, er), weight, color)

	def _prepLine(self, weight, color):
		if color != self._curcolor:
			self.canv.setStrokeColor(color)
			self._curcolor = color
		if weight != self._curweight:
			self.canv.setLineWidth(weight)
			self._curweight = weight

	def _drawHLines(self, (sc, sr), (ec, er), weight, color):
		self._prepLine(weight, color)
		scp = self._colpositions[sc]
		ecp = self._colpositions[ec+1]
		for rowpos in self._rowpositions[sr:er+1]:
			self.canv.line(scp, rowpos, ecp, rowpos)

	def _drawVLines(self, (sc, sr), (ec, er), weight, color):
		self._prepLine(weight, color)
		srp = self._rowpositions[sr]
		erp = self._rowpositions[er+1]
		for colpos in self._colpositions[sc:ec+1]:
			self.canv.line(colpos, srp, colpos, erp)

	def wrap(self, availWidth, availHeight):
		self._calc()
		#nice and easy, since they are predetermined size
		self.availWidth = availWidth
		return (self._width, self._height)

	def _cr_0(self,n,cmds):
		for op, (sc, sr), (ec, er), weight, color in cmds:
			if sr>=n: continue
			if er>=n: er = n-1
			self._addCommand((op, (sc, sr), (ec, er), weight, color))

	def _cr_1_1(self,n,repeatRows, cmds):
		for op, (sc, sr), (ec, er), weight, color in cmds:
			if sr>=0 and sr>=repeatRows and sr<n and er>=0 and er<n: continue
			if sr>=repeatRows and sr<n: sr=repeatRows
			elif sr>=repeatRows and sr>=n: sr=sr+repeatRows-n
			if er>=repeatRows and er<n: er=repeatRows
			elif er>=repeatRows and er>=n: er=er+repeatRows-n
			self._addCommand((op, (sc, sr), (ec, er), weight, color))

	def _cr_1_0(self,n,cmds):
		for op, (sc, sr), (ec, er), weight, color in cmds:
			if er>=0 and er<n: continue
			if sr>=0 and sr<n: sr=0
			if sr>=n: sr = sr-n
			if er>=n: er = er-n
			self._addCommand((op, (sc, sr), (ec, er), weight, color))

	def _splitRows(self,availHeight):
		self._calc()
		h = 0
		n = 0
		lim = len(self._rowHeights)
		while n<lim:
			hn = h + self._rowHeights[n]
			if hn>availHeight: break
			h = hn
			n = n + 1

		if n<=self.repeatRows:
			return []

		if n==lim: return [self]

		repeatRows = self.repeatRows
		repeatCols = self.repeatCols
		splitByRow = self.splitByRow
		data = self._cellvalues

		#we're going to split into two superRows
		R0 = Table( self._argW, self._argH[:n], data[:n],
				repeatRows=repeatRows, repeatCols=repeatCols,
				splitByRow=splitByRow)

		#copy the styles and commands
		R0._cellStyles = self._cellStyles[:n]
		R0._cr_0(n,self._linecmds)
		R0._cr_0(n,self._bkgrndcmds)

		if repeatRows:
			R1 = Table(self._argW, self._argH[:repeatRows]+self._argH[n:],
					data[:repeatRows]+data[n:],
					repeatRows=repeatRows, repeatCols=repeatCols,
					splitByRow=splitByRow)
			R1._cellStyles = self._cellStyles[:repeatRows]+self._cellStyles[n:]
			R1._cr_1_1(n,repeatRows,self._linecmds)
			R1._cr_1_1(n,repeatRows,self._bkgrndcmds)
		else:
			R1 = Table(self._argW, self._argH[n:],data[n:],
					repeatRows=repeatRows, repeatCols=repeatCols,
					splitByRow=splitByRow)
			R1._cellStyles = self._cellStyles[n:]
			R1._cr_1_0(n,self._linecmds)
			R1._cr_1_0(n,self._bkgrndcmds)

		return [R0,R1]

	def split(self, availWidth, availHeight):
		if self.splitByRow:
			if self._width>availWidth: return []
			return self._splitRows(availHeight)
		else:
			raise NotImplementedError
		
				
	def draw(self):
		nudge = 0.5 * (self.availWidth - self._width)
		self.canv.translate(nudge, 0)
		self._drawBkgrnd()
		self._drawLines()
		for row, rowstyle, rowpos, rowheight in map(None, self._cellvalues, self._cellStyles, self._rowpositions[1:], self._rowHeights):
			for cellval, cellstyle, colpos, colwidth in map(None, row, rowstyle, self._colpositions[:-1], self._colWidths):
				self._drawCell(cellval, cellstyle, (colpos, rowpos), (colwidth, rowheight))

	def _drawBkgrnd(self):
		for cmd, (sc, sr), (ec, er), color in self._bkgrndcmds:
			if sc < 0: sc = sc + self._ncols
			if ec < 0: ec = ec + self._ncols
			if sr < 0: sr = sr + self._nrows
			if er < 0: er = er + self._nrows
			color = colors.toColor(color, colors.Color(1,1,1))
			x0 = self._colpositions[sc]
			y0 = self._rowpositions[sr]
			x1 = self._colpositions[ec+1]
			y1 = self._rowpositions[er+1]
			self.canv.setFillColor(color)
			self.canv.rect(x0, y0, x1-x0, y1-y0,stroke=0,fill=1)

	def _drawCell(self, cellval, cellstyle, (colpos, rowpos), (colwidth, rowheight)):
		#print "cellstyle is ", repr(cellstyle), id(cellstyle)
		if self._curcellstyle is not cellstyle:
			cur = self._curcellstyle
			if cur is None or cellstyle.color != cur.color:
				#print "setting cell color to %s" % `cellstyle.color`
				self.canv.setFillColor(cellstyle.color)
			if cur is None or cellstyle.leading != cur.leading or cellstyle.fontname != cur.fontname or cellstyle.fontsize != cur.fontsize:
				#print "setting font: %s, %s, %s" % (cellstyle.fontname, cellstyle.fontsize, cellstyle.leading)
				self.canv.setFont(cellstyle.fontname, cellstyle.fontsize, cellstyle.leading)
			self._curcellstyle = cellstyle
		#print "leading is ", cellstyle.leading, "size is", cellstyle.fontsize
		just = cellstyle.alignment
		#print "alignment is ", just
		if just == 'LEFT':
			draw = self.canv.drawString
			x = colpos + cellstyle.leftPadding
		elif just in ('CENTRE', 'CENTER'):
			draw = self.canv.drawCentredString
			x = colpos + colwidth * 0.5
		elif just == 'RIGHT':
			draw = self.canv.drawRightString
			x = colpos + colwidth - cellstyle.rightPadding
		else:
			raise ValueError, 'Invalid justification %s' % just

		if type(cellval) is _stringtype:
			val = cellval
		else:
			val = str(cellval)
		vals = string.split(val, "\n")
		n = len(vals)-1
		leading = cellstyle.leading
		valign = cellstyle.valign
		if valign=='BOTTOM':
			y = rowpos + cellstyle.bottomPadding+n*leading
		elif valign=='TOP':
			y = rowpos + rowheight - cellstyle.topPadding - cellstyle.fontsize
		elif valign=='MIDDLE':
			y = rowpos + (cellstyle.bottomPadding + rowheight - cellstyle.topPadding+n*leading)/2.0
		else:
			raise ValueError, "Bad valign: '%s'" % str(valign)

		for v in vals:
			draw(x, y, v)
			y = y-leading
		
# for text,
#	drawCentredString(self, x, y, text) where x is center
#	drawRightString(self, x, y, text) where x is right
#	drawString(self, x, y, text) where x is left

LINECOMMANDS = (
	'GRID', 'BOX', 'OUTLINE', 'INNERGRID', 'LINEBELOW', 'LINEABOVE', 'LINEBEFORE', 'LINEAFTER', )


def _isLineCommand(cmd):
	return cmd[0] in LINECOMMANDS

def _setCellStyle(cellStyles, i, j, op, values):
	new = CellStyle('<%d, %d>' % (i,j), cellStyles[i][j])
	cellStyles[i][j] = new
	if op == 'FONT':
		new.fontname = values[0]
		new.fontsize = values[1]
	elif op == 'TEXTCOLOR':
		new.color = colors.toColor(values[0], colors.Color(0,0,0))
	elif op in ('ALIGN', 'ALIGNMENT'):
		new.alignment = values[0]
	elif op == 'VALIGN':
		new.valign = values[0]
	elif op == 'LEFTPADDING':
		new.leftPadding = values[0]
	elif op == 'RIGHTPADDING':
		new.rightPadding = values[0]
	elif op == 'TOPPADDING':
		new.topPadding = values[0]
	elif op == 'BOTTOMPADDING':
		new.bottomPadding = values[0]

GRID_STYLE = TableStyle(
	[('GRID', (0,0), (-1,-1), 0.25, colors.black),
	 ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
	)
BOX_STYLE = TableStyle(
	[('BOX', (0,0), (-1,-1), 0.50, colors.black),
	 ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
	)
LABELED_GRID_STYLE = TableStyle(
	[('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
	 ('BOX', (0,0), (-1,-1), 2, colors.black),
	 ('LINEBELOW', (0,0), (-1,0), 2, colors.black),
	 ('LINEAFTER', (0,0), (0,-1), 2, colors.black),
	 ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
	)
COLORED_GRID_STYLE = TableStyle(
	[('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
	 ('BOX', (0,0), (-1,-1), 2, colors.red),
	 ('LINEBELOW', (0,0), (-1,0), 2, colors.black),
	 ('LINEAFTER', (0,0), (0,-1), 2, colors.black),
	 ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
	)
LIST_STYLE = TableStyle(
	[('LINEABOVE', (0,0), (-1,0), 2, colors.green),
	 ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
	 ('LINEBELOW', (0,-1), (-1,-1), 2, colors.green),
	 ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
	)

def test():
	from reportlab.lib.units import inch
	rowheights = (24, 16, 16, 16, 16)
	rowheights2 = (24, 16, 16, 16, 30)
	colwidths = (50, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32)
	data = (
		('', 'Jan', 'Feb', 'Mar','Apr','May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'),
		('Mugs', 0, 4, 17, 3, 21, 47, 12, 33, 2, -2, 44, 89),
		('T-Shirts', 0, 42, 9, -3, 16, 4, 72, 89, 3, 19, 32, 119),
		('Key Ring', 0,0,0,0,0,0,1,0,0,0,2,13),
		('Hats', 893, 912, '1,212', 643, 789, 159, 888, '1,298', 832, 453, '1,344','2,843')
		)
	data2 = (
		('', 'Jan', 'Feb', 'Mar','Apr','May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'),
		('Mugs', 0, 4, 17, 3, 21, 47, 12, 33, 2, -2, 44, 89),
		('T-Shirts', 0, 42, 9, -3, 16, 4, 72, 89, 3, 19, 32, 119),
		('Key Ring', 0,0,0,0,0,0,1,0,0,0,2,13),
		('Hats\nLarge', 893, 912, '1,212', 643, 789, 159, 888, '1,298', 832, 453, '1,344','2,843')
		)
	styleSheet = getSampleStyleSheet()
	lst = []
	lst.append(Paragraph("Tables", styleSheet['Heading1']))
	lst.append(Paragraph(__doc__, styleSheet['BodyText']))
	lst.append(Paragraph("The Tables (shown in different styles below) were created using the following code:", styleSheet['BodyText']))
	lst.append(Preformatted("""
	colwidths = (50, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32)
	rowheights = (24, 16, 16, 16, 16)
	data = (
		('', 'Jan', 'Feb', 'Mar','Apr','May', 'Jun',
		   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'),
		('Mugs', 0, 4, 17, 3, 21, 47, 12, 33, 2, -2, 44, 89),
		('T-Shirts', 0, 42, 9, -3, 16, 4, 72, 89, 3, 19, 32, 119),
		('Key Ring', 0,0,0,0,0,0,1,0,0,0,2,13),
		('Hats', 893, 912, '1,212', 643, 789, 159,
			 888, '1,298', 832, 453, '1,344','2,843')
		)	
	t = Table(colwidths, rowheights,  data)
	""", styleSheet['Code'], dedent=4))
	lst.append(Paragraph("""
	You can then give the Table a TableStyle object to control its format. The first TableStyle used was
	created as follows:
	""", styleSheet['BodyText']))
	lst.append(Preformatted("""
GRID_STYLE = TableStyle(
	[('GRID', (0,0), (-1,-1), 0.25, colors.black),
	 ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
	)
	""", styleSheet['Code']))
	lst.append(Paragraph("""
	TableStyles are created by passing in a list of commands. There are two types of commands - line commands
	and cell formatting commands. In all cases, the first three elements of a command are the command name,
	the starting cell and the ending cell.
	""", styleSheet['BodyText']))
	lst.append(Paragraph("""
	Line commands always follow this with the weight and color of the desired lines. Colors can be names,
	or they can be specified as a (R,G,B) tuple, where R, G and B are floats and (0,0,0) is black. The line
	command names are: GRID, BOX, OUTLINE, INNERGRID, LINEBELOW, LINEABOVE, LINEBEFORE
	and LINEAFTER. BOX and OUTLINE are equivalent, and GRID is the equivalent of applying both BOX and
	INNERGRID.
	""", styleSheet['BodyText']))
	lst.append(Paragraph("""
	Cell formatting commands are:
	""", styleSheet['BodyText']))
	lst.append(Paragraph("""
	FONT - takes fontname, fontsize and (optional) leading.
	""", styleSheet['Definition']))
	lst.append(Paragraph("""
	TEXTCOLOR - takes a color name or (R,G,B) tuple.
	""", styleSheet['Definition']))
	lst.append(Paragraph("""
	ALIGNMENT (or ALIGN) - takes one of LEFT, RIGHT and CENTRE (or CENTER).
	""", styleSheet['Definition']))
	lst.append(Paragraph("""
	LEFTPADDING - defaults to 6.
	""", styleSheet['Definition']))
	lst.append(Paragraph("""
	RIGHTPADDING - defaults to 6.
	""", styleSheet['Definition']))
	lst.append(Paragraph("""
	BOTTOMPADDING - defaults to 3.
	""", styleSheet['Definition']))
	lst.append(Paragraph("""
	A tablestyle is applied to a table by calling Table.setStyle(tablestyle).
	""", styleSheet['BodyText']))
	t = Table(colwidths, rowheights,  data)
	t.setStyle(GRID_STYLE)
	lst.append(PageBreak())
	lst.append(Paragraph("This is GRID_STYLE\n", styleSheet['BodyText']))
	lst.append(t)
	
	t = Table(colwidths, rowheights,  data)
	t.setStyle(BOX_STYLE)
	lst.append(Paragraph("This is BOX_STYLE\n", styleSheet['BodyText']))
	lst.append(t)
	lst.append(Paragraph("""
	It was created as follows:
	""", styleSheet['BodyText']))
	lst.append(Preformatted("""
BOX_STYLE = TableStyle(
	[('BOX', (0,0), (-1,-1), 0.50, colors.black),
	 ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
	)
	""", styleSheet['Code']))
	
	t = Table(colwidths, rowheights,  data)
	t.setStyle(LABELED_GRID_STYLE)
	lst.append(Paragraph("This is LABELED_GRID_STYLE\n", styleSheet['BodyText']))
	lst.append(t)
	t = Table(colwidths, rowheights2,  data2)
	t.setStyle(LABELED_GRID_STYLE)
	lst.append(Paragraph("This is LABELED_GRID_STYLE ILLUSTRATES EXPLICIT LINE SPLITTING WITH NEWLINE (different heights and data)\n", styleSheet['BodyText']))
	lst.append(t)
	lst.append(Paragraph("""
	It was created as follows:
	""", styleSheet['BodyText']))
	lst.append(Preformatted("""
LABELED_GRID_STYLE = TableStyle(
	[('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
	 ('BOX', (0,0), (-1,-1), 2, colors.black),
	 ('LINEBELOW', (0,0), (-1,0), 2, colors.black),
	 ('LINEAFTER', (0,0), (0,-1), 2, colors.black),
	 ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
	)
	""", styleSheet['Code']))
	lst.append(PageBreak())
	
	t = Table(colwidths, rowheights,  data)
	t.setStyle(COLORED_GRID_STYLE)
	lst.append(Paragraph("This is COLORED_GRID_STYLE\n", styleSheet['BodyText']))
	lst.append(t)
	lst.append(Paragraph("""
	It was created as follows:
	""", styleSheet['BodyText']))
	lst.append(Preformatted("""
COLORED_GRID_STYLE = TableStyle(
	[('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
	 ('BOX', (0,0), (-1,-1), 2, colors.red),
	 ('LINEBELOW', (0,0), (-1,0), 2, colors.black),
	 ('LINEAFTER', (0,0), (0,-1), 2, colors.black),
	 ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
	)
	""", styleSheet['Code']))
	
	t = Table(colwidths, rowheights,  data)
	t.setStyle(LIST_STYLE)
	lst.append(Paragraph("This is LIST_STYLE\n", styleSheet['BodyText']))
	lst.append(t)
	lst.append(Paragraph("""
	It was created as follows:
	""", styleSheet['BodyText']))
	lst.append(Preformatted("""
LIST_STYLE = TableStyle(
	[('LINEABOVE', (0,0), (-1,0), 2, colors.green),
	 ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
	 ('LINEBELOW', (0,-1), (-1,-1), 2, colors.green),
	 ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
	)
	""", styleSheet['Code']))
   
	t = Table(colwidths, rowheights,  data)
	ts = TableStyle(
	[('LINEABOVE', (0,0), (-1,0), 2, colors.green),
	 ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
	 ('LINEBELOW', (0,-1), (-1,-1), 2, colors.green),
	 ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
	 ('TEXTCOLOR', (0,1), (0,-1), colors.red),
	 ('BACKGROUND', (0,0), (-1,0), colors.Color(0,0.7,0.7))]
	)
	t.setStyle(ts)
	lst.append(Paragraph("This is a custom style\n", styleSheet['BodyText']))
	lst.append(t)
	lst.append(Paragraph("""
	It was created as follows:
	""", styleSheet['BodyText']))
	lst.append(Preformatted("""
   ts = TableStyle(
	[('LINEABOVE', (0,0), (-1,0), 2, colors.green),
	 ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
	 ('LINEBELOW', (0,-1), (-1,-1), 2, colors.green),
	 ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
	 ('TEXTCOLOR', (0,1), (0,-1), colors.red),
	 ('BACKGROUND', (0,0), (-1,0), colors.Color(0,0.7,0.7))]
	)
	""", styleSheet['Code']))
	data = (
		('', 'Jan\nCold', 'Feb\n', 'Mar\n','Apr\n','May\n', 'Jun\nHot', 'Jul\n', 'Aug\nThunder', 'Sep\n', 'Oct\n', 'Nov\n', 'Dec\n'),
		('Mugs', 0, 4, 17, 3, 21, 47, 12, 33, 2, -2, 44, 89),
		('T-Shirts', 0, 42, 9, -3, 16, 4, 72, 89, 3, 19, 32, 119),
		('Key Ring', 0,0,0,0,0,0,1,0,0,0,2,13),
		('Hats', 893, 912, '1,212', 643, 789, 159, 888, '1,298', 832, 453, '1,344','2,843')
		)
	c = list(colwidths)
	c[0] = None
	c[8] = None
	t = Table(c, [None]+list(rowheights[1:]),  data)
	t.setStyle(LIST_STYLE)
	lst.append(Paragraph("""
		This is a LIST_STYLE table with the first rowheight set to None ie automatic.
		The top row cells are split at a newline '\\n' character. The first and August
		column widths were also set to None.
	""", styleSheet['BodyText']))
	lst.append(t)
	lst.append(Paragraph("""
		The red numbers should be aligned LEFT &amp; BOTTOM, the blue RIGHT &amp; TOP
		and the green CENTER &amp; MIDDLE.
	""", styleSheet['BodyText']))
	data=	[['X00y', 'X01y', 'X02y', 'X03y', 'X04y'],
			['X10y', 'X11y', 'X12y', 'X13y', 'X14y'],
			['X20y', 'X21y', 'X22y', 'X23y', 'X24y'],
			['X30y', 'X31y', 'X32y', 'X33y', 'X34y']]
	t=Table(5*[0.4*inch], 4*[0.4*inch], data)
	t.setStyle([('ALIGN',(1,1),(-2,-2),'LEFT'),
				('TEXTCOLOR',(1,1),(-2,-2),colors.red),

				('VALIGN',(0,0),(1,-1),'TOP'),
				('ALIGN',(0,0),(1,-1),'RIGHT'),
				('TEXTCOLOR',(0,0),(1,-1),colors.blue),

				('ALIGN',(0,-1),(-1,-1),'CENTER'),
				('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
				('TEXTCOLOR',(0,-1),(-1,-1),colors.green),

				('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
				('BOX', (0,0), (-1,-1), 0.25, colors.black),
				])
	lst.append(t)
	data = [('alignment', 'align\012alignment'),
			('bulletColor', 'bulletcolor\012bcolor'),
			('bulletFontName', 'bfont\012bulletfontname'),
			('bulletFontSize', 'bfontsize\012bulletfontsize'),
			('bulletIndent', 'bindent\012bulletindent'),
			('firstLineIndent', 'findent\012firstlineindent'),
			('fontName', 'face\012fontname\012font'),
			('fontSize', 'size\012fontsize'),
			('leading', 'leading'),
			('leftIndent', 'leftindent\012lindent'),
			('rightIndent', 'rightindent\012rindent'),
			('spaceAfter', 'spaceafter\012spacea'),
			('spaceBefore', 'spacebefore\012spaceb'),
			('textColor', 'fg\012textcolor\012color')]
	t = Table(2*[None], len(data)*[None], data)
	t.setStyle([
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ])
	lst.append(t)
	t=apply(Table,([None, None], [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], [('Attribute', 'Synonyms'), ('alignment', 'align, alignment'), ('bulletColor', 'bulletcolor, bcolor'), ('bulletFontName', 'bfont, bulletfontname'), ('bulletFontSize', 'bfontsize, bulletfontsize'), ('bulletIndent', 'bindent, bulletindent'), ('firstLineIndent', 'findent, firstlineindent'), ('fontName', 'face, fontname, font'), ('fontSize', 'size, fontsize'), ('leading', 'leading'), ('leftIndent', 'leftindent, lindent'), ('rightIndent', 'rightindent, rindent'), ('spaceAfter', 'spaceafter, spacea'), ('spaceBefore', 'spacebefore, spaceb'), ('textColor', 'fg, textcolor, color')]))
	t.repeatRows = 1
	t.setStyle([
				('FONT',(0,0),(-1,1),'Times-Bold',10,12),
				('FONT',(0,1),(-1,-1),'Courier',8,8),
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
				('BOX', (0,0), (-1,-1), 0.25, colors.black),
				])
	lst.append(t)
	SimpleDocTemplate('testtables.pdf', showBoundary=1).build(lst)

if __name__ == '__main__':
	test()
