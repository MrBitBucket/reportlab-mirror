#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/docs/userguide/ch2_graphics.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/docs/userguide/ch2a_fonts.py,v 1.7 2002/07/25 11:18:08 dinu_gherman Exp $
from reportlab.tools.docco.rl_doc_utils import *
from reportlab.lib.codecharts import SingleByteEncodingChart
from reportlab.platypus import Image

heading1("Fonts and encodings")

disc("""
This chapter covers fonts, encodings and Asian language capabilities.
If you are purely concerned with generating PDFs for Western
European languages, you can skip this on a first reading.
We expect this section to grow considerably over time. We
hope that Open Source will enable us to give better support for
more of the world's languages than other tools, and we welcome
feedback and help in this area.
""")

disc("""
Support for custom fonts and encoding is was new
in reportlab (Release 1.10, 6 Nov. 2001), and may
change in the future. The canvas methods  $setFont$, $getFont$,
$registerEncoding$ and $registerTypeFace$ can all be considered
stable. Other things such as how reportlab searches for fonts are more
liable to change.
""")


heading2("Using non-standard fonts")

disc("""
As discussed in the previous chapter, every copy of Acrobat Reader
comes with 14 standard fonts built in.  Therefore, the ReportLab
PDF Library only needs to refer to these by name.  If you want
to use other fonts, they must be embedded in the PDF document.""")

disc("""
You can use the mechanism described below to include arbitrary
fonts in your documents. Just van Rossum has kindly
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
In the following example locate the folder containing the test font and
register it for future use with the $pdfmetrics$ module,
after which we can use it like any other standard font.
""")


eg("""
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

heading3("Missing Glyphs")
disc("""If you specify an encoding, it is generally assumed that
the font designer has provided all the needed glyphs.  However,
this is not always true.  In the case of our example font,
the letters of the alphabet are present, but many symbols and
accents are missing.  The default behaviour is for the font to
print a 'notdef' character - typically a blob, dot or space -
when passed a character it cannot draw.  However, you can ask
the library to warn you instead; the code below (executed
before loading a font) will cause warnings to be generated
for any glyphs not in the font when you register it.""")

eg("""
import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0
""")



heading2("Standard Single-Byte Font Encodings")
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


heading2("Custom Font Encodings")

disc("""
It is possible to create your own single-byte encodings.  This may be necessary if you are
designing fonts, or want to use a character which is provided in the font but not in the
current encoding.  Adobe's fonts commonly contain 300 or more glyphs (covering symbols, ligatures
and various things used in professional publishing), but only 256 can be referenced in any one
encoding.
""")

disc("""
The code below comes from $test_pdfbase_encodings.py$ and shows a simple example.  The MacRoman
encoding lacks a Euro character, but it is there in the fonts.  You get hold of an encoding
object (which must be based on an existing standard encoding), and treat it like a dictionary,
assigning the byte values ("code points") you wish to change.  Then register it.  We'll make a
Mac font with the Euro at position 219 to demonstrate this. """)
eg("""
# now make our hacked encoding
euroMac = pdfmetrics.Encoding('MacWithEuro', 'MacRomanEncoding')
euroMac[219] = 'Euro'
pdfmetrics.registerEncoding(euroMac)

pdfmetrics.registerFont(pdfmetrics.Font('MacHelvWithEuro', 'Helvetica-Oblique', 'MacWithEuro'))

c.setFont('MacHelvWithEuro', 12)
c.drawString(125, 575, 'Hacked MacRoman with Euro: Character 219 = "\333"') # oct(219)=0333
""")

heading2("Asian Font Support")
disc("""The Reportlab PDF Library aims to expose full support for Asian fonts.
PDF is the first really portable solution for Asian text handling.
Japanese, Traditional Chinese (Taiwan/Hong Kong), Simplified Chinese (mainland China)
and Korean are all supported; however, you have to download the relevant font pack
from Adobe's web site to view such PDF files, or you'll get cryptic error messages
about "bad CMaps".  We do not yet support TrueType Unicode fonts with subsetting, which
is the other technique used by Distiller in creating Asian PDF documents.
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
message1 = '\\202\\261\\202\\352\\202\\315\\225\\275\\220\\254\\226\\276\\222\\251\\202\\305\\202\\267\\201B'
canvas.drawString(100, 675, message1)
""")
#had to double-escape the slashes above to get escapes into the PDF

disc("""A full list of the available fonts and encodings is available near the
top of $reportlab/pdfbase/_cidfontdata.py$.  Also, the following four test scripts
generate samples in the corresponding languages:""")
eg("""reportlab/test/test_multibyte_jpn.py
reportlab/test/test_multibyte_kor.py
reportlab/test/test_multibyte_chs.py
reportlab/test/test_multibyte_cht.py""")

disc("""The illustration below shows part of the first page
of the Japanese output sample.  It shows both horizontal and vertical
writing, and illustrates the ability to mix variable-width Latin
characters in Asian sentences.  The choice of horizontal and vertical
writing is determined by the encoding, which ends in 'H' or 'V'.
Whether an encoding uses fixed-width or variable-width versions
of Latin characters also depends on the encoding used; see the definitions
below.""")

Illustration(image("../images/jpn.gif", width=531*0.50,
height=435*0.50), 'Output from test_multibyte_jpn.py')

caption("""
Output from test_multibyte_jpn.py
""")
heading2("Available Asian typefaces and encodings")
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

heading3("To Do")
disc("""We expect to be developing this area of the package for some time.accept2dyear
Here is an outline of the main priorities.  We welcome help!""")

bullet("""
Ensure that we have accurate character metrics for all encodings in horizontal and
vertical writing.""")

bullet("""
document everything thoroughly.""")

bullet("""
build a compressed mapping database which will remove any
need to refer to Adobe's CMap files, and further speed up access.
""")

bullet("""
write accelerators in C for loading CMaps and calculating the widths of
strings""")

bullet("""
draw Asian text in the bitmap output of reportlab/graphics, so that we can provide
identical charts in all media
""")

bullet("""
allow support for Gaiji (user-defined characters) easily by implementing composite
fonts made out of a standard Asian font and a small custom-built Type 1 font.
""")

bullet("""
implement and then accelerate the correct paragraph wrapping rules for paragraphs""")

bullet("""
support Unicode documents with automatic selection of the underlying encoding
for printing""")

CPage(5)
heading2("TrueType Font Support")
disc("""
Marius Gedminas $mgedmin@codeworks.lt$ with the help of Viktorija Zaksien $viktorija@codeworks.lt$
have contributed support for embedded TrueType fonts and preliminary Unicode translation using UTF-8!""")

disc("""The current support should be regarded as experimental, but it seems to work and doesn't
interfere with anything else. Marius' patch worked almost out of the box and only some additional
support for finding TTF files was added.""")

CPage(3)
disc("""Simple things are done simply; we use <b>$reportlab.pdfbase.ttfonts.TTFont$</b> to create a true type
font object and register using <b>$reportlab.pdfbase.pdfmetrics.registerFont$</b>.
In pdfgen drawing directly to the canvas we can do""")
eg("""
# we know some glyphs are missing, suppress warnings
import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('Rina', 'rina.ttf'))
canvas.setFont(Rina, 32)
canvas.drawString(10, 150, "Some text encoded in UTF-8")
canvas.drawString(10, 100, "In the Rina TT Font!")
""")
illust(examples.ttffont1, "Using a the Rina TrueType Font")
disc("""In the above example the true type font object is created using""")
eg("""
    TTFont(name,filename)
""")
disc("""so that the ReportLab internal name is given by the first argument and the second argument
is a string(or file like object) denoting the font's TTF file. In Marius' original patch the filename
was supposed to be exactly correct, but we have modified things so that if the filename is relative
then a search for the corresponding file is done in the current directory and then in directories
specified by $reportlab.rl_config.TTFSearchpath$!""")

from reportlab.lib.styles import ParagraphStyle

from reportlab.lib.fonts import addMapping
addMapping('Rina', 0, 0, 'Rina')
addMapping('Rina', 0, 1, 'Rina')
addMapping('Rina', 1, 0, 'Rina')
addMapping('Rina', 1, 1, 'Rina')

disc("""Before using the TT Fonts in Platypus we should add a mapping from the family name to the
individual font names that describe the behaviour under the $<b>$ and $<i>$ attributes.""")

eg("""
from reportlab.lib.fonts import addMapping
addMapping('Rina', 0, 0, 'Rina')    #normal
addMapping('Rina', 0, 1, 'Rina')    #italic
addMapping('Rina', 1, 0, 'Rina')    #bold
addMapping('Rina', 1, 1, 'Rina')    #italic and bold
""")

disc("""we only have Rina regular so we map all to the same internal fontname. After registering and mapping
the Rina font as above we can use paragraph text like""")
parabox2("""<font name="Times-Roman" size="14">This is in Times-Roman</font>
<font name="Rina" color="magenta" size="14">and this is in magenta Rina!</font>""","Using TTF fonts in paragraphs")


##### FILL THEM IN