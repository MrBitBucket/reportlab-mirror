#!/usr/bin/env python
#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/setup.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/setup.py,v 1.13 2002/07/17 22:46:23 andy_robinson Exp $
if __name__=='__main__': #NO RUNTESTS
    import os, sys
    from distutils.core import setup, Extension

    if sys.platform in ['win32', 'sunos5', 'freebsd4', 'aix4', 'mac', 'darwin']:
        LIBS=[]
    else:
        raise ValueError, "Don't know about platform:"+sys.platform

    setup(  name = "_rl_accel",
            version = "0.2",
            description = "Python Reportlab acceleretaor extensions",
            author = "Robin Becker",
            author_email = "robin@reportlab.com",
            url = "http://www.reportlab.com",
            packages = [],
            ext_modules =   [Extension( '_rl_accel',
                                        ['_rl_accel.c'],
                                        include_dirs=[],
                                        define_macros=[],
                                        library_dirs=[],
                                        libraries=LIBS, # libraries to link against
                                        ),
                            Extension(  'sgmlop',
                                        ['sgmlop.c'],
                                        include_dirs=[],
                                        define_macros=[],
                                        library_dirs=[],
                                        libraries=LIBS, # libraries to link against
                                        ),
                            Extension(  'pyHnj',
                                        ['pyHnjmodule.c','hyphen.c', 'hnjalloc.c'],
                                        include_dirs=[],
                                        define_macros=[],
                                        library_dirs=[],
                                        libraries=LIBS, # libraries to link against
                                        ),
                            ],
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
        MovePYDs('sgmlop.pyd','_rl_accel.pyd','pyHnj.pyd')
