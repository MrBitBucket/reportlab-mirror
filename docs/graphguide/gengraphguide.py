#!/bin/env python
#Copyright ReportLab Europe Ltd. 2000-2008
#see license.txt for license details
__version__=''' $Id$ '''
__doc__ = """
This module contains the script for building the graphics guide.
"""
def run(pagesize=None, verbose=1, outDir=None):
    import sys,os
    cwd = os.getcwd()
    docsDir=os.path.dirname(os.path.dirname(sys.argv[0]) or cwd)
    topDir=os.path.dirname(docsDir)
    if not outDir: outDir=docsDir
    G = {}
    sys.path.insert(0,topDir)
    from tools.docco.rl_doc_utils import setStory, getStory, RLDocTemplate, defaultPageSize
    from tools.docco import rl_doc_utils
    exec 'from tools.docco.rl_doc_utils import *' in G, G
    from reportlab.lib.utils import open_and_read
    destfn = os.path.join(outDir,'graphguide.pdf')
    doc = RLDocTemplate(destfn,pagesize = pagesize or defaultPageSize)

    #this builds the story
    setStory()
    doc = RLDocTemplate(destfn,pagesize = pagesize or defaultPageSize)
    for f in (
        'ch1_intro',
        'ch2_concepts',
        'ch3_shapes',
        'ch4_widgets',
        'ch5_charts',
        ):
        exec open_and_read(f+'.py',mode='t') in G, G
    del G

    story = getStory()
    if verbose: print 'Built story contains %d flowables...' % len(story)
    doc.build(story)
    if verbose: print 'Saved "%s"' % destfn

def makeSuite():
    "standard test harness support - run self as separate process"
    from tests.utils import ScriptThatMakesFileTest
    return ScriptThatMakesFileTest('../docs/graphguide', 'gengraphguide.py', 'graphguide.pdf')

def main():
    import sys
    verbose = '-s' not in sys.argv
    if not verbose: sys.argv.remove('-s')
    if len(sys.argv) > 1:
        try:
            pagesize = eval(sys.argv[1])
        except:
            print 'Expected page size in argument 1', sys.argv[1]
            raise
        print 'set page size to',sys.argv[1]
    else:
        pagesize = None
    run(pagesize,verbose)

if __name__=="__main__":
    main()
