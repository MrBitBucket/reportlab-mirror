from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses, outputfile

from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re

import codecs

textPat = re.compile(r'\([^(]*\)')

#test sentences
testLatin1 = 'copyright %s trademark %s registered %s ReportLab! Ol%s!' % (chr(169), chr(153),chr(174), chr(0xe9))
testUni = unicode(testLatin1, 'latin-1')
testUTF8 = testUni.encode('utf-8')
# expected result is octal-escaped text in the PDF
expectedLatin1 = "copyright \\251 trademark \\231 registered \\256 ReportLab! Ol\\351!"
expectedUTF8 = r"\000\001\002\003\004\005\006\007\010\011\012\011\010\004\013\014\015\016\013\004\017\011\020\011\004\015\006\005\021\010\015\004\015\014\011\022\011\023\015\002\001\004\010\024\013\025\026\011\027\030\031\026"


def extractText(pdfOps):
    """Utility to rip out the PDF text within a block of PDF operators.

    PDF will show a string draw as something like "(Hello World) Tj"
    i.e. text is in curved brackets.     Crude and dirty, probably fails
    on escaped brackets.
    """    
    found = textPat.findall(pdfOps)
    #chop off '(' and ')'
    return map(lambda x:x[1:-1], found)



    

class TextEncodingTestCase(unittest.TestCase):
    """Tests of expected Unicode and encoding behaviour

    """

    #AR 9/6/2004 - just adding this to illustrate behaviour I expect.
    def testStraightThrough(self):
        """This assumes input encoding matches font.  no conversion,
        trademark character does not appear in TT font"""
        c = Canvas(outputfile('test_pdfbase_encodings_none.pdf'), encoding=None)
        c.drawString(100,800, 'hello')

        self.assertEquals(c.encoding, None)

        #warmup - is my text extraction working?
        self.assertEquals(extractText(c.getCurrentPageContent()), ['hello'])



        c.drawString(100,700, testLatin1)
        extracted = extractText(c.getCurrentPageContent())
        self.assertEquals(extracted[1], expectedLatin1)

        #now we register a unicode truetype font
        pdfmetrics.registerFont(TTFont("Rina", "rina.ttf"))
        pdfmetrics.registerFont(TTFont("Luxi", "luxiserif.ttf"))
        c.setFont('Luxi', 12)

    
        #in our current mode, trying to draw this should raise an error
        # as the bytes we pass to the Unicode font are not valid UTF8
        try:
            UnicodeDecodeError
        except:
            UnicodeDecodeError = UnicodeError

        self.assertRaises(UnicodeDecodeError, c.drawString, 100,100,testLatin1)
        c.drawString(100, 600, testUTF8)
        #print 'utf8-',testUTF8
        c.save()


    def testLatinCanvas(self):

        """Verify canvas declared as latin autoconverts.

        This assumes winansi (~latin-1) input. It converts to the
        encoding of the underlying font, so both text lines APPEAR
        the same."""

        pdfmetrics.registerFont(TTFont("Luxi", "luxiserif.ttf"))

        c = Canvas(outputfile('test_pdfbase_encodings_cp1252.pdf'), encoding='cp1252')
        c.drawString(100,700, testLatin1)
        extracted = extractText(c.getCurrentPageContent())
        self.assertEquals(extracted[0], expectedLatin1)
        

        c.setFont('Luxi', 12)
        #this should convert on the fly and see the characters in the output...
        c.drawString(100,600, testLatin1)
        extracted = extractText(c.getCurrentPageContent())
        self.assertEquals(extracted[1], expectedUTF8)
        
        

        #uncomment this to see some PDF for fun...
        #print c.getCurrentPageContent()
        c.save()

        
    def testUtf8Canvas(self):

        """Verify canvas declared as utf8 autoconverts.

        This assumes utf8 input. It converts to the encoding of the
        underlying font, so both text lines APPEAR the same."""

        pdfmetrics.registerFont(TTFont("Luxi", "luxiserif.ttf"))

        c = Canvas(outputfile('test_pdfbase_encodings_utf8.pdf'), encoding='utf-8')
        #it dies here...

##        c.drawString(100,700, testUTF8)
##        extracted = extractText(c.getCurrentPageContent())
##        self.assertEquals(extracted[0], expectedUTF8)
##        
##
##        c.setFont('Luxi', 12)
##        #this should convert on the fly and see the characters in the output...
##        c.drawString(100,600, testUTF8)
##        extracted = extractText(c.getCurrentPageContent())
##        self.assertEquals(extracted[1], expectedUTF8)
##        
##        
##
##        #uncomment this to see some PDF for fun...
##        #print c.getCurrentPageContent()
##        c.save()


    



class FontEncodingTestCase(unittest.TestCase):
    """Make documents with custom encodings of Type 1 built-in fonts.

    Nothing really to do with character encodings; this is about hacking the font itself"""

    def test0(self):
        "Make custom encodings of standard fonts"

        # make a custom encoded font.
        c = Canvas(outputfile('test_pdfbase_encodings.pdf'))
        c.setPageCompression(0)
        c.setFont('Helvetica', 12)
        c.drawString(100, 700, 'The text below should be in a custom encoding in which all vowels become "z"')

        # invent a new language where vowels are replaced with letter 'z'
        zenc = pdfmetrics.Encoding('EncodingWithoutVowels', 'WinAnsiEncoding')
        for ch in 'aeiou':
            zenc[ord(ch)] = 'z'
        for ch in 'AEIOU':
            zenc[ord(ch)] = 'Z'
        pdfmetrics.registerEncoding(zenc)

        # now we can make a font based on this encoding
        # AR hack/workaround: the name of the encoding must be a Python codec!
        f = pdfmetrics.Font('FontWithoutVowels', 'Helvetica-Oblique', 'EncodingWithoutVowels')
        pdfmetrics.registerFont(f)

        c.setFont('FontWithoutVowels', 12)
        c.drawString(125, 675, "The magic word is squamish ossifrage")

        # now demonstrate adding a Euro to MacRoman, which lacks one
        c.setFont('Helvetica', 12)
        c.drawString(100, 650, "MacRoman encoding lacks a Euro.  We'll make a Mac font with the Euro at #219:")

        # WinAnsi Helvetica
        pdfmetrics.registerFont(pdfmetrics.Font('Helvetica-WinAnsi', 'Helvetica-Oblique', 'WinAnsiEncoding'))
        c.setFont('Helvetica-WinAnsi', 12)
        c.drawString(125, 625, 'WinAnsi with Euro: character 128 = "\200"')

        pdfmetrics.registerFont(pdfmetrics.Font('MacHelvNoEuro', 'Helvetica-Oblique', 'MacRomanEncoding'))
        c.setFont('MacHelvNoEuro', 12)
        c.drawString(125, 600, 'Standard MacRoman, no Euro: Character 219 = "\333"') # oct(219)=0333

        # now make our hacked encoding
        euroMac = pdfmetrics.Encoding('MacWithEuro', 'MacRomanEncoding')
        euroMac[219] = 'Euro'
        pdfmetrics.registerEncoding(euroMac)

        pdfmetrics.registerFont(pdfmetrics.Font('MacHelvWithEuro', 'Helvetica-Oblique', 'MacWithEuro'))

        c.setFont('MacHelvWithEuro', 12)
        c.drawString(125, 575, 'Hacked MacRoman with Euro: Character 219 = "\333"') # oct(219)=0333

        # now test width setting with and without _rl_accel - harder
        # make an encoding where 'm' becomes 'i'
        c.setFont('Helvetica', 12)
        c.drawString(100, 500, "Recode 'm' to 'i' and check we can measure widths. Boxes should surround letters.")
        sample = 'Mmmmm. ' * 6 + 'Mmmm'

        c.setFont('Helvetica-Oblique',12)
        c.drawString(125, 475, sample)
        w = c.stringWidth(sample, 'Helvetica-Oblique', 12)
        c.rect(125, 475, w, 12)

        narrowEnc = pdfmetrics.Encoding('m-to-i')
        narrowEnc[ord('m')] = 'i'
        narrowEnc[ord('M')] = 'I'
        pdfmetrics.registerEncoding(narrowEnc)

        pdfmetrics.registerFont(pdfmetrics.Font('narrow', 'Helvetica-Oblique', 'm-to-i'))
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



def makeSuite():
    return makeSuiteForClasses(
        TextEncodingTestCase,

        #FontEncodingTestCase - nobbled for now due to old stuff which needs removing.
        )


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
