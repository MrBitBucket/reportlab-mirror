#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/test/test_paragraphs.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/test_paragraphs.py,v 1.12 2002/07/04 09:24:49 dinu_gherman Exp $
# tests some paragraph styles

from reportlab.test import unittest
from reportlab.test.utils import makeSuiteForClasses

from reportlab.platypus import Paragraph, SimpleDocTemplate, XBox
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import red, black, navy, white
from reportlab.lib.randomtext import randomText
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
        
        #need a style
        styNormal = ParagraphStyle('normal')
        
        # some to test
        stySpaced = ParagraphStyle('spaced',
                                   parent=styNormal,
                                   spaceBefore=12,
                                   spaceAfter=12)
        

        story.append(
            Paragraph("This is a normal paragraph. "
                      + randomText(), styNormal))
        story.append(
            Paragraph("This has 12 points space before and after, set in the style. "
                      + randomText(), stySpaced))
        story.append(
            Paragraph("This is normal. " +
                      randomText(), styNormal))

        story.append(
            Paragraph("""<para spacebefore="12" spaceafter="12">
            This has 12 points space before and after, set inline with
            XML tag.  It works too.""" + randomText() + "</para",
                      styNormal))

        story.append(
            Paragraph("This is normal. " +
                      randomText(), styNormal))

        styBackground = ParagraphStyle('MyTitle',
                                       fontName='Helvetica-Bold',
                                       fontSize=24,
                                       leading=28,
                                       textColor=white,
                                       backColor=navy)
        story.append(
            Paragraph("This is a title with a background. ", styBackground))
        
        story.append(
            Paragraph("""<para backcolor="pink">This got a background from the para tag</para>""", styNormal))


        story.append(
            Paragraph("""<para>\n\tThis has newlines and tabs on the front but inside the para tag</para>""", styNormal))
        story.append(
            Paragraph("""<para>  This has spaces on the front but inside the para tag</para>""", styNormal))

        story.append(
            Paragraph("""\n\tThis has newlines and tabs on the front but no para tag""", styNormal))
        story.append(
            Paragraph("""  This has spaces on the front but no para tag""", styNormal))

        story.append(Paragraph("""This has <font color=blue>blue text</font> here.""", styNormal))
        story.append(Paragraph("""This has <i>italic text</i> here.""", styNormal))
        story.append(Paragraph("""This has <b>bold text</b> here.""", styNormal))
        story.append(Paragraph("""This has m<super>2</super> a superscript.""", styNormal))
        story.append(Paragraph("""This has m<sub>2</sub> a subscript.""", styNormal))
        story.append(Paragraph("""This has a font change to <font name=Helvetica>Helvetica</font>.""", styNormal))
		#This one fails:
        #story.append(Paragraph("""This has a font change to <font name=Helvetica-Oblique>Helvetica-Oblique</font>.""", styNormal))
        story.append(Paragraph("""This has a font change to <font name=Helvetica><i>Helvetica in italics</i></font>.""", styNormal))
		

        template = SimpleDocTemplate('test_paragraphs.pdf',
                                     showBoundary=1)
        template.build(story,
            onFirstPage=myFirstPage, onLaterPages=myLaterPages)
        

def makeSuite():
    return makeSuiteForClasses(ParagraphTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
