#copyright ReportLab Inc. 2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/pdfbase/pdfmetrics.py?cvsroot=reportlab
#$Header $
__version__=''' $Id: pdfmetrics.py,v 1.33 2001/04/20 05:52:05 rgbecker Exp $ '''
__doc__=""" 
This provides a database of font metric information.

It is independent of the canvas or any particular context.  It keeps
a registry of Font, TypeFace and Encoding objects.  Ideally these
would be pre-loaded, but due to a nasty circularity problem we
trap attempts to access them and do it on first access.
"""
import string
from types import StringType, ListType, TupleType
from reportlab.rl_config import defaultEncoding
from reportlab.pdfbase import _fontdata
from reportlab.lib.logger import warnOnce
from reportlab.pdfgen.fonts import FontError, FontNotFoundError, TypeFace, Encoding, Font


# conditional import - try both import techniques, and set a flag
_dummyEncoding=' _not an encoding_ '
try:
    try:
        from reportlab.lib import _rl_accel
## I don't get exactly the message given so this bombs for me
##    except ImportError, errMsg:
##        if str(errMsg)!='cannot import name _rl_accel': raise
    except ImportError:
        import _rl_accel
    assert _rl_accel.version>="0.3", "bad _rl_accel"
    _stringWidth = _rl_accel.stringWidth
    _rl_accel.defaultEncoding(_dummyEncoding)
    #del widthVectorsByFont
except ImportError, errMsg:
    if str(errMsg)!='No module named _rl_accel': raise
    _stringWidth = None



_typefaces = {}
_encodings = {}
_fonts = {}

def registerTypeFace(face):
    assert isinstance(face, TypeFace), 'Not a TypeFace: %s' % face
    _typefaces[face.name] = face

def registerEncoding(enc):
    assert isinstance(enc, Encoding), 'Not an Encoding: %s' % enc
    if _encodings.has_key(enc.name):
        # already got one, complain if they are not the same
        if enc.isEqual(_encodings[enc.name]):
            enc.freeze()
        else:
            raise FontError('Encoding "%s" already registered with a different name vector!' % enc.Name)
    else:
        _encodings[enc.name] = enc
        enc.freeze()
    # have not yet dealt with immutability!

def registerFont(font):
    "Registers a font, including setting up info for accelerated stringWidth"
    #assert isinstance(font, Font), 'Not a Font: %s' % font
    _fonts[font.name] = font
    if _stringWidth:
        #TODO - add the accelerator info
        _rl_accel.setFontInfo(string.lower(font.name),
                              _dummyEncoding,
                              font.face.ascent,
                              font.face.descent,
                              font.widths)
        

def getTypeFace(faceName):
    """Lazily construct known typefaces if not found"""
    try:
        return _typefaces[faceName]
    except KeyError:
        # not found, construct it if known
        if faceName in _fontdata.standardFonts:
            face = TypeFace(faceName)
            registerTypeFace(face)
            #print 'auto-constructing type face %s' % face.name
            return face
        else:
            raise
        
def getEncoding(encName):
    """Lazily construct known encodings if not found"""
    try:
        return _encodings[encName]
    except KeyError:
        if encName in _fontdata.standardEncodings:
            enc = Encoding(encName)
            registerEncoding(enc)
            #print 'auto-constructing encoding %s' % encName
            return enc
        else:
            raise
    
def getFont(fontName):
    """Lazily constructs known fonts if not found.

    Names of form 'face-encoding' will be built if
    face and encoding are known.  Also if the name is
    just one of the standard 14, it will make up a font
    in the default encoding."""
    try:
        return _fonts[fontName]
    except KeyError:
        #it might have a font-specific encoding e.g. Symbol
        # or Dingbats.  If not, take the default.
        face = getTypeFace(fontName)
        if face.requiredEncoding:
            font = Font(fontName, fontName, face.requiredEncoding)
        else:
            font = Font(fontName, fontName, defaultEncoding)
        registerFont(font)
        return font

    
        
def _slowStringWidth(text, fontName, fontSize):
    """Define this anyway so it can be tested, but whether it is used or not depends on _rl_accel"""
    font = getFont(fontName)
    return font.stringWidth(text, fontSize)
    #this is faster, but will need more special-casing for multi-byte fonts. 
    #wid = getFont(fontName).widths
    #w = 0
    #for ch in text:
    #    w = w + wid[ord(ch)]
    #return 0.001 * w * fontSize


if _stringWidth:
    import new
    #Font.stringWidth = new.instancemethod(_rl_accel._instanceStringWidth,None,Font)
    stringWidth = _stringWidth

    def _SWRecover(text, fontName, fontSize, encoding):
        '''This is called when _rl_accel's database doesn't know about a font.
        Currently encoding is always a dummy.
        '''
        try:
            font = getFont(fontName)
            registerFont(font)
            #print 'registered font %s' % fontName
            #dumpFontData()
            return _stringWidth(text,fontName,fontSize,encoding)
        except:
            warnOnce('Font %s:%s not found - using Courier:%s for widths'%(fontName,encoding,encoding))
            return _stringWidth(text,'courier',fontSize,encoding)

    _rl_accel._SWRecover(_SWRecover)
else:
    stringWidth = _slowStringWidth
    


def dumpFontData():
    print 'Registered Encodings:'
    keys = _encodings.keys()
    keys.sort()
    for encName in keys:
        print '   ',encName

    print
    print 'Registered Typefaces:'
    faces = _typefaces.keys()
    faces.sort()
    for faceName in faces:
        print '   ',faceName


    print
    print 'Registered Fonts:'
    k = _fonts.keys()
    k.sort()
    for key in k:
        font = _fonts[key]
        print '    %s (%s/%s)' % (font.name, font.face.name, font.encoding.name)



def test3widths(texts):
    # checks all 3 algorithms give same answer, note speed
    import time
    for fontName in _fontdata.standardFonts[0:1]:
        t0 = time.time()
        for text in texts:
            l1 = _stringWidth(text, fontName, 10)
        t1 = time.time()
        print 'fast stringWidth took %0.4f' % (t1 - t0)

        t0 = time.time()
        w = getFont(fontName).widths
        for text in texts:
            l2 = 0
            for ch in text:
                l2 = l2 + w[ord(ch)]
        t1 = time.time()
        print 'slow stringWidth took %0.4f' % (t1 - t0)
        
        t0 = time.time()
        for text in texts:
            l3 = getFont(fontName).stringWidth(text, 10)
        t1 = time.time()
        print 'class lookup and stringWidth took %0.4f' % (t1 - t0)
        print

def testStringWidthAlgorithms():
    rawdata = open('../../rlextra/rml2pdf/doc/rml_user_guide.rml').read()
    print 'rawdata length %d' % len(rawdata)
    print 'test one huge string...'
    test3widths([rawdata])
    print
    words = string.split(rawdata)
    print 'test %d shorter strings (average length %0.2f chars)...' % (len(words), 1.0*len(rawdata)/len(words))
    test3widths(words)
    
    
def test():
    helv = TypeFace('Helvetica')
    registerTypeFace(helv)
    print helv.glyphNames[0:30]
    
    wombat = TypeFace('Wombat')
    print wombat.glyphNames
    registerTypeFace(wombat)

    dumpFontData()

    
if __name__=='__main__':
    test()
    #testStringWidthAlgorithms()
    