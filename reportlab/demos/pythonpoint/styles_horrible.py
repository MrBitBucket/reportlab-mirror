#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/demos/pythonpoint/styles_horrible.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/demos/pythonpoint/Attic/styles_horrible.py,v 1.6 2000/10/25 08:57:44 rgbecker Exp $
__version__=''' $Id: styles_horrible.py,v 1.6 2000/10/25 08:57:44 rgbecker Exp $ '''
# style_modern.py
__doc__="""This is an example style sheet.  You can create your own, and
have them loaded by the presentation.  A style sheet is just a
dictionary, where they keys are style names and the values are
ParagraphStyle objects.

You must provide a function called "getParagraphStyles()" to
return it.  In future, we can put things like LineStyles,
TableCellStyles etc. in the same modules.

You might wish to have two parallel style sheets, one for colour
and one for black and white, so you can switch your presentations
easily.

A style sheet MUST define a style called 'Normal'.
"""

from reportlab.lib import styles, enums
def getParagraphStyles():
    """Returns a dictionary of styles based on Helvetica"""
    stylesheet = {}
    
    para = styles.ParagraphStyle('Normal', None)   #the ancestor of all
    para.fontName = 'Courier'
    para.fontSize = 24
    para.leading = 28
    stylesheet['Normal'] = para

    para = ParagraphStyle('BodyText', stylesheet['Normal'])
    para.spaceBefore = 12
    stylesheet['BodyText'] = para
    
    para = ParagraphStyle('BigCentered', stylesheet['Normal'])
    para.spaceBefore = 12
    para.alignment = enums.TA_CENTER
    stylesheet['BigCentered'] = para

    para = ParagraphStyle('Italic', stylesheet['BodyText'])
    para.fontName = 'Courier-Oblique'
    stylesheet['Italic'] = para

    para = ParagraphStyle('Title', stylesheet['Normal'])
    para.fontName = 'Courier'
    para.fontSize = 48
    para.Leading = 58
    para.spaceAfter = 36
    para.alignment = enums.TA_CENTER
    stylesheet['Title'] = para
    
    para = ParagraphStyle('Heading1', stylesheet['Normal'])
    para.fontName = 'Courier-Bold'
    para.fontSize = 36
    para.leading = 44
    para.spaceAfter = 36
    para.alignment = enums.TA_CENTER
    stylesheet['Heading1'] = para
    
    para = ParagraphStyle('Heading2', stylesheet['Normal'])
    para.fontName = 'Courier-Bold'
    para.fontSize = 28
    para.leading = 34
    para.spaceBefore = 24
    para.spaceAfter = 12
    stylesheet['Heading2'] = para
    
    para = ParagraphStyle('Heading3', stylesheet['Normal'])
    para.fontName = 'Courier-BoldOblique'
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
    para.bulletFontName = 'Couruer-BoldOblique'
    stylesheet['Definition'] = para

    para = ParagraphStyle('Code', stylesheet['Normal'])
    para.fontName = 'Courier'
    para.fontSize = 16
    para.leading = 18
    para.leftIndent = 36
    stylesheet['Code'] = para

    return stylesheet
