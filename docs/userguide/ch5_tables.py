#ch5_tables

from genuserguide import *

#begin chapter oon paragraphs
heading1("Paragraphs")
disc("""
The $reportlab.platypus.Paragraph class$ is one of the most useful of the Platypus $Flowables$;
it can format fairly arbitrary text and provides for inline font style and colour changes using
an xml style markup. The overall shape of the formatted text can be justified, right or left ragged
or centered. The xml markup can even be used to insert greek characters or to do subscripts.
""")
eg("""Paragraph(text, style, bulletText=None)""")
disc("""
Creates an instance of the $Paragraph$ class. The $text$ argument contains the text of the
paragraph; excess white space is removed from the text at the ends and internally after
linefeeds. This allows easy use of indented triple quoted text in <b>Python</b> scripts.
The $bulletText$ argument provides the text of a default bullet for the paragraph
The font and other properties for the paragraph text and bullet are set using the style argument.
""")
disc("""
The $style$ argument should be an instance of $class ParagraphStyle$ obtained typically
using""")
eg("""
from reportlab.lib.styles import ParagraphStyle
""")
disc("""
this container class provides for the setting of multiple default paragraph attributes
in a structured way. The styles are arranged in a dictionary style object called a $stylesheet$
which allows for the styles to be accessed as $stylesheet['BodyText']$. A sample style
sheet is provided
""")
eg("""
from reportlab.lib.styles import getSampleStyleSheet
stylesheet=getSampleStyleSheet()
normalStyle = stylesheet['Normal']
""")
disc("""
The options which can be set for a $Paragraph$ can be seen from the $ParagraphStyle$ defaults.
""")
heading4("$class ParagraphStyle$")
eg("""
class ParagraphStyle(PropertySet):
    defaults = {
        'fontName':'Times-Roman',
        'fontSize':10,
        'leading':12,
        'leftIndent':0,
        'rightIndent':0,
        'firstLineIndent':0,
        'alignment':TA_LEFT,
        'spaceBefore':0,
        'spaceAfter':0,
        'bulletFontName':'Times-Roman',
        'bulletFontSize':10,
        'bulletIndent':0,
        'textColor': black
        }
""")

heading2("Using Paragraph Styles")

#this will be used in the ParaBox demos.
sample = """You are hereby charged that on the 28th day of May, 1970, you did
willfully, unlawfully, and with malice of forethought, publish an
alleged English-Hungarian phrase book with intent to cause a breach
of the peace.  How do you plead?"""


disc("""The $Paragraph$ and $ParagraphStyle$ classes together
handle most common formatting needs. The following examples
draw paragraphs in various styles, and add a bounding box
so that you can see exactly what space is taken up.""")

s1 = ParagraphStyle('Normal')
parabox(sample, s1, 'The default $ParagraphStyle$')
    
disc("""The two atributes $spaceBefore$ and $spaceAfter$ do what they
say, except at the top or bottom of a frame. At the top of a frame,
$spaceBefore$ is ignored, and at the bottom, $spaceAfter$ is ignored.
This means that you could specify that a 'Heading2' style had two
inches of space before when it occurs in mid-page, but will not
get acres fo whitespace at the top of a page.  These two attributes
should be thought of as 'requests' to the Frame and are not part
of the space occupied by the Paragraph itself.""")

disc("""The $fontSize$ and $fontName$ tags are obvious, but it is
important to set the $leading$.  This is the spacing between
adjacent lines of text; a good rule of thumb is to make this
20% larger than the point size.  To get double-spaced text,
use a high $leading$.""")

disc("""The figure below shows space before and after and an
increased leading:""")

parabox(sample,
        ParagraphStyle('Spaced',
                       spaceBefore=6,
                       spaceAfter=6,
                       leading=16),
        'Space before and after and increased leading'
        )

disc("""The $firstLineIndent$, $leftIndent$ and $rightIndent$ attributes do exactly
what you would expect.  If you want a straight left edge, remember
to set $firstLineIndent$ equal to $leftIndent$.""")

parabox(sample,
        ParagraphStyle('indented',
                       firstLineIndent=48,
                       leftIndent=24,
                       rightIndent=24),
        'one third inch indents at left and right, two thirds on first line'
        )

disc("""Setting $firstLineIndent$ equal to zero, $leftIndent$
much higher, and using a
different font (we'll show you how later!) can give you a
definition list:.""")

parabox('<b><i>Judge Pickles: </i></b>' + sample,
        ParagraphStyle('dl',
                       leftIndent=36),
        'Definition Lists'
        )

disc("""There are four possible values of $alignment$, defined as
constants in the module <i>reportlab.lib.enums</i>.  These are
TA_LEFT, TA_CENTER or TA_CENTRE, TA_RIGHT and
TA_JUSTIFY, with values of 0, 1, 2 and 4 respectively.  These
do exactly what you would expect.""")


heading2("Paragraph XML Markup Tags")
disc("""XML markup can be used to modify or specify the
overall paragraph style, and also to specify intra-
paragraph markup.""")

heading3("The outermost &lt; para &gt; tag")


disc("""
The paragraph text may optionally be surrounded by
&lt;para attributes....&gt;
&lt;/para&gt;
tags. The attributes if any of the opening &lt;para&gt; tag affect the style that is used
with the $Paragraph$ $text$ and/or $bulletText$.
""")

from reportlab.platypus.paraparser import _addAttributeNames, _paraAttrMap

def getAttrs(A):
    _addAttributeNames(A)
    S={}
    for k, v in _paraAttrMap.items():
        a = v[0]
        if not S.has_key(a):
            S[a] = k
        else:
            S[a] = "%s, %s" %(S[a],k)

    K = S.keys()
    K.sort()
    D=[('Attribute','Synonyms')]
    for k in K:
        D.append((k,S[k]))
    cols=2*[None]
    rows=len(D)*[None]
    return cols,rows,D

t=apply(Table,getAttrs(_paraAttrMap))
t.setStyle(TableStyle([
            ('FONT',(0,0),(-1,1),'Times-Bold',10,12),
            ('FONT',(0,1),(-1,-1),'Courier',8,8),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ]))
getStory().append(t)
disc("""Some useful synonyms have been provided for our Python attribute
names, including lowercase versions, and the equivalent properties
from the HTML standard where they exist.  These additions make
it much easier to build XML-printing applications, since
much intra-paragraph markup may not need translating. The
table below shows the allowed attributes and synonyms in the
outermost paragraph tag.""")


heading3("Intra-paragraph markup and the $&lt;fontgt;$ tag")


