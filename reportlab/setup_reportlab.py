#!/usr/bin/env python

# first stab at a distutils setup script

from distutils.core import setup

def run():
    setup(name="ReportLab",
          version="1.15.test1",
          description="""The ReportLab PDF Generation tools.
   An Open Source Python library for generating PDFs.

   This installer created using distutils by John Precedo.
   Created from a TOTALLY FRESH CVS checkout of the reportlab tree,
   on 15 OCT 2002 at 16:20.
""",
          author = "ReportLab Europe Ltd",
          author_email = "info@python.net",
          url = "http://www.reportlab.com/",
          package_dir = {'': '..'},
          packages = ['reportlab',
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
                    'reportlab.docs.images',
                    'reportlab.extensions',
                    'reportlab.fonts',
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
                    ],
          data_files = [('reportlab', ['docs/images/Edit_Prefs.gif',
                                                 'docs/images/Python_21.gif',
                                                 'docs/images/Python_21_HINT.gif',
                                                 'docs/images/fileExchange.gif',
                                                 'docs/images/jpn.gif',
                                                 'docs/images/jpnchars.jpg',
                                                 'docs/images/lj8100.jpg',
                                                 'docs/images/replogo.a85',
                                                 'docs/images/replogo.gif']),
                    ('reportlab', ['fonts/LeERC___.AFM',
                                         'fonts/LeERC___.PFB',
                                         'fonts/luxiserif.ttf',
                                         'fonts/rina.ttf'])]
         )


if __name__ == "__main__":
    run()