#!/usr/bin/env python
#copyright ReportLab Inc. 2000-2002
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/rl_addons/pyRXP/setup.py?cvsroot=reportlab
#$Header: /tmp/reportlab/rl_addons/pyRXP/setup.py,v 1.3 2002/04/01 22:38:39 rgbecker Exp $
if __name__=='__main__': #NO RUNTESTS
	import os, sys
	from distutils.core import setup, Extension

	RXPDIR='rxp'
	RXPLIBSOURCES=[]
	for f in ('xmlparser.c', 'url.c', 'charset.c', 'string16.c', 'ctype16.c', 'dtd.c',
			'input.c', 'stdio16.c', 'system.c', 'hash.c', 'version.c', 'namespaces.c', 'http.c'):
		RXPLIBSOURCES.append(os.path.join(RXPDIR,f))

	if sys.platform=="win32":
		LIBS=['wsock32']
	elif sys.platform=="sunos5":
		LIBS=['nsl', 'socket', 'dl']
	elif sys.platform=="aix4":
		LIBS=['nsl_r', 'dl']
	elif sys.platform=="freebsd4":
		LIBS=[]
	elif sys.platform=="darwin":
		LIBS=[]
	elif sys.platform=="mac":
		LIBS=[]
	else:
		print "Don't know about other systems"

	setup(	name = "pyRXP",
			version = "0.5",
			description = "Python RXP interface",
			author = "Robin Becker",
			author_email = "robin@reportlab.com",
			url = "http://www.reportlab.com",
			packages = [],
			ext_modules = 	[Extension(	'pyRXP',
										['pyRXP.c']+RXPLIBSOURCES,
										include_dirs=[RXPDIR],
										define_macros=[('CHAR_SIZE', 8)],
										library_dirs=[],

										# libraries to link against
										libraries=LIBS,
										),
							]
			)

	if sys.hexversion<0x20200a0 and sys.platform=='win32' and ('install' in sys.argv or 'install_ext' in sys.argv):
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
		MovePYDs('pyRXP.pyd',)
