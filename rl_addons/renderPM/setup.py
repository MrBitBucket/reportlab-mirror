#!/usr/bin/env python
import os, sys, string
def libart_version():
	K = ('LIBART_MAJOR_VERSION','LIBART_MINOR_VERSION','LIBART_MICRO_VERSION')
	D = {}
	for l in open('libart_lgpl/configure.in','r').readlines():
		l = string.split(string.strip(l),'=')
		if len(l)>1 and string.strip(l[0]) in K:
			D[string.strip(l[0])] = string.strip(l[1])
			if len(D)==3: break
	return (sys.platform == 'win32' and '\\"%s\\"' or '"%s"') % string.join(map(lambda k,D=D: D.get(k,'?'),K),'.')

if sys.hexversion<0x20000a0:
	import struct
	sys.byteorder = struct.pack('>L',0x12345678)==struct.pack('L',0x12345678) and 'big' or 'little'

def BIGENDIAN(macname,value=None):
	'define a macro if bigendian'
	return sys.byteorder=='big' and [(macname,value)] or []

if __name__=='__main__': #NO RUNTESTS
	import os, sys, string
	cwd = os.getcwd()
	os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
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

	LIBART_VERSION = libart_version()
	SOURCES=['_renderPM.c']
	DEVEL_DIR=os.curdir
	LIBART_DIR=pJoin(DEVEL_DIR,'libart_lgpl')
	LIBART_SRCS=glob(pJoin(LIBART_DIR, 'art_*.c'))
	GT1_DIR=pJoin(DEVEL_DIR,'gt1')
	GLIB_DIR=pJoin(DEVEL_DIR,'glib')
	if sys.platform in ['darwin', 'win32', 'sunos5', 'freebsd4', 'mac', 'linux2','linux-i386','aix4']:
		LIBS=[]
	else:
		raise ValueError, "Don't know about other systems"

	setup(	name = "_renderPM",
			version = "1.11",
			description = "Python low level render interface",
			author = "Robin Becker",
			author_email = "robin@reportlab.com",
			url = "http://www.reportlab.com",
			packages = [],
			libraries=[('_renderPM_libart',
						{
						'sources':	LIBART_SRCS,
						'include_dirs': [DEVEL_DIR,LIBART_DIR,],
						'macros': [('LIBART_COMPILATION',None),]+BIGENDIAN('WORDS_BIGENDIAN')+ROBIN_DEBUG,
						#'extra_compile_args':['/Z7'],
						}
						),
						('_renderPM_gt1',
						{
						'sources':	pfxJoin(GT1_DIR,'gt1-dict.c','gt1-namecontext.c','gt1-parset1.c','gt1-region.c','parseAFM.c'),
						'include_dirs': [DEVEL_DIR,GT1_DIR,GLIB_DIR,],
						'macros': ROBIN_DEBUG,
						#'extra_compile_args':['/Z7'],
						}
						),
						],
			ext_modules = 	[Extension(	'_renderPM',
										SOURCES,
										include_dirs=[DEVEL_DIR,LIBART_DIR,GT1_DIR],
										define_macros=[('LIBART_COMPILATION',None)]+ROBIN_DEBUG+[('LIBART_VERSION',LIBART_VERSION)],
										library_dirs=[],

										# libraries to link against
										libraries=LIBS,
										#extra_objects=['gt1.lib','libart.lib',],
										#extra_compile_args=['/Z7'],
										#extra_link_args=['/debug']
										),
							],
			)

	if sys.platform=='win32' and ('install' in sys.argv or 'install_ext' in sys.argv):
		def MovePYDs(*F):
			for x in sys.argv:
				if x[:18]=='--install-platlib=': return
			src = sys.exec_prefix
			dst = os.path.join(src,'DLLs')
			if sys.hexversion>=0x20200a0: src = os.path.join(src,'lib','site-packages')
			for f in F:
				srcf = os.path.join(src,f)
				if not os.path.isfile(srcf): continue
				dstf = os.path.join(dst,f)
				if os.path.isfile(dstf):
					os.remove(dstf)
				os.rename(srcf,dstf)
		MovePYDs('_renderPM.pyd','_renderPM.pdb')
