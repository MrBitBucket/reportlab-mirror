#copyright ReportLab Inc. 2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/pdfgen/fonts0.py?cvsroot=reportlab
#$Header $
__version__=''' $Id: pdfmetrics.py,v 1.23 2001/03/08 15:27:42 rgbecker Exp $ '''
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
widthVectorsByFont is populated each time a font is added.  This has
vectors of 256 elements and is the data used by the stringWidth function.
When _rl_accel is present, it maintains a similar database for itself.

"""
from _fontdata import *
# conditional import - try both import techniques, and set a flag
try:
	from reportlab.lib import _rl_accel
except ImportError:
	try:
		import _rl_accel
	except ImportError:
		_rl_accel = None

def addFont(font):
	"""This lets us use the optimized C stringWidth or pdfmetrics stringwidth
	function, saving one method call over asking the fonts to do it.  For
	e.g. CID fonts, it falls back to asking the font itself."""
	fontsByName[font.name] = font
	if hasattr(font, 'getWidths'):
		widthVectorsByFont[font.name] = font.getWidths()

def stringWidth(text, fontName, fontSize):
	try:
		widths = widthVectorsByFont[fontName]
		w = 0
		for char in text:
			w = w + widths[ord(char)]
		return w*fontSize*0.001
	except KeyError:
		# CID Font?  ask the font itself
		font = fonts[fontName]
		return font.stringWidth(text, fontSize)

def test():
	# load the standard ones:
	from reportlab.pdfgen import fonts0
	for baseFontName in standardFonts:
		encoding = fonts0.WinAnsi
		fontName = baseFontName + '-WinAnsi'
		font = fonts0.BuiltInType1Font(fontName, baseFontName, encoding)
		addWidths(fontName, font.getWidths())
		#test it
		msg = 'Hello World'
		w = stringWidth(msg, fontName, 10)#
		print 'width of "%s" in 10-point %s = %0.2f' % (msg, fontName, w)

if __name__=='__main__':
	test()
