from reportlab.lib import colors
from reportlab.lib.attrmap import *
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics.shapes import Group, Drawing, Ellipse, Wedge, String, STATE_DEFAULTS, Polygon, Line

def _getShaded(col,shd=None,shading=0.1):
    if shd is None:
        from reportlab.lib.colors import Blacker
        if col: shd = Blacker(col,1-shading)
    return shd

def _draw_3d_bar(G, x1, x2, y0, yhigh, xdepth, ydepth,
                fillColor=None, fillColorShaded=None,
                strokeColor=None, strokeWidth=1, shading=0.1):
    fillColorShaded = _getShaded(fillColor,fillColorShaded,shading)

    def _add_3d_bar(x1, x2, y1, y2, xoff, yoff,
                    G=G,strokeColor=strokeColor, strokeWidth=strokeWidth, fillColor=fillColor):
        G.add(Polygon((x1,y1,x1+xoff, y1-yoff,x2+xoff, y2-yoff,x2,y2),
            strokeWidth=strokeWidth, strokeColor=strokeColor, fillColor=fillColor))

    usd = max(y0, yhigh)
    if xdepth or ydepth:
        if y0!=yhigh:   #non-zero height
            _add_3d_bar( x2, x2, y0, yhigh, xdepth, ydepth,fillColor=fillColorShaded) #side

        _add_3d_bar(x1, x2, usd, usd, xdepth, ydepth)   #top

    G.add(Polygon((x1,y0,x2,y0,x2,yhigh,x1,yhigh),
        strokeColor=strokeColor, strokeWidth=strokeWidth, fillColor=fillColor)) #front

    if xdepth or ydepth:
        G.add(Line( x1, usd, x2, usd, strokeWidth=strokeWidth, strokeColor=strokeColor or fillColorShaded))

from math import pi, sin, cos
_pi_2 = pi*0.5
_2pi = 2*pi
_180_pi=180./pi

def _2rad(angle):
    return (angle*pi)/180

def mod_2pi(radians):
    radians = radians % _2pi
    if radians<-1e-6: radians += _2pi
    return radians

def _2deg(o):
    return o*_180_pi

def _360(a):
    a %= 360
    if a<-1e-6: a += 360
    return a


if __name__=='__main__':
    from reportlab.graphics.shapes import Drawing
    from reportlab.lib.colors import lightgrey, pink
    D = Drawing(300,200)
    #_draw_3d_bar(D, 10, 20, 10, 50, 5, -5, fillColor=lightgrey, strokeColor=pink)
    #_draw_3d_bar(D, 30, 40, 10, 45, 5, -5, fillColor=lightgrey, strokeColor=pink)
    D.add(Pie3d())
    D.save(formats=['pdf'],outDir='.',fnRoot='_draw_3d_bar')
