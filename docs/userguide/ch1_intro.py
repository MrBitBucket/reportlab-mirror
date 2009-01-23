#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/docs/userguide/ch1_intro.py
from tools.docco.rl_doc_utils import *
from reportlab.platypus.tableofcontents import TableOfContents
from datetime import datetime
import reportlab

title("ReportLab PDF Library")
title("User Guide")
centred('ReportLab Version ' + reportlab.Version)
centred(datetime.now().strftime('Document generated on %Y/%m/%d %H:%M:%S %Z'))

nextTemplate("TOC")

headingTOC()

toc = TableOfContents()
PS = ParagraphStyle
toc.levelStyles = [
    PS(fontName='Times-Bold', fontSize=14, name='TOCHeading1', leftIndent=20, firstLineIndent=-20, spaceBefore=5, leading=16),
    PS(fontSize=12, name='TOCHeading2', leftIndent=40, firstLineIndent=-20, spaceBefore=0, leading=12),
    PS(fontSize=10, name='TOCHeading3', leftIndent=60, firstLineIndent=-20, spaceBefore=0, leading=12),
    PS(fontSize=10, name='TOCHeading4', leftIndent=100, firstLineIndent=-20, spaceBefore=0, leading=12),
]
getStory().append(toc)

nextTemplate("Normal")

########################################################################
#
#               Chapter 1
#
########################################################################


heading1("Introduction")


heading2("About this document")
disc("""This document is an introduction to the ReportLab PDF library.
Some previous programming experience
is presumed and familiarity with the Python Programming language is
recommended.  If you are new to Python, we tell you in the next section
where to go for orientation.
""")

disc("""
This manual does not cover 100% of the features, but should explain all
the main concepts and help you get started, and point you at other
learning resources. 
After working your way through this, you should be ready to begin
writing programs to produce sophisticated reports.
""")

disc("""In this chapter, we will cover the groundwork:""")
bullet("What is ReportLab all about, and why should I use it?")
bullet("What is Python?")
bullet("How do I get everything set up and running?")

todo("""
We need your help to make sure this manual is complete and helpful.
Please send any feedback to our user mailing list,
which is signposted from <a href="http://www.reportlab.org/">www.reportlab.org</a>.
""")

heading2("What is the ReportLab PDF Library?")
disc("""This is a software library that lets you directly
create documents in Adobe's Portable Document Format (PDF) using
the Python programming language.   It also creates charts and data graphics
in various bitmap and vector formats as well as PDF.""")

disc("""PDF is the global standard for electronic documents. It
supports high-quality printing yet is totally portable across
platforms, thanks to the freely available Acrobat Reader.  Any
application which previously generated hard copy reports or driving a printer
can benefit from making PDF documents instead; these can be archived,
emailed, placed on the web, or printed out the old-fashioned way.
However, the PDF file format is a complex
indexed binary format which is impossible to type directly.
The PDF format specification is more than 600 pages long and
PDF files must provide precise byte offsets -- a single extra
character placed anywhere in a valid PDF document can render it
invalid.  This makes it harder to generate than HTML.""")

disc("""Most of the world's PDF documents have been produced
by Adobe's Acrobat tools, or rivals such as JAWS PDF Creator, which act
as 'print drivers'.  Anyone wanting to automate PDF production would
typically use a product like Quark, Word or Framemaker running in a loop
with macros or plugins, connected to Acrobat. Pipelines of several
languages and products can be slow and somewhat unwieldy.
""")


disc("""The ReportLab library directly creates PDF based on
your graphics commands.  There are no intervening steps.  Your applications
can generate reports extremely fast - sometimes orders
of magnitude faster than traditional report-writing
tools.   This approach is shared by several other libraries - PDFlib for C,
iText for Java, iTextSharp for .NET and others.  However, The ReportLab library
differs in that it can work at much higher levels, with a full featured engine
for laying out documents complete with tables and charts.  """)


disc("""In addition, because you are writing a program
in a powerful general purpose language, there are no
restrictions at all on where you get your data from,
how you transform it, and the kind of output
you can create.  And you can reuse code across
whole families of reports.""")

disc("""The ReportLab library is expected to be useful
in at least the following contexts:""")
bullet("Dynamic PDF generation on the web")
bullet("High-volume corporate reporting and database publishing")
bullet("""An embeddable print engine for other applications, including
a 'report language' so that users can customize their own reports. <i>
This is particularly relevant to cross-platform apps which cannot
rely on a consistent printing or previewing API on each operating
system</i>.""")
bullet("""A 'build system' for complex documents with charts, tables
and text such as management accounts, statistical reports and
scientific papers """)
bullet("""Going from XML to PDF in one step!""")




heading2("What is Python?")
disc("""
Python is an <i>interpreted, interactive, object-oriented</i> programming language. It is often compared to Tcl, Perl,
Scheme or Java.
""")

disc("""
Python combines remarkable power with very clear syntax. It has modules, classes, exceptions, very high level
dynamic data types, and dynamic typing. There are interfaces to many system calls and libraries, as well as to
various windowing systems (X11, Motif, Tk, Mac, MFC). New built-in modules are easily written in C or C++.
Python is also usable as an extension language for applications that need a programmable interface.
""")


disc("""
Python is as old as Java and has been growing steadily in popularity for years; since our
library first came out it has entered the mainstream.  Many ReportLab library users are
already Python devotees, but if you are not, we feel that the language is an excellent
choice for document-generation apps because of its expressiveness and ability to get
data from anywhere.
""")

disc("""
Python is copyrighted but <b>freely usable and distributable, even for commercial use</b>.
""")

heading2("Acknowledgements")
disc("""Many people have contributed to ReportLab.  We would like to thank
in particular (in approximately chronological order) Chris Lee, Magnus Lie Hetland,
Robert Kern, Jeff Bauer (who contributed normalDate.py); Jerome Alet (numerous patches
and the rlzope demo), Andre Reitz, Max M, Albertas Agejevas, T Blatter, Ron Peleg,
Gary Poster, Steve Halasz, Andrew Mercer, Paul McNett, Chad Miller, Tim Roberts,
Jorge Godoy and Benn B.""")

disc("""Special thanks go to Just van Rossum for his valuable assistance with
font technicalities.""")

disc("""Marius Gedminas deserves a big hand for contributing the work on TrueType fonts and we
are glad to include these in the toolkit. Finally we thank Michal Kosmulski for the DarkGarden font
for and Bitstream Inc. for the Vera fonts.""")

heading2("Installation and Setup")

heading3("A note on available versions")
disc("""The latest version of the ReportLab library can be found at
^http://www.reportlab.org/downloads.html^.  Older versions can be found at ^http://www.reportlab.com/ftp/^.
  Each successive version is stored in both zip
and tgz format, but the contents are identical apart from line endings.
Versions are numbered:  $ReportLab_1_00.zip$, $ReportLab_1_01.zip$ and so on. The
latest stable version is also available as just $reportlab.zip$ (or
$reportlab.tgz$), which is actually a symbolic link to the latest
numbered version.  Daily snapshots of the trunk are available as
$current.zip$ or $current.tgz$.
Finally, from version 2.3 onwards, there is also a Windows installer
available for Python versions 2.3 - 2.6, named $ReportLab-2.x.win32-py2.x.exe$
""")


heading3("Installation on Windows")


restartList()

list("""First, install Python from $http://www.python.org/.$
Reportlab 2.x works with Python 2.3 upwards but we recommend to use
the latest stable version of Python 2.5.  
After installing, you should be able to run the
'Python (command line)' option from the Start Menu.
""")

list("""We strongly recommend installing the Python Windows
Extensions, which gives you access to Windows data sources, COM support, WinAPI calls, and the PythonWin IDE.  This
can be found at ^http://sourceforge.net/projects/pywin32/^.
Once this is installed, you can start
Pythonwin from the Start Menu and get a GUI application.
""")

list("""Install the Python Imaging Library ($PIL$) from $http://www.pythonware.com/products/pil/$.  This
step is optional but allows you to include images in your reports.
""")

list("""Now you are ready to install reportlab itself.  
The easiest way to do this is to use the .exe installer for Windows, which
installs both the ReportLab source code and the precompiled DLLs for you.
""")

list("""
If, however, you wish to install from source, download and unzip the archive
from http://www.reportlab.org/downloads.html and copy the $reportlab$ directory
onto your PythonPath;  You should now be able to go to a Python
command line interpreter and type $import reportlab$ without getting
an error message.
""")

list("""Next, Download the zip file of precompiled DLLs for your Python version from
the bottom of the ^http://www.reportlab.org/downloads.html^ downloads page, and unzip
them into ^C:\Python2x\lib\site-packages^ (or its equivalent for other Python versions
""")

list("""Open up a $MS-DOS$ command prompt and CD to
"$reportlab\\..\\tests$".  Enter "$runAll.py$". You should see lots of dots
and no error messages.  This will also create many PDF files and generate
the manuals in ^reportlab/docs^ (including this one). """)

list("""
Finally, we recommend you download and run the script ^rl_check.py^ from
^http://www.reportlab.org/ftp/^. This will health-check all the above
steps and warn you if anything is missing or mismatched.""")

heading3("Installation instructions for Unix")
disc("""
     
""")

restartList()
list("""First, install Python.  On a large number of Unix and Linux distributions, Python is already installed,
or is available as a standard package you can install with the relevant package manager.""")

list("""
    You will also need to install the Freetype 2 Font Engine, Python Imaging Library, and the gzip library,
    along with a C compiler.
""")

list("""You will also need the source code or relevant dev packages for Python and the FreeType 2 Font engine.
""")

list("""
Download the latest ReportLab.tgz from the download page on http://www.reportlab.org.
""")

list("""
Unpack the archive and follow the instructions in INSTALL.txt.
""")

list("""You should now be able to run python and execute the python statement
$import reportlab$ without errors.
""")

heading3("Instructions for Python novices: Mac")
disc("""
This is much, much easier with Mac OS X since Python is installed on your
system as standard.   Just follow the instructions for installing the ReportLab archive
above.
""")


heading2("Getting Involved")
disc("""ReportLab is an Open Source project.  Although we are
a commercial company we provide the core PDF generation
sources freely, even for commercial purposes, and we make no income directly
from these modules.  We also welcome help from the community
as much as any other Open Source project.  There are many
ways in which you can help:""")

bullet("""General feedback on the core API. Does it work for you?
Are there any rough edges?  Does anything feel clunky and awkward?""")

bullet("""New objects to put in reports, or useful utilities for the library.
We have an open standard for report objects, so if you have written a nice
chart or table class, why not contribute it?""")

bullet("""Demonstrations and Case Studies: If you have produced some nice
output, send it to us (with or without scripts).  If ReportLab solved a
problem for you at work, write a little 'case study' and send it in.
And if your web site uses our tools to make reports, let us link to it.
We will be happy to display your work (and credit it with your name
and company) on our site!""")

bullet("""Working on the core code:  we have a long list of things
to refine or to implement.  If you are missing some features or
just want to help out, let us know!""")

disc("""The first step for anyone wanting to learn more or
get involved is to join the mailing list.  To Subscribe visit
$http://two.pairlist.net/mailman/listinfo/reportlab-users$.
From there you can also browse through the group's archives
and contributions.  The mailing list is
the place to report bugs and get support. """)


heading2("Site Configuration")
disc("""There are a number of options which most likely need to be configured globally for a site.
The python script module $reportlab/rl_config.py$ may be edited to change the values of several
important sitewide properties.""")
bullet("""verbose: set to integer values to control diagnostic output.""")
bullet("""shapeChecking: set this to zero to turn off a lot of error checking in the graphics modules""")
bullet("""defaultEncoding: set this to WinAnsiEncoding or MacRomanEncoding.""")
bullet("""defaultPageSize: set this to one of the values defined in reportlab/lib/pagesizes.py; as delivered
it is set to pagesizes.A4; other values are pagesizes.letter etc.""")
bullet("""defaultImageCaching: set to zero to inhibit the creation of .a85 files on your
hard-drive. The default is to create these preprocessed PDF compatible image files for faster loading""")
bullet("""T1SearchPath: this is a python list of strings representing directories that
may be queried for information on Type 1 fonts""")
bullet("""TTFSearchPath: this is a python list of strings representing directories that
may be queried for information on TrueType fonts""")
bullet("""CMapSearchPath: this is a python list of strings representing directories that
may be queried for information on font code maps.""")
bullet("""showBoundary: set to non-zero to get boundary lines drawn.""")
bullet("""ZLIB_WARNINGS: set to non-zero to get warnings if the Python compression extension is not found.""")
bullet("""pageComression: set to non-zero to try and get compressed PDF.""")
bullet("""allowtableBoundsErrors: set to 0 to force an error on very large Platypus table elements""")
bullet("""emptyTableAction: Controls behaviour for empty tables, can be 'error' (default), 'indicate' or 'ignore'.""")



heading2("Learning More About Python")

disc("""
If you are a total beginner to Python, you should check out one or more from the
growing number of resources on Python programming. The following are freely
available on the web:
""")


bullet("""<b>Introductory Material on Python.  </b>
A list of tutorials on the Python.org web site.
$http://www.python.org/doc/Intros.html$
""")


bullet("""<b>Python Tutorial.  </b>
The official Python Tutorial by Guido van Rossum (edited by Fred L. Drake, Jr.)
$http://www.python.org/doc/tut/$
""")


bullet("""<b>Learning to Program.  </b>
A tutorial on programming by Alan Gauld. Has a heavy emphasis on
Python, but also uses other languages.
$http://www.freenetpages.co.uk/hp/alan.gauld/$
""")


bullet("""<b>How to think like a computer scientist</b> (Python version)</b>.
$http://www.ibiblio.org/obp/thinkCSpy/$
""")


bullet("""<b>Instant Python</b>.
A 6-page minimal crash course by Magnus Lie Hetland.
$http://www.hetland.org/python/instant-python.php$
""")


bullet("""<b>Dive Into Python</b>.
A free Python tutorial for experienced programmers.
$http://diveintopython.org/$
""")


from reportlab.lib.codecharts import SingleByteEncodingChart
from tools.docco.stylesheet import getStyleSheet
styles = getStyleSheet()
indent0_style = styles['Indent0']
indent1_style = styles['Indent1']

heading2("What's New in ReportLab 2.0")
disc("""
Many new features have been added, foremost amongst which is the support
for unicode. This page documents what has changed since version 1.20.""")

disc("""
Adding full unicode support meant that we had to break backwards-compatibility,
so old code written for ReportLab 1 will sometimes need changes before it will
run correctly with ReportLab 2. Now that we have made the clean break to
introduce this important new feature, we intend to keep the API
backwards-compatible throughout the 2.* series.
""")
heading3("Goals for the 2.x series")
disc("""
The main rationale for 2.0 was an incompatible change at the character level:
to properly support Unicode input. Now that it's out we will maintain compatibility
with 2.0. There are no pressing feature wishlists and new features will be driven,
as always, by contributions and the demands of projects.""")

disc("""
Our 1.x code base is still Python 2.1 compatible. The new version lets us move forwards
with a baseline of Python 2.4 (2.3 will work too, for the moment, but we don't promise
that going forwards) so we can use newer language features freely in our development.""")

disc("""
One area where we do want to make progress from release to release is with documentation
and installability. We'll be looking into better support for distutils, setuptools,
eggs and so on; and into better examples and tools to help people learn what's in the
(substantial) code base.""")

disc("""
Bigger ideas and more substantial rewrites are deferred to Version 3.0, with no particular
target dates.
""")

heading3("Contributions")
disc("""Thanks to everybody who has contributed to the open-source toolkit in the run-up
to the 2.0 release, whether by reporting bugs, sending patches, or contributing to the
reportlab-users mailing list. Thanks especially to the following people, who contributed
code that has gone into 2.0: Andre Reitz, Max M, Albertas Agejevas, T Blatter, Ron Peleg,
Gary Poster, Steve Halasz, Andrew Mercer, Paul McNett, Chad Miller.
""")
todo("""If we missed you, please let us know!""")

heading3("Unicode support")
disc("""
This is the Big One, and the reason some apps may break. You must now pass in text either
in UTF-8 or as unicode string objects. The library will handle everything to do with output
encoding. There is more information on this below.
Since this is the biggest change, we'll start by reviewing how it worked in the past.""")

disc("""
In ReportLab 1.x, any string input you passed to our APIs was supposed to be in the same
encoding as the font you selected for output. If using the default fonts in Acrobat Reader
(Helvetica/Times/Courier), you would have implicitly used WinAnsi encoding, which is almost
exactly the same as Latin-1. However, if using TrueType fonts, you would have been using UTF-8.""")

disc("""For Asian fonts, you had a wide choice of encodings but had to specify which one
(e.g Shift-JIS or EUC for Japanese). This state of affairs meant that you had
to make sure that every piece of text input was in the same encoding as the font used
to display it.""")



disc("""Input text encoding is UTF-8 or Python Unicode strings""")
disc("""
Any text you pass to a canvas API (drawString etc.), Paragraph or other flowable
constructor, into a table cell, or as an attribute of a graphic (e.g. chart.title.text),
is supposed to be unicode. If you use a traditional Python string, it is assumed to be UTF-8.
If you pass a Unicode object, we know it's unicode.""", style=indent1_style)

disc("""Font encodings""")
disc("""
Fonts still work in different ways, and the built-in ones will still use WinAnsi or MacRoman
internally while TrueType will use UTF-8. However, the library hides this from you; it converts
as it writes out the PDF file. As before, it's still your job to make sure the font you use has
the characters you need, or you may get either a traceback or a visible error character.""",style=indent1_style)

disc("""Asian CID fonts""")
disc("""
You no longer need to specify the encoding for the built-in Asian fonts, just the face name.
ReportLab knows about the standard fonts in Adobe's Asian Language Packs
""", style=indent1_style)

disc("""Asian Truetype fonts""")
disc("""
The standard Truetype fonts differ slightly for Asian languages (e.g msmincho.ttc).
These can now be read and used, albeit somewhat inefficiently. 
""", style=indent1_style)

disc("""Asian word wrapping""")
disc("""
Previously we could display strings in Asian languages, but could not properly
wrap paragraphs as there are no gaps between the words. We now have a basic word wrapping
algorithm.
""", style=indent1_style)

disc("""unichar tag""")
disc("""
A convenience tag, &lt;unichar/&gt; has also been added. You can now do <unichar code="0xfc"/>
or &lt;unichar name='LATIN SMALL LETTER U WITH DIAERESIS'/&gt; and
get a lowercase u umlaut. Names should be those in the Unicode Character Database.
""", style=indent1_style)

disc("""Accents, greeks and symbols""")
disc("""
The correct way to refer to all non-ASCII characters is to use their unicode representation.
This can be literal Unicode or UTF-8. Special symbols and Greek letters (collectively, "greeks")
inserted in paragraphs using the greek tag (e.g. &lt;greek&gt;lambda&lt;/greek&gt;) or using the entity
references (e.g. &lambda;) are now processed in a different way than in version 1.""", style=indent1_style)
disc("""
Previously, these were always rendered using the Zapf Dingbats font. Now they are always output
in the font you specified, unless that font does not support that character. If the font does
not support the character, and the font you specified was an Adobe Type 1 font, Zapf Dingbats
is used as a fallback. However, at present there is no fallback in the case of TTF fonts.
Note that this means that documents that contain greeks and specify a TTF font may need
changing to explicitly specify the font to use for the greek character, or you will see a black
square in place of that character when you view your PDF output in Acrobat Reader.
""", style=indent1_style)

# Other New Features Section #######################
heading3("Other New Features")
disc("""PDF""")
disc("""Improved low-level annotation support for PDF "free text annotations"
""", style=indent0_style)
disc("""FreeTextAnnotation allows showing and hiding of an arbitrary PDF "form"
(reusable chunk of PDF content) depending on whether the document is printed or
viewed on-screen, or depending on whether the mouse is hovered over the content, etc.
""", style=indent1_style)

disc("""TTC font collection files are now readable"
""", style=indent0_style)
disc("""ReportLab now supports using TTF fonts packaged in .TTC files""", style=indent1_style)

disc("""East Asian font support (CID and TTF)""", style=indent0_style)
disc("""You no longer need to specify the encoding for the built-in Asian fonts,
just the face name. ReportLab knows about the standard fonts in Adobe's Asian Language Packs.
""", style=indent1_style)

disc("""Native support for JPEG CMYK images""", style=indent0_style)
disc("""ReportLab now takes advantage of PDF's native JPEG CMYK image support,
so that JPEG CMYK images are no longer (lossily) converted to RGB format before including
them in PDF.""", style=indent1_style)


disc("""Platypus""")
disc("""Link support in paragraphs""", style=indent0_style)
disc("""
Platypus paragraphs can now contain link elements, which support both internal links
to the same PDF document, links to other local PDF documents, and URL links to pages on
the web. Some examples:""", style=indent1_style) 
disc("""Web links:""", style=indent1_style)
disc("""&lt;link href="http://www.reportlab.com/"&gt;ReportLab&lt;link&gt;""", style=styles['Link'])

disc("""Internal link to current PDF document:""", style=indent1_style)
disc("""&lt;link href="summary"&gt;ReportLab&lt;link&gt;""", style=styles['Link'])

disc("""External link to a PDF document on the local filesystem:""", style=indent1_style)
disc("""&lt;link href="pdf:C:/john/report.pdf"&gt;ReportLab&lt;link&gt;""", style=styles['Link'])

disc("""Improved wrapping support""", style=indent0_style)
disc("""Support for wrapping arbitrary sequence of flowables around an image, using
reportlab.platypus.flowables.ImageAndFlowables (similar to ParagraphAndImage)."""
,style=indent1_style)

disc("""KeepInFrame""", style=indent0_style)
disc("""Sometimes the length of a piece of text you'd like to include in a fixed piece
of page "real estate" is not guaranteed to be constrained to a fixed maximum length.
In these cases, KeepInFrame allows you to specify an appropriate action to take when
the text is too long for the space allocated for it. In particular, it can shrink the text
to fit, mask (truncate) overflowing text, allow the text to overflow into the rest of the document,
or raise an error.""",style=indent1_style)


disc("""Improved convenience features for inserting unicode symbols and other characters
""", style=indent0_style)
disc("""<unichar/> lets you conveniently insert unicode characters using the standard long name
or code point. Characters inserted with the &lt;greek&gt; tags (e.g. <greek>lambda</greek>) or corresponding
entity references (e.g. &lambda;) support arbitrary fonts (rather than only Zapf Dingbats).""",style=indent1_style)

disc("""Improvements to Legending""", style=indent0_style)
disc("""Instead of manual placement, there is now a attachment point (N, S, E, W, etc.), so that
the legend is always automatically positioned correctly relative to the chart. Swatches (the small
sample squares of colour / pattern fill sometimes displayed in the legend) can now be automatically
created from the graph data. Legends can now have automatically-computed totals (useful for
financial applications).""",style=indent1_style)

disc("""More and better ways to place piechart labels""", style=indent0_style)
disc("""New smart algorithms for automatic pie chart label positioning have been added.
You can now produce nice-looking labels without manual positioning even for awkward cases in
big runs of charts.""",style=indent1_style)

disc("""Adjustable piechart slice ordering""", style=indent0_style)
disc("""For example. pie charts with lots of small slices can be configured to alternate thin and
thick slices to help the lagel placememt algorithm work better.""",style=indent1_style)
disc("""Improved spiderplots""", style=indent0_style)


# Noteworthy bug fixes Section #######################
heading3("Noteworthy bug fixes")
disc("""Fixes to TTF splitting (patch from Albertas Agejevas)""")
disc("""This affected some documents using font subsetting""", style=indent0_style)

disc("""Tables with spans improved splitting""")
disc("""Splitting of tables across pages did not work correctly when the table had
row/column spans""", style=indent0_style)

disc("""Fix runtime error affecting keepWithNext""")
