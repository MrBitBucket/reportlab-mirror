#!/bin/env python
###############################################################################
#
#	ReportLab Public License Version 1.0
#
#   Except for the change of names the spirit and intention of this
#   license is the same as that of Python
#
#	(C) Copyright ReportLab Inc. 1998-2000.
#
#   adapted with permission from PIDDLE, original author Joe Strout
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
#	$Log: pagesizes.py,v $
#	Revision 1.2  2000/03/08 13:40:49  rgbecker
#	Added DEFAULT_PAGE_SIZE at end
#
#	Revision 1.1  2000/03/08 12:55:07  andy_robinson
#	initial checkin
#	

"""This module defines a few common page sizes in points (1/72 inch).
To be expanded to include things like label sizes, envelope windows
etc."""
__version__=''' $Id: pagesizes.py,v 1.2 2000/03/08 13:40:49 rgbecker Exp $ '''

from units import cm, inch

_W, _H = (21*cm, 29.7*cm)

A6 = (_W*.5, _H*.5)
A5 = (_H*.5, _W)
A4 = (_W, _H)
A3 = (_H*2, _W)
A2 = (_W*2, _H*2)
A1 = (_H*4, _W*2)
A0 = (_W*4, _H*4)

letter = (8.5*inch, 11*inch)
legal = (8.5*inch, 17*inch)
elevenSeventeen = (11*inch, 17*inch)

_BW, _BH = (25*cm, 35.3*cm)
B6 = (_BW*.5, _BH*.5)
B5 = (_BH*.5, _BW)
B4 = (_BW, _BH)
B3 = (_BH*2, _BW)
B2 = (_BW*2, _BH*2)
B1 = (_BH*4, _BW*2)
B0 = (_BW*4, _BH*4)

#change this to suit your average needs
DEFAULT_PAGE_SIZE = A4
