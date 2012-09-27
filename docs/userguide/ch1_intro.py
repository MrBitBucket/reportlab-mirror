#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
__version__ = '$Id$'
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
which is signposted from <a href="http://www.reportlab.com/">www.reportlab.com</a>.
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
bullet("""Going from XML to PDF in one step""")


heading2("ReportLab's commercial software")
disc("""
The ReportLab library forms the foundation of our commercial solution for
PDF generation, Report Markup Language (RML).  This is available for evaluation
on our web site with full documentation.   We believe that RML is the fastest
and easiest way to develop rich PDF workflows.  You work in a markup language
at a similar level to HTML, using your favorite templating system to populate
an RML document; then call our rml2pdf API function to generate a PDF.  It's
what ReportLab staff use to build all of the solutions you can see on reportlab.com.
Key differences:
""")
bullet("""Fully documented with two manuals, a formal specification (the DTD) and extensive self-documenting tests.  (By contrast, we try to make sure the open source documentation isn't wrong, but we don't always keep up with the code)""")
bullet("""Work in high-level markup rather than constructing graphs of Python objects """)
bullet("""Requires no Python expertise - your colleagues may thank you after you've left!'""")
bullet("""Support for vector graphics and inclusion of other PDF documents""")
bullet("""Many more useful features expressed with a single tag, which would need a lot
of coding in the open source package""")
bullet("""Commercial support is included""")


disc("""
We ask open source developers to consider trying out RML where it is appropriate.
You can register on our site and try out a copy before buying.
The costs are reasonable and linked to the volume of the project, and the revenue
helps us spend more time developing this software.""")


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
disc("""Many people have contributed to ReportLab.  We would like to thank in particular 
(in alphabetical order): 
Albertas Agejevas, 
Alex Buck, 
Andre Reitz, 
Andrew Mercer, 
Benjamin Dumke,
Benn B,
Chad Miller, 
Chris Lee, 
Christian Jacobs, 
Dinu Gherman,
Eric Johnson,
Felix Labrecque,  
Gary Poster, 
Germán M. Bravo,
Guillaume Francois, 
Hans Brand,
Henning Vonbargen,
Hosam Aly,
Ian Stevens, 
James Martin-Collar, 
Jeff Bauer,
Jerome Alet,
Jerry Casiano,
Jorge Godoy,
Keven D Smith,
Magnus Lie Hetland,
Marcel Tromp, Ty Sarna
Marius Gedminas,
Max M, 
Michael Egorov,
Mike Folwell,
Moshe Wagner,
Nate Silva,
Paul McNett, 
Peter Johnson, 
PJACock,
Publio da Costa Melo,  
Randolph Bentson,
Robert Alsina,
Robert Hölzl,
Robert Kern,
Ron Peleg,
Simon King,
Steve Halasz, 
T Blatter,
Tim Roberts,
Tomasz Swiderski,
Volker Haas,
Yoann Roman, 
and many more.""")

disc("""Special thanks go to Just van Rossum for his valuable assistance with
font technicalities.""")

disc("""Moshe Wagner and Hosam Aly deserve a huge thanks for contributing to the RTL patch, which is not yet on thr trunk.""")

disc("""Marius Gedminas deserves a big hand for contributing the work on TrueType fonts and we
are glad to include these in the toolkit. Finally we thank Michal Kosmulski for the DarkGarden font
for and Bitstream Inc. for the Vera fonts.""")

heading2("Installation and Setup")

heading3("A note on available versions")
disc("""Our website ^http://www.reportlab.com/^ will always have up-to-date
information on setups and installations. The latest version of the ReportLab library can be found at
^http://www.reportlab.com/software/opensource/rl-toolkit/download/^.
Older versions can be found at ^http://www.reportlab.com/ftp/^.
""")
disc("""Each successive version is stored in both zip
and tgz format, but the contents are identical apart from line endings.
Versions are numbered:  $ReportLab_<major_version>_<minor_version>.zip$, 
$ReportLab_<major_version>_<minor_version>.tgz$ and so on.
""")
disc("""
The latest stable version is $reportlab2.6$ (.zip or .tgz). 
Daily snapshots of the trunk are available as
$reportlab-daily-unix.tar.gz$ or $reportlab-daily-win32.zip$.
""")
disc("""Finally, from version 2.4 onwards, there is also a Windows installer
available for Python versions 2.5 - 2.7, named $ReportLab-2.x.win32-py2.x.exe$
""")

pencilnote()
disc("""We plan to drop the support of Python 2.5 in our next release.
We advise you to move to Python 2.6 or 2.7.
""")

heading3("Installation on Windows")

restartList()

list("""First, install Python from $http://www.python.org/.$
Reportlab 2.x works with Python 2.5 upwards but we recommend to use
the latest stable version of Python 2.7.  
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
from from the downloads page on ^http://www.reportlab.com/^ and copy the $reportlab$ directory
onto your PythonPath;  You should now be able to go to a Python
command line interpreter and type $import reportlab$ without getting
an error message.
""")

list("""Next, Download the zip file of precompiled DLLs for your Python version from
the bottom of the downloads page on ^http://www.reportlab.com/^, and unzip
them into ^C:\Python2x\lib\site-packages^ (or its equivalent for other Python versions
""")

list("""Open up a $MS-DOS$ command prompt and CD to
"$reportlab\\..\\tests$".  Enter "$runAll.py$". You should see lots of dots
and no error messages.  This will also create many PDF files and generate
the manuals in ^reportlab/docs^ (including this one). """)

list("""
Finally, we recommend you download and run the script ^rl_check.py^ from
^http://www.reportlab.com/ftp/^. This will health-check all the above
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
Download the latest ReportLab.tgz from the download page on http://www.reportlab.com.
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

bullet("""Snippets and Case Studies: If you have produced some nice
output, register online on ^http://www.reportlab.com^ and submit a snippet
of your output (with or without scripts).  If ReportLab solved a
problem for you at work, write a little 'case study' and submit it.
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


bullet("""<b>Python Documentation.  </b>
A list of documentation on the Python.org web site.
$http://www.python.org/doc/$
""")


bullet("""<b>Python Tutorial.  </b>
The official Python Tutorial , originally written by Guido van Rossum himself.
$http://docs.python.org/tutorial/$
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
$http://www.diveintopython.net/$
""")


from reportlab.lib.codecharts import SingleByteEncodingChart
from tools.docco.stylesheet import getStyleSheet
styles = getStyleSheet()
indent0_style = styles['Indent0']
indent1_style = styles['Indent1']

heading2("Goals for the 2.x series")
disc("""The main rationale for 2.0 was an incompatible change at the character level:
to properly support Unicode input. Now that it's out we will maintain compatibility
with 2.0. There are no pressing feature wishlists and new features will be driven,
as always, by contributions and the demands of projects.""")

disc("""One area where we do want to make progress from release to release is with documentation
and installability. We'll be looking into better support for distutils, setuptools,
eggs and so on; and into better examples and tools to help people learn what's in the
(substantial) code base.""")

disc("""
Bigger ideas and more substantial rewrites are deferred to Version 3.0, with no particular
target dates.
""")

heading2("What's New in ReportLab 2.6")
disc("""This is a minor release focusing mainly on improved documentation. There are a 
number of minor enhancements, and a larger number of previous-undocumented
enhancements which we have documented better.""")

disc("""A big thanks goes to the community for their help in reporting bugs and providing patches. 
Thanks to everybody who has contributed to the open-source toolkit in the run-up to the 2.6 release, 
whether by reporting bugs, sending patches, or contributing to the reportlab-users mailing list. 
Thanks especially to the following people: Alex Buck, Felix Labrecque <felixl@densi.com>,
Peter Johnson <johnson.peter@gmail.com>, James Martin-Collar and Guillaume Francois.
This page documents what has changed since version 2.5.""")

disc('Reportlab 2.6 is installable with easy_install. You must have installed a compatible C compiler and the dependencies such as Freetype and PIL.')

heading4('General changes')
bullet("""Manuals have been reformatted with more pleasing code snippets and tables of 
contents, and reviewed and expanded.""")

heading4('Flowing documents (Platypus)')
bullet("""Added support for HTML-style list objects.""")
bullet("""Added flexible mechanism for drawing bullets.""")
bullet("""Allowed XPreformatted objects to use Asian line wrapping.""")
bullet("""Added an 'autoNextPageTemplate' attribute to PageTemplates. For example you 
can now set up a 'chapter first page template' which will always be followed
by a 'continuation template' on the next page break, saving the programmer from
having to issue control flow commands in the story.""")
bullet("""Added a TopPadder flowable, which will 'wrap' another Flowable and move it 
to the bottom of the current page.""")
bullet("""More helpful error messages when large tables cannot be rendered.""")

heading4('Charts and graphics')
bullet("""Support for UPCA bar codes.""")
bullet("""We now have a semi-intelligent system for labelling pie charts with 
callout lines.  Thanks to James Martin-Collar, a maths student at Warwick 
University, who did this as his summer internship.""")
bullet("""Axes - added startOffset and endOffset properties; allowed for axis 
background annotations.""")
bullet("""Bar charts - allow more control of z Index (i.e. drawing order of axes and
lines)""")
bullet("""Pie charts - fixed bugs in 3d appearance.""")
bullet("""SVG output back end has seen some bugs fixed and now outputs resizeable SVG.""")

# Noteworthy bug fixes Section #######################
#heading3("Noteworthy bug fixes")
