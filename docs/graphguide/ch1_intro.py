#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/docs/userguide/ch1_intro.py?cvsroot=reportlab
#$Header: /tmp/reportlab/docs/graphguide/ch1_intro.py,v 1.5 2001/03/30 17:05:23 dinu_gherman Exp $

from gengraphguide import *
import reportlab

title("Graphics Guide")
centred('ReportLab Version ' + reportlab.Version)

nextTemplate("Normal")

########################################################################
#
#               Chapter 1
#
########################################################################

heading1("Introduction")

heading2("About this document")

disc("""
This document is intended to be a conversational introduction
to the use of the ReportLab Graphics package.
As this package is a subcomponent of the general ReportLab document
toolkit some previous exposure to the content of the general "ReportLab
User Guide" is not only highly recommended, but absolutely necessary!
If you haven't read the general User Guide yet, this is the time to
do so!
""")

disc("""
After working your way throught this, you should be ready to
begin writing programs to produce reports containing graphics elements
like simple drawings and charts.
""")

# Hack to force a new paragraph before the todo() :-(
disc("")

todo("""
Be warned! This document is in a preliminary form.
We need your help to make sure it is complete and helpful.
Please send any feedback to our user mailing list,
reportlab-users@egroups.com.
""")


heading2("Background")

disc("""
The ReportLab library is a general document toolkit aiming to help
generate documents for reporting solutions.
One important aspect of such applications is to present data with
graphics like diagrams or charts.
Ideally, these graphics could be used not only to generate PDF
documents, but other output formats, bitmap or vector ones, as
well.
ReportLab is in the process of adding such a graphics package to
its standard distribution.
This document is both the "design document" and the "tutorial".
""")


heading2("Requirements")

disc("""
The graphics library should support the creation of custom
graphical applications containing charts, diagrams, drawings, plans,
etc. in various domains like business, finance, publishing, engineering
and research.
It is especially intended as a foundation for a chart library that
happens to be the first major subpackage for a real-world client
in the financial industry.
""")

disc("The general graphics package should help with the following activities: ")

bullet("creating reusable shapes collections")
bullet("supporting paths, clipping and coordinate transformations")
bullet("writing output to PDF, Postscript, bitmap and vector formats")
bullet("using a consistent font model (Type 1)")
bullet("providing identical metrics on all platforms")
bullet("""using a framework for creating, documenting and reusing graphical "widgets" """)

disc("""Within the charting domain the target features are:""")

bullet("Horizontal/vertical bar charts based on category/value axes.")
bullet("Horizontal/vertical line charts based on category/value axes.")
bullet("""Special time series charts based on genuine x/y values.""")
bullet("Simple pie charts.")
bullet("""Compounding - one can define 'multiples' placing several charts on one 
       drawing, or arbitrary decorations around the chart. This technique 
       also allows easy overlaying of lines on bars, or of different axes on 
       the right and left side of a plot.""")
bullet("""'Plug-In Architecture' - with training, you can write a new chart type
       based on an existing one but only changing/adding the features you
       need to.""")
bullet("Control over drawing size, plot rectangle size and position within drawing.")
bullet("""Control over width, dash style, line cap/join style and
       color for all lines.""")
bullet("""Choice of any solid color (or gray level, or transparent) for any
       enclosed area. Fill patterns may be added later. The public library
       will be limited to RGB and possibly plain CMYK colors but we can
       cleanly layer custom Postscript requirements on top.""")
bullet("""Control over font name (any Type 1 font on the system) and size, plus
       the ability to scale, stretch and rotate the text
       right, left and centre alignment of label text strings with correct
       metrics.""")

disc("""
The charting requirements are based on a commercial sponsor who
needs to create batches of charts rapidly with precise control over
layout.
""")
