from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import operator, string
from reportlab.platypus import *
#from reportlab import rl_config
from reportlab.lib.styles import PropertySet, getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
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

        lst = []
        lst.append(Paragraph("""Oversized cells""", styleSheet['Heading1']))

        lst.append(Paragraph("""Cells can end up being larger than a page.
        In that case, we need to split the cell. splitByRow and splitInRow
        controls that. By default splitByRow is 1 and splitInRow is 0.
        It splits between two rows. """,
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
            """This is a very tall cell to make a tall row.""",
            styNormal)]
        cell2 = [Paragraph("A cell with two flowables.", styNormal),
            Paragraph("And valign= MIDDLE.", styNormal)]
        cell3 = [Paragraph("Paragraph with valign=TOP", styNormal)]

        tableData = [
            ['Row 1', 'Two rows:\nSo there', 'is a', 'place', 'to split', 'the table'],
            [cell1, cell2, cell3, 'valign=BOTTOM', 'valign=MIDDLE', 'valign=TOP']
        ]
        colWidths = (50, 75, 70, 90, 90, 70)

        # This is the table with splitByRow, which splits between row 1 & 2:
        t = Table(tableData,
                  colWidths=colWidths,
                  rowHeights=None,
                  style=ministy,
                  splitByRow=1,
                  splitInRow=0)
        parts = t.split(451, 60)
        lst.append(parts[0])
        lst.append(Spacer(0,6))
        lst.append(parts[1])

        lst.append(Paragraph("""Here is the same table, with splitByRow=0 and
        splitInRow=1. It splits inside a row.""",
        styNormal))

        # This is the table with splitInRow, which splits in row 2:
        t = Table(tableData,
                  colWidths=colWidths,
                  rowHeights=None,
                  style=ministy,
                  splitByRow=0,
                  splitInRow=1)

        parts = t.split(451, 60)
        lst.append(parts[0])
        lst.append(Spacer(0,6))
        lst.append(parts[1])

        lst.append(Paragraph("""Here is the same table, with splitByRow=1 and
        splitInRow=1. It splits between the rows, if possible.""",
        styNormal))

        # This is the table with both splits, which splits in row 2:
        t = Table(tableData,
                  colWidths=colWidths,
                  rowHeights=None,
                  style=ministy,
                  splitByRow=1,
                  splitInRow=1)

        parts = t.split(451, 60)
        lst.append(parts[0])
        lst.append(Spacer(0,6))
        lst.append(parts[1])

        lst.append(Paragraph("""But if we constrict the space to less than the first row,
        it splits that row.""",
        styNormal))

        # This is the table with both splits and no space, which splits in row 1:
        t = Table(tableData,
                  colWidths=colWidths,
                  rowHeights=None,
                  style=ministy,
                  splitByRow=1,
                  splitInRow=1)

        parts = t.split(451, 15)
        lst.append(parts[0])
        lst.append(Spacer(0,6))
        lst.append(parts[1])

        # Split it at a point in row 2, where the split fails
        lst.append(Paragraph("""When splitByRow is 0 and splitInRow is 1, we should
        still allow fallback to splitting between rows""",
        styNormal))

        t = Table(tableData,
                  colWidths=colWidths,
                  rowHeights=None,
                  style=ministy,
                  splitByRow=0,
                  splitInRow=1)
        parts = t.split(451, 50)
        lst.append(parts[0])
        lst.append(Spacer(0,6))
        lst.append(parts[1])

        lst.append(PageBreak())
        lst.append(Paragraph("""Long cell with multiple splits, and minimum split size""",
                             styleSheet['Heading2']))

        lst.append(Paragraph("With a height of 80 amd splitInRow=1 (no minimum rest) "
                             "we get a small last split.",
                             styleSheet['Normal']))

        ministy = TableStyle([('GRID', (0,0), (-1,-1), 1.0, colors.black),])
        cell1 = [Paragraph(
            "This is a very very tall cell to make a very very tall row so we can split it "
            "many many times, and also test for minimum splits.""",
            styNormal)]

        tableData = [['Row 1', 'Row 1'],[cell1, 'Cell2']]
        colWidths = (50,50)

        # This is the table with splitByRow, which splits between row 1 & 2:
        t = Table(tableData,
                  colWidths=colWidths,
                  rowHeights=None,
                  style=ministy,
                  splitByRow=0,
                  splitInRow=1)

        while True:
            s = t.split(4*inch, 80)
            lst.append(s[0])
            lst.append(Spacer(6,6))
            if len(s) > 1:
                t = s[1]
            else:
                break

        # Now the same, but with a minimum size of 40.
        lst.append(Paragraph("With minimum split size to 40 (splitInRow=40) the last split "
                             "isn't done, and it should instead flow over to the next page.",
                             styleSheet['Normal']))
        t = Table(tableData,
                  colWidths=colWidths,
                  rowHeights=None,
                  style=ministy,
                  splitByRow=0,
                  splitInRow=40)

        while True:
            s = t.split(4*inch, 80)
            if s:
                lst.append(s[0])
                lst.append(Spacer(6,6))
            else:
                lst.append(t)
            if len(s) > 1:
                t = s[1]
            else:
                break

        # It should also not split at less than 40 in the beginning.
        assert not t.split(4*inch, 30)

        lst.append(PageBreak())
        lst.append(Paragraph("""Style handling splitInRow""", styleSheet['Heading2']))

        tableData = [
            ['00\n\naa', '01', '02', '03', '04'],
            ['10', '11\nbb', '12', '13', '14'],
            ['20', '21', '22\ncc', '23', '24'],
            ['30', '31', '32', '33\ndd', '34']
        ]
        styles = [
            ('GRID',(0,0),(-1,-1),0.5,colors.grey),
            ('GRID',(1,1),(-2,-2),1,colors.green),
            ('BOX',(0,0),(1,-1),2,colors.red),
            ('BOX',(0,0),(-1,-1),2,colors.black),
            ('LINEABOVE',(1,2),(-2,2),1,colors.blue),
            ('LINEBEFORE',(2,1),(2,-2),1,colors.pink),
            ('BACKGROUND', (0, 0), (0, 1), colors.pink),
            ('BACKGROUND', (1, 1), (1, 2), colors.lavender),
            ('BACKGROUND', (2, 2), (2, 3), colors.orange),
            ('TEXTCOLOR',(0,-1),(-2,-1),colors.green),
        ]

        t = Table(tableData,style=styles, splitInRow=1, splitByRow=0)
        for split in (36, 60, 100, 130,):
            parts = t.split(4*inch, split)
            lst.append(parts[0])
            lst.append(Spacer(0,6))
            lst.append(parts[1])
            lst.append(Spacer(0,12))

        lst.append(PageBreak())
        lst.append(Paragraph("""Splitfirst/splitlast behavior with split rows and spans""",
                             styleSheet['Heading2']))

        data=  [['A', 'BBBBB', 'C', 'D', 'E'],
                ['00', '01', '02', '03', '04'],
                ['10\n11', ],
                ['20', '21', '22', '23', '24'],
                ['30', '31', '32', '33', '34']]
        sty = [
                ('ALIGN',(0,0),(-1,-1),'CENTER'),
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('GRID',(0,0),(-1,-1),1,colors.green),
                ('BOX',(0,0),(-1,-1),2,colors.red),

                #span 'BBBB' across middle 3 cells in top row
                ('SPAN',(1,0),(3,0)),
                #now color the first cell in this range only,
                #i.e. the one we want to have spanned.  Hopefuly
                #the range of 3 will come out khaki.
                ('BACKGROUND',(1,0),(1,0),colors.khaki),

                ('SPAN',(0,2),(-1,2)),

                #span 'AAA'down entire left column
                ('SPAN',(0,0), (0, 1)),
                ('BACKGROUND',(0,0),(0,0),colors.cyan),
                ('TEXTCOLOR', (0,'splitfirst'), (-1,'splitfirst'), colors.cyan),
                ('TEXTCOLOR', (0,'splitlast'), (-1,'splitlast'), colors.red),
                ('BACKGROUND', (0,'splitlast'), (-1,'splitlast'), colors.pink),
                ('LINEBELOW', (0,'splitlast'), (-1,'splitlast'), 1, colors.grey,'butt'),
               ]
        t=Table(data,style=sty, colWidths = [20] * 5, splitInRow=1, splitByRow=0)
        lst.append(t)
        lst.append(Spacer(18,18))

        for split in (40, 60, 75):
            for s in t.split(4*inch, split):
                lst.append(s)
                lst.append(Spacer(0,6))
            lst.append(Spacer(18,12))

        lst.append(PageBreak())
        lst.append(Paragraph("""Style handling with rowspans""", styleSheet['Heading2']))

        data = [
            ['R0C0\nR1C0\nR2C0', 'R0C1', 'R0C2', 'R0C3', 'R0C4\nR1C4'],
            ['', 'R1C1', 'R1C2', 'R1C3', ''],
            ['', 'R2C1', 'R2C2', 'R2C3', 'R2C4'],
            ['R3C0', 'R3C1', 'R3C2', 'R3C3 R3C4\nR4C3 R4C4', ''],
            ['R4C0', 'R4C1', 'R4C2', '', ''],
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
                ('TEXTCOLOR',(0,0),(-1,0),colors.brown),
                ('TEXTCOLOR',(1,1),(-2,-1),colors.green),
                ('SPAN',(0,0), (0, 2)),
                ('SPAN',(2,0), (2, 1)),
                ('SPAN',(3,3), (4, 4)),
                ('SPAN',(4,0), (4, 1)),
                ]
        t=Table(data,style=sty, colWidths = [40] * 5, splitInRow=1, splitByRow=0)
        lst.append(t)
        lst.append(Spacer(18,18))

        for split in (30, 45, 60, 75):
            for s in t.split(4*inch, split):
                lst.append(s)
                lst.append(Spacer(0,6))
            lst.append(Spacer(18,18))

        lst.append(PageBreak())
        lst.append(Paragraph("""More Style handling with rowspans""", styleSheet['Heading2']))

        data = [
            ['R0C0', 'R0C1', 'R0C2', 'R0C3', 'R0C4'],
            ['R1C0', 'R1C1', 'R1C2', 'R1C3', 'R1C4'],
            ['R2C0', 'R2C1', 'R2C2', 'R2C3', 'R2C4'],
            ['R3C0', 'R3C1', 'R3C2', 'R3C3', 'R3C4'],
            ['R4C0', 'R4C1', 'R4C2', 'R4C3', 'R4C4'],
        ]

        sty = [
                ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                ('GRID',(1,1),(1,-1),1,colors.green),
                ('BOX',(0,0),(-3,-3),3,colors.black),
                ('BOX',(1,1),(-1,-1),2,colors.red),
                ('LINEABOVE',(1,1),(2,2),1,colors.blue),
                ('LINEBELOW',(2,2),(4,4),1,colors.pink),
                ('BACKGROUND', (0, 0), (0, 0), colors.pink),
                ('BACKGROUND', (1, 1), (1, 2), colors.lavender),
                ('BACKGROUND', (4, 3), (4, 4), colors.orange),
                ('TEXTCOLOR',(0,0),(-1,0),colors.brown),
                ('TEXTCOLOR',(1,1),(-2,-1),colors.green),
                ('SPAN',(0,0), (0, -1)),
                ('SPAN',(2,1), (-2, 3)),
                ]
        t=Table(data,style=sty, colWidths = [40] * 5, splitInRow=1, splitByRow=0)
        lst.append(t)
        lst.append(Spacer(18,18))

        for split in (30, 45, 60, 75):
            for s in t.split(4*inch, split):
                lst.append(s)
                lst.append(Spacer(0,6))
            lst.append(Spacer(18,18))

        lst.append(PageBreak())
        lst.append(Paragraph("""Testing for a couple of height alignment bugs""", styleSheet['Heading2']))

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
        t=Table(data,style=sty, colWidths = [40] * 6, splitInRow=1, splitByRow=0)
        lst.append(t)
        lst.append(Spacer(0,6))

        for split in (30, 40, 50, 60):
            for s in t.split(4*inch, split):
                lst.append(s)
                lst.append(Spacer(0,6))
            lst.append(Spacer(18,18))

        SimpleDocTemplate(outputfile('test_table_inrowsplit.pdf'), showBoundary=1).build(lst)

def makeSuite():
    return makeSuiteForClasses(TableTestCase)


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    print('saved '+outputfile('test_table_inrowsplit.pdf'))
    printLocation()
