"""
This does a test drawing with lots of things in it, running
with and without attribute checking
"""

__version__ = ''' $Id $ '''


import os, sys, time

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Flowable
from reportlab.test import unittest


def run(isFast):
    

    """Hello World, on a rectangular background.

    The rectangle's fillColor is yellow.
    The string's fillColor is red.
    """
    import reportlab.config
    reportlab.config.shapeChecking = not isFast
    from reportlab.graphics.shapes import *
    from reportlab.graphics.charts.piechart0 import PieWithWedges
        
    pdfPath = 'test_graphics_speed_fast.pdf'
    c = Canvas(pdfPath)
    t0 = time.time()

    d = Drawing(400, 200)
    num = 100
    for i in range(num):
        pc = PieWithWedges()
        pc.x = 150
        pc.y = 50
        pc.data = [10,20,30,40,50,60]
        pc.labels = ['a','b','c','d','e','f']
        pc.wedges.strokeWidth=0.5
        pc.wedges[3].popout = 20
        pc.wedges[3].strokeWidth = 2
        pc.wedges[3].strokeDashArray = [2,2]
        pc.wedges[3].labelRadius = 1.75
        pc.wedges[3].fontColor = colors.red
        d.add(pc)
    d.drawOn(c, 80, 500)

    t1 = time.time()
    print 'drew %d pie charts in %0.4f' % (num, t1 - t0)

def profile():
    import profile
    profile.run('run(0)')

if __name__ == "__main__":
    usage = 'Usage: test_graphics_speed [ fast | slow | profile ]'
    if len(sys.argv) < 2:
        print usage
    elif sys.argv[1] not in ('fast','slow','profile'):
        print usage
    else:
        arg = sys.argv[1]
        if arg == 'profile':
            profile()
        elif arg == 'fast':
            run(1)
        elif arg == 'slow':
            run(0)