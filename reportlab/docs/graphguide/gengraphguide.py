#!/bin/env python
#copyright ReportLab Inc. 2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/docs/graphguide/gengraphguide.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/docs/graphguide/gengraphguide.py,v 1.3 2001/10/28 21:18:03 andy_robinson Exp $
__version__=''' $Id: gengraphguide.py,v 1.3 2001/10/28 21:18:03 andy_robinson Exp $ '''
__doc__ = """
This module contains the script for building the graphics guide.
"""
from reportlab.tools.docco.rl_doc_utils import *
def run(pagesize, verbose=1):
	doc = RLDocTemplate('graphguide.pdf',pagesize = pagesize)
	import ch1_intro
	import ch2_concepts
	import ch3_shapes
	import ch4_widgets
	import ch5_charts

	story = getStory()
	if verbose: print 'Built story contains %d flowables...' % len(story)
	doc.build(story)
	if verbose: print 'Saved graphguide.pdf'

	# copy to target
	import reportlab
	docdir = os.path.dirname(reportlab.__file__) + os.sep + 'docs'
	destfn = docdir + os.sep + 'graphguide.pdf'
	import shutil
	shutil.copyfile('graphguide.pdf',
					destfn)
	if verbose: print 'copied to %s' % destfn

	# remove *.pyc files
	pat = os.path.join(os.path.dirname(sys.argv[0]), '*.pyc')
	for file in glob.glob(pat):
		os.remove(file)

def makeSuite():
    "standard test harness support - run self as separate process"
    from reportlab.test.utils import ScriptThatMakesFileTest
    return ScriptThatMakesFileTest('../docs/graphguide',
								   'gengraphguide.py',
								   'graphguide.pdf')

if __name__=="__main__":
	verbose = '-s' not in sys.argv
	if not verbose: sys.argv.remove('-s')
	if len(sys.argv) > 1:
		try:
			(w, h) = eval(sys.argv[1])
		except:
			print 'Expected page size in argument 1', sys.argv[1]
			raise
		print 'set page size to',sys.argv[1]
	else:
		(w, h) = defaultPageSize
	run((w, h),verbose)
