#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/pdfgen/pdfimages.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/pdfgen/pdfimages.py,v 1.7 2001/01/12 21:36:57 dinu_gherman Exp $
__version__=''' $Id: pdfimages.py,v 1.7 2001/01/12 21:36:57 dinu_gherman Exp $ '''
__doc__="""
Image functionality sliced out of canvas.py for generalization
"""

import os
import string
import cStringIO
from types import StringType
from reportlab.pdfbase import pdfutils
from reportlab.lib.utils import fp_str
from reportlab.lib.logger import warnOnce


try:
    import zlib
except ImportError:
    zlib = None


class PDFImage:
    def __init__(self, image, x,y, width=None, height=None):
        self.image = image
        self.point = (x,y)
        self.dimensions = (width, height)

    def jpg_imagedata(self):
        #directly process JPEG files
        #open file, needs some error handling!!
        imageFile = open(self.image, 'rb')
        info = pdfutils.readJPEGInfo(imageFile)
        imgwidth, imgheight = info[0], info[1]
        if info[2] == 1:
            colorSpace = 'DeviceGray'
        elif info[2] == 3:
            colorSpace = 'DeviceRGB'
        else: #maybe should generate an error, is this right for CMYK?
            colorSpace = 'DeviceCMYK'
        imageFile.seek(0) #reset file pointer
        imagedata = []
        #imagedata.append('BI /Width %d /Height /BitsPerComponent 8 /ColorSpace /%s /Filter [/Filter [ /ASCII85Decode /DCTDecode] ID' % (info[0], info[1], colorSpace))
        imagedata.append('BI /W %d /H %d /BPC 8 /CS /%s /F [/A85 /DCT] ID' % (imgwidth, imgheight, colorSpace))
        #write in blocks of (??) 60 characters per line to a list
        compressed = imageFile.read()
        encoded = pdfutils._AsciiBase85Encode(compressed)
        outstream = cStringIO.StringIO(encoded)
        dataline = outstream.read(60)
        while dataline <> "":
            imagedata.append(dataline)
            dataline = outstream.read(60)
        imagedata.append('EI')
        return (imagedata, imgwidth, imgheight)
    
    def cache_imagedata(self):
        image = self.image
        if not pdfutils.cachedImageExists(image):
            if not zlib:
                warnOnce('zlib not available')
                return
            try:
                import Image
            except ImportError:
                warnOnce('Python Imaging Library not available')
                return
            pdfutils.cacheImageFile(image)

        #now we have one cached, slurp it in
        cachedname = os.path.splitext(image)[0] + '.a85'
        imagedata = open(cachedname,'rb').readlines()
        #trim off newlines...
        imagedata = map(string.strip, imagedata)
        return imagedata

    def PIL_imagedata(self):
        if not zlib:
            warnOnce('zlib not available')
            return
        image = self.image
        myimage = image.convert('RGB')
        imgwidth, imgheight = myimage.size

        # this describes what is in the image itself
        # *NB* according to the spec you can only use the short form in inline images
        #imagedata=['BI /Width %d /Height /BitsPerComponent 8 /ColorSpace /%s /Filter [/Filter [ /ASCII85Decode /FlateDecode] ID]' % (imgwidth, imgheight,'RGB')]
        imagedata=['BI /W %d /H %d /BPC 8 /CS /RGB /F [/A85 /Fl] ID' % (imgwidth, imgheight)]

        #use a flate filter and Ascii Base 85 to compress
        raw = myimage.tostring()
        assert(len(raw) == imgwidth * imgheight, "Wrong amount of data for image")
        compressed = zlib.compress(raw)   #this bit is very fast...
        encoded = pdfutils._AsciiBase85Encode(compressed) #...sadly this isn't

        #write in blocks of (??) 60 characters per line to a list
        outstream = cStringIO.StringIO(encoded)
        dataline = outstream.read(60)
        while dataline <> "":
            imagedata.append(dataline)
            dataline = outstream.read(60)
        imagedata.append('EI')
        return (imagedata, imgwidth, imgheight) 

    def drawInlineImage(self, canvas): #, image, x,y, width=None,height=None):
        """Draw an Image into the specified rectangle.  If width and
        height are omitted, they are calculated from the image size.
        Also allow file names as well as images.  This allows a
        caching mechanism"""

        image = self.image 
        (x,y) = self.point
        (width, height) = self.dimensions
        
        if type(image) == StringType:
            if os.path.splitext(image)[1] in ['.jpg', '.JPG', '.jpeg', '.JPEG']:
                (imagedata, imgwidth, imgheight) = self.jpg_imagedata()
            else:
                if hasattr(self,'noImageCaching') and canvas.noImageCaching:
                    imagedata = pdfutils.cacheImageFile(image,returnInMemory=1)
                else:
                    imagedata = self.cache_imagedata()
                #parse line two for width, height
                words = string.split(imagedata[1])
                imgwidth = string.atoi(words[1])
                imgheight = string.atoi(words[3])
        else:
            (imagedata, imgwidth, imgheight) = self.PIL_imagedata()
        #now build the PDF for the image.
        if not width:
            width = imgwidth
        if not height:
            height = imgheight
        
        # this says where and how big to draw it
        if not canvas.bottomup: y = y+height
        canvas._code.append('q %s 0 0 %s cm' % (fp_str(width), fp_str(height, x, y)))

        # self._code.extend(imagedata) if >=python-1.5.2
        for line in imagedata:
            canvas._code.append(line)

        canvas._code.append('Q')
