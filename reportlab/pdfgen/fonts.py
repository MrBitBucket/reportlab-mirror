# fonts
"""
This defines Font, Encoding and TypeFace classes aimed at end users.

There are counterparts to some of these in pdfbase/pdfdoc.py, but
the latter focus on constructing the right PDF objects.  These
classes are declarative and focus on letting the user construct
and query font objects.

pdfmetrics.py maintains a registry of font objects at run time,
but does not import any classes from here to avoid circularity.

NOTE - due to circularity problems, I have not managed to
move the base classes fron pdfmetrics to here yet.

"""
import os
import string
from types import ListType, TupleType, StringType
from reportlab.pdfbase import _fontdata # needs to know names of standard fonts
from reportlab.rl_config import defaultEncoding
#from reportlab.pdfbase import pdfmetrics

class FontError(Exception):
    pass
class FontNotFoundError(Exception):
    pass

def parseAFMFile(afmFileName):
    """Quick and dirty - gives back a top-level dictionary
    with top-level items, and a 'widths' key containing
    a dictionary of glyph names and widths.  Just enough
    needed for embedding.  A better parser would accept
    options for what data you wwanted, and preserve the
    order."""

    lines = open(afmFileName, 'r').readlines()
    topLevel = {}
    glyphLevel = []

    lines = map(string.strip, lines)
    #pass 1 - get the widths
    inMetrics = 0  # os 'TOP', or 'CHARMETRICS'
    for line in lines:
        if line[0:16] == 'StartCharMetrics':
            inMetrics = 1
        elif line[0:14] == 'EndCharMetrics':
            inMetrics = 0
        elif inMetrics:
            chunks = string.split(line, ';')
            chunks = map(string.strip, chunks)
            cidChunk, widthChunk, nameChunk = chunks[0:3]

            # character ID
            l, r = string.split(cidChunk)
            assert l == 'C', 'bad line in font file %s' % line
            cid = string.atoi(r)

            # width
            l, r = string.split(widthChunk)
            assert l == 'WX', 'bad line in font file %s' % line
            width = string.atoi(r)

            # name
            l, r = string.split(nameChunk)
            assert l == 'N', 'bad line in font file %s' % line
            name = r

            glyphLevel.append((cid, width, name))

    # pass 2 font info
    inHeader = 0  
    for line in lines:
        if line[0:16] == 'StartFontMetrics':
            inHeader = 1
        if line[0:16] == 'StartCharMetrics':
            inHeader = 0
        elif inHeader:
            left, right = string.split(line, ' ', 1)
            if left == 'Comment':
                pass
            try:
                right = string.atoi(right)
            except:
                pass
            topLevel[left] = right
    
            
    return (topLevel, glyphLevel)

class TypeFace:
    def __init__(self, name):
        self.name = name
        self.glyphNames = []
        self.glyphWidths = {}
        self.ascent = 0   
        self.descent = 0
        if name == 'ZapfDingbats':
            self.requiredEncoding = 'ZapfDingbatsEncoding'
        elif name == 'Symbol':
            self.requiredEncoding = 'SymbolEncoding'
        else:
            self.requiredEncoding = None
        
        if name in _fontdata.standardFonts:
            self.builtIn = 1
            self._loadBuiltInData(name)
        else:
            self.builtIn = 0
            
    def _loadBuiltInData(self, name):
        """Called for the built in 14 fonts.  Gets their glyph data.

        We presume they never change so this can be a shared reference."""
        self.glyphWidths = _fontdata.widthsByFontGlyph[name]
        self.glyphNames = self.glyphWidths.keys()

#for faceName in _fontdata.standardFonts:
#    registerTypeFace(TypeFace(faceName))
    

class Encoding:
    """Object to help you create and refer to encodings."""
    def __init__(self, name, base=None):
        self.name = name
        self.frozen = 0
        if name in _fontdata.standardEncodings:
            assert base is None, "Can't have a base encoding for a standard encoding"
            self.baseEncodingName = name
            self.vector = _fontdata.encodings[name]
        elif base == None:
            # assume based on the usual one
            self.baseEncodingName = defaultEncoding
            self.vector = _fontdata.encodings[defaultEncoding]
        elif type(base) is StringType:
            from reportlab.pdfbase import pdfmetrics
            baseEnc = pdfmetrics.getEncoding(base)
            self.baseEncodingName = baseEnc.name
            self.vector = baseEnc.vector[:]
        elif type(base) in (ListType, TupleType):
            self.baseEncodingName = defaultEncoding
            self.vector = base[:]
        elif isinstance(base, Encoding):
            # accept a vector
            self.baseEncodingName = base.name
            self.vector = base.vector[:]
            
    def __getitem__(self, index):
        "Return glyph name for that code point, or None"
        return self.vector[index]

    def __setitem__(self, index, value):
        # should fail if they are frozen
        assert self.frozen == 0, 'Cannot modify a frozen encoding'
        if self.vector[index]!=value:
            L = list(self.vector)
            L[index] = value
            self.vector = tuple(L)

    def freeze(self):
        self.vector = tuple(self.vector)
        self.frozen = 1
        
    def isEqual(self, other):
        return ((enc.name == other.name) and (enc.vector == other.vector))

    def modifyRange(self, base, newNames):
        """Set a group of character names starting at the code point 'base'."""
        assert self.frozen == 0, 'Cannot modify a frozen encoding'
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
        # avoid circular imports - this cannot go at module level
        from reportlab.pdfbase import pdfdoc
        from reportlab.pdfbase import pdfmetrics
    
        D = {}
        baseEnc = pdfmetrics.getEncoding(self.baseEncodingName)
        differences = self.getDifferences(baseEnc) #[None] * 256)

        # if no differences, we just need the base name
        if differences == []:
            return pdfdoc.PDFName(self.baseEncodingName)
        else:
            #make up a dictionary describing the new encoding
            diffArray = []
            for range in differences:
                diffArray.append(range[0])        # numbers go 'as is'
                for glyphName in range[1:]:
                    if glyphName is not None:
                        # there is no way to 'unset' a character in the base font.
                        diffArray.append('/' + glyphName)

            #print 'diffArray = %s' % diffArray
            D["Differences"] = pdfdoc.PDFArray(diffArray)
            D["BaseEncoding"] = pdfdoc.PDFName(self.baseEncodingName)
            D["Type"] = pdfdoc.PDFName("Encoding")
            PD = pdfdoc.PDFDictionary(D)
            return PD

#for encName in _fontdata.standardEncodings:
#    registerEncoding(Encoding(encName))

class Font:
    """Represents a font (i.e combination of face and encoding).

    Defines suitable machinery for single byte fonts.  This is
    a concrete class which can handle the basic built-in fonts;
    not clear yet if embedded ones need a new font class or
    just a new typeface class (which would do the job through
    composition)"""
    def __init__(self, name, faceName, encName):
        from reportlab.pdfbase import pdfmetrics
        self.name = name
        self.face = pdfmetrics.getTypeFace(faceName)
        self.encoding= pdfmetrics.getEncoding(encName)
        self._calcWidths()
        
    def _calcWidths(self):
        """Vector of widths for stringWidth function"""
        #synthesize on first request
        w = [0] * 256
        gw = self.face.glyphWidths
        vec = self.encoding.vector
        for i in range(256):
            glyphName = vec[i]
            if glyphName is not None:
                try:
                    width = gw[glyphName]
                    w[i] = width
                except KeyError:
                    print 'typeface "%s" does not have a glyph "%s", bad font!' % (self.face.name, glyphName)
        self.widths = w

    def stringWidth(self, text, size):
        """This is the "purist" approach to width.  The practical one
        is to use the pdfmetrics.stringWidth one which may be optimized
        in C."""
        w = 0
        widths = self.widths
        for ch in text:
            w = w + widths[ord(ch)]
        return w * 0.001 * size

    def _formatWidths(self):
        "returns a pretty block in PDF Array format to aid inspection"
        text = '['
        for i in range(256):
            text = text + ' ' + str(self.widths[i])
            if i == 255:
                text = text + ' ]'
            if i % 16 == 15:
                text = text + '\n'
        return text


    def addObjects(self, doc):
        """Makes and returns one or more PDF objects to be added
        to the document.  The caller supplies the internal name
        to be used (typically F1, F2... in sequence) """
        # avoid circular imports - this cannot go at module level
        from reportlab.pdfbase import pdfdoc

        # construct a Type 1 Font internal object
        internalName = 'F' + repr(len(doc.fontMapping)+1)
        pdfFont = pdfdoc.PDFType1Font()
        pdfFont.Name = internalName
        pdfFont.BaseFont = self.face.name
        pdfFont.__Comment__ = 'Font %s' % self.name
        pdfFont.Encoding = self.encoding.makePDFObject()

        # is it a built-in one?  if not, need more stuff.
        if not self.face.name in _fontdata.standardFonts:
            pdfFont.FirstChar = 0
            pdfFont.LastChar = 255
            pdfFont.Widths = pdfdoc.PDFArray(self.widths)
            pdfFont.FontDescriptor = self.face.addObjects(doc)
        # now link it in
        ref = doc.Reference(pdfFont, internalName)

        # also refer to it in the BasicFonts dictionary
        fontDict = doc.idToObject['BasicFonts'].dict
        fontDict[internalName] = pdfFont

        # and in the font mappings
        doc.fontMapping[self.name] = '/' + internalName


class EmbeddedType1Face(TypeFace):
    """A Type 1 font other than one of the basic 14.

    Its glyph data will be embedded in the PDF file."""
    def __init__(self, afmFileName, pfbFileName):
        # ignore afm file for now
        self.afmFileName = afmFileName
        self.pfbFileName = pfbFileName
        self.requiredEncoding = None
        self._loadGlyphs(pfbFileName)
        self._loadMetrics(afmFileName)


    def _loadGlyphs(self, pfbFileName):
        """Loads in binary glyph data, and finds the four length
        measurements needed for the font descriptor"""
        assert os.path.isfile(pfbFileName), 'file %s not found'
        rawdata = open(pfbFileName, 'rb').read()
        self._binaryData = rawdata
        firstPS = string.find(rawdata, '%!PS')
        self._length = len(rawdata)
        self._length1 = string.find(rawdata, 'eexec')
        pos2 = string.find(rawdata, 'cleartomark')
        if pos2 < 0:
            # need to append the zeros
            rawdata = rawdata + '0'*256 + 'cleartomark'
            pos2 = string.find(rawdata, 'cleartomark')
        zeroes = 0
        while zeroes < 512:
            pos2 = pos2 - 1
            if rawdata[pos2] == '0':
                zeroes = zeroes + 1
        self._length2 = pos2 - self._length1
        self._length3 = len(rawdata) - pos2


    def _loadMetrics(self, afmFileName):
        """Loads in and parses font metrics"""
        #assert os.path.isfile(afmFileName), "AFM file %s not found" % afmFileName
        (topLevel, glyphData) = parseAFMFile(afmFileName)

        self.name = topLevel['FontName']

        self.ascent = topLevel.get('Ascender', 1000)
        self.descent = topLevel.get('Descender', 0)
        self.capHeight = topLevel.get('CapHeight', 1000)
        self.italicAngle = topLevel.get('ItalicAngle', 0)
        self.stemV = topLevel.get('stemV', 0)
        self.xHeight = topLevel.get('XHeight', 1000)
        
        strBbox = topLevel.get('FontBBox', [0,0,1000,1000])
        tokens = string.split(strBbox)
        self.bbox = []
        for tok in tokens:
            self.bbox.append(string.atoi(tok))
        
        glyphWidths = {}
        for (cid, width, name) in glyphData:
            glyphWidths[name] = width
        self.glyphWidths = glyphWidths        
        self.glyphNames = glyphWidths.keys()
        self.glyphNames.sort()

        # for font-specific encodings like Symbol, Dingbats, Carta we
        # need to make a new encoding as well....
        if topLevel.get('EncodingScheme', None) == 'FontSpecific':
            names = [None] * 256
            for (code, width, name) in glyphData:
                if code >=0 and code <=255:
                    names[code] = name
            encName = self.name + 'Encoding'
            self.requiredEncoding = encName
            enc = Encoding(encName, names)
            from reportlab.pdfbase import pdfmetrics
            pdfmetrics.registerEncoding(enc)
        
    def addObjects(self, doc):
        """Add whatever needed to PDF file, and return a FontDescriptor reference"""
        from reportlab.pdfbase import pdfdoc
        
        fontFile = pdfdoc.PDFStream()
        fontFile.content = self._binaryData
        #fontFile.dictionary['Length'] = self._length
        fontFile.dictionary['Length1'] = self._length1
        fontFile.dictionary['Length2'] = self._length2
        fontFile.dictionary['Length3'] = self._length3

        fontFileRef = doc.Reference(fontFile, 'fontFile:' + self.pfbFileName)

        fontDescriptor = pdfdoc.PDFDictionary({
            'Ascent':self.ascent,
            'CapHeight':self.capHeight,
            'Descent':self.descent,
            'Flags': 34,
            'FontBBox':pdfdoc.PDFArray(self.bbox),
            'FontName':pdfdoc.PDFName(self.name),
            'ItalicAngle':self.italicAngle,
            'StemV':self.stemV,
            'XHeight':self.xHeight,
            'FontFile': fontFileRef
            })
        fontDescriptorRef = doc.Reference(fontDescriptor, 'fontDescriptor:' + self.name)    
        return fontDescriptorRef
