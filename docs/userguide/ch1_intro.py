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

heading2("What is ReportLab all about")
disc("""The ReportLab library is the foundation for a new generation of reporting
tools.  It was written out of frustration with the limitations of conventional
approaches to reporting and database publishing, and in the realisation that
tools such as PDF and Python made a better approach possible.
""")

disc("""Most existing reporting tools suffer from a number of constraints:""")
bullet("They assume the data is coming from a relational database")
bullet("They impose constraints on the output - you have to work the way they want")
bullet("""They go to the printer; getting electronic documents out requires
extra products such as Acrobat Distiller and a more complex workflow""")
bullet("They usually run on Windows")
bullet("""They don't give you any way to re-use visual elements across a family
of reports""")
bullet("They are slow!")

disc("""For these reasons, companies doing high-end database publishing or
high-volume customer documents have generally selected expensive proprietary
tools which use scripting languages to assemble data from various input
files and to provide input to some formatter.  Controlling the whole
system tends to involve export scripts, shell scripts and administrative
tools.  These systems are basically trying to do what Python was born
to do - gluing systems together and organising data.  And the languages
the vendors create generally suck.  """)

disc("""It became clear to us that putting the formatting functionality
into a general-purpose language such as Python was a much better
approach.  This would permit programmers to acquire data from anywhere
and work in a pleasant language.""")

disc("""The second realisation was that PDF itself was the natural
target, rather than any operating system's print driver.  It is
the only truly global format for electronic document storage.""")

heading2("Oh dear, I'm writing a load of crap.  I can't check this in!")



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
disc("1.  Install Python 1.5.1 or later")
disc("""2.  If you want to produce compressed PDF files (recommended),
check zlib is installed.""")
disc("""3.  If you want to work with bitmap images, install and
test the Python Imaging Library""")
disc("""4.  Unzip the reportlab package (reportlab.zip
or reportlab.tgz) into a directory on your path""")
disc("")
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

heading2("Detailed Instructions")
disc("""This section assumes you
don't know much about Python.  We cover all of the steps for three
common platforms, including how to verify that each one is complete.
While this may seem like a long list, everything takes 5 minutes if
you have the binaries at hand.""")

heading3("Windows users:")

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

list("Add the DLLs to your Python\DLLs directory")

list("""Add this directory to your path by creating …To verify,
start the command line Python and type "import Image", followed by
"import _imaging".  If you see no error messages, all is well.""")

list("""Now for reportlab itself.  Unzip the archive straight into
your Python directory; it creates a subdirectory named
"reportlab".""")

list("""Open up a DOS prompt and CD to
"..\reportlab\pdfgen\test".  On NT, enter "testpdfgen.py"; on
Win9x, enter "python testpdfgen.py".  After a couple of seconds,
the script completes and the file testpdfgen.pdf should be ready for
viewing.  If PIL is installed, there should be a "Python Powered"
image on the last page.  You’re done!""")
