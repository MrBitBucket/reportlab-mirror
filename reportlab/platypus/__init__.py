###############################################################################
#
#	ReportLab Public License Version 1.0
#
#   Except for the change of names the spirit and intention of this
#   license is the same as that of Python
#
#	(C) Copyright ReportLab Inc. 1998-2000.
#
#
# All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted, provided
# that the above copyright notice appear in all copies and that both that
# copyright notice and this permission notice appear in supporting
# documentation, and that the name of ReportLab not be used
# in advertising or publicity pertaining to distribution of the software
# without specific, written prior permission. 
# 
#
# Disclaimer
#
# ReportLab Inc. DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS,
# IN NO EVENT SHALL ReportLab BE LIABLE FOR ANY SPECIAL, INDIRECT
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#
###############################################################################
#	$Log: __init__.py,v $
#	Revision 1.8  2000/06/27 10:07:55  rgbecker
#	Added CondPageBreak
#
#	Revision 1.7  2000/06/21 12:27:42  rgbecker
#	remove UserDocTemplate, but add Andy's hook methods
#	
#	Revision 1.6  2000/06/19 23:51:23  andy_robinson
#	Added UserDocTemplate class, and paragraph.getPlainText()
#	
#	Revision 1.5  2000/06/01 15:23:06  rgbecker
#	Platypus re-organisation
#	
#	Revision 1.4  2000/02/17 02:09:05  rgbecker
#	Docstring & other fixes
#	
#	Revision 1.3  2000/02/15 17:55:59  rgbecker
#	License text fixes
#	
#	Revision 1.2  2000/02/15 15:47:09  rgbecker
#	Added license, __version__ and Logi comment
#	
__version__=''' $Id: __init__.py,v 1.8 2000/06/27 10:07:55 rgbecker Exp $ '''
__doc__=''
from reportlab.platypus.flowables import Flowable, Image, Macro, PageBreak, Preformatted, Spacer, XBox, \
						CondPageBreak
from reportlab.platypus.paragraph import Paragraph, cleanBlockQuotedText
from reportlab.platypus.paraparser import ParaFrag
from reportlab.platypus.tables import Table, TableStyle, CellStyle
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import BaseDocTemplate, NextPageTemplate, PageTemplate, ActionFlowable, \
						SimpleDocTemplate, FrameBreak
