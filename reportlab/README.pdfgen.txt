Unpack reportlab.zip to some directory, say d:\ReportLab.

Create a .pth file, say reportlab.pth in your Python
home directory. It should have one line:
d:/ReportLab

Then reportlab.pdfbase, reportlab.pdfgen and reportlab.platypus are available packages.

Modifying existing code to work with the package structure:

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
