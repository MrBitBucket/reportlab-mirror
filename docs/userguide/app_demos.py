#app_demos
from genuserguide import *

Appendix1("ReportLab Demos")
disc("In the subdirectories of reportlab/demos there are a number of working examples showing
almost all aspects of reportLab in use.""")

heading2("""Odyssey""")
disc("""
The three scripts odyssey.py, dodyssey.py and fodyssey.py all take the file odyssey.txt
and produce pdf documents. The included odyssey.txt is short a longer and more testing version
can be found at ftp://ftp.reportlab.com/odyssey.full.zip.
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
