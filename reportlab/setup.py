# a dangerously incomplete attempt at a reportlab setup script,
# do not trust it to do anything.  It builds the extensions
# though :-)

from distutils.core import setup, Extension

# why oh why don't most setup scripts have a script handler?
# if you don't have one, you can't edit in Pythonwin
def run():
    LIBS = []
    setup(
            name="Reportlab",
            version="1.15.3",
            description="Reportlab PDF generation tools",
            author="The boys from SW19",
            author_email="info@reportlab.com",
            url="http://www.reportlab.com/",

            package_dir = {'': '..'},

            packages=[ # include anything with an __init__
                    'reportlab',
                    'reportlab.docs',
                    'reportlab.docs.graphguide',
                    'reportlab.docs.images',
                    'reportlab.docs.reference',
                    'reportlab.docs.userguide',
                    'reportlab.fonts',
                    'reportlab.graphics',
                    'reportlab.graphics.charts',
                    'reportlab.graphics.widgets',
                    'reportlab.lib',
                    'reportlab.pdfbase',
                    'reportlab.pdfgen',
                    'reportlab.platypus',
                      ],
              data_files = [('docs/images', ['docs/images/Edit_Prefs.gif',
                                                 'docs/images/Python_21.gif',
                                                 'docs/images/Python_21_HINT.gif',
                                                 'docs/images/fileExchange.gif',
                                                 'docs/images/jpn.gif',
                                                 'docs/images/jpnchars.jpg',
                                                 'docs/images/lj8100.jpg',
                                                 'docs/images/replogo.a85',
                                                 'docs/images/replogo.gif']),
                    ('fonts', ['fonts/LeERC___.AFM',
                                     'fonts/LeERC___.PFB',
                                     'fonts/luxiserif.ttf',
                                     'fonts/rina.ttf']
                     )],

            ext_modules =   [Extension( '_rl_accel',
                                        ['lib/_rl_accel.c'],
                                        include_dirs=[],
                                        define_macros=[],
                                        library_dirs=[],
                                        libraries=LIBS, # libraries to link against
                                        ),
                            Extension(  'sgmlop',
                                        ['lib/sgmlop.c'],
                                        include_dirs=[],
                                        define_macros=[],
                                        library_dirs=[],
                                        libraries=LIBS, # libraries to link against
                                        ),
                            Extension(  'pyHnj',
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