#!/bin/env python
#copyright ReportLab Inc. 2001
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/docs/userguide/genuserguide.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/docs/userguide/genuserguide.py,v 1.2 2001/10/26 13:15:41 rgbecker Exp $

__version__=''' $Id: genuserguide.py,v 1.2 2001/10/26 13:15:41 rgbecker Exp $ '''

__doc__ = """
This module contains the script for building the user guide.
"""

import os, sys
sys.path.insert(0,os.path.join('..','tools'))
from rl_doc_utils import *

def run(pagesize):

	doc = RLDocTemplate('userguide.pdf',pagesize = pagesize)

	#this builds the story
	#resetStory()

	import ch1_intro
	import ch2_graphics
	import ch3_pdffeatures
	import ch4_platypus_concepts
	import ch5_paragraphs
	import ch6_tables
	import ch7_custom
	import ch9_future

	import app_demos

	story = getStory()
	print 'Built story contains %d flowables...' % len(story)
	doc.build(story)
	print 'Saved userguide.pdf'

	# copy to target
	import reportlab
	docdir = os.path.dirname(reportlab.__file__) + os.sep + 'docs'
	destfn = docdir + os.sep + 'userguide.pdf'
	import shutil
	shutil.copyfile('userguide.pdf',
					destfn)
	print 'copied to %s' % destfn
	
	# remove *.pyc files
	pat = os.path.join(os.path.dirname(sys.argv[0]), '*.pyc')
	for file in glob.glob(pat):
		os.remove(file)


def makeSuite():
    "standard test harness support - run self as separate process"
    from reportlab.test.utils import ScriptThatMakesFileTest
    return ScriptThatMakesFileTest('../docs/userguide',
								   'genuserguide.py',
								   'userguide.pdf')

if __name__=="__main__":
	prof = '-prof' in sys.argv
	if prof: sys.argv.remove('-prof')
	if len(sys.argv) > 1:
		try:
			(w, h) = eval(sys.argv[1])
		except:
			print 'Expected page size in argument 1', sys.argv[1]
			raise
		print 'set page size to',sys.argv[1]
	else:
		(w, h) = defaultPageSize
	if prof:
		import profile
		profile.run('run((w, h))','genuserguide.stats')
	else:
		run((w, h))
