#!/bin/env python
if __name__=='__main__':
	import os, sys
	d = os.path.dirname(sys.argv[0])
	if not d: d = '.'
	if not os.path.isabs(d):
		d = os.path.normpath(os.path.join(os.getcwd(),d))
	for p in ('../reference/genreference.py', '../userguide/genuserguide.py',
			'../graphguide/gengraphguide.py'):
		os.chdir(d)
		os.chdir(os.path.dirname(p))
		os.system('%s %s' % (sys.executable,os.path.basename(p)))
