#!/bin/env python
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/platypus/test/testtables.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/test_platypus_tables.py,v 1.1 2001/04/13 16:02:55 andy_robinson Exp $
__version__=''' $Id: test_platypus_tables.py,v 1.1 2001/04/13 16:02:55 andy_robinson Exp $ '''
__doc__='Test script for reportlab.tables'

from reportlab.platypus import Spacer, SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.test import unittest

def getTable():
    t = Table((('','North','South','East','West'),
             ('Quarter 1',100,200,300,400),
             ('Quarter 2',100,400,600,800),
             ('Total',300,600,900,'1,200')),
             (72,36,36,36,36),
             (24, 16,16,18)
            )
    return t

def makeStyles():
    styles = []
    for i in range(5):
        styles.append(TableStyle([('ALIGN', (1,1), (-1,-1), 'RIGHT'),
                                         ('ALIGN', (0,0), (-1,0), 'CENTRE') ]))
    for style in styles[1:]:
        style.add('GRID', (0,0), (-1,-1), 0.25, colors.black)
    for style in styles[2:]:
        style.add('LINEBELOW', (0,0), (-1,0), 2, colors.black)
    for style in styles[3:]:
        style.add('LINEABOVE', (0, -1), (-1,-1), 2, colors.black)
    styles[-1].add('LINEBELOW',(1,-1), (-1, -1), 2, (0.5, 0.5, 0.5))
    return styles

def run():
    doc = SimpleDocTemplate('test_platypus_tables.pdf', pagesize=(8.5*inch, 11*inch), showBoundary=1)
    styles = makeStyles()
    lst = []
    for style in styles:
        t = getTable()
        t.setStyle(style)
##        print '--------------'
##        for rowstyle in t._cellstyles:
##            for s in rowstyle:
##                print s.alignment
        lst.append(t)
        lst.append(Spacer(0,12))
    doc.build(lst)

class TablesTestCase(unittest.TestCase):
    "Make documents with tables"
    def test1(self):
        "Make a document full of tables"
        run()

def makeSuite():
    suite = unittest.TestSuite()
    suite.addTest(TablesTestCase('test1'))
    return suite


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())

#LINEABOVE
#LINEBELOW
#LINEBEFORE
#LINEAFTER
#GRID
#BOX
#INNERGRID ??

#FONT
#TEXTCOLOR
#ALIGNMENT
#PADDING
