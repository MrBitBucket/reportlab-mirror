#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/platypus/tables.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/platypus/tables.py,v 1.59 2002/06/20 09:56:51 rgbecker Exp $
__version__=''' $Id: tables.py,v 1.59 2002/06/20 09:56:51 rgbecker Exp $ '''
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
from reportlab import rl_config
from reportlab.lib.styles import PropertySet, getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.utils import fp_str
from reportlab.pdfbase import pdfmetrics
import operator, string

from types import TupleType, ListType, StringType

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

# experimental replacement
class CellStyle1(PropertySet):
	fontname = "Times-Roman"
	fontsize = 10
	leading = 12
	leftPadding = 6
	rightPadding = 6
	topPadding = 3
	bottomPadding = 3
	firstLineIndent = 0
	color = colors.black
	alignment = 'LEFT'
	background = (1,1,1)
	valign = "BOTTOM"
	def __init__(self, name, parent=None):
		self.name = name
		if parent is not None:
			parent.copy(self)
	def copy(self, result=None):
		if result is None:
			result = CellStyle1()
		for name in dir(self):
			setattr(result, name, gettattr(self, name))
		return result

CellStyle = CellStyle1

class TableStyle:
	def __init__(self, cmds=None, parent=None, **kw):
		#handle inheritance from parent first.
		commands = []
		if parent:
			# copy the parents list at construction time
			commands = commands + parent.getCommands()
			self._opts = parent._opts
		if cmds:
			commands = commands + list(cmds)
		self._cmds = commands
		self._opts={}
		self._opts.update(kw)

	def add(self, *cmd):
		self._cmds.append(cmd)
	def __repr__(self):
		L = map(repr, self._cmds)
		import string
		L = string.join(L, "  \n")
		return "TableStyle(\n%s\n) # end TableStyle" % L
	def getCommands(self):
		return self._cmds

TableStyleType = type(TableStyle())
_SeqTypes = (TupleType, ListType)

def _rowLen(x):
	return type(x) not in _SeqTypes and 1 or len(x)


class Table(Flowable):
	def __init__(self, data, colWidths=None, rowHeights=None, style=None,
				repeatRows=0, repeatCols=0, splitByRow=1, emptyTableAction=None):
		#print "colWidths", colWidths
		self.hAlign = 'CENTER'
		self.vAlign = 'MIDDLE'
		if type(data) not in _SeqTypes:
			raise ValueError, "%s invalid data type" % self.identity()
		self._nrows = nrows = len(data)
		if nrows: self._ncols = ncols = max(map(_rowLen,data))
		elif colWidths: ncols = len(colWidths)
		else: ncols = 0
		if not emptyTableAction: emptyTableAction = rl_config.emptyTableAction
		if not (nrows and ncols):
			if emptyTableAction=='error':
				raise ValueError, "%s must have at least a row and column" % self.identity()
			elif emptyTableAction=='indicate':
				self.__class__ = Preformatted
				global _emptyTableStyle
				if '_emptyTableStyle' not in globals().keys():
					_emptyTableStyle = ParagraphStyle('_emptyTableStyle')
					_emptyTableStyle.textColor = colors.red
					_emptyTableStyle.backColor = colors.yellow
				Preformatted.__init__(self,'Table(%d,%d)' % (nrows,ncols), _emptyTableStyle)
			elif emptyTableAction=='ignore':
				self.__class__ = Spacer
				Spacer.__init__(self,0,0)
			else:
				raise ValueError, '%s bad emptyTableAction: "%s"' % (self.identity(),emptyTableAction)
			return

		if colWidths is None: colWidths = ncols*[None]
		elif len(colWidths) != ncols:
			raise ValueError, "%s data error - %d columns in data but %d in grid" % (self.identity(),ncols, len(colWidths))
		if rowHeights is None: rowHeights = nrows*[None]
		elif len(rowHeights) != nrows:
			raise ValueError, "%s data error - %d rows in data but %d in grid" % (self.identity(),nrows, len(rowHeights))
		for i in range(nrows):
			if len(data[i]) != ncols:
				raise ValueError, "%s not enough data points in row %d!" % (self.identity(),i)
		self._rowHeights = self._argH = rowHeights
		self._colWidths = self._argW = colWidths
		self._cellvalues = data
##		dflt = CellStyle('<default>')
##
##		self._cellStyles = [None]*nrows
##		for i in range(nrows):
##			self._cellStyles[i] = [dflt]*ncols
		# make unique cell styles for each entry
		cellrows = []
		for i in range(nrows):
			cellcols = []
			for j in range(ncols):
				cellcols.append(CellStyle(`(i,j)`))
			cellrows.append(cellcols)
		self._cellStyles = cellrows

		self._bkgrndcmds = []
		self._linecmds = []
		self.repeatRows = repeatRows
		self.repeatCols = repeatCols
		self.splitByRow = splitByRow

		if style:
			self.setStyle(style)
	def __repr__(self):
		"incomplete, but better than nothing"
		r = self._rowHeights
		c = self._colWidths
		cv = self._cellvalues
		import pprint, string
		cv = pprint.pformat(cv)
		cv = string.replace(cv, "\n", "\n  ")
		return "Table(\n rowHeights=%s,\n colWidths=%s,\n%s\n) # end table" % (r,c,cv)

	def identity(self, maxLen=30):
		'''Identify our selves as well as possible'''
		vx = None
		nr = self._nrows
		if not hasattr(self,'_ncols'):
			nc = 'unknown'
		else:
			nc = self._ncols
			cv = self._cellvalues
			b = 0
			for i in xrange(nr):
				for j in xrange(nc):
					v = cv[i][j]
					t = type(v)
					if t in _SeqTypes or isinstance(v,Flowable):
						if not t in _SeqTypes: v = (v,)
						r = ''
						for vij in v:
							r = vij.identity(maxLen)
							if r and r[-4:]!='>...':
								break
						if r and r[-4:]!='>...':
							ix, jx, vx, b = i, j, r, 1
					else:
						v = v is None and '' or str(v)
						ix, jx, vx = i, j, v
						b = (vx and t is StringType) and 1 or 0
						if maxLen: vx = vx[:maxLen]
					if b: break
				if b: break
		if vx:
			vx = ' with cell(%d,%d) containing\n%s' % (ix,jx,repr(vx))
		else:
			vx = '...'

		return "<%s at %d %d rows x %s cols>%s" % (self.__class__.__name__, id(self), nr, nc, vx)

	def _listCellGeom(self, V,w,s,W=None,H=None):
		aW = w-s.leftPadding-s.rightPadding
		t = 0
		w = 0
		canv = getattr(self,'canv',None)
		for v in V:
			vw, vh = v.wrapOn(canv,aW, 72000)
			if W is not None: W.append(vw)
			if H is not None: H.append(vh)
			w = max(w,vw)
			t = t + vh + v.getSpaceBefore()+v.getSpaceAfter()
		return w, t - V[0].getSpaceBefore()-V[-1].getSpaceAfter() 

	def _calc_width(self):

		W = self._argW

		canv = getattr(self,'canv',None)
		saved = None

		if None in W:
			W = W[:]
			self._colWidths = W
			while None in W:
				j = W.index(None)
				f = lambda x,j=j: operator.getitem(x,j)
				V = map(f,self._cellvalues)
				S = map(f,self._cellStyles)
				w = 0
				i = 0
				for v, s in map(None, V, S):
					i = i + 1
					t = type(v)
					if t in _SeqTypes or isinstance(v,Flowable):
						raise ValueError, "Flowable %s in cell(%d,%d) can't have auto width\n%s" % (v.identity(30),i,j,self.identity(30))
					elif t is not StringType: v = v is None and '' or str(v)
					v = string.split(v, "\n")
					t = s.leftPadding+s.rightPadding + max(map(lambda a, b=s.fontname,
								c=s.fontsize,d=pdfmetrics.stringWidth: d(a,b,c), v))
					if t>w: w = t	#record a new maximum
				W[j] = w

		width = 0
		self._colpositions = [0]		#index -1 is right side boundary; we skip when processing cells
		for w in W:
			#print w, width
			width = width + w
			self._colpositions.append(width)
		#print "final width", width
		
		self._width = width

	def _calc_height(self):

		H = self._argH
		W = self._argW

		canv = getattr(self,'canv',None)
		saved = None

		if None in H:
			if canv: saved = canv._fontname, canv._fontsize, canv._leading
			H = H[:]	#make a copy as we'll change it
			self._rowHeights = H
			while None in H:
				i = H.index(None)
				V = self._cellvalues[i] # values for row i
				S = self._cellStyles[i] # styles for row i
				h = 0
				j = 0
				for v, s, w in map(None, V, S, W): # value, style, width (lengths must match)
					j = j + 1
					t = type(v)
					if t in _SeqTypes or isinstance(v,Flowable):
						if not t in _SeqTypes: v = (v,)
						if w is None:
							raise ValueError, "Flowable %s in cell(%d,%d) can't have auto width in\n%s" % (v[0].identity(30),i,j,self.identity(30))
						if canv: canv._fontname, canv._fontsize, canv._leading = s.fontname, s.fontsize, s.leading or 1.2*s.fontsize
						dW,t = self._listCellGeom(v,w,s)
						if canv: canv._fontname, canv._fontsize, canv._leading = saved
						#print "leftpadding, rightpadding", s.leftPadding, s.rightPadding
						dW = dW + s.leftPadding + s.rightPadding
						if not rl_config.allowTableBoundsErrors and dW>w:
							raise "LayoutError", "Flowable %s (%sx%s points) too wide for cell(%d,%d) (%sx* points) in\n%s" % (v[0].identity(30),fp_str(dW),fp_str(t),i,j, fp_str(w), self.identity(30))
					else:
						if t is not StringType:
							v = v is None and '' or str(v)
						v = string.split(v, "\n")
						t = s.leading*len(v)
					t = t+s.bottomPadding+s.topPadding
					if t>h: h = t	#record a new maximum
				H[i] = h

		height = self._height = reduce(operator.add, H, 0)
		#print "height, H", height, H
		self._rowpositions = [height]	 # index 0 is actually topline; we skip when processing cells
		for h in H:
			height = height - h
			self._rowpositions.append(height)
		assert abs(height)<1e-8, 'Internal height error'

	def _calc(self):
		if hasattr(self,'_width'): return

		# calculate the full table height
		self._calc_height()

		# if the width has already been calculated, don't calculate again
		# there's surely a better, more pythonic way to short circuit this FIXME FIXME
		if hasattr(self,'_width_calculated_once'): return
		self._width_calculated_once = 1

		# calculate the full table width
		self._calc_width()

	def setStyle(self, tblstyle):
		if type(tblstyle) is not TableStyleType:
			tblstyle = TableStyle(tblstyle)
		for cmd in tblstyle.getCommands():
			self._addCommand(cmd)
		for k,v in tblstyle._opts.items():
			setattr(self,k,v)

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
		# use round caps
		self.canv.setLineCap(1)
		for op, (sc, sr), (ec, er), weight, color in self._linecmds:
			if sc < 0: sc = sc + self._ncols
			if ec < 0: ec = ec + self._ncols
			if sr < 0: sr = sr + self._nrows
			if er < 0: er = er + self._nrows
			getattr(self,_LineOpMap.get(op, '_drawUnknown' ))( (sc, sr), (ec, er), weight, color)
		self._curcolor = None

	def _drawUnknown(self,	(sc, sr), (ec, er), weight, color):
		raise ValueError, "Unknown line command '%s'" % op

	def _drawGrid(self,	(sc, sr), (ec, er), weight, color):
		self._drawBox( (sc, sr), (ec, er), weight, color)
		self._drawInnerGrid( (sc, sr), (ec, er), weight, color)

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
		ecp = self._colpositions[sc:ec+2]
		rp = self._rowpositions[sr:er+1]
		if len(ecp)<=1 or len(rp)<1: return
		self._prepLine(weight, color)
		scp = ecp[0]
		ecp = ecp[-1]
		for rowpos in rp:
			self.canv.line(scp, rowpos, ecp, rowpos)

	def _drawHLinesB(self, (sc, sr), (ec, er), weight, color):
		self._drawHLines((sc, sr+1), (ec, er+1), weight, color)

	def _drawVLines(self, (sc, sr), (ec, er), weight, color):
		erp = self._rowpositions[sr:er+2]
		cp  = self._colpositions[sc:ec+1]
		if len(erp)<=1 or len(cp)<1: return
		self._prepLine(weight, color)
		srp = erp[0]
		erp = erp[-1]
		for colpos in cp:
			self.canv.line(colpos, srp, colpos, erp)

	def _drawVLinesA(self, (sc, sr), (ec, er), weight, color):
		self._drawVLines((sc+1, sr), (ec+1, er), weight, color)

	def wrap(self, availWidth, availHeight):
		self._calc()
		#nice and easy, since they are predetermined size
		self.availWidth = availWidth
		return (self._width, self._height)

	def onSplit(self,T,byRow=1):
		'''
		This method will be called when the Table is split.
		Special purpose tables can override to do special stuff.
		'''
		pass

	def _cr_0(self,n,cmds):
		for c in cmds:
			c = tuple(c)
			(sc,sr), (ec,er) = c[1:3]
			if sr>=n: continue
			if er>=n: er = n-1
			self._addCommand((c[0],)+((sc, sr), (ec, er))+c[3:])

	def _cr_1_1(self,n,repeatRows, cmds):
		for c in cmds:
			c = tuple(c)
			(sc,sr), (ec,er) = c[1:3]
			if sr>=0 and sr>=repeatRows and sr<n and er>=0 and er<n: continue
			if sr>=repeatRows and sr<n: sr=repeatRows
			elif sr>=repeatRows and sr>=n: sr=sr+repeatRows-n
			if er>=repeatRows and er<n: er=repeatRows
			elif er>=repeatRows and er>=n: er=er+repeatRows-n
			self._addCommand((c[0],)+((sc, sr), (ec, er))+c[3:])

	def _cr_1_0(self,n,cmds):
		for c in cmds:
			c = tuple(c)
			(sc,sr), (ec,er) = c[1:3]
			if er>=0 and er<n: continue
			if sr>=0 and sr<n: sr=0
			if sr>=n: sr = sr-n
			if er>=n: er = er-n
			self._addCommand((c[0],)+((sc, sr), (ec, er))+c[3:])

	def _splitRows(self,availHeight):
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
		#R0 = Table( data[:n], self._argW, self._argH[:n],
		R0 = Table( data[:n], self._colWidths, self._argH[:n],
				repeatRows=repeatRows, repeatCols=repeatCols,
				splitByRow=splitByRow)

		#copy the styles and commands
		R0._cellStyles = self._cellStyles[:n]

		A = []
		# hack up the line commands
		for op, (sc, sr), (ec, er), weight, color in self._linecmds:
			if sc < 0: sc = sc + self._ncols
			if ec < 0: ec = ec + self._ncols
			if sr < 0: sr = sr + self._nrows
			if er < 0: er = er + self._nrows

			if op in ('BOX','OUTLINE','GRID'):
				if sr<n and er>=n:
					# we have to split the BOX
					A.append(('LINEABOVE',(sc,sr), (ec,sr), weight, color))
					A.append(('LINEBEFORE',(sc,sr), (sc,er), weight, color))
					A.append(('LINEAFTER',(ec,sr), (ec,er), weight, color))
					A.append(('LINEBELOW',(sc,er), (ec,er), weight, color))
					if op=='GRID':
						A.append(('LINEBELOW',(sc,n-1), (ec,n-1), weight, color))
						A.append(('LINEABOVE',(sc,n), (ec,n), weight, color))
						A.append(('INNERGRID',(sc,sr), (ec,er), weight, color))
				else:
					A.append((op,(sc,sr), (ec,er), weight, color))
			elif op in ('INNERGRID','LINEABOVE'):
				if sr<n and er>=n:
					A.append(('LINEBELOW',(sc,n-1), (ec,n-1), weight, color))
					A.append(('LINEABOVE',(sc,n), (ec,n), weight, color))
				A.append((op,(sc,sr), (ec,er), weight, color))
			elif op == 'LINEBELOW':
				if sr<n and er>=(n-1):
					A.append(('LINEABOVE',(sc,n), (ec,n), weight, color))
				A.append((op,(sc,sr), (ec,er), weight, color))
			elif op == 'LINEABOVE':
				if sr<=n and er>=n:
					A.append(('LINEBELOW',(sc,n-1), (ec,n-1), weight, color))
				A.append((op,(sc,sr), (ec,er), weight, color))
			else:
				A.append((op,(sc,sr), (ec,er), weight, color))

		R0._cr_0(n,A)
		R0._cr_0(n,self._bkgrndcmds)

		if repeatRows:
			#R1 = Table(data[:repeatRows]+data[n:],self._argW, 
			R1 = Table(data[:repeatRows]+data[n:],self._colWidths, 
					self._argH[:repeatRows]+self._argH[n:],
					repeatRows=repeatRows, repeatCols=repeatCols,
					splitByRow=splitByRow)
			R1._cellStyles = self._cellStyles[:repeatRows]+self._cellStyles[n:]
			R1._cr_1_1(n,repeatRows,A)
			R1._cr_1_1(n,repeatRows,self._bkgrndcmds)
		else:
			#R1 = Table(data[n:], self._argW, self._argH[n:],
			R1 = Table(data[n:], self._colWidths, self._argH[n:],
					repeatRows=repeatRows, repeatCols=repeatCols,
					splitByRow=splitByRow)
			R1._cellStyles = self._cellStyles[n:]
			R1._cr_1_0(n,A)
			R1._cr_1_0(n,self._bkgrndcmds)


		R0.hAlign = R1.hAlign = self.hAlign
		R0.vAlign = R1.vAlign = self.vAlign
		self.onSplit(R0)
		self.onSplit(R1)
		return [R0,R1]

	def split(self, availWidth, availHeight):
		self._calc()
		if self.splitByRow:
			if self._width>availWidth: return []
			return self._splitRows(availHeight)
		else:
			raise NotImplementedError

	def draw(self):
		self._curweight = self._curcolor = self._curcellstyle = None
		self._drawBkgrnd()
		self._drawLines()
		for row, rowstyle, rowpos, rowheight in map(None, self._cellvalues, self._cellStyles, self._rowpositions[1:], self._rowHeights):
			for cellval, cellstyle, colpos, colwidth in map(None, row, rowstyle, self._colpositions[:-1], self._colWidths):
				self._drawCell(cellval, cellstyle, (colpos, rowpos), (colwidth, rowheight))

	def _drawBkgrnd(self):
		nrows = self._nrows
		ncols = self._ncols
		for cmd, (sc, sr), (ec, er), arg in self._bkgrndcmds:
			if sc < 0: sc = sc + ncols
			if ec < 0: ec = ec + ncols
			if sr < 0: sr = sr + nrows
			if er < 0: er = er + nrows
			x0 = self._colpositions[sc]
			y0 = self._rowpositions[sr]
			x1 = self._colpositions[min(ec+1,ncols)]
			y1 = self._rowpositions[min(er+1,nrows)]
			w, h = x1-x0, y1-y0
			canv = self.canv
			if callable(arg):
				apply(arg,(self,canv, x0, y0, w, h))
			else:
				canv.setFillColor(colors.toColor(arg))
				canv.rect(x0, y0, w, h, stroke=0,fill=1)

	def _drawCell(self, cellval, cellstyle, (colpos, rowpos), (colwidth, rowheight)):
		if self._curcellstyle is not cellstyle:
			cur = self._curcellstyle
			if cur is None or cellstyle.color != cur.color:
				self.canv.setFillColor(cellstyle.color)
			if cur is None or cellstyle.leading != cur.leading or cellstyle.fontname != cur.fontname or cellstyle.fontsize != cur.fontsize:
				self.canv.setFont(cellstyle.fontname, cellstyle.fontsize, cellstyle.leading)
			self._curcellstyle = cellstyle

		just = cellstyle.alignment
		valign = cellstyle.valign
		n = type(cellval)
		if n in _SeqTypes or isinstance(cellval,Flowable):
			if not n in _SeqTypes: cellval = (cellval,)
			# we assume it's a list of Flowables
			W = []
			H = []
			w, h = self._listCellGeom(cellval,colwidth,cellstyle,W=W, H=H)
			if valign=='TOP':
				y = rowpos + rowheight - cellstyle.topPadding
			elif valign=='BOTTOM':
				y = rowpos+cellstyle.bottomPadding + h
			else:
				y = rowpos+(rowheight+cellstyle.bottomPadding-cellstyle.topPadding+h)/2.0
			y = y+cellval[0].getSpaceBefore()
			for v, w, h in map(None,cellval,W,H):
				if just=='LEFT': x = colpos+cellstyle.leftPadding
				elif just=='RIGHT': x = colpos+colwidth-cellstyle.rightPadding - w
				elif just in ('CENTRE', 'CENTER'):
					x = colpos+(colwidth+cellstyle.leftPadding-cellstyle.rightPadding-w)/2.0
				else:
					raise ValueError, 'Invalid justification %s' % just
				y = y - v.getSpaceBefore()
				y = y - h
				v.drawOn(self.canv,x,y)
				y = y - v.getSpaceAfter()
		else:
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
			if n is StringType: val = cellval
			else: val = str(cellval)
			vals = string.split(val, "\n")
			n = len(vals)
			leading = cellstyle.leading
			fontsize = cellstyle.fontsize
			if valign=='BOTTOM':
				y = rowpos + cellstyle.bottomPadding+n*leading-fontsize
			elif valign=='TOP':
				y = rowpos + rowheight - cellstyle.topPadding - fontsize
			elif valign=='MIDDLE':
				y = rowpos + (cellstyle.bottomPadding + rowheight-cellstyle.topPadding+(n-1)*leading)/2.0
			else:
				raise ValueError, "Bad valign: '%s'" % str(valign)

			for v in vals:
				draw(x, y, v)
				y = y-leading
		
# for text,
#	drawCentredString(self, x, y, text) where x is center
#	drawRightString(self, x, y, text) where x is right
#	drawString(self, x, y, text) where x is left

_LineOpMap = {	'GRID':'_drawGrid',
				'BOX':'_drawBox',
				'OUTLINE':'_drawBox',
				'INNERGRID':'_drawInnerGrid',
				'LINEBELOW':'_drawHLinesB',
				'LINEABOVE':'_drawHLines',
				'LINEBEFORE':'_drawVLines',
				'LINEAFTER':'_drawVLinesA', }

LINECOMMANDS = _LineOpMap.keys()

def _isLineCommand(cmd):
	return cmd[0] in LINECOMMANDS

def _setCellStyle(cellStyles, i, j, op, values):
	#new = CellStyle('<%d, %d>' % (i,j), cellStyles[i][j])
	#cellStyles[i][j] = new
	## modify in place!!!
	new = cellStyles[i][j]
	if op == 'FONT':
		n = len(values)
		new.fontname = values[0]
		if n>1:
			new.fontsize = values[1]
			if n>2:
				new.leading = values[2]
			else:
				new.leading = new.fontsize*1.2
	elif op in ('FONTNAME', 'FACE'):
		new.fontname = values[0]
	elif op in ('SIZE', 'FONTSIZE'):
		new.fontsize = values[0]
	elif op == 'LEADING':
		new.leading = values[0]
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
	t = Table(data, colwidths, rowheights)
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
	t = Table(data, colwidths, rowheights)
	t.setStyle(GRID_STYLE)
	lst.append(PageBreak())
	lst.append(Paragraph("This is GRID_STYLE\n", styleSheet['BodyText']))
	lst.append(t)
	
	t = Table(data, colwidths, rowheights)
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
	
	t = Table(data, colwidths, rowheights)
	t.setStyle(LABELED_GRID_STYLE)
	lst.append(Paragraph("This is LABELED_GRID_STYLE\n", styleSheet['BodyText']))
	lst.append(t)
	t = Table(data2, colwidths, rowheights2)
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
	
	t = Table(data, colwidths, rowheights)
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
	
	t = Table(data, colwidths, rowheights)
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
   
	t = Table(data, colwidths, rowheights)
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
	t = Table(data, c, [None]+list(rowheights[1:]))
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
	XY	=	[['X00y', 'X01y', 'X02y', 'X03y', 'X04y'],
			['X10y', 'X11y', 'X12y', 'X13y', 'X14y'],
			['X20y', 'X21y', 'X22y', 'X23y', 'X24y'],
			['X30y', 'X31y', 'X32y', 'X33y', 'X34y']]
	t=Table(XY, 5*[0.6*inch], 4*[0.6*inch])
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
	t = Table(data)
	t.setStyle([
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ])
	lst.append(t)
	t = Table([	('Attribute', 'Synonyms'),
				('alignment', 'align, alignment'),
				('bulletColor', 'bulletcolor, bcolor'),
				('bulletFontName', 'bfont, bulletfontname'),
				('bulletFontSize', 'bfontsize, bulletfontsize'),
				('bulletIndent', 'bindent, bulletindent'),
				('firstLineIndent', 'findent, firstlineindent'),
				('fontName', 'face, fontname, font'),
				('fontSize', 'size, fontsize'),
				('leading', 'leading'),
				('leftIndent', 'leftindent, lindent'),
				('rightIndent', 'rightindent, rindent'),
				('spaceAfter', 'spaceafter, spacea'),
				('spaceBefore', 'spacebefore, spaceb'),
				('textColor', 'fg, textcolor, color')])
	t.repeatRows = 1
	t.setStyle([
				('FONT',(0,0),(-1,1),'Times-Bold',10,12),
				('FONT',(0,1),(-1,-1),'Courier',8,8),
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
				('BOX', (0,0), (-1,-1), 0.25, colors.black),
				('BACKGROUND', (0, 0), (-1, 0), colors.green),
				('BACKGROUND', (0, 1), (-1, -1), colors.pink),
				('ALIGN', (0, 0), (-1, 0), 'CENTER'),
				('ALIGN', (0, 1), (0, -1), 'LEFT'),
				('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
				('FONT', (0, 0), (-1, 0), 'Times-Bold', 12),
				('ALIGN', (1, 1), (1, -1), 'CENTER'),
				])
	lst.append(t)
	lst.append(Table(XY,
			style=[	('FONT',(0,0),(-1,-1),'Times-Roman', 5,6),
					('GRID', (0,0), (-1,-1), 0.25, colors.blue),]))
	lst.append(Table(XY,
			style=[	('FONT',(0,0),(-1,-1),'Times-Roman', 10,12),
					('GRID', (0,0), (-1,-1), 0.25, colors.black),]))
	lst.append(Table(XY,
			style=[	('FONT',(0,0),(-1,-1),'Times-Roman', 20,24),
					('GRID', (0,0), (-1,-1), 0.25, colors.red),]))
	lst.append(PageBreak())
	data=  [['00', '01', '02', '03', '04'],
			['10', '11', '12', '13', '14'],
			['20', '21', '22', '23', '24'],
			['30', '31', '32', '33', '34']]
	t=Table(data,style=[
					('GRID',(0,0),(-1,-1),0.5,colors.grey),
					('GRID',(1,1),(-2,-2),1,colors.green),
					('BOX',(0,0),(1,-1),2,colors.red),
					('BOX',(0,0),(-1,-1),2,colors.black),
					('LINEABOVE',(1,2),(-2,2),1,colors.blue),
					('LINEBEFORE',(2,1),(2,-2),1,colors.pink),
					('BACKGROUND', (0, 0), (0, 1), colors.pink),
					('BACKGROUND', (1, 1), (1, 2), colors.lavender),
					('BACKGROUND', (2, 2), (2, 3), colors.orange),
					])
	lst.append(t)
	lst.append(Spacer(0,6))
	for s in t.split(4*inch,30):
		lst.append(s)
		lst.append(Spacer(0,6))
	lst.append(Spacer(0,6))
	for s in t.split(4*inch,36):
		lst.append(s)
		lst.append(Spacer(0,6))

	lst.append(Spacer(0,6))
	for s in t.split(4*inch,56):
		lst.append(s)
		lst.append(Spacer(0,6))

	import os, reportlab.platypus
	I = Image(os.path.join(os.path.dirname(reportlab.platypus.__file__),'..','tools','pythonpoint','demos','leftlogo.gif'))
	I.drawHeight = 1.25*inch*I.drawHeight / I.drawWidth
	I.drawWidth = 1.25*inch
	#I.drawWidth = 9.25*inch #uncomment to see better messaging
	P = Paragraph("<para align=center spaceb=3>The <b>ReportLab Left <font color=red>Logo</font></b> Image</para>", styleSheet["BodyText"])
	data=  [['A', 'B', 'C', Paragraph("<b>A pa<font color=red>r</font>a<i>graph</i></b><super><font color=yellow>1</font></super>",styleSheet["BodyText"]), 'D'],
			['00', '01', '02', [I,P], '04'],
			['10', '11', '12', [I,P], '14'],
			['20', '21', '22', '23', '24'],
			['30', '31', '32', '33', '34']]

	t=Table(data,style=[('GRID',(1,1),(-2,-2),1,colors.green),
					('BOX',(0,0),(1,-1),2,colors.red),
					('LINEABOVE',(1,2),(-2,2),1,colors.blue),
					('LINEBEFORE',(2,1),(2,-2),1,colors.pink),
					('BACKGROUND', (0, 0), (0, 1), colors.pink),
					('BACKGROUND', (1, 1), (1, 2), colors.lavender),
					('BACKGROUND', (2, 2), (2, 3), colors.orange),
					('BOX',(0,0),(-1,-1),2,colors.black),
					('GRID',(0,0),(-1,-1),0.5,colors.black),
					('VALIGN',(3,0),(3,0),'BOTTOM'),
					('BACKGROUND',(3,0),(3,0),colors.limegreen),
					('BACKGROUND',(3,1),(3,1),colors.khaki),
					('ALIGN',(3,1),(3,1),'CENTER'),
					('BACKGROUND',(3,2),(3,2),colors.beige),
					('ALIGN',(3,2),(3,2),'LEFT'),
					])

	t._argW[3]=1.5*inch
	lst.append(t)

	SimpleDocTemplate('tables.pdf', showBoundary=1).build(lst)

if __name__ == '__main__':
	test()
