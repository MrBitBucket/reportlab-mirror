#!/bin/env python
if __name__=='__main__':
	import os, sys
	for p in ('../reference/genreference.py', '../userguide/genuserguide.py',
			'../graphguide/gengraphguide.py'):
		os.chdir(os.path.dirname(sys.argv[0]))
		os.chdir(os.path.dirname(p))
		os.system('%s %s' % (sys.executable,os.path.basename(p)))
