#copyright ReportLab Inc. 2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/pdfbase/cidfonts?cvsroot=reportlab
#$Header $
__version__=''' $Id: cidfonts.py,v 1.1 2001/09/04 08:52:13 andy_robinson Exp $ '''
__doc__="""CID (Asian multi-byte) font support.

This defines classes to represent CID fonts.  They know how to calculate
their own width and how to write themselves into PDF files."""

import os
from types import ListType, TupleType
from string import find, split, strip

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase._cidfontdata import allowedTypeFaces, allowedEncodings, CIDFontInfo
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfdoc

## need to find CMAP files to work out widths accurately.
CMAP_DIR = None
for dirname in [
    '/usr/local/Acrobat4/Resource/CMap',
    'C:\\Program Files\\Adobe\\Acrobat\\Resource\\CMap',
    'C:\\Program Files\\Adobe\\Acrobat 4.0\\Resource\\CMap'
    ]:
    if os.path.exists(dirname):
        CMAP_DIR = dirname
        break

if CMAP_DIR is None:
    raise IOError("""Unable to find CMAP directory in any of the standard locations.
Please modify the directory list at the beginning of jpsupport.py to include
the correct directory location for your Adobe CMap files.  If you believe
your files are in a standard location, let us know and we will extend the
search path in the next release.""")

class CIDEncoding(pdfmetrics.Encoding):
    """Multi-byte encoding.  These are loaded from CMAP files.

    A CMAP file is like a mini-codec.  It defines the correspondence
    between code points in the (multi-byte) input data and Character
    IDs. """
    # aims to do similar things to Brian Hooper's CMap class,
    # but I could not get it working and had to rewrite.
    # also, we should really rearrange our current encoding
    # into a SingleByteEncoding since many of its methods
    # should not apply here.

    def __init__(self, name):
        self._codeSpaceRanges = []
        self._notDefRanges = []
        self._cmap = {}
        
        self.parseCMAPFile(name)

    def parseCMAPFile(self, name):
        """This is a tricky one as CMAP files are Postscript
        ones.  Some refer to others with a 'usecmap'
        command"""
        
        #print 'parsing cmap file for ' + name,
        cmapfile = CMAP_DIR + os.sep + name
        assert os.path.isfile(cmapfile), 'CMAP file for encodings "%s" not found!' % name

        rawdata = open(cmapfile, 'r').read()
        if len(rawdata) > 50000:
            # CMAPs for unicode have 7000+ explicit ranges, takes minutes
            # to parse.  Can we 'can' this data?
            #print 'CMAP file %s too big, needs recoding in C' % name
            return
        #if it contains the token 'usecmap', parse the other
        #cmap file first....
        usecmap_pos = find(rawdata, 'usecmap')
        if  usecmap_pos > -1:
            #they tell us to look in another file
            #for the code space ranges. The one
            # to use will be the previous word.
            chunk = rawdata[0:usecmap_pos]
            words = split(chunk)
            otherCMAPName = words[-1]
            #print 'referred to another CMAP %s' % otherCMAPName
            self.parseCMAPFile(otherCMAPName)
            # now continue parsing this, as it may
            # override some settings

        
        words = split(rawdata)
        while words <> []:
            if words[0] == 'begincodespacerange':
                words = words[1:]
                while words[0] <> 'endcodespacerange':
                    strStart, strEnd, words = words[0], words[1], words[2:]
                    start = int(strStart[1:-1], 16)
                    end = int(strEnd[1:-1], 16)
                    self._codeSpaceRanges.append((start, end),)
            elif words[0] == 'beginnotdefrange':
                words = words[1:]
                while words[0] <> 'endnotdefrange':
                    strStart, strEnd, strValue = words[0:3]
                    start = int(strStart[1:-1], 16)
                    end = int(strEnd[1:-1], 16)
                    value = int(strValue)
                    self._notDefRanges.append((start, end, value),)
                    words = words[3:]
            elif words[0] == 'begincidrange':
                words = words[1:]
                while words[0] <> 'endcidrange':
                    strStart, strEnd, strValue = words[0:3]
                    start = int(strStart[1:-1], 16)
                    end = int(strEnd[1:-1], 16)
                    value = int(strValue)
                    # this means that 'start' corresponds to 'value',
                    # start+1 corresponds to value+1 and so on up
                    # to end
                    offset = 0
                    while start + offset <= end:
                        self._cmap[start + offset] = value + offset
                        offset = offset + 1
                    words = words[3:]
                
            else:
                words = words[1:]
                
    def translate(self, text):
        "Convert a string into a list of CIDs"
        output = []
        cmap = self._cmap
        lastChar = ''
        for char in text:
            if lastChar <> '':
                #print 'convert character pair "%s"' % (lastChar + char)
                num = ord(lastChar) * 256 + ord(char)
            else:
                #print 'convert character "%s"' % char
                num = ord(char)
            lastChar = char
            found = 0
            for low, high in self._codeSpaceRanges:
                if low < num < high:
                    try:
                        cid = cmap[num]
                        #print '%d -> %d' % (num, cid)
                    except KeyError:
                        #not defined.  Try to find the appropriate
                        # notdef character, or failing that return
                        # zero
                        cid = 0
                        for low2, high2, notdef in self._notDefRanges:
                            if low2 < num < high2:
                                cid = notdef
                                break
                    output.append(cid)
                    found = 1
                    break
            if found:
                lastChar = ''
            else:
                lastChar = char
        return output
    
                    
                        

        
class CIDTypeFace(pdfmetrics.TypeFace):
    """Multi-byte type face.

    Conceptually similar to a single byte typeface,
    but the glyphs are identified by a numeric Character
    ID (CID) and not a glyph name. """
    def __init__(self, name):
        """Initialised from one of the canned dictionaries in allowedEncodings

        Or rather, it will be shortly..."""
        pdfmetrics.TypeFace.__init__(self, name)
        self._extractDictInfo(name)
    def _extractDictInfo(self, name):
        try:
            fontDict = CIDFontInfo[name]
        except KeyError:
            raise KeyError, ("Unable to find information on CID typeface '%s'" % name + 
                            "Only the following font names work:" + repr(allowedTypeFaces)
                             )
        descFont = fontDict['DescendantFonts'][0]
        self.ascent = descFont['FontDescriptor']['Ascent']
        self.descent = descFont['FontDescriptor']['Descent']
        self._defaultWidth = descFont['DW']
        self._explicitWidths = self._expandWidths(descFont['W'])

        # should really support self.glyphWidths, self.glyphNames
        # but not done yet.

        
    def _expandWidths(self, compactWidthArray):
        """Expands Adobe nested list structure to get a dictionary of widths.

        Here is an example of such a structure.
        (
            # starting at character ID 1, next n  characters have the widths given.
            1,  (277,305,500,668,668,906,727,305,445,445,508,668,305,379,305,539),
            # all Characters from ID 17 to 26 are 668 em units wide
            17, 26, 668,
            27, (305, 305, 668, 668, 668, 566, 871, 727, 637, 652, 699, 574, 555,
                 676, 687, 242, 492, 664, 582, 789, 707, 734, 582, 734, 605, 605,
                 641, 668, 727, 945, 609, 609, 574, 445, 668, 445, 668, 668, 590,
                 555, 609, 547, 602, 574, 391, 609, 582, 234, 277, 539, 234, 895,
                 582, 605, 602, 602, 387, 508, 441, 582, 562, 781, 531, 570, 555,
                 449, 246, 449, 668),
            # these must be half width katakana and the like.
            231, 632, 500
        )
        """
        data = compactWidthArray[:]
        widths = {}
        while data:
            start, data = data[0], data[1:]
            if type(data[0]) in (ListType, TupleType):
                items, data = data[0], data[1:]
                for offset in range(len(items)):
                    widths[start + offset] = items[offset]
            else:
                end, width, data = data[0], data[1], data[2:]
                for idx in range(start, end+1):
                    widths[idx] = width
        return widths

    def getCharWidth(self, characterId):
        return self._explicitWidths.get(characterId, self._defaultWidth)

class CIDFont(pdfmetrics.Font):
    def __init__(self, face, encoding):
##        self._multiByte = 1
##        self.fontName = face + '-' + encoding
##        self.face = CIDTypeFace(face)
##        self.encoding = CIDEncoding(encoding)

        self._multiByte = 1
        assert face in allowedTypeFaces, "TypeFace '%s' not supported! Use any of these instead: %s" % (face, allowedTypeFaces)
        self.faceName = face
        self.face = CIDTypeFace(face)
        self.encoding = CIDEncoding(encoding)

#        self.widths = [0.668] * 256
        assert encoding in allowedEncodings, "Encoding '%s' not supported!  Use any of these instead: %s" % (encoding, allowedEncodings)
        self.encoding = encoding

        #legacy hack doing quick cut and paste.
        self.fontName = self.faceName + '-' + self.encoding
        self.name = self.fontName
            
    def stringWidth(self, text, size):
        cidlist = self.encoding.translate(text)
        w = 0
        for cid in cidlist:
            w = w + self.face.getCharWidth(cid)
        return 0.001 * w * size


    def addObjects(self, doc):
        """The explicit code in addMichoObjects and addGothicObjects
        will be replaced by something that pulls the data from
        _cidfontdata.py in the next few days."""
        internalName = 'F' + repr(len(doc.fontMapping)+1)
        
        if self.face.name == 'HeiseiMin-W3':
            self.addMinchoObjects(doc, internalName)
        elif self.face.name == 'HeiseiKakuGo-W5':
            self.addGothicObjects(doc, internalName)
        else:
            raise Exception("Sack the programmer! Unexpected font face which should have been trapped earlier")

        doc.fontMapping[self.name] = '/' + internalName

    def addMinchoObjects(self, doc, internalName):
        """Adds the PDF objects for HeiseiMin-W3"""
        Mincho_part_3 = pdfdoc.PDFDictionary({
            'Type': '/FontDescriptor',
            'Ascent': 723,
            'CapHeight': 709,
            'Descent': -241,
            'Flags': 6,
            'FontBBox': pdfdoc.PDFArray([-123, -257, 1001, 910]),
            'FontName': '/' + self.name,
            'ItalicAngle': 0,
            'StemV': 69,
            'XHeight': 450,
            'Style': pdfdoc.PDFDictionary({'Panose': '<010502020400000000000000>'})
            })
        Mincho_part_3.__Comment__ = 'CID Font (Mincho) FontDescriptor'
        r1 = doc.Reference(Mincho_part_3)

        Mincho_part_2 = pdfdoc.PDFDictionary({
            'Type':'/Font',
            'Subtype':'/CIDFontType0',
            'BaseFont':'/' + self.name,
            'FontDescriptor': r1, # <---- here's the cross-reference
            'CIDSystemInfo': pdfdoc.PDFDictionary({
                'Registry': '(Adobe)',
                'Ordering': '(Japan1)',
                'Supplement': 2
                }),
            'DW': 1000,
            'W': pdfdoc.PDFArray([
                1, pdfdoc.PDFArray([277,305,500,668,668,906,727,305,445,445,508,668,305,379,305,539 ]),
                17, 26, 668,
                27, pdfdoc.PDFArray([305, 305, 668, 668, 668, 566, 871, 727, 637, 652, 699, 574, 555,
                                     676, 687, 242, 492, 664, 582, 789, 707, 734, 582, 734, 605, 605,
                                     641, 668, 727, 945, 609, 609, 574, 445, 668, 445, 668, 668, 590,
                                     555, 609, 547, 602, 574, 391, 609, 582, 234, 277, 539, 234, 895,
                                     582, 605, 602, 602, 387, 508, 441, 582, 562, 781, 531, 570, 555,
                                     449, 246, 449, 668]),
                231, 632, 500
                ])
            })
        Mincho_part_2.__Comment__ = 'CID Font'
        r2 = doc.Reference(Mincho_part_2)
        
        Mincho_part_1 = pdfdoc.PDFDictionary({
            'Type':'/Font',
            'Subtype':'/Type0',
            'Name': '/'+internalName, #<-- the internal name
            'BaseFont': '/' + self.fontName,
            'Encoding': '/' + self.encoding,
            'DescendantFonts': pdfdoc.PDFArray([r2])
            })
        Mincho_part_1.__Comment__ = 'CID Font Parent'
        
        r3 = doc.Reference(Mincho_part_1, internalName)

                # also refer to it in the BasicFonts dictionary
        fontDict = doc.idToObject['BasicFonts'].dict
        fontDict[internalName] = r3
    

    def addGothicObjects(self, doc, internalName):
        """Adds the PDF objects for HeiseiKakuGo-W5"""
        Gothic_part_3 = pdfdoc.PDFDictionary({
            'Type': '/FontDescriptor',
            'Ascent': 752,
            'CapHeight': 737,
            'Descent': -221,
            'Flags': 4,
            'FontBBox': pdfdoc.PDFArray([-92, -250, 1010, 922]),
            'FontName': '/' + self.faceName,
            'ItalicAngle': 0,
            'StemV': 114,
            'XHeight': 553,
            'Style': pdfdoc.PDFDictionary({'Panose': '<0801020b0600000000000000>'})
            })
        Gothic_part_3.__Comment__ = 'CID Font (Mincho) FontDescriptor'
        r1 = doc.Reference(Gothic_part_3)

        Gothic_part_2 = pdfdoc.PDFDictionary({
            'Type':'/Font',
            'Subtype':'/CIDFontType0',
            'BaseFont':'/' + self.faceName,
            'FontDescriptor': r1, # <---- here's the cross-reference
            'CIDSystemInfo': pdfdoc.PDFDictionary({
                'Registry': '(Adobe)',
                'Ordering': '(Japan1)',
                'Supplement': 2
                }),
            'DW': 1000,
            'W': pdfdoc.PDFArray([
                1, pdfdoc.PDFArray([277,305,500,668,668,906,727,305,445,445,508,668,305,379,305,539 ]),
                17, 26, 668,
                27, pdfdoc.PDFArray([305, 305, 668, 668, 668, 566, 871, 727, 637, 652, 699, 574, 555,
                                     676, 687, 242, 492, 664, 582, 789, 707, 734, 582, 734, 605, 605,
                                     641, 668, 727, 945, 609, 609, 574, 445, 668, 445, 668, 668, 590,
                                     555, 609, 547, 602, 574, 391, 609, 582, 234, 277, 539, 234, 895,
                                     582, 605, 602, 602, 387, 508, 441, 582, 562, 781, 531, 570, 555,
                                     449, 246, 449, 668]),
                231, 632, 500
                ])
            })
        Gothic_part_2.__Comment__ = 'CID Font'
        r2 = doc.Reference(Gothic_part_2)
        
        Gothic_part_1 = pdfdoc.PDFDictionary({
            'Type':'/Font',
            'Subtype':'/Type0',
            'Name': '/'+internalName, #<-- the internal name
            'BaseFont': '/' + self.name,
            'Encoding': '/' + self.encoding,
            'DescendantFonts': pdfdoc.PDFArray([r2])
            })
        Gothic_part_1.__Comment__ = 'CID Font Parent'
        
        r3 = doc.Reference(Gothic_part_1, internalName)

                # also refer to it in the BasicFonts dictionary
        fontDict = doc.idToObject['BasicFonts'].dict
        fontDict[internalName] = r3
    
def test():
    c = Canvas('test_japanese.pdf')
    c.setFont('Helvetica', 30)
    c.drawString(100,700, 'Japanese Font Support')

    pdfmetrics.registerFont(CIDFont('HeiseiMin-W3','90ms-RKSJ-H'))
    pdfmetrics.registerFont(CIDFont('HeiseiKakuGo-W5','90ms-RKSJ-H'))

    # the two typefaces
    c.setFont('HeiseiMin-W3-90ms-RKSJ-H', 16)
    # this says "This is HeiseiMincho" in shift-JIS.  Not all our readers
    # have a Japanese PC, so I escaped it. On a Japanese-capable
    # system, print the string to see Kanji
    message1 = '\202\261\202\352\202\315\225\275\220\254\226\276\222\251\202\305\202\267\201B'
    c.drawString(100, 675, message1)
    c.save()
    print 'saved test_japanese.pdf'
##    print 'CMAP_DIR = ', CMAP_DIR
##    tf1 = CIDTypeFace('HeiseiMin-W3')
##    print 'ascent = ',tf1.ascent
##    print 'descent = ',tf1.descent
##    for cid in [1,2,3,4,5,18,19,28,231,1742]:
##        print 'width of cid %d = %d' % (cid, tf1.getCharWidth(cid))

    encName = '90ms-RKSJ-H'
    enc = CIDEncoding(encName)
    print message1, '->', enc.translate(message1)
    
    f = CIDFont('HeiseiMin-W3','90ms-RKSJ-H')
    print 'width = %0.2f' % f.stringWidth(message1, 10)


    #testing all encodings
##    import time
##    started = time.time()
##    import glob
##    for encName in _cidfontdata.allowedEncodings:
##    #encName = '90ms-RKSJ-H'
##        enc = CIDEncoding(encName)
##        print 'encoding %s:' % encName
##        print '    codeSpaceRanges = %s' % enc._codeSpaceRanges
##        print '    notDefRanges = %s' % enc._notDefRanges
##        print '    mapping size = %d' % len(enc._cmap)
##    finished = time.time()
##    print 'constructed all encodings in %0.2f seconds' % (finished - started)
    
if __name__=='__main__':
    test()

    



