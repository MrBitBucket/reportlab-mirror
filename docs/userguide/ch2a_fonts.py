#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/docs/userguide/ch2_graphics.py?cvsroot=reportlab
#$Header: /tmp/reportlab/docs/userguide/ch2a_fonts.py,v 1.1 2001/11/05 13:34:28 johnprecedo Exp $
from rl_doc_utils import *

heading1("Arbitrary fonts and font encodings")

#heading2("Yadda Yada Yadda")

disc("""
This chapter explains how you can use arbitrary fonts and encodings. 
Using arbitrary fonts will increase the document size slightly 
because these fonts need to be embedded within the document.
""")

disc("""The $encoding$ argument determines which font encoding
is used for the standard fonts; this should correspond to
the encoding on your system.  It has two values at present:
$'WinAnsiEncoding'$ or $'MacRomanEncoding'$.  The variable
$rl_config.defaultEncoding$ above points to the former, which
is standard on Windows and many Unices (including Linux). If
you are a Mac user and want to make a global change, modify the
line at the top of <i>reportlab/pdfbase/pdfdoc.py</i> to switch it
over.""")


heading2("Arbitrary fonts")

disc("""
You can use the following mechanism described below to include
arbitrary fonts in your documents. Just van Rossum has kindly
donated a font named <i>LettErrorRobot-Chrome</i> which we may
use for testing and/or documenting purposes (and which you may
use as well). It comes bundled with the ReportLab distribution in the
directory $reportlab/fonts$.
""")

disc("""
Right now font-embedding relies on font description files in
the Adobe AFM and PFB format. The former is an ASCII file and
contains font metrics information while the latter is a
binary file that describes the shapes of the font. The
$reportlab/fonts$ directory contains the files $'LeERC___.AFM'$
and $'LeERC___.PFB'$ that are used as an example font.
""")

disc("""
In the following example we first set to suppress any
warnings during the font-emdedding as a result of missing
glyphs (sometime the case for the Euro character, say).
Then we locate the folder containing the test font and
register it for future use with the $pdfmetrics$ module,
after which we can use it like any other standard font.
""")


eg("""
# we know some glyphs are missing, suppress warnings
import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0

import os
import reportlab.test
folder = os.path.dirname(reportlab.__file__) + os.sep + 'fonts'
afmFile = os.path.join(folder, 'LeERC___.AFM')
pfbFile = os.path.join(folder, 'LeERC___.PFB')

from reportlab.pdfbase import pdfmetrics
justFace = pdfmetrics.EmbeddedType1Face(afmFile, pfbFile)
faceName = 'LettErrorRobot-Chrome' # pulled from AFM file
pdfmetrics.registerTypeFace(justFace)
justFont = pdfmetrics.Font('LettErrorRobot-Chrome',
                           faceName,
                           'WinAnsiEncoding')
pdfmetrics.registerFont(justFont)

canvas.setFont('LettErrorRobot-Chrome', 32)
canvas.drawString(10, 150, 'This should be in')
canvas.drawString(10, 100, 'LettErrorRobot-Chrome')
""")

illust(examples.customfont1, "Using a very non-standard font")

disc("""
The font's facename comes from the AFM file's $FontName$ field.
In the example above we knew the name in advance, but quite
often the names of font description files are pretty cryptic
and then you might want to retrieve the name from an AFM file
automatically.
When lacking a more sophisticated method you can use some
code as simple as this:
""")

eg("""
class FontNameNotFoundError(Exception):
    pass


def findFontName(path):
    "Extract a font name from an AFM file."

    f = open(path)

    found = 0
    while not found:
        line = f.readline()[:-1]
        if not found and line[:16] == 'StartCharMetrics':
            raise FontNameNotFoundError, path
        if line[:8] == 'FontName':
            fontName = line[9:]
            found = 1

    return fontName
""")

disc("""
In the <i>LettErrorRobot-Chrome</i> example we explicitely specified
the place of the font description files to be loaded.
In general, you'll prefer to store your fonts in some canonic
locations and make the embedding mechanism aware of them.
Using the same configuration mechanism we've already seen at the
beginning of this section we can indicate a default search path
for Type-1 fonts.
""")

disc("""
Unfortunately, there is no reliable standard yet for such
locations (not even on the same platform) and, hence, you might
have to edit the file $reportlab/rl_config.py$ to modify the
value of the $T1SearchPath$ identifier to contain additional
directories.
""")


heading2("Custom fonts")
todo("""To be added...""")

heading2("Custom encodings")
todo("""To be added...""")

heading2("Asian fonts")
todo("""To be added...""")


##### FILL THEM IN
