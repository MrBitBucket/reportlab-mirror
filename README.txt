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
This should now (Sep 2008) be distutils-compliant.  Use
'python setup.py install' for a classic distutils
installation.

We also have a setuptools-based setup script, setup_egg.py

A minimal, pure-python-only install can be achieved
simply by placing the directory 'src/reportlab' on your
path.  It should make PDFs but will lack certain
capabilities.  

Documentation
=============
Naturally, we generate our own manuals using the library.
In a 'built' distribution, they may already be present in the
docs directory.  If not, execute "python genAll.py" in
that directory, and it will create the manuals.


Acknowledgements and Thanks
===========================
lib/normalDate.py originally by Jeff Bauer

(this section needs updating badly! Many, many contributors
between 2000 and 2008 - please let us know your names)

setup_egg script and utilities contributed by Dirk Holtwick

