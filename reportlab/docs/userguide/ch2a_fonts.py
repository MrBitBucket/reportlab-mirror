#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/docs/userguide/ch2_graphics.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/docs/userguide/ch2a_fonts.py,v 1.1 2001/11/06 11:13:53 johnprecedo Exp $
from reportlab.tools.docco.rl_doc_utils import *
from reportlab.lib.codecharts import SingleByteEncodingChart
from reportlab.platypus import Image
    
heading1("Arbitrary fonts and encodings")

disc("""
This chapter explains how you can use arbitrary fonts,
which will increase slightly the document size because these
fonts need to be embedded within the document.
""")

disc("""
Support for custom fonts and encoding is new in this release of 
reportlab (Release 1.10, 6 Nov. 2001), and as such some things may 
change in the future. The canvas methods  $setFont$, $getFont$, 
$registerEncoding$ and $registerTypeFace$ can all be considered 
stable. Other things such as how reportlab searches for fonts are more 
liable to change.
""")

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
Right now font-embedding relies on font description files in the Adobe
AFM ('Adobe Font Metrics') and PFB ('Printer Font Binary') format. The
former is an ASCII file and contains information about the characters
('glyphs') in the font such as height, width, bounding box info and
other 'metrics', while the latter is a binary file that describes the
shapes of the font. The $reportlab/fonts$ directory contains the files
$'LeERC___.AFM'$ and $'LeERC___.PFB'$ that are used as an example
font.
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
import reportlab
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

heading2("Single-Byte Font Encodings")
disc("""
Every time you draw some text, you presume an encoding.
The Reportlab PDF library offers very fine-grained control
of character encodings, which can be critical.  You can specify
the encoding to use at a per-installation, per-document or per-font
level, and also synthesize your own encodings.  
""")

disc("""The module reportlab/rl_config.py contains a variable
'defaultEncoding' which will usually be set to one of "WinAnsiEncoding"
or "MacRomanEncoding".  In the distribution, it is the first, but Mac users will
commonly edit it.  Unless otherwise specified, this is used for text fonts.
Let's start by reviewing the characters in these fonts.
""")

disc("""The code chart below shows the characters in the $WinAnsiEncoding$.
This is the standard encoding on Windows and many Unix systems in America
and Western Europe.  It is also knows as Code Page 1252, and is practically
identical to ISO-Latin-1 (it contains one or two extra characters). This
is the default encoding used by the Reportlab PDF Library. It was generated from
a standard routine in $reportlab/lib$, $codecharts.py$, 
which can be used to display the contents of fonts.  The index numbers
along the edges are in hex.""")

cht1 = SingleByteEncodingChart(encodingName='WinAnsiEncoding',charsPerRow=32, boxSize=12)
illust(lambda canv: cht1.drawOn(canv, 0, 0), "WinAnsi Encoding", cht1.width, cht1.height)

disc("""The code chart below shows the characters in the $MacRomanEncoding$.
as it sounds, this is the standard encoding on Macintosh computers in
America and Western Europe.  As usual with non-unicode encodings, the first
128 code points (top 4 rows in this case) are the ASCII standard and agree
with the WinAnsi code chart above; but the bottom 4 rows differ.""")
cht2 = SingleByteEncodingChart(encodingName='MacRomanEncoding',charsPerRow=32, boxSize=12)
illust(lambda canv: cht2.drawOn(canv, 0, 0), "MacRoman Encoding", cht2.width, cht2.height)

disc("""These two encodings are available for the standard fonts (Helvetica,
Times-Roman and Courier and their variants) and will be available for most
commercial fonts including those from Adobe.  However, some fonts contain non-
text glyphs and the concept does not really apply.  For example, ZapfDingbats
and Symbol can each be treated as having their own encoding.""")

cht3 = SingleByteEncodingChart(faceName='ZapfDingbats',encodingName='ZapfDingbatsEncoding',charsPerRow=32, boxSize=12)
illust(lambda canv: cht3.drawOn(canv, 0, 0), "ZapfDingbats and its one and only encoding", cht3.width, cht3.height)

cht4 = SingleByteEncodingChart(faceName='Symbol',encodingName='SymbolEncoding',charsPerRow=32, boxSize=12)
illust(lambda canv: cht4.drawOn(canv, 0, 0), "Symbol and its one and only encoding", cht4.width, cht4.height)

todo(""""Complete this section with examples of synthesizing new encodings
and fonts, based on test_pdfbase_encodings.py""")

heading2("Asian Font Support")
disc("""The Reportlab PDF Library aims to expose full support for Asian fonts.
PDF is the first really portable solution for Asian text handling.
Japanese, Traditional Chinese (Taiwan/Hong Kong), Simplified Chinese (mainland China)
and Korean are all supported; however, you have to download the relevant font pack
from Adobe's web site to view such PDF files, or you'll get cryptic error messages
about "bad CMaps".
""")

disc("""Since many users will not have the font packs installed, we have included
a rather grainy ^bitmap^ of some Japanese characters.  We will discuss below what is needed to
generate them.""")
# include a bitmap of some Asian text
I=os.path.join(os.path.dirname(__file__),'..','images','jpnchars.jpg')
try:
	getStory().append(Image(I))
except:
	disc("""An image should have appeared here.""")

disc("""Asian multi-byte fonts are called 'CIDFonts'.  CID stands for 'Character ID'.  The
central idea is that a font contains many thousands of glyphs each identified by a numeric
character ID, and that encodings determine which strings (typically one or two bytes long)
map to which character IDs.  This is exactly the same concept as for single byte fonts.
However, the implementation differs slightly, as does the amount of work we have to do
to load and measure these fonts accurately.""")

disc("""You create CID fonts with a combination of a face name and an encoding name.
By convention, the font name is a combination of the two separated by a dash.
It is actually possible to create separate CIDTypeFace and CIDEncoding objects, and
to assign your own names, but there is no point; Adobe has followed the naming
convention since CID fonts were introduced.  We wish they (and we) had done so with
single byte fonts too!  Once a font is registered, you can use it by its combined
name with $setFont$.""")

eg("""
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import CIDFont
pdfmetrics.registerFont(CIDFont('HeiseiMin-W3','90ms-RKSJ-H'))
canvas.setFont('HeiseiMin-W3-90ms-RKSJ-H', 16)

# this says "This is HeiseiMincho" in shift-JIS.  Not all our readers
# have a Japanese PC, so I escaped it. On a Japanese-capable
# system, print the string to see Kanji
message1 = '\202\261\202\352\202\315\225\275\220\254\226\276\222\251\202\305\202\267\201B'
canvas.drawString(100, 675, message1)
""")

disc("""A full list of the available fonts and encodings is available near the
top of $reportlab/pdfbase/_cidfontdata.py$.  Also, the following four test scripts
generate samples in the corresponding languages:""")
eg("""reportlab/test/test_multibyte_jpn.py
reportlab/test/test_multibyte_kor.py
reportlab/test/test_multibyte_chs.py
reportlab/test/test_multibyte_cht.py""")

Illustration(image("../images/jpn.gif", width=531*0.50,
height=435*0.50), 'Output from test_multibyte_jpn.py')

caption("""
Output from test_multibyte_jpn.py
""")

disc("""
The encoding and font data are grouped by some standard 'language
prefixes':
""")
bullet("""
$chs$ = Chinese Simplified (mainland)
""")
bullet("""
$cht$ = Chinese Traditional (Taiwan)
""")
bullet("""
$kor$ = Korean
""")
bullet("""
$jpn$ = Japanese
""")

disc("""
Each of the following sections provided the following information for each language:
""")

bullet("""
'language prefix':
chs, cht, kor or jpn
""")
bullet("""
'typefaces':
the allowed typefaces for that language
""")
bullet("""
'encoding names':
the official encoding names, with comments taken verbatim from the PDF
Spec (also found in file $pdfbase/_cidfontdata.py$)
""")
bullet("""
test:
the name and location of the test file for that language
""")


CPage(3)
heading3("Chinese Simplified")
disc("""
'language prefix': $chs$
""")
disc("""
typefaces: '$STSong-Light$'
""")
disc("""
encoding names:
""")
eg("""
'GB-EUC-H',         # Microsoft Code Page 936 (lfCharSet 0x86), GB 2312-80
                    # character set, EUC-CN encoding
'GB-EUC-V',         # Vertical version of GB-EUC-H
'GBpc-EUC-H',       # Macintosh, GB 2312-80 character set, EUC-CN encoding,
                    # Script Manager code 2
'GBpc-EUC-V',       # Vertical version of GBpc-EUC-H
'GBK-EUC-H',        # Microsoft Code Page 936 (lfCharSet 0x86), GBK character
                    # set, GBK encoding
'GBK-EUC-V',        # Vertical version of GBK-EUC-V
'UniGB-UCS2-H',     # Unicode (UCS-2) encoding for the Adobe-GB1
                    # character collection
'UniGB-UCS2-V'      # Vertical version of UniGB-UCS2-H.
""")
disc("""
test:
$reportlab/test/test_multibyte_chs.py$
""")


CPage(3)
heading3("Chinese Traditional")
disc("""
'language prefix': $cht$
""")
disc("""
typefaces: '$MSung-Light$', '$MHei-Medium$'
""")
disc("""
encoding names:
""")
eg("""
'B5pc-H',           # Macintosh, Big Five character set, Big Five encoding,
                    # Script Manager code 2
'B5pc-V',           # Vertical version of B5pc-H
'ETen-B5-H',        # Microsoft Code Page 950 (lfCharSet 0x88), Big Five
                    # character set with ETen extensions
'ETen-B5-V',        # Vertical version of ETen-B5-H
'ETenms-B5-H',      # Microsoft Code Page 950 (lfCharSet 0x88), Big Five
                    # character set with ETen extensions; this uses proportional
                    # forms for half-width Latin characters.
'ETenms-B5-V',      # Vertical version of ETenms-B5-H
'CNS-EUC-H',        # CNS 11643-1992 character set, EUC-TW encoding
'CNS-EUC-V',        # Vertical version of CNS-EUC-H
'UniCNS-UCS2-H',    # Unicode (UCS-2) encoding for the Adobe-CNS1
                    # character collection
'UniCNS-UCS2-V'     # Vertical version of UniCNS-UCS2-H.
""")
disc("""
test:
$reportlab/test/test_multibyte_cht.py$
""")


CPage(3)
heading3("Korean")
disc("""
'language prefix': $kor$ 
""")
disc("""
typefaces: '$HYSMyeongJoStd-Medium$','$HYGothic-Medium$'
""")
disc("""
encoding names:
""")
eg("""
'KSC-EUC-H',        # KS X 1001:1992 character set, EUC-KR encoding
'KSC-EUC-V',        # Vertical version of KSC-EUC-H
'KSCms-UHC-H',      # Microsoft Code Page 949 (lfCharSet 0x81), KS X 1001:1992
                    #character set plus 8,822 additional hangul, Unified Hangul
                    #Code (UHC) encoding
'KSCms-UHC-V',      #Vertical version of KSCms-UHC-H
'KSCms-UHC-HW-H',   #Same as KSCms-UHC-H, but replaces proportional Latin
                    # characters with halfwidth forms
'KSCms-UHC-HW-V',   #Vertical version of KSCms-UHC-HW-H
'KSCpc-EUC-H',      #Macintosh, KS X 1001:1992 character set with MacOS-KH
                    #extensions, Script Manager Code 3
'UniKS-UCS2-H',     #Unicode (UCS-2) encoding for the Adobe-Korea1 character collection
'UniKS-UCS2-V'      #Vertical version of UniKS-UCS2-H
    
""")
disc("""
test:
$reportlab/test/test_multibyte_kor.py$
""")


CPage(3)
heading3("Japanese")
disc("""
'language prefix': $jpn$
""")
disc("""
typefaces: '$HeiseiMin-W3$', '$HeiseiKakuGo-W5$'
""")
disc("""
encoding names:
""")
eg("""
'83pv-RKSJ-H',      #Macintosh, JIS X 0208 character set with KanjiTalk6
                    #extensions, Shift-JIS encoding, Script Manager code 1
'90ms-RKSJ-H',      #Microsoft Code Page 932 (lfCharSet 0x80), JIS X 0208
                    #character set with NEC and IBM extensions
'90ms-RKSJ-V',      #Vertical version of 90ms-RKSJ-H
'90msp-RKSJ-H',     #Same as 90ms-RKSJ-H, but replaces half-width Latin
                    #characters with proportional forms
'90msp-RKSJ-V',     #Vertical version of 90msp-RKSJ-H
'90pv-RKSJ-H',      #Macintosh, JIS X 0208 character set with KanjiTalk7
                    #extensions, Shift-JIS encoding, Script Manager code 1
'Add-RKSJ-H',       #JIS X 0208 character set with Fujitsu FMR extensions,
                    #Shift-JIS encoding
'Add-RKSJ-V',       #Vertical version of Add-RKSJ-H
'EUC-H',            #JIS X 0208 character set, EUC-JP encoding
'EUC-V',            #Vertical version of EUC-H
'Ext-RKSJ-H',       #JIS C 6226 (JIS78) character set with NEC extensions,
                    #Shift-JIS encoding
'Ext-RKSJ-V',       #Vertical version of Ext-RKSJ-H
'H',                #JIS X 0208 character set, ISO-2022-JP encoding,
'V',                #Vertical version of H
'UniJIS-UCS2-H',    #Unicode (UCS-2) encoding for the Adobe-Japan1 character
                    #collection
'UniJIS-UCS2-V',    #Vertical version of UniJIS-UCS2-H
'UniJIS-UCS2-HW-H', #Same as UniJIS-UCS2-H, but replaces proportional Latin
                    #characters with half-width forms
'UniJIS-UCS2-HW-V'  #Vertical version of UniJIS-UCS2-HW-H
""")
disc("""
test:
$reportlab/test/test_multibyte_jpn.py$
""")




pencilnote()
heading3("Character Mappings and Configuration")
disc("""In order to accurately measure the width of Asian characters, and
thus to correctly right-align and centre them, we need access to the mapping
tables which relate each encoding to the glyphs in the font file.  We currently
get this by processing the Acrobat Reader CMap files; these wil be on your
system if the relevant font packs are installed.  If you try to generate an
Asian document and get an error, check that the relevant Acrobat Language Pack
is installed.  Then, check in rl_config.py which has a list of standard locations;
you may need to edit this list.
""")

disc("""
Most of these files are small and fast to parse, but the Unicode ones are
big.  Any encoding with 'UCS2' in the name is Unicode.  The files work with
consecutive runs of characters, but there may be 10,000 runs of 1 character
in a Unicode maping table; it may take minutes to parse these.  Therefore,
after the first parse, we write a marshalled dictionary in the
$reportlab/fonts$ directory with the extension $.fastmap$.  This is used on
subsequent calls and loads up to 100x faster.  If you are running in a
secure environment such as a web server, be aware that you either need
to pre-generate and copy up this file, or ensure that the web user can
write this directory.
""")

disc("""
We are working on a compressed mapping database which will remove any
need to refer to Adobe's CMap files, and further speed up access.
""")


##### FILL THEM IN
