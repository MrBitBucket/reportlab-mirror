Unpack pdfgen.zip to some directory, say d:\ReportLab.

Create a .pth file, say platypus.pth in your Python
home directory. It should have one line:
d:/ReportLab

Then pdfbase, pdfgen and platypus are available packages.

Modifying existing code to work with the package structure:

import pdfmetrics	->	from pdfbase import pdfmetrics
import pdfutils		->	from pdfbase import pdfutils
import pdfdoc		->	from pdfbase import pdfdoc

import pdfgeom		-> 	from pdfgen import pdfgeom

import pdfgen		->	from pdfgen import canvas
			->	from pdfgen import pathobject
			->	from pdfgen import textobject
	# then 	pdfgen.Canvas -> canvas.Canvas
	#	pdfgen.PDFPathObject ->	pathobject.PDFPathObject
	#	pdfgen.PDFTextObject ->	textobject.PDFTextObject

import platypus		->	from platypus import layout
				from platypus import tables
