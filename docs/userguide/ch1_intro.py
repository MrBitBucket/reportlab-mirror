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
feedback to our user mailing list, reportlab-users@egroups.com.
""")

heading2("What is ReportLab?")
disc("""ReportLab is a software library that lets you directly
create documents in Adobe's Portabe Document Format (PDF) using
the Python programming language. """)

disc("""PDF is the global standard for electronic documents. It
supports high-quality printing yet is totally portable across
platforms, thanks to the freely available Acrobat Reader.  Any
application which previously generated hard copy reports can
benefit from making PDF documents instead; these can be archived,
emailed, placed on the web, or printed out the old-fashioned way.
However, the PDF file format is a complex
indexed binary format which is impossible to type directly.
The PDF format specification is more than 600 pages long and
PDF files must provide precise byte offsets -- a single extra
character placed anywhere in a valid PDF document can render it
invalid.
Until now, most of the world's PDF documents have been produced
by Adobe's Acrobat tools, which act as a 'print driver'.
""")

disc("""The ReportLab library directly creates PDF based on
your graphics commands.  There are no intervening steps.  Your applications
can generate reports extremely fast - sometimes orders
of magnitude faster than traditional report-writing
tools.""")

disc("""
By contrast, many other methods for generating PDF documents
involve "pipelines" of several processes, which make the generation process
slow, and very difficult to manage and maintain.
""")

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
bitchin' very high level programming language (which in <i>our</i> exceedingly humble opinions
(for what they are worth)
whallops the snot out of all the other contenders (but your
mileage may vary real soon now, as far as we know).</para>
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
The Python implementation is portable: it runs on most brands of UNIX
(including clones such as Linux), on Windows, DOS, OS/2, Mac, Amiga, DEC/VMS,
IBM operating systems, VxWorks, PSOS, ... If
your favorite system isn't listed here, it may still be supported, if there's a C
programming language compiler for it. Ask around on
comp.lang.python -- or just try compiling Python yourself. 
""")

disc("""
Python is copyrighted but <b>freely usable and distributable, even for commercial use</b>. 
The ReportLab core modules share the same copyright with the name of the copyright holder
modified.  Both packages use the "Berkeley Standard Distribution (BSD) style" free software copyright.
""")

heading2("Installation and Setup")

disc("""
Below we provide an abbreviated setup procedure for Python experts and a more
verbose procedure for people who are new to Python.
""")

heading3("Installation for experts")
disc("""First of all, we'll give you the high-speed version for experienced
Python developers:""")
list("Install Python 1.5.1 or later")
list("""If you want to produce compressed PDF files (recommended),
check that zlib is installed.""")
list("""If you want to work with bitmap images, install and
test the Python Imaging Library""")
list("""Unpack the reportlab package (reportlab.zip
or reportlab.tgz) into a directory on your path""")
list("""$cd$ to ^reportlab/pdfgen/test^ and execute $testpdfgen.py$,
which will create a file 'testpdfgen.pdf'.""")
disc(" ")
disc("""If you have any problems, check the 'Detailed Instructions' section below.""")

heading3("A note on available versions")
disc("""The $reportlab$
library can be found at $ftp.reportlab.com$ in the top-level directory.
Each successive version is stored in both zip and tgz format, but the
contents are identical.  Versions are numbered:  $ReportLab_0_85.zip$,
$ReportLab_0_86.zip$ and so on.  The latest stable version is also
available as just $reportlab.zip$ (or $reportlab.tgz$), which
is actually a symbolic link to the latest numbered version.""")

disc("""We also make nightly snapshots of our CVS 
(version control) tree available.  In
general, these are very stable because we have a comprehensive test
suite that all developers can run at any time.
New modules and functions within the overall package may be in a state
of flux, but stable features can be assumed to be stable.  If a bug is
reported and fixed, we assume people who need the fix in a hurry will
get $current.zip$""")

heading3("Instructions for novices: Windows")



disc("""This section assumes you
don't know much about Python.  We cover all of the steps for three
common platforms, including how to verify that each one is complete.
While this may seem like a long list, everything takes 5 minutes if
you have the binaries at hand.""")


restartList()

list("""Get and install Python from $http://www.python.org/.$
Follow the links to 'Download' and get the latest official
version.  Currently this is Python 1.5.2 in the file $py152.exe$.
It will prompt you for a directory location, which by default is
$C:\Program Files\Python$. This works, but we recommend entering
$C:\Python15$.  Python 1.6 will be out shortly and will adopt
$C:\Python16$ as its default; and quite often one wants to change directory into the
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

list("Install the Python Imaging Library ($PIL$).  (todo:  make up a bundle that works)")

list("Add the $DLL$s in $PIL$ to your $Python\DLLs$ directory")

list("""To verify,
start the Python interpreter (command line) and type $import Image$, followed by
$import _imaging$.  If you see no error messages, all is well.""")

disc("""Now you are ready to install reportlab itself.""")

list("""Unzip the archive straight into
your Python directory; it creates a subdirectory named
$reportlab$.  You should now be able to go to a Python
command line interpreter and type $import reportlab$ without getting
an error message.""")

list("""Open up a $MS-DOS$ command prompt and CD to
"..\\reportlab\\pdfgen\\test".  On NT, enter "testpdfgen.py"; on
Win9x, enter "python testpdfgen.py".  After a couple of seconds,
the script completes and the file testpdfgen.pdf should be ready for
viewing.  If PIL is installed, there should be a "Python Powered"
image on the last page.  You're done!""")

disc("""
[Note: the "couple of seconds" delay is mainly due to
compilation of the python scripts in the ReportLab package.
The next time the ReportLab modules are used the execution
will be noticably faster because the $pyc$ compiled python
files will be used in place of the $py$ python source files.]""")

heading3("Instructions for Python novices: Unix")

restartList()
list("""First you need to decide if you want to install the Python sources
and compile these yourself or if you only want to install a binary package
for one of the many variants of Linux or Unix. If you want to compile from
source download the latest
sources from http://www.python.org (currently the latest source is
in http://www.python.org/ftp/python/src/py152.tgz). If you wish to use
binaries
get the latest RPM or DEB or whatever package and install (or get your
super user (system administrator) to do the work).""")

list("""If you are building Python yourself, unpack the sources into a temporary directory using a tar command
e.g. $tar xzvf py152.tgz$; this will create a subdirectory called Python-1.5.2
(or whatever) cd into this directory. Then read the file $README$! It contains the 
latest information on how to install Python.""")

list("""If your system has the gzip libz library installed
check that the zlib extension will be installed by default by editing
the file Modules/Setup.in and ensuring that (near line 405) the line
containing zlib zlibmodule.c is uncommented i.e. has no hash '#' character at the
beginning. You also need to decide if you will be installing in the default location
(/usr/local/) or in some other place.
The zlib module is needed if you want compressed PDF and for some images.""")

list("""Invoke the command $./configure --prefix=/usr/local$ this should configure
the source directory for building. Then you can build the binaries with
a $make$ command. If your $make$ command is not up to it try building
with $make MAKE=make$. If all goes well install with $make install$.""")

list("""If all has gone well and python is in the execution search path
you should now be able to type $python$ and see a <b>Python</b> prompt.
Once you can do that it's time to try and install ReportLab.
First get the latest reportlab.tgz.
If ReportLab is to be available to all then the reportlab archive should be unpacked in
the lib/site-python directory (typically /usr/local/lib/site-python) if neccessary by
a superuser.
Otherwise unpack in a directory of your choice and arrange for that directory to be on your
$PYTHONPATH$ variable.
""")
eg("""
#put something like this in your
#shell rcfile
PYTHONPATH=$HOME/mypythonpackages
export PYTHONPATH
""",after=0.1)

list("""You should now be able to run python and execute the python statement
""",doBullet=0)
eg("""import reportlab""",after=0.1)
list("""If you want to use images you should certainly consider
getting &amp; installing the Python Imaging Library from
<font color=blue>http://www.pythonware.com/products/pil</font>.
""")

heading3("Instructions for Python novices: Mac")

todo("[Earth to Just van Rossum, come in Just!?]")

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
get involved is to join the mailing list.  Just send an email
with the subject "Subscribe" to
$reportlab-users-subscribe@egroups.com$.  You can also browse
through the group's archives and contributions at
$http://www.egroups.com/group/reportlab-users$.  This list is
the place to report bugs and get support. """)

