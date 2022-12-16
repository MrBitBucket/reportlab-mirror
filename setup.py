#Copyright ReportLab Europe Ltd. 2000-2022
#see LICENSE for license details
__version__='3.6.12'
import os, sys, glob, shutil, re, sysconfig, traceback, io, subprocess
from urllib.parse import quote as urlquote
platform = sys.platform
pjoin = os.path.join
abspath = os.path.abspath
isfile = os.path.isfile
isdir = os.path.isdir
dirname = os.path.dirname
basename = os.path.basename
splitext = os.path.splitext
addrSize = 64 if sys.maxsize > 2**32 else 32
sysconfig_platform = sysconfig.get_platform()

INFOLINES=[]
def infoline(t,
        pfx='#####',
        add=True,
        ):
    bn = splitext(basename(sys.argv[0]))[0]
    ver = '.'.join(map(str,sys.version_info[:3]))
    s = '%s %s-python-%s-%s: %s' % (pfx, bn, ver, sysconfig_platform, t)
    print(s)
    if add: INFOLINES.append(s)

def showTraceback(s):
    buf = io.StringIO()
    print(s,file=buf)
    if verbose>2:
        traceback.print_exc(file=buf)
    for l in buf.getvalue().split('\n'):
        infoline(l,pfx='!!!!!',add=False)

def spCall(cmd,*args,**kwds):
    r = subprocess.call(
            cmd,
            stderr = subprocess.STDOUT,
            stdout = subprocess.DEVNULL if kwds.pop('dropOutput',False) else None,
            timeout = kwds.pop('timeout',3600),
            )
    if verbose>=3:
        infoline('%r --> %s' % (' '.join(cmd),r), pfx='!!!!!' if r else '#####', add=False)
    return r

def specialOption(n,ceq=False):
    v = 0
    while n in sys.argv:
        v += 1
        sys.argv.remove(n)
    if ceq:
        n += '='
        V = [_ for _ in sys.argv if _.startswith(n)]
        for _ in V: sys.argv.remove(_)
        if V:
            n = len(n)
            v = V[-1][n:]
    return v

dlt1 = not specialOption('--no-download-t1-files')
verbose = specialOption('--verbose',ceq=True)
nullDivert = not verbose

if __name__=='__main__':
    pkgDir=dirname(sys.argv[0])
else:
    pkgDir=dirname(__file__)
if not pkgDir:
    pkgDir=os.getcwd()
elif not os.path.isabs(pkgDir):
    pkgDir=abspath(pkgDir)
try:
    os.chdir(pkgDir)
except:
    showTraceback('warning could not change directory to %r' % pkgDir)

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

def _packages_path(d):
    P = [_ for _ in sys.path if basename(_)==d]
    if P: return P[0]

package_path = _packages_path('dist-packages') or _packages_path('site-packages')
package_path = pjoin(package_path, 'reportlab')

def get_version():
    #determine Version

    #first try source
    FN = pjoin(pkgDir,'src','reportlab','__init__')
    try:
        for l in open(pjoin(FN+'.py'),'r').readlines():
            if l.startswith('Version'):
                D = {}
                exec(l.strip(),D)
                return D['Version']
    except:
        pass

    #don't have source, try import
    import imp
    for desc in ('.pyc', 'rb', 2), ('.pyo', 'rb', 2):
        try:
            fn = FN+desc[0]
            f = open(fn,desc[1])
            m = imp.load_module('reportlab',f,fn,desc)
            return m.Version
        except:
            pass
    raise ValueError('Cannot determine ReportLab Version')

#this code from /FBot's PIL setup.py
def aDir(P, d, x=None):
    if d and isdir(d) and d not in P:
        if x is None:
            P.append(d)
        else:
            P.insert(x, d)

# protection against loops needed. reported by
# Michał Górny &lt; mgorny at gentoo dot org &gt;
# see https://stackoverflow.com/questions/36977259
def findFile(root, wanted, followlinks=True):
    visited = set()
    for p, D, F in os.walk(root,followlinks=followlinks):
        #scan directories to check for prior visits
        #use dev/inode to make unique key
        SD = [].append
        for d in D:
            dk = os.stat(pjoin(p,d))
            dk = dk.st_dev, dk.st_ino
            if dk not in visited:
                visited.add(dk)
                SD(d)
        D[:] = SD.__self__  #set the dirs to be scanned
        for fn in F:
            if fn==wanted:  
                return abspath(pjoin(p,fn))

def listFiles(root,followlinks=True,strJoin=None):
    visited = set()
    R = [].append
    for p, D, F in os.walk(root,followlinks=followlinks):
        #scan directories to check for prior visits
        #use dev/inode to make unique key
        SD = [].append
        for d in D:
            dk = os.stat(pjoin(p,d))
            dk = dk.st_dev, dk.st_ino
            if dk not in visited:
                visited.add(dk)
                SD(d)
        D[:] = SD.__self__  #set the dirs to be scanned
        for fn in F:
            R(abspath(pjoin(p,fn)))
    R = R.__self__
    return strJoin.join(R) if strJoin else R

reportlab_files= [
        'fonts/00readme.txt',
        'fonts/bitstream-vera-license.txt',
        'fonts/DarkGarden-changelog.txt',
        'fonts/DarkGarden-copying-gpl.txt',
        'fonts/DarkGarden-copying.txt',
        'fonts/DarkGarden-readme.txt',
        'fonts/DarkGarden.sfd',
        'fonts/DarkGardenMK.afm',
        'fonts/DarkGardenMK.pfb',
        'fonts/Vera.ttf',
        'fonts/VeraBd.ttf',
        'fonts/VeraBI.ttf',
        'fonts/VeraIt.ttf',
        'fonts/_abi____.pfb',
        'fonts/_ab_____.pfb',
        'fonts/_ai_____.pfb',
        'fonts/_a______.pfb',
        'fonts/cobo____.pfb',
        'fonts/cob_____.pfb',
        'fonts/com_____.pfb',
        'fonts/coo_____.pfb',
        'fonts/_ebi____.pfb',
        'fonts/_eb_____.pfb',
        'fonts/_ei_____.pfb',
        'fonts/_er_____.pfb',
        'fonts/sy______.pfb',
        'fonts/zd______.pfb',
        'fonts/zx______.pfb',
        'fonts/zy______.pfb',
        'fonts/callig15.pfb',
        'fonts/callig15.afm',
        'reportlab/graphics/barcode/README'
        'reportlab/graphics/barcode/TODO'
        'license.txt',
        ]

def url2data(url,returnRaw=False):
    import urllib.request as ureq
    remotehandle = ureq.urlopen(url)
    try:
        raw = remotehandle.read()
        return raw if returnRaw else io.BytesIO(raw)
    finally:
        remotehandle.close()

def get_fonts(PACKAGE_DIR, reportlab_files):
    import zipfile
    rl_dir = PACKAGE_DIR['reportlab']
    if not [x for x in reportlab_files if not isfile(pjoin(rl_dir,x))]:
        xitmsg = "Standard T1 font curves already downloaded"
    elif not dlt1:
        xitmsg = "not downloading T1 font curve files"
    else:
        try:
            infoline("Downloading standard T1 font curves")
            zipdata = url2data("http://www.reportlab.com/ftp/pfbfer-20180109.zip")
            archive = zipfile.ZipFile(zipdata)
            dst = pjoin(rl_dir, 'fonts')

            for name in archive.namelist():
                if not name.endswith('/'):
                    with open(pjoin(dst, name), 'wb') as outfile:
                        outfile.write(archive.read(name))
            xitmsg = "Finished download of standard T1 font curves"
        except:
            xitmsg = "Failed to download standard T1 font curves"
    infoline(xitmsg)

def get_glyphlist_module(PACKAGE_DIR):
    try:
        lfn = pjoin("pdfbase","_glyphlist.py")
        fn = pjoin(PACKAGE_DIR['reportlab'],lfn)
        if isfile(fn):
            xitmsg = "The _glyphlist module already exists"
        else:
            text = url2data("https://raw.githubusercontent.com/adobe-type-tools/agl-aglfn/master/glyphlist.txt",True)
            comments = ['#see https://github.com/adobe-type-tools/agl-aglfn\n'].append
            G2U = [].append
            G2Us = [].append
            if not isinstance(text,str):
                text = text.decode('latin1')
            for line in text.split('\n'):
                line = line.strip()
                if not line: continue
                if line.startswith('#'):
                    comments(line+'\n')
                else:
                    gu = line.split(';')
                    if len(gu)==2:
                        v = gu[1].split()
                        if len(v)==1:
                            G2U('\t%r: 0x%s,\n' % (gu[0],gu[1]))
                        else:
                            G2Us('\t%r: (%s),\n' % (gu[0],','.join('0x%s'%u for u in v)))
                    else:
                        infoline('bad glyphlist line %r' % line, '!!!!!')
            with open(fn,'w') as f:
                f.write(''.join(comments.__self__))
                f.write('_glyphname2unicode = {\n')
                f.write(''.join(G2U.__self__))
                f.write('\t}\n')
                f.write('_glyphname2unicodes = {\n')
                f.write(''.join(G2Us.__self__))
                f.write('\t}\n')
            xitmsg = "Finished creation of _glyphlist.py"
    except:
        xitmsg = "Failed to download glyphlist.txt"
    infoline(xitmsg)

def canImport(pkg):
    ns = [pkg.find(_) for _ in '<>=' if _ in pkg]
    if ns: pkg =pkg[:min(ns)]
    ns = {}
    try:
        exec('import %s as M' % pkg,{},ns)
    except:
        if verbose>=2:
            showTraceback("can't import %s" % pkg)
    return 'M' in ns

def pipInstall(pkg, ixu=None):
    if canImport(pkg): return True
    i = ['-i%s' % ixu] if ixu else []
    r = spCall([sys.executable, '-mpip', 'install']+i+[pkg],dropOutput=verbose<3)
    return canImport(pkg)

def pipUninstall(pkg):
    spCall((sys.executable,'-mpip','-q','uninstall','-y', pkg), dropOutput=verbose<3)

def pipInstallGroups(pkgs, ixu=None):
    '''install groups of packages; if any of a group fail we backout the group'''
    for g in pkgs:
        I = []  #thse are the installed in this group
        for pkg in g.split():
            if pipInstall(pkg,ixu):
                I.append(pkg)
            else:
                print('!!!!! pip uninstalled %s' % repr(I)) 
                for pkg in I:
                    pipUninstall(pkg)
                I = []
                break
        if I:
            print('===== pip installed %s' % repr(I)) 

def vopt(opt):
    opt = '--%s=' % opt
    v = [_ for _ in sys.argv if _.startswith(opt)]
    for _ in v: sys.argv.remove(_)
    n = len(opt)
    return list(filter(None,[_[n:] for _ in v]))

class QUPStr(str):
    def __new__(cls,s,u,p):
        self = str.__new__(cls,s)
        self.u = u
        self.p = p
        return self

def qup(url, pat=re.compile(r'(?P<scheme>https?://)(?P<up>[^@]*)(?P<rest>@.*)$')):
    '''urlquote the user name and password'''
    m = pat.match(url)
    if m:
        u, p = m.group('up').split(':',1)
        url = "%s%s:%s%s" % (m.group('scheme'),urlquote(u),urlquote(p),m.group('rest'))
    else:
        u = p = ''
    return QUPStr(url,u,p)

def performPipInstalls():
    pip_installs = vopt('pip-install')
    pipInstallGroups(pip_installs)
    rl_pip_installs = vopt('rl-pip-install')
    if rl_pip_installs:
        rl_ixu = vopt('rl-index-url')
        if len(rl_ixu)==1:
            pipInstallGroups(rl_pip_installs,qup(rl_ixu[0]))
        else:
            raise ValueError('rl-pip-install requires exactly 1 --rl-index-url not %d' % len(rl_ixu))

def showEnv():
    action = -1 if specialOption('--show-env-only') else 1 if specialOption('--show-env') else 0
    if not action: return
    print('+++++ setup.py environment')
    print('+++++ sys.version = %s' % sys.version.replace('\n',''))
    import platform
    for k in sorted((_ for _ in dir(platform) if not _.startswith('_'))):
        try:
            v = getattr(platform,k)
            if isinstance(v,(str,list,tuple,bool)):
                v = repr(v)
            if callable(v) and v.__module__=='platform':
                v = repr(v())
            else:
                continue
        except:
            v = '?????'
        print('+++++ platform.%s = %s' % (k,v))
    print('--------------------------')
    for k, v in sorted(os.environ.items()):
        print('+++++ environ[%s] = %r' % (k,v))
    print('--------------------------')
    if action<0:
        sys.exit(0)

def main():
    showEnv()
    performPipInstalls()
    #test to see if we've a special command
    if 'test' in sys.argv \
        or 'tests' in sys.argv \
        or 'tests-postinstall' in sys.argv \
        or 'tests-preinstall' in sys.argv:
        verboseTests = specialOption('--verbose-tests')
        if len(sys.argv)!=2:
            raise ValueError('tests commands may only be used alone sys.argv[1:]=%s' % repr(sys.argv[1:]))
        cmd = sys.argv[-1]
        PYTHONPATH = [pkgDir] if cmd!='test' else []
        if cmd=='tests-preinstall':
            PYTHONPATH.insert(0,pjoin(pkgDir,'src'))
        if PYTHONPATH: os.environ['PYTHONPATH']=os.pathsep.join(PYTHONPATH)
        os.chdir(pjoin(pkgDir,'tests'))
        cli = [sys.executable, 'runAll.py']
        if cmd=='tests-postinstall':
            cli.append('--post-install')
        if verboseTests:
            cli.append('--verbosity=2')
        r = spCall(cli)
        sys.exit(('!!!!! runAll.py --> %s should exit with error !!!!!' % r) if r else r)
    elif 'null-cmd' in sys.argv or 'null-command' in sys.argv:
        sys.exit(0)

    EXT_MODULES = []

    #copy some special case files into place so package_data will treat them properly
    PACKAGE_DIR = {'':'src','reportlab': pjoin('src','reportlab')}
    get_fonts(PACKAGE_DIR, reportlab_files)
    get_glyphlist_module(PACKAGE_DIR)
    setup(
        name="reportlab",
        version=get_version(),
        license="BSD license (see license.txt for details), Copyright (c) 2000-2022, ReportLab Inc.",
        description="The Reportlab Toolkit",
        long_description="""The ReportLab Toolkit. An Open Source Python library for generating PDFs and graphics.""",

        author="Andy Robinson, Robin Becker, the ReportLab team and the community",
        author_email="reportlab-users@lists2.reportlab.com",
        url="http://www.reportlab.com/",
        packages=[
                'reportlab',
                'reportlab.graphics.charts',
                'reportlab.graphics.samples',
                'reportlab.graphics.widgets',
                'reportlab.graphics.barcode',
                'reportlab.graphics',
                'reportlab.lib',
                'reportlab.pdfbase',
                'reportlab.pdfgen',
                'reportlab.platypus',
                ],
        package_dir = PACKAGE_DIR,
        package_data = {'reportlab': reportlab_files},
        ext_modules =   EXT_MODULES,
        classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Topic :: Printing',
            'Topic :: Text Processing :: Markup',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            ],
        
        #this probably only works for setuptools, but distutils seems to ignore it
        install_requires=['pillow>=9.0.0', 'rlPyCairo>=0.2.0,<1','freetype-py>=2.3.0,<2.4'],
        python_requires='>=3.7,<4',
        extras_require={
            'RL_ACCEL': ['rl_accel>=0.9.0,<1.1'],
            'RL_RENDERPM': ['rl_renderPM>=4.0.3,<4.1'],
            },
        )
    print()
    print('########## SUMMARY INFO #########')
    print('\n'.join(INFOLINES))

if __name__=='__main__':
    main()
