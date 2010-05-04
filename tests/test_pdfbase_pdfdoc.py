from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation, NearTestCase
setOutDir(__name__)
import unittest,re,codecs
from reportlab.pdfbase import pdfdoc

class PdfdocTestCase(NearTestCase):
    """Tests of expected Unicode and encoding behaviour
    """
    def setUp(self):
        self.doc = pdfdoc.DummyDoc()

    def testPDFText(self):
        self.assertEquals(pdfdoc.PDFText('Hello World').format(self.doc),'<48656c6c6f20576f726c64>')

    def testPDFString(self):
        self.assertEquals(pdfdoc.PDFString('Hello World').format(self.doc),'(Hello World)')
        self.assertEquals(pdfdoc.PDFString('Hello\xc2\xa2World',0).format(self.doc),'(Hello\xa2World)')
        self.assertEquals(pdfdoc.PDFString('Hello\xc2\xa0World',0).format(self.doc),'(\xfe\xff\x00H\x00e\x00l\x00l\x00o\x00\xa0\x00W\x00o\x00r\x00l\x00d)')
        self.assertEquals(pdfdoc.PDFString('Hello\xc2\xa0World',1).format(self.doc),'(\\376\\377\\000H\\000e\\000l\\000l\\000o\\000\\240\\000W\\000o\\000r\\000l\\000d)')
        self.assertEquals(pdfdoc.PDFString(u'Hello\xa0World',1).format(self.doc),'(\\376\\377\\000H\\000e\\000l\\000l\\000o\\000\\240\\000W\\000o\\000r\\000l\\000d)')
        self.assertEquals(pdfdoc.PDFString(u'Hello\xa0World',0).format(self.doc),'(\xfe\xff\x00H\x00e\x00l\x00l\x00o\x00\xa0\x00W\x00o\x00r\x00l\x00d)')

def makeSuite():
    return makeSuiteForClasses(
        PdfdocTestCase,
        )

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
