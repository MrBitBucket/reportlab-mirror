#!/bin/env python
import os, sys
def _genAll(d=None,quiet=''):
	if not d: d = '.'
	if not os.path.isabs(d):
		d = os.path.normpath(os.path.join(os.getcwd(),d))
	for p in ('reference/genreference.py',
			  'userguide/genuserguide.py',
			  'graphguide/gengraphguide.py',
			  '../tools/docco/graphdocpy.py'):
		os.chdir(d)
		os.chdir(os.path.dirname(p))
		os.system('%s %s %s' % (sys.executable,os.path.basename(p), quiet))

"""Runs the manual-building scripts"""
if __name__=='__main__':
	#need a quiet mode for the test suite	
	if '-s' in sys.argv:  # 'silent
		quiet = '-s'
	else:
		quiet = ''
	_genAll(os.path.dirname(sys.argv[0]),quiet)
