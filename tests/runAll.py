#!/usr/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2017
#see license.txt for license details
"""Runs all test files in all subfolders.
"""
__version__='3.3.0'
import os, glob, sys, traceback, unittest

#we need to ensure 'tests' is on the path.  It will be if you
#run 'setup.py tests', but won't be if you CD into the tests
#directory and run this directly
if __name__=='__main__':
    if '--post-install' in sys.argv:
        while '--post-install' in sys.argv: sys.argv.remove('--post-install')
        import reportlab
        from reportlab import rl_config
        d = os.path.join(os.path.dirname(reportlab.__file__),'fonts')
        for x in ('T1SearchPath','TTFSearchPath','CMapSearchPath'):
            P = getattr(rl_config,x)
            if d not in P:
                P.insert(0,d)
                print('+++++ inserted %r into rl_config.%s' % (d,x))
        del reportlab, rl_config, d, x, P
    P=[]
    os.environ['RL_trustedHosts'] = '*.reportlab.com'
    try:
        from reportlab.lib.testutils import setOutDir
    except ImportError:
        if __name__=='__main__':
            topDir = os.path.dirname(sys.argv[0])
            if not topDir: topDir = os.getcwd()
        else:
            topDir = os.path.dirname(__file__)
        topDir = os.path.dirname(os.path.abspath(topDir))
        if not os.path.isdir(os.path.join(topDir,'reportlab')):
            topDir=os.path.join(topDir,'src')
            assert os.path.isdir(os.path.join(topDir,'reportlab')), "Cannot find reportlab"
        sys.path.insert(0, topDir)
        P.append(topDir)
        del topDir
        from reportlab.lib.testutils import setOutDir

    setOutDir(__name__)
    from reportlab.lib.testutils import testsFolder as topDir
    if topDir:
        topDir = os.path.dirname(topDir)
        if topDir not in sys.path:
            sys.path.insert(0,topDir)
            P.append(topDir)
    del topDir
    from reportlab.lib.testutils import GlobDirectoryWalker, RestrictedGlobDirectoryWalker, outputfile, printLocation
    pp = os.environ.get('PYTHONPATH','')
    if pp: P.append(pp)
    del pp
    os.environ['PYTHONPATH']=os.pathsep.join(P)
    del P

def makeSuite(folder, exclude=[],nonImportable=[],pattern='test_*.py'):
    "Build a test suite of all available test files."
    allTests = unittest.TestSuite()

    if os.path.isdir(folder): sys.path.insert(0, folder)
    for filename in RestrictedGlobDirectoryWalker(folder, pattern,['*/charts-out/*.py']):
        modname = os.path.splitext(os.path.basename(filename))[0]
        if modname not in exclude:
            try:
                ns ={}
                exec('import %s as module' % modname,ns)
                allTests.addTest(ns['module'].makeSuite())
            except:
                tt, tv, tb = sys.exc_info()[:]
                nonImportable.append((filename,traceback.format_exception(tt,tv,tb)))
                del tt,tv,tb
    del sys.path[0]

    return allTests

def main(pattern='test_*.py'):
    try:
        folder = os.path.dirname(__file__)
        assert folder
    except:
        folder = os.path.dirname(sys.argv[0]) or os.getcwd()
    #allow for Benn's "screwball cygwin distro":
    if not folder:
        folder = '.'
    from reportlab.lib.utils import isSourceDistro
    haveSRC = isSourceDistro()

    def cleanup(folder,patterns=('*.pdf', '*.log','*.svg','runAll.txt', 'test_*.txt','_i_am_actually_a_*.*')):
        if not folder: return
        for pat in patterns:
            for filename in GlobDirectoryWalker(folder, pattern=pat):
                try:
                    os.remove(filename)
                except:
                    pass

    # special case for tests directory - clean up
    # all PDF & log files before starting run.  You don't
    # want this if reusing runAll anywhere else.
    if os.sep+'tests' in folder: cleanup(folder)
    cleanup(outputfile(''))
    NI = []
    cleanOnly = '--clean' in sys.argv
    verbosity = [_ for _ in sys.argv if _.startswith('--verbosity=')]
    if not verbosity: verbosity = [f'''--verbosity={os.environ.get('RL_testVerbosity','1')}''']
    verbosity = int(verbosity[-1][12:])
    failfast = bool([_ for _ in sys.argv if _=='--failfast'])
    if not cleanOnly:
        exclude = sum([
                    [os.path.splitext(os.path.basename(_.strip()))[0]
                            for _ in a[10:].split(',') if _.strip()]
                                for a in sys.argv if a.startswith('--exclude=')
                    ],[])
        testSuite = makeSuite(folder,nonImportable=NI,exclude=exclude,pattern=pattern+(not haveSRC and 'c' or ''))
        result = unittest.TextTestRunner(verbosity=verbosity,failfast=failfast).run(testSuite)
    else:
        result = None

    if haveSRC: cleanup(folder,patterns=('*.pyc','*.pyo'))
    if not cleanOnly:
        if NI:
            sys.stderr.write('\n###################### the following tests could not be imported\n')
            for f,tb in NI:
                print('file: "%s"\n%s\n' % (f,''.join(tb)))
        printLocation()
    if __name__=='__main__':
        sys.exit(not result.wasSuccessful())

def mainEx():
    '''for use in subprocesses'''
    try:
        main()
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        sys.stdout.close()
        os.close(sys.stderr.fileno())

def runExternally():
    cmd = '"%s" -c"from tests import runAll;runAll.mainEx()"' % sys.executable
    i,o,e=os.popen3(cmd)
    i.close()
    out = o.read()
    err=e.read()
    return '\n'.join((out,err))

def checkForFailure(outerr):
    return '\nFAILED' in outerr

if __name__ == '__main__': #noruntests
    main()
