#!/bin/env python
###############################################################################
#
#	ReportLab Public License Version 1.0
#
#   Except for the change of names the spirit and intention of this
#   license is the same as that of Python
#
#	(C) Copyright ReportLab Inc. 1998-2000.
#
#
# All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted, provided
# that the above copyright notice appear in all copies and that both that
# copyright notice and this permission notice appear in supporting
# documentation, and that the name of ReportLab not be used
# in advertising or publicity pertaining to distribution of the software
# without specific, written prior permission. 
# 
#
# Disclaimer
#
# ReportLab Inc. DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS,
# IN NO EVENT SHALL ReportLab BE LIABLE FOR ANY SPECIAL, INDIRECT
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#
###############################################################################
#	$Log: testtables.py,v $
#	Revision 1.4  2000/02/16 09:42:50  rgbecker
#	Conversion to reportlab package
#
#	Revision 1.3  2000/02/15 17:55:59  rgbecker
#	License text fixes
#	
#	Revision 1.2  2000/02/15 15:47:10  rgbecker
#	Added license, __version__ and Logi comment
#
__version__=''' $Id: testtables.py,v 1.4 2000/02/16 09:42:50 rgbecker Exp $ '''
from reportlab.platypus import layout
from reportlab.platypus import tables

INCH = 72

def getTable():
    t = tables.Table(
            (72,36,36,36,36),
            (24, 16,16,18),
            (('','North','South','East','West'),
             ('Quarter 1',100,200,300,400),
             ('Quarter 2',100,400,600,800),
             ('Total',300,600,900,'1,200'))
            )
    return t

def makeStyles():
    styles = []
    for i in range(5):
        styles.append(tables.TableStyle([('ALIGN', (1,1), (-1,-1), 'RIGHT'),
                                         ('ALIGN', (0,0), (-1,0), 'CENTRE') ]))
    for style in styles[1:]:
        style.add('GRID', (0,0), (-1,-1), 0.25, 'BLACK')
    for style in styles[2:]:
        style.add('LINEBELOW', (0,0), (-1,0), 2, 'BLACK')
    for style in styles[3:]:
        style.add('LINEABOVE', (0, -1), (-1,-1), 2, 'RED')
    styles[-1].add('LINEBELOW',(1,-1), (-1, -1), 2, (0.5, 0.5, 0.5))
    return styles

def run():
    doc = layout.SimpleFlowDocument('testtables.pdf', (8.5*INCH, 11*INCH), 1)
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
        lst.append(layout.Spacer(0,12))
    doc.build(lst)

run()

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
