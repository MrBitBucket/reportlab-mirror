#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/attrmap.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/attrmap.py,v 1.6 2002/07/24 19:56:37 andy_robinson Exp $
__version__=''' $Id: attrmap.py,v 1.6 2002/07/24 19:56:37 andy_robinson Exp $ '''
from UserDict import UserDict
from reportlab.lib.validators import isAnything, _SequenceTypes

class CallableValue:
    '''a class to allow callable initial values'''
    def __init__(self,func,*args,**kw):
        #assert iscallable(func)
        self.func = func
        self.args = args
        self.kw = kw

    def __call__(self):
        return apply(self.func,self.args,self.kw)

class AttrMapValue:
    '''Simple multi-value holder for attribute maps'''
    def __init__(self,validate=None,desc=None,initial=None, **kw):
        self.validate = validate or isAnything
        self.desc = desc
        self.initial = initial
        for k,v in kw.items():
            setattr(self,k,v)

    def __getattr__(self,name):
        #hack to allow callable initial values
        if name=='initial':
            if isinstance(self._initial,CallableValue): return self._initial()
            return self._initial
        elif name=='hidden':
            return 0
        raise AttributeError, name

class AttrMap(UserDict):
    def __init__(self,BASE=None,UNWANTED=[],**kw):
        if BASE:
            if isinstance(BASE,AttrMap):
                data = BASE.data                        #they used BASECLASS._attrMap
            elif hasattr(BASE,'_attrMap'):
                data = getattr(BASE._attrMap,'data',{}) #they gave us the BASECLASS
            else:
                raise ValueError, 'BASE=%s has wrong kind of value' % str(BASE)
        else:
            data = {}

        UserDict.__init__(self,data)
        self.remove(UNWANTED)
        self.data.update(kw)

    def update(self,kw):
        if isinstance(kw,AttrMap): kw = kw.data
        self.data.update(kw)

    def remove(self,unwanted):
        for k in unwanted:
            try:
                del self[k]
            except KeyError:
                pass

    def clone(self,UNWANTED=[],**kw):
        c = AttrMap(BASE=self,UNWANTED=UNWANTED)
        c.update(kw)
        return c

def validateSetattr(obj,name,value):
    '''validate setattr(obj,name,value)'''
    map = obj._attrMap
    if map and name[0]!= '_':
        try:
            validate = map[name].validate
            if not validate(value):
                raise AttributeError, "Illegal assignment of '%s' to '%s' in class %s" % (value, name, obj.__class__.__name__)
        except KeyError:
            raise AttributeError, "Illegal attribute '%s' in class %s" % (name, obj.__class__.__name__)
    obj.__dict__[name] = value

def _privateAttrMap(obj,ret=0):
    '''clone obj._attrMap if required'''
    A = obj._attrMap
    oA = getattr(obj.__class__,'_attrMap',None)
    if ret:
        if oA is A:
            return A.clone(), oA
        else:
            return A, None
    else:
        if oA is A:
            obj._attrMap = A.clone()

def _findObjectAndAttr(src, P):
    '''Locate the object src.P for P a string, return parent and name of attribute
    '''
    P = string.split(P, '.')
    if len(P) == 0:
        return None, None
    else:
        for p in P[0:-1]:
            src = getattr(src, p)
        return src, P[-1]

def addProxyAttribute(src,name=None,dst=None):
    '''
    Add a proxy attribute 'name' to src with targets dst
    '''
    #sanity
    assert hasattr(src,'_attrMap'), 'src object has no _attrMap'
    A, oA = _privateAttrMap(src,1)
    assert name and name in A.keys(), 'invalid proxy attribute name %s' % repr(name)
    if type(dst) not in _SequenceTypes: dst = dst,
    D = []
    DV = []
    for d in dst:
        if type(d) in _SequenceTypes:
            d, e = d[0], d[1:]
        obj, attr = _findObjectAndAttr(src,d)
        if obj:
            dA = getattr(obj,'_attrMap',None)
            assert dA and attr in dA.keys(), 'target attribute %s not in _attrMap' % d