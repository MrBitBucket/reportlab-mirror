#!/usr/bin/env python
#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/setup.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/setup.py,v 1.8 2001/06/13 18:24:14 jvr Exp $
if __name__=='__main__': #NO RUNTESTS
	import os, sys
	from distutils.core import setup, Extension

	if sys.platform=="win32":
		LIBS=[]
	elif sys.platform=="sunos5":
		LIBS=[]
	elif sys.platform=="aix4":
		LIBS=[]
	elif sys.platform=="mac":
		LIBS=[]
	else:
		print "Don't know about other systems"

	setup(	name = "_rl_accel",
			version = "0.2",
			description = "Python Reportlab acceleretaor extensions",
			author = "Robin Becker",
			author_email = "robin@reportlab.com",
			url = "http://www.reportlab.com",
			packages = [],
			ext_modules =	[Extension(	'_rl_accel',
										['_rl_accel.c'],
										include_dirs=[],
										define_macros=[],
										library_dirs=[],
										libraries=LIBS,	# libraries to link against
										),
							Extension(	'sgmlop',
										['sgmlop.c'],
										include_dirs=[],
										define_macros=[],
										library_dirs=[],
										libraries=LIBS,	# libraries to link against
										),
							Extension(	'pyHnj',
										['pyHnjmodule.c','hyphen.c', 'hnjalloc.c'],
										include_dirs=[],
										define_macros=[],
										library_dirs=[],
										libraries=LIBS,	# libraries to link against
										),
							],
			)

	if sys.platform=='win32' and ('install' in sys.argv or 'install_ext' in sys.argv):
		def MovePYDs(*F):
			for x in sys.argv:
				if x[:18]=='--install-platlib=': return
			src = sys.exec_prefix
			dst = os.path.join(src,'DLLs')
			for f in F:
				dstf = os.path.join(dst,f)
				if os.path.isfile(dstf):
					os.remove(dstf)
				os.rename(os.path.join(src,f),dstf)
		MovePYDs('sgmlop.pyd','_rl_accel.pyd','pyHnj.pyd')
