#!/usr/bin/env python
#copyright ReportLab Inc. 2000-2002
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/rl_addons/pyRXP/setup.py?cvsroot=reportlab
#$Header: /tmp/reportlab/rl_addons/pyRXP/setup.py,v 1.4 2002/04/12 11:22:47 rgbecker Exp $
if __name__=='__main__': #NO RUNTESTS
	import os, sys
	from distutils.core import setup, Extension

	def raiseConfigError(msg):
		import exceptions 
		class ConfigError(exceptions.Exception): 
			pass 
		raise ConfigError(msg)

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
	elif sys.platform in ("freebsd4", "darwin", "mac"):
		LIBS=[]
	else:
		msg = "Don't know about system %s" % sys.platform
		if int(os.environ.get('LIBERROR',1)): 
			raiseConfigError(msg+'\nset environment LIBERROR=0 to try no extra libs')
		else:
			print msg
			LIBS=[]


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
