#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
# tests some paragraph styles
__version__='''$Id$'''
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import unittest
from reportlab.platypus import Paragraph, SimpleDocTemplate, XBox, Indenter, XPreformatted, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.abag import ABag
from reportlab.lib.colors import red, black, navy, white, green
from reportlab.lib.randomtext import randomText
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.rl_config import defaultPageSize

(PAGE_WIDTH, PAGE_HEIGHT) = defaultPageSize

def myFirstPage(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(red)
    canvas.setLineWidth(5)
    canvas.line(66,72,66,PAGE_HEIGHT-72)
    canvas.setFont('Times-Bold',24)
    canvas.drawString(108, PAGE_HEIGHT-54, "TESTING PARAGRAPH STYLES")
    canvas.setFont('Times-Roman',12)
    canvas.drawString(4 * inch, 0.75 * inch, "First Page")
    canvas.restoreState()


def myLaterPages(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(red)
    canvas.setLineWidth(5)
    canvas.line(66,72,66,PAGE_HEIGHT-72)
    canvas.setFont('Times-Roman',12)
    canvas.drawString(4 * inch, 0.75 * inch, "Page %d" % doc.page)
    canvas.restoreState()


class ParagraphTestCase(unittest.TestCase):
    "Test Paragraph class (eyeball-test)."

    def test0(self):
        """Test...

        The story should contain...

        Features to be visually confirmed by a human being are:

            1. ...
            2. ...
            3. ...
        """

        story = []
        SA = story.append

        #need a style
        styNormal = ParagraphStyle('normal')
        styGreen = ParagraphStyle('green',parent=styNormal,textColor=green)

        styDots = ParagraphStyle('styDots',parent=styNormal,endDots='.')
        styDots1 = ParagraphStyle('styDots1',parent=styNormal,endDots=ABag(text=' -',dy=2,textColor='red'))
        styDotsR = ParagraphStyle('styDotsR',parent=styNormal,alignment=TA_RIGHT,endDots=' +')
        styDotsC = ParagraphStyle('styDotsC',parent=styNormal,alignment=TA_CENTER,endDots=' *')
        styDotsJ = ParagraphStyle('styDotsJ',parent=styNormal,alignment=TA_JUSTIFY,endDots=' =')

        istyDots = ParagraphStyle('istyDots',parent=styNormal,firstLineIndent=12,leftIndent=6,endDots='.')
        istyDots1 = ParagraphStyle('istyDots1',parent=styNormal,firstLineIndent=12,leftIndent=6,endDots=ABag(text=' -',dy=2,textColor='red'))
        istyDotsR = ParagraphStyle('istyDotsR',parent=styNormal,firstLineIndent=12,leftIndent=6,alignment=TA_RIGHT,endDots=' +')
        istyDotsC = ParagraphStyle('istyDotsC',parent=styNormal,firstLineIndent=12,leftIndent=6,alignment=TA_CENTER,endDots=' *')
        istyDotsJ = ParagraphStyle('istyDotsJ',parent=styNormal,firstLineIndent=12,leftIndent=6,alignment=TA_JUSTIFY,endDots=' =')

        styNormalCJK = ParagraphStyle('normal',wordWrap='CJK')
        styDotsCJK = ParagraphStyle('styDots',parent=styNormalCJK,endDots='.')
        styDots1CJK = ParagraphStyle('styDots1',parent=styNormalCJK,endDots=ABag(text=' -',dy=2,textColor='red'))
        styDotsRCJK = ParagraphStyle('styDotsR',parent=styNormalCJK,alignment=TA_RIGHT,endDots=' +')
        styDotsCCJK = ParagraphStyle('styDotsC',parent=styNormalCJK,alignment=TA_CENTER,endDots=' *')
        styDotsJCJK = ParagraphStyle('styDotsJ',parent=styNormalCJK,alignment=TA_JUSTIFY,endDots=' =')

        istyDotsCJK = ParagraphStyle('istyDots',parent=styNormalCJK,firstLineIndent=12,leftIndent=6,endDots='.')
        istyDots1CJK = ParagraphStyle('istyDots1',parent=styNormalCJK,firstLineIndent=12,leftIndent=6,endDots=ABag(text=' -',dy=2,textColor='red'))
        istyDotsRCJK = ParagraphStyle('istyDotsR',parent=styNormalCJK,firstLineIndent=12,leftIndent=6,alignment=TA_RIGHT,endDots=' +')
        istyDotsCCJK = ParagraphStyle('istyDotsC',parent=styNormalCJK,firstLineIndent=12,leftIndent=6,alignment=TA_CENTER,endDots=' *')
        istyDotsJCJK = ParagraphStyle('istyDotsJ',parent=styNormalCJK,firstLineIndent=12,leftIndent=6,alignment=TA_JUSTIFY,endDots=' =')
        

        # some to test
        stySpaced = ParagraphStyle('spaced',
                                   parent=styNormal,
                                   spaceBefore=12,
                                   spaceAfter=12)


        SA(Paragraph("This is a normal paragraph. "+ randomText(), styNormal))
        SA(Paragraph("There follows a paragraph with only \"&lt;br/&gt;\"", styNormal))
        SA(Paragraph("<br/>", styNormal))
        SA(Paragraph("This has 12 points space before and after, set in the style. " + randomText(), stySpaced))
        SA(Paragraph("This is normal. " + randomText(), styNormal))
        SA(Paragraph("""<para spacebefore="12" spaceafter="12">
            This has 12 points space before and after, set inline with
            XML tag.  It works too.""" + randomText() + "</para>",
                      styNormal))

        SA(Paragraph("This is normal. " + randomText(), styNormal))

        styBackground = ParagraphStyle('MyTitle',
                                       fontName='Helvetica-Bold',
                                       fontSize=24,
                                       leading=28,
                                       textColor=white,
                                       backColor=navy)
        SA(Paragraph("This is a title with a background. ", styBackground))
        SA(Paragraph("""<para backcolor="pink">This got a background from the para tag</para>""", styNormal))
        SA(Paragraph("""<para>\n\tThis has newlines and tabs on the front but inside the para tag</para>""", styNormal))
        SA(Paragraph("""<para>  This has spaces on the front but inside the para tag</para>""", styNormal))
        SA(Paragraph("""\n\tThis has newlines and tabs on the front but no para tag""", styNormal))
        SA(Paragraph("""  This has spaces on the front but no para tag""", styNormal))
        SA(Paragraph("""This has <font color=blue>blue text</font> here.""", styNormal))
        SA(Paragraph("""This has <i>italic text</i> here.""", styNormal))
        SA(Paragraph("""This has <b>bold text</b> here.""", styNormal))
        SA(Paragraph("""This has <u>underlined text</u> here.""", styNormal))
        SA(Paragraph("""This has <font color=blue><u>blue and <font color=red>red</font> underlined text</u></font> here.""", styNormal))
        SA(Paragraph("""<u>green underlining</u>""", styGreen))
        SA(Paragraph("""<u>green <font size="+4"><i>underlining</i></font></u>""", styGreen))
        SA(Paragraph("""This has m<super>2</super> a superscript.""", styNormal))
        SA(Paragraph("""This has m<sub>2</sub> a subscript. Like H<sub>2</sub>O!""", styNormal))
        SA(Paragraph("""This has a font change to <font name=Helvetica>Helvetica</font>.""", styNormal))
        #This one fails:
        #SA(Paragraph("""This has a font change to <font name=Helvetica-Oblique>Helvetica-Oblique</font>.""", styNormal))
        SA(Paragraph("""This has a font change to <font name=Helvetica><i>Helvetica in italics</i></font>.""", styNormal))

        SA(Paragraph('''This one uses upper case tags and has set caseSensitive=0: Here comes <FONT FACE="Helvetica" SIZE="14pt">Helvetica 14</FONT> with <STRONG>strong</STRONG> <EM>emphasis</EM>.''', styNormal, caseSensitive=0))
        SA(Paragraph('''The same as before, but has set not set caseSensitive, thus the tags are ignored: Here comes <FONT FACE="Helvetica" SIZE="14pt">Helvetica 14</FONT> with <STRONG>strong</STRONG> <EM>emphasis</EM>.''', styNormal))
        SA(Paragraph('''This one uses fonts with size "14pt" and also uses the em and strong tags: Here comes <font face="Helvetica" size="14pt">Helvetica 14</font> with <Strong>strong</Strong> <em>emphasis</em>.''', styNormal, caseSensitive=0))
        SA(Paragraph('''This uses a font size of 3cm: Here comes <font face="Courier" size="3cm">Courier 3cm</font> and normal again.''', styNormal, caseSensitive=0))
        SA(Paragraph('''This is just a very long silly text to see if the <FONT face="Courier">caseSensitive</FONT> flag also works if the paragraph is <EM>very</EM> long. '''*20, styNormal, caseSensitive=0))

        SA(Indenter("1cm"))
        SA(Paragraph("<para><bullet bulletIndent='-1cm' bulletOffsetY='2'><seq id='s0'/>)</bullet>Indented list bulletOffsetY=2. %s</para>" % randomText(), styNormal))
        SA(Paragraph("<para><bullet bulletIndent='-1cm'><seq id='s0'/>)</bullet>Indented list. %s</para>" % randomText(), styNormal))
        SA(Paragraph("<para><bullet bulletIndent='-1cm'><seq id='s0'/>)</bullet>Indented list. %s</para>" % randomText(), styNormal))
        SA(Indenter("1cm"))
        SA(XPreformatted("<para leftIndent='0.5cm' backcolor=pink><bullet bulletIndent='-1cm'><seq id='s1'/>)</bullet>Indented list.</para>", styNormal))
        SA(XPreformatted("<para leftIndent='0.5cm' backcolor=palegreen><bullet bulletIndent='-1cm'><seq id='s1'/>)</bullet>Indented list.</para>", styNormal))
        SA(Indenter("-1cm"))
        SA(Paragraph("<para><bullet bulletIndent='-1cm'><seq id='s0'/>)</bullet>Indented list. %s</para>" % randomText(), styNormal))
        SA(Indenter("-1cm"))
        SA(Paragraph("<para>Indented list using seqChain/Format<seqChain order='s0 s1 s2 s3 s4'/><seqReset id='s0'/><seqFormat id='s0' value='1'/><seqFormat id='s1' value='a'/><seqFormat id='s2' value='i'/><seqFormat id='s3' value='A'/><seqFormat id='s4' value='I'/></para>", stySpaced))
        SA(Indenter("1cm"))
        SA(Paragraph("<para><bullet bulletIndent='-1cm'><seq id='s0'/>)</bullet>Indented list. %s</para>" % randomText(), styNormal))
        SA(Paragraph("<para><bullet bulletIndent='-1cm'><seq id='s0'/>)</bullet>Indented list. %s</para>" % randomText(), styNormal))
        SA(Paragraph("<para><bullet bulletIndent='-1cm'><seq id='s0'/>)</bullet>Indented list. %s</para>" % randomText(), styNormal))
        SA(Indenter("1cm"))
        SA(XPreformatted("<para backcolor=pink boffsety='-3'><bullet bulletIndent='-1cm'><seq id='s1'/>)</bullet>Indented list bulletOffsetY=-3.</para>", styNormal))
        SA(XPreformatted("<para backcolor=pink><bullet bulletIndent='-1cm'><seq id='s1'/>)</bullet>Indented list.</para>", styNormal))
        SA(Indenter("-1cm"))
        SA(Paragraph("<para><bullet bulletIndent='-1cm'><seq id='s0'/>)</bullet>Indented list. %s</para>" % randomText(), styNormal))
        SA(Indenter("1cm"))
        SA(XPreformatted("<para backcolor=palegreen><bullet bulletIndent='-1cm'><seq id='s1'/>)</bullet>Indented list.</para>", styNormal))
        SA(Indenter("1cm"))
        SA(XPreformatted("<para><bullet bulletIndent='-1cm'><seq id='s2'/>)</bullet>Indented list. line1</para>", styNormal))
        SA(XPreformatted("<para><bullet bulletIndent='-1cm'><seq id='s2'/>)</bullet>Indented list. line2</para>", styNormal))
        SA(Indenter("-1cm"))
        SA(XPreformatted("<para backcolor=palegreen><bullet bulletIndent='-1cm'><seq id='s1'/>)</bullet>Indented list.</para>", styNormal))
        SA(Indenter("-1cm"))
        SA(Indenter("-1cm"))
        
        for i in range(2):
            SA(PageBreak())
            SA(Paragraph('''%s dotted paragraphs''' % (i and 'CJK' or 'Normal'), styNormal))
            SA(Paragraph('''Simple paragraph with dots''', i and styDotsCJK or styDots))
            SA(Paragraph('''Simple indented paragraph with dots''', i and istyDotsCJK or istyDots))
            SA(Paragraph('''Simple centred paragraph with stars''', i and styDotsCCJK or styDotsC))
            SA(Paragraph('''Simple centred indented paragraph with stars''', i and istyDotsCCJK or istyDotsC))
            SA(Paragraph('''Simple right justified paragraph with pluses, but no pluses''', i and styDotsRCJK or styDotsR))
            SA(Paragraph('''Simple right justified indented paragraph with pluses, but no pluses''', i and istyDotsRCJK or istyDotsR))
            SA(Paragraph('''Simple justified paragraph with equals''', i and styDotsJCJK or styDotsJ))
            SA(Paragraph('''Simple justified indented paragraph with equals''', i and istyDotsJCJK or istyDotsJ))
            SA(Paragraph('''A longer simple paragraph with dots''', i and styDotsCJK or styDots))
            SA(Paragraph('''A longer simple indented paragraph with dots''', i and istyDotsCJK or istyDots))
            SA(Paragraph('A very much' +50*' longer'+' simple paragraph with dots', i and styDotsCJK or styDots))
            SA(Paragraph('A very much' +50*' longer'+' simple indented paragraph with dots', i and istyDotsCJK or istyDots))
            SA(Paragraph('A very much' +50*' longer'+' centred simple paragraph with stars', i and styDotsCCJK or styDotsC))
            SA(Paragraph('A very much' +50*' longer'+' centred simple indented paragraph with stars', i and istyDotsCCJK or istyDotsC))
            SA(Paragraph('A very much' +50*' longer'+' right justified simple paragraph with pluses, but no pluses', i and styDotsRCJK or styDotsR))
            SA(Paragraph('A very much' +50*' longer'+' right justified simple indented paragraph with pluses, but no pluses', i and istyDotsRCJK or istyDotsR))
            SA(Paragraph('A very much' +50*' longer'+' justified simple paragraph with equals', i and styDotsJCJK or styDotsJ))
            SA(Paragraph('A very much' +50*' longer'+' justified simple indented paragraph with equals', i and istyDotsJCJK or istyDotsJ))
            SA(Paragraph('''Simple paragraph with dashes that have a dy and a textColor.''', i and styDots1CJK or styDots1))
            SA(Paragraph('''Simple indented paragraph with dashes that have a dy and a textColor.''', i and istyDots1CJK or istyDots1))
            SA(Paragraph('''Complex <font color="green">paragraph</font> with dots''', i and styDotsCJK or styDots))
            SA(Paragraph('''Complex <font color="green">indented paragraph</font> with dots''', i and istyDotsCJK or istyDots))
            SA(Paragraph('''Complex centred <font color="green">paragraph</font> with stars''', i and styDotsCCJK or styDotsC))
            SA(Paragraph('''Complex centred <font color="green">indented paragraph</font> with stars''', i and istyDotsCCJK or istyDotsC))
            SA(Paragraph('''Complex right justfied <font color="green">paragraph</font> with pluses, but no pluses''', i and styDotsRCJK or styDotsR))
            SA(Paragraph('''Complex right justfied <font color="green">indented paragraph</font> with pluses, but no pluses''', i and istyDotsRCJK or istyDotsR))
            SA(Paragraph('''Complex justfied <font color="green">paragraph</font> with equals''', i and styDotsJCJK or styDotsJ))
            SA(Paragraph('''Complex justfied <font color="green">indented paragraph</font> with equals''', i and istyDotsJCJK or istyDotsJ))
            SA(Paragraph('''A longer complex <font color="green">paragraph</font> with dots''', i and styDotsCJK or styDots))
            SA(Paragraph('''A longer complex <font color="green">indented paragraph</font> with dots''', i and istyDotsCJK or istyDots))
            SA(Paragraph('A very much' +50*' longer'+' complex <font color="green">paragraph</font> with dots', i and styDotsCJK or styDots))
            SA(Paragraph('A very much' +50*' longer'+' complex <font color="green">indented paragraph</font> with dots', i and istyDotsCJK or istyDots))
            SA(Paragraph('''Complex <font color="green">paragraph</font> with dashes that have a dy and a textColor.''', i and styDots1CJK or styDots1))
            SA(Paragraph('''Complex <font color="green">indented paragraph</font> with dashes that have a dy and a textColor.''', i and istyDots1CJK or istyDots1))
            SA(Paragraph('A very much' +50*' longer'+' centred complex <font color="green">paragraph</font> with stars', i and styDotsCCJK or styDotsC))
            SA(Paragraph('A very much' +50*' longer'+' centred complex <font color="green">indented paragraph</font> with stars', i and istyDotsCCJK or istyDotsC))
            SA(Paragraph('A very much' +50*' longer'+' right justified <font color="green">complex</font> paragraph with pluses, but no pluses', i and styDotsRCJK or styDotsR))
            SA(Paragraph('A very much' +50*' longer'+' right justified <font color="green">complex</font> indented paragraph with pluses, but no pluses', i and istyDotsRCJK or istyDotsR))
            SA(Paragraph('A very much' +50*' longer'+' justified complex <font color="green">paragraph</font> with equals', i and styDotsJCJK or styDotsJ))
            SA(Paragraph('A very much' +50*' longer'+' justified complex <font color="green">indented paragraph</font> with equals', i and istyDotsJCJK or istyDotsJ))

        template = SimpleDocTemplate(outputfile('test_paragraphs.pdf'),
                                     showBoundary=1)
        template.build(story,
            onFirstPage=myFirstPage, onLaterPages=myLaterPages)


def makeSuite():
    return makeSuiteForClasses(ParagraphTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
