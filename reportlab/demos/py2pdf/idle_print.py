# idle_print [py2pdf_options] filename
__version__=''' $Id: idle_print.py,v 1.4 2000/04/26 13:00:17 rgbecker Exp $ '''
# you should adjust the globals below to configure for your system

import sys, os, py2pdf, string, time
#whether we remove input/output files; if you get trouble on windows try setting _out to 0
auto_rm_in	= 1
auto_rm_out = 1

#how to call up your acrobat reader
if sys.platform=='win32':
	acrord = 'C:\\Program Files\\Adobe\\Acrobat 4.0\\Reader\\AcroRd32.exe'
	def printpdf(pdfname):
		args = [acrord, pdfname]
		os.spawnv(os.P_WAIT, args[0], args)
else:
	acrord = '/opt/Acrobat4/bin/acroread'
	def printpdf(pdfname):
		cmd = "%s -toPostScript < %s | lpr" % (acrord,pdfname)
		os.system(cmd)

args = ['--format=pdf']
files = []
for f in sys.argv[1:]:
	if f[:2]=='--':
		if f[2:]=='no_auto_rm_in':
			auto_rm_in = 0
		elif f[2:]=='auto_rm_in':
			auto_rm_in = 1
		elif f[2:]=='no_auto_rm_out':
			auto_rm_out = 0
		elif f[2:]=='auto_rm_out':
			auto_rm_out = 1
		else:
			args.append(f)
	else: files.append(f)

for f in files:
	py2pdf.main(args+[f])
	if auto_rm_in: os.remove(f)
	pdfname = os.path.splitext(f)[0]+'.pdf'
	printpdf(pdfname)
	if auto_rm_out: os.remove(pdfname)
