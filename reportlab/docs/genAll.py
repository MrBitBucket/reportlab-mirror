#!/bin/env python
import os, sys
def _genAll(d=None,verbose=None):
	if not d: d = '.'
	if not os.path.isabs(d):
		d = os.path.normpath(os.path.join(os.getcwd(),d))
	for p in ('reference/genreference.py',
			  'userguide/genuserguide.py',
			  'graphguide/gengraphguide.py',
			  '../tools/docco/graphdocpy.py'):
		os.chdir(d)
		os.chdir(os.path.dirname(p))
		cmd = '%s %s %s' % (sys.executable,os.path.basename(p), verbose and '-s' or '')
		if verbose>=2: print cmd
		os.system(cmd)

"""Runs the manual-building scripts"""
if __name__=='__main__':
	#need a quiet mode for the test suite	
	if '-s' in sys.argv:  # 'silent
		quiet = '-s'
	else:
		quiet = ''
	_genAll(os.path.dirname(sys.argv[0]),quiet)
