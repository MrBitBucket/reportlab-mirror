from string import find, strip
import os
def cvs_status(path):
	"Extract a list of paths from a CVS statuts command response file."
	cwd = os.getcwd()
	try:
		os.chdir(path)
		repos = open(os.path.join('CVS','Repository'),'r').readlines()[0][:-1]+'/'
		cmd = os.popen('CVS -z9 status','r')
		lines = cmd.readlines()
		cmd.close()
		unknown = filter(lambda x:find(x, "? ") == 0, lines)
		unknown = map(lambda x:strip(x[2:]), unknown)
		status = filter(lambda x:find(x, "File:") == 0, lines)
		status = map(lambda x:strip(x[find(x, 'Status: ')+8:]), status)
		paths = filter(lambda x:find(x, "Repository revision:") >= 0, lines)
		paths = map(lambda x,y=repos:x[find(x, y)+len(y):], paths)
		paths = map(lambda x:x[:find(x, ',v')], paths)
	finally:
		os.chdir(cwd)
	return map(None,paths+unknown,status+len(unknown)*['Unknown'])

if __name__=='__main__':
	import sys
	if len(sys.argv)==1:
		fn = '.'
	else:
		fn = sys.argv[1]
	for i in cvs_status(fn):
		print i
