$Name:  $


Installation
============
Either unpack reportlab.zip or reportlab.tgz to some directory say
d:\ReportLab. If you can, ensure that the  line terminator style is
correct for your OS (man zip programs have a text mode option eg -a).

Create a .pth file, say reportlab.pth in your Python
home directory.  It should have one line:
d:/ReportLab.

Alternatively unpack the archive into a directory which is already on your
python path.

Then reportlab.pdfbase, reportlab.pdfgen and reportlab.platypus are
available packages.


Documentation
=============
Execute the script reportlab/pdfgen/test/testpdfgen.py.  This will
generate a PDF document which you can read; the script and document
together show how to use the low-level canvas.

Ditto for reportlab/platypus/test/testplatypus.py.  These show how 
to use the high-level page flow API.  Be warned that the latter is
subject to change.


Existing Code
=============
If you have code from before December 1999, here is how to modifying 
it to work with the package structure:

import pdfmetrics   ->  from reportlab.pdfbase import pdfmetrics
import pdfutils     ->  from reportlab.pdfbase import pdfutils
import pdfdoc       ->  from reportlab.pdfbase import pdfdoc

import pdfgeom      ->  from reportlab.pdfgen import pdfgeom

import pdfgen       ->  from reportlab.pdfgen import canvas
                    ->  from reportlab.pdfgen import pathobject
                    ->  from reportlab.pdfgen import textobject
                        then pdfgen.Canvas   -> canvas.Canvas
                        pdfgen.PDFPathObject -> pathobject.PDFPathObject
                        pdfgen.PDFTextObject -> textobject.PDFTextObject

import platypus     ->  from report.platypus import layout
                        from report.platypus import tables

Testing
=======
You can run all python scripts in directories named test or tests.
At present there are tests in reportlab/pdfgen/test, reportlab/platypus/test
and reportlab/demos/tests.

The scripts in other subdirectories of demos are fairly useful.

Other executable scripts are
	./pdfbase/pdfdoc.py
	./pdfgen/canvas.py
	./platypus/layout.py
	./platypus/tables.py
