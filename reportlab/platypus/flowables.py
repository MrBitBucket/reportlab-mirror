#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/platypus/flowables.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/platypus/flowables.py,v 1.28 2002/01/18 13:31:39 rgbecker Exp $
__version__=''' $Id: flowables.py,v 1.28 2002/01/18 13:31:39 rgbecker Exp $ '''
__doc__="""
A flowable is a "floating element" in a document whose exact position is determined by the
other elements that precede it, such as a paragraph, a diagram interspersed between paragraphs,
a section header, etcetera.  Examples of non-flowables include page numbering annotations,
headers, footers, fixed diagrams or logos, among others.

Flowables are defined here as objects which know how to determine their size and which
can draw themselves onto a page with respect to a relative "origin" position determined
at a higher level. The object's draw() method should assume that (0,0) corresponds to the
bottom left corner of the enclosing rectangle that will contain the object. The attributes
vAlign and hAlign may be used by 'packers' as hints as to how the object should be placed.

Some Flowables also know how to "split themselves".  For example a
long paragraph might split itself between one page and the next.

Packers should set the canv attribute during wrap, split & draw operations to allow
the flowable to work out sizes etc in the proper context.

The "text" of a document usually consists mainly of a sequence of flowables which
flow into a document from top to bottom (with column and page breaks controlled by
higher level components).
"""
import os
import string
from copy import deepcopy
from types import ListType, TupleType, StringType

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import red
from reportlab.pdfbase import pdfutils

from reportlab.rl_config import defaultPageSize
PAGE_HEIGHT = defaultPageSize[1]

#############################################################
#	Flowable Objects - a base class and a few examples.
#	One is just a box to get some metrics.	We also have
#	a paragraph, an image and a special 'page break'
#	object which fills the space.
#############################################################
class Flowable:
	"""Abstract base class for things to be drawn.	Key concepts:
	1. It knows its size
	2. It draws in its own coordinate system (this requires the
		base API to provide a translate() function.
	"""
	def __init__(self):
		self.width = 0
		self.height = 0
		self.wrapped = 0

		#these are hints to packers/frames as to how the floable should be positioned
		self.hAlign = 'LEFT'	#CENTER/CENTRE or RIGHT
		self.vAlign = 'BOTTOM'	#MIDDLE or TOP


	def _drawOn(self,canv):
		'''ensure canv is set on and then draw'''
		self.canv = canv
		self.draw()#this is the bit you overload
		del self.canv

	def drawOn(self, canvas, x, y, _sW=0):
		"Tell it to draw itself on the canvas.	Do not override"
		if _sW and hasattr(self,'hAlign'):
			a = self.hAlign
			if a in ['CENTER','CENTRE']:
				x = x + 0.5*_sW
			elif a == 'RIGHT':
				x = x + _sW
			elif a != 'LEFT':
				raise ValueError, "Bad hAlign value "+str(a)
		canvas.saveState()
		canvas.translate(x, y)
		self._drawOn(canvas)
		canvas.restoreState()

	def wrapOn(self, canv, aW, aH):
		'''intended for use by packers allows setting the canvas on
		during the actual wrap'''
		self.canv = canv
		w, h = self.wrap(aW,aH)
		del self.canv
		return w, h

	def wrap(self, availWidth, availHeight):
		"""This will be called by the enclosing frame before objects
		are asked their size, drawn or whatever.  It returns the
		size actually used."""
		return (self.width, self.height)

	def minWidth(self):
		"""This should return the minimum required width"""
		return getattr(self,'_minWidth',self.width)

	def splitOn(self, canv, aW, aH):
		'''intended for use by packers allows setting the canvas on
		during the actual split'''
		self.canv = canv
		S = self.split(aW,aH)
		del self.canv
		return S

	def split(self, availWidth, availheight):
		"""This will be called by more sophisticated frames when
		wrap fails. Stupid flowables should return []. Clever flowables
		should split themselves and return a list of flowables"""
		return []

	def getKeepWithNext(self):
		"""returns boolean determining whether the next flowabel should stay with this one"""
		if hasattr(self,'keepWithNext'): return self.keepWithNext
		elif hasattr(self,'style') and hasattr(self.style,'keepWithNext'): return self.style.keepWithNext
		else: return 0

	def getSpaceAfter(self):
		"""returns how much space should follow this item if another item follows on the same page."""
		if hasattr(self,'spaceAfter'): return self.spaceAfter
		elif hasattr(self,'style') and hasattr(self.style,'spaceAfter'): return self.style.spaceAfter
		else: return 0

	def getSpaceBefore(self):
		"""returns how much space should precede this item if another item precedess on the same page."""
		if hasattr(self,'spaceBefore'): return self.spaceBefore
		elif hasattr(self,'style') and hasattr(self.style,'spaceBefore'): return self.style.spaceBefore
		else: return 0

	def isIndexing(self):
		"""Hook for IndexingFlowables - things which have cross references"""
		return 0

	def identity(self, maxLen=None):
		'''
		This method should attempt to return a string that can be used to identify
		a particular flowable uniquely. The result can then be used for debugging
		and or error printouts
		'''
		if hasattr(self, 'getPlainText'):
			r = self.getPlainText()
		elif hasattr(self, 'text'):
			r = self.text
		else:
			r = '...'
		if r and maxLen:
			r = r[:maxLen]
		return "<%s at %d>%s" % (self.__class__.__name__, id(self), r)

class XBox(Flowable):
	"""Example flowable - a box with an x through it and a caption.
	This has a known size, so does not need to respond to wrap()."""
	def __init__(self, width, height, text = 'A Box'):
		Flowable.__init__(self)
		self.width = width
		self.height = height
		self.text = text

	def __repr__(self):
		return "XBox(w=%s, h=%s, t=%s)" % (self.width, self.height, self.text)

	def draw(self):
		self.canv.rect(0, 0, self.width, self.height)
		self.canv.line(0, 0, self.width, self.height)
		self.canv.line(0, self.height, self.width, 0)

		#centre the text
		self.canv.setFont('Times-Roman',12)
		self.canv.drawCentredString(0.5*self.width, 0.5*self.height, self.text)

def _trimEmptyLines(lines):
	#don't want the first or last to be empty
	while len(lines) and string.strip(lines[0]) == '':
		lines = lines[1:]
	while len(lines) and string.strip(lines[-1]) == '':
		lines = lines[:-1]
	return lines

def _dedenter(text,dedent=0):
	'''
	tidy up text - carefully, it is probably code.	If people want to
	indent code within a source script, you can supply an arg to dedent
	and it will chop off that many character, otherwise it leaves
	left edge intact.
	'''
	lines = string.split(text, '\n')
	if dedent>0:
		templines = _trimEmptyLines(lines)
		lines = []
		for line in templines:
			line = string.rstrip(line[dedent:])
			lines.append(line)
	else:
		lines = _trimEmptyLines(lines)

	return lines

class Preformatted(Flowable):
	"""This is like the HTML <PRE> tag.  
	It attempts to display text exactly as you typed it in a fixed width "typewriter" font.
	The line breaks are exactly where you put
	them, and it will not be wrapped."""
	def __init__(self, text, style, bulletText = None, dedent=0):
		"""text is the text to display. If dedent is set then common leading space
		will be chopped off the front (for example if the entire text is indented
		6 spaces or more then each line will have 6 spaces removed from the front).
		"""
		self.style = style
		self.bulletText = bulletText
		self.lines = _dedenter(text,dedent)

	def __repr__(self):
		bT = self.bulletText
		H = "Preformatted("
		if bT is not None:
			H = "Preformatted(bulletText=%s," % repr(bT)
		import string
		text = join(self.lines, "\n")
		return "%s'''\\ \n%s''')" % (H, text)

	def wrap(self, availWidth, availHeight):
		self.width = availWidth
		self.height = self.style.leading*len(self.lines)
		return (self.width, self.height)

	def split(self, availWidth, availHeight):
		#returns two Preformatted objects

		#not sure why they can be called with a negative height		
		if availHeight < self.style.leading:
			return []
		
		linesThatFit = int(availHeight * 1.0 / self.style.leading)
		
		text1 = string.join(self.lines[0:linesThatFit], '\n')
		text2 = string.join(self.lines[linesThatFit:], '\n')
		style = self.style
		if style.firstLineIndent != 0:
			style = deepcopy(style)
			style.firstLineIndent = 0
		return [Preformatted(text1, self.style), Preformatted(text2, style)]
		

	def draw(self):
		#call another method for historical reasons.  Besides, I
		#suspect I will be playing with alternate drawing routines
		#so not doing it here makes it easier to switch.

		cur_x = self.style.leftIndent
		cur_y = self.height - self.style.fontSize
		self.canv.addLiteral('%PreformattedPara')
		if self.style.textColor:
			self.canv.setFillColor(self.style.textColor)
		tx = self.canv.beginText(cur_x, cur_y)
		#set up the font etc.
		tx.setFont( self.style.fontName,
					self.style.fontSize,
					self.style.leading)

		for text in self.lines:
			tx.textLine(text)
		self.canv.drawText(tx)

class Image(Flowable):
	"""an image (digital picture).	Formats supported by PIL (the Python Imaging Library
	   are supported.  At the present time images as flowables are always centered horozontally
	   in the frame.
	"""
	def __init__(self, filename, width=None, height=None, kind='direct'):
		"""If size to draw at not specified, get it from the image."""
		from reportlab.lib.utils import PIL_Image  #this will raise an error if they do not have PIL.
		self._filename = self.filename = filename
		self.hAlign = 'CENTER'
		# if it is a JPEG, will be inlined within the file -
		# but we still need to know its size now
		if type(filename) is StringType and os.path.splitext(filename)[1] in ['.jpg', '.JPG', '.jpeg', '.JPEG']:
			info = pdfutils.readJPEGInfo(open(filename, 'rb'))
			self.imageWidth = info[0]
			self.imageHeight = info[1]
		else:
			# we have to assume this is a file like object
			self.filename = img = PIL_Image.open(filename)
			(self.imageWidth, self.imageHeight) = img.size

		if kind in ['direct','absolute']:
			self.drawWidth = width or self.imageWidth
			self.drawHeight = height or self.imageHeight
		elif kind in ['percentage','%']:
			self.drawWidth = self.imageWidth*width*0.01
			self.drawHeight = self.imageHeight*height*0.01
		elif kind in ['bound','proportional']:
			factor = min(float(width)/self.imageWidth,float(height)/self.imageHeight)
			self.drawWidth = self.imageWidth*factor
			self.drawHeight = self.imageHeight*factor

	def wrap(self, availWidth, availHeight):
		#the caller may decide it does not fit.
		return (self.drawWidth, self.drawHeight)

	def draw(self):
		#center it
		self.canv.drawInlineImage(self.filename,
								0,
								0,
								self.drawWidth,
								self.drawHeight
								)

	def identity(self,maxLen):
		r = Flowable.identity(self,maxLen)
		if r[-4:]=='>...' and type(self._filename) is StringType:
			r = "%s filename=%s>" % (r[:-4],self._filename)
		return r

class Spacer(Flowable):
	"""A spacer just takes up space and doesn't draw anything - it guarantees
	   a gap between objects."""
	def __init__(self, width, height):
		self.width = width
		self.height = height

	def __repr__(self):
		return "Spacer(%s, %s)" % (self.width, self.height)

	def wrap(self, availWidth, availHeight):
		return (self.width, self.height)

	def draw(self):
		pass

class PageBreak(Spacer):
	"""Move on to the next page in the document.
	   This works by consuming all remaining space in the frame!"""
	def __init__(self):
		pass
	
	def __repr__(self):
		return "PageBreak()"

	def wrap(self, availWidth, availHeight):
		self.width = availWidth
		self.height = availHeight
		return (availWidth,availHeight)  #step back a point

class CondPageBreak(Spacer):
	"""Throw a page if not enough vertical space"""
	def __init__(self, height):
		self.height = height
		
	def __repr__(self):
		return "CondPageBreak(%s)" %(self.height,)

	def wrap(self, availWidth, availHeight):
		if availHeight<self.height:
			return (availWidth, availHeight)
		return (0, 0)

_SeqTypes = (ListType, TupleType)

class KeepTogether(Flowable):
	def __init__(self,flowables):
		if type(flowables) not in _SeqTypes:
			self._flowables = [flowables]
		else:
			self._flowables = flowables

	def __repr__(self):
		f = self._flowables
		L = map(repr,f)
		import string
		L = "\n"+string.join(L, "\n")
		L = string.replace(L, "\n", "\n  ")
		return "KeepTogether(%s) # end KeepTogether" % L

	def wrap(self, aW, aH):
		W = 0
		H = 0
		F = self._flowables
		canv = self.canv
		for f in F:
			w,h = f.wrapOn(canv,aW,0xfffffff)
			if f is not F[0]: h = h + f.getSpaceBefore()
			if f is not F[-1]: h = h + f.getSpaceAfter()
			W = max(W,w)
			H = H+h
		self._CPage = H>aH
		return W, 0xffffff	# force a split

	def split(self, aW, aH):
		S = getattr(self,'_CPage',1) and [CondPageBreak(aH+1)] or []
		for f in self._flowables: S.append(f)
		return S

class Macro(Flowable):
	"""This is not actually drawn (i.e. it has zero height)
	but is executed when it would fit in the frame.  Allows direct
	access to the canvas through the object 'canvas'"""
	def __init__(self, command):
		self.command = command
	def __repr__(self):
		return "Macro(%s)" % repr(self.command)
	def wrap(self, availWidth, availHeight):
		return (0,0)
	def draw(self):
		exec self.command in globals(), {'canvas':self.canv}
