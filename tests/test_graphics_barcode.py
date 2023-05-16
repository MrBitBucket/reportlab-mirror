#Copyright ReportLab Europe Ltd. 2000-2017
#see license.txt for license details
"""
Tests for barcodes
"""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation, haveRenderPM
setOutDir(__name__)
import unittest, os, sys, glob, time

from reportlab import Version as __RL_Version__
from reportlab.graphics.barcode.common import *
from reportlab.graphics.barcode.code39 import *
from reportlab.graphics.barcode.code93 import *
from reportlab.graphics.barcode.code128 import *
from reportlab.graphics.barcode.usps import *
from reportlab.graphics.barcode.usps4s import USPS_4State
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.barcode.dmtx import DataMatrixWidget, pylibdmtx


from reportlab.platypus import Spacer, SimpleDocTemplate, Table, TableStyle, Preformatted, PageBreak
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.utils import TimeStamp

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.frames import Frame
from reportlab.platypus.flowables import XBox, KeepTogether
from reportlab.graphics.shapes import Drawing, Rect, Line

from reportlab.graphics.barcode import getCodes, getCodeNames, createBarcodeDrawing, createBarcodeImageInMemory
def run(fileName):
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']
    story = []
    storyAdd = story.append

    #for codeNames in code
    storyAdd(Paragraph('I2of5', styleN))
    storyAdd(I2of5(1234, barWidth = inch*0.02, checksum=0))

    storyAdd(Paragraph('MSI', styleN))
    storyAdd(MSI(1234))

    storyAdd(Paragraph('Codabar', styleN))
    storyAdd(Codabar("A012345B", barWidth = inch*0.02))

    storyAdd(Paragraph('Code 11', styleN))
    storyAdd(Code11("01234545634563"))

    storyAdd(Paragraph('Code 39', styleN))
    storyAdd(Standard39("A012345B%R"))

    storyAdd(Paragraph('Extended Code 39', styleN))
    storyAdd(Extended39("A012345B}"))

    storyAdd(Paragraph('Code93', styleN))
    storyAdd(Standard93("CODE 93"))

    storyAdd(Paragraph('Extended Code93', styleN))
    storyAdd(Extended93("L@@K! Code 93 :-)")) #, barWidth=0.005 * inch))

    storyAdd(Paragraph('Code 128', styleN))
    storyAdd(Code128("AB-12345678"))

    storyAdd(Paragraph('Code 128 Auto', styleN))
    storyAdd(Code128Auto("AB-12345678"))

    storyAdd(Paragraph('USPS FIM', styleN))
    storyAdd(FIM("A"))

    storyAdd(Paragraph('USPS POSTNET', styleN))
    storyAdd(POSTNET('78247-1043'))

    storyAdd(Paragraph('USPS 4 State', styleN))
    storyAdd(USPS_4State('01234567094987654321','01234567891'))

    from reportlab.graphics.barcode import createBarcodeDrawing

    storyAdd(Paragraph('EAN13', styleN))
    storyAdd(createBarcodeDrawing('EAN13', value='123456789012'))

    storyAdd(Paragraph('EAN13 quiet=False', styleN))
    storyAdd(createBarcodeDrawing('EAN13', value='123456789012', quiet=False))

    storyAdd(Paragraph('EAN8', styleN))
    storyAdd(createBarcodeDrawing('EAN8', value='1234567'))

    storyAdd(PageBreak())

    storyAdd(Paragraph('EAN5 price=True', styleN))
    storyAdd(createBarcodeDrawing('EAN5', value='11299', price=True))

    storyAdd(Paragraph('EAN5 price=True quiet=False', styleN))
    storyAdd(createBarcodeDrawing('EAN5', value='11299', price=True, quiet=False))

    storyAdd(Paragraph('EAN5 price=False', styleN))
    storyAdd(createBarcodeDrawing('EAN5', value='11299', price=False))

    storyAdd(Paragraph('ISBN alone', styleN))
    storyAdd(createBarcodeDrawing('ISBN', value='9781565924796'))

    storyAdd(Paragraph('ISBN  with ean5 price', styleN))
    storyAdd(createBarcodeDrawing('ISBN', value='9781565924796',price='01299'))

    storyAdd(Paragraph('ISBN  with ean5 price, quiet=False', styleN))
    storyAdd(createBarcodeDrawing('ISBN', value='9781565924796',price='01299',quiet=False))

    storyAdd(Paragraph('UPCA', styleN))
    storyAdd(createBarcodeDrawing('UPCA', value='03600029145'))

    storyAdd(Paragraph('USPS_4State', styleN))
    storyAdd(createBarcodeDrawing('USPS_4State', value='01234567094987654321',routing='01234567891'))

    storyAdd(Paragraph('QR', styleN))
    storyAdd(createBarcodeDrawing('QR', value='01234567094987654321'))

    storyAdd(Paragraph('QR', styleN))
    storyAdd(createBarcodeDrawing('QR', value='01234567094987654321',x=30,y=50))

    def addCross(d,x,y,w=5,h=5, strokeColor='black', strokeWidth=0.5):
        w *= 0.5
        h *= 0.5
        d.add(Line(x-w,y,x+w,y,strokeWidth=0.5,strokeColor=colors.blue))
        d.add(Line(x, y-h, x, y+h,strokeWidth=0.5,strokeColor=colors.blue))
    storyAdd(Paragraph('QR in drawing at (0,0)', styleN))
    d = Drawing(100,100)
    d.add(Rect(0,0,100,100,strokeWidth=1,strokeColor=colors.red,fillColor=None))
    d.add(QrCodeWidget(value='01234567094987654321'))
    storyAdd(d)

    storyAdd(Paragraph('QR in drawing at (10,10)', styleN))
    d = Drawing(100,100)
    d.add(Rect(0,0,100,100,strokeWidth=1,strokeColor=colors.red,fillColor=None))
    addCross(d,10,10)
    d.add(QrCodeWidget(value='01234567094987654321',x=10,y=10))
    storyAdd(d)

    storyAdd(Paragraph('Label Size', styleN))
    storyAdd(XBox((2.0 + 5.0/8.0)*inch, 1 * inch, '1x2-5/8"'))

    storyAdd(Paragraph('Label Size', styleN))
    storyAdd(XBox((1.75)*inch, .5 * inch, '1/2x1-3/4"'))

    if pylibdmtx:
        storyAdd(PageBreak())
        storyAdd(Paragraph('DataMatrix in drawing at (10,10)', styleN))
        d = Drawing(100,100)
        d.add(Rect(0,0,100,100,strokeWidth=1,strokeColor=colors.red,fillColor=None))
        addCross(d,10,10)
        d.add(DataMatrixWidget(value='1234567890',x=10,y=10))
        storyAdd(d)
        storyAdd(Paragraph('DataMatrix in drawing at (10,10)', styleN))
        d = Drawing(100,100)
        d.add(Rect(0,0,100,100,strokeWidth=1,strokeColor=colors.red,fillColor=None))
        addCross(d,10,10)
        d.add(DataMatrixWidget(value='1234567890',x=10,y=10,color='black',bgColor='lime'))
        storyAdd(d)

        storyAdd(Paragraph('DataMatrix in drawing at (90,90) anchor=ne', styleN))
        d = Drawing(100,100)
        d.add(Rect(0,0,100,100,strokeWidth=1,strokeColor=colors.red,fillColor=None))
        addCross(d,90,90)
        d.add(DataMatrixWidget(value='1234567890',x=90,y=90,color='darkblue',bgColor='yellow', anchor='ne'))
        storyAdd(d)
    

    SimpleDocTemplate(fileName).build(story)

def fullTest(fileName):
    """Creates large-ish test document with a variety of parameters"""

    story = []

    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']
    styleH2 = styles['Heading2']
    story = []

    story.append(Paragraph('ReportLab %s Barcode Test Suite - full output' % __RL_Version__,styleH))
    story.append(Paragraph('Generated at %s' % TimeStamp().asctime, styleN))

    story.append(Paragraph('About this document', styleH2))
    story.append(Paragraph('History and Status', styleH2))

    story.append(Paragraph("""
        This is the test suite and docoumentation for the ReportLab open source barcode API.
        """, styleN))

    story.append(Paragraph("""
        Several years ago Ty Sarna contributed a barcode module to the ReportLab community.
        Several of the codes were used by him in hiw work and to the best of our knowledge
        this was correct.  These were written as flowable objects and were available in PDFs,
        but not in our graphics framework.  However, we had no knowledge of barcodes ourselves
        and did not advertise or extend the package.
        """, styleN))

    story.append(Paragraph("""
        We "wrapped" the barcodes to be usable within our graphics framework; they are now available
        as Drawing objects which can be rendered to EPS files or bitmaps.  For the last 2 years this
        has been available in our Diagra and Report Markup Language products.  However, we did not
        charge separately and use was on an "as is" basis.
        """, styleN))

    story.append(Paragraph("""
        A major licensee of our technology has kindly agreed to part-fund proper productisation
        of this code on an open source basis in Q1 2006.  This has involved addition of EAN codes
        as well as a proper testing program.  Henceforth we intend to publicise the code more widely,
        gather feedback, accept contributions of code and treat it as "supported".  
        """, styleN))

    story.append(Paragraph("""
        This involved making available both downloads and testing resources.  This PDF document
        is the output of the current test suite.  It contains codes you can scan (if you use a nice sharp
        laser printer!), and will be extended over coming weeks to include usage examples and notes on
        each barcode and how widely tested they are.  This is being done through documentation strings in
        the barcode objects themselves so should always be up to date.
        """, styleN))

    story.append(Paragraph('Usage examples', styleH2))
    story.append(Paragraph("""
        To be completed
        """, styleN))

    story.append(Paragraph('The codes', styleH2))
    story.append(Paragraph("""
        Below we show a scannable code from each barcode, with and without human-readable text.
        These are magnified about 2x from the natural size done by the original author to aid
        inspection.  This will be expanded to include several test cases per code, and to add
        explanations of checksums.  Be aware that (a) if you enter numeric codes which are too
        short they may be prefixed for you (e.g. "123" for an 8-digit code becomes "00000123"),
        and that the scanned results and readable text will generally include extra checksums
        at the end.
        """, styleN))

    codeNames = getCodeNames()
    from reportlab.lib.utils import flatten
    width = [float(x[8:]) for x in sys.argv if x.startswith('--width=')]
    height = [float(x[9:]) for x in sys.argv if x.startswith('--height=')]
    isoScale = [int(x[11:]) for x in sys.argv if x.startswith('--isoscale=')]
    options = {}
    if width: options['width'] = width[0]
    if height: options['height'] = height[0]
    if isoScale: options['isoScale'] = isoScale[0]
    scales = [x[8:].split(',') for x in sys.argv if x.startswith('--scale=')]
    scales = list(map(float,scales and flatten(scales) or [1]))
    scales = list(map(float,scales and flatten(scales) or [1]))
    for scale in scales:
        story.append(PageBreak())
        story.append(Paragraph('Scale = %.1f'%scale, styleH2))
        story.append(Spacer(36, 12))
        for codeName in codeNames:
            s = [Paragraph('Code: ' + codeName, styleH2)]
            for hr in (0,1):
                s.append(Spacer(36, 12))
                dr = createBarcodeDrawing(codeName, humanReadable=hr,**options)
                dr.renderScale = scale
                s.append(dr)
                s.append(Spacer(36, 12))
            s.append(Paragraph('Barcode should say: ' + dr._bc.value, styleN))
            story.append(KeepTogether(s))

    SimpleDocTemplate(fileName).build(story)

try:
    from reportlab.graphics import renderPM
    if not haveRenderPM(): renderPM = None
except ImportError:
    renderPM = None

class BarcodeWidgetTestCase(unittest.TestCase):
    "Test barcode classes."
    _safe_formats = (['gif','pict'] if renderPM else []) + ['pdf']

    @classmethod
    def setUpClass(cls):
        cls.outDir = outDir = outputfile('barcode-out')
        cls.makeFn = lambda _, fn: os.path.join(outDir,fn)
        if not os.path.isdir(outDir):
            os.makedirs(outDir)
        for x in glob.glob(os.path.join(outDir,'*')):
            os.remove(x)

    def test0(self):
        from reportlab.graphics.shapes import Drawing
        outDir = self.outDir
        html = ['<html><head></head><body>']
        a = html.append
        formats = self._safe_formats
        from reportlab.graphics.barcode import getCodes
        CN = list(getCodes().items())
        for name,C in CN:
            i = C()
            x0,y0,x1,y1 = i.getBounds()
            D = Drawing(x1-x0,y1-y0)
            D.add(i)
            D.save(formats=formats,outDir=outDir,fnRoot=name)
            if renderPM:
                a('<h2>%s</h2><img src="%s.gif"><br>' % (name, name))
            for fmt in formats:
                efn = os.path.join(outDir,'%s.%s' % (name,fmt))
                self.assertTrue(os.path.isfile(efn),msg="Expected file %r was not created" % efn)
        a('</body></html>')
        open(os.path.join(outDir,'index.html'),'w').write('\n'.join(html))

    def test1(self):
        '''test createBarcodeDrawing'''
        from reportlab.graphics.barcode import createBarcodeDrawing
        from reportlab.graphics.barcode import getCodeNames
        for name in getCodeNames():
            d = createBarcodeDrawing(name)
            for t in getattr(d.__class__,'_tests',[]):
                createBarcodeDrawing(name,value=t)

    def test_qr_code_with_comma(self):
        from reportlab.graphics.barcode.qr import QrCodeWidget
        from reportlab.graphics.shapes import Drawing
        i = QrCodeWidget("VALUE WITH A COMMA,")
        x0, y0, x1, y1 = i.getBounds()
        D = Drawing(x1-x0, y1-y0)
        D.add(i)
        D.save(self._safe_formats, outDir=self.outDir, fnRoot="QR_with_comma")

    def test_qr_character_set_valid(self):
        from reportlab.graphics.barcode.qrencoder import QRNumber, QRAlphaNum
        for klass in (QRNumber,QRAlphaNum):
            for c in klass.chars:
                if not klass.valid(c):
                    raise ValueError('%s.valid(%r) does not match' % (klass.__name__,c))

    def createSample(self,name,memory):
        f = open(self.makeFn(name),'wb')
        f.write(memory)
        f.close()
    def test_graphics_barcode(self):
        run(self.makeFn('graphics-barcode-out.pdf'))
        fullTest(self.makeFn('graphics-barcode-full.pdf'))
        if renderPM:
            self.createSample('test_cbcim.png',createBarcodeImageInMemory('EAN13', value='123456789012'))
            self.createSample('test_cbcim.gif',createBarcodeImageInMemory('EAN8', value='1234567', format='gif'))
        self.createSample('test_cbcim.pdf',createBarcodeImageInMemory('UPCA', value='03600029145',format='pdf', barHeight=40))
        if renderPM:
            self.createSample('test_cbcim.tiff',createBarcodeImageInMemory('USPS_4State', value='01234567094987654321',routing='01234567891',format='tiff'))

def makeSuite():
    return makeSuiteForClasses(BarcodeWidgetTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
