#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/platypus/__init__.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/platypus/__init__.py,v 1.13 2002/03/15 09:03:37 rgbecker Exp $
__version__=''' $Id: __init__.py,v 1.13 2002/03/15 09:03:37 rgbecker Exp $ '''
__doc__=''
from reportlab.platypus.flowables import Flowable, Image, Macro, PageBreak, Preformatted, Spacer, XBox, \
						CondPageBreak, KeepTogether
from reportlab.platypus.paragraph import Paragraph, cleanBlockQuotedText, ParaLines
from reportlab.platypus.paraparser import ParaFrag
from reportlab.platypus.tables import Table, TableStyle, CellStyle
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import BaseDocTemplate, NextPageTemplate, PageTemplate, ActionFlowable, \
						SimpleDocTemplate, FrameBreak, PageBegin
from xpreformatted import XPreformatted
