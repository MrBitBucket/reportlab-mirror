#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/test/test_pdfbase_pdfmetrics.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/test_pdfbase_pdfmetrics.py,v 1.6 2001/04/18 10:48:50 rgbecker Exp $
#test_pdfbase_pdfmetrics_widths
"""
Various tests for PDF metrics.

The main test prints out a PDF documents enabling checking of widths of every
glyph in every standard font.  Long!
"""
from reportlab.test import unittest

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import _fontdata
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors

verbose = 0
fontNamesToTest = _fontdata.standardFonts #[0:12]  #leaves out Symbol and Dingbats for now

def decoratePage(c, header):
    c.setFont('Helvetica-Oblique',10)
    c.drawString(72, 800, header)
    c.drawCentredString(297, 54, 'Page %d' % c.getPageNumber())

def makeWidthTestForAllGlyphs(canv, fontName):
    """New page, then runs down doing all the glyphs in one encoding"""
    canv.setFont('Helvetica-Bold', 20)
    title = 'Glyph Width Test for font %s' % fontName
    canv.drawString(80, 750,  title)
    canv.setFont('Helvetica-Oblique',10)
    canv.drawCentredString(297, 54, 'Page %d' % canv.getPageNumber())

    # put it in the outline
    canv.bookmarkPage('GlyphWidths:' + fontName)
    canv.addOutlineEntry(fontName,'GlyphWidths:' + fontName, level=1)

    y = 720
    thisFont = pdfmetrics.getFont(fontName)
    widths = thisFont.widths
    glyphNames = thisFont.encoding.vector
    # need to get the right list of names for the font in question
    for i in range(256):
        if y < 72:
            canv.showPage()
            decoratePage(canv, title)
            y = 750
        glyphName = glyphNames[i]
        if glyphName is not None:
            canv.setFont('Helvetica', 10)
            canv.drawString(80, y, '%03d   %s ' % (i, glyphName))
            try:
                glyphWidth = thisFont.face.glyphWidths[glyphName]
                canv.setFont(fontName, 10)
                canv.drawString(200, y, chr(i) * 30)

                # now work out width and put a red marker next to the end.
                w = canv.stringWidth(chr(i) * 30, fontName, 10)
                canv.setFillColor(colors.red)
                canv.rect(200 + w, y-1, 5, 10, stroke=0, fill=1)
                canv.setFillColor(colors.black)
            except KeyError:
                canv.drawString(200, y, 'Could not find glyph named "%s"' % glyphName)
            y = y - 12
                


def makeTestDoc(fontNames):
    filename = 'test_pdfbase_pdfmetrics.pdf'
    c = Canvas(filename)
    c.bookmarkPage('Glyph Width Tests')
    c.showOutline()
    c.addOutlineEntry('Glyph Width Tests', 'Glyph Width Tests', level=0)
    if verbose:
        print   # get it on a different line to the unittest log output.
    for fontName in fontNames:
        if verbose:
            print 'width test for', fontName
    
        makeWidthTestForAllGlyphs(c, fontName)
        c.showPage()
    c.save()
    if verbose:
        if verbose:
            print 'saved',filename

class PDFMetricsTestCase(unittest.TestCase):
    "Test various encodings used in PDF files."
    def testGlyphWidthsAreCorrect(self):
        "Visual test for glyph widths"
        makeTestDoc(fontNamesToTest)        

def makeSuite():
    return unittest.makeSuite(PDFMetricsTestCase,'test')


#noruntests
if __name__=='__main__':
    usage = """Usage:
    (1) test_pdfbase_pdfmetrics.py     -  makes doc for all standard fonts
    (2) test_pdfbase_pdfmetrics.py fontname - " " for just one font."""
    import sys
    verbose = 1
    global fontNamesToTest
    # accept font names as arguments; otherwise it does the lot
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if not arg in fontNamesToTest:
                print 'unknown font %s' % arg
                print usage
                sys.exit(0)
                
        fontNamesToTest = sys.argv[1:]

    runner = unittest.TextTestRunner()
    runner.run(makeSuite())
