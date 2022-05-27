#!/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2017
#see license.txt for license details
__doc__="""Verfy that if in invariant mode, repeated runs
make identical file.  This does NOT test across platforms
or python versions, only a user can do that :-)"""
__version__='3.3.0'
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
setOutDir(__name__)

import unittest
from reportlab.pdfgen.canvas import Canvas
filename = outputfile('test_invariant.pdf')

class InvarTestCase(unittest.TestCase):
    "Simplest test that makes PDF"
    def test0(self):
        import os
        from reportlab.lib.testutils import testsFolder
        c = Canvas(filename, invariant=1, pageCompression=0)
        c.setFont('Helvetica-Bold', 36)
        c.drawString(100,700, 'Hello World')
        gif = os.path.join(testsFolder,'pythonpowered.gif')
        c.drawImage(gif,100,600)
        c.save()

        with open(filename, 'rb') as f:
            raw1 = f.read()

        c = Canvas(filename, invariant=1, pageCompression=0)
        c.setFont('Helvetica-Bold', 36)
        c.drawString(100,700, 'Hello World')
        c.drawImage(gif,100,600)
        c.save()

        with open(filename, 'rb') as f:
            raw2 = f.read()

        assert raw1 == raw2, 'repeated runs differ!'

    def test1(self):
        import os
        from reportlab.lib.testutils import testsFolder
        filename = outputfile('test_no_helvetica.pdf')
        c = Canvas(filename, invariant=1, pageCompression=0, initialFontName='Times-Roman')
        c.drawString(100,700, 'Hello World')
        c.save()
        with open(filename, 'rb') as f:
            raw = f.read()
        assert b'Helvetica' not in raw and b'Times-Roman' in raw, 'Canvas initialFontName expectations not satisfied!'

def makeSuite():
    return makeSuiteForClasses(InvarTestCase)


#noruntests
if __name__ == "__main__":
    # add some diagnostics, useful in invariant tests
    import sys, os
    from hashlib import md5
    from reportlab.lib.utils import bytestr
    verbose = ('-v' in sys.argv)
    unittest.TextTestRunner().run(makeSuite())
    if verbose:
        #tell us about the file we produced
        fileSize = os.stat(filename)[6]
        raw = open(filename,'rb').read()
        digest = md5(bytestr(raw)).hexdigest()
        major, minor = sys.version_info[0:2]
        print('%s on %s (Python %d.%d):\n    %d bytes, digest %s' % (
            filename,sys.platform, major, minor, fileSize, digest))
    printLocation()
