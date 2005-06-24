from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses, outputfile, printLocation

from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics


class EncodingTestCase(unittest.TestCase):
    "Make documents with custom encodings"

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
    return makeSuiteForClasses(EncodingTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
