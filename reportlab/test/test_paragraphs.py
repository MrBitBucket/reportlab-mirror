# tests some paragraph styles
from reportlab.platypus import Paragraph, SimpleDocTemplate, XBox
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import red, black, navy, white

from reportlab.lib.pagesizes import DEFAULT_PAGE_SIZE
(PAGE_WIDTH, PAGE_HEIGHT) = DEFAULT_PAGE_SIZE

from reportlab.lib.randomtext import randomText

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

def run():
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


    template = SimpleDocTemplate('test_paragraphs.pdf',
                                 showBoundary=1)
    template.build(story,
        onFirstPage=myFirstPage,onLaterPages=myLaterPages)

if __name__ == '__main__':
    run()
