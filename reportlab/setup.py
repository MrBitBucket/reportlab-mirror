#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/setup.py
__version__=''' $Id$ '''

import os, sys, distutils
from distutils.core import setup, Extension


# from Zope - App.Common.package_home

def package_home(globals_dict):
    __name__=globals_dict['__name__']
    m=sys.modules[__name__]
    r=os.path.split(m.__path__[0])[0]
    return r

pjoin = os.path.join
package_path = pjoin(package_home(distutils.__dict__), 'reportlab')

def get_version():
    #determine Version
    if __name__=='__main__':
        HERE=os.path.dirname(sys.argv[0])
    else:
        HERE=os.path.dirname(__file__)

    #first try source
    FN = pjoin(HERE,'__init__')
    try:
        for l in open(pjoin(FN+'.py'),'r').readlines():
            if l.startswith('Version'):
                exec l.strip()
                return Version
    except:
        pass

    #don't have source, try import
    import imp
    for desc in ('.pyc', 'rb', 2), ('.pyo', 'rb', 2):
        try:
            fn = FN+desc[0]
            f = open(fn,desc[1])
            m = imp.load_module('reportlab',f,fn,desc)
            return m.Version
        except:
            pass
    raise ValueError('Cannot determine ReportLab Version')

# why oh why don't most setup scripts have a script handler?
# if you don't have one, you can't edit in Pythonwin
def run():
    LIBS = []
    setup(
            name="Reportlab",
            version=get_version(),
            license="BSD license (see license.txt for details), Copyright (c) 2000-2003, ReportLab Inc.",
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
              data_files = [
                            (package_path,
                                ['README',
                                 'changes',
                                 'license.txt']),

                            (pjoin(package_path,'demos', 'gadflypaper'),
                                ['demos/gadflypaper/00readme.txt']),

                            (pjoin(package_path,'demos', 'odyssey'),
                                ['demos/odyssey/00readme.txt',
                                 'demos/odyssey/odyssey.txt']),

                            (pjoin(package_path,'demos', 'rlzope'),
                                ['demos/rlzope/readme.txt']),

                            (pjoin(package_path,'demos', 'stdfonts'),
                                ['demos/stdfonts/00readme.txt']),

                            (pjoin(package_path,'docs', 'images'),
                                ['docs/images/Edit_Prefs.gif',
                                 'docs/images/Python_21.gif',
                                 'docs/images/Python_21_HINT.gif',
                                 'docs/images/fileExchange.gif',
                                 'docs/images/jpn.gif',
                                 'docs/images/jpnchars.jpg',
                                 'docs/images/lj8100.jpg',
                                 'docs/images/replogo.a85',
                                 'docs/images/replogo.gif']),

                            (pjoin(package_path,'docs', 'reference'),
                                ['docs/reference/reference.yml']),

                            (pjoin(package_path,'docs', 'userguide'),
                                ['docs/userguide/testfile.txt']),

                            (pjoin(package_path,'extensions'),
                                ['extensions/README']),

                            (pjoin(package_path, 'fonts'),
                                ['fonts/00readme.txt',
                                 'fonts/LeERC___.AFM',
                                 'fonts/LeERC___.PFB',
                                 'fonts/luxiserif.ttf',
                                 'fonts/luxiserif_license.txt',
                                 'fonts/rina.ttf',
                                 'fonts/rina_license.txt']),

                            (pjoin(package_path, 'lib'),
                                ['lib/hyphen.mashed',]),

                            (pjoin(package_path, 'test'),
                                ['test/pythonpowered.gif',]),

                            (pjoin(package_path, 'tools'),
                                ['tools/README',]),

                            (pjoin(package_path, 'tools', 'docco'),
                                ['tools/docco/README',]),

                            (pjoin(package_path, 'tools', 'py2pdf'),
                                ['tools/py2pdf/README',
                                 'tools/py2pdf/demo-config.txt',
                                 'tools/py2pdf/vertpython.jpg'
                                 ]),

                            (pjoin(package_path, 'tools', 'pythonpoint'),
                                ['tools/pythonpoint/README',
                                 'tools/pythonpoint/pythonpoint.dtd',]),

                            (pjoin(package_path, 'tools', 'pythonpoint', 'demos'),
                                ['tools/pythonpoint/demos/htu.xml',
                                 'tools/pythonpoint/demos/LeERC___.AFM',
                                 'tools/pythonpoint/demos/LeERC___.PFB',
                                 'tools/pythonpoint/demos/leftlogo.a85',
                                 'tools/pythonpoint/demos/leftlogo.gif',
                                 'tools/pythonpoint/demos/lj8100.jpg',
                                 'tools/pythonpoint/demos/monterey.xml',
                                 'tools/pythonpoint/demos/outline.gif',
                                 'tools/pythonpoint/demos/pplogo.gif',
                                 'tools/pythonpoint/demos/python.gif',
                                 'tools/pythonpoint/demos/pythonpoint.xml',
                                 'tools/pythonpoint/demos/spectrum.png',
                                 'tools/pythonpoint/demos/vertpython.gif']),

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
