#!/usr/bin/env python
#copyright ReportLab Inc. 2000-2002
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/rl_addons/pyRXP/setup.py?cvsroot=reportlab
#$Header: /tmp/reportlab/rl_addons/pyRXP/setup.py,v 1.7 2003/04/03 00:07:51 rgbecker Exp $
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

	# We copy the rxp source - we need to build it a second time for uRXP
	# with different compile time flags
	RXPUDIR=os.path.join('build','_pyRXPU')
	RXPDIR='rxp'
	if os.path.exists(RXPUDIR):
		shutil.rmtree(RXPUDIR)
	os.makedirs(RXPUDIR)
	RXPLIBSOURCES=[]
	uRXPLIBSOURCES=[]
	for f in ('xmlparser.c', 'url.c', 'charset.c', 'string16.c', 'ctype16.c', 
                'dtd.c', 'input.c', 'stdio16.c', 'system.c', 'hash.c', 
                'version.c', 'namespaces.c', 'http.c'):
		RXP_file = os.path.join(RXPDIR,f)
		uRXP_file = os.path.join(RXPUDIR,f.replace('.','U.'))
		RXPLIBSOURCES.append(RXP_file)
		shutil.copy2(RXP_file,uRXP_file)
		uRXPLIBSOURCES.append(uRXP_file)
	pyRXPU_c = os.path.join(RXPUDIR,'pyRXPU.c')
	shutil.copy2('pyRXP.c',pyRXPU_c)
	uRXPLIBSOURCES.append(pyRXPU_c)

	if sys.platform=="win32":
		LIBS=['wsock32']
	elif sys.platform=="sunos5":
		LIBS=['nsl', 'socket', 'dl']
	elif sys.platform=="aix4":
		LIBS=['nsl_r', 'dl']
	elif sys.platform in ("freebsd4", "darwin", "mac", "linux2"):
		LIBS=[]
	else:
		msg = "Don't know about system %s" % sys.platform
		if int(os.environ.get('LIBERROR',1)): 
			raiseConfigError(msg+'\nset environment LIBERROR=0 to try no extra libs')
		else:
			print msg
			LIBS=[]

	setup(	name = "pyRXP",
			version = VERSION,
			description = "Python RXP interface - fast validating XML parser",
			author = "Robin Becker",
			author_email = "robin@reportlab.com",
			url = "http://www.reportlab.com",
			packages = [],
			ext_modules = 	[Extension(	'pyRXP',
										['pyRXP.c']+RXPLIBSOURCES,
										include_dirs=[RXPDIR],
										define_macros=[('CHAR_SIZE', 8),],
										library_dirs=[],
										# libraries to link against
										libraries=LIBS,
										),
							Extension(	'pyRXPU',
										uRXPLIBSOURCES,
										include_dirs=[RXPDIR],
										define_macros=[('CHAR_SIZE', 16),],
										library_dirs=[],
										# libraries to link against
										libraries=LIBS,
										),
							],
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

	if sys.platform=='win32' and ('install' in sys.argv or 'install_ext' in sys.argv):
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
		MovePYDs('pyRXPU.pyd',)
