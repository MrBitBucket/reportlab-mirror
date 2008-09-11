#copyright ReportLab Inc. 2000-2008
#see LICENSE.txt for license details

This is the ReportLab PDF Library.
It allows rapid creation of rich PDF documents,
and also creation of charts in a variety of bitmap
and vector formats.


Licensing
=========
BSD license.  See LICENSE.txt for details


Installation
============
This should now (Sep 2008) be distutils-compliant. Installation
depends which distribution you are using.


(1). Subversion or source distributions:

Use
   python setup.py install

This assumes you have a C compiler and the necessary
packages to build Python extensions.  On Ubuntu, you
will need at least build-essentials and python-devel.
Most other Linux and xBSD distributions have packages with
similar names.
On Windows you need the correct version of Visual Studio
for the Python you are using.

(2) Manual installation without C compiler (e.g. Windows):

- either place the src/ folder on your path, or move
the 'reportlab' package inside it to somewhere on your
path such as site-packages

- Optional: on Win32, get the DLLs for your Python version from
here and copy them into site-packages.  The library can
make PDFs without these but will go slower and lack
bitmap image generation capabilities.
   http://www.reportlab.org/ftp/win32-dlls/

(3) setuptools / easy-install 

We also have a setuptools-based setup script, setup_egg.py,
contributed by Dirk Holtwick.  It does not yet build the
C extensions.  We welcome contributions to improve this
for future releases.

(4) Binary distributions (e.g. windows .exe)
We are starting to experiment with these.  At the time of the
writing (Sep 11 2008), distutils builds self-installing EXEs.
As and when these get built they will appear at
http://www.reportlab.org/downloads.


Prerequisites / dependencies
============================
This works with Python 23, 2.4 and 2.5.
2.6 is not tested yet but you are welcome to try.

There are no absolute prerequisites beyond the Python
standard library; but the Python Imaging Library (PIL)
is needed to include images other than JPG inside PDF files.

The C extension are optional but anyone able to do so should
use _rl_accel as it helps achieve acceptable speeds.  The
_renderPM extension allows graphics (such as charts) to be saved
as bitmap images for the web, as well as inside PDFs.


Documentation
=============
Naturally, we generate our own manuals using the library.
In a 'built' distribution, they may already be present in the
docs/ directory.  If not, execute "python genAll.py" in
that directory, and it will create the manuals.


Acknowledgements and Thanks
===========================
lib/normalDate.py originally by Jeff Bauer

(this section needs updating badly! Many, many contributors
between 2000 and 2008 - please let us know your names)

setup_egg script and utilities contributed by Dirk Holtwick

