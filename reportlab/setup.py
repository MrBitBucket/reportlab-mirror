# a dangerously incomplete attempt at a reportlab setup script,
# do not trust it to do anything.  It builds the extensions
# though :-)

from distutils.core import setup, Extension

import os, sys, distutils

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

            author="The boys from SW19",
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
                                ['docs/images/Edit_Prefs.gif',
                                 'docs/images/Python_21.gif',
                                 'docs/images/Python_21_HINT.gif',
                                 'docs/images/fileExchange.gif',
                                 'docs/images/jpn.gif',
                                 'docs/images/jpnchars.jpg',
                                 'docs/images/lj8100.jpg',
                                 'docs/images/replogo.a85',
                                 'docs/images/replogo.gif']),
                            (pjoin(package_path, 'fonts'), 
                                ['fonts/LeERC___.AFM',
                                 'fonts/LeERC___.PFB',
                                 'fonts/luxiserif.ttf',
                                 'fonts/luxiserif_license.txt',
                                 'fonts/rina.ttf',
                                 'fonts/rina_license.txt']),
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
                                        ['lib/_rl_accel.c'],
                                        include_dirs=[],
                                        define_macros=[],
                                        library_dirs=[],
                                        libraries=LIBS, # libraries to link against
                                        ),
                             Extension( 'sgmlop',
                                        ['lib/sgmlop.c'],
                                        include_dirs=[],
                                        define_macros=[],
                                        library_dirs=[],
                                        libraries=LIBS, # libraries to link against
                                        ),
                             Extension( 'pyHnj',
                                        ['lib/pyHnjmodule.c',
                                         'lib/hyphen.c',
                                         'lib/hnjalloc.c'],
                                        include_dirs=[],
                                        define_macros=[],
                                        library_dirs=[],
                                        libraries=LIBS, # libraries to link against
                                        ),
                            ],

        )

if __name__=='__main__':
    run()
