# doc template for RL manuals.  Currently YAML is hard-coded
#to use this, which is wrong.


from reportlab.platypus import PageTemplate, \
     BaseDocTemplate, Frame, Paragraph
from reportlab.lib.units import inch, cm

##def decoratePage(canvas, doc):##    canvas.saveState()
##    canvas.setFont('Times-Roman', 10)
##    canvas.drawCentredString(doc.pagesize[0] / 2, 0.75*inch, 'Page %d' % canvas.getPageNumber())
##    canvas.restoreState()

class RLBodyPageTemplate(PageTemplate):
    def __init__(self, id):
        myFrame = Frame(inch, inch, 6*inch, 10*inch, id='normal')
        PageTemplate.__init__(self, id, [myFrame])  # note lack of onPage

    def drawPage(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 10)
        canvas.drawRightString(7*inch, 11.1*inch, doc.chapter)
        canvas.line(inch, 11*inch, 7*inch, 11*inch)
        canvas.drawCentredString(doc.pagesize[0] / 2, 0.75*inch, 'Page %d' % canvas.getPageNumber())
        canvas.restoreState()



class RLDocTemplate(BaseDocTemplate):
    _invalidInitArgs = ('pageTemplates',)
    def __init__(self, filename, **kw):
        apply(BaseDocTemplate.__init__,(self,filename),kw)

        #give it a single PageTemplate
        self.addPageTemplates(RLBodyPageTemplate('Normal'))

        #just playing
        self.title = "Document Titles Goes Here"
        self.chapter = "(No chapter yet)"

    def handle_flowable(self, flowables):
        
        flo_before = flowables[0]
        self._handle_flowable(flowables)
        if flowables:
            flo_after = flowables[0]
            if flo_before <> flo_after:
                #it got drawn.  Must be an easier way
                if isinstance(flo_after, Paragraph):
                    self.chapter = flo_after.text[0:20]
