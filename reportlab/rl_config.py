#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/rl_config.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/rl_config.py,v 1.12 2001/06/26 14:45:30 andy_robinson Exp $
import sys, string
from reportlab.lib import pagesizes
shapeChecking = 1
defaultEncoding = 'WinAnsiEncoding'     # 'WinAnsi' or 'MacRoman'
pageCompression = 1                     # the default page compression mode
defaultPageSize=pagesizes.A4            #check in reportlab/lib/pagesizes for other possibilities

defaultImageCaching = 0                 #set to zero to remove those annoying cached images
PIL_WARNINGS=1                              # set to zero to avoid any warning
ZLIB_WARNINGS=1

#places to search for Type 1 Font files
if sys.platform=='win32':
    T1SearchPath=['c:\\Program Files\\Adobe\\Acrobat 4.0\\Resource\\Font']
elif sys.platform in ('linux2',):
    T1SearchPath=['/usr/lib/Acrobat4/Resource/Font']
elif sys.platform=='mac':   # we must be able to do better than this
    import os
    diskName = string.split(os.getcwd(), ':')[0]
    fontDir = diskName + ':Applications:Python 2.1:reportlab:fonts'
    T1SearchPath = [fontDir]   # tba
    PIL_WARNINGS = 0 # PIL is not packagized in the Mac Python buildelse:
    T1SearchPath=[]

_verbose=0

sys_version = string.split(sys.version)[0]  #strip off the other garbage
