from random import randint
from xml.sax.saxutils import escape as xmlEscape
from reportlab import xrange
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)
import os,unittest
from reportlab.platypus import Spacer, SimpleDocTemplate, Table, TableStyle, ListFlowable, ListItem, \
        Paragraph, PageBreak, DDIndenter, MultiCol
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.utils import simpleSplit
from reportlab.lib import colors
from reportlab.lib import randomtext

TEXTS=[
'''We have already seen that the notion of level of grammaticalness is,
apparently, determined by a corpus of utterance tokens upon which
conformity has been defined by the paired utterance test.  If the
position of the trace in (99c) were only relatively inaccessible to
movement, a descriptively adequate grammar suffices to account for the
traditional practice of grammarians.  Notice, incidentally, that this
analysis of a formative as a pair of sets of features cannot be
arbitrary in the strong generative capacity of the theory.''',
'''
Of course, the systematic use of complex symbols raises serious doubts
about a stipulation to place the constructions into these various
categories.  By combining adjunctions and certain deformations, the
natural general principle that will subsume this case is to be regarded
as a descriptive fact.  This suggests that this analysis of a formative
as a pair of sets of features suffices to account for the requirement
that branching is not tolerated within the dominance scope of a complex
symbol.''',
'''In the discussion of resumptive pronouns following (81), this
selectionally introduced contextual feature is to be regarded as a
parasitic gap construction.  With this clarification, the systematic use
of complex symbols is not to be considered in determining a descriptive
fact.  On our assumptions, the notion of level of grammaticalness is
necessary to impose an interpretation on the strong generative capacity
of the theory.  It appears that a descriptively adequate grammar is not
subject to the requirement that branching is not tolerated within the
dominance scope of a complex symbol.  Comparing these examples with
their parasitic gap counterparts in (96) and (97), we see that this
selectionally introduced contextual feature is rather different from a
parasitic gap construction.''',
'''
Blah blah blah blah blah blah discipline?... naked? ... With a melon!? blah blah blah blah blah Very silly indeed Mr. Nesbitt has learned the first lesson of 'Not Being Seen', not to stand up. blah blah blah Would you like a twist of lemming sir?. 
''',
'''
Blah blah blah multidisciplinary blah blah blah blah blah blah blah blah blah blah blah. Blah blah blah conceptualize blah contribution blah blah blah blah blah blah blah blah blah blah blah blah proactive. Blah blah blah blah blah blah proactive blah mastery learning blah blah blah blah blah projection Total Quality Management blah. 
''',
'''
Blah Archer IV blah blah blah blah blah blah blah asteroid field USS Enterprise quantum flux blah blah Pacifica blah blah blah blah blah asteroid field. Blah blah K'Vort Class Bird-of-Prey battle bridge blah blah blah Bolian blah blah Dr. Pulaski blah blah blah blah. 
''',
'''
Blah blah blah Rexx blah RFC822-compliant blah blah ...went into "yo-yo mode" blah blah blah blah blah blah security blah DOS Unix blah blah blah. Blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah Virtual Reality Modeling Language blah blah blah blah blah. 
''',
]

class ListsTestCase(unittest.TestCase):
    "Make documents with tables"

    def test1(self):
        styleSheet = getSampleStyleSheet()
        doc = SimpleDocTemplate(outputfile('test_platypus_lists1.pdf'),showBoundary=True)
        story=[]
        sty = [ ('GRID',(0,0),(-1,-1),1,colors.green),
            ('BOX',(0,0),(-1,-1),2,colors.red),
            ]
        normal = styleSheet['BodyText']
        bold = normal.clone('bold',fontName='Helvetica-Bold')
        lpSty = normal.clone('lpSty',spaceAfter=18)
        data = [[str(i+1), Paragraph("xx "* (i%10), styleSheet["BodyText"]), Paragraph(("blah "*(i%40)), normal)] for i in xrange(5)]
        data1 = [[str(i+1), Paragraph(["zz ","yy "][i]*(i+3), styleSheet["BodyText"]), Paragraph(("duh  "*(i+3)), normal)] for i in xrange(2)]
        OL = ListFlowable(
            [
            Paragraph("A table with 5 rows", lpSty),
            Table(data, style=sty, colWidths = [50,100,200]),
            ListItem(
                Paragraph("A sublist", normal),
                value=7,
                ),
            ListFlowable(
                    [
                    Paragraph("Another table with 3 rows", normal),
                    Table(data[:3], style=sty, colWidths = [60,90,180]),
                    Paragraph(TEXTS[0], normal),
                    ],
                    bulletType='i',
                    ),
            Paragraph("An unordered sublist", normal),
            ListFlowable(
                    [
                    Paragraph("A table with 2 rows", normal),
                    ListItem(Table(data1, style=sty, colWidths = [60,90,180]),bulletColor='green'),
                    ListItem(Paragraph(TEXTS[2], normal),bulletColor='red',value='square')
                    ],
                    bulletType='bullet',
                    start='circle',
                    ),
            Paragraph(TEXTS[1], normal),
            ])

        story.append(OL)
        
        
        story.append(PageBreak())
        story.append(Paragraph("Now try a list with a very long URL in it.  Without splitting the long word it used to be that this can push out the right page margin", normal))
        OL = ListFlowable(
            [
            Paragraph(TEXTS[1], normal),
            Paragraph('''For details about pairing the smart card reader with the Android device, refer to the baiMobile specification: 
<a href="http://www.biometricassociates.com/downloads/user-guides/baiMobile-3000MP-User-Guide-for-Android-v2.0.pdf" color="blue">http://www.biometricassociates.com/downloads/user-guides/make-the-url-even-longer/baiMobile-3000MP-User-Guide-for-Android-v2.0.pdf</a>.''', normal),
            
            Paragraph(TEXTS[1], normal),
            ])

        story.append(OL)

        story.append(Paragraph("Same as above with a simple paragraph for the long word", normal))
        OL = ListFlowable(
            [
            Paragraph(TEXTS[1], normal),
            Paragraph('''For details about pairing the smart card reader with the Android device, refer to the baiMobile specification: 
http://www.biometricassociates.com/downloads/user-guides/make-the-url-even-longer/baiMobile-3000MP-User-Guide-for-Android-v2.0.pdf.''', normal),
            Paragraph(TEXTS[1], normal),
            ])
        story.append(OL)

        story.append(Paragraph("Same as above with a simple unicode paragraph for the long word", normal))
        OL = ListFlowable(
            [
            Paragraph(TEXTS[1], normal),
            Paragraph(u'''For details about pairing the smart card reader with the Android device, refer to the baiMobile specification: 
http://www.biometricassociates.com/downloads/user-guides/make-the-url-even-longer/baiMobile-3000MP-User-Guide-for-Android-v2.0.pdf.''', normal),
            Paragraph(TEXTS[1], normal),
            ])
        story.append(OL)

        story.append(
            ListFlowable(
                    [
                    Paragraph("Level 0.1", normal),
                    Paragraph("Level 0.2", normal),
                    ListFlowable(
                            [
                            Paragraph("Level 1.1", normal),
                            Paragraph("Level 1.1", normal),
                            ListFlowable(
                                    [
                                    Paragraph("Level 2.1", normal),
                                    Paragraph("Level 2.1", normal),
                                    Paragraph("Level 2.3", normal),
                                    ],
                                ),
                            Paragraph("Level 1.4", normal),
                            ],
                        ),
                    Paragraph("Level 0.4", normal),
                    ],
                    bulletType='1',
                    start='10',
                    ),
            )
        
        story.append(PageBreak())
        story.append(Paragraph("DDIndenter", style=normal))
        story.append(Paragraph("Coffee",style=bold))
        story.append(DDIndenter(Paragraph("Black hot drink",style=normal),leftIndent=36))
        story.append(Paragraph("Milk",style=bold))
        story.append(DDIndenter(Paragraph("White cold drink",style=normal),leftIndent=36))
        story.append(Paragraph("Whiskey",style=bold))
        story.append(DDIndenter(Paragraph("A nice alcoholic drink",style=normal),leftIndent=36))
        story.append(PageBreak())
        story.append(Paragraph("MultiCol", style=normal))
        RT = 'STARTUP COMPUTERS BLAH BUZZWORD STARTREK PRINTING PYTHON CHOMSKY CHOMSKY'.split()
        for i in xrange(5):
            topic = RT[randint(0,len(RT)-1)]
            np = randint(2,6)
            story.append(
                    MultiCol([
                        [Paragraph('Column %d' % (i+1,),style=bold)],
                        [],
                        [Paragraph(xmlEscape(randomtext.randomText(topic,randint(1,7))),style=normal) for j in xrange(np)]
                        ],
                        widths=['20%',3,'80%'],
                        )
                    )

        story.append(PageBreak())
        story.append(Paragraph("MultiCol 2", style=normal))
        for i in xrange(5):
            topic = RT[randint(0,len(RT)-1)]
            np = randint(2,6)
            story.append(
                    MultiCol([
                        ([Paragraph('Column %d' % (i+1,),style=bold)]+
                        [Paragraph(xmlEscape(randomtext.randomText(topic,randint(1,7))),style=normal) for j in xrange(np)]),
                        [],
                        [Paragraph(xmlEscape(randomtext.randomText(topic,randint(1,7))),style=normal) for j in xrange(np)]
                        ],
                        widths=['50%',5,'50%'],
                        )
                    )
        
        doc.build(story)

def makeSuite():
    return makeSuiteForClasses(ListsTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
