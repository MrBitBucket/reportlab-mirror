#Copyright ReportLab Europe Ltd. 2000-2017
#see license.txt for license details
"""
Tests for chart class.
"""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)

import os, sys, copy
from os.path import join, basename, splitext
import unittest
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.validators import Auto
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics.shapes import *
from reportlab.graphics.charts.textlabels import Label, _text2Path
from reportlab.platypus.flowables import Spacer, PageBreak
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.xpreformatted import XPreformatted
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.lineplots import LinePlot, GridLinePlot
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.spider import SpiderChart
from reportlab.graphics.widgets.markers import makeMarker

try:
    from reportlab.graphics import _renderPM
except ImportError:
    _renderPM = None

def myMainPageFrame(canvas, doc):
    "The page frame used for all PDF documents."

    canvas.saveState()

    #canvas.rect(2.5*cm, 2.5*cm, 15*cm, 25*cm)
    canvas.setFont('Times-Roman', 12)
    pageNumber = canvas.getPageNumber()
    canvas.drawString(10*cm, cm, str(pageNumber))

    canvas.restoreState()


class MyDocTemplate(BaseDocTemplate):
    "The document template used for all PDF documents."

    _invalidInitArgs = ('pageTemplates',)

    def __init__(self, filename, **kw):
        frame1 = Frame(2.5*cm, 2.5*cm, 15*cm, 25*cm, id='F1')
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kw)
        template = PageTemplate('normal', [frame1], myMainPageFrame)
        self.addPageTemplates(template)


def sample1bar(data=[(13, 5, 20, 22, 37, 45, 19, 4)]):
    drawing = Drawing(400, 200)

    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 125
    bc.width = 300
    bc.data = data

    bc.strokeColor = colors.black

    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 60
    bc.valueAxis.valueStep = 15

    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30

    catNames = 'Jan Feb Mar Apr May Jun Jul Aug'.split( ' ')
    catNames = [n+'-99' for n in catNames]
    bc.categoryAxis.categoryNames = catNames
    drawing.add(bc)

    return drawing


def sample2bar(data=[(13, 5, 20, 22, 37, 45, 19, 4),
                  (14, 6, 21, 23, 38, 46, 20, 5)]):
    return sample1bar(data)


def sample1line(data=[(13, 5, 20, 22, 37, 45, 19, 4)]):
    drawing = Drawing(400, 200)

    bc = HorizontalLineChart()
    bc.x = 50
    bc.y = 50
    bc.height = 125
    bc.width = 300
    bc.data = data

    bc.strokeColor = colors.black

    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 60
    bc.valueAxis.valueStep = 15

    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30

    catNames = 'Jan Feb Mar Apr May Jun Jul Aug'.split(' ')
    catNames = [n+'-99' for n in catNames]
    bc.categoryAxis.categoryNames = catNames
    drawing.add(bc)

    return drawing


def sample2line(data=[(13, 5, 20, 22, 37, 45, 19, 4),
                  (14, 6, 21, 23, 38, 46, 20, 5)]):
    return sample1line(data)


def sample3(drawing=None):
    "Add sample swatches to a diagram."

    d = drawing or Drawing(400, 200)

    swatches = Legend()
    swatches.alignment = 'right'
    swatches.x = 80
    swatches.y = 160
    swatches.deltax = 60
    swatches.dxTextSpace = 10
    swatches.columnMaximum = 4
    items = [(colors.red, 'before'), (colors.green, 'after')]
    swatches.colorNamePairs = items

    d.add(swatches, 'legend')

    return d


def sample4pie():
    width = 300
    height = 150
    d = Drawing(width, height)
    pc = Pie()
    pc.x = 150
    pc.y = 50
    pc.data = [1, 50, 100, 100, 100, 100, 100, 100, 100, 50]
    pc.labels = ['0','a','b','c','d','e','f','g','h','i']
    pc.slices.strokeWidth=0.5
    pc.slices[3].popout = 20
    pc.slices[3].strokeWidth = 2
    pc.slices[3].strokeDashArray = [2,2]
    pc.slices[3].labelRadius = 1.75
    pc.slices[3].fontColor = colors.red
    d.add(pc)
    legend = Legend()
    legend.x = width-5
    legend.y = height-5
    legend.dx = 20
    legend.dy = 5
    legend.deltax = 0
    legend.boxAnchor = 'nw'
    legend.colorNamePairs=Auto(chart=pc)
    d.add(legend)
    return d

def autoLegender(i,chart,styleObj,sym='symbol'):
    if sym:
        setattr(styleObj[0],sym, makeMarker('Diamond',size=6))
        setattr(styleObj[1],sym,makeMarker('Square'))
    width = 300
    height = 150
    legend = Legend()
    legend.x = width-5
    legend.y = 5
    legend.dx = 20
    legend.dy = 5
    legend.deltay = 0
    legend.boxAnchor = 'se'
    if i=='col auto':
        legend.colorNamePairs[0]=(Auto(chart=chart),'auto chart=self.chart')
        legend.colorNamePairs[1]=(Auto(obj=chart,index=1),'auto  chart=self.chart index=1')
    elif i=='full auto':
        legend.colorNamePairs=Auto(chart=chart)
    elif i=='swatch set':
        legend.swatchMarker=makeMarker('Circle')
        legend.swatchMarker.size = 10
    elif i=='swatch auto':
        legend.swatchMarker=Auto(chart=chart)
    d = Drawing(width,height)
    d.background = Rect(0,0,width,height,strokeWidth=1,strokeColor=colors.red,fillColor=None)
    m = makeMarker('Cross')
    m.x = width-5
    m.y = 5
    m.fillColor = colors.red
    m.strokeColor = colors.yellow
    d.add(chart)
    d.add(legend)
    d.add(m)
    return d

def lpleg(i=None):
    chart = LinePlot()
    return autoLegender(i,chart,chart.lines)

def hlcleg(i=None):
    chart = HorizontalLineChart()
    return autoLegender(i,chart,chart.lines)

def bcleg(i=None):
    chart = VerticalBarChart()
    return autoLegender(i,chart,chart.bars,None)

def pcleg(i=None):
    chart = Pie()
    return autoLegender(i,chart,chart.slices,None)

def scleg(i=None):
    chart = SpiderChart()
    return autoLegender(i,chart,chart.strands,None)

def plpleg(i=None):
    from reportlab.lib.colors import pink, red, green
    pie = Pie()
    pie.x = 0
    pie.y = 0
    pie.pointerLabelMode='LeftAndRight'
    pie.slices.label_boxStrokeColor      = red
    pie.simpleLabels = 0
    pie.sameRadii = 1
    pie.data = [1, 0.1, 1.7, 4.2,0,0]
    pie.labels = ['abcdef', 'b', 'c', 'd','e','fedcba']
    pie.strokeWidth=1
    pie.strokeColor=green
    pie.slices.label_pointer_piePad      = 6
    pie.width = 160
    pie.direction = 'clockwise'
    pie.pointerLabelMode  = 'LeftRight'
    return autoLegender(i,pie,pie.slices,None)

def notFail(d):
    try:
        return d.getContents()
    except:
        import traceback
        traceback.print_exc()
        return None

STORY = []
styleSheet = getSampleStyleSheet()
bt = styleSheet['BodyText']
h1 = styleSheet['Heading1']
h2 = styleSheet['Heading2']
h3 = styleSheet['Heading3']
FINISHED = 0

def run_samples(S,kind='axes'):
    outDir = outputfile('charts-out')
    for f in S:
        if f.startswith('sample'):
            d = S[f]()
            d.save(formats=['pdf', 'gif', 'svg'],outDir=outDir, fnRoot='test_graphics_charts_%s_%s' % (kind,f))

class ChartTestCase(unittest.TestCase):
    "Test chart classes."

    def setUp(self):
        "Hook method for setting up the test fixture before exercising it."

        global STORY
        self.story = STORY

        if self.story == []:
            self.story.append(Paragraph('Tests for chart classes', h1))

    def tearDown(self):
        "Hook method for deconstructing the test fixture after testing it."

        if FINISHED:
            path=outputfile('test_graphics_charts.pdf')
            doc = MyDocTemplate(path)
            doc.build(self.story)

    def test0(self):
        "Test bar charts."

        story = self.story
        story.append(Paragraph('Single data row', h2))

        story.append(Spacer(0, 0.5*cm))
        drawing = sample1bar()
        story.append(drawing)
        story.append(Spacer(0, 1*cm))


    def test1(self):
        "Test bar charts."

        story = self.story
        story.append(Paragraph('Double data row', h2))

        story.append(Spacer(0, 0.5*cm))
        drawing = sample2bar()
        story.append(drawing)
        story.append(Spacer(0, 1*cm))


    def test2(self):
        "Test bar charts."

        story = self.story
        story.append(Paragraph('Double data row with legend', h2))

        story.append(Spacer(0, 0.5*cm))
        drawing = sample2bar()
        drawing = sample3(drawing)
        story.append(drawing)
        story.append(Spacer(0, 1*cm))


    def test3(self):
        "Test line charts."

        story = self.story
        story.append(Paragraph('Single data row', h2))

        story.append(Spacer(0, 0.5*cm))
        drawing = sample1line()
        story.append(drawing)
        story.append(Spacer(0, 1*cm))


    def test4(self):
        "Test line charts."

        story = self.story
        story.append(Paragraph('Single data row', h2))

        story.append(Spacer(0, 0.5*cm))
        drawing = sample2line()
        story.append(drawing)
        story.append(Spacer(0, 1*cm))

    def test4b(self):
        story = self.story
        for code in (lpleg, hlcleg, bcleg, pcleg, scleg, plpleg):
            code_name = code.__code__.co_name
            for i in ('standard', 'col auto', 'full auto', 'swatch set', 'swatch auto'):
                d = code(i)
                assert notFail(d),'getContents failed for %s %s' % (code_name,i)
                story.append(Paragraph('%s %s' % (i,code_name), h2))
                story.append(Spacer(0, 0.5*cm))
                story.append(code(i))
                story.append(Spacer(0, 1*cm))

    def test4c(self):
        story = self.story
        d=Drawing(215,115)
        d.add(GridLinePlot(),name='chart')
        d.chart.y = 20
        story.append(Paragraph('GridLinePlot', h2))
        story.append(Spacer(0, 0.5*cm))
        story.append(d)
        story.append(Spacer(0, 1*cm))

    def test5(self):
        "Test pie charts."

        story = self.story
        story.append(Paragraph('Pie', h2))

        story.append(Spacer(0, 0.5*cm))
        drawing = sample4pie()
        story.append(drawing)
        story.append(Spacer(0, 1*cm))


    def test7(self):
        "Added some new side labelled pies"

        story = self.story
        story.append(Paragraph('Side Labelled Pie', h2))
        story.append(Spacer(0,1*cm))
        story.append(Paragraph('Here are two examples of side labelled pies.',bt))

        story.append(Spacer(0, 0.5*cm))
        from reportlab.graphics.charts.piecharts import sample5, sample6, sample7, sample8, sample9
        drawing5 = sample5()
        story.append(drawing5)

        story.append(Spacer(0, 0.5*cm))
        drawing9 = sample9()
        story.append(drawing9)
        story.append(Spacer(0, 1*cm))

        story.append(Paragraph('Moving the pie', h3))
        story.append(Paragraph('Here is a pie that has pie.x = 0 and is moved sideways in order to make space for the labels.', bt))
        story.append(Paragraph('The line represents x = 0',bt))
        story.append(Paragraph('This has not been implemented and is on line 863 in piecharts.py', bt))

        story.append(Spacer(0,0.5*cm))
        drawing6 = sample6()
        story.append(drawing6)
        story.append(Spacer(0,1*cm))

        story.append(Paragraph('Case with overlapping pointers', h3))
        story.append(Paragraph('If there are many slices then the pointer labels can end up overlapping as shown below.', bt))

        story.append(Spacer(0,0.5*cm))
        drawing7 = sample7()
        story.append(drawing7)
        story.append(Spacer(0,1*cm))

        story.append(Paragraph('Case with overlapping labels', h3))
        story.append(Paragraph('Labels overlap if they do not belong to adjacent pie slices.', bt))

        story.append(Spacer(0,0.5*cm))
        drawing8 = sample8()
        story.append(drawing8)
        story.append(Spacer(0,1*cm))

    @unittest.skipIf(not _renderPM,'no _renderPM')
    def test8(self):
        '''text _text2Path'''
        story = self.story
        story.append(Paragraph('Texts drawn using a Path', h3))
        story.append(Spacer(0,0.5*cm))
        P=_text2Path('Hello World from font Times-Roman!',x=10,y=20,fontName='Times-Roman',fontSize=20,strokeColor=colors.blue,strokeWidth=0.1,fillColor=colors.red)
        d = Drawing(400,50)
        d.add(P)
        story.append(d)
        P=_text2Path('Hello World from font Helvetica!',x=10,y=20,fontName='Helvetica',fontSize=20,strokeColor=colors.blue,strokeWidth=0.1,fillColor=colors.red)
        d = Drawing(400,50)
        d.add(P)
        story.append(d)
        story.append(Spacer(0,1*cm))


    def test999(self):
        #keep this last
        from reportlab.graphics.charts.piecharts import Pie, _makeSideArcDefs, intervalIntersection
        L = []

        def intSum(arcs,A):
            s = 0
            for a in A:
                for arc in arcs:
                    i = intervalIntersection(arc[1:],a)
                    if i: s += i[1] - i[0]
            return s

        def subtest(sa,d):
            pc = Pie()
            pc.direction=d
            pc.startAngle=sa
            arcs = _makeSideArcDefs(sa,d)
            A = [x[1] for x in pc.makeAngles()]
            arcsum = sum([a[2]-a[1] for a in arcs])
            isum = intSum(arcs,A)
            mi = max([a[2]-a[1] for a in arcs])
            ni = min([a[2]-a[1] for a in arcs])
            l = []
            s = (arcsum-360)
            if s>1e-8: l.append('Arc length=%s != 360' % s)
            s = abs(isum-360)
            if s>1e-8: l.append('interval intersection length=%s != 360' % s)
            if mi>360: l.append('max interval intersection length=%s >360' % mi)
            if ni<0: l.append('min interval intersection length=%s <0' % ni)
            if l:
                l.append('sa: %s d: %s' % (sa,d))
                l.append('sidearcs: %s' % str(arcs))
                l.append('Angles: %s' % A)
                raise ValueError('piecharts._makeSideArcDefs failure\n%s' % '\n'.join(l))

        for d in ('anticlockwise','clockwise'):
            for sa in (225, 180, 135, 90, 45, 0, -45, -90):
                subtest(sa,d)

        # This triggers the document build operation (hackish).
        global FINISHED
        FINISHED = 1

    def test801(self):
        '''test for bitbucket issue 105 reported by Johann Du Toit'''
        from reportlab.graphics.charts.doughnut import Doughnut
        from reportlab.graphics import renderSVG
        d = Drawing(500, 500)
        pie = Doughnut()
        pie.data = [5]
        pie.labels = ['Only 1 Value','']
        d.add(pie)
        s = renderSVG.drawToString(d)

    def test_axes(self):
        from reportlab.graphics.charts.axes import YValueAxis, XValueAxis, LogYValueAxis, LogXValueAxis, LogYValueAxis, XCategoryAxis, YCategoryAxis
        # Sample functions.
        def sample0a():
            "Sample drawing with one xcat axis and two buckets."

            drawing = Drawing(400, 200)

            data = [(10, 20)]

            xAxis = XCategoryAxis()
            xAxis.setPosition(75, 75, 300)
            xAxis.configure(data)
            xAxis.categoryNames = ['Ying', 'Yang']
            xAxis.labels.boxAnchor = 'n'
            drawing.add(xAxis)
            return drawing

        def sample0b():
            "Sample drawing with one xcat axis and one bucket only."

            drawing = Drawing(400, 200)

            data = [(10,)]

            xAxis = XCategoryAxis()
            xAxis.setPosition(75, 75, 300)
            xAxis.configure(data)
            xAxis.categoryNames = ['Ying']
            xAxis.labels.boxAnchor = 'n'
            drawing.add(xAxis)
            return drawing

        def sample1():
            "Sample drawing containing two unconnected axes."
            from reportlab.graphics.shapes import _baseGFontNameB
            drawing = Drawing(400, 200)
            data = [(10, 20, 30, 42)]
            xAxis = XCategoryAxis()
            xAxis.setPosition(75, 75, 300)
            xAxis.configure(data)
            xAxis.categoryNames = ['Beer','Wine','Meat','Cannelloni']
            xAxis.labels.boxAnchor = 'n'
            xAxis.labels[3].dy = -15
            xAxis.labels[3].angle = 30
            xAxis.labels[3].fontName = _baseGFontNameB
            yAxis = YValueAxis()
            yAxis.setPosition(50, 50, 125)
            yAxis.configure(data)
            drawing.add(xAxis)
            drawing.add(yAxis)
            return drawing

        def sample4a():
            "Sample drawing, xvalue/yvalue axes, y connected at 100 pts to x."
            drawing = Drawing(400, 200)
            data = [(10, 20, 30, 42)]
            yAxis = YValueAxis()
            yAxis.setPosition(50, 50, 125)
            yAxis.configure(data)
            xAxis = XValueAxis()
            xAxis._length = 300
            xAxis.joinAxis = yAxis
            xAxis.joinAxisMode = 'points'
            xAxis.joinAxisPos = 100
            xAxis.configure(data)
            drawing.add(xAxis)
            drawing.add(yAxis)
            return drawing

        def sample4b():
            "Sample drawing, xvalue/yvalue axes, y connected at value 35 of x."
            drawing = Drawing(400, 200)
            data = [(10, 20, 30, 42)]
            yAxis = YValueAxis()
            yAxis.setPosition(50, 50, 125)
            yAxis.configure(data)
            xAxis = XValueAxis()
            xAxis._length = 300
            xAxis.joinAxis = yAxis
            xAxis.joinAxisMode = 'value'
            xAxis.joinAxisPos = 35
            xAxis.configure(data)
            drawing.add(xAxis)
            drawing.add(yAxis)
            return drawing

        def sample4c():
            "Sample drawing, xvalue/yvalue axes, y connected to bottom of x."
            drawing = Drawing(400, 200)
            data = [(10, 20, 30, 42)]
            yAxis = YValueAxis()
            yAxis.setPosition(50, 50, 125)
            yAxis.configure(data)
            xAxis = XValueAxis()
            xAxis._length = 300
            xAxis.joinAxis = yAxis
            xAxis.joinAxisMode = 'bottom'
            xAxis.configure(data)
            drawing.add(xAxis)
            drawing.add(yAxis)
            return drawing

        def sample4c1():
            "xvalue/yvalue axes, without drawing axis lines/ticks."
            drawing = Drawing(400, 200)
            data = [(10, 20, 30, 42)]
            yAxis = YValueAxis()
            yAxis.setPosition(50, 50, 125)
            yAxis.configure(data)
            yAxis.visibleAxis = 0
            yAxis.visibleTicks = 0
            xAxis = XValueAxis()
            xAxis._length = 300
            xAxis.joinAxis = yAxis
            xAxis.joinAxisMode = 'bottom'
            xAxis.configure(data)
            xAxis.visibleAxis = 0
            xAxis.visibleTicks = 0
            drawing.add(xAxis)
            drawing.add(yAxis)
            return drawing

        def sample4d():
            "Sample drawing, xvalue/yvalue axes, y connected to top of x."
            drawing = Drawing(400, 200)
            data = [(10, 20, 30, 42)]
            yAxis = YValueAxis()
            yAxis.setPosition(50, 50, 125)
            yAxis.configure(data)
            xAxis = XValueAxis()
            xAxis._length = 300
            xAxis.joinAxis = yAxis
            xAxis.joinAxisMode = 'top'
            xAxis.configure(data)
            drawing.add(xAxis)
            drawing.add(yAxis)
            return drawing

        def sample5a():
            "Sample drawing, xvalue/yvalue axes, y connected at 100 pts to x."
            drawing = Drawing(400, 200)
            data = [(10, 20, 30, 42)]
            xAxis = XValueAxis()
            xAxis.setPosition(50, 50, 300)
            xAxis.configure(data)
            yAxis = YValueAxis()
            yAxis.setPosition(50, 50, 125)
            yAxis.joinAxis = xAxis
            yAxis.joinAxisMode = 'points'
            yAxis.joinAxisPos = 100
            yAxis.configure(data)
            drawing.add(xAxis)
            drawing.add(yAxis)
            return drawing

        def sample5b():
            "Sample drawing, xvalue/yvalue axes, y connected at value 35 of x."
            drawing = Drawing(400, 200)
            data = [(10, 20, 30, 42)]
            xAxis = XValueAxis()
            xAxis.setPosition(50, 50, 300)
            xAxis.configure(data)
            yAxis = YValueAxis()
            yAxis.setPosition(50, 50, 125)
            yAxis.joinAxis = xAxis
            yAxis.joinAxisMode = 'value'
            yAxis.joinAxisPos = 35
            yAxis.configure(data)
            drawing.add(xAxis)
            drawing.add(yAxis)
            return drawing

        def sample5c():
            "Sample drawing, xvalue/yvalue axes, y connected at right of x."
            drawing = Drawing(400, 200)
            data = [(10, 20, 30, 42)]
            xAxis = XValueAxis()
            xAxis.setPosition(50, 50, 300)
            xAxis.configure(data)
            yAxis = YValueAxis()
            yAxis.setPosition(50, 50, 125)
            yAxis.joinAxis = xAxis
            yAxis.joinAxisMode = 'right'
            yAxis.configure(data)
            drawing.add(xAxis)
            drawing.add(yAxis)
            return drawing

        def sample5d():
            "Sample drawing, xvalue/yvalue axes, y connected at left of x."
            drawing = Drawing(400, 200)
            data = [(10, 20, 30, 42)]
            xAxis = XValueAxis()
            xAxis.setPosition(50, 50, 300)
            xAxis.configure(data)
            yAxis = YValueAxis()
            yAxis.setPosition(50, 50, 125)
            yAxis.joinAxis = xAxis
            yAxis.joinAxisMode = 'left'
            yAxis.configure(data)
            drawing.add(xAxis)
            drawing.add(yAxis)
            return drawing

        def sample6a():
            "Sample drawing, xcat/yvalue axes, x connected at top of y."
            drawing = Drawing(400, 200)
            data = [(10, 20, 30, 42)]
            yAxis = YValueAxis()
            yAxis.setPosition(50, 50, 125)
            yAxis.configure(data)
            xAxis = XCategoryAxis()
            xAxis._length = 300
            xAxis.configure(data)
            xAxis.joinAxis = yAxis
            xAxis.joinAxisMode = 'top'
            xAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
            xAxis.labels.boxAnchor = 'n'
            drawing.add(xAxis)
            drawing.add(yAxis)
            return drawing

        def sample6b():
            "Sample drawing, xcat/yvalue axes, x connected at bottom of y."
            drawing = Drawing(400, 200)
            data = [(10, 20, 30, 42)]
            yAxis = YValueAxis()
            yAxis.setPosition(50, 50, 125)
            yAxis.configure(data)
            xAxis = XCategoryAxis()
            xAxis._length = 300
            xAxis.configure(data)
            xAxis.joinAxis = yAxis
            xAxis.joinAxisMode = 'bottom'
            xAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
            xAxis.labels.boxAnchor = 'n'
            drawing.add(xAxis)
            drawing.add(yAxis)
            return drawing

        def sample6c():
            "Sample drawing, xcat/yvalue axes, x connected at 100 pts to y."
            drawing = Drawing(400, 200)
            data = [(10, 20, 30, 42)]
            yAxis = YValueAxis()
            yAxis.setPosition(50, 50, 125)
            yAxis.configure(data)
            xAxis = XCategoryAxis()
            xAxis._length = 300
            xAxis.configure(data)
            xAxis.joinAxis = yAxis
            xAxis.joinAxisMode = 'points'
            xAxis.joinAxisPos = 100
            xAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
            xAxis.labels.boxAnchor = 'n'
            drawing.add(xAxis)
            drawing.add(yAxis)
            return drawing

        def sample6d():
            "Sample drawing, xcat/yvalue axes, x connected at value 20 of y."
            drawing = Drawing(400, 200)
            data = [(10, 20, 30, 42)]
            yAxis = YValueAxis()
            yAxis.setPosition(50, 50, 125)
            yAxis.configure(data)
            xAxis = XCategoryAxis()
            xAxis._length = 300
            xAxis.configure(data)
            xAxis.joinAxis = yAxis
            xAxis.joinAxisMode = 'value'
            xAxis.joinAxisPos = 20
            xAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
            xAxis.labels.boxAnchor = 'n'
            drawing.add(xAxis)
            drawing.add(yAxis)
            return drawing

        def sample7a():
            "Sample drawing, xvalue/ycat axes, y connected at right of x."
            drawing = Drawing(400, 200)
            data = [(10, 20, 30, 42)]
            xAxis = XValueAxis()
            xAxis._length = 300
            xAxis.configure(data)
            yAxis = YCategoryAxis()
            yAxis.setPosition(50, 50, 125)
            yAxis.joinAxis = xAxis
            yAxis.joinAxisMode = 'right'
            yAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
            yAxis.labels.boxAnchor = 'e'
            yAxis.configure(data)
            drawing.add(xAxis)
            drawing.add(yAxis)
            return drawing

        def sample7b():
            "Sample drawing, xvalue/ycat axes, y connected at left of x."
            drawing = Drawing(400, 200)
            data = [(10, 20, 30, 42)]
            xAxis = XValueAxis()
            xAxis._length = 300
            xAxis.configure(data)
            yAxis = YCategoryAxis()
            yAxis.setPosition(50, 50, 125)
            yAxis.joinAxis = xAxis
            yAxis.joinAxisMode = 'left'
            yAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
            yAxis.labels.boxAnchor = 'e'
            yAxis.configure(data)
            drawing.add(xAxis)
            drawing.add(yAxis)
            return drawing

        def sample7c():
            "Sample drawing, xvalue/ycat axes, y connected at value 30 of x."
            drawing = Drawing(400, 200)
            data = [(10, 20, 30, 42)]
            xAxis = XValueAxis()
            xAxis._length = 300
            xAxis.configure(data)
            yAxis = YCategoryAxis()
            yAxis.setPosition(50, 50, 125)
            yAxis.joinAxis = xAxis
            yAxis.joinAxisMode = 'value'
            yAxis.joinAxisPos = 30
            yAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
            yAxis.labels.boxAnchor = 'e'
            yAxis.configure(data)
            drawing.add(xAxis)
            drawing.add(yAxis)
            return drawing

        def sample7d():
            "Sample drawing, xvalue/ycat axes, y connected at 200 pts to x."
            drawing = Drawing(400, 200)
            data = [(10, 20, 30, 42)]
            xAxis = XValueAxis()
            xAxis._length = 300
            xAxis.configure(data)
            yAxis = YCategoryAxis()
            yAxis.setPosition(50, 50, 125)
            yAxis.joinAxis = xAxis
            yAxis.joinAxisMode = 'points'
            yAxis.joinAxisPos = 200
            yAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
            yAxis.labels.boxAnchor = 'e'
            yAxis.configure(data)
            drawing.add(xAxis)
            drawing.add(yAxis)
            return drawing

        def sample8a():
            "Sample drawing with one xlog axis"
            drawing = Drawing(400,200)

            data = [[float(i)**2. for i in range(10, 1001, 10)], ]

            xAxis = LogXValueAxis()
            xAxis.configure(data)

            drawing.add(xAxis)

            return drawing

        def sample8b():
            "Sample drawing with one xlog axis"
            drawing = Drawing(400,200)

            data = [[float(i)**2. for i in range(10, 1001, 10)], ]

            yAxis = LogYValueAxis()
            yAxis.configure(data)

            drawing.add(yAxis)

            return drawing

        def sample9a():
            lp = LinePlot()
            lp.yValueAxis = LogYValueAxis()
            lp.x += 20
            lp.y += 20
            data = [[(i, float(i)**2.) for i in range(10, 1001, 10)], ]
            data.append([(i, float(i)**3.) for i in range(10, 1001, 10)])
            data.append([(i, float(i)**1.6) for i in range(10, 1001, 10)])
            lp.data = data
            lp.lines.strokeWidth = .2
            lp.lines[0].strokeColor = colors.red
            lp.lines[1].strokeColor = colors.blue
            lp.lines[2].strokeColor = colors.green

            drawing = Drawing(400,200)
            drawing.add(lp)

            return drawing

        def sample9b():
            lp = LinePlot()
            lp.yValueAxis = LogYValueAxis()
            lp.x += 20
            lp.y += 20
            lp.height = 250
            lp.width = 350
            data = [[(i, float(i)**2.) for i in range(10, 1001, 10)], ]
            data.append([(i, float(i)**3.) for i in range(10, 1001, 10)])
            data.append([(i, float(i)**1.6) for i in range(10, 1001, 10)])
            lp.data = data
            lp.lines.strokeWidth = .2
            lp.lines[0].strokeColor = colors.red
            lp.lines[1].strokeColor = colors.blue
            lp.lines[2].strokeColor = colors.green

            lp.xValueAxis.visibleGrid = 1
            lp.xValueAxis.gridStrokeDashArray = [1, 1]
            lp.yValueAxis.visibleGrid = 1
            lp.yValueAxis.visibleSubTicks = 1
            lp.yValueAxis.visibleSubGrid = 1
            lp.yValueAxis.gridStrokeDashArray = [1, 1]
            lp.yValueAxis.subGridStrokeDashArray = [1, 1]

            drawing = Drawing(400,300)
            drawing.add(lp)

            return drawing

        def sample9c():
            lp = LinePlot()
            lp.yValueAxis = LogYValueAxis()
            lp.x += 20
            lp.y += 20
            lp.height = 250
            lp.width = 350
            data = [[(i, float(i)**2.) for i in range(10, 1001, 10)], ]
            data.append([(i, float(i)**3.) for i in range(10, 1001, 10)])
            data.append([(i, float(i)**1.6) for i in range(10, 1001, 10)])
            lp.data = data
            lp.lines.strokeWidth = .2
            lp.lines[0].strokeColor = colors.red
            lp.lines[1].strokeColor = colors.blue
            lp.lines[2].strokeColor = colors.green

            lp.xValueAxis.visibleGrid = 1
            lp.xValueAxis.gridStrokeDashArray = [1, 1]
            lp.yValueAxis.visibleGrid = 1
            lp.yValueAxis.visibleSubTicks = 1
            lp.yValueAxis.visibleSubGrid = 1
            lp.yValueAxis.subTickNum = 4
            lp.yValueAxis.gridStrokeDashArray = [.3, 1]
            lp.yValueAxis.subGridStrokeDashArray = [.15, 1]

            drawing = Drawing(400,300)
            drawing.add(lp)

            return drawing

        run_samples(locals())

    def test_legends(self):
        from reportlab.graphics.charts.legends import Legend, LineLegend, LineSwatch

        def sample1c():
            "Make sample legend."

            d = Drawing(200, 100)

            legend = Legend()
            legend.alignment = 'right'
            legend.x = 0
            legend.y = 100
            legend.dxTextSpace = 5
            items = 'red green blue yellow pink black white'.split()
            items = [(getattr(colors, i), i) for i in items]
            legend.colorNamePairs = items

            d.add(legend, 'legend')

            return d


        def sample2c():
            "Make sample legend."

            d = Drawing(200, 100)

            legend = Legend()
            legend.alignment = 'right'
            legend.x = 20
            legend.y = 90
            legend.deltax = 60
            legend.dxTextSpace = 10
            legend.columnMaximum = 4
            items = 'red green blue yellow pink black white'.split()
            items = [(getattr(colors, i), i) for i in items]
            legend.colorNamePairs = items

            d.add(legend, 'legend')

            return d

        def sample3():
            "Make sample legend with line swatches."

            d = Drawing(200, 100)

            legend = LineLegend()
            legend.alignment = 'right'
            legend.x = 20
            legend.y = 90
            legend.deltax = 60
            legend.dxTextSpace = 10
            legend.columnMaximum = 4
            items = 'red green blue yellow pink black white'.split()
            items = [(getattr(colors, i), i) for i in items]
            legend.colorNamePairs = items
            d.add(legend, 'legend')

            return d


        def sample3a():
            "Make sample legend with line swatches and dasharrays on the lines."
            d = Drawing(200, 100)
            legend = LineLegend()
            legend.alignment = 'right'
            legend.x = 20
            legend.y = 90
            legend.deltax = 60
            legend.dxTextSpace = 10
            legend.columnMaximum = 4
            items = 'red green blue yellow pink black white'.split()
            darrays = ([2,1], [2,5], [2,2,5,5], [1,2,3,4], [4,2,3,4], [1,2,3,4,5,6], [1])
            cnp = []
            for i in range(0, len(items)):
                l =  LineSwatch()
                l.strokeColor = getattr(colors, items[i])
                l.strokeDashArray = darrays[i]
                cnp.append((l, items[i]))
            legend.colorNamePairs = cnp
            d.add(legend, 'legend')

            return d

        def sample4a():
            '''Satish Darade failure''' 
            from reportlab.graphics.charts.legends import LegendSwatchCallout
            from reportlab.graphics import shapes
            class LSwatchCallout(LegendSwatchCallout):
                def __init__(self,texts,fontName,fontSize):
                    self._texts = texts
                    self._fontName = fontName
                    self._fontSize = fontSize

                def __call__(self,legend,g,thisx,y,i,colName,swatch):
                    g.add(shapes.String(swatch.x-2,y,self._texts[i],textAnchor='end',fontName=self._fontName,fontSize=self._fontSize))

            d = Drawing(200, 100)
            legend = LineLegend()
            d.add(legend, 'legend')
            items = 'red green blue yellow pink black white'
            sw_names = items.upper().split()
            items = items.split()
            legend.colorNamePairs = [(getattr(colors, i), i) for i in items]
            legend.x = 20
            legend.y = 90
            d.legend.swatchCallout = LSwatchCallout(sw_names,'Helvetica',12)
            return d

        run_samples(locals(),'legends')

def makeSuite():
    return makeSuiteForClasses(ChartTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
