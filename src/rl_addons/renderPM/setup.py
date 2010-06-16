#!/usr/bin/env python
import os, sys, string, re, ConfigParser
VERSION = re.search(r'^#\s*define\s+VERSION\s*"([^"]+)"',open('_renderPM.c','r').read(),re.MULTILINE)
VERSION = VERSION and VERSION.group(1) or 'unknown'

INFOLINES=[]
def infoline(t):
	print t
	INFOLINES.append(t)

platform = sys.platform
pjoin = os.path.join
abspath = os.path.abspath
isfile = os.path.isfile
isdir = os.path.isdir
dirname = os.path.dirname
if __name__=='__main__':
	pkgDir=dirname(sys.argv[0])
else:
	pkgDir=dirname(__file__)
if not pkgDir:
	pkgDir=os.getcwd()
elif not os.path.isabs(pkgDir):
	pkgDir=os.path.abspath(pkgDir)
try:
	os.chdir(pkgDir)
except:
	infoline('!!!!! warning could not change directory to %r' % pkgDir)
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


def check_ft_lib(ft_lib):
	if sys.hexversion<0x20000a0: return ''
	return isfile(ft_lib) and ft_lib or ''

class config:
	def __init__(self):
		try:
			self.parser = ConfigParser.RawConfigParser()
			self.parser.read(pjoin('setup.cfg'))
		except:
			self.parser = None

	def __call__(self,sect,name,default=None):
		try:
			return self.parser.get(sect,name)
		except:
			return default
config = config()

def main():
	cwd = os.getcwd()
	os.chdir(dirname(abspath(sys.argv[0])))
	MACROS=[('ROBIN_DEBUG',None)]
	MACROS=[]
	from glob import glob
	from distutils.core import setup, Extension

	RENDERPM=os.getcwd()
	LIBART_DIR=pjoin(RENDERPM,'libart_lgpl')
	GT1_DIR=pjoin(RENDERPM,'gt1')
	MACROS=[('ROBIN_DEBUG',None)]
	MACROS=[]
	def libart_version():
		K = ('LIBART_MAJOR_VERSION','LIBART_MINOR_VERSION','LIBART_MICRO_VERSION')
		D = {}
		for l in open(pjoin(LIBART_DIR,'configure.in'),'r').readlines():
			l = l.strip().split('=')
			if len(l)>1 and l[0].strip() in K:
				D[l[0].strip()] = l[1].strip()
				if len(D)==3: break
		return (platform == 'win32' and '\\"%s\\"' or '"%s"') % '.'.join(map(lambda k,D=D: D.get(k,'?'),K))
	LIBART_VERSION = libart_version()
	SOURCES=[pjoin(RENDERPM,'_renderPM.c'),
				pjoin(LIBART_DIR,'art_vpath_bpath.c'),
				pjoin(LIBART_DIR,'art_rgb_pixbuf_affine.c'),
				pjoin(LIBART_DIR,'art_rgb_svp.c'),
				pjoin(LIBART_DIR,'art_svp.c'),
				pjoin(LIBART_DIR,'art_svp_vpath.c'),
				pjoin(LIBART_DIR,'art_svp_vpath_stroke.c'),
				pjoin(LIBART_DIR,'art_svp_ops.c'),
				pjoin(LIBART_DIR,'art_vpath.c'),
				pjoin(LIBART_DIR,'art_vpath_dash.c'),
				pjoin(LIBART_DIR,'art_affine.c'),
				pjoin(LIBART_DIR,'art_rect.c'),
				pjoin(LIBART_DIR,'art_rgb_affine.c'),
				pjoin(LIBART_DIR,'art_rgb_affine_private.c'),
				pjoin(LIBART_DIR,'art_rgb.c'),
				pjoin(LIBART_DIR,'art_rgb_rgba_affine.c'),
				pjoin(LIBART_DIR,'art_svp_intersect.c'),
				pjoin(LIBART_DIR,'art_svp_render_aa.c'),
				pjoin(LIBART_DIR,'art_misc.c'),
				pjoin(GT1_DIR,'gt1-parset1.c'),
				pjoin(GT1_DIR,'gt1-dict.c'),
				pjoin(GT1_DIR,'gt1-namecontext.c'),
				pjoin(GT1_DIR,'gt1-region.c'),
				]

	if platform=='win32':
		FT_LIB=os.environ.get('FREETYPE_LIB','')
		if not FT_LIB: FT_LIB=config('FREETYPE','lib','')
		if FT_LIB and not isfile(FT_LIB):
			infoline('!!!!! freetype lib %r not found' % FT_LIB)
			FT_LIB=[]
		if FT_LIB:
			FT_INC_DIR=os.environ.get('FREETYPE_INC','')
			if not FT_INC_DIR: FT_INC_DIR=config('FREETYPE','incdir')
			FT_MACROS = [('RENDERPM_FT',None)]
			FT_LIB_DIR = [dirname(FT_LIB)]
			FT_INC_DIR = [FT_INC_DIR or pjoin(dirname(FT_LIB_DIR[0]),'include')]
			FT_LIB_PATH = FT_LIB
			FT_LIB = [os.path.splitext(os.path.basename(FT_LIB))[0]]				
			if isdir(FT_INC_DIR[0]):				   
				infoline('##### installing with freetype %r' % FT_LIB_PATH)
			else:
				infoline('!!!!! freetype2 include folder %r not found' % FT_INC_DIR[0])
				FT_LIB=FT_LIB_DIR=FT_INC_DIR=FT_MACROS=[]
		else:
			FT_LIB=FT_LIB_DIR=FT_INC_DIR=FT_MACROS=[]
	else:
		FT_LIB_DIR=config('FREETYPE','libdir')
		FT_INC_DIR=config('FREETYPE','incdir')
		I,L=inc_lib_dirs()
		ftv = None
		for d in I:
			if isfile(pjoin(d, "ft2build.h")):
				ftv = 21
				FT_INC_DIR=[d,pjoin(d, "freetype2")]
				break
			d = pjoin(d, "freetype2")
			if isfile(pjoin(d, "ft2build.h")):
				ftv = 21
				FT_INC_DIR=[d]
				break
			if isdir(pjoin(d, "freetype")):
				ftv = 20
				FT_INC_DIR=[d]
				break
		if ftv:
			FT_LIB=['freetype']
			FT_LIB_DIR=L
			FT_MACROS = [('RENDERPM_FT',None)]
			infoline('# installing with freetype version %d' % ftv)
		else:
			FT_LIB=FT_LIB_DIR=FT_INC_DIR=FT_MACROS=[]
	if not FT_LIB:
		infoline('!!!!! installing without freetype no ttf, sorry!')
		infoline('!!!!! You need to install a static library version of the freetype2 software')
		infoline('!!!!! If you need truetype support in renderPM')
		infoline('!!!!! You may need to edit setup.cfg (win32)')
		infoline('!!!!! or edit this file to access the library if it is installed')

	setup(	name = "_renderPM",
			version = VERSION,
			description = "Python low level render interface",
			author = "Robin Becker",
			author_email = "robin@reportlab.com",
			url = "http://www.reportlab.com",
			packages = [],
			ext_modules = 	[
							Extension( '_renderPM',
										SOURCES,
										include_dirs=[RENDERPM,LIBART_DIR,GT1_DIR]+FT_INC_DIR,
										define_macros=FT_MACROS+[('LIBART_COMPILATION',None)]+MACROS+[('LIBART_VERSION',LIBART_VERSION)],
										library_dirs=[]+FT_LIB_DIR,

										# libraries to link against
										libraries=FT_LIB,
										#extra_objects=['gt1.lib','libart.lib',],
										#extra_compile_args=['/Z7'],
										extra_link_args=[]
										),
							],
			)

if __name__=='__main__': #NO RUNTESTS
	main()
