#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/rl_config.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/rl_config.py,v 1.3 2001/04/05 09:30:11 rgbecker Exp $
import sys
from reportlab.lib import pagesizes
shapeChecking = 1
defaultEncoding = 'WinAnsiEncoding'		# 'WinAnsi' or 'MacRoman'
defaultPageSize=pagesizes.A4			#check in reportlab/lib/pagesizes for other possibilities

defaultImageCaching = 1					#set to zero to remove those annoying cached images

#places to search for Type 1 Font files
if sys.platform=='win32':
	T1SearchPathPath=['c:\\Program Files\\Adobe\\Acrobat 4.0\\Resource\\Font']
else:
	T1SearchPathPath=[]
