#copyright ReportLab Inc. 2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/pdfgen/fonts0.py?cvsroot=reportlab
#$Header $
__version__=''' $Id: fonts0.py,v 1.1 2001/03/06 17:38:15 andy_robinson Exp $ '''
__doc__=""" 
This is an attempt to break out fonts as user-accessible objects.  You can explicitly
construct a font object with any desired encoding and add it to the document.  The
font objects here are a base to build more complex fonts onto in future. For example
the even more experimental jpsupport.py module adds CIDFonts, which have thousands
of characters and multiple encodings.

You construct fonts and register them with the canvas.  Every font knows its encoding.
Encodings can either be objects, or just string names if you don't want to mess with
them; the latter saves some time and file size.

The simplest way to construct a font is like this:
    >>> f1 = fonts0.BuiltInType1Font('myFont', 'Helvetica', 'WinAnsiEncoding')
    >>> myCanvas.registerFont0(f1)

The first argument is the name you will use later in stringWidth, setFont and so on.
The second must be one of the 14 built-in font names.  The third must be
'WinAnsiEncoding' or 'MacRomanEncoding'.

This is not interesting; in fact the canvas auto-creates 14 fonts with the standard
names when it starts up.  However, you can customize the encodings by using a
SingleByteEncoding object instead of a string.  Here we construct a special
encoding where every vowel is replaced with the letter 'z', and use it:

    zenc = SingleByteEncoding('WinAnsiEncoding')
    for ch in 'aeiou':
        zenc[ord(ch)] = 'z'
    for ch in 'AEIOU':
        zenc[ord(ch)] = 'Z'
    f = BuiltInType1Font('FontWithoutVowels', 'Helvetica-Oblique', zenc)
    c.registerFont0(f)
    
    c.setFont('FontWithoutVowels', 12)
    c.drawString(125, 675, "The magic word is squamish ossifrage")

If you execute this script, you will see the results.
Re-encoding has one or two uses even with the built-in fonts; you can make
all-caps fonts.  We also found one more relevant use; MacRoman encoding lacks
the Euro character, even though it is in all Adobe fonts. Adobe recommend
re-encoding the font with the Euro at position 219.  Here we make a Mac
font with a Euro:

    euroMacEncoding = SingleByteEncoding('MacRomanEncoding')
    euroMacEncoding[219] = 'Euro'
    c.registerFont0(BuiltInType1Font('MacHelvWithEuro', 'Helvetica-Oblique', euroMacEncoding))
    c.setFont('MacHelvWithEuro', 12)
    c.drawString(125, 575, 'Hacked MacRoman with Euro: Character 219 = "\333"') # oct(219)=0333

The ability to re-encode fonts is critical when we start embedding fonts,
or referring to fonts in Adobe add-on language packs.




In progress - see to-do list at bottom




To Do:
------
(1) Make encoding vectors for ZapfDingbats and Symbol based on the AFM files.
Add special-casing to extract their widths, and check test_pdfbase_pdfmetrics.py
gets them all correct.

(2) Discuss - can we delegate stringWidth to the fonts?  That's the right way
to let CIDFonts or TrueType fonts do their own thing.  
If the canvas does it, stringWdth come right out of pdfmetrics.  Add one call to
use the C function. Otherwise, pdfmetrics should keep a font list and 

(3) Get it working with _rl_accel


"""

import string
import types
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import pdfdoc

class Encoding:
    """This is an abstract base class for encodings.  """

    def __init__(self):
        "Warning to deter them from creating these directly"
        raise "Error", "Do not create Encoding objects - use a derived class such as SingleByteEncoding"

    def getGlyphs(self):
        "Return list of glyph names, in undefined order"
        return []

    def getDifferences(self, otherEnc):
        """Return a compact list of the code points differing between two encodings
        This is in the Adobe format: list of
           [[b1, name1, name2, name3],
           [b2, name4]]
        where b1...bn is the starting code point, and the glyph names following
        are assigned consecutive code points."""
        return []
    
    def makePDFObject(self):
        pass

class SingleByteEncoding(Encoding):
    """Represents a mapping of code points to character names.  Unassigned
    code points are given the value 'None'"""
    # in PDF, encodings are based on a list of differences
    # over a standard encoding.
    def __init__(self, vector):
        errMsg = "Single-byte encodings may only be initialized with the strings 'MacRomanEncoding' or 'WinAnsiEncoding', or a 256-element list"
        if type(vector) in (types.ListType, types.TupleType):
            assert len(vector) == 256, 'Encoding vector must have 256 elements'
            self.vector = vector[:]  # TAKE A COPY so they don't mess up pdfmetrics
            self._encodingName = None
            self._baseEncodingName = pdfdoc.DEFAULT_ENCODING
        elif type(vector) is types.StringType:
            try:
                self.vector = pdfmetrics.encodings[vector][:]  # TAKE A COPY!
                self._encodingName = vector
                self._baseEncodingName = vector
            except KeyError:
                raise KeyError('Unknown font encoding "%s", allowed values are %s' % (vector, pdfmetrics.encodings.keys()))
        else:
            raise TypeError, errMsg

    def __getitem__(self, index):
        "Return glyph name for that code point, or None"
        return self.vector[index]

    def __setitem__(self, index, value):
        self.vector[index] = value

    def makePDFObject(self):
        "Returns a PDF Object representing self"
        #if self._encodingName:
            # it's a predefined one, we only need a string
            
        D = {}
        baseEnc = pdfmetrics.encodings[self._baseEncodingName]
        differences = self.getDifferences(baseEnc) #[None] * 256)

        # if no differences, we just need the base name
        if differences == []:
            return pdfdoc.PDFName(self._baseEncodingName)
        else:
            #make up a dictionary describing the new encoding
            diffArray = []
            for range in differences:
                diffArray.append(range[0])  # numbers go 'as is'
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
    
    def getGlyphs(self):
        "Return glyph names, in no particular order"
        glyphs = []
        for glyph in self.vector: # copy it
            if glyph:
                glyphs.append(glyph)
        glyphs.sort()
        return glyphs

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
        for i in range(256):
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
                
        
WinAnsiEncoding = SingleByteEncoding('WinAnsiEncoding')
MacRomanEncoding = SingleByteEncoding('MacRomanEncoding')
defaultEncoding = SingleByteEncoding(pdfdoc.DEFAULT_ENCODING)

        

class Font:
    """Base class for a font.  Not sure yet what it needs to do"""
    def __init__(self):
        self.ascent = None
        self.descent = None
        self.widths = []

    def addObjects(self, doc):
        """Adds PDF objects to the document as needed to represent self."""
        pass

    def stringWidth(self, text, size):
        "Calculates width of text for given point size"
        pass

class BuiltInType1Font(Font):
    """Defines a standard font with a new name, possibly with
    a new encoding."""
    def __init__(self, newName, baseFontName, encoding):
        """The new name should be distinct from any other font
        in the document.  baseFontName is one of the standard
        14 fonts.  encoding is either a predefined string such
        as 'WinAnsiEncoding' or 'MacRomanEncoding', or a valid
        Encoding object."""
        
        Font.__init__(self)
        assert baseFontName in pdfmetrics.standardEnglishFonts, "baseFontName must be one of the following: %s" % pdfmetrics.StandardEnglishFonts
        self.name = newName
        self.baseFontName = baseFontName
        #assert isinstance(encoding, Encoding)
        self.encoding = encoding
        self._widths = None 

        self._calcWidths()

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
        if type(self.encoding) is types.StringType:
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
        "Computes widths array, if not done already"
        # get the dictionary of glyph -> width
        if self._widths:
            return self._widths
        else:
            if self.baseFontName == 'Symbol':
                self._widths = pdfmetrics.SymbolWidths[:]
            elif self.baseFontName == 'ZapfDingbats':
                self._widths = pdfmetrics.ZapfDingbatsWidths[:]
            else:
                widthVector = []
                thisFontWidths = pdfmetrics.widthsByName[self.baseFontName]
                if type(self.encoding) is types.StringType:
                    vector = pdfmetrics.encodings[self.encoding]
                else:
                    vector = self.encoding
                for glyphName in vector:
                    try:
                        glyphWidth = thisFontWidths[glyphName]
                    except KeyError:
                        glyphWidth = 0 # None?
                    widthVector.append(glyphWidth)
                self._widths = widthVector
            return self._widths

    
    def getWidths(self):
        "Returns width array for use in optimized pdfmetrics database"
        return self._widths
    
    def stringWidth(self, text, size):
        # weakness - assumes getWidths called.  do the latter on _init_
        w = 0
        for ch in text:
            w = w + self._widths[ord(ch)]
        return w * 0.001 * size
    
def checkWidths(fontName, encName):
    if encName == 'WinAnsiEncoding':
        enc = WinAnsi
        names = pdfmetrics.WinAnsiNames
    elif encName == 'MacRomanEncoding':
        enc = MacRoman
        names = pdfmetrics.MacRomanNames
    f = BuiltInType1Font('NewFont',fontName, enc)
    
    new_w = f.getWidths()
    lowerFontName = string.lower(fontName)
    old_w = pdfmetrics.widths['WinAnsiEncoding'][lowerFontName]

    if new_w == old_w:
        print 'Font %s compares same' % fontName
    else:
        print 'Font %s differs as follows:' % fontName
        for i in range(256):
            if new_w[i] <> old_w[i]:
                print '    %d (%s): old = %s, new = %s' % (i, names[i], old_w[i], new_w[i])
        
        
if __name__=='__main__':
    # make a custom encoded font.
    import reportlab.pdfgen.canvas
    c = reportlab.pdfgen.canvas.Canvas('testfonts.pdf')
    c.setPageCompression(0)
    c.setFont('Helvetica', 12)
    c.drawString(100, 700, 'The text below should be in a custom encoding in which all vowels become "z"')

    # invent a new language where vowels are replaced with letter 'z'
    zenc = SingleByteEncoding('WinAnsiEncoding')
    for ch in 'aeiou':
        zenc[ord(ch)] = 'z'
    for ch in 'AEIOU':
        zenc[ord(ch)] = 'Z'
    f = BuiltInType1Font('FontWithoutVowels', 'Helvetica-Oblique', zenc)
    c.registerFont0(f)
    
    c.setFont('FontWithoutVowels', 12)
    c.drawString(125, 675, "The magic word is squamish ossifrage")

    # now demonstrate adding a Euro to MacRoman, which lacks one
    c.setFont('Helvetica', 12)
    c.drawString(100, 650, "MacRoman encoding lacks a Euro.  We'll make a Mac font with the Euro at #219:")

    # WinAnsi Helvetica
    c.registerFont0(BuiltInType1Font('Helvetica-WinAnsi', 'Helvetica-Oblique', WinAnsiEncoding))
    c.setFont('Helvetica-WinAnsi', 12)
    c.drawString(125, 625, 'WinAnsi with Euro: character 128 = "\200"') 

    c.registerFont0(BuiltInType1Font('MacHelvNoEuro', 'Helvetica-Oblique', MacRomanEncoding))
    c.setFont('MacHelvNoEuro', 12)
    c.drawString(125, 600, 'Standard MacRoman, no Euro: Character 219 = "\333"') # oct(219)=0333

    # now make our hacked encoding    
    euroMac = SingleByteEncoding('MacRomanEncoding')
    euroMac[219] = 'Euro'
    c.registerFont0(BuiltInType1Font('MacHelvWithEuro', 'Helvetica-Oblique', euroMac))
    c.setFont('MacHelvWithEuro', 12)
    c.drawString(125, 575, 'Hacked MacRoman with Euro: Character 219 = "\333"') # oct(219)=0333

    # now test width setting with and without _rl_accel - harder
    # make an encoding where 'm' becomes 'i'
    c.setFont('Helvetica', 12)
    c.drawString(100, 500, "Recode 'm' to 'i' and check we can measure widths.  Boxes should surround letters.")
    sample = 'Mmmmm. ' * 6 + 'Mmmm'

    c.setFont('Helvetica-Oblique',12)
    c.drawString(125, 475, sample)
    w = c.stringWidth(sample, 'Helvetica-Oblique', 12)
    c.rect(125, 475, w, 12)

    narrowEnc = SingleByteEncoding('WinAnsiEncoding')
    narrowEnc[ord('m')] = 'i'
    narrowEnc[ord('M')] = 'I'
    c.registerFont0(BuiltInType1Font('narrow', 'Helvetica-Oblique', narrowEnc))
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
    