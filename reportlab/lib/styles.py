###############################################################################
#
#	ReportLab Public License Version 1.0
#
#   Except for the change of names the spirit and intention of this
#   license is the same as that of Python
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
#	$Log: styles.py,v $
#	Revision 1.3  2000/04/19 12:44:57  rgbecker
#	Typo fix thanks to Daniel G. Rusch
#
#	Revision 1.2  2000/04/14 11:54:56  rgbecker
#	Splitting layout.py
#	
#	Revision 1.1  2000/04/14 10:51:56  rgbecker
#	Moved out of layout.py
#	
__version__=''' $Id: styles.py,v 1.3 2000/04/19 12:44:57 rgbecker Exp $ '''

from reportlab.lib.colors import white, black
from reportlab.lib.enums import TA_LEFT

###########################################################
# This class provides an 'instance inheritance'
# mechanism for its descendants, simpler than acquisition
# but not as far-reaching
###########################################################
class PropertySet:
	defaults = {}

	def __init__(self, name, parent=None):
		self.name = name
		self.parent = parent
		self.attributes = {}

	def __setattr__(self, key, value):
		if self.defaults.has_key(key):
			self.attributes[key] = value
		else:
			self.__dict__[key] = value

	def __getattr__(self, key):
		if self.defaults.has_key(key):
			if self.attributes.has_key(key):
				found = self.attributes[key]
			elif self.parent:
				found = getattr(self.parent, key)
			else:  #take the class default
				found = self.defaults[key]
		else:
			found = self.__dict__[key]
		return found

	def __repr__(self):
		return "<%s '%s'>" % (self.__class__.__name__, self.name)

	def listAttrs(self):
		print 'name =', self.name
		print 'parent =', self.parent
		keylist = self.defaults.keys()
		keylist.sort()
		for key in keylist:
			value = self.attributes.get(key, None)
			if value:
				print '%s = %s (direct)' % (key, value)
			else: #try for inherited
				value = getattr(self.parent, key, None)
				if value:
					print '%s = %s (inherited)' % (key, value)
				else:
					value = self.defaults[key]
					print '%s = %s (class default)' % (key, value)

class ParagraphStyle(PropertySet):
	defaults = {
		'fontName':'Times-Roman',
		'fontSize':10,
		'leading':12,
		'leftIndent':0,
		'rightIndent':0,
		'firstLineIndent':0,
		'alignment':TA_LEFT,
		'spaceBefore':0,
		'spaceAfter':0,
		'bulletFontName':'Times-Roman',
		'bulletFontSize':10,
		'bulletIndent':0,
		'textColor': black
		}

class LineStyle(PropertySet):
	defaults = {
		'width':1,
		'color': black
		}
	def prepareCanvas(self, canvas):
		"""You can ask a LineStyle to set up the canvas for drawing
		the lines."""
		canvas.setLineWidth(1)
		#etc. etc.

class CellStyle(PropertySet):
	defaults = {
		'fontName':'Times-Roman',
		'fontsize':10,
		'leading':12,
		'leftPadding':6,
		'rightPadding':6,
		'topPadding':3,
		'bottomPadding':3,
		'firstLineIndent':0,
		'color':white,
		'alignment': 'LEFT',
		}

def testStyles():
	pNormal = ParagraphStyle('Normal',None)
	pNormal.fontName = 'Times-Roman'
	pNormal.fontSize = 12
	pNormal.leading = 14.4

	pNormal.listAttrs()
	print
	pPre = ParagraphStyle('Literal', pNormal)
	pPre.fontName = 'Courier'
	pPre.listAttrs()
	return pNormal, pPre

def getSampleStyleSheet():
	"""Returns a dictionary of styles to get you started.  Should be
	usable for fairly basic word processing tasks.	We should really have
	a class for StyleSheets, which can list itself and avoid the
	duplication of item names seen below."""
	stylesheet = {}

	para = ParagraphStyle('Normal', None)	#the ancestor of all
	para.fontName = 'Times-Roman'
	para.fontSize = 10
	para.leading = 12
	stylesheet['Normal'] = para

	para = ParagraphStyle('BodyText', stylesheet['Normal'])
	para.spaceBefore = 6
	stylesheet['BodyText'] = para

	para = ParagraphStyle('Italic', stylesheet['BodyText'])
	para.fontName = 'Times-Italic'
	stylesheet['Italic'] = para

	para = ParagraphStyle('Heading1', stylesheet['Normal'])
	para.fontName = 'Times-Bold'
	para.fontSize = 18
	para.spaceAfter = 6
	stylesheet['Heading1'] = para

	para = ParagraphStyle('Heading2', stylesheet['Normal'])
	para.fontName = 'Times-Bold'
	para.fontSize = 14
	para.spaceBefore = 12
	para.spaceAfter = 6
	stylesheet['Heading2'] = para

	para = ParagraphStyle('Heading3', stylesheet['Normal'])
	para.fontName = 'Times-BoldItalic'
	para.fontSize = 12
	para.spaceBefore = 12
	para.spaceAfter = 6
	stylesheet['Heading3'] = para

	para = ParagraphStyle('Bullet', stylesheet['Normal'])
	para.firstLineIndent = 36
	para.leftIndent = 36
	para.spaceBefore = 3
	stylesheet['Bullet'] = para

	para = ParagraphStyle('Definition', stylesheet['Normal'])
	#use this for definition lists
	para.firstLineIndent = 36
	para.leftIndent = 36
	para.bulletIndent = 0
	para.spaceBefore = 6
	para.bulletFontName = 'Times-BoldItalic'
	stylesheet['Definition'] = para

	para = ParagraphStyle('Code', stylesheet['Normal'])
	para.fontName = 'Courier'
	para.fontSize = 8
	para.leading = 8.8
	para.leftIndent = 36
	stylesheet['Code'] = para

	return stylesheet
