#codegrab.py
"""
This grabs various Python class, method and function
headers and their doc strings to include in documents
"""

import imp
import types
import string
import os


class Dog:
    def woof(self):
        print 'bark'

def getStuffDefinedIn(modulename, path=None):
    """Checks each item for where it
    is defined."""
    found = imp.find_module(modulename, path)
    assert found, "Module %s not found" % modulename
    (file, pathname, description) = found
    mod = imp.load_module(modulename, file, pathname, description)
    useful_stuff = []
    for name in dir(mod):
        value = getattr(mod, name)
        if type(value) in (types.FunctionType, types.MethodType, types.ClassType):
            #we're possibly interested in it
            if os.path.splitext(value.func_code.co_filename)[0] == modulename:
                #it was defined here
                useful_stuff.append((name, value))

    return useful_stuff


def getPrototype(f):
    # finds the first line of code
    lines = open(f.func_code.co_filename, 'r').readlines()
    firstLineNo = f.func_code.co_firstlineno - 1
    lineNo = firstLineNo
    brackets = 0
    while 1:
        line = lines[lineNo]
        for char in line:
            if char == '(':
                brackets = brackets + 1
            elif char == ')':
                brackets = brackets - 1
        if brackets == 0:
            break
        else:
            lineNo = lineNo + 1

    usefulLines = map(string.rstrip, lines[firstLineNo:lineNo+1])
    return string.join(usefulLines, '\n')

def test():
    stuff = getStuffDefinedIn('codegrab', ['c:\\home\\utils\\yaml'])
    for (name, value) in stuff:
        print getPrototype(value)
        print value.__doc__
        


if __name__=='__main__':
    test()
    