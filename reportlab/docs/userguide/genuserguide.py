#!/bin/env python
#copyright ReportLab Inc. 2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/docs/userguide/genuserguide.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/docs/userguide/genuserguide.py,v 1.10 2001/12/20 13:55:55 rgbecker Exp $

__version__=''' $Id: genuserguide.py,v 1.10 2001/12/20 13:55:55 rgbecker Exp $ '''

__doc__ = """
This module contains the script for building the user guide.
"""

from reportlab.tools.docco.rl_doc_utils import *

def run(pagesize=defaultPageSize, verbose=0, outDir=None):

	# copy to target
	import reportlab
	if not outDir: outDir = os.path.join(os.path.dirname(reportlab.__file__),'docs')
	destfn = os.path.join(outDir,'userguide.pdf')
	doc = RLDocTemplate(destfn,pagesize = pagesize)

	#this builds the story
	#resetStory()

	import ch1_intro
	import ch2_graphics
	import ch2a_fonts
	import ch3_pdffeatures
	import ch4_platypus_concepts
	import ch5_paragraphs
	import ch6_tables
	import ch7_custom
	import ch9_future

	import app_demos

	story = getStory()
	if verbose: print 'Built story contains %d flowables...' % len(story)
	doc.build(story)
	if verbose: print 'Saved "%s"' % destfn

	# remove *.pyc files
	pat = os.path.join(os.path.dirname(sys.argv[0]), '*.pyc')
	for file in glob.glob(pat):
		os.remove(file)


def makeSuite():
	"standard test harness support - run self as separate process"
	from reportlab.test.utils import ScriptThatMakesFileTest
	return ScriptThatMakesFileTest('../docs/userguide', 'genuserguide.py', 'userguide.pdf') 

if __name__=="__main__":
	outDir = filter(lambda x: x[:9]=='--outdir=',sys.argv)
	if outDir:
		outDir = outDir[0]
		sys.argv.remove(outDir)
		outDir = outDir[9:]
	else:
		outDir = None
	verbose = '-s' not in sys.argv
	if not verbose: sys.argv.remove('-s')
	timing = '-timing' in sys.argv
	if timing: sys.argv.remove('-timing')
	prof = '-prof' in sys.argv
	if prof: sys.argv.remove('-prof')

	if len(sys.argv) > 1:
		try:
			(w, h) = eval(sys.argv[1])
		except:
			print 'Expected page size in argument 1', sys.argv[1]
			raise
		if verbose:
			print 'set page size to',sys.argv[1]
	else:
		(w, h) = defaultPageSize
	if timing:
		from time import time
		t0 = time()
		run((w, h), verbose,outDir)
		if verbose:
			print 'Generation of userguide took %.2f seconds' % (time()-t0)
	elif prof:
		import profile
		profile.run('run((w, h),verbose,outDir)','genuserguide.stats')
	else:
		run((w, h), verbose,outDir)
