#ch1_intro

from genuserguide import *
import reportlab

title("User Guide")
centred('ReportLab Version ' + reportlab.Version)

nextTemplate("Normal")

########################################################################
#
#               Chapter 1
#
########################################################################


heading1("Introduction")


heading2("About this document")
disc("""This document is intended to be a conversational introduction
to the use of the ReportLab packages.  Some previous programming experience
is presumed and familiarity with the Python Programming language is
recommended.  If you are new to Python, we tell you in the next section
where to go for orientation.
""")

disc("""After working your way throught this, you should be ready to begin
writing programs to produce sophisticated reports.
""")

disc("""In this chapter, we will cover the groundwork:""")
bullet("What is ReportLab all about, and why should I use it?")
bullet("What is Python?")
bullet("How do I get everything set up and running?")

todo("""
Be warned! This document is in a <em>very</em> preliminary form.  We need
your help to make sure it is complete and helpful.  Please send any
feedback to our mailing list, reportlab-users@egroups.com.
""")

heading2("What is ReportLab?")
disc("""ReportLab is a software library lets you directly create documents
in Adobe's Portabe Document Format (PDF) using the Python programming
language. """)

disc("""PDF is the global standard for electronic documents. It
supports high-quality printing yet is totally portable across
platforms, thanks the freely available Acrobat Reader.  Any
application which previously generated hard copy reports can
benefit from making PDF documents instead; these can be archived,
emailed, placed on the web, or printed out the old-fashioned way.
However, the PDF file format (600 pages long) is a complex
indexed binary format which is impossible to write directly.
Until now, most of the world's PDF documents have been produced
by Adobe's Acrobat tools, which act as a 'print driver.
""")

disc("""The ReportLab library directly creates PDF based on
your graphics commands.  There are no intervening steps
and thus no time-consuming pipelines.  Your applications
can generate reports extremely fast - sometimes orders
of magnitude faster than traditional report-writing
tools.""")

disc("""In addition, because you are writing a program
in a powerful general purpose language, there are no
restrictions at all on where you get your data from,
how you transform it, and the the kind of output
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
disc("""<para lindent=+36>
<b>python</b>, (<i>Gr. Myth.</i> An enormous serpent that lurked in the cave of Mount Parnassus and was slain
by Apollo) <b>1.</b> any of a genus of large, non-poisonous snakes of Asia, Africa and Australia that
suffocate their prey to death. <b>2.</b> popularly, any large snake that crushes its prey. <b>3.</b> totally awesome,
bitchin' language that will someday crush the $'s out of certain <i>other</i> so-called VHLL's ;-)</para>
""")
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
The Python implementation is portable: it runs on many brands of UNIX, on Windows, DOS, OS/2, Mac, Amiga... If
your favorite system isn't listed here, it may still be supported, if there's a C compiler for it. Ask around on
comp.lang.python -- or just try compiling Python yourself. 
""")

disc("""
Python is copyrighted but <b>freely usable and distributable, even for commercial use</b>. 
""")

heading2("Installation and Setup")
heading3("Installation for experts")
disc("""First of all, we'll give you the high-speed version for experienced
Python developers:""")
list("Install Python 1.5.1 or later")
list("""If you want to produce compressed PDF files (recommended),
check zlib is installed.""")
list("""If you want to work with bitmap images, install and
test the Python Imaging Library""")
list("""Unzip the reportlab package (reportlab.zip
or reportlab.tgz) into a directory on your path""")
list("""$cd$ to ^reportlab/pdfgen/test^ and execute $testpdfen.py$,
which will create a file 'testpdfgen.pdf'.""")
disc(" ")
disc("""If you have any problems, check the 'Detailed Instructions' section below""")

heading3("A note on available versions")
disc("""The $reportlab$
library can be found at ftp.reportlab.com in the top-level directory.
Each successive version is stored in both zip and tgz format, but the
contents are identical.  Versions are numbered:  ReportLab_0_85.zip,
ReportLab_0_86.zip and so on.  The latest stable version is also
available as just 'reportlab.zip' (or 'reportlab.tgz'), which
is actually a symbolic link to the latest numbered version.""")

disc("""We also make nightly snapshots of our CVS tree available.  In
general, these are very stable because we have a comprehensive test
suite that all developers can run at any time.  What happens is that
new modules and functions within the overall package may be in a state
of flux, but stable features can be assumed to be stable.  If a bug is
reported and fix, we assume people who need the fix in a hurry will
get $current.zip$""")

disc("""The next section assumes you
don't know much about Python.  We cover all of the steps for three
common platforms, including how to verify that each one is complete.
While this may seem like a long list, everything takes 5 minutes if
you have the binaries at hand.""")

heading3("Instructions for novices: Windows")

restartList()

list("""Get and install Python from http://www.python.org/.
Follow the links to 'Download' and get the latest official
version.  Currently this is Python 1.5.2 in the file 'py152.exe'.
It will prompt you for a directory location, which by default is
$C:\Program Files\Python$. This works, but we recommend entering
$C:\Python15$.  Python 1.6 will be out shortly and will adopt
C:\Python16 as its default; and quite often one wants to CD into the
Python directory from a command prompt, so a path without spaces saves
a lot of typing!  After installing, you should be able to run the
'Python (command line)' option from the Start Menu.""")

list("""If on Win9x, we recommend either copying python.exe to a
location on your path, or adding your Python directory to the path, so
that you can execute Python from any directory.""")

list("""If you want a nice editing environment or might need to
access Microsoft applications, get the Pythonwin add-on package from
the same page.  Once this is installed, you can start Pythonwin from
the Start Menu and get a GUI application.""")

disc("""The next step is optional and only necessary if you want to
include images in your reports; it can also be carried out later.""")

list("Install the Python Imaging Library.  (todo:  make up a bundle that works)")

list("Add the DLLs in PIL to your Python\DLLs directory")

list("""To verify,
start the command line Python and type "import Image", followed by
"import _imaging".  If you see no error messages, all is well.""")

disc("""Now for reportlab itself:""")
list("""Unzip the archive straight into
your Python directory; it creates a subdirectory named
"reportlab".  You should now be able to go to a Python
prompt and type $import reportlab$ without getting
an error message.""")

list("""Open up a DOS prompt and CD to
"..\reportlab\pdfgen\test".  On NT, enter "testpdfgen.py"; on
Win9x, enter "python testpdfgen.py".  After a couple of seconds,
the script completes and the file testpdfgen.pdf should be ready for
viewing.  If PIL is installed, there should be a "Python Powered"
image on the last page.  You're done!""")

heading3("Instructions for Python novices: Unix")
todo("""Aaron? Robin?""")

heading3("Instructions for Python novices: Mac")
todo("Just?")

heading2("Getting Involved")
disc("""ReportLab is an Open Source project.  Although we are
a commercial company, we do not have gazillions of dollars
of dot-com venture capital, and we make no income directly
from the product.  We therefore need help from the community
as much as any other Open Source project.  There are many
ways in which you can help:""")

bullet("""General feedback on the core A.P.I. Does it work for you?
are there any rough edges?  Does anything feel clunky and awkward?""")

bullet("""New objects to put in reports, or useful utilities for the library.
We have an open standard for report objects, so if you have written a nice
chart or table class, why not contribute it?""")

bullet("""Demonstrations and Case Studies: If you have produced some nice
output, send it to us (with or without scripts).  If ReportLab solved a
problem for you at work, write a little 'case study' and send it in!
And if your web site uses our tools to make reports, let us link to it!""")

bullet("""Working on the core code:  we have a long list of things
to refine or to implement.  If you are missing some features or
just want to help out, let us know!""")


disc("""The first step for anyone wanting to learn more or
get involved is to join the mailing list.  Just send an email
with the subject "Subscribe" to
$reportlab-users-subscribe@egroups.com$.  You can also browse
through the group's archives and contributions at
$http://www.egroups.com/group/reportlab-users$.  This list is
the place to report bugs and get support. """)

