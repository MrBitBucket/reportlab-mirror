# runs all the GUIedit charts in this directory - 
# makes a PDF sample for eaxh existing chart type

if __name__ == "__main__":
    def run():
        import glob, string
        def moduleClasses(mod):
            import inspect, types
            def P(obj, m=mod.__name__, CT=types.ClassType):
                return (type(obj)==CT and obj.__module__==m)
            try:
                return inspect.getmembers(mod, P)[0][1]
            except:
                return None
        def getclass(f):
            return moduleClasses(__import__(f))

        allfiles = glob.glob('*.py')
        allfiles.sort()
        for fn in allfiles:
            f = string.split(fn, '.')[0]
            c = getclass(f)
            if c != None:
                print c.__name__
                try:
                    c().save(formats=['pdf'],outDir='.',fnRoot=c.__name__)
                except:
                    print " COULDN'T CREATE '%s.pdf'!" % c.__name__

    run()