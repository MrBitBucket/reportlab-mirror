#Copyright ReportLab Europe Ltd. 2000-2007
#see license.txt for license details
__version__=''' $Id$ '''


#modification of users/robin/ttflist.py.
"""This provides some general-purpose tools for finding fonts.

The FontFinder object can search for font files.  It aims to build
a catalogue of fonts which our framework can work with.  It may be useful
if you are building GUIs or design-time interfaces and want to present users
with a choice of fonts.

By default it will look in the directories specified in reportlab/rl_config.py
You can pass in your own directories as extras or replacements.

Because the disk search takes some time to find and parse hundreds of fonts,
it tries to cache a temporary file listing all (healthy) fonts found.

For each font found, it aims to record
- the short font name
- the long font name
- the principal file (.pfb for type 1 fonts)
- the time modified (unix time stamp)
- a type code ('ttf')
- the family name
- the style

Unfortunately the ReportLab API has a fairly messy font class hierarchy; the
Type 1 files separate the 'face' and the 'encoding', and TT Fonts don't inherit
from the same base.  


"""


class FontFinder:
    """Keeps a database of fonts"""
    def __init__(self):


        self._extraFontDirs = []
        self.readInfo()

    def readInfo(self):
        L = {}
        B = {}
        try:
            execfile(self.getFontsListFN(),locals())
        except:
            pass
        self._fontInfo = L
        self._badFiles = B
        self._checkBadFiles()

    def _checkBadFiles(self):
        from os.path import isfile
        BF = self._badFiles
        for fn in BF.keys():
            if not isfile(fn):
                del BF[fn]

    def _knownFiles(self):
        L = self._fontInfo
        KF = {}
        for k,v in L.items():
            fn = v[0]
            tm = v[1]
            if KF.has_key(fn):
                otm,N = KF[fn]
                assert otm==tm, "Times differ for same file"
                N += [k]
                KF[fn] = tm,N
            else:
                KF[fn] = tm,[k]
        return KF

    def getFontsListFN(self):
        from reportlab.lib.utils import get_rl_tempfile
        return get_rl_tempfile('ReportLabFontsList.txt')

    def build(self):
        from reportlab.pdfbase.ttfonts import TTFontFile, TTFError
        from reportlab import rl_config
        from os import stat
        from os.path import isfile
        from stat import ST_MTIME
        names = ('name','fullName','uniqueFontID')
        L = self._fontInfo
        KF = self._knownFiles()
        BF = self._badFiles
        self._checkBadFiles()
        from reportlab.lib.utils import _findFiles
        dirsForTrueType = rl_config.TTFSearchPath + self._extraFontDirs
        for fn in _findFiles(rl_config.TTFSearchPath,'.ttf'):
            try:
                tm = stat(fn)[ST_MTIME]
                if KF.has_key(fn):
                    kf = KF[fn]
                    del KF[fn]
                    if kf[0]==tm: continue
                    for n in kf[1]:
                        del L[n]

                if BF.has_key(fn):
                    if BF[fn]==tm: continue
                    del BF[fn]

                ttff = TTFontFile(fn,validate=1,charInfo=0)
                t = fn, tm, 'ttf', ttff.familyName, ttff.styleName
                print 'File: %s, TTF OK, fullName: "%s" psName: %s' % (fn, ttff.fullName, ttff.name)
                for n in names:
                    n = getattr(ttff,n)
                    if not L.has_key(n): L[n] = t
                del ttff
            except TTFError, x:
                print 'File:',fn,'  !!!!!!!!!!!',x,'!!!!!!!!!!!'
                BF[fn] = tm
        for fn, kf in KF.items():
            if not isfile(fn):
                for n in kf[1]:
                    del L[n]
        #AR - adding equivalent information for Type 1 files
        dirsForTypeOne = rl_config.T1SearchPath + self._extraFontDirs                    
        typeOneFaces = self._findTypeOneFonts(dirsForTypeOne)
        for face in typeOneFaces:
            #('c:\\windows\\fonts\\VERDANA.TTF', 1030593600, 'ttf', 'Verdana', 'Regular')
            info = (
                face.pfbFileName,
                stat(fn)[ST_MTIME],
                'pfb',
                face.familyName,
                '(unknown)',
                
                )
            self._fontInfo[face.name] = info
            #print '%s: %s' % (face.name, str(info))
        f = open(self.getFontsListFN(),'w')
        def _(a,b,L=L):
            x = L[a]
            y = L[b]
            return cmp((x[3],x[4],x[2],a,x[0],x[1]),(y[3],y[4],y[2],b,y[0],y[1]))
        K = L.keys()
        K.sort(_)
        for k in K:
            print >> f, "L[%s]=%s" % (repr(k),repr(L[k]))
        K = BF.keys()
        K.sort()
        for k in K:
            print >> f, "B[%s]=%s" % (repr(k),repr(BF[k]))
        f.close()

    def _findTypeOneFonts(self, searchPath):
        """Return list of structures for Type 1 fonts.
        """
        from reportlab.pdfbase.pdfmetrics import EmbeddedType1Face
        from reportlab import rl_config
        from os import stat
        from os.path import isfile, splitext
        from stat import ST_MTIME
        from reportlab.lib.utils import _findFiles

        
        found = []
        for pfbFileName in _findFiles(searchPath,'.pfb'):
            pfbFileRoot = splitext(pfbFileName)[0]
            #look for metrics file in either case
            afmFileLower = pfbFileRoot + '.afm'
            afmFileUpper = pfbFileRoot + '.AFM'
            if isfile(afmFileLower):
                afmFileName = afmFileLower
            elif isfile(afmFileUpper):
                afmFileName = afmFileUpper
            else:
                #print "no .afm file for %s, cannot use" % pfbFileName
                continue
            #we don't actually need the font object right now, just the typeface object.
            
            face = EmbeddedType1Face(afmFileName, pfbFileName)
            found.append(face)
        return found

    def getFamilies(self):
        """Returns a list of all font family names found.

        This just returns the family name.  
        """
        if not hasattr(self,'_families'):
            F = {}
            for fn, tm, fontType, familyName, styleName in self._fontInfo.values():
                S={styleName: fn}
                try:
                    F[familyName].update(S)
                except:
                    F[familyName] = S
            self._families = F
        return self._families.keys()

    def getFamily(self, familyName):
        """Returns 
        """

    def getStyles(self):
        """Returns a list of distinct styles found"""
        if not hasattr(self,'_styles'):
            S = {}
            self.getFamilies()
            for s in self._families.values():
                for k in s.keys():
                    S[k] = 1
            self._styles = S.keys()
        return self._styles

    

if __name__=='__main__':
    ttfl = FontFinder()
    ttfl.build()
    import sys
    if '--families' in sys.argv:
        print 'Families'
        F = ttfl.getFamilies()
        if F:
            F.sort()
            #fn, tm, fontType, familyName, styleName
            for f in F:
                print f
                V = filter(lambda i: i[1][3]==f,ttfl._fontInfo.items())
                V.sort()
                for k,v in V:
                    print '        ',', '.join((k,v[4],v[0]))
    if '--styles' in sys.argv:
        print 'Styles'
        F = ttfl.getStyles()
        if F:
            F.sort()
            #fn, tm, fontType, familyName, styleName
            for f in F:
                print f
                V = filter(lambda i: i[1][4]==f,ttfl._fontInfo.items())
                V.sort()
                for k,v in V:
                    print '        ',', '.join((k,v[3],v[0]))
