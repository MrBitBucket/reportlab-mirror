#!/usr/bin/env python
if __name__=='__main__': #NO RUNTESTS
	import os, sys
	ROBIN_DEBUG=[('ROBIN_DEBUG',None)]
	ROBIN_DEBUG=[]
	from glob import glob
	from distutils.core import setup, Extension
	pJoin=os.path.join
	def pfxJoin(pfx,*N):
		R=[]
		for n in N:
			R.append(pJoin(pfx,n))
		return R

	SOURCES=['_renderPM.c']
	DEVEL_DIR=os.curdir
	LIBART_DIR=pJoin(DEVEL_DIR,'libart_lgpl')
	LIBART_SRCS=glob(pJoin(LIBART_DIR, 'art_*.c'))
	GT1_DIR=pJoin(DEVEL_DIR,'gt1')
	GLIB_DIR=pJoin(DEVEL_DIR,'glib')
	if sys.platform in ['win32', 'sunos5', 'freebsd4', 'mac', 'linux2',]:
		LIBS=[]
	else:
		raise ValueError, "Don't know about other systems"

	setup(	name = "_renderPM",
			version = "0.0",
			description = "Python low level render interface",
			author = "Robin Becker",
			author_email = "robin@reportlab.com",
			url = "http://www.reportlab.com",
			packages = [],
			libraries=[('_renderPM_libart',
						{
						'sources':	LIBART_SRCS,
						'include_dirs': [DEVEL_DIR,LIBART_DIR,],
						'macros': [('LIBART_COMPILATION',None),]+ROBIN_DEBUG,
						}
						),
						('_renderPM_gt1',
						{
						'sources':	pfxJoin(GT1_DIR,'gt1-dict.c','gt1-namecontext.c','gt1-parset1.c','gt1-region.c','parseAFM.c'),
						'include_dirs': [DEVEL_DIR,GT1_DIR,GLIB_DIR,],
						'macros': ROBIN_DEBUG,
						}
						),
						],
			ext_modules = 	[Extension(	'_renderPM',
										SOURCES,
										include_dirs=[DEVEL_DIR,LIBART_DIR,GT1_DIR],
										define_macros=[('LIBART_COMPILATION',None)]+ROBIN_DEBUG,
										library_dirs=[],

										# libraries to link against
										libraries=LIBS,
										#extra_objects=['gt1.lib','libart.lib',],
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
		MovePYDs('_renderPM.pyd')
