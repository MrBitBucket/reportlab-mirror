# Tables of Contents and Indices
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/tocindex.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/tocindex.py,v 1.2 2000/11/21 10:59:12 andy_robinson Exp $
__version__=''' $Id: tocindex.py,v 1.2 2000/11/21 10:59:12 andy_robinson Exp $ '''
__doc__=''
"""
This module will contain standard Table of Contents and Index objects.
under development, and pending certain hooks adding in DocTemplate
As of today, it onyl handles the formatting aspect of TOCs
"""


from reportlab.platypus import Flowable, BaseDocTemplate, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import tables
from reportlab.lib import enums
from reportlab.lib import colors

    ##############################################################
    #
    # we first define a paragraph style for each level of the
    # table, and one for the table as whole; you can supply your
    # own.
    #
    ##############################################################


levelZeroParaStyle = ParagraphStyle(name='LevelZero',
                                  fontName='Times-Roman',
                                  fontSize=10,
                                  leading=12)
levelOneParaStyle = ParagraphStyle(name='LevelOne',
                                   parent = levelZeroParaStyle,
                                   firstLineIndent = 18,
                                   leftIndent = 18)
levelTwoParaStyle = ParagraphStyle(name='LevelTwo',
                                   parent = levelOneParaStyle,
                                   firstLineIndent = 36,
                                   leftIndent = 36)
levelThreeParaStyle = ParagraphStyle(name='LevelThree',
                                   parent = levelTwoParaStyle,
                                   firstLineIndent = 54,
                                   leftIndent = 54)

defaultTableStyle = tables.TableStyle([
                        ('VALIGN',(0,0),(-1,-1),'TOP'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                        ])

class TableOfContents0(Flowable):
    """This creates a formatted table of contents.  It presumes
    a correct block of data is passed in.  The data block contains
    a list of (level, text, pageNumber) triplets.  You can supply
    a paragraph style for each level (starting at zero)."""
    def __init__(self):
        self.entries = []
        self.rightColumnWidth = 72
        self.levelStyles = [levelZeroParaStyle,
                            levelOneParaStyle,
                            levelTwoParaStyle,
                            levelThreeParaStyle]
        self.tableStyle = defaultTableStyle
        self._table = None
        self._entries = []

    def clearEntries(self):
        self._entries = []

    def addEntry(self, level, text, pageNum):
        """Adds one entry; allows incremental buildup by a doctemplate.
        Requires that enough styles are defined."""
        assert type(level) == type(1), "Level must be an integer"
        assert level < len(self.levelStyles), \
               "Table of contents must have a style defined " \
               "for paragraph level %d before you add an entry" % level
        self._entries.append((level, text, pageNum))

    def addEntries(self, listOfEntries):
        """Bulk creation.  If you knew the titles but
        not the page numbers, you could supply them to
        get sensible output on the first run."""
        for (level, text, pageNum) in listOfEntries:
            self.addEntry(level, text, pageNum)
            
    def wrap(self, availWidth, availHeight):
        """All table properties should be known by now."""
        widths = (availWidth - self.rightColumnWidth,
                  self.rightColumnWidth)

        # makes an internal table which does all the work.
        tableData = []
        for (level, text, pageNum) in self._entries:
            leftColStyle = self.levelStyles[level]
            #right col style is right aligned
            rightColStyle = ParagraphStyle(name='leftColLevel%d' % level,
                                           parent=leftColStyle,
                                           leftIndent=0,
                                           alignment=enums.TA_RIGHT)
            leftPara = Paragraph(text, leftColStyle)
            rightPara = Paragraph(str(pageNum), rightColStyle)
            tableData.append([leftPara, rightPara])
        self._table = tables.Table(tableData, colWidths=widths,
                                   style=self.tableStyle)
        self.width, self.height = self._table.wrap(availWidth, availHeight)
        return (self.width, self.height)

    def split(self, availWidth, availHeight):
        """At this stage we do not care about splitting the entries,
        we wil just return a list of platypus tables.  Presumably the
        calling app has a pointer to the original TableOfContents object;
        Platypus just sees tables."""
        return self._table.split(availWidth, availHeight)

    def drawOn(self, canvas, x, y, _sW=0):
        """Don't do this at home!  The standard calls for implementing
        draw(); we are hooking this in order to delegate ALL the drawing
        work to the embedded table object"""
        self._table.drawOn(canvas, x, y, _sW)
        
        

def getSampleTOCData(depth=3):
    """Returns a longish block of page numbers over 3 levels"""
    from random import randint
    pgNum = 2
    data = []
    for chapter in range(1,11):
        data.append(0, """Chapter %d with a really long name which will hopefully
        wrap onto a second line, fnding out if the right things happen with
        full paragraphs n the table of contents""" % chapter, pgNum)
        pgNum = pgNum + randint(0,2)
        if depth > 1:
            for section in range(1,6):
                data.append(1, 'Chapter %d Section %d' % (chapter, section), pgNum)
                pgNum = pgNum + randint(0,2)
                if depth > 2:
                    for subSection in range(1,4):
                        data.append(2, 'Chapter %d Section %d Subsection %d' %
                                    (chapter, section, subSection),
                                    pgNum)
                        pgNum = pgNum + randint(0,1)
    return data        

def getSampleTOC(depth=3):
    data = getSampleTOCData(depth)
    toc = TableOfContents0()
    toc.addEntries(data)
    return toc

if __name__=='__main__':
    from reportlab.platypus import SimpleDocTemplate
    doc = SimpleDocTemplate('tocindex.pdf')

    story = [Paragraph("This is a demo of the table of contents object",
                       levelZeroParaStyle)]

    toc = getSampleTOC(3)
    story.append(toc)
    doc.build(story)
    print 'done'