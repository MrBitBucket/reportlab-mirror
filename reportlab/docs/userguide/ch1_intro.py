#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/docs/userguide/ch1_intro.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/docs/userguide/ch1_intro.py,v 1.14 2003/09/08 14:16:37 andy_robinson Exp $
from reportlab.tools.docco.rl_doc_utils import *
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

disc("""After working your way through this, you should be ready to begin
writing programs to produce sophisticated reports.
""")

disc("""In this chapter, we will cover the groundwork:""")
bullet("What is ReportLab all about, and why should I use it?")
bullet("What is Python?")
bullet("How do I get everything set up and running?")

todo("""
Be warned! This document is a work in progress.  We need your help to
make sure it is complete and helpful.  Please send any feedback to our
user mailing list, reportlab-users@reportlab.com.
""")

heading2("What is ReportLab?")
disc("""ReportLab is a software library that lets you directly
create documents in Adobe's Portable Document Format (PDF) using
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
disc("""<para lindent=+36>
<b>python</b>, (<i>Gr. Myth.</i> An enormous serpent that lurked in the cave of Mount Parnassus and was slain
by Apollo) <b>1.</b> any of a genus of large, non-poisonous snakes of Asia, Africa and Australia that
suffocate their prey to death. <b>2.</b> popularly, any large snake that crushes its prey. <b>3.</b> totally awesome,
bitchin' very high level programming language (which in <i>our</i> exceedingly humble opinions
(for what they are worth)
wallops the snot out of all the other contenders (but your
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

heading2("Acknowledgements")
disc("""Many people have contributed to ReportLab.  We would like to thank
in particular (in approximately chronological order) Chris Lee, Magnus Lie Hetland,
Robert Kern, Jeff Bauer (who contributed normalDate.py) and Jerome Alet (numerous patches
and the rlzope demo).""")

disc("""Special thanks go to Just van Rossum for his valuable assistance with
font technicalities and the LettErrorRobot-Chrome type 1 font.""")

disc("""Marius Gedminas deserves a big hand for contributing the work on TrueType fonts and we
are glad to include these in the toolkit. Finally we thank Bigelow &amp; Holmes Inc ($design@bigelowandholmes.com$)
for Luxi Serif Regular and Ray Larabie ($http://www.larabiefonts.com$) for the Rina TrueType font.""")

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
list("""$cd$ to ^reportlab/test^ and execute $test_pdfgen_general.py$,
which will create a file 'test_pdfgen_general.pdf'.""")
list("""Execute $runAll.py$ to do a run of all the tests in this
directory, and make sure that none of them fail.""")
disc(" ")
disc("""If you have any problems, check the 'Detailed Instructions' section below.""")

heading3("A note on available versions")
disc("""The $reportlab$ library can be found at $ftp.reportlab.com$ in
the top-level directory. Each successive version is stored in both zip
and tgz format, but the contents are identical.  Versions are
numbered:  $ReportLab_1_00.zip$, $ReportLab_1_01.zip$ and so on. The
latest stable version is also available as just $reportlab.zip$ (or
$reportlab.tgz$), which is actually a symbolic link to the latest
numbered version.""")

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
Reportlab works with Python 1.5.2 upwards, but you will want something
more up to date!  Follow the links to 'Download' and get the latest
official version.  Currently this is Python 2.1 in the file
$Python-2.1.exe$. It will prompt you for a directory location, which
by default is
$C:\Program Files\Python$. This works, but we recommend entering
$C:\Python21$.  Quite often one wants to change directory into the
Python directory from a command prompt, so a path without spaces saves
a lot of typing!  After installing, you should be able to run the
'Python (command line)' option from the Start Menu.""")

list("""If on Win9x, we recommend either adding your Python directory
to the path , or copying python.exe to a location on your path, so
that you can execute Python from any directory.""")

list("""If you want a nice editing environment or might need to access
Microsoft applications, get the Pythonwin add-on package from
$http://aspn.activestate.com/ASPN/Downloads/ ActivePython/Extensions/Win32all$.
The version that works with Python 2.1 is 'win32all.exe, build 140' in
the file $win32all-140.exe$.  Once this is installed, you can start
Pythonwin from the Start Menu and get a GUI application.""")

disc("""The next step is optional and only necessary if you want to
include images in your reports; it can also be carried out later.""")

list("""Install the Python Imaging Library ($PIL$).  Follow the
directions from $http://www.python.org/sigs/image-sig/index.html$ or
get it directly from $http://www.pythonware.com/products/pil/$.
""")

list("Add the $DLL$s in $PIL$ to your $Python\DLLs$ directory")

list("""To verify,
start the Python interpreter (command line) and type $from PIL import Image$, followed by
$import _imaging$.  If you see no error messages, all is well.""")

disc("""Now you are ready to install reportlab itself.""")

list("""Unzip the archive straight into
your Python directory; it creates a subdirectory named
$reportlab$.  You should now be able to go to a Python
command line interpreter and type $import reportlab$ without getting
an error message.""")

list("""Open up a $MS-DOS$ command prompt and CD to
"$..\\reportlab\\test$".  On NT, enter "$test_pdfgen_general.py$"; on
Win9x, enter "$python test_pdfgen_general.py$".  After a couple of seconds,
the script completes and the file test_pdfgen_general.pdf should be ready for
viewing.  If PIL is installed, there should be a "Python Powered"
image on page 7.""")
list("""$test_pdfgen_general.py$ tests most of the functions that you
will need. To run all the tests and make sure that absolutely
everything works, type $runAll.py$. If none of the tests fail, you're
done!""")

disc("""
[Note: the "couple of seconds" delay in step 8 is mainly due to
compilation of the python scripts in the ReportLab package.
The next time the ReportLab modules are used the execution
will be noticeably faster because the $pyc$ compiled python
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

list("""If you are building Python yourself, unpack the sources into a
temporary directory using a tar command e.g. $tar xzvf py152.tgz$;
this will create a subdirectory called Python-1.5.2 (or whatever) cd
into this directory. Then read the file $README$! It contains the
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
the lib/site-python directory (typically /usr/local/lib/site-python) if necessary by
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
getting &amp; installing the Python Imaging Library - follow the
directions from
$http://www.python.org/sigs/image-sig/index.html$ or get it directly from
$http://www.pythonware.com/products/pil/$.""")


heading3("Instructions for Python novices: Mac")
#this stuff was provided by humbert@ls12.cs.uni-dortmund.de
#updated with stuff from EPSChartsDocs by John Precedo (7/11/2001)
disc("""
First install Python.  The latest stable release is 2.1, but it is
also possible to run Reportlab with any official Python from 1.5.2
upwards.  You get the software (ready to run) by following the link from
$http://www.python.org/download/download_mac.html$.
Currently, you should go to 'Jack's MacPython page' and download
$MacPython21active.bin$.
""")

disc("""
After a while a file should appear on your desktop called
$MacPython21Active$. This file appears in this way if the 'helper
applications' are correctly set up in your browser. If you are asked
to 'select an alternate program', choose Stuffit Expander. If you get
a dialogue saying 'The Document "MacPython21active.bin" could not be
opened, because the application program that created it could not be
found", you will have to do this manually. Find where Stuffit Expander
is located on your system (using Sherlock if you have to), and then
drag the icon for MacPython21active.bin onto Stuffit's icon. Stuffit
should then unpack it for you.
""")

disc("""
Double-click MacPython21Active. Say yes or continue to all the
defaults. This will put Python 2.1 in your applications folder. Once
you get to the 'the software was successfully installed' dialogue,
click on 'OK'. The Finder should pop up a window called Python 2.1
which contains the Python IDE, Interpreter etc with a folder
structure like this:
""")

image('Python_21.gif', 3*inch, 3*inch )


disc("""
We should now tell the OS about Python files, so you get the right
icons and so the operating system knows that  .py files are text
files. Open the File Exchange control panel. Click the Add button.
Wait for a list of applications to be generated.
""")

image('fileExchange.gif', 3*inch, 3*inch )

disc("""
If you cannot see all of the dialogue features, click 'Show Advanced
Options' and the dialogue should resemble the one above.
""")

disc("""
Enter the extension ".py". Next to 'file type', click the 'Select'
button and choose "Python Interpreter" from the list of applications.
The 'File Type' box should then show 'text' and a logo like the one
above. Fill in the same options on the right hand side as in the
illustration above. Click 'change', then close the control panel.
""")

disc("""
Now you can put Extensions in the Extensions-Folder;
which is where you should unpack the <b>reportlab.zip</b> with your
favorite unpack-utility (Stuffit also does this).
You'll get a subfolder named <b>reportlab</b>.
""")

disc("""
After this step, you have to tell the PythonInterpreter, where to look for extensions.
Start EditPythonPrefs (by double-clicking the icon).
""")
image('Python_21_HINT.gif',3*inch,3*inch)
disc("""
You should get the following modal dialog.
This is the point, where your special data goes in.
Reportlab is on the path in Extensions. So all you have to do is add
the last line
<b>$(PYTHON):Extensions</b>.
""")

image('Edit_Prefs.gif',3*inch,3*inch)

disc("""
You should find a folder under reportlab called test - inside that are
all the test scripts. For the moment, double click on the file
'test_pdfgen_general.py'. You should see a window called Python
Interpreter.Out with some text appearing in it, and after that it
should create a PDF file called 'test_pdfgen_general.pdf'. Make sure
that a PDF file actually is output, and that you can view it from
Adobe Acrobat. If this PDF file works, then you have successfully
installed both Python and the basic ReportLab package. If you want to
do a full test of everything, execute the script reportlab:test:runAll
with a double click. It runs lots of tests for a few minutes and
eventually says 'OK'.
""")


heading3("Instructions for Jython (Java implementation of Python) users")

disc("""
Please note that we are still testing ReportLab toolkit under Jython.
At the moment, it seems that most of ReportLab toolkit features work under
Jython. However, things that need OS specific features, like os.chdir()
will not work, because they're not supported by Java. This is especially
true for the set of test suites.
ReportLab toolkit has been tested under Sun's J2SDK 1.3.1. It is known that under
J2SDK 1.4.0_01 $test_pdfbase_ttfonts.py$ fails horribly with an outOfMemory
exception, probably caused by a JVM bug.
""")

disc("")

restartList()

list("""
Before installing Jython, make sure you have a supported version of
Java Virtual Machine installed. For the list of supported JVM's see
$http://www.jython.org/platform.html$
""")

list("""
To install Jython, download the setup package from $www.jython.org$ and
follow installation instructions.
""")

list("""
To set ReportLab toolkit under Jython PATH, edit $JYTHON_HOME/registry$ file
and include line that tells Jython where to look for packages. To include
ReportLab toolkit under Jython PATH, directory that contains Reportlab
should be included: $python.path=REPORTLAB_HOME_PARENT_DIR$
For example, if your Reportlab toolkit is installed under $C:\code\\reportlab$
the path line should be: $python.path=C:\\\\code$ (note two backslashes!)
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
bullet("""T1SearchPathPath: this is a python list of strings representing directories that
may be queried for information on Type 1 fonts""")
bullet("""TTFSearchPathPath: this is a python list of strings representing directories that
may be queried for information on TrueType fonts""")
bullet("""CMapSearchPathPath: this is a python list of strings representing directories that
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
disc("")

bullet("""<b>Introductory Material on Python.  </b>
A list of tutorials on the Python.org web site.
$http://www.python.org/doc/Intros.html$
""")
disc("")

bullet("""<b>Python Tutorial.  </b>
The official Python Tutorial by Guido van Rossum (edited by Fred L. Drake, Jr.)
$http://www.python.org/doc/tut/$
""")
disc("")

bullet("""<b>Learning to Program.  </b>
A tutorial on programming by Alan Gauld. Has a heavy emphasis on
Python, but also uses other languages.
$http://www.freenetpages.co.uk/hp/alan.gauld/$
""")
disc("")

bullet("""<b>How to think like a computer scientist</b> (Python version)</b>.
$http://www.ibiblio.org/obp/thinkCSpy/$
""")
disc("")

bullet("""<b>Instant Python</b>.
A 6-page minimal crash course by Magnus Lie Hetland.
$http://www.hetland.org/python/instant-python.php$
""")
disc("")

bullet("""<b>Dive Into Python</b>.
A free Python tutorial for experienced programmers.
$http://diveintopython.org/$
""")
disc("")