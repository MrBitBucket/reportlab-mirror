#!/usr/bin/env python
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/utils/compress_images.py?cvsroot=reportlab
#$Header: /tmp/reportlab/utils/compress_images.py,v 1.2 2000/10/25 08:57:46 rgbecker Exp $
import sitecustomize
import sys
from reportlab.pdfbase.pdfutils import preProcessImages

for spec in sys.argv[1:]:
	preProcessImages(spec)
