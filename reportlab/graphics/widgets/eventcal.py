#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/graphics/widgets/eventcal.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/graphics/widgets/eventcal.py,v 1.2 2003/04/01 07:17:15 andy_robinson Exp $
# Event Calendar widget
# author: Andy Robinson
"""This file is a 
"""
__version__=''' $Id: eventcal.py,v 1.2 2003/04/01 07:17:15 andy_robinson Exp $ '''

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
        self.timeColWidth = None  # if declared, use it; otherwise auto-size.
        self.trackRowHeight = 20
        self.data = []  # list of Event objects
        self.trackNames = None
        
        self.startTime = None  #displays ALL data on day if not set
        self.endTime = None    # displays ALL data on day if not set
        self.day = 0


        # we will keep any internal geometry variables
        # here.  These are computed by computeSize(),
        # which is the first thing done when drawing.
        self._talksVisible = []  # subset of data which will get plotted, cache
        self._startTime = None
        self._endTime = None
        self._trackCount = 0
        self._colWidths = []
        self._colLeftEdges = []  # left edge of each column

    def computeSize(self):
        "Called at start of draw.  Sets various column widths"
        self._talksVisible = self.getRelevantTalks(self.data)
        self._trackCount = len(self.getAllTracks())
        self.computeStartAndEndTimes()
        self._colLeftEdges = [self.x]        
        if self.timeColWidth is None:
            w = self.width / (1 + self._trackCount)
            self._colWidths = [w] * (1+ self._trackCount)
            for i in range(self._trackCount):
                self._colLeftEdges.append(self._colLeftEdges[-1] + w)
        else:
            self._colWidths = [self.timeColWidth]
            w = (self.width - self.timeColWidth) / self._trackCount
            for i in range(self._trackCount):
                self._colWidths.append(w)
                self._colLeftEdges.append(self._colLeftEdges[-1] + w)



    def computeStartAndEndTimes(self):
        "Work out first and last times to display"
        if self.startTime:
            self._startTime = self.startTime
        else:
            for (title, speaker, trackId, day, start, duration) in self._talksVisible:

                if self._startTime is None: #first one
                    self._startTime = start
                else:
                    if start < self._startTime:
                        self._startTime = start

        if self.endTime:
            self._endTime = self.endTime
        else:
            for (title, speaker, trackId, day, start, duration) in self._talksVisible:
                if self._endTime is None: #first one
                    self._endTime = start + duration
                else:
                    if start + duration > self._endTime:
                        self._endTime = start + duration
                
                

        
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
            assert trackId <> 0, "trackId must be None or 1,2,3... zero not allowed!"
            if day == self.day:
                if (((self.startTime is None) or ((hours + duration) >= self.startTime)) 
                and ((self.endTime is None) or (hours <= self.endTime))):
                    used.append(talk)
        return used

    def scaleTime(self, theTime):
        "Return y-value corresponding to times given"
        axisHeight = self.height - self.trackRowHeight
        # compute fraction between 0 and 1, 0 is at start of period        
        proportionUp = ((theTime - self._startTime) / (self._endTime - self._startTime))
        y = self.y + axisHeight - (axisHeight * proportionUp)        
        return y
            

    def getTalkRect(self, startTime, duration, trackId):
        "Return shapes for a specific talk"
        y_bottom = self.scaleTime(startTime + duration)
        y_top = self.scaleTime(startTime)
        y_height = y_top - y_bottom

        if trackId is None:
            #spans all columns
            x = self._colLeftEdges[1]
            width = self.width - self._colWidths[0] 
        else:
            #trackId is 1-based and these arrays have the margin info in column
            #zero, so no need to add 1
            x = self._colLeftEdges[trackId]
            width = self._colWidths[trackId]

        r = Rect(x, y_bottom, width, y_height, fillColor=colors.cyan)
        # would expect to color-code and add text
        return r
            
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

        for talk in self._talksVisible:
            (title, speaker, trackId, day, start, duration) = talk
            talkShapes = self.getTalkRect(start, duration, trackId) 
            g.add(talkShapes)

        return g
    



def test():
    "Make a conference event for day 1 of UP Python 2003"
    
    
    d = Drawing(400,200)

    cal = EventCalendar()
    cal.x = 50
    cal.y = 25
    cal.data = [
        # these might be better as objects instead of tuples, since I
        # predict a large number of "optionsl" variables to affect
        # formatting in future.
        
        #title, speaker, track id, day, start time (hrs), duration (hrs)
        # track ID is 1-based not zero-based!
        ('Keynote: Why design another programming language?',  'Guido van Rossum', None, 1, 9.0, 1.0),

        ('Siena Web Service Architecture', 'Marc-Andre Lemburg', 1, 1, 10.5, 1.5),
        ('Extreme Programming in Python', 'Chris Withers', 2, 1, 10.5, 1.5),
        ('Pattern Experiences in C++', 'Mark Radford', 3, 1, 10.5, 1.5),
        ('What is the Type of std::toupper()', 'Gabriel Dos Reis', 4, 1, 10.5, 1.5),
        ('Linguistic Variables: Clear Thinking with Fuzzy Logic ', 'Walter Banks', 5, 1, 10.5, 1.5),

        ('lunch, short presentations, vendor presentations', '', None, 1, 12.0, 2.0),

        ]

    #return cal
    cal.day = 1

    d.add(cal)


    for format in ['pdf']:#,'gif','png']:
        out = d.asString(format)
        open('eventcal.%s' % format, 'wb').write(out)
        print 'saved eventcal.%s' % format

if __name__=='__main__':
    test()
    