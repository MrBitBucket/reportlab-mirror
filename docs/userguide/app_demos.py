#app_demos
from genuserguide import *

Appendix1("ReportLab Demos")
disc("""In the subdirectories of reportlab/demos there are a number of working examples showing
almost all aspects of reportLab in use.""")

heading2("""Odyssey""")
disc("""
The three scripts odyssey.py, dodyssey.py and fodyssey.py all take the file odyssey.txt
and produce pdf documents. The included odyssey.txt is short a longer and more testing version
can be found at ftp://ftp.reportlab.com/odyssey.full.zip.
""")
eg("""
Windows
cd reportlab\\demos\\odyssey
python odyssey.py
start odyssey.pdf

Linux
cd reportlab/demos/odyssey
python odyssey.py
acrord odyssey.pdf
""")
disc("""Simple formatting is illustrated by the odyssey.py script. It runs quite fast,
but all it does is gather the text and force it onto the canvas pages. It does no paragraph
manipulation at all so you get to see the XML &lt;  &amp; &gt; tags.
""")
disc("""The scripts fodyssey.py and dodussey.py handle paragraph formatting so you get
to see colour changes etc. Both scripts
use the document template class and the dodyssey.py script shows the ability to do dual column
layout and illustrates multiple page templates.
""")

heading2("""Stdfonts""")
disc("""In reportlab/demos/stdfonts the script stdfonts.py can be used to illustrate
ReportLab's standard fonts. Run the script using""")
eg("""
cd reportlab\\demos\\stdfonts
python stdfonts.py
""")
disc("""
to produce two <b>PDF</b> documents, StandardFonts_MacRoman.pdf &amp;
StandardFonts_WinAnsi.pdf which illustrate the two most common built in
font encodings.
""")
heading2("""Py2pdf""")
disc("""Dinu Gherman (<gherman@darwin.in-berlin.de>) contributed this useful script
which uses reportlab to produces nicely colorized pdf documents from python
scripts. To get a nice version of the main script try""")
eg("""
cd reportlab/demos/py2pdf
python py2pdf.py py2pdf.py
acrord py2pdf.pdf
""")
disc("""ie we used py2pdf to produce a nice version of py2pdf.py in
the document with the same rootname and a .pdf extension.
""")
