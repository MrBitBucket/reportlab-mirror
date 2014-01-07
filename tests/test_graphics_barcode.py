#Copyright ReportLab Europe Ltd. 2000-2013
#see license.txt for license details
"""
Tests for barcodes
"""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import unittest, os, sys, glob

class BarcodeWidgetTestCase(unittest.TestCase):
    "Test barcode classes."

    @classmethod
    def setUpClass(cls):
        cls.outDir = outDir = outputfile('barcode-out')
        if not os.path.isdir(outDir):
            os.makedirs(outDir)
        for x in glob.glob(os.path.join(outDir,'*')):
            os.remove(x)

    def test0(self):
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.barcode import widgets
        outDir = self.outDir
        html = ['<html><head></head><body>']
        a = html.append
        formats = ['gif','pict','pdf']
        CN='''BarcodeI2of5
                BarcodeCode128
                BarcodeStandard93
                BarcodeExtended93
                BarcodeStandard39
                BarcodeExtended39
                BarcodeMSI
                BarcodeCodabar
                BarcodeCode11
                BarcodeFIM
                BarcodePOSTNET
                BarcodeUSPS_4State'''.split()
        for name in CN:
            C = getattr(widgets,name)
            i = C()
            D = Drawing(100,50)
            D.add(i)
            D.save(formats=formats,outDir=outDir,fnRoot=name)
            a('<h2>%s</h2><img src="%s.gif"><br>' % (name, name))
            for fmt in formats:
                efn = os.path.join(outDir,'%s.%s' % (name,fmt))
                self.assertTrue(os.path.isfile(efn),msg="Expected file %r was not created" % efn)
        a('</body></html>')
        open(os.path.join(outDir,'index.html'),'w').write('\n'.join(html))

def makeSuite():
    return makeSuiteForClasses(BarcodeWidgetTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
