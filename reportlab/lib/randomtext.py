#!/bin/env python
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/randomtext.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/randomtext.py,v 1.1 2000/12/29 02:06:13 andy_robinson Exp $
__version__=''' $Id: randomtext.py,v 1.1 2000/12/29 02:06:13 andy_robinson Exp $ '''
import string
###############################################################################
#	generates so-called 'Greek Text' for use in filling documents.
###############################################################################
"""
This modules exposes a function randomText() which generates paragraphs.
These can be used when testing out document templates and stylesheets.
A number of 'themes' are provided - please contribute more!
We need some real Greek text too.
"""

#theme one :-)
STARTUP = ['strategic','direction','proactive',
    'reengineering','forecast','resources',
    'forward-thinking','profit','growth','doubletalk','B2B','B2C'
    'venture capital','IPO', "NASDAQ meltdown - we're all doomed!"]



def randomText(theme=STARTUP):
	#this may or may not be appropriate in your company
	from random import randint, choice

	RANDOMWORDS = theme

	sentences = 5
	output = ""
	for sentenceno in range(randint(1,5)):
		output = output + 'Blah'
		for wordno in range(randint(10,25)):
			if randint(0,4)==0:
				word = choice(RANDOMWORDS)
			else:
				word = 'blah'
			output = output + ' ' +word
		output = output+'.'
	return output

