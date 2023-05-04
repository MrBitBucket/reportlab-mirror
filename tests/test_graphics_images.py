#Copyright ReportLab Europe Ltd. 2000-2017
#see license.txt for license details
"""
Tests for RLG Image shapes.
"""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import os
import unittest
from reportlab.graphics.shapes import Image, Drawing, Rect
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import toColor

IMAGENAME = 'pythonpowered.gif'
GSIMAGE = 'pythonpowered-gs.gif'
GAIMAGE = 'gray-alpha.png'

class ImageTestCase(unittest.TestCase):
    "Test RLG Image shape."

    @classmethod
    def setUpClass(cls):
        cls.IMAGES = []
    
    @classmethod
    def tearDownClass(cls):
        if not cls.IMAGES: return
        d = Drawing(A4[0], A4[1])
        for img in cls.IMAGES:
            d.add(img)
        outPath = outputfile("test_graphics_images.pdf")
        renderPDF.drawToFile(d, outPath) #, '')
        assert os.path.exists(outPath)

        try:
            import rlPyCairo
        except ImportError:
            rlPyCairo = None

        try:
            import _rl_renderPM
        except ImportError:
            _rl_renderPM = None

        from reportlab.rl_config import renderPMBackend
        if rlPyCairo:
            d.save(formats=['png', 'gif', 'ps','svg'],outDir=os.path.dirname(outPath), fnRoot='test_graphics_images', _renderPM_backend='rlPyCairo')
        if _rl_renderPM:
            d.save(formats=['png', 'gif'],outDir=os.path.dirname(outPath), fnRoot='test_graphics_images-libart', _renderPM_backend='_renderPM')


    def test0(self):
        "Test convert a bitmap file as Image shape into a tmp. PDF file."

        d = Drawing(110, 44)
        inPath = IMAGENAME
        img = Image(0, 0, 110, 44, inPath)
        d.add(img)
        self.IMAGES.append(img)

    def test1(self):
        "Test Image shape, adding it to a PDF page."

        inPath = IMAGENAME
        img = Image(0, 0, 110, 44, inPath)
        self.IMAGES.append(img)


    def test2(self):
        "Test scaled Image shape adding it to a PDF page."

        inPath = IMAGENAME
        img = Image(0, 0, 110, 44, inPath)
        d = Drawing(110, 44)
        d.add(img)
        d.translate(120, 0)
        d.scale(2, 2)
        self.IMAGES.append(d)

    def test3(self):
        "Test rotated Image shape adding it to a PDF page."

        inPath = IMAGENAME
        img = Image(0, 0, 110, 44, inPath)
        d = Drawing(110, 44)
        d.add(img)
        d.translate(420, 0)
        d.scale(2, 2)
        d.rotate(45)
        self.IMAGES.append(d)

    def test4(self):
        "Test convert a greyscale bitmap file as Image shape into a tmp. PDF file."

        d = Drawing(110, 44)
        img = Image(0, 0, 110, 44, GSIMAGE)
        d.add(img)
        d.translate(0,2*72)
        self.IMAGES.append(d)

    def test5(self):
        "Test convert a greyscale +alpha bitmap file as Image shape into a tmp. PDF file."

        d = Drawing(48, 48)
        img = Image(0, 0, 48, 48, GAIMAGE)
        d.add(img)
        d.translate(72,4*72)
        self.IMAGES.append(d)

    def test6(self):
        d = Drawing(200, 100)
        d.add(Rect(1,1,d.width-2,d.height-2,strokeWidth=2,strokeColor=toColor('red'),fillColor=toColor('lightblue')),name='bg0')
        def addImage(x,y,w,h):
            img = Image(x, y, w, h, IMAGENAME)
            d.add(Rect(img.x-1,img.y-1,img.width+2,img.height+2,strokeWidth=2,strokeColor=toColor('green'),fillColor=toColor('black')),name='bg1')
            d.add(img)
        addImage(40,60,55,22)
        addImage(10,10,110,44)
        d.translate(72,6*72)
        self.IMAGES.append(d)

def makeSuite():
    return makeSuiteForClasses(ImageTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
