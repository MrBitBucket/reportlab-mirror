#!/usr/bin/env python
#copyright ReportLab Inc. 2000-2002
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/rl_addons/pyRXP/setup.py?cvsroot=reportlab
#$Header: /tmp/reportlab/rl_addons/pyRXP/setup.py,v 1.10 2003/11/10 18:38:24 rgbecker Exp $
if __name__=='__main__': #NO RUNTESTS
	import os, sys, shutil, re
	from distutils.core import setup, Extension
	VERSION = re.search(r'^#\s*define\s+VERSION\s*"([^"]+)"',open('pyRXP.c','r').read(),re.MULTILINE)
	VERSION = VERSION and VERSION.group(1) or 'unknown'

    # patch distutils if it can't cope with the "classifiers" keyword
	if sys.version < '2.2.3':
		from distutils.dist import DistributionMetadata
		DistributionMetadata.classifiers = None

	def raiseConfigError(msg):
		import exceptions 
		class ConfigError(exceptions.Exception): 
			pass 
		raise ConfigError(msg)

	if sys.platform=="win32":
		LIBS=['wsock32']
	elif sys.platform=="sunos5":
		LIBS=['nsl', 'socket', 'dl']
	elif sys.platform=="aix4":
		LIBS=['nsl_r', 'dl']
	elif sys.platform in ("freebsd4", "darwin", "mac", "linux2", "linux-i386"):
		LIBS=[]
	else:
		msg = "Don't know about system %s" % sys.platform
		if int(os.environ.get('LIBERROR',1)): 
			raiseConfigError(msg+'\nset environment LIBERROR=0 to try no extra libs')
		else:
			print msg
			LIBS=[]

	rxpFiles = ('xmlparser.c', 'url.c', 'charset.c', 'string16.c', 'ctype16.c', 
                'dtd.c', 'input.c', 'stdio16.c', 'system.c', 'hash.c', 
                'version.c', 'namespaces.c', 'http.c')
	RXPLIBSOURCES=[]
	RXPDIR='rxp'
	for f in rxpFiles:
		RXPLIBSOURCES.append(os.path.join(RXPDIR,f))
	EXT_MODULES =	[Extension(	'pyRXP',
								['pyRXP.c']+RXPLIBSOURCES,
								include_dirs=[RXPDIR],
								define_macros=[('CHAR_SIZE', 8),],
								library_dirs=[],
								# libraries to link against
								libraries=LIBS,
								),
							]

	buildU = sys.version >= '2.0.0'
	if buildU:
		# We copy the rxp source - we need to build it a second time for uRXP
		# with different compile time flags
		RXPUDIR=os.path.join('build','_pyRXPU')
		if os.path.exists(RXPUDIR):
			shutil.rmtree(RXPUDIR)
		os.makedirs(RXPUDIR)
		uRXPLIBSOURCES=[]
		for f in rxpFiles:
			uRXP_file = os.path.join(RXPUDIR,f.replace('.','U.'))
			shutil.copy2(os.path.join(RXPDIR,f),uRXP_file)
			uRXPLIBSOURCES.append(uRXP_file)
		pyRXPU_c = os.path.join(RXPUDIR,'pyRXPU.c')
		shutil.copy2('pyRXP.c',pyRXPU_c)
		uRXPLIBSOURCES.append(pyRXPU_c)
		EXT_MODULES.append(Extension('pyRXPU',
						uRXPLIBSOURCES,
						include_dirs=[RXPDIR],
						define_macros=[('CHAR_SIZE', 16),],
						library_dirs=[],
						# libraries to link against
						libraries=LIBS,
						))


	setup(	name = "pyRXP",
			version = VERSION,
			description = "Python RXP interface - fast validating XML parser",
			author = "Robin Becker",
			author_email = "robin@reportlab.com",
			url = "http://www.reportlab.com",
			packages = [],
			ext_modules = EXT_MODULES,
			#license = open(os.path.join('rxp','COPYING')).read(),
            classifiers = [
				'Development Status :: 5 - Production/Stable',
				'Intended Audience :: Developers',
				'License :: OSI Approved :: ReportLab BSD derived',
				'Programming Language :: Python',
				'Programming Language :: C',
				'Operating System :: Unix',
				'Operating System :: POSIX',
				'Operating System :: Microsoft :: Windows',
				'Topic :: Software Development :: Libraries :: Python Modules',
				'Topic :: Text Processing :: Markup :: XML',
                ]
			)

	if sys.hexversion<0x2030000 and sys.platform=='win32' and ('install' in sys.argv or 'install_ext' in sys.argv):
		def MovePYDs(*F):
			for x in sys.argv:
				if x[:18]=='--install-platlib=': return
			src = sys.exec_prefix
			dst = os.path.join(src,'DLLs')
			if sys.hexversion>=0x20200a0:
				src = os.path.join(src,'Lib','site-packages')
			for f in F:
				dstf = os.path.join(dst,f)
				if os.path.isfile(dstf):
					os.remove(dstf)
				srcf = os.path.join(src,f)
				os.rename(srcf,dstf)
				print 'Renaming %s to %s' % (srcf, dstf)
		MovePYDs('pyRXP.pyd',)
		if buildU: MovePYDs('pyRXPU.pyd',)
