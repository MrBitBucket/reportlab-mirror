"""
This module defines a single TableOfContents0() class that can be used to
create automatically a table of tontents for Platypus documents like
this:

    story = []
    toc = TableOfContents0()
    story.append(toc)
    # some heading paragraphs here...
    doc = MyTemplate(path)
    doc.multiBuild0(story)

The data needed to create the table is a list of (level, text, pageNum)
triplets, plus some paragraph styles for each level of the table itself.
The triplets will usually be created in a document template's method
like afterFlowable(), making notification calls using the notify0()
method with appropriate data like this:

    (level, text, pageNum) = ...
    self.notify0('TOCEntry', (level, text, pageNum))

As the table of contents need at least two passes over the Platypus
story which is why the moultiBuild0() method must be called.

The level<NUMBER>ParaStyle variables are the paragraph styles used
to render the entries in the table of contents.
"""


from reportlab.lib import enums
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.doctemplate import IndexingFlowable0
from reportlab.platypus.tables import TableStyle, Table


# Default paragraph styles for tables of contents.

levelZeroParaStyle = \
    ParagraphStyle(name='LevelZero',
                   fontName='Times-Roman',
                   fontSize=10,
                   leading=11)

levelOneParaStyle = \
    ParagraphStyle(name='LevelOne',
                   parent = levelZeroParaStyle,
                   leading=11,
                   firstLineIndent = 12,
                   leftIndent = 12)

levelTwoParaStyle = \
    ParagraphStyle(name='LevelTwo',
                   parent = levelOneParaStyle,
                   leading=11,
                   firstLineIndent = 24,
                   leftIndent = 24)

levelThreeParaStyle = \
    ParagraphStyle(name='LevelThree',
                   parent = levelTwoParaStyle,
                   leading=11,
                   firstLineIndent = 36,
                   leftIndent = 36)

levelFourParaStyle = \
    ParagraphStyle(name='LevelFour',
                   parent = levelTwoParaStyle,
                   leading=11,
                   firstLineIndent = 48,
                   leftIndent = 48)

defaultTableStyle = \
    TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')])


class TableOfContents0(IndexingFlowable0):
    """This creates a formatted table of contents.

    It presumes a correct block of data is passed in.
    The data block contains a list of (level, text, pageNumber)
    triplets.  You can supply a paragraph style for each level
    (starting at zero).
    """

    def __init__(self):
        self.entries = []
        self.rightColumnWidth = 72
        self.levelStyles = [levelZeroParaStyle,
                            levelOneParaStyle,
                            levelTwoParaStyle,
                            levelThreeParaStyle,
                            levelFourParaStyle]
        self.tableStyle = defaultTableStyle
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


    # Shouldn't that be notify0??
    def notify(self, kind, stuff):
        """The notification hook called to register all kinds of events.

        Here we are interested in 'TOCEntry' events only.
        """
        if kind == 'TOCEntry':
            (level, text, pageNum) = stuff
            self.addEntry(level, text, pageNum)


    def clearEntries(self):
        self._entries = []


    def addEntry(self, level, text, pageNum):
        """Adds one entry to the table of contents.

        This allows incremental buildup by a doctemplate.
        Requires that enough styles are defined."""

        assert type(level) == type(1), "Level must be an integer"
        assert level < len(self.levelStyles), \
               "Table of contents must have a style defined " \
               "for paragraph level %d before you add an entry" % level

        self._entries.append((level, text, pageNum))


    def addEntries(self, listOfEntries):
        """Bulk creation of entries in the table of contents.

        If you knew the titles but not the page numbers, you could
        supply them to get sensible output on the first run."""
        
        for (level, text, pageNum) in listOfEntries:
            self.addEntry(level, text, pageNum)


    def wrap(self, availWidth, availHeight):
        "All table properties should be known by now."

        widths = (availWidth - self.rightColumnWidth,
                  self.rightColumnWidth)

        # makes an internal table which does all the work.
        # we draw the LAST RUN's entries!  If there are
        # none, we make some dummy data to keep the table
        # from complaining
        if len(self._lastEntries) == 0:
            _tempEntries = [(0,'Placeholder for table of contents',0)]
        else:
            _tempEntries = self._lastEntries

        tableData = []
        for (level, text, pageNum) in _tempEntries:
            leftColStyle = self.levelStyles[level]
            #right col style is right aligned
            rightColStyle = ParagraphStyle(name='leftColLevel%d' % level,
                                           parent=leftColStyle,
                                           leftIndent=0,
                                           alignment=enums.TA_RIGHT)
            leftPara = Paragraph(text, leftColStyle)
            rightPara = Paragraph(str(pageNum), rightColStyle)
            tableData.append([leftPara, rightPara])

        self._table = Table(tableData, colWidths=widths,
                            style=self.tableStyle)

        self.width, self.height = self._table.wrap(availWidth, availHeight)
        return (self.width, self.height)


    def split(self, availWidth, availHeight):
        """At this stage we do not care about splitting the entries,
        we will just return a list of platypus tables.  Presumably the
        calling app has a pointer to the original TableOfContents object;
        Platypus just sees tables.
        """
        return self._table.split(availWidth, availHeight)


    def drawOn(self, canvas, x, y, _sW=0):
        """Don't do this at home!  The standard calls for implementing
        draw(); we are hooking this in order to delegate ALL the drawing
        work to the embedded table object.
        """
        self._table.drawOn(canvas, x, y, _sW)
