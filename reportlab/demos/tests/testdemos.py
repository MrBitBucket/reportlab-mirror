_globals=globals().copy()
import os, sys
import pdfgen

for p in ('pythonpoint/pythonpoint.py','stdfonts/stdfonts.py','odyssey/odyssey.py', 'gadflypaper/gfe.py'):
	fn = os.path.normcase(os.path.normpath(os.path.join(os.path.dirname(pdfgen.__file__),'..','demos',p)))
	os.chdir(os.path.dirname(fn))
	execfile(fn,_globals.copy())
