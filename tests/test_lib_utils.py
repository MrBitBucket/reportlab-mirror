#Copyright ReportLab Europe Ltd. 2000-2017
#see license.txt for license details
"""Tests for reportlab.lib.utils
"""
__version__='3.3.0'
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, printLocation, mockUrlRead
from unittest.mock import patch
setOutDir(__name__)
import os, time, sys
import reportlab
from reportlab import rl_config
import unittest
from reportlab.lib import colors
from reportlab.lib.utils import recursiveImport, recursiveGetAttr, recursiveSetAttr, rl_isfile, \
                                isCompactDistro, isPyPy, TimeStamp, rl_get_module, \
                                recursiveGetAttr, recursiveSetAttr, recursiveDelAttr, \
                                asUnicode, asUnicodeEx, asBytes

def _rel_open_and_read(fn):
    from reportlab.lib.utils import open_and_read
    from reportlab.lib.testutils import testsFolder
    cwd = os.getcwd()
    os.chdir(testsFolder)
    try:
        return open_and_read(fn)
    finally:
        os.chdir(cwd)

class ImporterTestCase(unittest.TestCase):
    "Test import utilities"

    @classmethod
    def setUpClass(cls):
        from reportlab.lib.utils import get_rl_tempdir
        cls._value = float(repr(time.time()))
        s = int(cls._value)
        cls._tempdir = get_rl_tempdir('reportlab_test','tmp_%s' % s)
        if not os.path.isdir(cls._tempdir):
            os.makedirs(cls._tempdir,0o700)
        _testmodulename = os.path.join(cls._tempdir,'test_module_%s.py' % s)
        with open(_testmodulename,'w') as f:
            f.write('__all__=[]\nvalue=%s\n' % repr(cls._value))
        if sys.platform=='darwin':
            time.sleep(0.3)
        cls._testmodulename = os.path.splitext(os.path.basename(_testmodulename))[0]

    @classmethod
    def tearDownClass(cls):
        from shutil import rmtree
        rmtree(cls._tempdir,1)

    def myAssertRaisesRegex(self,*args,**kwds):
        return self.assertRaisesRegex(*args,**kwds)

    def test1(self):
        "try stuff known to be in the path"
        m1 = recursiveImport('reportlab.pdfgen.canvas')
        import reportlab.pdfgen.canvas
        assert m1 == reportlab.pdfgen.canvas

    def test2(self):
        "try under a well known directory NOT on the path"
        from reportlab.lib.testutils import testsFolder
        D = os.path.join(testsFolder,'..','tools','pythonpoint')
        fn = os.path.join(D,'stdparser.py')
        if rl_isfile(fn) or rl_isfile(fn+'c') or rl_isfile(fn+'o'):
            m1 = recursiveImport('stdparser', baseDir=D)

    def test3(self):
        "ensure CWD is on the path"
        try:
            cwd = os.getcwd()
            os.chdir(self._tempdir)
            m1 = recursiveImport(self._testmodulename)
        finally:
            os.chdir(cwd)

    def test4(self):
        "ensure noCWD removes current dir from path"
        try:
            cwd = os.getcwd()
            os.chdir(self._tempdir)
            import sys
            try:
                del sys.modules[self._testmodulename]
            except KeyError:
                pass
            self.assertRaises(ImportError,
                              recursiveImport,
                              self._testmodulename,
                              noCWD=1)
        finally:
            os.chdir(cwd)

    def test5(self):
        "recursive attribute setting/getting on modules"
        import reportlab.lib.units
        inch = recursiveGetAttr(reportlab, 'lib.units.inch')
        assert inch == 72

        recursiveSetAttr(reportlab, 'lib.units.cubit', 18*inch)
        cubit = recursiveGetAttr(reportlab, 'lib.units.cubit')
        assert cubit == 18*inch

    def test6(self):
        "recursive attribute setting/getting on drawings"
        from reportlab.graphics.charts.barcharts import sampleH1
        drawing = sampleH1()
        recursiveSetAttr(drawing, 'barchart.valueAxis.valueMax', 72)
        theMax = recursiveGetAttr(drawing, 'barchart.valueAxis.valueMax')
        assert theMax == 72

    def test7(self):
        "test open and read of a simple relative file"
        b = _rel_open_and_read('../docs/images/Edit_Prefs.gif')

    def test8(self):
        "test open and read of a relative file: URL"
        b = _rel_open_and_read('file:../docs/images/Edit_Prefs.gif')

    @patch('reportlab.lib.utils.rlUrlRead',mockUrlRead)
    def test9(self):
        "test open and read of an http: URL"
        from reportlab.lib.utils import open_and_read
        b = open_and_read('http://www.reportlab.com/rsrc/encryption.gif')

    def test10(self):
        "test open and read of a simple relative file"
        from io import BytesIO
        from reportlab.lib.utils import open_and_read
        b = BytesIO(_rel_open_and_read('../docs/images/Edit_Prefs.gif'))
        b = open_and_read(b)

    def test11(self):
        "test open and read of an RFC 2397 data URI with base64 encoding"
        result = _rel_open_and_read('data:image/gif;base64,R0lGODdhAQABAIAAAP///////ywAAAAAAQABAAACAkQBADs=')
        self.assertEqual(result,b'GIF87a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\xff\xff\xff,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')

    def test12(self):
        "test open and read of an RFC 2397 data URI without an encoding"
        result = _rel_open_and_read('data:text/plain;,Hello%20World')
        self.assertEqual(result,b'Hello World')

    def testRecursiveImportErrors(self):
        "check we get useful error messages"
        try:
            m1 = recursiveImport('reportlab.pdfgen.brush')
            self.fail("Imported a nonexistent module")
        except ImportError as e:
            self.assertIn('reportlab.pdfgen.brush',str(e))

        try:
            m1 = recursiveImport('totally.non.existent')
            self.fail("Imported a nonexistent module")
        except ImportError as e:
            self.assertIn('totally',str(e))

        try:
            #import a module in the 'tests' directory with a bug
            m1 = recursiveImport('unimportable')
            self.fail("Imported a buggy module")
        except Exception as e:
            self.assertIn(("integer division by zeroException raised while importing 'unimportable': integer division by zero"
                            if isPyPy else 'division by zero')
                        ,str(e))
    def test14(self):
        "test the TimeStamp behaviour"
        oinvariant = rl_config.invariant
        sden = 'SOURCE_DATE_EPOCH'
        if sden in os.environ:
            sde = os.environ[sden]
            del os.environ[sden]
        else:
            sde = self

        try:
            rl_config.invariant = False
            t = time.time()
            ts = TimeStamp()
            self.assertTrue(abs(t-ts.t)<1)
            ts = TimeStamp(invariant=True)
            self.assertEqual(ts.t,946684800.0)
            self.assertEqual(ts.YMDhms,(2000, 1, 1, 0, 0, 0))
            self.assertEqual(ts.tzname,'UTC')
            os.environ[sden] = '1490003100'
            ts = TimeStamp(invariant=True)  #debian variable takes precedence here
            self.assertEqual(ts.t,1490003100)
            self.assertEqual(ts.YMDhms,(2017, 3, 20, 9, 45, 0))
            self.assertEqual(ts.tzname,'UTC')
            rl_config.invariant = True
            ts = TimeStamp()                #still takes precedence
            self.assertEqual(ts.t,1490003100)
            self.assertEqual(ts.YMDhms,(2017, 3, 20, 9, 45, 0))
            self.assertEqual(ts.tzname,'UTC')
            del os.environ[sden]
            ts = TimeStamp()                #now rl_config takes precedence
            self.assertEqual(ts.t,946684800.0)
            self.assertEqual(ts.YMDhms,(2000, 1, 1, 0, 0, 0))
            self.assertEqual(ts.tzname,'UTC')
        finally:
            if sde is not self:
                os.environ[sden] = sde
            rl_config.invariant = oinvariant

    def test15(self):
        m = rl_get_module(self._testmodulename,self._tempdir)
        self.assertEqual(self._value,m.value)

    def test16(self):
        from reportlab.lib import fontfinder
        ff = fontfinder.FontFinder(useCache=False,recur=True)
        ff.addDirectories(rl_config.T1SearchPath + rl_config.TTFSearchPath)
        ff.search()
        ff.getFamilyNames()

    def test17(self):
        self.assertEqual(asUnicode(u'abc'),u'abc')
        self.assertEqual(asUnicode(b'abc'),u'abc')
        self.assertRaises(AttributeError,asUnicode,['abc'])
        self.myAssertRaisesRegex(AttributeError,r"asUnicode\(.*'list' object has no attribute 'decode'", asUnicode,['abc'])
        self.assertEqual(asUnicodeEx(u'abc'),u'abc')
        self.assertEqual(asUnicodeEx(b'abc'),u'abc')
        self.assertEqual(asUnicodeEx(123),u'123')
        self.assertEqual(asBytes(u'abc'),b'abc')
        self.assertEqual(asBytes(b'abc'),b'abc')
        self.assertRaises(AttributeError,asBytes,['abc'])
        self.myAssertRaisesRegex(AttributeError,r"asBytes\(.*'list' object has no attribute 'encode'", asBytes,['abc'])

class RaccessTest:
    l = [1, 2]
    a = [0, [1, 2, [3,4]]]
    b = {'x': {'y': 'y'}, 'z': [1, 2]}
    z = 'z'

class RaccessPerson:
    settings = {
        'autosave': True,
        'style': {
            'height': 30,
            'width': 200
        },
        'themes': ['light', 'dark']
    }
    def __init__(self, name, age, friends):
        self.name = name
        self.age = age
        self.friends = friends

class RaccessTestCase(unittest.TestCase):
    "Test recursive access functions"
    def test1(self):
        def innerTest(k,v):
            obj = RaccessTest()
            obj.t = obj
            obj.a.append(obj)
            obj.b['w'] = obj
            self.assertEqual(recursiveGetAttr(obj,k),v,"error getattr(obj,%r)==%r" % (k,v))
        for k,v in [
            ('l', RaccessTest.l),
            ('t.t.t.t.z', 'z'),
            ('a[0]', 0),
            ('a[1][0]', 1),
            ('a[1][2]', [3,4]),
            ('b["x"]', {'y': 'y'}),
            ('b["x"]["y"]', 'y'),
            ('b["z"]', [1,2]),
            ('b["z"][1]', 2),
            ('b["w"].z', 'z'),
            ('b["w"].t.l', [1, 2]),
            ('a[-1].z', 'z'),
            ('l[-1]', 2),
            ('a[2].t.a[-1].z', 'z'),
            ('a[2].t.b["z"][0]', 1),
            ('a[-1].t.z', 'z'),
            ]:
            innerTest(k,v)

    def test_person_example(self):
        bob = RaccessPerson(name="Bob", age=31, friends=[])
        jill = RaccessPerson(name="Jill", age=29, friends=[bob])
        jack = RaccessPerson(name="Jack", age=28, friends=[bob, jill])

        # Nothing new
        self.assertEqual(recursiveGetAttr(bob, 'age') ,31)

        # Lists
        self.assertEqual(recursiveGetAttr(jill, 'friends[0].name') ,'Bob')
        self.assertEqual(recursiveGetAttr(jack, 'friends[-1].age') ,29)

        # Dict lookups
        self.assertEqual(recursiveGetAttr(jack, 'settings["style"]["width"]') ,200)

        # Combination of lookups
        self.assertEqual(recursiveGetAttr(jack, 'settings["themes"][-2]') ,'light')
        self.assertEqual(recursiveGetAttr(jack, 'friends[-1].settings["themes"][1]') ,'dark')

        # Setattr
        #recursiveSetAttr(bob, 'settings["style"]["width"]', 400)
        #self.assertEqual(recursiveGetAttr(bob, 'settings["style"]["width"]') ,400)

        # Nested objects
        recursiveSetAttr(bob, 'friends', [jack, jill])
        self.assertEqual(recursiveGetAttr(jack, 'friends[0].friends[0]') ,jack)

        recursiveSetAttr(jill, 'friends[0].age', 32)
        self.assertEqual(bob.age ,32)

        # Deletion
        #recursiveDelAttr(jill, 'friends[0]')
        #self.assertEqual(len(jill.friends) ,0)

        recursiveDelAttr(jill, 'age')
        assert not hasattr(jill, 'age')

        recursiveDelAttr(bob, 'friends[0].age')
        assert not hasattr(jack, 'age')

        # Unsupported
        #with self.assertRaises(NotImplementedError) as e:
        #   recursiveGetAttr(bob, 'friends[0+1]')

        # Nice try, function calls are not allowed
        #with self.assertRaises(ValueError):
        #   recursiveGetAttr(bob, 'friends.pop(0)')

        # Must be an expression
        with self.assertRaises(SyntaxError):
            recursiveGetAttr(bob, 'friends = []')

        # Must be an expression
        with self.assertRaises(SyntaxError):
            recursiveGetAttr(bob, 'friends..')

        # Must be an expression
        with self.assertRaises(KeyError):
            recursiveGetAttr(bob, 'settings["DoesNotExist"]')

        # Must be an expression
        with self.assertRaises(IndexError):
            recursiveGetAttr(bob, 'friends[100]')

    def test_empty(self):
        obj = RaccessTest()
        with self.assertRaises(ValueError):
           recursiveGetAttr(obj,"  ")

        with self.assertRaises(ValueError):
            recursiveGetAttr(obj,"")

        with self.assertRaises(TypeError):
            recursiveGetAttr(obj, 0)

        with self.assertRaises(TypeError):
            recursiveGetAttr(obj, None)

        with self.assertRaises(TypeError):
            recursiveGetAttr(obj, obj)

def makeSuite():
    return makeSuiteForClasses(ImporterTestCase,RaccessTestCase)

if __name__ == "__main__": #noruntests
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
