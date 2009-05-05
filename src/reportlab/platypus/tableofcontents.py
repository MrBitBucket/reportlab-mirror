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

from reportlab.lib import enums
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.doctemplate import IndexingFlowable
from reportlab.platypus.tables import TableStyle, Table
from reportlab.platypus.flowables import Spacer, Flowable
from reportlab.pdfbase.pdfmetrics import stringWidth
try:
    set
except:
    class set(list):
        def add(self,x):
            if x not in self:
                list.append(self,x)

def drawPageNumbers(canvas, style, pagestr, availWidth, availHeight, dot=' . '):
    '''
    Draws pagestr on the canvas using the given style.
    If dot is None, pagestr is drawn at the current position in the canvas.
    If dot is a string, pagestr is drawn right-aligned. If the string is not empty,
    the gap is filled with it.
    '''
    x, y = canvas._curr_tx_info['cur_x'], canvas._curr_tx_info['cur_y']
    pagestrw = stringWidth(pagestr, style.fontName, style.fontSize)
    if isinstance(dot, basestring):
        if dot:
            dotw = stringWidth(dot, style.fontName, style.fontSize)
            dotsn = int((availWidth-x-pagestrw)/dotw)
        else:
            dotsn = dotw = 0
        text = '%s%s' % (dotsn * dot, pagestr)
        newx = availWidth-dotsn*dotw-pagestrw
    elif dot is None:
        text = ',  ' + pagestr
        newx = x
    else:
        raise TypeError('Argument dot should either be None or an instance of basestring.')

    tx = canvas.beginText(newx, y)
    tx.setFont(style.fontName, style.fontSize)
    tx.setFillColor(style.textColor)
    tx.textLine(text)
    canvas.drawText(tx)

# Default paragraph styles for tables of contents.
# (This could also be generated automatically or even
# on-demand if it is not known how many levels the
# TOC will finally need to display...)

delta = 1*cm
epsilon = 0.5*cm

defaultLevelStyles = []
for x, n in enumerate(('Zero', 'One', 'Two', 'Three', 'Four')):
    s = ParagraphStyle(name='Level' + n,
                   fontName='Times-Roman',
                   fontSize=10,
                   leading=11,
                   firstLineIndent = x*delta,
                   leftIndent = x*delta + epsilon)
    defaultLevelStyles.append(s)

defaultTableStyle = \
    TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
    ])

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
        self.levelStyles = defaultLevelStyles
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
            style = self.levelStyles[level]
            dot = ' . ' if self.dotsMinLevel >= 0 and level >= self.dotsMinLevel else ''
            drawPageNumbers(canvas, style, str(page), availWidth, availHeight, dot)
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

        self._table = Table(tableData, colWidths=(availWidth,), style=self.tableStyle)

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
        
def makeTuple(x):
    if hasattr(x, '__iter__'):
        return tuple(x)
    return (x,)

class SimpleIndex(IndexingFlowable):
    """This creates a very simple index.

    Entries have a string key, and appear with a page number on
    the right.  Prototype for more sophisticated multi-level index."""
    def __init__(self, style=None, dot=None, tableStyle=None):
        #keep stuff in a dictionary while building
        self._entries = {}
        self._lastEntries = {}
        self._flowable = None
        if style is None:
            style = ParagraphStyle(name='index',
                                        fontName='Times-Roman',
                                        fontSize=11)
        self.textStyle = style
        self.tableStyle = tableStyle or defaultTableStyle
        self.dot = dot

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
        self._entries.setdefault(makeTuple(text),set([])).add(pageNum)

    def split(self, availWidth, availHeight):
        """At this stage we do not care about splitting the entries,
        we will just return a list of platypus tables.  Presumably the
        calling app has a pointer to the original TableOfContents object;
        Platypus just sees tables.
        """
        return self._flowable.splitOn(self.canv,availWidth, availHeight)

    def _getlastEntries(self, dummy=[(['Placeholder for index'],[0,1,2])]):
        '''Return the last run's entries!  If there are none, returns dummy.'''
        if not self._lastEntries:
            if self._entries:
                return self._entries.items()
            return dummy
        return self._lastEntries.items()
    
    def _build(self,availWidth,availHeight):
        _tempEntries = self._getlastEntries()
        _tempEntries.sort(cmp=lambda a,b: cmp([ x.upper() for x in a[0]], [ x.upper() for x in b[0]]))

        def drawIndexEntryEnd(canvas, kind, label):
            '''Callback to draw dots and page numbers after each entry.'''
            style = self.getLevelStyle(0)
            drawPageNumbers(canvas, style, label, availWidth, availHeight, self.dot)
        self.canv.drawIndexEntryEnd = drawIndexEntryEnd

        tableData = []
        lastTexts = []
        for texts, pageNumbers in _tempEntries:
            texts = list(texts)
            i, diff = listdiff(lastTexts, texts)
            if diff:
                lastTexts = texts
                texts = texts[i:]
            texts[-1] = '%s<onDraw name="drawIndexEntryEnd" label="%s"/>' % (texts[-1], ', '.join(map(str, pageNumbers)))
            for text in texts:
                style = self.getLevelStyle(i)
                para = Paragraph(text, style)
                if style.spaceBefore:
                    tableData.append([Spacer(1, style.spaceBefore),])
                tableData.append([para,])
                i += 1
        self._flowable = Table(tableData, colWidths=[availWidth], style=self.tableStyle)

    def wrap(self, availWidth, availHeight):
        "All table properties should be known by now."
        self._build(availWidth,availHeight)
        self.width, self.height = self._flowable.wrapOn(self.canv,availWidth, availHeight)
        return self.width, self.height

    def drawOn(self, canvas, x, y, _sW=0):
        """Don't do this at home!  The standard calls for implementing
        draw(); we are hooking this in order to delegate ALL the drawing
        work to the embedded table object.
        """
        self._flowable.drawOn(canvas, x, y, _sW)

    def draw(self):
        t = self._flowable
        ocanv = getattr(t,'canv',None)
        if not ocanv:
            t.canv = self.canv
        try:
            t.draw()
        finally:
            if not ocanv:
                del t.canv

    def getLevelStyle(self, n):
        '''Returns the style for level n, generating and caching styles on demand if not present.'''
        if not hasattr(self.textStyle, '__iter__'):
            self.textStyle = [self.textStyle]
        try:
            return self.textStyle[n]
        except IndexError:
            self.textStyle = list(self.textStyle)
            prevstyle = self.getLevelStyle(n-1)
            self.textStyle.append(ParagraphStyle(
                    name='%s-%d-indented' % (prevstyle.name, n),
                    parent=prevstyle,
                    firstLineIndent = prevstyle.firstLineIndent+n*.1*cm,
                    leftIndent = prevstyle.leftIndent+n*.1*cm))
            return self.textStyle[n]

class AlphabeticIndex(SimpleIndex):
    
    def _build(self,availWidth,availHeight):
        _tempEntries = self._getlastEntries()
        _tempEntries.sort(cmp=lambda a,b: cmp([x.upper() for x in a[0]], [x.upper() for x in b[0]]))

        def drawIndexEntryEnd(canvas, kind, label):
            '''Callback to draw dots and page numbers after each entry.'''
            style = self.getLevelStyle(1)
            drawPageNumbers(canvas, style, label, availWidth, availHeight, self.dot)
        self.canv.drawIndexEntryEnd = drawIndexEntryEnd

        alpha = ''
        tableData = []
        lastTexts = []
        for texts, pageNumbers in _tempEntries:
            texts = list(texts)
            # Alpha
            alphaStyle = self.getLevelStyle(0)
            nalpha = texts[0][0].upper()
            if alpha != nalpha:
                alpha = nalpha
                tableData.append([Spacer(1, alphaStyle.spaceBefore),])
                tableData.append([Paragraph(alpha, alphaStyle),])
                tableData.append([Spacer(1, alphaStyle.spaceAfter),])

            i, diff = listdiff(lastTexts, texts)
            if diff:
                lastTexts = texts
                texts = texts[i:]
            texts[-1] = '%s<onDraw name="drawIndexEntryEnd" label="%s"/>' % (texts[-1], ', '.join(map(str, pageNumbers)))
            for text in texts:
                style = self.getLevelStyle(i+1)
                para = Paragraph(text, style)
                if style.spaceBefore:
                    tableData.append([Spacer(1, style.spaceBefore),])
                tableData.append([para,])
                i += 1

        self._flowable = Table(tableData, colWidths=[availWidth], style=self.tableStyle)

def listdiff(l1, l2):
    m = min(len(l1), len(l2))
    for i in range(m):
        if l1[i] != l2[i]:
            return i, l2[i:]
    return m, l2[m:]

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


