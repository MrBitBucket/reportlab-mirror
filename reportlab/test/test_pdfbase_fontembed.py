import os
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.test import unittest
from reportlab.pdfgen import fonts

class EmbeddingTestCase(unittest.TestCase):
    "Make documents with embedded fonts"
    def testEmbedding(self):
        "Make documents with embedded fonts"
        # to avoid lawsuits, the test directory does not contain any fonts.
        # RL staff can copy a couple in from users/andy/fontembed.  Just
        # Van Rossum is going to send us one we can distribute.

        ok = 1
        for filename in ('GDB_____.AFM','GDB_____.PFB',
                         'CR______.AFM','CR______.PFB'):
            if not os.path.isfile(filename):
                ok = 0
        if not ok:
            print '\n test font files not present, skipping...'
            return
        
        c = Canvas('test_pdfbase_fontembed.pdf')
        c.setPageCompression(0)
        c.setFont('Helvetica', 12)
        c.drawString(100, 700, 'This is Helvetica.  The text below should be different fonts...')


        # a normal text font
        garaFace = fonts.EmbeddedType1Face('GDB_____.AFM','GDB_____.PFB')
        faceName = 'AGaramond-Bold'  # pulled from AFM file
        pdfmetrics.registerTypeFace(garaFace)

        garaFont = pdfmetrics.Font('MyGaramondBold', faceName, 'WinAnsiEncoding')
        pdfmetrics.registerFont(garaFont)

        c.setFont('AGaramond-Bold', 12)
        c.drawString(100, 650, 'This should be in AGaramond-Bold')
        
        # one with a custom encoding
        cartaFace = fonts.EmbeddedType1Face('CR______.AFM','CR______.PFB')
        faceName = 'Carta'  # pulled from AFM file
        pdfmetrics.registerTypeFace(cartaFace)

        cartaFont = pdfmetrics.Font('Carta', 'Carta', 'CartaEncoding')
        pdfmetrics.registerFont(cartaFont)


        text = 'This should be in Carta, a map symbol font:'
        c.setFont('Helvetica', 12)
        c.drawString(100, 600, text)
        w = c.stringWidth(text, 'Helvetica', 12)
        
        c.setFont('Carta', 12)
        c.drawString(100+w, 600, ' Hello World')
                

        c.save()



def makeSuite():
    suite = unittest.TestSuite()
    suite.addTest(EmbeddingTestCase('testEmbedding'))
    return suite

    
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())

