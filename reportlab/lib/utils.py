#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/utils.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/utils.py,v 1.67 2004/03/23 15:20:50 rgbecker Exp $
__version__=''' $Id: utils.py,v 1.67 2004/03/23 15:20:50 rgbecker Exp $ '''

import string, os, sys
from types import *
from reportlab.lib.logger import warnOnce
SeqTypes = (ListType,TupleType)

def _findFiles(dirList,ext='.ttf'):
    from os.path import isfile, isdir, join as path_join
    from os import listdir
    ext = ext.lower()
    R = []
    A = R.append
    for D in dirList:
        if not isdir(D): continue
        for fn in listdir(D):
            fn = path_join(D,fn)
            if isfile(fn) and (not ext or fn.lower().endswith(ext)): A(fn)
    return R

try:
    _UserDict = dict
except:
    from UserDict import UserDict as _UserDict

class CIDict(_UserDict):
    def __init__(self,*a,**kw):
        map(self.update, a)
        self.update(kw)

    def update(self,D):
        for k,v in D.items(): self[k] = v

    def __setitem__(self,k,v):
        try:
            k = k.lower()
        except:
            pass
        _UserDict.__setitem__(self,k,v)

    def __getitem__(self,k):
        try:
            k = k.lower()
        except:
            pass
        return _UserDict.__getitem__(self,k)

    def __delitem__(self,k):
        try:
            k = k.lower()
        except:
            pass
        return _UserDict.__delitem__(self,k)

    def get(self,k,dv=None):
        try:
            return self[k]
        except KeyError:
            return dv

    def has_key(self,k):
        try:
            self[k]
            return True
        except:
            return False

    def pop(self,k,*a):
        try:
            k = k.lower()
        except:
            pass
        return _UserDict.pop(*((self,k)+a))

    def setdefault(self,k,*a):
        try:
            k = k.lower()
        except:
            pass
        return _UserDict.setdefault(*((self,k)+a))

if os.name == 'mac':
    #with the Mac, we need to tag the file in a special
    #way so the system knows it is a PDF file.
    #This supplied by Joe Strout
    import macfs, macostools
    _KNOWN_MAC_EXT = {
        'BMP' : ('ogle','BMP '),
        'EPS' : ('ogle','EPSF'),
        'EPSF': ('ogle','EPSF'),
        'GIF' : ('ogle','GIFf'),
        'JPG' : ('ogle','JPEG'),
        'JPEG': ('ogle','JPEG'),
        'PCT' : ('ttxt','PICT'),
        'PICT': ('ttxt','PICT'),
        'PNG' : ('ogle','PNGf'),
        'PPM' : ('ogle','.PPM'),
        'TIF' : ('ogle','TIFF'),
        'TIFF': ('ogle','TIFF'),
        'PDF' : ('CARO','PDF '),
        'HTML': ('MSIE','TEXT'),
        }
    def markfilename(filename,creatorcode=None,filetype=None,ext='PDF'):
        try:
            if creatorcode is None or filetype is None and ext is not None:
                try:
                    creatorcode, filetype = _KNOWN_MAC_EXT[string.upper(ext)]
                except:
                    return
            macfs.FSSpec(filename).SetCreatorType(creatorcode,filetype)
            macostools.touched(filename)
        except:
            pass
else:
    def markfilename(filename,creatorcode=None,filetype=None):
        pass

import reportlab
__RL_DIR=os.path.dirname(reportlab.__file__)    #possibly relative
_RL_DIR=os.path.isabs(__RL_DIR) and __RL_DIR or os.path.abspath(__RL_DIR)
del reportlab

#Attempt to detect if this copy of reportlab is running in a
#file system (as opposed to mostly running in a zip or McMillan
#archive or Jar file).  This is used by test cases, so that
#we can write test cases that don't get activated in a compiled
try:
    __file__
except:
    __file__ = sys.argv[0]
try:
    _isFSD = not __loader__
    _loaderpfxlenR = len(__loader__.archive+os.sep)
    _loaderpfxlen = _loaderpfxlenR+len(_RL_DIR)-len(__RL_DIR)
except:
    _isFSD = os.path.isfile(__file__)   #slight risk of wrong path
    __loader__ = None
_isFSSD = _isFSD and os.path.isfile(os.path.splitext(__file__)[0] +'.py')

def _startswith_rl(fn):
    '''if the name starts with a known prefix strip it off'''
    fn = fn.replace('/',os.sep)
    if fn.startswith(_RL_DIR): return fn[_loaderpfxlen:]
    if fn.startswith(__RL_DIR): return fn[_loaderpfxlenR:]
    return fn

def isFileSystemDistro():
    '''return truth if a file system distribution'''
    return _isFSD

def isCompactDistro():
    '''return truth if not a file system distribution'''
    return not _isFSD

def isSourceDistro():
    '''return truth if a source file system distribution'''
    return _isFSSD

try:
    #raise ImportError
    ### NOTE!  FP_STR SHOULD PROBABLY ALWAYS DO A PYTHON STR() CONVERSION ON ARGS
    ### IN CASE THEY ARE "LAZY OBJECTS".  ACCELLERATOR DOESN'T DO THIS (YET)
    try:
        from _rl_accel import fp_str                # in case of builtin version
    except ImportError:
        from reportlab.lib._rl_accel import fp_str  # specific
except ImportError:
    from math import log
    _log_10 = lambda x,log=log,_log_e_10=log(10.0): log(x)/_log_e_10
    _fp_fmts = "%.0f", "%.1f", "%.2f", "%.3f", "%.4f", "%.5f", "%.6f"
    import re
    _tz_re = re.compile('0+$')
    del re
    def fp_str(*a):
        if len(a)==1 and type(a[0]) in SeqTypes: a = a[0]
        s = []
        A = s.append
        for i in a:
            sa =abs(i)
            if sa<=1e-7: A('0')
            else:
                l = sa<=1 and 6 or min(max(0,(6-int(_log_10(sa)))),6)
                n = _fp_fmts[l]%i
                if l:
                    n = _tz_re.sub('',n)
                    try:
                        if n[-1]=='.': n = n[:-1]
                    except:
                        print i, n
                        raise
                A((n[0]!='0' or len(n)==1) and n or n[1:])
        return string.join(s)

#hack test for comma users
if ',' in fp_str(0.25):
    _FP_STR = fp_str
    def fp_str(*a):
        return string.replace(apply(_FP_STR,a),',','.')

def recursiveImport(modulename, baseDir=None, noCWD=0, debug=0):
    """Dynamically imports possible packagized module, or raises ImportError"""
    normalize = lambda x: os.path.normcase(os.path.abspath(os.path.normpath(x)))
    path = map(normalize,sys.path)
    if baseDir:
        if type(baseDir) not in SeqTypes:
            tp = [baseDir]
        else:
            tp = filter(None,list(baseDir))
        for p in tp:
            p = normalize(p)
            if p not in path: path.insert(0,p)

    if noCWD:
        for p in ('','.',normalize('.')):
            while p in path:
                if debug: print 'removed "%s" from path' % p
                path.remove(p)
    elif '.' not in path:
            path.insert(0,'.')

    if debug:
        import pprint
        pp = pprint.pprint
        print 'path=',
        pp(path)

    #make import errors a bit more informative
    opath = sys.path
    try:
        sys.path = path
        exec 'import %s\nm = %s\n' % (modulename,modulename) in locals()
        sys.path = opath
        return m
    except ImportError:
        sys.path = opath
        msg = "recursiveimport(%s,baseDir=%s) failed" % (modulename,baseDir)
        if baseDir:
            msg = msg + " under paths '%s'" % `path`
        raise ImportError, msg

def recursiveGetAttr(obj, name):
    "Can call down into e.g. object1.object2[4].attr"
    return eval(name, obj.__dict__)

def recursiveSetAttr(obj, name, value):
    "Can call down into e.g. object1.object2[4].attr = value"
    #get the thing above last.
    tokens = string.split(name, '.')
    #print 'name=%s, tokens=%s' % (name, tokens)
    if len(tokens) == 1:
        setattr(obj, name, value)
    else:
        most = string.join(tokens[:-1], '.')
        last = tokens[-1]
        #print 'most=%s, last=%s' % (most, last)
        parent = recursiveGetAttr(obj, most)
        #print 'parent=%s' % parent
        setattr(parent, last, value)

def import_zlib():
    try:
        import zlib
    except ImportError:
        zlib = None
        from reportlab.rl_config import ZLIB_WARNINGS
        if ZLIB_WARNINGS: warnOnce('zlib not available')
    return zlib


# Image Capability Detection.  Set a flag haveImages
# to tell us if either PIL or Java imaging libraries present.
# define PIL_Image as either None, or an alias for the PIL.Image
# module, as there are 2 ways to import it

if sys.platform[0:4] == 'java':
    try:
        import javax.imageio
        import java.awt.image
        haveImages = 1
    except:
        haveImages = 0
else:
    try:
        from PIL import Image
    except ImportError:
        try:
            import Image
        except ImportError:
            Image = None
    haveImages = Image is not None
    if haveImages: del Image


__StringIO=None
def getStringIO(buf=None):
    '''unified StringIO instance interface'''
    global __StringIO
    if not __StringIO:
        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO
        __StringIO = StringIO
    return buf is not None and __StringIO(buf) or __StringIO()

class ArgvDictValue:
    '''A type to allow clients of getArgvDict to specify a conversion function'''
    def __init__(self,value,func):
        self.value = value
        self.func = func

def getArgvDict(**kw):
    ''' Builds a dictionary from its keyword arguments with overrides from sys.argv.
        Attempts to be smart about conversions, but the value can be an instance
        of ArgDictValue to allow specifying a conversion function.
    '''
    def handleValue(v,av,func):
        if func:
            v = func(av)
        else:
            t = type(v)
            if t is StringType:
                v = av
            elif t is FloatType:
                v = float(av)
            elif t is IntType:
                v = int(av)
            elif t is ListType:
                v = list(eval(av))
            elif t is TupleType:
                v = tuple(eval(av))
            else:
                raise TypeError, "Can't convert string '%s' to %s" % (av,str(t))
        return v

    A = sys.argv[1:]
    R = {}
    for k, v in kw.items():
        if isinstance(v,ArgvDictValue):
            v, func = v.value, v.func
        else:
            func = None
        handled = 0
        ke = k+'='
        for a in A:
            if string.find(a,ke)==0:
                av = a[len(ke):]
                A.remove(a)
                R[k] = handleValue(v,av,func)
                handled = 1
                break

        if not handled: R[k] = handleValue(v,v,func)

    return R

def getHyphenater(hDict=None):
    try:
        from reportlab.lib.pyHnj import Hyphen
        if hDict is None: hDict=os.path.join(os.path.dirname(__file__),'hyphen.mashed')
        return Hyphen(hDict)
    except ImportError, errMsg:
        if str(errMsg)!='No module named pyHnj': raise
        return None

def _className(self):
    '''Return a shortened class name'''
    try:
        name = self.__class__.__name__
        i=string.rfind(name,'.')
        if i>=0: return name[i+1:]
        return name
    except AttributeError:
        return str(self)

def open_for_read(name,mode='b'):
    '''attempt to open a file or URL for reading'''
    if hasattr(name,'read'): return name
    import urllib
    try:
        t, o = urllib.splittype(name)
        if not t or t=='file': raise ValueError
        o = urllib.urlopen(name)
        return getStringIO(o.read())
    except:
        if 'r' not in mode: mode = 'r'+mode
        try:
            return open(name,mode)
        except IOError:
            t, v = sys.exc_info()[:2]
            if _isFSD or __loader__ is None: raise
            try:
                #we have a __loader__, perhaps the filename starts with
                #the dirname(reportlab.__file__) or is relative
                name = _startswith_rl(name)
                s = __loader__.get_data(name)
                if 'b' not in mode and os.linesep!='\n': s = s.replace(os.linesep,'\n')
                return getStringIO(s)
            except:
                raise t, v

def open_and_read(name,mode='b'):
    return open_for_read(name,mode).read()

def open_and_readlines(name,mode='t'):
    return open_and_read(name,mode).split('\n')

def rl_isfile(fn,os_path_isfile=os.path.isfile):
    if hasattr(fn,'read'): return True
    if os_path_isfile(fn): return True
    if _isFSD or __loader__ is None: return False
    fn = _startswith_rl(fn)
    return fn in __loader__._files.keys()

def rl_isdir(pn,os_path_isdir=os.path.isdir):
    if os_path_isdir(pn): return True
    if _isFSD or __loader__ is None: return False
    pn = _startswith_rl(pn)
    return len(filter(lambda x: x.startswith(pn),__loader__._files.keys()))>0

class ImageReader:
    "Wraps up either PIL or Java to get data from bitmaps"
    def __init__(self, fileName):
        if not haveImages:
            warnOnce('Imaging Library not available, unable to import bitmaps')
            return
        #start wih lots of null private fields, to be populated by
        #the relevant engine.
        self.fileName = fileName
        self._image = None
        self._width = None
        self._height = None
        self._transparent = None
        self._data = None
        self.fp = open_for_read(fileName,'b')

        #detect which library we are using and open the image
        if sys.platform[0:4] == 'java':
            from javax.imageio import ImageIO
            self._image = ImageIO.read(self.fp)
        else:
            import PIL.Image
            self._image = PIL.Image.open(self.fp)

    def getSize(self):
        if (self._width is None or self._height is None):
            if sys.platform[0:4] == 'java':
                self._width = self._image.getWidth()
                self._height = self._image.getHeight()
            else:
                self._width, self._height = self._image.size
        return (self._width, self._height)

    def getRGBData(self):
        "Return byte array of RGB data as string"
        if self._data is None:
            if sys.platform[0:4] == 'java':
                import jarray
                from java.awt.image import PixelGrabber
                width, height = self.getSize()
                buffer = jarray.zeros(width*height, 'i')
                pg = PixelGrabber(self._image, 0,0,width,height,buffer,0,width)
                pg.grabPixels()
                # there must be a way to do this with a cast not a byte-level loop,
                # I just haven't found it yet...
                pixels = []
                a = pixels.append
                for i in range(len(buffer)):
                    rgb = buffer[i]
                    a(chr((rgb>>16)&0xff))
                    a(chr((rgb>>8)&0xff))
                    a(chr(rgb&0xff))
                self._data = ''.join(pixels)
            else:
                rgb = self._image.convert('RGB')
                self._data = rgb.tostring()
        return self._data

    def getImageData(self):
        width, height = self.getSize()
        return width, height, self.getRGBData()

    def getTransparent(self):
        if sys.platform[0:4] == 'java':
            return None
        else:
            if self._image.info.has_key("transparency"):
                transparency = self._image.info["transparency"] * 3
                palette = self._image.palette
                try:
                    palette = palette.palette
                except:
                    palette = palette.data
                return map(ord, palette[transparency:transparency+3])
            else:
                return None

def getImageData(imageFileName):
    "Get width, height and RGB pixels from image file.  Wraps Java/PIL"
    return ImageReader.getImageData(imageFileName)

class DebugMemo:
    '''Intended as a simple report back encapsulator

    Typical usages
    1) To record error data
        dbg = DebugMemo(fn='dbgmemo.dbg',myVar=value)
        dbg.add(anotherPayload='aaaa',andagain='bbb')
        dbg.dump()

    2) To show the recorded info
        dbg = DebugMemo(fn='dbgmemo.dbg',mode='r')
        dbg.load()
        dbg.show()

    3) To re-use recorded information
        dbg = DebugMemo(fn='dbgmemo.dbg',mode='r')
            dbg.load()
        myTestFunc(dbg.payload('myVar'),dbg.payload('andagain'))

    in addition to the payload variables the dump records many useful bits
    of information which are also printed in the show() method.
    '''
    def __init__(self,fn='rl_dbgmemo.dbg',mode='w',getScript=1,modules=(),**kw):
        import time, socket
        self.fn = fn
        if mode!='w': return
        self.store = store = {}
        if sys.exc_info() != (None,None,None):
            import traceback
            s = getStringIO()
            traceback.print_exc(None,s)
            store['__traceback'] = s.getvalue()
        cwd=os.getcwd()
        lcwd = os.listdir(cwd)
        exed = os.path.abspath(os.path.dirname(sys.argv[0]))
        store.update({  'gmt': time.asctime(time.gmtime(time.time())),
                        'platform': sys.platform,
                        'version': sys.version,
                        'executable': sys.executable,
                        'prefix': sys.prefix,
                        'path': sys.path,
                        'argv': sys.argv,
                        'cwd': cwd,
                        'hostname': socket.gethostname(),
                        'lcwd': lcwd,
                        })
        if exed!=cwd: store.update({'exed': exed,
                                    'lexed': os.listdir(exed),
                                    })
        if hasattr(os,'uname'):
            store.update({
                'uname': os.uname(),
                'ctermid': os.ctermid(),
                'getgid': os.getgid(),
                'getuid': os.getuid(),
                'getegid': os.getegid(),
                'geteuid': os.geteuid(),
                'getlogin': os.getlogin(),
                'getgroups': os.getgroups(),
                'getpgrp': os.getpgrp(),
                'getpid': os.getpid(),
                'getppid': os.getppid(),
                })
        if getScript:
            fn = os.path.abspath(sys.argv[0])
            if os.path.isfile(fn):
                store['__script'] = open(fn,'r').read()
        module_versions = {}
        for n,m in sys.modules.items():
            if n=='reportlab' or n=='rlextra' or n[:10]=='reportlab.' or n[:8]=='rlextra.':
                v = getattr(m,'__version__',None)
                if v: module_versions[n] = v
        store['__module_versions'] = module_versions
        self.store['__payload'] = {}
        self._add(kw)

    def _add(self,D):
        payload = self.store['__payload']
        for k, v in D.items():
            payload[k] = v

    def add(self,**kw):
        self._add(kw)

    def dump(self):
        import pickle
        pickle.dump(self.store,open(self.fn,'wb'))

    def load(self):
        import pickle
        self.store = pickle.load(open(self.fn,'rb'))

    def _show_module_versions(self,k,v):
        print k[2:]
        K = v.keys()
        K.sort()
        for k in K:
            vk = v[k]
            try:
                m = recursiveImport(k,sys.path[:],1)
                d = getattr(m,'__version__',None)==vk and 'SAME' or 'DIFFERENT'
            except:
                m = None
                d = '??????unknown??????'
            print '  %s = %s (%s)' % (k,vk,d)

    def _banner(self,k,what):
        print '###################%s %s##################' % (what,k[2:])

    def _start(self,k):
        self._banner(k,'Start  ')

    def _finish(self,k):
        self._banner(k,'Finish ')

    def _show_lines(self,k,v):
        self._start(k)
        print v
        self._finish(k)

    def _show_payload(self,k,v):
        if v:
            import pprint
            self._start(k)
            pprint.pprint(v)
            self._finish(k)

    specials = {'__module_versions': _show_module_versions,
                '__payload': _show_payload,
                '__traceback': _show_lines,
                '__script': _show_lines,
                }
    def show(self):
        K = self.store.keys()
        K.sort()
        for k in K:
            if k not in self.specials.keys(): print '%-15s = %s' % (k,self.store[k])
        for k in K:
            if k in self.specials.keys(): apply(self.specials[k],(self,k,self.store[k]))

    def payload(self,name):
        return self.store['__payload'][name]

    def __setitem__(self,name,value):
        self.store['__payload'][name] = value

    def __getitem__(self,name):
        return self.store['__payload'][name]
