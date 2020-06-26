#Copyright ReportLab Europe Ltd. 2000-2017
#see license.txt for license details
"""Tests for the reportlab.platypus.paragraphs module.
"""
__version__='3.5.23'
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import sys, os, unittest

class IssueTestCase(unittest.TestCase):
    def test_issue183(self):
        '''issue 183 raised by Marius Gedminas'''
        from reportlab.pdfgen.canvas import Canvas
        from reportlab.platypus.paragraph import Paragraph
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.pdfbase.pdfmetrics import registerFont
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.enums import TA_JUSTIFY
        sty = ParagraphStyle('A')
        sty.fontSize = 11
        sty.leading = sty.fontSize*1.2
        sty.fontName = 'Helvetica'
        sty.alignment = TA_JUSTIFY
        canv = Canvas(outputfile('test_issue183.pdf'))
        aW = 440
        text = u'''AAAAAAAAAAAA BBBBB C Dddd EEEEEEEE\xa0\u2014 FF GGGGGG HHHHHHHHH III JJJJJJJJJ KKK
LLLLLLLLL MMMMMM NNNNN O PPPPPP Q RRRRR SSSSSS TTTTTTTTTTT. UUUUUUU VVVVVVVV
WWWWWWWWWWWW XXX YYYYYY ABBBBB BCCCCCCCCCCC.'''
        def do1(x,y,text,sty):
            p = Paragraph(text,sty)
            w,h=p.wrap(aW,1000000)
            y -= h
            p.drawOn(canv,x,y)
            canv.saveState()
            canv.setLineWidth(0.5)
            canv.setStrokeColor((1,0,0))
            canv.rect(x,y,aW,h,stroke=1,fill=0)
            canv.restoreState()
            return y

        def do2(x,y,text,sty):
            y = do1(x,y,text,sty)
            return do1(x,y-10,text.replace(u'\xa0\u2014',u'&nbsp;&mdash;'),sty)

        fonts = set()
        fonts.add('Helvetica')
        for fontName, fontPath in (('Vera','Vera.ttf'),
                ('TTFTimes','times.ttf'),
                ('TTFTimes','Times.TTF')):
            try:
                registerFont(TTFont(fontName, fontPath))
                fonts.add(fontName)
            except:
                pass

        y = canv._pagesize[1] - 72
        y = do2(72,y,text,sty)
        if 'Vera' in fonts:
            styv = sty.clone('AV',fontName='Vera')
            y = do2(72,y-10,text,styv)

        if 'TTFTimes' in fonts:
            styv = sty.clone('AV',fontName='TTFTimes')
            y = do2(72,y-10,text,styv)

        text = u'|A B C D E F G H I J K L|'
        y -= 13.1
        offs = None
        for fontName in 'Helvetica Vera TTFTimes'.split():
            if fontName not in fonts: continue
            for ws in 0, -1, 1:
                for s in (u' ',u'\xa0'):
                    canv.saveState()
                    canv.setFont('Courier',11)
                    lab = '%-9s ws=%2d %s:' % (fontName,ws,s==u' ' and 'soft' or 'hard')
                    if offs == None:
                        offs = 72+canv.stringWidth(lab)+2
                    canv.drawString(72,y,lab)
                    canv.setFont(fontName,11)
                    canv.drawString(offs,y,text.replace(u' ',s),wordSpace=ws)
                    canv.restoreState()
                    y -= 13.1

        canv.showPage()
        canv.save()

    def test_issue181(self):
        '''issue #181 rasied by Daniel Turecek'''
        from reportlab.lib.styles import ParagraphStyle as PS
        from reportlab.platypus import Paragraph, SimpleDocTemplate, PageBreak
        style = PS(fontname='Helvetica', name='Title', fontSize=10, leading=12, alignment=1)
        add = [].append
        add(Paragraph('<a name="top"/>Top', style))
        add(Paragraph('<a href="#test">Local Link</a>', style))
        add(Paragraph('<a href="document:test">Document Link</a>', style))
        add(Paragraph('<a href="www.reportlab.com">website</a>', style))
        add(PageBreak())
        add(Paragraph('<a name="test"/>Anchor', style))
        add(Paragraph('<a href="#top">top</a>', style))
        doc = SimpleDocTemplate(outputfile("test_issue181.pdf"))
        doc.build(add.__self__)

#noruntests
def makeSuite():
    return makeSuiteForClasses(IssueTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
