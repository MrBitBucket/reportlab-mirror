###############################################################################
#
#	ReportLab Public License Version 1.0
#
#	Except for the change of names the spirit and intention of this
#	license is the same as that of Python
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
#	$Log: fodyssey.py,v $
#	Revision 1.8  2000/05/13 09:23:45  rgbecker
#	Fix spacing bugs
#
#	Revision 1.7  2000/05/12 16:19:07  rgbecker
#	Title leading changes
#	
#	Revision 1.6  2000/05/12 14:19:03  andy_robinson
#	Added 'if __name__=='__main__'' handlers to demos
#	
#	Revision 1.5  2000/05/12 12:49:38  rgbecker
#	Minor fixes and changes for comparison with dodyssey.py
#	
#	Revision 1.4  2000/04/14 12:17:05  rgbecker
#	Splitting layout.py
#	
#	Revision 1.3  2000/04/13 14:48:41  rgbecker
#	<para> tag added in layout.py paraparser.py
#	
#	Revision 1.2  2000/04/12 16:24:34  rgbecker
#	XML Tagged Paragraph parser changes
#	
#	Revision 1.1  2000/04/06 08:58:09  rgbecker
#	Paragraph formatting version of odyssey.py
#	
__version__=''' $Id: fodyssey.py,v 1.8 2000/05/13 09:23:45 rgbecker Exp $ '''
__doc__=''

#REPORTLAB_TEST_SCRIPT
import sys, copy, string, os
from reportlab.platypus import layout
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY

styles = getSampleStyleSheet()

Title = "The Odyssey"
Author = "Homer"

def myFirstPage(canvas, doc):
	canvas.saveState()
	canvas.restoreState()
	
def myLaterPages(canvas, doc):
	canvas.saveState()
	canvas.setFont('Times-Roman',9)
	canvas.drawString(inch, 0.75 * inch, "Page %d" % doc.page)
	canvas.restoreState()
	
def go():
	doc = layout.SimpleFlowDocument('fodyssey.pdf',layout.DEFAULT_PAGE_SIZE,showBoundary=0)
	doc.onFirstPage = myFirstPage
	doc.onNewPage = myLaterPages
	doc.build(Elements)

Elements = []

ChapterStyle = copy.copy(styles["Heading1"])
ChapterStyle.alignment = TA_CENTER
ChapterStyle.fontsize = 16
InitialStyle = copy.deepcopy(ChapterStyle)
InitialStyle.fontsize = 16
InitialStyle.leading = 20
PreStyle = styles["Code"] 

def newPage():
	Elements.append(layout.PageBreak())

def chapter(txt, style=ChapterStyle):
	newPage()
	Elements.append(Paragraph(txt, style))
	Elements.append(layout.Spacer(0.2*inch, 0.3*inch))

def fTitle(txt,style=InitialStyle):
	Elements.append(Paragraph(txt, style))

ParaStyle = copy.deepcopy(styles["Normal"])
ParaStyle.spaceBefore = 0.1*inch
if 'right' in sys.argv:
	ParaStyle.alignment = TA_RIGHT
elif 'left' in sys.argv:
	ParaStyle.alignment = TA_LEFT
elif 'justify' in sys.argv:
	ParaStyle.alignment = TA_JUSTIFY
elif 'center' in sys.argv or 'centre' in sys.argv:
	ParaStyle.alignment = TA_CENTER
else:
	ParaStyle.alignment = TA_JUSTIFY

def spacer(inches):
	Elements.append(layout.Spacer(0.1*inch, inches*inch))

def p(txt, style=ParaStyle):
	Elements.append(Paragraph(txt, style))

def pre(txt, style=PreStyle):
	spacer(0.1)
	p = layout.Preformatted(txt, style)
	Elements.append(p)

def parseOdyssey(fn):
	from time import time
	E = []
	t0=time()
	L = open(fn,'r').readlines()
	t1 = time()
	print "open(%s,'r').readlines() took %.4f seconds" %(fn,t1-t0)
	for i in xrange(len(L)):
		if L[i][-1]=='\012':
			L[i] = L[i][:-1]
	t2 = time()
	print "Removing all linefeeds took %.4f seconds" %(t2-t1)
	L.append('')
	L.append('-----')

	def findNext(L, i):
		while 1:
			if string.strip(L[i])=='':
				del L[i]
				kind = 1
				if i<len(L):
					while string.strip(L[i])=='':
						del L[i]

					if i<len(L):
						kind = L[i][-1]=='-' and L[i][0]=='-'
						if kind:
							del L[i]
							if i<len(L):
								while string.strip(L[i])=='':
									del L[i]
				break
			else:
				i = i + 1

		return i, kind

	f = s = 0
	while 1:
		f, k = findNext(L,0)
		if k: break

	E.append([spacer,2])
	E.append([fTitle,'<font color=red>%s</font>' % Title, InitialStyle])
	E.append([fTitle,'<font size=-4>by</font> <font color=green>%s</font>' % Author, InitialStyle])

	while 1:
		if f>=len(L): break

		if string.upper(L[f][0:5])=='BOOK ':
			E.append([chapter,L[f]])
			f=f+1
			while string.strip(L[f])=='': del L[f]
			style = ParaStyle
			func = p
		else:
			style = PreStyle
			func = pre
	
		while 1:
			s=f
			f, k=findNext(L,s)
			sep= (func is pre) and '\012' or ' '
			E.append([func,string.join(L[s:f],sep),style])
			if k: break
	t3 = time()
	print "Parsing into memory took %.4f seconds" %(t3-t2)
	del L
	t4 = time()
	print "Deleting list of lines took %.4f seconds" %(t4-t3)
	for i in xrange(len(E)):
		apply(E[i][0],E[i][1:])
	t5 = time()
	print "Moving into platypus took %.4f seconds" %(t5-t4)
	del E
	t6 = time()
	print "Deleting list of actions took %.4f seconds" %(t6-t5)
	go()
	t7 = time()
	print "saving to PDF took %.4f seconds" %(t7-t6)
	print "Total run took %.4f seconds"%(t7-t0)

for fn in ('Odyssey.full.txt','Odyssey.txt'):
	if os.path.isfile(fn):
		break
if __name__=='__main__':
	parseOdyssey(fn)
