#!/usr/bin/env python
import os, sys, string, re
VERSION = re.search(r'^#\s*define\s+VERSION\s*"([^"]+)"',open('_renderPM.c','r').read(),re.MULTILINE)
VERSION = VERSION and VERSION.group(1) or 'unknown'
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

def pfxJoin(pfx,*N):
	R=[]
	for n in N:
		R.append(os.path.join(pfx,n))
	return R

FT_LIB='C:/Python/devel/freetype-2.1.5/objs/freetype214.lib'
FT_INCLUDE=None
def check_ft_lib(ft_lib=FT_LIB):
	if sys.hexversion<0x20000a0: return ''
	return os.path.isfile(ft_lib) and ft_lib or ''

def main():
	cwd = os.getcwd()
	os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
	MACROS=[('ROBIN_DEBUG',None)]
	MACROS=[]
	from glob import glob
	from distutils.core import setup, Extension
	pJoin=os.path.join

	LIBART_VERSION = libart_version()
	SOURCES=['_renderPM.c']
	DEVEL_DIR=os.curdir
	LIBART_DIR=pJoin(DEVEL_DIR,'libart_lgpl')
	LIBART_SRCS=glob(pJoin(LIBART_DIR, 'art_*.c'))
	GT1_DIR=pJoin(DEVEL_DIR,'gt1')
	platform = sys.platform
	LIBS = []		#assume empty libraries list

	if os.path.isdir('/usr/local/include/freetype2'):
		FT_LIB = ['freetype']
		FT_LIB_DIR = ['/usr/local/lib']
		FT_MACROS = [('RENDERPM_FT',None)]
		FT_INC_DIR = ['/usr/local/include','/usr/local/include/freetype2']
	else:
		ft_lib = check_ft_lib()
		if ft_lib:
			FT_LIB = [os.path.splitext(os.path.basename(ft_lib))[0]]
			FT_LIB_DIR = [os.path.dirname(ft_lib)]
			FT_MACROS = [('RENDERPM_FT',None)]
			FT_INC_DIR = [FT_INCLUDE or os.path.join(os.path.dirname(os.path.dirname(ft_lib)),'include')]
		else:
			FT_LIB = []
			FT_LIB_DIR = []
			FT_MACROS = []
			FT_INC_DIR = []

	setup(	name = "_renderPM",
			version = VERSION,
			description = "Python low level render interface",
			author = "Robin Becker",
			author_email = "robin@reportlab.com",
			url = "http://www.reportlab.com",
			packages = [],
			libraries=[('_renderPM_libart',
						{
						'sources':	LIBART_SRCS,
						'include_dirs': [DEVEL_DIR,LIBART_DIR,],
						'macros': [('LIBART_COMPILATION',None),]+BIGENDIAN('WORDS_BIGENDIAN')+MACROS,
						#'extra_compile_args':['/Z7'],
						}
						),
						('_renderPM_gt1',
						{
						'sources':	pfxJoin(GT1_DIR,'gt1-dict.c','gt1-namecontext.c','gt1-parset1.c','gt1-region.c','parseAFM.c'),
						'include_dirs': [DEVEL_DIR,GT1_DIR,],
						'macros': MACROS,
						#'extra_compile_args':['/Z7'],
						}
						),
						],
			ext_modules = 	[Extension(	'_renderPM',
										SOURCES,
										include_dirs=[DEVEL_DIR,LIBART_DIR,GT1_DIR]+FT_INC_DIR,
										define_macros=FT_MACROS+[('LIBART_COMPILATION',None)]+MACROS+[('LIBART_VERSION',LIBART_VERSION)],
										library_dirs=[]+FT_LIB_DIR,

										# libraries to link against
										libraries=LIBS+FT_LIB,
										#extra_objects=['gt1.lib','libart.lib',],
										#extra_compile_args=['/Z7'],
										extra_link_args=[]
										),
							],
			)

	if sys.hexversion<0x2030000 and sys.platform=='win32' and ('install' in sys.argv or 'install_ext' in sys.argv):
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

if __name__=='__main__': #NO RUNTESTS
	main()
