#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/docs/userguide/ch1_intro.py?cvsroot=reportlab
#$Header: /tmp/reportlab/docs/graphguide/ch1_intro.py,v 1.1 2001/03/29 07:15:25 dinu_gherman Exp $

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

disc("""This document is intended to be a conversational introduction
to the use of the ReportLab Graphics package.
As this package is a subcomponent of the general ReportLab document
toolkit some previous exposure to the content of the general "ReportLab
User Guide" is not only highly recommended, but absolutely necessary!
If you haven't read the general User Guide yet, this is time to do so!
""")

disc("""After working your way throught this, you should be ready to
begin writing programs to produce reports containing graphics elements
like simple drawings and charts.
""")

todo("""
Be warned! This document is in a <em>very</em> preliminary form.
We need your help to make sure it is complete and helpful.
Please send any feedback to our user mailing list,
reportlab-users@egroups.com.
""")

