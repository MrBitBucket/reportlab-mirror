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
#	$Log: paragraph.py,v $
#	Revision 1.9  2000/05/16 16:15:16  rgbecker
#	Changes related to removal of SimpleFlowDocument
#
#	Revision 1.8  2000/05/16 15:58:27  rgbecker
#	Fixed font setting bug
#	
#	Revision 1.7  2000/05/16 14:28:55  rgbecker
#	Fixes/Changes to get testplatypus to work with new framework
#	
#	Revision 1.6  2000/05/15 13:36:11  rgbecker
#	Splitting changes
#	
#	Revision 1.5  2000/05/13 16:03:23  rgbecker
#	Fix extraspace calculation
#	
#	Revision 1.4  2000/05/12 15:13:41  rgbecker
#	Fixes to alignment handling
#	
#	Revision 1.3  2000/05/11 14:04:34  rgbecker
#	Removed usage of spaceBefore/After in wrap methods
#	
#	Revision 1.2  2000/04/19 13:14:06  rgbecker
#	Fixed repeated breaklines bug
#	
#	Revision 1.1  2000/04/14 13:21:52  rgbecker
#	Removed from layout.py
#	
__version__=''' $Id: paragraph.py,v 1.9 2000/05/16 16:15:16 rgbecker Exp $ '''
import string
import types
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus.paraparser import ParaParser, ParaFrag
from layout import Flowable
from reportlab.lib.colors import Color
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from copy import deepcopy

#our one and only parser
_parser=ParaParser()

def cleanBlockQuotedText(text):
	"""This is an internal utility which takes triple-
	quoted text form within the document and returns
	(hopefully) the paragraph the user intended originally."""
	stripped = string.strip(text)
	lines = string.split(stripped, '\n')
	trimmed_lines = map(string.lstrip, lines)
	return string.join(trimmed_lines, ' ')

def	_leftDrawParaLine( tx, offset, extraspace, words, last=0):
	tx.moveCursor(offset, 0)
	tx._textOut(string.join(words),1)
	tx.moveCursor(-offset, 0)

def	_centerDrawParaLine( tx, offset, extraspace, words, last=0):
	m = offset + 0.5 * extraspace
	tx.moveCursor(m, 0)
	tx._textOut(string.join(words),1)
	tx.moveCursor(-m, 0)

def	_rightDrawParaLine( tx, offset, extraspace, words, last=0):
	m = offset + extraspace
	tx.moveCursor(m, 0)
	tx._textOut(string.join(words),1)
	tx.moveCursor(-m, 0)

def	_justifyDrawParaLine( tx, offset, extraspace, words, last=0):
	tx.moveCursor(offset, 0)
	text  = string.join(words)
	if last:
		#last one, left align
		tx._textOut(text,1)
	else:
		tx.setWordSpace(extraspace / float(len(words)-1))
		tx._textOut(text,1)
		tx.setWordSpace(0)
	tx.moveCursor(-offset, 0)

def	_putFragLine(tx,words):
	for f in words:
		if (tx._fontname,tx._fontsize)!=(f.fontName,f.fontSize):
			tx._setFont(f.fontName, f.fontSize)
		if tx.XtraState.textColor!=f.textColor:
			tx.XtraState.textColor = f.textColor
			tx.setFillColor(f.textColor)
		if tx.XtraState.rise!=f.rise:
			tx.XtraState.rise=f.rise
			tx.setRise(f.rise)
		tx._textOut(f.text,f is words[-1])	# cheap textOut

def	_leftDrawParaLineX( tx, offset, line, last=0):
	tx.moveCursor(offset, 0)
	_putFragLine(tx, line.words)
	tx.moveCursor(-offset, 0)

def	_centerDrawParaLineX( tx, offset, line, last=0):
	m = offset+0.5*line.extraSpace
	tx.moveCursor(m, 0)
	_putFragLine(tx, line.words)
	tx.moveCursor(-m, 0)

def	_rightDrawParaLineX( tx, offset, line, last=0):
	m = offset+line.extraSpace
	tx.moveCursor(m, 0)
	_putFragLine(tx, line.words)
	tx.moveCursor(-m, 0)

def	_justifyDrawParaLineX( tx, offset, line, last=0):
	tx.moveCursor(offset, 0)
	if last:
		#last one, left align
		tx.moveCursor(offset, 0)
		_putFragLine(tx, line.words)
		tx.moveCursor(-offset, 0)
	else:
		tx.setWordSpace(line.extraSpace / float(line.wordCount-1))
		_putFragLine(tx, line.words)
		tx.setWordSpace(0)
	tx.moveCursor(-offset, 0)

def	_sameFrag(f,g):
	'returns 1 if two frags map out the same'
	for a in ('fontName', 'fontSize', 'textColor', 'rise'):
		if getattr(f,a)!=getattr(g,a): return 0
	return 1

def _getFragWords(frags):
	'''	given a fragment list return a list of lists
		[[size, (f00,w00), ..., (f0n,w0n)],....,[size, (fm0,wm0), ..., (f0n,wmn)]]
		each pair f,w represents a style and some string
		each sublist represents a word
	'''
	R = []
	W = []
	n = 0
	for f in frags:
		text = f.text
		#del f.text	# we can't do this until we sort out splitting
					# of paragraphs
		if text!='':
			S = string.split(text,' ')
			if W!=[] and text[0] in [' ','\t']:
				W.insert(0,n)
				R.append(W)
				W = []
				n = 0

			for w in S[:-1]:
				W.append((f,w))
				n = n + stringWidth(w, f.fontName, f.fontSize)
				W.insert(0,n)
				R.append(W)
				W = []
				n = 0

			w = S[-1]
			W.append((f,w))
			n = n + stringWidth(w, f.fontName, f.fontSize)
			if text[-1] in [' ','\t']:
				W.insert(0,n)
				R.append(W)
				W = []
				n = 0
	if W!=[]:
		W.insert(0,n)
		R.append(W)

	for r in R:
		f = r[1][0]
	return R

def	_split_bfragSimple(bfrag,start,stop):
	f = bfrag.clone()
	for a in ('lines', 'kind', 'text'):
		if hasattr(f,a): delattr(f,a)

	f.words = []
	for l in bfrag.lines[start:stop]:
		for w in l[1]:
			f.words.append(w)
	return [f]

def	_split_bfragHard(bfrag,start,stop):
	f = []
	for l in bfrag.lines[start:stop-1]:
		for w in l.words:
			f.append(w)
	return f

class Paragraph(Flowable):
	def __init__(self, text, style, bulletText = None, frags=None):
		if frags is None:
			text = cleanBlockQuotedText(text)
			style, frags = _parser.parse(text,style)
			if frags is None:
				raise "xml parser error (%s) in paragraph beginning\n'%s'"\
					% (_parser.errors[0],text[:min(30,len(text))])
		self.frags = frags
		self.style = style
		self.bulletText = bulletText
		self.debug = 0	 #turn this on to see a pretty one with all the margins etc.

	def wrap(self, availWidth, availHeight):
		# work out widths array for breaking
		self.width = availWidth
		first_line_width = availWidth - self.style.firstLineIndent - self.style.rightIndent
		later_widths = availWidth - self.style.leftIndent - self.style.rightIndent
		self.bfrags = self.breakLines([first_line_width, later_widths])
		self.height = len(self.bfrags.lines) * self.style.leading

		#estimate the size
		return (self.width, self.height)

	def split(self,availWidth, availHeight):
		if len(self.frags)<=0: return []

		#the split information is all inside self.bfrags
		if not hasattr(self,'bfrags'):
			self.wrap(availWidth,availHeight)
		bfrags = self.bfrags
		style = self.style
		leading = style.leading
		lines = bfrags.lines
		n = len(lines)
		s = int(availHeight/leading)
		if s<=1: return []
		if n<=s: return [self]
		func = bfrags.kind==0 and _split_bfragSimple or _split_bfragHard

		P1=Paragraph(None,style,bulletText=self.bulletText,frags=func(bfrags,0,s))
		P1._JustifyLast = 1
		if style.firstLineIndent != 0:
			style = deepcopy(style)
			style.firstLineIndent = 0
		P2=Paragraph(None,style,bulletText=None,frags=func(bfrags,s,n))
		return [P1,P2]

	def draw(self):
		#call another method for historical reasons.  Besides, I
		#suspect I will be playing with alternate drawing routines
		#so not doing it here makes it easier to switch.
		self.drawPara(self.debug)

	def breakLines(self, width):
		"""
		Returns a broken line structure. There are two cases
		
		A) For the simple case of a single formatting input fragment the output is
			A fragment specifier with
				kind = 0
				fontName, fontSize, leading, textColor
				lines=	A list of lines
						Each line has two items.
						1) unused width in points
						2) word list

		B) When there is more than one input formatting fragment the out put is
			A fragment specifier with
				kind = 1
				lines=	A list of fragments each having fields
							extraspace (needed for justified)
							fontSize
							words=word list
								each word is itself a fragment with
								various settings

		This structure can be used to easily draw paragraphs with the various alignments.
		You can supply either a single width or a list of widths; the latter will have its
		last item repeated until necessary. A 2-element list is useful when there is a
		different first line indent; a longer list could be created to facilitate custom wraps
		around irregular objects."""

		if type(width) <> types.ListType: maxwidths = [width]
		else: maxwidths = width
		lines = []
		lineno = 0
		maxwidth = maxwidths[lineno]
		style = self.style
		fFontSize = float(style.fontSize)

		#for bullets, work out width and ensure we wrap the right amount onto line one
		if self.bulletText <> None:
			bulletWidth = stringWidth(
				self.bulletText,
				style.bulletFontName, style.bulletFontSize)
			bulletRight = style.bulletIndent + bulletWidth
			if bulletRight > style.firstLineIndent:
				#..then it overruns, and we have less space available on line 1
				maxwidths[0] = maxwidths[0] - (bulletRight - style.firstLineIndent)

		self.height = 0
		frags = self.frags
		nFrags= len(frags)
		if nFrags==1:
			f = frags[0]
			fontSize = f.fontSize
			fontName = f.fontName
			words = hasattr(f,'text') and string.split(f.text, ' ') or f.words
			spacewidth = stringWidth(' ', fontName, fontSize)
			cLine = []
			currentwidth = - spacewidth   # hack to get around extra space for word 1
			for word in words:
				wordwidth = stringWidth(word, fontName, fontSize)
				space_available = maxwidth - (currentwidth + spacewidth + wordwidth)
				if	space_available > 0:
					# fit one more on this line
					cLine.append(word)
					currentwidth = currentwidth + spacewidth + wordwidth
				else:
					#end of line
					lines.append((maxwidth - currentwidth, cLine))
					cLine = [word]
					currentwidth = wordwidth
					lineno = lineno + 1
					try:
						maxwidth = maxwidths[lineno]
					except IndexError:
						maxwidth = maxwidths[-1]  # use the last one

			#deal with any leftovers on the final line
			if cLine!=[]: lines.append((maxwidth - currentwidth, cLine))
			return f.clone(kind=0, lines=lines)
		elif nFrags<=0:
			return ParaFrag(kind=0, fontSize=style.fontSize, fontName=style.fontName,
							textColor=style.textColor, lines=[])
		else:
			n = 0
			for w in _getFragWords(frags):
				spacewidth = stringWidth(' ',w[-1][0].fontName, w[-1][0].fontSize)

				if n==0:
					currentwidth = -spacewidth	 # hack to get around extra space for word 1
					words = []
					maxSize = 0

				wordwidth = w[0]
				f = w[1][0]
				space_available = maxwidth - (currentwidth + spacewidth + wordwidth)
				if	space_available > 0:
					# fit one more on this line
					n = n + 1
					maxSize = max(maxSize,f.fontSize)
					if words==[]:
						words = [f.clone()]
						words[-1].text = w[1][1]
					elif not _sameFrag(words[-1],f):
						words[-1].text = words[-1].text+' '
						words.append(f.clone())
						words[-1].text = w[1][1]
					else:
						words[-1].text = words[-1].text + ' ' + w[1][1]

					for i in w[2:]:
						f = i[0].clone()
						f.text=i[1]
						words.append(f)
						maxSize = max(maxSize,f.fontSize)
						
					currentwidth = currentwidth + spacewidth + wordwidth
				else:
					#end of line
					lines.append(ParaFrag(extraSpace=(maxwidth - currentwidth),wordCount=n,
										words=words, fontSize=maxSize))

					#start new line
					lineno = lineno + 1
					try:
						maxwidth = maxwidths[lineno]
					except IndexError:
						maxwidth = maxwidths[-1]  # use the last one
					currentwidth = wordwidth
					n = 1
					maxSize = f.fontSize
					words = [f.clone()]
					words[-1].text = w[1][1]

					for i in w[2:]:
						f = i[0].clone()
						f.text=i[1]
						words.append(f)
						maxSize = max(maxSize,f.fontSize)

			#deal with any leftovers on the final line
			if words<>[]:
				lines.append(ParaFrag(extraSpace=(maxwidth - currentwidth),wordCount=n,
									words=words, fontSize=maxSize))
			return ParaFrag(kind=1, lines=lines)

		return lines

	def drawPara(self,debug=0):
		"""Draws a paragraph according to the given style.
		Returns the final y position at the bottom. Not safe for
		paragraphs without spaces e.g. Japanese; wrapping
		algorithm will go infinite."""

		#stash the key facts locally for speed
		canvas = self.canv
		style = self.style
		bfrags = self.bfrags
		lines = bfrags.lines

		#work out the origin for line 1
		cur_x = style.leftIndent


		if debug:
			# This boxes and shades stuff to show how the paragraph
			# uses its space.  Useful for self-documentation so
			# the debug code stays!
			# box the lot
			canvas.rect(0, 0, self.width, self.height)
			#left and right margins
			canvas.saveState()
			canvas.setFillColor(Color(0.9,0.9,0.9))
			canvas.rect(0, 0, style.leftIndent, self.height)
			canvas.rect(self.width - style.rightIndent, 0, style.rightIndent, self.height)
			# shade above and below
			canvas.setFillColor(Color(1.0,1.0,0.0))
			canvas.restoreState()
			#self.drawLine(x + style.leftIndent, y, x + style.leftIndent, cur_y)


		nLines = len(lines)
		if nLines > 0:
			canvas.saveState()
			canvas.addLiteral('% textcanvas.drawParagraph()')
			alignment = style.alignment
			offset = style.firstLineIndent - style.leftIndent
			lim = nLines-1
			noJustifyLast = not (hasattr(self,'_JustifyLast') and self._JustifyLast)

			if bfrags.kind==0:
				if alignment == TA_LEFT:
					dpl = _leftDrawParaLine
				elif alignment == TA_CENTER:
					dpl = _centerDrawParaLine
				elif self.style.alignment == TA_RIGHT:
					dpl = _rightDrawParaLine
				elif self.style.alignment == TA_JUSTIFY:
					dpl = _justifyDrawParaLine
				f = bfrags
				cur_y = self.height - f.fontSize

				if self.bulletText <> None:
					tx2 = canvas.beginText(style.bulletIndent, cur_y)
					tx2.setFont(style.bulletFontName, style.bulletFontSize)
					tx2.setFillColor(hasattr(style,'bulletColor') and style.bulletColor or style.textColor)
					tx2.textOut(self.bulletText)
					bulletEnd = tx2.getX()
					offset = max(offset, bulletEnd - style.leftIndent)
					canvas.drawText(tx2)

				#set up the font etc.
				canvas._code.append('%s %s %s rg' % (f.textColor.red, f.textColor.green, f.textColor.blue))

				tx = canvas.beginText(cur_x, cur_y)

				#now the font for the rest of the paragraph
				tx.setFont(f.fontName, f.fontSize, style.leading)
				dpl( tx, offset, lines[0][0], lines[0][1], noJustifyLast and nLines==1)

				#now the middle of the paragraph, aligned with the left margin which is our origin.
				for i in range(1, nLines):
					dpl( tx, 0, lines[i][0], lines[i][1], noJustifyLast and i==lim)
			else:
				f = lines[0]
				cur_y = self.height - f.fontSize
				if alignment == TA_LEFT:
					dpl = _leftDrawParaLineX
				elif alignment == TA_CENTER:
					dpl = _centerDrawParaLineX
				elif self.style.alignment == TA_RIGHT:
					dpl = _rightDrawParaLineX
				elif self.style.alignment == TA_JUSTIFY:
					dpl = _justifyDrawParaLineX

				if self.bulletText <> None:
					tx2 = canvas.beginText(style.bulletIndent, cur_y)
					tx2.setFont(style.bulletFontName, style.bulletFontSize)
					tx2.textOut(self.bulletText)
					bulletEnd = tx2.getX()
					offset = max(offset, bulletEnd - style.leftIndent)
					canvas.drawText(tx2)

				#set up the font etc.
				tx = canvas.beginText(cur_x, cur_y)
				tx.XtraState=ParaFrag()
				tx.XtraState.textColor=None
				tx.XtraState.rise=0
				tx.setLeading(style.leading)
				f = lines[0].words[0]
				tx._setFont(f.fontName, f.fontSize)
				dpl( tx, offset, lines[0], noJustifyLast and nLines==1)

				#now the middle of the paragraph, aligned with the left margin which is our origin.
				for i in range(1, nLines):
					f = lines[i]
					dpl( tx, 0, f, noJustifyLast and i==lim)

			canvas.drawText(tx)
			canvas.restoreState()
