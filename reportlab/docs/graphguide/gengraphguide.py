#!/bin/env python
#copyright ReportLab Inc. 2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/docs/graphguide/gengraphguide.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/docs/graphguide/gengraphguide.py,v 1.9 2004/04/28 14:39:23 rgbecker Exp $
__version__=''' $Id: gengraphguide.py,v 1.9 2004/04/28 14:39:23 rgbecker Exp $ '''
__doc__ = """
This module contains the script for building the graphics guide.
"""
def run(pagesize=None, verbose=1, outDir=None):
    import os
    from reportlab.tools.docco.rl_doc_utils import setStory, getStory, RLDocTemplate, defaultPageSize
    from reportlab.tools.docco import rl_doc_utils
    from reportlab.lib.utils import open_and_read, _RL_DIR
    if not outDir: outDir = os.path.join(_RL_DIR,'docs')
    destfn = os.path.join(outDir,'graphguide.pdf')
    doc = RLDocTemplate(destfn,pagesize = pagesize or defaultPageSize)

    #this builds the story
    setStory()
    G = {}
    exec 'from reportlab.tools.docco.rl_doc_utils import *' in G, G
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
    from reportlab.test.utils import ScriptThatMakesFileTest
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
