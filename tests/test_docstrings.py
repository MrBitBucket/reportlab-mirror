#!/usr/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details

"""This is a test on a package level that find all modules,
classes, methods and functions that do not have a doc string
and lists them in individual log files.

Currently, methods with leading and trailing double underscores
are skipped.
"""
from reportlab.lib.testutils import setOutDir,SecureTestCase, GlobDirectoryWalker, outputfile, printLocation
setOutDir(__name__)
import os, sys, glob, re, unittest, inspect
import reportlab

def typ2is(typ):
    return getattr(inspect,'is'+typ)

def obj2typ(obj):
    for typ in ('function','module','class','method'):
        if typ2is(typ)(obj): return typ
    return None

def getModuleObjects(folder, rootName, typ, pattern='*.py'):
    "Get a list of all objects defined *somewhere* in a package."
    objects = []
    lookup = {}
    for file in GlobDirectoryWalker(folder, pattern):
        folder = os.path.dirname(file)

        if os.path.basename(file) == '__init__.py':
            continue

##        if os.path.exists(os.path.join(folder, '__init__.py')):
####            print 'skipping', os.path.join(folder, '__init__.py')
##            continue

        sys.path.insert(0, folder)
        cwd = os.getcwd()
        os.chdir(folder)

        modName = os.path.splitext(os.path.basename(file))[0]
        prefix = folder[folder.find(rootName):]
        prefix = prefix.replace(os.sep,'.')
        mName = prefix + '.' + modName

        try:
            module = __import__(mName)
        except ImportError:
            # Restore sys.path and working directory.
            os.chdir(cwd)
            del sys.path[0]
            continue

        # Get the 'real' (leaf) module
        # (__import__ loads only the top-level one).
        if mName.find('.') != -1:
            for part in mName.split('.')[1:]:
                module = getattr(module, part)

            # Find the objects in the module's content.
            modContentNames = dir(module)

            # Handle modules.
            if typ=='module':
                if module.__name__.find('reportlab') > -1:
                    objects.append((mName, module))
                    continue

            for n in modContentNames:
                obj = eval(mName + '.' + n)
                # Handle functions and classes.
                if typ in ('function','module'):
                    if obj2typ(obj) == typ and obj not in lookup:
                        if typ == 'class':
                            if obj.__module__.find(rootName) != 0:
                                continue
                        objects.append((mName, obj))
                        lookup[obj] = 1
                # Handle methods.
                elif typ == 'method':
                    if obj2typ(obj) == 'class':
                        for m in dir(obj):
                            a = getattr(obj, m)
                            if obj2typ(a) == typ and a not in lookup:
                                if a.__self__.__class__.__module__.find(rootName) != 0:
                                    continue
                                cName = obj.__name__
                                objects.append((mName, a))
                                lookup[a] = 1

        # Restore sys.path and working directory.
        os.chdir(cwd)
        del sys.path[0]
    return objects

class DocstringTestCase(SecureTestCase):
    "Testing if objects in the ReportLab package have docstrings."

    def _writeLogFile(self, objType):
        "Write log file for different kind of documentable objects."

        cwd = os.getcwd()
        from reportlab.lib.testutils import RL_HOME
        objects = getModuleObjects(RL_HOME, 'reportlab', objType)
        if objType!='function':
            objects.sort()
        os.chdir(cwd)

        expl = {'function':'functions',
                'class':'classes',
                'method':'methods',
                'module':'modules'}[objType]

        path = outputfile("test_docstrings-%s.log" % expl)
        file = open(path, 'w')
        file.write('No doc strings found for the following %s below.\n\n' % expl)
        p = re.compile('__.+__')

        lines = []
        for name, obj in objects:
            if objType == 'method':
                n = obj.__name__
                # Skip names with leading and trailing double underscores.
                if p.match(n):
                    continue

            if objType == 'function':
                if not obj.__doc__ or len(obj.__doc__) == 0:
                    lines.append("%s.%s\n" % (name, obj.__name__))
            else:
                if not obj.__doc__ or len(obj.__doc__) == 0:
                    if objType == 'class':
                        lines.append("%s.%s\n" % (obj.__module__, obj.__name__))
                    elif objType == 'method':
                        lines.append("%s.%s\n" % (obj.__self__.__class__, obj.__name__))
                    else:
                        lines.append("%s\n" % (obj.__name__))

        lines.sort()
        for line in lines:
            file.write(line)

        file.close()

    def test0(self):
        "Test if functions have a doc string."
        self._writeLogFile('function')

    def test1(self):
        "Test if classes have a doc string."
        self._writeLogFile('class')

    def test2(self):
        "Test if methods have a doc string."
        self._writeLogFile('method')

    def test3(self):
        "Test if modules have a doc string."
        self._writeLogFile('module')

def makeSuite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    if sys.platform[:4] != 'java': suite.addTest(loader.loadTestsFromTestCase(DocstringTestCase))
    return suite

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
