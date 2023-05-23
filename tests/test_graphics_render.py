#Copyright ReportLab Europe Ltd. 2000-2017
#see license.txt for license details
"""
Tests for renderers
"""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation, haveRenderPM, rlSkipIf
setOutDir(__name__)
import unittest, os, sys, glob
try:
    from reportlab.graphics import renderPM
    if not haveRenderPM(): renderPM = None
except:
    renderPM = None
from reportlab.graphics.shapes import _DrawingEditorMixin, Drawing, Group, Rect, Path, String, Polygon, Hatching, Line, definePath
from reportlab.lib.colors import Color, CMYKColor, PCMYKColor, toColor

class FillModeDrawing(_DrawingEditorMixin,Drawing):
    def __init__(self,width=600.0,height=200.0,fillMode='even-odd',*args,**kw):
        Drawing.__init__(self,width,height,*args,**kw)
        self.transform = (1,0,0,1,0,0)
        v0=self._nn(Group())
        v0.transform = (1,0,0,-1,0,200)
        v0.add(Rect(1,1,599,199,rx=0,ry=0,strokeDashArray=None,strokeWidth=2,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillOpacity=1,strokeColor=Color(0,0,1,1),strokeLineCap=0,fillColor=None))
        v1=v0._nn(Group())
        v1.transform = (.5,0,0,.5,0,0)
        v1.add(Path(points=[250,75,323,301,131,161,369,161,177,301],operators=[0,1,1,1,1,3],isClipPath=0,autoclose='svg',fillMode=fillMode,strokeDashArray=None,strokeWidth=3,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillOpacity=1,strokeColor=Color(0,0,0,1),strokeLineCap=0,fillColor=Color(1,0,0,1)))
        v2=v1._nn(Group())
        v2.transform = (.309017,.951057,-0.951057,.309017,306.21,249)
        v2.add(Path(points=[16,0,-8,9,-8,-9],operators=[0,1,1,3],isClipPath=0,autoclose='svg',fillMode=1,strokeDashArray=None,strokeWidth=1,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillColor=Color(0,0,0,1),strokeColor=None,strokeLineCap=0,fillOpacity=1))
        v2=v1._nn(Group())
        v2.transform = (-0.809017,-0.587785,.587785,-0.809017,175.16,193.2)
        v2.add(Path(points=[16,0,-8,9,-8,-9],operators=[0,1,1,3],isClipPath=0,autoclose='svg',fillMode=1,strokeDashArray=None,strokeWidth=1,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillColor=Color(0,0,0,1),strokeColor=None,strokeLineCap=0,fillOpacity=1))
        v2=v1._nn(Group())
        v2.transform = (1,0,0,1,314.26,161)
        v2.add(Path(points=[16,0,-8,9,-8,-9],operators=[0,1,1,3],isClipPath=0,autoclose='svg',fillMode=1,strokeDashArray=None,strokeWidth=1,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillColor=Color(0,0,0,1),strokeColor=None,strokeLineCap=0,fillOpacity=1))
        v2=v1._nn(Group())
        v2.transform = (-0.809017,.587785,-0.587785,-0.809017,221.16,268.8)
        v2.add(Path(points=[16,0,-8,9,-8,-9],operators=[0,1,1,3],isClipPath=0,autoclose='svg',fillMode=1,strokeDashArray=None,strokeWidth=1,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillColor=Color(0,0,0,1),strokeColor=None,strokeLineCap=0,fillOpacity=1))
        v2=v1._nn(Group())
        v2.transform = (.309017,-0.951057,.951057,.309017,233.21,126.98)
        v2.add(Path(points=[16,0,-8,9,-8,-9],operators=[0,1,1,3],isClipPath=0,autoclose='svg',fillMode=1,strokeDashArray=None,strokeWidth=1,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillColor=Color(0,0,0,1),strokeColor=None,strokeLineCap=0,fillOpacity=1))
        v1.add(Path(points=[600,81,659.0945,81,707,128.9055,707,188,707,247.0945,659.0945,295,600,295,540.9055,295,493,247.0945,493,188,493,128.9055,540.9055,81,600,81,600,139,627.062,139,649,160.938,649,188,649,215.062,627.062,237,600,237,572.938,237,551,215.062,551,188,551,160.938,572.938,139,600,139],operators=[0,2,2,2,2,3,0,2,2,2,2,3],isClipPath=0,autoclose='svg',fillMode=fillMode,strokeDashArray=None,strokeWidth=3,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillOpacity=1,strokeColor=Color(0,0,0,1),strokeLineCap=0,fillColor=Color(1,0,0,1)))
        v2=v1._nn(Group())
        v2.transform = (0,1,-1,0,707,188)
        v2.add(Path(points=[16,0,-8,9,-8,-9],operators=[0,1,1,3],isClipPath=0,autoclose='svg',fillMode=1,strokeDashArray=None,strokeWidth=1,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillColor=Color(0,0,0,1),strokeColor=None,strokeLineCap=0,fillOpacity=1))
        v2=v1._nn(Group())
        v2.transform = (-0.866025,-0.5,.5,-0.866025,546.5,280.6647)
        v2.add(Path(points=[16,0,-8,9,-8,-9],operators=[0,1,1,3],isClipPath=0,autoclose='svg',fillMode=1,strokeDashArray=None,strokeWidth=1,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillColor=Color(0,0,0,1),strokeColor=None,strokeLineCap=0,fillOpacity=1))
        v2=v1._nn(Group())
        v2.transform = (.866025,-0.5,.5,.866025,546.5,95.33528)
        v2.add(Path(points=[16,0,-8,9,-8,-9],operators=[0,1,1,3],isClipPath=0,autoclose='svg',fillMode=1,strokeDashArray=None,strokeWidth=1,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillColor=Color(0,0,0,1),strokeColor=None,strokeLineCap=0,fillOpacity=1))
        v2=v1._nn(Group())
        v2.transform = (-0.866025,.5,-0.5,-0.866025,624.5,230.4352)
        v2.add(Path(points=[16,0,-8,9,-8,-9],operators=[0,1,1,3],isClipPath=0,autoclose='svg',fillMode=1,strokeDashArray=None,strokeWidth=1,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillColor=Color(0,0,0,1),strokeColor=None,strokeLineCap=0,fillOpacity=1))
        v2=v1._nn(Group())
        v2.transform = (0,-1,1,0,551,188)
        v2.add(Path(points=[16,0,-8,9,-8,-9],operators=[0,1,1,3],isClipPath=0,autoclose='svg',fillMode=1,strokeDashArray=None,strokeWidth=1,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillColor=Color(0,0,0,1),strokeColor=None,strokeLineCap=0,fillOpacity=1))
        v2=v1._nn(Group())
        v2.transform = (.866025,.5,-0.5,.866025,624.5,145.5648)
        v2.add(Path(points=[16,0,-8,9,-8,-9],operators=[0,1,1,3],isClipPath=0,autoclose='svg',fillMode=1,strokeDashArray=None,strokeWidth=1,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillColor=Color(0,0,0,1),strokeColor=None,strokeLineCap=0,fillOpacity=1))
        v1.add(Path(points=[950,81,1009.094,81,1057,128.9055,1057,188,1057,247.0945,1009.094,295,950,295,890.9055,295,843,247.0945,843,188,843,128.9055,890.9055,81,950,81,950,139,922.938,139,901,160.938,901,188,901,215.062,922.938,237,950,237,977.062,237,999,215.062,999,188,999,160.938,977.062,139,950,139],operators=[0,2,2,2,2,3,0,2,2,2,2,3],isClipPath=0,autoclose='svg',fillMode=fillMode,strokeDashArray=None,strokeWidth=3,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillOpacity=1,strokeColor=Color(0,0,0,1),strokeLineCap=0,fillColor=Color(1,0,0,1)))
        v2=v1._nn(Group())
        v2.transform = (0,1,-1,0,1057,188)
        v2.add(Path(points=[16,0,-8,9,-8,-9],operators=[0,1,1,3],isClipPath=0,autoclose='svg',fillMode=1,strokeDashArray=None,strokeWidth=1,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillColor=Color(0,0,0,1),strokeColor=None,strokeLineCap=0,fillOpacity=1))
        v2=v1._nn(Group())
        v2.transform = (-0.866025,-0.5,.5,-0.866025,896.5,280.6647)
        v2.add(Path(points=[16,0,-8,9,-8,-9],operators=[0,1,1,3],isClipPath=0,autoclose='svg',fillMode=1,strokeDashArray=None,strokeWidth=1,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillColor=Color(0,0,0,1),strokeColor=None,strokeLineCap=0,fillOpacity=1))
        v2=v1._nn(Group())
        v2.transform = (.866025,-0.5,.5,.866025,896.5,95.33528)
        v2.add(Path(points=[16,0,-8,9,-8,-9],operators=[0,1,1,3],isClipPath=0,autoclose='svg',fillMode=1,strokeDashArray=None,strokeWidth=1,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillColor=Color(0,0,0,1),strokeColor=None,strokeLineCap=0,fillOpacity=1))
        v2=v1._nn(Group())
        v2.transform = (.866025,-0.5,.5,.866025,974.5,230.4352)
        v2.add(Path(points=[16,0,-8,9,-8,-9],operators=[0,1,1,3],isClipPath=0,autoclose='svg',fillMode=1,strokeDashArray=None,strokeWidth=1,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillColor=Color(0,0,0,1),strokeColor=None,strokeLineCap=0,fillOpacity=1))
        v2=v1._nn(Group())
        v2.transform = (0,1,-1,0,901,188)
        v2.add(Path(points=[16,0,-8,9,-8,-9],operators=[0,1,1,3],isClipPath=0,autoclose='svg',fillMode=1,strokeDashArray=None,strokeWidth=1,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillColor=Color(0,0,0,1),strokeColor=None,strokeLineCap=0,fillOpacity=1))
        v2=v1._nn(Group())
        v2.transform = (-0.866025,-0.5,.5,-0.866025,974.5,145.5648)
        v2.add(Path(points=[16,0,-8,9,-8,-9],operators=[0,1,1,3],isClipPath=0,autoclose='svg',fillMode=1,strokeDashArray=None,strokeWidth=1,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillColor=Color(0,0,0,1),strokeColor=None,strokeLineCap=0,fillOpacity=1))

class _410Drawing(_DrawingEditorMixin,Drawing):
    def __init__(self,width=100.0,height=100.0,*args,**kw):
        Drawing.__init__(self,width,height,*args,**kw)
        self.transform = (1,0,0,1,0,0)
        v0=self._nn(Group())
        v0.transform = (1,0,0,-1,0,100)
        v0.add(Path(points=[30,1,70,1,99,30,99,70,70,99,30,99,1,70,1,30],operators=[0,1,1,1,1,1,1,1,3],isClipPath=0,autoclose='svg',fillMode=1,strokeDashArray=None,strokeWidth=1,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillOpacity=1,strokeColor=Color(0,0,0,1),strokeLineCap=0,fillColor=Color(0,0,0,1)))
        v0.add(Path(points=[31,3,69,3,97,31,97,69,69,97,31,97,3,69,3,31],operators=[0,1,1,1,1,1,1,1,3],isClipPath=0,autoclose='svg',fillMode=1,strokeDashArray=None,strokeWidth=1,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillOpacity=1,strokeColor=None,strokeLineCap=0,fillColor=Color(.666667,.133333,.2,1)))
        v1=v0._nn(Group())
        v1.transform = (1,0,0,-1,0,136)
        v1.add(String(50,68,u'410',textAnchor=u'middle',fontName='Helvetica',fontSize=48,fillColor=Color(1,1,1,1)))

class SVGLibIssue104(_DrawingEditorMixin,Drawing):
    def __init__(self,width=224,height=124,*args,**kw):
        Drawing.__init__(self,width,height,*args,**kw)
        points = [122.0, 87.0, 122.0, 88.0, 123.0, 88.0, 123.0, 89.0, 124.0, 89.0, 124.0, 90.0, 126.0, 90.0, 126.0, 89.0, 128.0, 88.0, 128.0, 89.0, 129.0, 89.0, 129.0, 91.0, 128.0, 91.0, 128.0, 92.0, 130.0, 99.0, 130.0, 100.0, 129.0, 100.0, 126.0, 103.0, 125.0, 103.0, 125.0, 104.0, 126.0, 106.0, 130.0, 87.0, 129.0, 87.0, 129.0, 86.0, 126.0, 86.0, 126.0, 87.0]
        grp = Group(Polygon(points, fillColor=toColor('red')))
        grp.scale(1, -1)
        grp.translate(0, -124)
        self.add(grp)

class AutoCloseDrawing(_DrawingEditorMixin,Drawing):
    def __init__(self,width=100.0,height=100.0,autoclose='',*args,**kw):
        Drawing.__init__(self,width,height,*args,**kw)
        self.transform = (1,0,0,1,0,0)
        v0=self._nn(Group())
        v0.transform = (1,0,0,-1,0,100)
        v1=v0._nn(Group())
        v1.transform = (1,0,0,-1,0,100)
        v1.add(Path(points=[10,10,10,90,20,90,20,10,30,10,30,90,40,90,40,10,50,10,50,90,60,90,60,10,70,10,70,90,80,90,80,10],operators=[0,1,1,1,3,0,1,1,1,0,1,1,1,3,0,1,1,1],isClipPath=0,autoclose=autoclose,fillMode=1,strokeDashArray=None,strokeWidth=2,strokeMiterLimit=0,strokeOpacity=None,strokeLineJoin=0,fillOpacity=1,strokeColor=Color(1,0,0,1),strokeLineCap=0,fillColor=Color(0,0,1,1)))

class HatchDrawing(_DrawingEditorMixin,Drawing):
    def __init__(self,width=400,height=200,*args,**kw):
        Drawing.__init__(self,width,height,*args,**kw)
        #for x1,y1, x2,y2 in diagonalLines(45, 5, [Polygon([5,5,  5,100, 99,105, 105,5])]): self._add(self,Line(x1,y1,x2,y2,strokeWidth=1,strokeColor=toColor('black')),name=None,validate=None,desc=None)
        self._add(self,Hatching(spacing=(30,30,30),angles=(45,0,-45),xyLists=[5,5,  5,100, 99,105, 105,5],strokeWidth=0.1,strokeColor=toColor('red'), strokeDashArray=None),name='hatching',validate=None,desc=None)
        self.width        = 110
        self.height       = 110
        self._add(self,Line(0,105,110,105,strokeWidth=0.5,strokeColor=toColor('blue')),name=None,validate=None,desc=None)

class TextRenderModeDrawing(_DrawingEditorMixin,Drawing):
    def __init__(self,width=400,height=200,*args,**kw):
        Drawing.__init__(self,width,height,*args,**kw)
        smallFontSize = float(os.environ.get('smallFontSize','40'))
        self._add(self,String(65,10,'text0',fontSize=80,fontName='Helvetica',fillColor=toColor('blue'),strokeColor=toColor('red'),strokeWidth=1.5,textRenderMode=0),name='S0',validate=None,desc=None)
        self._add(self,String(405,20,'text1',fontSize=80,fontName='Helvetica',fillColor=toColor('blue'),strokeColor=toColor('red'),strokeWidth=1.5,textRenderMode=1, textAnchor='end'),name='S1',validate=None,desc=None)
        self._add(self,String(190,90,'text2',fontSize=80,fontName='Helvetica',fillColor=toColor('blue'),strokeColor=toColor('red'),strokeWidth=1.5,textRenderMode=2),name='S2',validate=None,desc=None)
        self._add(self,String(240,150,'text3',fontSize=smallFontSize,fontName='Helvetica',fillColor=toColor('green'),strokeColor=toColor('magenta'),strokeWidth=0.5,textRenderMode=2),name='S3',validate=None,desc=None)
        self._add(self,String(140,150,'text4',fontSize=smallFontSize,fontName='Helvetica',fillColor=toColor('green'),strokeColor=toColor('magenta'),strokeWidth=0.5,textRenderMode=1),name='S4',validate=None,desc=None)
        self._add(self,String(70,120,'text5',fontSize=smallFontSize,fontName='Helvetica',fillColor=toColor('green'),strokeColor=toColor('magenta'),strokeWidth=0.5,textRenderMode=0),name='S5',validate=None,desc=None)
        self._add(self,Line(40,40,70,70,strokeWidth=0.5,strokeColor=toColor('green')),name='L0',validate=None,desc=None)
        self._add(self,definePath([('moveTo',80,80),('lineTo',110,110),('lineTo',80,110),'closePath'],fillColor=None,strokeWidth=2,strokeColor=toColor('yellow')),name='P0',validate=None,desc=None)

class RenderTestCase(unittest.TestCase):
    "Test renderPS classes."

    @classmethod
    def setUpClass(cls):
        cls.outDir = outDir = outputfile('render-out')
        if not os.path.isdir(outDir):
            os.makedirs(outDir)
        for x in glob.glob(os.path.join(outDir,'*')):
            os.remove(x)

    def test0(self):
        from reportlab.graphics.renderPS import test
        assert test(self.outDir) is None

    def test1(self):
        from reportlab.graphics.renderPDF import test
        assert test(self.outDir) is None

    @rlSkipIf(not renderPM,'no renderPM')
    def test2(self):
        from reportlab.graphics.renderPM import test
        assert test(self.outDir) is None

    def test3(self):
        from reportlab.graphics.renderSVG import test
        assert test(self.outDir) is None

    def test4(self):
        formats = ('pdf svg ps py' + (' png' if renderPM else '')).split()
        for fm in (0,1):
            FillModeDrawing(fillMode=fm).save(formats=formats,outDir=self.outDir,fnRoot='fillmode-'+('non-zero' if fm else 'even-odd'))
        _410Drawing().save(formats=formats,outDir=self.outDir,fnRoot='410')
        for ac in (None,'pdf','svg'):
            AutoCloseDrawing(autoclose=ac).save(formats=formats,outDir=self.outDir,fnRoot='autoclose-'+(ac or 'none'))
        HatchDrawing().save(formats=formats,outDir=self.outDir,fnRoot='hatch')
        TextRenderModeDrawing().save(formats=formats,outDir=self.outDir,fnRoot='textmode')

    @rlSkipIf(not renderPM,'no renderPM')
    def testSVGLibIssues(self):
        SVGLibIssue104().save(formats=['pdf','png'],outDir=self.outDir, fnRoot='svglib-issue104')
        from PIL import Image
        im = Image.open(os.path.join(self.outDir,'svglib-issue104.png'))
        lastColWhite = [y for y in range(124) if im.getpixel((223,y))==(255,255,255)]
        self.assertEqual(len(lastColWhite),124)

def makeSuite():
    return makeSuiteForClasses(RenderTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
