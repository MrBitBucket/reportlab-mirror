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
#	$Log: flowables.py,v $
#	Revision 1.3  2000/06/13 13:03:31  aaron_watters
#	more documentation changes
#
#	Revision 1.2  2000/06/01 16:27:56  rgbecker
#	pageSize is wrong at present
#	
#	Revision 1.1  2000/06/01 15:23:06  rgbecker
#	Platypus re-organisation
#	
#	
__version__=''' $Id: flowables.py,v 1.3 2000/06/13 13:03:31 aaron_watters Exp $ '''
__doc__="""
A flowable is a "floating element" in a document whose exact position is determined by the
other elements that precede it, such as a paragraph, a diagram interspersed between paragraphs,
a section header, etcetera.  Examples of non-flowables include page numbering annotations,
headers, footers, fixed diagrams or logos, among others.

Flowables are defined here as objects which know how to determine their size and which
can draw themselves onto a page with respect to a relative "origin" position determined
at a higher level.  Some Flowables also know how to "split themselves".  For example a
long paragraph might split itself between one page and the next.

The "text" of a document usually consists mainly of a sequence of flowables which
flow into a document from top to bottom (with column and page breaks controlled by
higher level components).
"""

# 200-10-13 gmcm
#	packagizing
#	rewrote grid stuff - now in tables.py
import os
import string
from copy import deepcopy


from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import red
from reportlab.pdfbase import pdfutils

from reportlab.lib.pagesizes import DEFAULT_PAGE_SIZE
PAGE_HEIGHT = DEFAULT_PAGE_SIZE[1]

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

	def drawOn(self, canvas, x, y):
		"Tell it to draw itself on the canvas.	Do not override"
		self.canv = canvas
		self.canv.saveState()
		self.canv.translate(x, y)

		self.draw()   #this is the bit you overload

		self.canv.restoreState()
		del self.canv


	def wrap(self, availWidth, availHeight):
		"""This will be called by the enclosing frame before objects
		are asked their size, drawn or whatever.  It returns the
		size actually used."""
		return (self.width, self.height)

	def split(self, availWidth, availheight):
		"""This will be called by more sophisticated frames when
		wrap fails. Stupid flowables should return []. Clever flowables
		should split themselves and return a list of flowables"""
		return []

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

class XBox(Flowable):
	"""Example flowable - a box with an x through it and a caption.
	This has a known size, so does not need to respond to wrap()."""
	def __init__(self, width, height, text = 'A Box'):
		Flowable.__init__(self)
		self.width = width
		self.height = height
		self.text = text

	def draw(self):
		self.canv.rect(0, 0, self.width, self.height)
		self.canv.line(0, 0, self.width, self.height)
		self.canv.line(0, self.height, self.width, 0)

		#centre the text
		self.canv.setFont('Times-Roman',12)
		self.canv.drawCentredString(0.5*self.width, 0.5*self.height, self.text)

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

		#tidy up text - carefully, it is probably code.  If people want to
		#indent code within a source script, you can supply an arg to dedent
		#and it will chop off that many character, otherwise it leaves
		#left edge intact.

		templines = string.split(text, '\n')
		self.lines = []
		for line in templines:
			line = string.rstrip(line[dedent:])
			self.lines.append(line)
		#don't want the first or last to be empty
		while string.strip(self.lines[0]) == '':
			self.lines = self.lines[1:]
		while string.strip(self.lines[-1]) == '':
			self.lines = self.lines[:-1]

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
		tx.setFont(self.style.fontName,
				   self.style.fontSize,
				   self.style.leading)

		for text in self.lines:
			tx.textLine(text)
		self.canv.drawText(tx)

class Image(Flowable):
	"""an image (digital picture).  Formats supported by PIL (the Python Imaging Library
	   are supported.  At the present time images as flowables are always centered horozontally
	   in the frame.
	"""
	def __init__(self, filename, width=None, height=None):
		"""If size to draw at not specified, get it from the image."""
		import Image  #this will raise an error if they do not have PIL.
		self.filename = filename
		# if it is a JPEG, will be inlined within the file -
		# but we still need to know its size now
		if os.path.splitext(filename)[1] in ['.jpg', '.JPG', '.jpeg', '.JPEG']:
			info = pdfutils.readJPEGInfo(open(filename, 'rb'))
			self.imageWidth = info[0]
			self.imageHeight = info[1]
		else:
			img = Image.open(filename)
			(self.imageWidth, self.imageHeight) = img.size
		if width:
			self.drawWidth = width
		else:
			self.drawWidth = self.imageWidth
		if height:
			self.drawHeight = height
		else:
			self.drawHeight = self.imageHeight

	def wrap(self, availWidth, availHeight):
		#the caller may decide it does not fit.
		self.availWidth = availWidth
		return (self.drawWidth, self.drawHeight)

	def draw(self):
		#center it
		startx = 0.5 * (self.availWidth - self.drawWidth)
		self.canv.drawInlineImage(self.filename,
								  startx,
								  0,
								  self.drawWidth,
								  self.drawHeight
								  )
class Spacer(Flowable):
	"""A spacer just takes up space and doesn't draw anything - it guarantees
	   a gap between objects."""
	def __init__(self, width, height):
		self.width = width
		self.height = height

	def wrap(self, availWidth, availHeight):
		return (self.width, self.height)

	def draw(self):
		pass

class PageBreak(Flowable):
	"""Move on to the next page in the document.
	   This works by consuming all remaining space in the frame!"""

	def wrap(self, availWidth, availHeight):
		self.width = availWidth
		self.height = availHeight
		return (availWidth,availHeight)  #step back a point

	def draw(self):
		pass

class Macro(Flowable):
	"""This is not actually drawn (i.e. it has zero height)
	but is executed when it would fit in the frame.  Allows direct
	access to the canvas through the object 'canvas'"""
	def __init__(self, command):
		self.command = command
	def wrap(self, availWidth, availHeight):
		return (0,0)
	def draw(self):
		exec self.command in globals(), {'canvas':self.canv}

#from paragraph import Paragraph
