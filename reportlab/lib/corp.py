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
#	$Log: corp.py,v $
#	Revision 1.1  2000/03/08 12:53:49  andy_robinson
#	initial checkin
#

""" This module includes some reusable routines for ReportLab's
 'Corporate Image' - the logo, standard page backdrops and
 so on - you are advised to do the same for your own company!"""
__version__=''' $Id: corp.py,v 1.1 2000/03/08 12:53:49 andy_robinson Exp $ '''

from reportlab.lib.units import inch

class ReportLabLogo:
    """vector reportlab logo centered in a 250x by 150y rectangle"""
    
    def __init__(self, atx=0, aty=0, width=2.5*inch, height=1.5*inch, powered_by=0):
        self.origin = (atx, aty)
        self.dimensions = (width, height)
        self.powered_by = powered_by
        
    dogrid = 0
    xticks = 25
    yticks = 15
    def draw(self, canvas):
        canvas.saveState()
        (atx,aty) = self.origin
        canvas.translate(atx, aty)
        (width, height) = self.dimensions
        canvas.scale(width/250.0, height/150.0)
        # do a skew
        canvas.skew(0,20)
        self.setup(canvas)
        if self.powered_by:
            canvas.setFont("Helvetica-Bold", 18)
            canvas.drawString(-15, 135, "powered by")
        # do a stretched "ReportLab"
        canvas.saveState()
        canvas.setFont("Helvetica-Bold", 30)
        canvas.scale(1.65,1)
        canvas.drawString(0,60,"ReportLab")
        canvas.restoreState()
        # draw the "page" as a bunch of rectangles
        rects = [
        #  x  y  h, w
         [65,10,40,8], # below p
         [65,53,22.5,8], # over p
         [65,78,50,8], # above p
         [65,123,7,75], # across top
         [161,86,29,9], # above L
         [161,60.5,21,9], # over L
         [161,10,47,9], # below L
         [65,10,7,102], # across bottom
         [140,110,20,10], # notch vertical
         [140,110,7,29.5],# notch horizontal
         ]
        fill = 1
        for [x,y,h,w] in rects:
            canvas.rect(x,y,w,h, stroke=1, fill=fill)
            #break
        path = canvas.beginPath()
        path.moveTo(150,130)
        for (x,y) in ((170,115), (167,112), (147,127)):
            path.lineTo(x,y)
        #path.close()
        canvas.drawPath(path, stroke=1, fill=fill)
        canvas.restoreState()
   
    def setup(self, canvas):
        xticks, yticks = self.xticks, self.yticks
        if self.dogrid:
            canvas.saveState()
            for y in range(yticks):
                if y%5==0:
                     canvas.setStrokeColorRGB(1,0,0)
                canvas.line(0,y*10,xticks*10,y*10)
                if y%5==0:
                     canvas.setStrokeColorRGB(0,1,0)
            for x in range(xticks):
                if x%5==0:
                     canvas.setStrokeColorRGB(1,0,0)
                canvas.line(x*10,yticks*10,x*10,0)
                if x%5==0:
                     canvas.setStrokeColorRGB(0,1,0)
            canvas.restoreState()

def main(filename, logomaker):
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(filename)
    #c.translate(inch,inch)
    # scale each point to a quarter inch/10
    #tqinch = inch/40.0
    #c.scale(tqinch, tqinch)
    logomaker.draw(c)
    c.save()
    
if __name__=="__main__":
    logomaker = ReportLabLogo(inch, 8*inch, powered_by=1)
    main("logo.pdf", logomaker)
    







