# doc template for RL manuals.  Currently YAML is hard-coded
#to use this, which is wrong.


from reportlab.platypus import PageTemplate, \
     UserDocTemplate, Frame, Paragraph
from reportlab.lib.units import inch, cm

##def decoratePage(canvas, doc):##    canvas.saveState()
##    canvas.setFont('Times-Roman', 10)
##    canvas.drawCentredString(doc.pagesize[0] / 2, 0.75*inch, 'Page %d' % canvas.getPageNumber())
##    canvas.restoreState()


class OneColumnTemplate(PageTemplate):
    def __init__(self, id):
        frame1 = Frame(inch, inch, 6.27*inch, 9.69*inch, id='normal')
        PageTemplate.__init__(self, id, [frame1])  # note lack of onPage

    def afterDrawPage(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 10)
        canvas.drawString(inch, 11.1*inch, doc.title)
        canvas.drawRightString(7*inch, 11.1*inch, doc.chapter)
        canvas.line(inch, 11*inch, 7*inch, 11*inch)
        canvas.drawCentredString(doc.pagesize[0] / 2, 0.75*inch, 'Page %d' % canvas.getPageNumber())
        canvas.restoreState()

class TwoColumnTemplate(PageTemplate):
    def __init__(self, id):
        frame1 = Frame(inch, inch, 3*inch, 9.69*inch, id='leftCol')
        frame2 = Frame(4.27 * inch, inch, 3*inch, 9.69*inch, id='rightCol')
        PageTemplate.__init__(self, id, [frame1, frame2])  # note lack of onPage

    def afterDrawPage(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 10)
        canvas.drawString(inch, 11.1*inch, doc.title)
        canvas.drawRightString(7*inch, 11.1*inch, doc.chapter)
        canvas.line(inch, 11*inch, 7*inch, 11*inch)
        canvas.drawCentredString(doc.pagesize[0] / 2, 0.75*inch, 'Page %d' % canvas.getPageNumber())
        canvas.restoreState()


class RLDocTemplate(UserDocTemplate):
    def afterInit(self):
        self.addPageTemplates(OneColumnTemplate('Normal'))
        self.addPageTemplates(TwoColumnTemplate('TwoColumn'))

        #just playing
        self.title = "(Document Title Goes Here)"
        self.chapter = "(No chapter yet)"
        self.chapterNo = 1 #unique keys
        self.sectionNo = 1 # uniqque keys
        
    def beforeDocument(self):
        self.canv.showOutline()
        
    def afterFlowable(self, flowable):
        """Detect Level 1 and 2 headings, build outline,
        and track chapter title."""
        if isinstance(flowable, Paragraph):
            style = flowable.style.name
            if style == 'Title':
                self.title = flowable.getPlainText()
            elif style == 'Heading1':
                self.chapter = flowable.getPlainText()
                key = 'ch%d' % self.chapterNo
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(flowable.getPlainText(),
                                            key, 0, 0)
                self.chapterNo = self.chapterNo + 1
                self.sectionNo = 1
            elif style == 'Heading2':
                self.section = flowable.text
                key = 'ch%ds%d' % (self.chapterNo, self.sectionNo)
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(flowable.getPlainText(),
                                             key, 1, 0)
                self.sectionNo = self.sectionNo + 1

