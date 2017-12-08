#Copyright ReportLab Europe Ltd. 2000-2017
#see license.txt for license details
"""
Tests for barcodes
"""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import unittest, os, sys, glob

try:
    from reportlab.graphics import _renderPM
except ImportError:
    _renderPM = None

class BarcodeWidgetTestCase(unittest.TestCase):
    "Test barcode classes."

    @classmethod
    def setUpClass(cls):
        cls.outDir = outDir = outputfile('barcode-out')
        if not os.path.isdir(outDir):
            os.makedirs(outDir)
        for x in glob.glob(os.path.join(outDir,'*')):
            os.remove(x)

    @unittest.skipIf(not _renderPM,'no _renderPM')
    def test0(self):
        from reportlab.graphics.shapes import Drawing
        outDir = self.outDir
        html = ['<html><head></head><body>']
        a = html.append
        formats = ['gif','pict','pdf']
        from reportlab.graphics.barcode import getCodes
        CN = list(getCodes().items())
        for name,C in CN:
            i = C()
            x0,y0,x1,y1 = i.getBounds()
            D = Drawing(x1-x0,y1-y0)
            D.add(i)
            D.save(formats=formats,outDir=outDir,fnRoot=name)
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
        D.save(['gif','pict','pdf'], outDir=self.outDir, fnRoot="QR_with_comma")

    def test_qr_character_set_valid(self):
        from reportlab.graphics.barcode.qrencoder import QRNumber, QRAlphaNum
        for klass in (QRNumber,QRAlphaNum):
            for c in klass.chars:
                if not klass.valid(c):
                    raise ValueError('%s.valid(%r) does not match' % (klass.__name__,c))

def makeSuite():
    return makeSuiteForClasses(BarcodeWidgetTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
