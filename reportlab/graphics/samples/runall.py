# runs all the GUIedit charts in this directory - 
# makes a PDF sample for eaxh existing chart type
import sys
import glob
import string
import inspect
import types

def moduleClasses(mod):
    def P(obj, m=mod.__name__, CT=types.ClassType):
        return (type(obj)==CT and obj.__module__==m)
    try:
        return inspect.getmembers(mod, P)[0][1]
    except:
        return None

def getclass(f):
    return moduleClasses(__import__(f))

def run(format):
    allfiles = glob.glob('*.py')
    allfiles.sort()
    for fn in allfiles:
        f = string.split(fn, '.')[0]
        c = getclass(f)
        if c != None:
            print c.__name__
            try:
                c().save(formats=[format],outDir='.',fnRoot=c.__name__)
            except:
                print " COULDN'T CREATE '%s.%s'!" % (c.__name__, format)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'usage: runall.py FORMAT'
        print '  (where format one of pdf,gif,eps,png etc.)'
    else:
        run(sys.argv[1])