#!/usr/local/bin/python
###############################################################################
#
#	ReportLab Public License Version 1.0
#
#   Except for the change of names the spirit and intention of this
#   license is the same as that of Python
#
#	(C) Copyright ReportLab Inc. 1998-2000.
#
#
# All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted, provided
# that the above copyright notice appear in all copies and that both that
# copyright notice and this permission notice appear in supporting
# documentation, and that the name of ReportLab not be used
# in advertising or publicity pertaining to distribution of the software
# without specific, written prior permission. 
# 
#
# Disclaimer
#
# ReportLab Inc. DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS,
# IN NO EVENT SHALL ReportLab BE LIABLE FOR ANY SPECIAL, INDIRECT
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#
###############################################################################
#	$Log: idle_print.py,v $
#	Revision 1.3  2000/04/25 12:15:10  rgbecker
#	Linux fixes
#
#	Revision 1.2  2000/04/21 13:15:22  rgbecker
#	Changed to spawnve
#	
#	Revision 1.1  2000/04/20 12:19:35  rgbecker
#	Initial interface script for idle
#	
__version__=''' $Id: idle_print.py,v 1.3 2000/04/25 12:15:10 rgbecker Exp $ '''
# this is a simple script to convert a specified input file to pdf
# it should have only filename arguments; these are assumed temporary
# and will be removed unless there's a -noremove flag.
# you should adjust the globals below to configure for your system

import sys, os, py2pdf, string, time
#whether we remove input/output files; if you get trouble on windows try setting _out to 0
auto_rm_in	= 1
auto_rm_out = 1

#formatting options to be passed to the py2pdf program. see below for others
py2pdf_options = ['--format=pdf','--mode=color','--paperFormat=A4']

#how to call up your acrobat reader, will get changed at run time
if sys.platform=='win32':
	useSpawn = 1
	# under win32 we can't get to a PS file so use acrord32 to come up as normal
	acrord = 'C:\\Program Files\\Adobe\\Acrobat 4.0\\Reader\\AcroRd32.exe'
	argstr = '%s'
else:
	useSpawn = 0
	# change /opt to /usr/local if that's where you installed Acrobat4
	acrord = '/opt/Acrobat4/bin/acroread'
	argstr = '-toPostScript'
	filterCmd = '/usr/local/bin/myFilter'

for f in sys.argv[1:]:
	print f
	py2pdf.main(py2pdf_options + [f])
	if auto_rm_in: os.remove(f)
	pdfname = os.path.splitext(f)[0]+'.pdf'
	if useSpawn:
		args = [acrord] + string.split(argstr%pdfname,',')
		print args, os.spawnve(os.P_WAIT,args[0],args,os.environ)
	else:
		cmd = "cat %s | %s %s | %s" % (pdfname,acrord,argstr,filterCmd)
		os.system(cmd)

	if auto_rm_out: os.remove(pdfname)

#########################################################################
# the script ends here the stuff below is for info only
#########################################################################
#
#    py2pdf options:
#     -h  or  --help    print help (this message)
#     -                 read from stdin, write to stdout
#     --stdout          read from files, write to stdout
#     --config=<file>   read configuration options from <file> 
#     --format=<format> set output format
#                         'pdf': output as PDF (default)
#                         'txt': output as tagged plain text
#     --mode:<mode>     set output mode
#                         'color': output in color (default)
#                         'mono':  output b/w
#     --paperFormat=    set paper format (ISO A, B, C series, 
#       <format>        US legal, letter; default: A4)
#     --paperSize=      set paper size in points (size being a valid
#       <size>          numeric 2-tuple (x,y) w/o any whitespace)  
#     --landscape       set landscape format (default: portrait)
#     --bgCol=<col>     set page background-color in hex code like
#                         '#FFA024' or '0xFFA024' for RGB components
#                         (overwrites mono mode)
#     --<cat>Col=<col>  set color of certain code categories, i.e.
#                         <cat> can be the following:
#                         'comm':  comments 
#                         'ident': identifiers
#                         'kw':    keywords
#                         'strng': strings
#                         'param': parameters
#                         'rest':  all the rest
#     --fontName=<name> set base font name (default: 'Courier')
#     --fontSize=<size> set font size (default: 8)
#     --lineNum         print line numbers
#     --multiPage       generate one file per page (labeled 1, 2...)
#     -v  or  --verbose set verbose mode
