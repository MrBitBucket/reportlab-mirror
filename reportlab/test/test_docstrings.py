#!/usr/bin/env python
#copyright ReportLab Inc. 2000-2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/test/test_docstrings.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/test/test_docstrings.py,v 1.5 2001/05/18 12:16:42 dinu_gherman Exp $

"""This is a test on a package level that find all modules,
classes, methods and functions that do not have a doc string
and lists them in individual log files.

Currently, methods with leading and trailing double underscores
are skipped.
"""

import os, sys, glob, string, types, re

import reportlab
from reportlab.test import unittest
from reportlab.test.utils import SecureTestCase


RL_HOME = os.path.dirname(reportlab.__file__)


# Should replace with test.utils.GlobDirectoryWalker, soon...
def subFoldersOfFolder(folder):
    "Return a list of full paths of all subfolders."

    files = os.listdir(folder)
    for i in range(len(files)):
        files[i] = os.path.join(folder, files[i])
    subFolders = filter(lambda f: os.path.isdir(f), files)

    return subFolders


def getModuleObjects(folder, rootName, typ):
    "Get a list of all function objects defined *somewhere* in a package."

    folders = [folder] + subFoldersOfFolder(folder)
    
    objects = []
    for f in folders:
        sys.path.insert(0, f)
        os.chdir(f)
        pattern = os.path.join('*.py')
        prefix = f[string.find(f, rootName):]
        prefix = string.replace(prefix, os.sep, '.')
        modNames = glob.glob(pattern)
        modNames = filter(lambda m:string.find(m, '__init__.py') == -1, modNames)
        # Make module names fully qualified.
        for i in range(len(modNames)):
            modNames[i] = prefix + '.' + modNames[i][:string.find(modNames[i], '.')]
        for mName in modNames:
            module = __import__(mName)
            # Get the 'real' (leaf) module
            # (__import__ loads only the top-level one). 
            if string.find(mName, '.') != -1:
                for part in string.split(mName, '.')[1:]:
                    module = getattr(module, part)
            # Find the objects in the module's content.
            modContentNames = dir(module)
            # Handle modules.
            if typ  == types.ModuleType:
                if string.find(module.__name__, 'reportlab') > -1:
                    objects.append((mName, module))
                    continue
            for n in modContentNames:
                obj = eval(mName + '.' + n)
                # Handle functions and classes.
                if typ in (types.FunctionType, types.ClassType):
                    if type(obj) == typ:
                        objects.append((mName, obj))
                # Handle methods.
                elif typ == types.MethodType:
                    if type(obj) == types.ClassType:
                        for m in dir(obj):
                            a = getattr(obj, m)
                            if type(a) == typ:
                                cName = obj.__name__
                                objects.append(("%s.%s" % (mName, cName), a))
        del sys.path[0]

    return objects

    
class DocstringTestCase(SecureTestCase):
    "Testing if objects in the ReportLab package have docstrings."
    
    def _writeLogFile(self, objType):
        "Write log file for different kind of documentable objects."
        
        cwd = os.getcwd()

        objects = getModuleObjects(RL_HOME, 'reportlab', objType)

        expl = {types.FunctionType:'functions',
                types.ClassType:'classes',
                types.MethodType:'methods',
                types.ModuleType:'modules'}[objType]

        os.chdir(cwd)
        path = "test_docstrings-%s.log" % expl
        file = open(path, 'w')
        file.write('No doc strings found for the following %s below.\n\n' % expl)
        p = re.compile('__.+__')
        for name, obj in objects:
            n = string.split(obj.__name__, '.')[-1]
            # Skip names with leading and trailing double underscores.
            if p.match(n):
                continue
            if objType != types.ModuleType:
                if not obj.__doc__ or len(obj.__doc__) == 0:
                    file.write("%s.%s()\n" % (name, obj.__name__))
            else:
                if not obj.__doc__ or len(obj.__doc__) == 0:
                    file.write("%s\n" % (obj.__name__))
        file.close()

        
    def test1(self):
        "Test if functions have a doc string."

        self._writeLogFile(types.FunctionType)


    def test2(self):
        "Test if classes have a doc string."

        self._writeLogFile(types.ClassType)


    def test3(self):
        "Test if methods have a doc string."

        self._writeLogFile(types.MethodType)


    def test4(self):
        "Test if modules have a doc string."

        self._writeLogFile(types.ModuleType)


def makeSuite():
    suite = unittest.TestSuite()
    
    suite.addTest(DocstringTestCase('test1'))
    suite.addTest(DocstringTestCase('test2'))
    suite.addTest(DocstringTestCase('test3'))
    suite.addTest(DocstringTestCase('test4'))

    return suite


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    
