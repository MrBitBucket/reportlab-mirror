#copyright ReportLab Inc. 2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/pdfgen/fonts0.py?cvsroot=reportlab
#$Header $
__version__=''' $Id: pdfmetrics.py,v 1.29 2001/03/17 15:21:22 rgbecker Exp $ '''
__doc__=""" 
This provides the character widths database for calculating
text metrics.  Everything for the base 14 fonts is pre-computed
and available in dictionaries and lists in this module.  The
machinery is also available to parse AFM files annd add new fonts
and encodings of fonts at run-time.

There are two steps to adding a new font.  First, the width of each names
glyph in the font must be added to the glyphs-by-name database. Then
for a particular encoding of a font, # how to explain this.
loadAFMFile() loads an AFM file, adding the glyph widths by name to the
database.

The static database portion (in _fontdata.py) contains three dictionaries
keyed on font names and leading to more data:
	ascent_descent - ascent and descent for each font
	widthsByName - glyph names and widths for each glyph in each font
	encodings - encoding vectors for standard encodings

When the C accelerator module _rl_accel is not present, a dictionary
widthVectorsByFont is populated each time a font is added.	This has
vectors of 256 elements and is the data used by the stringWidth function.
When _rl_accel is present, it maintains a similar database for itself.

"""
import string
from types import ListType, TupleType, StringType
from reportlab.pdfbase import pdfdoc
from reportlab import rl_config
from _fontdata import *
_dummyEncoding=' _not an encoding_ '

# conditional import - try both import techniques, and set a flag
try:
	try:
		from reportlab.lib import _rl_accel
	except ImportError, errMsg:
		if str(errMsg)!='cannot import name _rl_accel': raise
		import _rl_accel
	assert _rl_accel.version>="0.3", "bad _rl_accel"
	_stringWidth = _rl_accel.stringWidth
	_rl_accel.defaultEncoding(_dummyEncoding)
	del widthVectorsByFont
except ImportError, errMsg:
	if str(errMsg)!='No module named _rl_accel': raise
	_stringWidth = None

class Encoding:
	"""This is a class for encodings. It represents single byte encodings by default.
	"""
	_requiredLen = 256
	def __init__(self, vector):
		errMsg = "Single-byte encodings may only be initialized with the strings 'MacRomanEncoding' or 'WinAnsiEncoding', or a 256-element list"
		if type(vector) in (ListType, TupleType):
			assert not self._requiredLen or len(vector) == self._requiredLen, 'Encoding vector must have %d elements' % self._requiredLen
			self.vector = tuple(vector)
			self._encodingName = None
			self._baseEncodingName = rl_config.defaultEncoding
		elif type(vector) is StringType:
			try:
				self.vector = encodings[vector]	#This is a tuple so ca'nt be messed with
				self._encodingName = vector
				self._baseEncodingName = vector
			except KeyError:
				raise KeyError('Unknown font encoding "%s", allowed values are %s' % (vector, encodings.keys()))
		else:
			raise TypeError, errMsg

	def __getitem__(self, index):
		"Return glyph name for that code point, or None"
		return self.vector[index]

	def __setitem__(self, index, value):
		if self.vector[index]!=value:
			L = list(self.vector)
			L[index] = value
			self.vector = tuple(L)

	def getGlyphs(self):
		"Return glyph names"
		return filter(lambda x: x, self.vector)

	def modifyRange(self, base, newNames):
		"""Set a group of character names starting at the code point 'base'."""
		idx = base
		for name in newNames:
			self.vector[idx] = name
			idx = idx + 1

	def getDifferences(self, otherEnc):
		"""Return a compact list of the code points differing between two encodings

		This is in the Adobe format: list of
		   [[b1, name1, name2, name3],
		   [b2, name4]]
		where b1...bn is the starting code point, and the glyph names following
		are assigned consecutive code points."""

		ranges = []
		curRange = None
		for i in xrange(len(self.vector)):
			glyph = self[i]
			if glyph == otherEnc[i]:
				if curRange:
					ranges.append(curRange)
					curRange = []
			else:
				if curRange:
					curRange.append(glyph)
				else:
					curRange = [i, glyph]
		if curRange:
			ranges.append(curRange)
		return ranges

	def makePDFObject(self):
		"Returns a PDF Object representing self"
		#if self._encodingName:
			# it's a predefined one, we only need a string

		D = {}
		baseEnc = encodings[self._baseEncodingName]
		differences = self.getDifferences(baseEnc) #[None] * 256)

		# if no differences, we just need the base name
		if differences == []:
			return pdfdoc.PDFName(self._baseEncodingName)
		else:
			#make up a dictionary describing the new encoding
			diffArray = []
			for range in differences:
				diffArray.append(range[0])	# numbers go 'as is'
				for glyphName in range[1:]:
					if glyphName is not None:
						# there is no way to 'unset' a character in the base font.
						diffArray.append('/' + glyphName)

			#print 'diffArray = %s' % diffArray
			D["Differences"] = pdfdoc.PDFArray(diffArray)
			D["BaseEncoding"] = pdfdoc.PDFName(self._baseEncodingName)
			D["Type"] = pdfdoc.PDFName("Encoding")
			PD = pdfdoc.PDFDictionary(D)
			return PD

WinAnsiEncoding = Encoding('WinAnsiEncoding')
MacRomanEncoding = Encoding('MacRomanEncoding')
defaultEncoding = Encoding(rl_config.defaultEncoding)

class Font:
	"""Base class for a font.  Not sure yet what it needs to do"""
	def __init__(self,name):
		if ascent_descent.has_key(name):
			self.ascent = ascent_descent[name][0]
			self.descent = ascent_descent[name][1]
		else:
			self.ascent = 0
			self.descent = 0
		self.name = name
		fontsByName[name] = self
		widths = self._calcWidths()
		if _stringWidth:
			_rl_accel.setFontInfo(name,_dummyEncoding,self.ascent,self.descent,widths)
		else:
			widthVectorsByFont[name] = widths

	def getWidths(self):
		"Returns width array"
		if _stringWidth:
			return _rl_accel.getFontInfo(self.fontName)[0]
		else:
			return widthVectorsByFont[self.fontName]

	if not _stringWidth:
		def stringWidth(self, text, size):
			w = 0
			widths = self.getWidths()
			for ch in text:
				w = w + widths[ord(ch)]
			return w * 0.001 * size

		def getWidths(self):
			"Returns width array"
			return _rl_accel.getFontInfo(self.fontName)[0]
	else:
		def getWidths(self):
			"Returns width array"
			return widthVectorsByFont[self.fontName]

if _stringWidth:
	import new
	Font.stringWidth = new.instancemethod(_rl_accel._instanceStringWidth,None,Font)
	stringWidth = _stringWidth
else:
	def stringWidth(text, fontName, fontSize):
		try:
			widths = widthVectorsByFont[fontName]
			w = 0
			for char in text:
				w = w + widths[ord(char)]
			return w*fontSize*0.001
		except KeyError:
			# CID Font?  ask the font itself
			font = fontsByName[fontName]
			return font.stringWidth(text, fontSize)

class Type1Font(Font):
	"""Defines a font with a possibly with a new encoding."""
	def __init__(self, name, baseFontName, encoding):
		"""
		The name should be distinct
		baseFontName is one of the standard
		14 fonts.  encoding is either a predefined string such
		as 'WinAnsiEncoding' or 'MacRomanEncoding', or a valid
		Encoding object."""

		assert baseFontName in standardFonts, "baseFontName must be one of the following: %s" % StandardFonts
		self.baseFontName = baseFontName
		self.encoding = encoding
		fontsByBaseEnc[(baseFontName,encoding)] = self
		Font.__init__(self,name)

	def addObjects(self, doc):
		"""Makes and returns one or more PDF objects to be added
		to the document.  The caller supplies the internal name
		to be used (typically F1, F2... in sequence) """

		# construct a Type 1 Font internal object
		internalName = 'F' + repr(len(doc.fontMapping)+1)
		pdfFont = pdfdoc.PDFType1Font()
		pdfFont.Name = internalName
		pdfFont.BaseFont = self.baseFontName
		pdfFont.__Comment__ = 'Font %s' % self.name
		if type(self.encoding) is StringType:
			pdfFont.Encoding = pdfdoc.PDFName(self.encoding)
		else:
			enc = self.encoding.makePDFObject()
			pdfFont.Encoding = enc
			#objects.append(enc)

		# now link it in
		ref = doc.Reference(pdfFont, internalName)

		# also refer to it in the BasicFonts dictionary
		fontDict = doc.idToObject['BasicFonts'].dict
		fontDict[internalName] = pdfFont

		# and in the font mappings
		doc.fontMapping[self.name] = '/' + internalName

	def _calcWidths(self):
		"Computes widths array"
		widthVector = []
		thisFontWidths = widthsByFontGlyph[self.baseFontName]
		if type(self.encoding) is StringType:
			vector = encodings[self.encoding]
		else:
			vector = self.encoding
		for glyphName in vector:
			try:
				glyphWidth = thisFontWidths[glyphName]
			except KeyError:
				glyphWidth = 0 # None?
			widthVector.append(glyphWidth)
		return widthVector

def addFont(name,baseFontName,encoding):
	'''
	This function either finds an existing font or creates one
	'''
	if type(encoding) is StringType: encoding = Encoding(encoding)
	x=(baseFontName,encoding.vector)
	font = fontsByBaseEnc.get(x,None)
	if not font:
		font = Type1Font(name,baseFontName,encoding)
	elif fontsByName.has_key(name) and fontByName[name] is not font:
		raise ValueError, "Attempted to addFont(%s,%s,%s) font %s aready added" %(name,baseFontName,encoding,name)
	return font

#add all the standard Fonts
for fontName in standardFonts:
	addFont(fontName,fontName, fontName in ('Symbol','ZapfDingbats') and fontName or defaultEncoding)
del fontName

def testMetrics():
	def fontDataDump():
		print 'fontsByName'
		for k,i in fontsByName.items():
			print k, i
		print 'fontsByBaseEnc'
		for k,i in fontsByBaseEnc.items():
			print k, i
	fontDataDump()
	# load the standard ones:
	for baseFontName in standardFonts:
		encoding = WinAnsiEncoding
		fontName = baseFontName + '-WinAnsi'
		font = Type1Font(fontName, baseFontName, encoding)
		#test it
		msg = 'Hello World'
		w = stringWidth(msg, fontName, 10)#
		print 'width of "%s" in 10-point %s = %0.2f' % (msg, fontName, w)
	fontDataDump()

def testFonts():
	# make a custom encoded font.
	import reportlab.pdfgen.canvas
	c = reportlab.pdfgen.canvas.Canvas('testfonts.pdf')
	c.setPageCompression(0)
	c.setFont('Helvetica', 12)
	c.drawString(100, 700, 'The text below should be in a custom encoding in which all vowels become "z"')

	# invent a new language where vowels are replaced with letter 'z'
	zenc = Encoding('WinAnsiEncoding')
	for ch in 'aeiou':
		zenc[ord(ch)] = 'z'
	for ch in 'AEIOU':
		zenc[ord(ch)] = 'Z'
	f = Type1Font('FontWithoutVowels', 'Helvetica-Oblique', zenc)
	c.addFont(f)

	c.setFont('FontWithoutVowels', 12)
	c.drawString(125, 675, "The magic word is squamish ossifrage")

	# now demonstrate adding a Euro to MacRoman, which lacks one
	c.setFont('Helvetica', 12)
	c.drawString(100, 650, "MacRoman encoding lacks a Euro.  We'll make a Mac font with the Euro at #219:")

	# WinAnsi Helvetica
	c.addFont(Type1Font('Helvetica-WinAnsi', 'Helvetica-Oblique', WinAnsiEncoding))
	c.setFont('Helvetica-WinAnsi', 12)
	c.drawString(125, 625, 'WinAnsi with Euro: character 128 = "\200"')

	c.addFont(Type1Font('MacHelvNoEuro', 'Helvetica-Oblique', MacRomanEncoding))
	c.setFont('MacHelvNoEuro', 12)
	c.drawString(125, 600, 'Standard MacRoman, no Euro: Character 219 = "\333"') # oct(219)=0333

	# now make our hacked encoding
	euroMac = Encoding('MacRomanEncoding')
	euroMac[219] = 'Euro'
	c.addFont(Type1Font('MacHelvWithEuro', 'Helvetica-Oblique', euroMac))
	c.setFont('MacHelvWithEuro', 12)
	c.drawString(125, 575, 'Hacked MacRoman with Euro: Character 219 = "\333"') # oct(219)=0333

	# now test width setting with and without _rl_accel - harder
	# make an encoding where 'm' becomes 'i'
	c.setFont('Helvetica', 12)
	c.drawString(100, 500, "Recode 'm' to 'i' and check we can measure widths.	Boxes should surround letters.")
	sample = 'Mmmmm. ' * 6 + 'Mmmm'

	c.setFont('Helvetica-Oblique',12)
	c.drawString(125, 475, sample)
	w = c.stringWidth(sample, 'Helvetica-Oblique', 12)
	c.rect(125, 475, w, 12)

	narrowEnc = Encoding('WinAnsiEncoding')
	narrowEnc[ord('m')] = 'i'
	narrowEnc[ord('M')] = 'I'
	c.addFont(Type1Font('narrow', 'Helvetica-Oblique', narrowEnc))
	c.setFont('narrow', 12)
	c.drawString(125, 450, sample)
	w = c.stringWidth(sample, 'narrow', 12)
	c.rect(125, 450, w, 12)

	c.setFont('Helvetica', 12)
	c.drawString(100, 400, "Symbol & Dingbats fonts - check we still get valid PDF in StandardEncoding")
	c.setFont('Symbol', 12)
	c.drawString(100, 375, 'abcdefghijklmn')
	c.setFont('ZapfDingbats', 12)
	c.drawString(300, 375, 'abcdefghijklmn')

	c.save()

	print 'saved testfonts.pdf'

if __name__=='__main__':
	testMetrics()
	testFonts()
