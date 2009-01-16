#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/platypus/tableofcontents.py

__version__=''' $Id$ '''
__doc__="""Experimental class to generate Tables of Contents easily

This module defines a single TableOfContents() class that can be used to
create automatically a table of tontents for Platypus documents like
this:

    story = []
    toc = TableOfContents()
    story.append(toc)
    # some heading paragraphs here...
    doc = MyTemplate(path)
    doc.multiBuild(story)

The data needed to create the table is a list of (level, text, pageNum)
triplets, plus some paragraph styles for each level of the table itself.
The triplets will usually be created in a document template's method
like afterFlowable(), making notification calls using the notify()
method with appropriate data like this:

    (level, text, pageNum) = ...
    self.notify('TOCEntry', (level, text, pageNum))

Optionally the list can contain four items in which case the last item
is a destination key which the entry should point to. A bookmark
with this key needs to be created first like this:

    key = 'ch%s' % self.seq.nextf('chapter')
    self.canv.bookmarkPage(key)
    self.notify('TOCEntry', (level, text, pageNum, key))

As the table of contents need at least two passes over the Platypus
story which is why the moultiBuild0() method must be called.

The level<NUMBER>ParaStyle variables are the paragraph styles used
to format the entries in the table of contents. Their indentation
is calculated like this: each entry starts at a multiple of some
constant named delta. If one entry spans more than one line, all
lines after the first are indented by the same constant named
epsilon.
"""

import string

from reportlab.lib import enums
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.doctemplate import IndexingFlowable
from reportlab.platypus.tables import TableStyle, Table
from reportlab.platypus.flowables import Spacer
from reportlab.pdfbase.pdfmetrics import stringWidth

# Default paragraph styles for tables of contents.
# (This could also be generated automatically or even
# on-demand if it is not known how many levels the
# TOC will finally need to display...)

delta = 1*cm
epsilon = 0.5*cm

levelZeroParaStyle = \
    ParagraphStyle(name='LevelZero',
                   fontName='Times-Roman',
                   fontSize=10,
                   leading=11,
                   firstLineIndent = -epsilon,
                   leftIndent = 0*delta + epsilon)

levelOneParaStyle = \
    ParagraphStyle(name='LevelOne',
                   parent = levelZeroParaStyle,
                   leading=11,
                   firstLineIndent = -epsilon,
                   leftIndent = 1*delta + epsilon)

levelTwoParaStyle = \
    ParagraphStyle(name='LevelTwo',
                   parent = levelOneParaStyle,
                   leading=11,
                   firstLineIndent = -epsilon,
                   leftIndent = 2*delta + epsilon)

levelThreeParaStyle = \
    ParagraphStyle(name='LevelThree',
                   parent = levelTwoParaStyle,
                   leading=11,
                   firstLineIndent = -epsilon,
                   leftIndent = 3*delta + epsilon)

levelFourParaStyle = \
    ParagraphStyle(name='LevelFour',
                   parent = levelTwoParaStyle,
                   leading=11,
                   firstLineIndent = -epsilon,
                   leftIndent = 4*delta + epsilon)

defaultTableStyle = \
    TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')])


class TableOfContents(IndexingFlowable):
    """This creates a formatted table of contents.

    It presumes a correct block of data is passed in.
    The data block contains a list of (level, text, pageNumber)
    triplets.  You can supply a paragraph style for each level
    (starting at zero).
    Set dotsMinLevel to determine from which level on a line of
    dots should be drawn between the text and the page number.
    If dotsMinLevel is set to a negative value, no dotted lines are drawn.
    """

    def __init__(self):
        self.rightColumnWidth = 72
        self.levelStyles = [levelZeroParaStyle,
                            levelOneParaStyle,
                            levelTwoParaStyle,
                            levelThreeParaStyle,
                            levelFourParaStyle]
        self.tableStyle = defaultTableStyle
        self.dotsMinLevel = 1
        self._table = None
        self._entries = []
        self._lastEntries = []


    def beforeBuild(self):
        # keep track of the last run
        self._lastEntries = self._entries[:]
        self.clearEntries()


    def isIndexing(self):
        return 1


    def isSatisfied(self):
        return (self._entries == self._lastEntries)

    def notify(self, kind, stuff):
        """The notification hook called to register all kinds of events.

        Here we are interested in 'TOCEntry' events only.
        """
        if kind == 'TOCEntry':
            self.addEntry(*stuff)


    def clearEntries(self):
        self._entries = []


    def addEntry(self, level, text, pageNum, key=None):
        """Adds one entry to the table of contents.

        This allows incremental buildup by a doctemplate.
        Requires that enough styles are defined."""

        assert type(level) == type(1), "Level must be an integer"
        assert level < len(self.levelStyles), \
               "Table of contents must have a style defined " \
               "for paragraph level %d before you add an entry" % level

        self._entries.append((level, text, pageNum, key))


    def addEntries(self, listOfEntries):
        """Bulk creation of entries in the table of contents.

        If you knew the titles but not the page numbers, you could
        supply them to get sensible output on the first run."""

        for entryargs in listOfEntries:
            self.addEntry(*entryargs)


    def wrap(self, availWidth, availHeight):
        "All table properties should be known by now."

        # makes an internal table which does all the work.
        # we draw the LAST RUN's entries!  If there are
        # none, we make some dummy data to keep the table
        # from complaining
        if len(self._lastEntries) == 0:
            _tempEntries = [(0,'Placeholder for table of contents',0,None)]
        else:
            _tempEntries = self._lastEntries

        def drawTOCEntryEnd(canvas, kind, label):
            '''Callback to draw dots and page numbers after each entry.'''
            page, level = [ int(x) for x in label.split(',') ]
            x, y = canvas._curr_tx_info['cur_x'], canvas._curr_tx_info['cur_y']
            style = self.levelStyles[level]
            pagew = stringWidth('  %d' % page, style.fontName, style.fontSize)
            if self.dotsMinLevel >= 0 and level >= self.dotsMinLevel:
                dotw = stringWidth(' . ', style.fontName, style.fontSize)
                dotsn = int((availWidth-x-pagew)/dotw)
            else:
                dotsn = dotw = 0

            tx = canvas.beginText(availWidth-pagew-dotsn*dotw, y)
            tx.setFont(style.fontName, style.fontSize)
            tx.textLine('%s  %d' % (dotsn * ' . ', page))
            canvas.drawText(tx)
        self.canv.drawTOCEntryEnd = drawTOCEntryEnd

        tableData = []
        for (level, text, pageNum, key) in _tempEntries:
            style = self.levelStyles[level]
            if key:
                text = '<a href="#%s">%s</a>' % (key, text)
            para = Paragraph('%s<onDraw name="drawTOCEntryEnd" label="%d,%d"/>' % (text, pageNum, level), style)
            if style.spaceBefore:
                tableData.append([Spacer(1, style.spaceBefore),])
            tableData.append([para,])

        self._table = Table(tableData, colWidths=(availWidth,),
                            style=self.tableStyle)

        self.width, self.height = self._table.wrapOn(self.canv,availWidth, availHeight)
        return (self.width, self.height)


    def split(self, availWidth, availHeight):
        """At this stage we do not care about splitting the entries,
        we will just return a list of platypus tables.  Presumably the
        calling app has a pointer to the original TableOfContents object;
        Platypus just sees tables.
        """
        return self._table.splitOn(self.canv,availWidth, availHeight)


    def drawOn(self, canvas, x, y, _sW=0):
        """Don't do this at home!  The standard calls for implementing
        draw(); we are hooking this in order to delegate ALL the drawing
        work to the embedded table object.
        """
        self._table.drawOn(canvas, x, y, _sW)


class SimpleIndex(IndexingFlowable):
    """This creates a very simple index.

    Entries have a string key, and appear with a page number on
    the right.  Prototype for more sophisticated multi-level index."""
    def __init__(self):
        #keep stuff in a dictionary while building
        self._entries = {}
        self._lastEntries = {}
        self._table = None
        self.textStyle = ParagraphStyle(name='index',
                                        fontName='Times-Roman',
                                        fontSize=12)
    def isIndexing(self):
        return 1

    def isSatisfied(self):
        return (self._entries == self._lastEntries)

    def beforeBuild(self):
        # keep track of the last run
        self._lastEntries = self._entries.copy()
        self.clearEntries()

    def clearEntries(self):
        self._entries = {}

    def notify(self, kind, stuff):
        """The notification hook called to register all kinds of events.

        Here we are interested in 'IndexEntry' events only.
        """
        if kind == 'IndexEntry':
            (text, pageNum) = stuff
            self.addEntry(text, pageNum)

    def addEntry(self, text, pageNum):
        """Allows incremental buildup"""
        if self._entries.has_key(text):
            self._entries[text].append(str(pageNum))
        else:
            self._entries[text] = [pageNum]

    def split(self, availWidth, availHeight):
        """At this stage we do not care about splitting the entries,
        we will just return a list of platypus tables.  Presumably the
        calling app has a pointer to the original TableOfContents object;
        Platypus just sees tables.
        """
        return self._table.splitOn(self.canv,availWidth, availHeight)

    def wrap(self, availWidth, availHeight):
        "All table properties should be known by now."
        # makes an internal table which does all the work.
        # we draw the LAST RUN's entries!  If there are
        # none, we make some dummy data to keep the table
        # from complaining
        if len(self._lastEntries) == 0:
            _tempEntries = [('Placeholder for index',[0,1,2])]
        else:
            _tempEntries = self._lastEntries.items()
            _tempEntries.sort()

        tableData = []
        for (text, pageNumbers) in _tempEntries:
            #right col style is right aligned
            allText = text + ': ' + string.join(map(str, pageNumbers), ', ')
            para = Paragraph(allText, self.textStyle)
            tableData.append([para])

        self._table = Table(tableData, colWidths=[availWidth])

        self.width, self.height = self._table.wrapOn(self.canv,availWidth, availHeight)
        return (self.width, self.height)

    def drawOn(self, canvas, x, y, _sW=0):
        """Don't do this at home!  The standard calls for implementing
        draw(); we are hooking this in order to delegate ALL the drawing
        work to the embedded table object.
        """
        self._table.drawOn(canvas, x, y, _sW)

class ReferenceText(IndexingFlowable):
    """Fakery to illustrate how a reference would work if we could
    put it in a paragraph."""
    def __init__(self, textPattern, targetKey):
        self.textPattern = textPattern
        self.target = targetKey
        self.paraStyle = ParagraphStyle('tmp')
        self._lastPageNum = None
        self._pageNum = -999
        self._para = None

    def beforeBuild(self):
        self._lastPageNum = self._pageNum

    def notify(self, kind, stuff):
        if kind == 'Target':
            (key, pageNum) = stuff
            if key == self.target:
                self._pageNum = pageNum

    def wrap(self, availWidth, availHeight):
        text = self.textPattern % self._lastPageNum
        self._para = Paragraph(text, self.paraStyle)
        return self._para.wrap(availWidth, availHeight)

    def drawOn(self, canvas, x, y, _sW=0):
        self._para.drawOn(canvas, x, y, _sW)


