#copyright ReportLab Inc. 2000-2010
#see LICENSE.txt for license details

This is the ReportLab PDF Toolkit. It allows rapid creation 
of rich PDF documents, and also creation of charts in a variety 
of bitmap and vector formats.  

This library is also the foundation for our commercial product
Report Markup Language (RML), available in the ReportLab PLUS
package. RML offers many more features, a template-based style
of document development familiar to all web developers, and
higher development productivity.  Please consider trying out
RML for your project, as the license sales support our open
source development.


Contents of this file:
1. Licensing
2. Installation
 2.1 Source distribution or subversion
 2.2 Manual installation without C compiler
 2.3 easy_install
 2.4 Windows .exe installer 
 2.5 Ubuntu and other Debian-based systems
3. Prerequisites / dependencies
4. Documentation
5. Acknowledgments

1.Licensing
===========
BSD license.  See LICENSE.txt for details


2.Installation
==============
You need to have installed Python (versions 2.3 through 2.7),
and ideally PIL with Freetype support; more notes on prerequisites
follow below.  

We aim to be compatible with several of the popular installation
techniques - please pick your preferred one below...


2.1. Subversion or source distributions:
---------------------------------------

Use
    python setup.py install

After this has completed you should be able to run

    python setup.py tests

and see error-free output.

(Note 1: If you see a line of dots, and a small number of errors
relating to 'renderPM', it's likely that your C compiler
environment is incorrect and that the renderPM C extension
could not be installed. However, it's only needed if you
want to generate bitmap graphics - more on this below)

(Note 2: there is also an option 'python setup.py tests-preinstall', 
which will run the tests where you unpack the files; this is 
expected to fail on one or two tests involving renderPM as 
that extension has not been compiled yet.)


This assumes you have a C compiler and the necessary
packages to build Python extensions. If you are installing
system-wide you will need root permissions e.g.:

    sudo python setup.py install

On Ubuntu, you will need
build-essential, libfreetype6-dev, python-dev and python-imaging.
Most other Linux and xBSD distributions have packages with
similar names.

On Windows you need the correct version of Visual Studio
for the Python you are using.


2.2 Manual installation without C compiler (e.g. Windows):
---------------------------------------------------------

- either place the src/ folder on your path, or move
the 'reportlab' package inside it to somewhere on your
path such as site-packages

- Optional: on Win32, get the DLLs for your Python version from
here and copy them into site-packages.  The library can
make PDFs without these but will go slower and lack
bitmap image generation capabilities.
   http://www.reportlab.org/ftp/win32-dlls/


2.3 easy-install
----------------
easy_install is a popular Python deployment tool.

As of this version, you should be able to install with 
"easy_install reportlab".   We do NOT use a setuptools-based
script, but have modified our distribution to be compatible with 
easy_install.


2.4 Windows .exe installer
--------------------------
A binary .exe installer for Windows (built with distutils) is
available on our website.  


2.5 Ubuntu and other Debian-based systems
-----------------------------------------
The latest releases are generally available in the ubuntu repositories
within 2-3 weeks.  At the time of writing (20th Jan 2010) the basic
reportlab installer does not include the C extensions, so we recommend
installing these THREE packages for a full-speed, full-features installation:

    sudo apt-get install python-reportlab python-reportlab-accel python-renderpm  
    
There is also a package 'python-reportlab-doc' including the built PDF manuals,
which are also available on our website.

Alternatively, if you would rather compile from source
you will need compilers and other dependencies as follows, and can then
follow the instructions in 2.1 above...
    sudo apt-get install build-essential libfreetype6-dev python-dev python-imaging


3. Prerequisites / dependencies
===============================
This works with Python 2.3 - 2.6.
2.7 is not tested yet but you are welcome to try.

There are no absolute prerequisites beyond the Python
standard library; but the Python Imaging Library (PIL)
is needed to include images other than JPG inside PDF files.

The C extension are optional but anyone able to do so should
use _rl_accel as it helps achieve acceptable speeds.  The
_renderPM extension allows graphics (such as charts) to be saved
as bitmap images for the web, as well as inside PDFs.


4. Documentation
================
Naturally, we generate our own manuals using the library.
In a 'built' distribution, they may already be present in the
docs/ directory.  If not, execute "python genAll.py" in
that directory, and it will create the manuals.


5. Acknowledgements and Thanks
==============================
lib/normalDate.py originally by Jeff Bauer

Many, many contributors have helped out between 2000 and 2010.
we keep a list in the first chapter of the User Guide; if you
have contributed and are not listed there, please let us know.


