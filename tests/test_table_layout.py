from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import operator, string
from reportlab.platypus import *
#from reportlab import rl_config
from reportlab.lib.styles import PropertySet, getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus.paragraph import Paragraph
#from reportlab.lib.utils import fp_str
#from reportlab.pdfbase import pdfmetrics
from reportlab.platypus.flowables import PageBreak
import os
import unittest

class TableTestCase(unittest.TestCase):


    def getDataBlock(self):
        "Helper - data for our spanned table"
        return [
            # two rows are for headers
            ['Region','Product','Period',None,None,None,'Total'],
            [None,None,'Q1','Q2','Q3','Q4',None],

            # now for data
            ['North','Spam',100,110,120,130,460],
            ['North','Eggs',101,111,121,131,464],
            ['North','Guinness',102,112,122,132,468],

            ['South','Spam',100,110,120,130,460],
            ['South','Eggs',101,111,121,131,464],
            ['South','Guinness',102,112,122,132,468],
            ]

    def test_document(self):

        rowheights = (24, 16, 16, 16, 16)
        rowheights2 = (24, 16, 16, 16, 30)
        colwidths = (50, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32)
        GRID_STYLE = TableStyle(
            [('GRID', (0,0), (-1,-1), 0.25, colors.black),
             ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
            )

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 6
        styNormal.spaceAfter = 6

        data = (
            ('', 'Jan', 'Feb', 'Mar','Apr','May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'),
            ('Mugs', 0, 4, 17, 3, 21, 47, 12, 33, 2, -2, 44, 89),
            ('T-Shirts', 0, 42, 9, -3, 16, 4, 72, 89, 3, 19, 32, 119),
            ('Miscellaneous accessories', 0,0,0,0,0,0,1,0,0,0,2,13),
            ('Hats', 893, 912, '1,212', 643, 789, 159, 888, '1,298', 832, 453, '1,344','2,843')
            )
        data2 = (
            ('', 'Jan', 'Feb', 'Mar','Apr','May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'),
            ('Mugs', 0, 4, 17, 3, 21, 47, 12, 33, 2, -2, 44, 89),
            ('T-Shirts', 0, 42, 9, -3, 16, 4, 72, 89, 3, 19, 32, 119),
            ('Key Ring', 0,0,0,0,0,0,1,0,0,0,2,13),
            ('Hats\nLarge', 893, 912, '1,212', 643, 789, 159, 888, '1,298', 832, 453, '1,344','2,843')
            )


        data3 = (
            ('', 'Jan', 'Feb', 'Mar','Apr','May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'),
            ('Mugs', 0, 4, 17, 3, 21, 47, 12, 33, 2, -2, 44, 89),
            ('T-Shirts', 0, 42, 9, -3, 16, 4, 72, 89, 3, 19, 32, 119),
            ('Key Ring', 0,0,0,0,0,0,1,0,0,0,2,13),
            (Paragraph("Let's <b>really mess things up with a <i>paragraph</i></b>",styNormal),
                   893, 912, '1,212', 643, 789, 159, 888, '1,298', 832, 453, '1,344','2,843')
            )

        lst = []


        lst.append(Paragraph("""Basics about column sizing and cell contents""", styleSheet['Heading1']))

        t1 = Table(data, colwidths, rowheights)
        t1.setStyle(GRID_STYLE)
        lst.append(Paragraph("This is GRID_STYLE with explicit column widths.  Each cell contains a string or number\n", styleSheet['BodyText']))
        lst.append(t1)
        lst.append(Spacer(18,18))

        t2 = Table(data, None, None)
        t2.setStyle(GRID_STYLE)
        lst.append(Paragraph("""This is GRID_STYLE with no size info. It
                                does the sizes itself, measuring each text string
                                and computing the space it needs.  If the text is
                                too wide for the frame, the table will overflow
                                as seen here.""",
                             styNormal))
        lst.append(t2)
        lst.append(Spacer(18,18))

        t3 = Table(data2, None, None)
        t3.setStyle(GRID_STYLE)
        lst.append(Paragraph("""This demonstrates the effect of adding text strings with
        newlines to a cell. It breaks where you specify, and if rowHeights is None (i.e
        automatic) then you'll see the effect. See bottom left cell.""",
                             styNormal))
        lst.append(t3)
        lst.append(Spacer(18,18))


        colWidths = (None, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32)
        t3 = Table(data3, colWidths, None)
        t3.setStyle(GRID_STYLE)
        lst.append(Paragraph("""This table does not specify the size of the first column,
                                so should work out a sane one.  In this case the element
                                at bottom left is a paragraph, which has no intrinsic size
                                (the height and width are a function of each other).  So,
                                it tots up the extra space in the frame and divides it
                                between any such unsizeable columns.  As a result the
                                table fills the width of the frame (except for the
                                6 point padding on either size).""",
                             styNormal))
        lst.append(t3)
        lst.append(PageBreak())

        lst.append(Paragraph("""Row and Column spanning""", styleSheet['Heading1']))

        lst.append(Paragraph("""This shows a very basic table.  We do a faint pink grid
        to show what's behind it - imagine this is not printed, as we'll overlay it later
        with some black lines.  We're going to "span" some cells, and have put a
        value of None in the data to signify the cells we don't care about.
        (In real life if you want an empty cell, put '' in it rather than None). """, styNormal))

        sty = TableStyle([
            #very faint grid to show what's where
            ('GRID', (0,0), (-1,-1), 0.25, colors.pink),
            ])

        t = Table(self.getDataBlock(), colWidths=None, rowHeights=None, style=sty)
        lst.append(t)



        lst.append(Paragraph("""We now center the text for the "period"
        across the four cells for each quarter.  To do this we add a 'span'
        command to the style to make the cell at row 1 column 3 cover 4 cells,
        and a 'center' command for all cells in the top row. The spanning
        is not immediately evident but trust us, it's happening - the word
        'Period' is centered across the 4 columns.""", styNormal))
        sty = TableStyle([
            #
            ('GRID', (0,0), (-1,-1), 0.25, colors.pink),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('SPAN', (2,0), (5,0)),
            ])

        t = Table(self.getDataBlock(), colWidths=None, rowHeights=None, style=sty)
        lst.append(t)

        lst.append(Paragraph("""We repeat this for the words 'Region', Product'
        and 'Total', which each span the top 2 rows; and for 'North' and 'South'
        which span 3 rows.  At the moment each cell's alignment is the default
        (bottom), so these words appear to have "dropped down"; in fact they
        are sitting on the bottom of their allocated ranges.  You will just see that
        all the 'None' values vanished, as those cells are not drawn any more.""", styNormal))
        sty = TableStyle([
            #
            ('GRID', (0,0), (-1,-1), 0.25, colors.pink),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('SPAN', (2,0), (5,0)),
            #span the other column heads down 2 rows
            ('SPAN', (0,0), (0,1)),
            ('SPAN', (1,0), (1,1)),
            ('SPAN', (6,0), (6,1)),
            #span the 'north' and 'south' down 3 rows each
            ('SPAN', (0,2), (0,4)),
            ('SPAN', (0,5), (0,7)),
            ])

        t = Table(self.getDataBlock(), colWidths=None, rowHeights=None, style=sty)
        lst.append(t)


        lst.append(PageBreak())


        lst.append(Paragraph("""Now we'll tart things up a bit.  First,
        we set the vertical alignment of each spanned cell to 'middle'.
        Next we add in some line drawing commands which do not slash across
        the spanned cells (for demonstration only, as lines do not show through
        spanned cells).  Finally we'll add some thicker lines to divide it up.
        We leave the pink as proof that spanned rows hide underlying lines.  Voila!
        """, styNormal))
        sty = TableStyle([
            #
            ('GRID', (0,0), (-1,-1), 0.25, colors.pink),
            ('TOPPADDING', (0,0), (-1,-1), 3),

            #span the 'period'
            ('SPAN', (2,0), (5,0)),
            #span the other column heads down 2 rows
            ('SPAN', (0,0), (0,1)),
            ('SPAN', (1,0), (1,1)),
            ('SPAN', (6,0), (6,1)),
            #span the 'north' and 'south' down 3 rows each
            ('SPAN', (0,2), (0,4)),
            ('SPAN', (0,5), (0,7)),

            #top row headings are centred
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            #everything we span is vertically centred
            #span the other column heads down 2 rows
            ('VALIGN', (0,0), (0,1), 'MIDDLE'),
            ('VALIGN', (1,0), (1,1), 'MIDDLE'),
            ('VALIGN', (6,0), (6,1), 'MIDDLE'),
            #span the 'north' and 'south' down 3 rows each
            ('VALIGN', (0,2), (0,4), 'MIDDLE'),
            ('VALIGN', (0,5), (0,7), 'MIDDLE'),

            #numeric stuff right aligned
            ('ALIGN', (2,1), (-1,-1), 'RIGHT'),

            #draw lines carefully so as not to swipe through
            #any of the 'spanned' cells
           ('GRID', (1,2), (-1,-1), 1.0, colors.black),
            ('BOX', (0,2), (0,4), 1.0, colors.black),
            ('BOX', (0,5), (0,7), 1.0, colors.black),
            ('BOX', (0,0), (0,1), 1.0, colors.black),
            ('BOX', (1,0), (1,1), 1.0, colors.black),

            ('BOX', (2,0), (5,0), 1.0, colors.black),
            ('GRID', (2,1), (5,1), 1.0, colors.black),

            ('BOX', (6,0), (6,1), 1.0, colors.black),

            # do fatter boxes around some cells
            ('BOX', (0,0), (-1,1), 2.0, colors.black),
            ('BOX', (0,2), (-1,4), 2.0, colors.black),
            ('BOX', (0,5), (-1,7), 2.0, colors.black),
            ('BOX', (-1,0), (-1,-1), 2.0, colors.black),

            ])

        t = Table(self.getDataBlock(), colWidths=None, rowHeights=None, style=sty)
        lst.append(t)

        lst.append(Paragraph("""How cells get sized""", styleSheet['Heading1']))

        lst.append(Paragraph("""So far the table has been auto-sized.  This can be
        computationally expensive, and can lead to yucky effects. Imagine a lot of
        numbers, one of which goes to 4 figures - tha numeric column will be wider.
        The best approach is to specify the column
        widths where you know them, and let the system do the heights.  Here we set some
        widths - an inch for the text columns and half an inch for the numeric ones.
        """, styNormal))

        t = Table(self.getDataBlock(),
                    colWidths=(72,72,36,36,36,36,56),
                    rowHeights=None,
                    style=sty)
        lst.append(t)

        lst.append(Paragraph("""The auto-sized example 2 steps back demonstrates
        one advanced feature of the sizing algorithm. In the table below,
        the columns for Q1-Q4 should all be the same width.  We've made
        the text above it a bit longer than "Period".  Note that this text
        is technically in the 3rd column; on our first implementation this
        was sized and column 3 was therefore quite wide.  To get it right,
        we ensure that any cells which span columns, or which are 'overwritten'
        by cells which span columns, are assigned zero width in the cell
        sizing.  Thus, only the string 'Q1' and the numbers below it are
        calculated in estimating the width of column 3, and the phrase
        "What time of year?" is not used.  However, row-spanned cells are
        taken into account. ALL the cells in the leftmost column
        have a vertical span (or are occluded by others which do)
        but it can still work out a sane width for them.

        """, styNormal))

        data = self.getDataBlock()
        data[0][2] = "Which time of year?"
        #data[7][0] = Paragraph("Let's <b>really mess things up with a <i>paragraph</i>",styNormal)
        t = Table(data,
                    #colWidths=(72,72,36,36,36,36,56),
                    rowHeights=None,
                    style=sty)
        lst.append(t)

        lst.append(Paragraph("""Paragraphs and unsizeable objects in table cells.""", styleSheet['Heading1']))

        lst.append(Paragraph("""Paragraphs and other flowable objects make table
        sizing much harder. In general the height of a paragraph is a function
        of its width so you can't ask it how wide it wants to be - and the
        REALLY wide all-on-one-line solution is rarely what is wanted. We
        refer to Paragraphs and their kin as "unsizeable objects". In this example
        we have set the widths of all but the first column.  As you can see
        it uses all the available space across the page for the first column.
        Note also that this fairly large cell does NOT contribute to the
        height calculation for its 'row'.  Under the hood it is in the
        same row as the second Spam, but this row gets a height based on
        its own contents and not the cell with the paragraph.

        """, styNormal))


        def messedUpTable():
            data = self.getDataBlock()
            data[5][0] = Paragraph("Let's <b>really mess things up</b> with a <i>paragraph</i>, whose height is a function of the width you give it.",styNormal)
            t = Table(data,
                        colWidths=(None,72,36,36,36,36,56),
                        rowHeights=None,
                        style=sty)
            return t
        lst.append(messedUpTable())


        lst.append(Paragraph("""This one demonstrates that our current algorithm
        does not cover all cases :-(  The height of row 0 is being driven by
        the width of the para, which thinks it should fit in 1 column and not 4.
        To really get this right would involve multiple passes through all the cells
        applying rules until everything which can be sized is sized (possibly
        backtracking), applying increasingly dumb and brutal
        rules on each pass.
        """, styNormal))
        data = self.getDataBlock()
        data[0][2] = Paragraph("Let's <b>really mess things up</b> with a <i>paragraph</i>.",styNormal)
        data[5][0] = Paragraph("Let's <b>really mess things up</b> with a <i>paragraph</i>, whose height is a function of the width you give it.",styNormal)
        t = Table(data,
                    colWidths=(None,72,36,36,36,36,56),
                    rowHeights=None,
                    style=sty)
        lst.append(t)

        lst.append(Paragraph("""To avoid these problems remember the golden rule
        of ReportLab tables:  (1) fix the widths if you can, (2) don't use
        a paragraph when a string will do.
        """, styNormal))

        lst.append(Paragraph("""Unsized columns that contain flowables without
        precise widths, such as paragraphs and nested tables,
        still need to try and keep their content within borders and ideally
        even honor percentage requests.  This can be tricky--and expensive.
        But sometimes you can't follow the golden rules.
        """, styNormal))

        lst.append(Paragraph("""The code first calculates the minimum width
        for each unsized column by iterating over every flowable in each column
        and remembering the largest minimum width.  It then allocates
        available space to accomodate the minimum widths.  Any remaining space
        is divided up, treating a width of '*' as greedy, a width of None as
        non-greedy, and a percentage as a weight.  If a column is already
        wider than its percentage warrants, it is not further expanded, and
        the other widths accomodate it.
        """, styNormal))

        lst.append(Paragraph("""For instance, consider this tortured table.
        It contains four columns, with widths of None, None, 60%, and 20%,
        respectively, and a single row.  The first cell contains a paragraph.
        The second cell contains a table with fixed column widths that total
        about 50% of the total available table width.  The third cell contains
        a string.  The last cell contains a table with no set widths but a
        single cell containing a paragraph.
        """, styNormal))
        ministy = TableStyle([
            ('GRID', (0,0), (-1,-1), 1.0, colors.black),
            ])
        nested1 = [Paragraph(
            'This is a paragraph.  The column has a width of None.',
            styNormal)]
        nested2 = [Table(
            [[Paragraph(
                'This table is set to take up two and a half inches.  The '
                'column that holds it has a width of None.', styNormal)]],
            colWidths=(180,),
            rowHeights=None,
            style=ministy)]
        nested3 = '60% width'
        nested4 = [Table(
            [[[Paragraph(
                "This is a table with a paragraph in it but no width set.  "
                "The column width in the containing table is 20%.",
                styNormal)]]],
            colWidths=(None,),
            rowHeights=None,
            style=ministy)]
        t = Table([[nested1, nested2, nested3, nested4]],
                  colWidths=(None, None, '60%', '20%'),
                  rowHeights=None,
                  style=ministy)
        lst.append(t)

        lst.append(Paragraph("""Notice that the second column does expand to
        account for the minimum size of its contents; and that the remaining
        space goes to the third column, in an attempt to honor the '60%'
        request as much as possible.  This is reminiscent of the typical HTML
        browser approach to tables.""", styNormal))

        lst.append(Paragraph("""To get an idea of how potentially expensive
        this is, consider the case of the last column: the table gets the
        minimum width of every flowable of every cell in the column.  In this
        case one of the flowables is a table with a column without a set
        width, so the nested table must itself iterate over its flowables.
        The contained paragraph then calculates the width of every word in it
        to see what the biggest word is, given the set font face and size.  It
        is easy to imagine creating a structure of this sort that took an
        unacceptably large amount of time to calculate.  Remember the golden
        rule, if you can. """, styNormal))

        lst.append(Paragraph("""This code does not yet handle spans well.""",
        styNormal))

        lst.append(PageBreak())

        lst.append(Paragraph("""Oversized cells""", styleSheet['Heading1']))

        lst.append(Paragraph("""In some cases cells with flowables can end up
        being larger than a page. In that case, we need to split the page.
        The splitInRow attribute allows that, it's by default 0.""",
        styNormal))

        lst.append(Paragraph("""Here is a table, with splitByRow=1 and
        splitInRow=0. It splits between the two rows.""",
        styNormal))

        ministy = TableStyle([
            ('GRID', (0,0), (-1,-1), 1.0, colors.black),
            ('VALIGN', (0,1), (1,1), 'BOTTOM'),
            ('VALIGN', (1,1), (2,1), 'MIDDLE'),
            ('VALIGN', (2,1), (3,1), 'TOP'),
            ('VALIGN', (3,1), (4,1), 'BOTTOM'),
            ('VALIGN', (4,1), (5,1), 'MIDDLE'),
            ('VALIGN', (5,1), (6,1), 'TOP'),
            ])
        cell1 = [Paragraph(
            """This is a very tall cell to make a tall row for splitting.""",
            styNormal)]
        cell2 = [Paragraph("This cell has two flowables.", styNormal),
            Paragraph("And valign=MIDDLE.", styNormal)]
        cell3 = [Paragraph("Paragraph with valign=TOP", styNormal)]

        tableData = [
            ['Row 1', 'Two rows:\nSo there', 'is a', 'place', 'to split', 'the table'],
            [cell1, cell2, cell3, 'valign=BOTTOM', 'valign=MIDDLE', 'valign=TOP']
        ]

        # This is the table with splitByRow, which splits between row 1 & 2:
        t = Table(tableData,
                  colWidths=(50, 70, 70, 90, 90, 70),
                  rowHeights=None,
                  style=ministy,
                  splitByRow=1,
                  splitInRow=0)
        parts = t.split(451, 55)
        lst.append(parts[0])
        lst.append(Paragraph("", styNormal))
        lst.append(parts[1])

        lst.append(Paragraph("""Here is the same table, with splitByRow=0 and
        splitInRow=1. It splits inside a row.""",
        styNormal))

        # This is the table with splitInRow, which splits in row 2:
        t = Table(tableData,
                  colWidths=(50, 70, 70, 90, 90, 70),
                  rowHeights=None,
                  style=ministy,
                  splitByRow=0,
                  splitInRow=1)

        parts = t.split(451, 57)
        lst.append(parts[0])
        lst.append(Paragraph("", styNormal))
        lst.append(parts[1])

        lst.append(Paragraph("""Here is the same table, with splitByRow=1 and
        splitInRow=1. It splits between the rows, if possible.""",
        styNormal))

        # This is the table with both splits, which splits in row 2:
        t = Table(tableData,
                  colWidths=(50, 70, 70, 90, 90, 70),
                  rowHeights=None,
                  style=ministy,
                  splitByRow=1,
                  splitInRow=1)

        parts = t.split(451, 57)
        lst.append(parts[0])
        #lst.append(Paragraph("", styNormal))
        lst.append(parts[1])

        lst.append(Paragraph("""But if we constrict the space to less than the first row,
        it splits that row.""",
        styNormal))

        # This is the table with both splits and no space, which splits in row 1:
        t = Table(tableData,
                  colWidths=(50, 70, 70, 90, 90, 70),
                  rowHeights=None,
                  style=ministy,
                  splitByRow=1,
                  splitInRow=1)

        parts = t.split(451, 15)
        lst.append(parts[0])
        lst.append(Paragraph("", styNormal))
        lst.append(parts[1])

        # Split it at a point in row 2, where the split fails
        lst.append(Paragraph("""When splitByRow is 0 and splitInRow is 1, we should
        still allow fallback to splitting between rows""",
        styNormal))

        t = Table(tableData,
                  colWidths=(50, 70, 70, 90, 90, 70),
                  rowHeights=None,
                  style=ministy,
                  splitByRow=0,
                  splitInRow=1)
        parts = t.split(451, 55)
        lst.append(parts[0])
        lst.append(Paragraph("", styNormal))
        lst.append(parts[1])

        lst.append(PageBreak())
        lst.append(Paragraph("""Similar table, with splitByRow=1 and splitInRow=0. String version.""",styNormal))
        cell1 = "This is a\nvery tall\ncell to\nmake a\ntall row\nfor split-\nting."
        cell2 = "This cell has\ntwo\nstrings.\n\nAnd valign=\nMIDDLE."
        cell3 = "String\nwith\nvalign=TOP"

        tableData = [
            ['Row 1', 'Two rows:\nSo there', 'is a', 'place', 'to split', 'the table'],
            [cell1, cell2, cell3, 'valign=BOTTOM', 'valign=MIDDLE', 'valign=TOP']
        ]

        # This is the table with splitByRow, which splits between row 1 & 2:
        t = Table(tableData,
                  colWidths=(50, 70, 70, 90, 90, 70),
                  rowHeights=None,
                  style=ministy,
                  splitByRow=1,
                  splitInRow=0)
        parts = t.split(451, 55)
        lst.append(parts[0])
        lst.append(Paragraph("", styNormal))
        lst.append(parts[1])

        lst.append(Paragraph("""Here is the same table, with splitByRow=0 and
        splitInRow=1. It splits inside a row.""",
        styNormal))

        # This is the table with splitInRow, which splits in row 2:
        t = Table(tableData,
                  colWidths=(50, 70, 70, 90, 90, 70),
                  rowHeights=None,
                  style=ministy,
                  splitByRow=0,
                  splitInRow=1)

        parts = t.split(451, 57)
        lst.append(parts[0])
        lst.append(Paragraph("", styNormal))
        lst.append(parts[1])

        lst.append(Paragraph("""Here is the same table, with splitByRow=1 and
        splitInRow=1. It splits between the rows, if possible.""",
        styNormal))

        # This is the table with both splits, which splits in row 2:
        t = Table(tableData,
                  colWidths=(50, 70, 70, 90, 90, 70),
                  rowHeights=None,
                  style=ministy,
                  splitByRow=1,
                  splitInRow=1)

        parts = t.split(451, 57)
        lst.append(parts[0])
        #lst.append(Paragraph("", styNormal))
        lst.append(parts[1])

        lst.append(Paragraph("""But if we constrict the space to less than the first row,
        it splits that row.""",
        styNormal))

        # This is the table with both splits and no space, which splits in row 1:
        t = Table(tableData,
                  colWidths=(50, 70, 70, 90, 90, 70),
                  rowHeights=None,
                  style=ministy,
                  splitByRow=1,
                  splitInRow=1)

        parts = t.split(451, 15)
        lst.append(parts[0])
        lst.append(Paragraph("", styNormal))
        lst.append(parts[1])

        # Split it at a point in row 2, where the split fails
        lst.append(Paragraph("""When splitByRow is 0 and splitInRow is 1, we should
        still allow fallback to splitting between rows""",
        styNormal))

        t = Table(tableData,
                  colWidths=(50, 70, 70, 90, 90, 70),
                  rowHeights=None,
                  style=ministy,
                  splitByRow=0,
                  splitInRow=1)
        parts = t.split(451, 55)
        lst.append(parts[0])
        lst.append(Paragraph("", styNormal))
        lst.append(parts[1])

        def lennartExample(splitByRow=0,splitInRow=1,split=0):
            #special case examples of inRowSplit
            class IndicatorTable(Table):
                def draw(self):
                    Table.draw(self)
                    c = self.canv
                    x = self._width
                    y = self._height - split
                    c.setStrokeColor(colors.toColor('red'))
                    c.setLineWidth(0.5)
                    c.setDash([2,2])
                    c.line(0,y,x+13,y)

            storyAdd = lst.append
            storyAdd(PageBreak())
            styleSheet = getSampleStyleSheet()
            btStyle = styleSheet['BodyText']
            def makeTable(klass=Table):
                xkwd = {}
                data = [
                    ['R0C0\nR1C0\nR2C0', 'R0C1', 'R0C2', 'R0C3', 'R0C4\nR1C4', 'R0C5'],
                    ['', 'R1C1', 'R1C2', 'R1C3', '', 'R1C5\nR2C5\nR3C5'],
                    ['', 'R2C1', 'R2C2', 'R2C3', 'R2C4', ''],
                    ['R3C0', 'R3C1', 'R3C2', 'R3C3 R3C4\nR4C3 R4C4', '', ''],
                    ['R4C0', 'R4C1', 'R4C2', '', '', 'R4C5'],
                ]

                sty = [
                        ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                        ('GRID',(1,1),(-2,-2),1,colors.green),
                        ('BOX',(0,0),(-1,-1),3,colors.black),
                        ('BOX',(0,0),(1,-1),2,colors.red),
                        ('LINEABOVE',(1,2),(-2,2),1,colors.blue),
                        ('LINEBEFORE',(2,1),(2,-2),1,colors.pink),
                        ('BACKGROUND', (0, 0), (0, 0), colors.pink),
                        ('BACKGROUND', (1, 1), (1, 2), colors.lavender),
                        ('BACKGROUND', (2, 3), (2, 4), colors.orange),
                        ('BACKGROUND',(5,1),(5,3),colors.greenyellow),
                        ('BACKGROUND',(5,4),(5,4),colors.darkviolet),
                        ('TEXTCOLOR',(0,0),(-1,0),colors.brown),
                        ('TEXTCOLOR',(1,1),(-2,-1),colors.green),
                        ('TEXTCOLOR',(5,1),(5,3),colors.magenta),
                        ('TEXTCOLOR',(5,4),(5,4),colors.white),
                        ('SPAN',(0,0), (0, 2)),
                        ('SPAN',(2,0), (2, 1)),
                        ('SPAN',(3,3), (4, 4)),
                        ('SPAN',(4,0), (4, 1)),
                        ('SPAN',(5,1), (5, 3)),
                        ]
                xkwd['colWidths'] = [40]*6
                return klass(data,
                            style=sty,
                            splitInRow=splitInRow,
                            splitByRow=splitByRow,
                            **xkwd,
                            )
            storyAdd(Paragraph("Illustrating splits: nosplit", btStyle))
            storyAdd(makeTable(klass=IndicatorTable))
            storyAdd(Spacer(0,6))
            def addSplitTable(size=30):
                t = makeTable()
                S = t.split(4*72,size)
                if not S:
                    storyAdd(Paragraph(f"<span color=red>Illustrating splits failed</span>: split(4in,{size}) splitByRow={splitByRow} splitInRow={splitInRow}", btStyle))
                    storyAdd(Spacer(0,6))
                    #print('!!!!! Failed')
                else:
                    #print('##### OK')
                    storyAdd(Paragraph(f"Illustrating splits: split(4in,{size}) splitByRow={splitByRow} splitInRow={splitInRow}", btStyle))
                    storyAdd(Spacer(0,6))
                    for s in S:
                        storyAdd(s)
                        storyAdd(Spacer(0,20))
            addSplitTable(split)

        for split in (30,40,50,60):
            lennartExample(split=split)

        plainlg = (
            ("ALIGN", (0,0), (-1,-1), "LEFT"),
            ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
            ("FONTSIZE", (0,0), (-1,-1), 10),
            ("VALIGN", (1,2), (1,3), "MIDDLE"),
            ("VALIGN", (2,2), (2,3), "TOP"),
            ("ALIGN", (1,1), (1,1), "CENTER"),
            ("ALIGN", (1,4), (1,4), "CENTER"),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('OUTLINE', (0,0), (-1,-1), 2, colors.black),
            ("BOTTOMPADDING", (0,0), (-1,-1), 0),
            ("TOPPADDING", (0,0), (-1,-1), 0),
            ("LEFTPADDING", (0,0), (-1,-1), 0),
            ("RIGHTPADDING", (0,0), (-1,-1), 0),
            ("BACKGROUND", (1,1), (1,1), ("HORIZONTAL", colors.green, colors.yellow)),
            ("BACKGROUND", (0,2), (1,2), ("VERTICAL", colors.red, '#008000')),
            ("BACKGROUND", (0,3), (1,3), ("VERTICAL2", colors.blue, colors.yellow)),
            ("BACKGROUND", (1,4), (1,4), ("HORIZONTAL2", colors.green, colors.yellow)),
            ("BACKGROUND", (2,2), (2,2), ("LINEARGRADIENT", (0,0),(1,1), True, (colors.green, colors.yellow, colors.red), (0.25,0.5,0.75))),
            ("BACKGROUND", (2,3), (2,3), ("LINEARGRADIENT", (0,1),(1,0), True, (colors.green, colors.yellow, colors.red), (0.25,0.5,0.75))),
            ("BACKGROUND", (1,5), (1,5), ("LINEARGRADIENT", (0,0),(1,0), True, (colors.pink, colors.lightgreen, colors.lightblue), (0.25,0.5,0.75))),
            ("BACKGROUND", (0,6), (1,6), ("LINEARGRADIENT", (0,0),(0,1), True, (colors.pink, colors.lightgreen, colors.lightblue), (0.25,0.5,0.75))),
            ("BACKGROUND", (2,6), (2,6), ("LINEARGRADIENT", (1,0.2),(0,0.8), True, (colors.red, colors.yellow, colors.green, colors.lightblue), (0.2,0.4,0.6,0.8))),
            ("BACKGROUND", (0,7), (0,7), ("RADIALGRADIENT", (0.5,0.5),(1,'width'), True, (colors.red, colors.yellow, colors.green, colors.lightblue), (0.2,0.4,0.6,0.8))),
            ("BACKGROUND", (1,7), (1,7), ("RADIALGRADIENT", (0.5,0.5),(1,'height'), True, (colors.red, colors.yellow, colors.green, colors.lightblue), (0.2,0.4,0.6,0.8))),
            ("BACKGROUND", (2,7), (2,7), ("RADIALGRADIENT", (0.6,0.4),(1,'max'), True, (colors.red, colors.yellow, colors.green, colors.lightblue), (0.2,0.4,0.6,0.8))),
            ("BACKGROUND", (0,8), (1,8), ("LINEARGRADIENT", (0,1),(0,0), True, (colors.blue, colors.yellow, colors.blue), (0.25,0.5,0.75))),
            ("BACKGROUND", (2,8), (2,8), ("LINEARGRADIENT", (0,1),(1,0), True, (colors.green, colors.yellow, colors.green), (0.25,0.5,0.75))),
            )
        datalg = [
            ["00","01","02"],
            ["10","11 this is a long string","12"],
            ["20\nthis is the\nend\nmy friend","21\nthe bells of hell\ngo ting-aling-aling",
                "22\ndespair all who\nenter here"],
            ["30\nthis is the\nend\nmy friend","31\nthe bells of hell\ngo ting-aling-aling",
                "32\ndespair all who\nenter here"],
            ["40","41 this is a long string","42"],
            ["50","51 this is a long string","52"],
            ["60\nthis is the\nend\nmy friend","61\nthe bells of hell\ngo ting-aling-aling",
                "62\ndespair all who\nenter here"],
            ["70\nthis is the\nend\nmy friend","71\nthe bells of hell\ngo ting-aling-aling",
                "72\ndespair all who\nenter here"],
            ["80\nthis is the\nend\nmy friend","81\nthe bells of hell\ngo ting-aling-aling",
                "82\ndespair all who\nenter here"],
            ]
        lst.append(PageBreak())
        lst.append(Paragraph("Table with gradient backgrounds", styleSheet['Heading1']))
        lst.append(Table(datalg,style=plainlg))

        SimpleDocTemplate(outputfile('test_table_layout.pdf'), showBoundary=1).build(lst)

def makeSuite():
    return makeSuiteForClasses(TableTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    print('saved '+outputfile('test_table_layout.pdf'))
    printLocation()
