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
#	$Log: styles_modern.py,v $
#	Revision 1.4  2000/02/17 02:06:28  rgbecker
#	Docstring & other fixes
#
#	Revision 1.3  2000/02/16 09:42:50  rgbecker
#	Conversion to reportlab package
#	
#	Revision 1.2  2000/02/15 17:55:59  rgbecker
#	License text fixes
#	
#	Revision 1.1.1.1  2000/02/15 15:09:12  rgbecker
#	Initial setup of demos directory and contents.
#	
__version__=''' $Id: styles_modern.py,v 1.4 2000/02/17 02:06:28 rgbecker Exp $ '''
# style_modern.py
__doc__="""This is an example style sheet.  You can create your own, and
have them loaded by the presentation.  A style sheet is just a
dictionary, where they keys are style names and the values are
layout.ParagraphStyle objects.

You must provide a function called "getParagraphStyles()" to
return it.  In future, we can put things like LineStyles,
TableCellStyles etc. in the same modules.

You might wish to have two parallel style sheets, one for colour
and one for black and white, so you can switch your presentations
easily.

A style sheet MUST define a style called 'Normal'.
"""

from reportlab.platypus import layout

def getParagraphStyles():
    """Returns a dictionary of styles based on Helvetica"""
    stylesheet = {}
    ParagraphStyle = layout.ParagraphStyle
 
    para = ParagraphStyle('Normal', None)   #the ancestor of all
    para.fontName = 'Helvetica'
    para.fontSize = 24
    para.leading = 28
    stylesheet['Normal'] = para

    para = ParagraphStyle('BodyText', stylesheet['Normal'])
    para.spaceBefore = 12
    stylesheet['BodyText'] = para
    
    para = ParagraphStyle('BigCentered', stylesheet['Normal'])
    para.spaceBefore = 12
    para.alignment = layout.TA_CENTER
    stylesheet['BigCentered'] = para

    para = ParagraphStyle('Italic', stylesheet['BodyText'])
    para.fontName = 'Helvetica-Oblique'
    stylesheet['Italic'] = para

    para = ParagraphStyle('Title', stylesheet['Normal'])
    para.fontName = 'Helvetica'
    para.fontSize = 48
    para.Leading = 58
    para.spaceAfter = 36
    para.alignment = layout.TA_CENTER
    stylesheet['Title'] = para
    
    para = ParagraphStyle('Heading1', stylesheet['Normal'])
    para.fontName = 'Helvetica-Bold'
    para.fontSize = 36
    para.leading = 44
    para.spaceAfter = 36
    para.alignment = layout.TA_CENTER
    stylesheet['Heading1'] = para
    
    para = ParagraphStyle('Heading2', stylesheet['Normal'])
    para.fontName = 'Helvetica-Bold'
    para.fontSize = 28
    para.leading = 34
    para.spaceBefore = 24
    para.spaceAfter = 12
    stylesheet['Heading2'] = para
    
    para = ParagraphStyle('Heading3', stylesheet['Normal'])
    para.fontName = 'Helvetica-BoldOblique'
    para.spaceBefore = 24
    para.spaceAfter = 12
    stylesheet['Heading3'] = para

    para = ParagraphStyle('Bullet', stylesheet['Normal'])
    para.firstLineIndent = 54
    para.leftIndent = 72
    para.spaceBefore = 6
    #para.bulletFontName = 'Symbol'
    para.bulletFontSize = 24
    para.bulletIndent = 36
    stylesheet['Bullet'] = para

    para = ParagraphStyle('Definition', stylesheet['Normal'])
    #use this for definition lists
    para.firstLineIndent = 72
    para.leftIndent = 72
    para.bulletIndent = 0
    para.spaceBefore = 12
    para.bulletFontName = 'Helvetica-BoldOblique'
    stylesheet['Definition'] = para

    para = ParagraphStyle('Code', stylesheet['Normal'])
    para.fontName = 'Courier'
    para.fontSize = 16
    para.leading = 18
    para.leftIndent = 36
    stylesheet['Code'] = para

    return stylesheet
