#Copyright ReportLab Europe Ltd. 2000-2006
#see license.txt for license details
__version__=''' $Id$ '''
def anchorAdjustXY(anchor,x,y,width,height):
    if anchor not in ('sw','s','se'):
        if anchor in ('e','c','w'):
            y += height/2.
        else:
            y += height
    if anchor not in ('nw','w','sw'):
        if anchor in ('n','c','s'):
            x -= width/2.
        else:
            x -= width
    return x,y

def aspectRatioFix(preserve,width,height,imWidth,imHeight):
    if width is None:
        width = imWidth
    if height is None:
        height = imHeight
    if preserve:
        scale = min(width/float(imWidth),height/float(imHeight))
        width = scale*imWidth-1e-8
        height = scale*imHeight-1e-8
    return width, height
