#copyright ReportLab Inc. 2000-2003
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/setup.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/setup.py,v 1.6 2002/12/22 22:15:34 andy_robinson Exp $
__version__=''' $Id: setup.py,v 1.6 2002/12/22 22:15:34 andy_robinson Exp $ '''

import os, sys, distutils
from distutils.core import setup, Extension


# from Zope - App.Common.package_home

def package_home(globals_dict):
    __name__=globals_dict['__name__']
    m=sys.modules[__name__]
    r=os.path.split(m.__path__[0])[0]
    return r

pjoin = os.path.join

package_path = pjoin(package_home(distutils.__dict__), 'site-packages', 'reportlab')


# why oh why don't most setup scripts have a script handler?
# if you don't have one, you can't edit in Pythonwin
def run():
    LIBS = []
    setup(
            name="Reportlab",
            version="1.17",
            licence="BSD license (see license.txt for details), Copyright (c) 2000-2003, ReportLab Inc.",
            description="The Reportlab Toolkit",
            long_description="""The ReportLab Toolkit.
An Open Source Python library for generating PDFs and graphics.
""",

            author="Robinson, Watters, Becker, Precedo and many more...",
            author_email="info@reportlab.com",
            url="http://www.reportlab.com/",

            package_dir = {'reportlab': '.'},

            packages=[ # include anything with an __init__
                    'reportlab',
                    'reportlab.demos',
                    'reportlab.demos.colors',
                    'reportlab.demos.gadflypaper',
                    'reportlab.demos.odyssey',
                    'reportlab.demos.rlzope',
                    'reportlab.demos.stdfonts',
                    'reportlab.demos.tests',
                    'reportlab.docs',
                    'reportlab.docs.graphguide',
                    'reportlab.docs.reference',
                    'reportlab.docs.userguide',
                    'reportlab.graphics',
                    'reportlab.graphics.charts',
                    'reportlab.graphics.widgets',
                    'reportlab.lib',
                    'reportlab.pdfbase',
                    'reportlab.pdfgen',
                    'reportlab.platypus',
                    'reportlab.test',
                    'reportlab.tools',
                    'reportlab.tools.docco',
                    'reportlab.tools.py2pdf',
                    'reportlab.tools.pythonpoint',
                    'reportlab.tools.pythonpoint.demos',
                    'reportlab.tools.pythonpoint.styles',
                     ],
              data_files = [(pjoin(package_path, 'docs', 'images'),
                                ['reportlab/docs/images/Edit_Prefs.gif',
                                 'reportlab/docs/images/Python_21.gif',
                                 'reportlab/docs/images/Python_21_HINT.gif',
                                 'reportlab/docs/images/fileExchange.gif',
                                 'reportlab/docs/images/jpn.gif',
                                 'reportlab/docs/images/jpnchars.jpg',
                                 'reportlab/docs/images/lj8100.jpg',
                                 'reportlab/docs/images/replogo.a85',
                                 'reportlab/docs/images/replogo.gif']),
                            (pjoin(package_path, 'fonts'), 
                                ['reportlab/fonts/LeERC___.AFM',
                                 'reportlab/fonts/LeERC___.PFB',
                                 'reportlab/fonts/luxiserif.ttf',
                                 'reportlab/fonts/luxiserif_license.txt',
                                 'reportlab/fonts/rina.ttf',
                                 'reportlab/fonts/rina_license.txt']),
                            (package_path,
                                ['README',
                                 'changes',
                                 'license.txt']),
                            (pjoin(package_path, 'test'),
                                ['test/pythonpowered.gif',]),
                            (pjoin(package_path, 'lib'),
                                ['lib/hyphen.mashed',]),
                            ],

            ext_modules =   [Extension( '_rl_accel',
                                        ['reportlab/lib/_rl_accel.c'],
                                        include_dirs=[],
                                        define_macros=[],
                                        library_dirs=[],
                                        libraries=LIBS, # libraries to link against
                                        ),
                             Extension( 'sgmlop',
                                        ['reportlab/lib/sgmlop.c'],
                                        include_dirs=[],
                                        define_macros=[],
                                        library_dirs=[],
                                        libraries=LIBS, # libraries to link against
                                        ),
                             Extension( 'pyHnj',
                                        ['reportlab/lib/pyHnjmodule.c',
                                         'reportlab/lib/hyphen.c',
                                         'reportlab/lib/hnjalloc.c'],
                                        include_dirs=[],
                                        define_macros=[],
                                        library_dirs=[],
                                        libraries=LIBS, # libraries to link against
                                        ),
                            ],

        )

if __name__=='__main__':
    run()
