import string
from types import StringType, ListType
from paragraph import Paragraph, cleanBlockQuotedText, _handleBulletWidth, ParaFrag, _getFragWords, \
	stringWidth, _sameFrag
from flowables import _dedenter

def _getFragLines(frags):
	lines = []
	cline = []
	W = frags[:]
	while W != []:
		w = W[0]
		t = w.text
		del W[0]
		i = string.find(t,'\n')
		if i>=0:
			tleft = t[i+1:]
			w.text = t[:i]
			cline.append(w)
			lines.append(cline)
			cline = []
			if tleft!='':
				W.insert(0,w.clone(text=tleft))
		else:
			cline.append(w)
	if cline!=[]: lines.append(cline)
	return lines

class XPreformatted(Paragraph):
	def __init__(self, text, style, bulletText = None, dedent=0, frags=None):
		cleaner = lambda text, dedent=dedent: string.join(_dedenter(text,dedent),'\n')
		self._setup(text, style, bulletText, frags, cleaner)

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
						2) a list of words

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

		if type(width) <> ListType: maxWidths = [width]
		else: maxWidths = width
		lines = []
		lineno = 0
		maxWidth = maxWidths[lineno]
		style = self.style
		fFontSize = float(style.fontSize)
		requiredWidth = 0

		#for bullets, work out width and ensure we wrap the right amount onto line one
		_handleBulletWidth(self.bulletText,style,maxWidths)

		self.height = 0
		frags = self.frags
		nFrags= len(frags)
		if nFrags==1:
			f = frags[0]
			fontSize = f.fontSize
			fontName = f.fontName
			if hasattr(f,'text'):
				L=string.split(f.text, '\n')
				for l in L:
					currentWidth = stringWidth(l,fontName,fontSize)
					requiredWidth = max(currentWidth,requiredWidth)
					extraSpace = maxWidth-currentWidth
					lines.append((extraSpace,string.split(l,' ')))
					lineno = lineno+1
					maxWidth = lineno<len(maxWidths) and maxWidths[lineno] or maxWidths[-1]
			else:
				lines=f.lines

			self.width = max(self.width,requiredWidth)
			return f.clone(kind=0, lines=lines)
		elif nFrags<=0:
			return ParaFrag(kind=0, fontSize=style.fontSize, fontName=style.fontName,
							textColor=style.textColor, lines=[])
		else:
			for L in _getFragLines(frags):
				n = 0
				maxSize = 0
				currentWidth = 0
				words = []
				for w in _getFragWords(L):
					spaceWidth = stringWidth(' ',w[-1][0].fontName, w[-1][0].fontSize)
					if not n: currentWidth = -spaceWidth	# hack to get around extra space for word 1
					wordWidth = w[0]
					f = w[1][0]
					space_available = maxWidth - (currentWidth + spaceWidth + wordWidth)
					n = n + 1
					maxSize = max(maxSize,f.fontSize)
					nText = w[1][1]
					if words==[]:
						words = [f.clone()]
						words[-1].text = nText
					elif not _sameFrag(words[-1],f):
						if nText!='' and nText[0]!=' ':
							words[-1].text = words[-1].text + ' ' 
						words.append(f.clone())
						words[-1].text = nText
					else:
						if nText!='' and nText[0]!=' ':
							words[-1].text = words[-1].text + ' ' + nText

					for i in w[2:]:
						f = i[0].clone()
						f.text=i[1]
						words.append(f)
						maxSize = max(maxSize,f.fontSize)

					currentWidth = currentWidth + spaceWidth + wordWidth

				lineno = lineno+1
				maxWidth = lineno<len(maxWidths) and maxWidths[lineno] or maxWidths[-1]
				requiredWidth = max(currentWidth,requiredWidth)
				extraSpace = maxWidth - currentWidth
				lines.append(ParaFrag(extraSpace=extraSpace,wordCount=n, words=words, fontSize=maxSize))

			self.width = max(self.width,requiredWidth)
			return ParaFrag(kind=1, lines=lines)

		return lines

if __name__=='__main__':	#NORUNTESTS
	def dumpXPreformattedLines(P):
		print 'dumpXPreforemattedLines(%s)' % str(P)
		lines = P.bfrags.lines
		n =len(lines)
		for l in range(n):
			line = lines[l]
			words = line.words
			nwords = len(words)
			print 'line%d: %d(%d)\n  ' % (l,nwords,line.wordCount),
			for w in range(nwords):
				print "%d:'%s'"%(w,words[w].text),
			print

	def dumpXPreformattedFrags(P):
		print 'dumpXPreforemattedFrags(%s)' % str(P)
		frags = P.frags
		n =len(frags)
		for l in range(n):
			print "frag%d: '%s'" % (l, frags[l].text)
	
		l = 0
		for W in _getFragWords(frags):
			print "fragword%d: size=%d" % (l, W[0]),
			for w in W[1:]:
				print "'%s'" % w[1],
			print
			l = l + 1

	from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
	styleSheet = getSampleStyleSheet()
	B = styleSheet['BodyText']
	style = ParagraphStyle("discussiontext", parent=B)
	style.fontName= 'Helvetica'
	text='''


The <font name=courier color=green>CMYK</font> or subtractive

method follows the way a printer
mixes three pigments (cyan, magenta, and yellow) to form colors.
Because mixing chemicals is more difficult than combining light there
is a fourth parameter for darkness.  For example a chemical
combination of the <font name=courier color=green>CMY</font> pigments generally never makes a perfect

black -- instead producing a muddy color -- so, to get black printers
don't use the <font name=courier color=green>CMY</font> pigments but use a direct black ink.  Because
<font name=courier color=green>CMYK</font> maps more directly to the way printer hardware works it may
be the case that &amp;| &amp; | colors specified in <font name=courier color=green>CMYK</font> will provide better fidelity
and better control when printed.


'''
	P=XPreformatted(text,style)
	dumpXPreformattedFrags(P)
	aW, aH = 456.0, 42.8
	w,h = P.wrap(aW, aH)
	dumpXPreformattedLines(P)
	S = P.split(aW,aH)
	for s in S:
		s.wrap(aW,aH)
		dumpXPreformattedLines(s)
		aH = 500
