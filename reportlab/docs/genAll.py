#!/bin/env python
"""Runs the three manual-building scripts"""
if __name__=='__main__':
    import os, sys
    d = os.path.dirname(sys.argv[0])

    #need a quiet mode for the test suite   
    if '-s' in sys.argv:  # 'silent
        quiet = '-s'
    else:
        quiet = ''
        
    if not d: d = '.'
    if not os.path.isabs(d):
        d = os.path.normpath(os.path.join(os.getcwd(),d))
    for p in ('reference/genreference.py',
              'userguide/genuserguide.py',
              'graphguide/gengraphguide.py',
              '../tools/docco/graphdocpy.py'):
        os.chdir(d)
        os.chdir(os.path.dirname(p))
        os.system('%s %s %s' % (sys.executable,os.path.basename(p), quiet))
