#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/widgets/eventcal.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/widgets/eventcal.py,v 1.1 2003/03/28 17:30:48 andy_robinson Exp $
# Event Calendar widget
# author: Andy Robinson
"""This file is a 
"""
__version__=''' $Id: eventcal.py,v 1.1 2003/03/28 17:30:48 andy_robinson Exp $ '''

from reportlab.lib import colors
from reportlab.lib.validators import *
from reportlab.lib.attrmap import *
from reportlab.graphics.shapes import Line, Rect, Polygon, Drawing, Group, String, Circle, Wedge
from reportlab.graphics.widgetbase import Widget
from reportlab.graphics import renderPDF




class EventCalendar(Widget):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 300
        self.height = 150
        self.timeColWidth = None
        self.trackRowHeight = 20
        self.data = []  # list of Event objects
        self.trackNames = None
        
        self.startTime = 0.0
        self.endTime = 24.0
        self.day = 0

        self._trackCount = 0
        self._colWidths = []        

    def computeSize(self):
        "Called at start of draw.  Sets various column widths"
        self._talksVisible = self.getRelevantTalks(self.data)
        self._trackCount = len(self.getAllTracks())
        print '%d tracks' % self._trackCount
        if self.timeColWidth is None:
            w = self.width / (1 + self._trackCount)
            self._colWidths = [w] * (1+ self._trackCount)
        else:
            self._colWidths = [self.timeColWidth]
            w = (self.width - self.timeColWidth) / self._trackCount
            for i in range(self._trackCount):
                self._colWidths.append(w)
            
    def getAllTracks(self):
        tracks = []
        for (title, speaker, trackId, day, hours, duration) in self.data:
            if trackId is not None:
                if trackId not in tracks:
                    tracks.append(trackId)
        tracks.sort()
        return tracks
        
    def getRelevantTalks(self, talkList):
        "Scans for tracks actually used"
        used = []
        for talk in talkList:
            (title, speaker, trackId, day, hours, duration) = talk
            if day == self.day:
                if (hours + duration) >= self.startTime and (hours <= self.endTime):
                    used.append(talk)
       

    def draw(self):
        self.computeSize()
        g = Group()

        # time column
        g.add(Rect(self.x, self.y, self._colWidths[0], self.height - self.trackRowHeight, fillColor=colors.cornsilk))

        # track headers
        x = self.x + self._colWidths[0]
        y = self.y + self.height - self.trackRowHeight
        for trk in range(self._trackCount):
            wid = self._colWidths[trk+1]
            r = Rect(x, y, wid, self.trackRowHeight, fillColor=colors.yellow)
            s = String(x + 0.5*wid, y, 'Track %d' % trk, align='middle')
            g.add(r)
            g.add(s)
            x = x + wid
        return g
    



def test():
    "Make a conference event for day 1 of UP Python 2003"
    
    
    d = Drawing(400,200)

    cal = EventCalendar()
    cal.x = 50
    cal.y = 25

    cal.data = [
        #title, speaker, track id, day, start time (hrs), duration (hrs) 
        ('Keynote: Why design another programming language?',  'Guido van Rossum', None, 1, 9.0, 1.0),
        ('Siena Web Service Architecture', 'Marc-Andre Lemburg', 1, 1, 10.5, 1.5),
        ('Extreme Programming in Python', 'Chris Withers', 2, 1, 10.5, 1.5),
        ]

    #return cal
    cal.day = 1

    d.add(cal)


    for format in ['pdf','gif','png']:
        out = d.asString(format)
        open('eventcal.%s' % format, 'wb').write(out)
        print 'saved eventcal.%s' % format

if __name__=='__main__':
    test()
    