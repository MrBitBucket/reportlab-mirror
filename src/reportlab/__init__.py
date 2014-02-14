#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/__init__.py
__version__=''' $Id$ '''
__doc__="""The Reportlab PDF generation library."""
Version = "3.0"

import sys

if sys.version_info[0:2]!=(2, 7) and sys.version_info<(3, 3):
    raise ImportError("""reportlab requires Python 2.7+ or 3.3+; 3.0-3.2 are not supported.""")

#define these early in reportlab's life
isPy3 = sys.version_info[0]==3
if isPy3:
    def cmp(a,b):
        return -1 if a<b else (1 if a>b else 0)

    import builtins
    builtins.cmp = cmp
    builtins.xrange = range
    del cmp, builtins
else:
    from future_builtins import ascii
    import __builtin__
    __builtin__.ascii = ascii
    del ascii, __builtin__

#the module reportlab.local_rl_mods can be used to customize just about anything
try:
    import reportlab.local_rl_mods
except ImportError:
    pass
