# idle_print [py2pdf_options] filename
__version__=''' $Id: idle_print.py,v 1.5 2000/04/27 10:46:34 rgbecker Exp $ '''
# you should adjust the globals below to configure for your system

import sys, os, py2pdf, string, time
#whether we remove input/output files; if you get trouble on windows try setting _out to 0
auto_rm_in	= 1
auto_rm_out = 1
viewOnly = 0

#how to call up your acrobat reader
if sys.platform=='win32':
	acrord = 'C:\\Program Files\\Adobe\\Acrobat 4.0\\Reader\\AcroRd32.exe'
	def printpdf(pdfname):
		args = [acrord, pdfname]
		os.spawnv(os.P_WAIT, args[0], args)
else:
	acrord = 'acroread'
	def printpdf(pdfname):
		if viewOnly:
			cmd = "%s %s" % (acrord,pdfname)
		else:
			cmd = "%s -toPostScript < %s | lpr" % (acrord,pdfname)
		os.system(cmd)

args = ['--format=pdf']
files = []
for f in sys.argv[1:]:
	if f[:2]=='--':
		opt = f[2:]
		if opt =='no_auto_rm_in':
			auto_rm_in = 0
		elif opt =='auto_rm_in':
			auto_rm_in = 1
		elif opt =='no_auto_rm_out':
			auto_rm_out = 0
		elif opt =='auto_rm_out':
			auto_rm_out = 1
		elif opt =='viewonly':
			viewOnly = 1
		elif opt[:9] =='acroread=':
			acrord = opt[9:]
		else:
			args.append(f)
	else: files.append(f)

for f in files:
	py2pdf.main(args+[f])
	if auto_rm_in: os.remove(f)
	pdfname = os.path.splitext(f)[0]+'.pdf'
	printpdf(pdfname)
	if auto_rm_out: os.remove(pdfname)
