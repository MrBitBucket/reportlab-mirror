# -*- coding: UTF-8 -*-
"""
Updates the version infos
"""

import time
import re
import cgi

VERSION = open("VERSION.txt", "r").read().strip()
BUILD = time.strftime("%Y-%m-%d")
FILES = [
    "setup_egg.py",
    #"src/pyxer/setup.py",
    #"src/pyxer/__init__.py",
    #"docs/pyxer.html",
    ]

rxversion = re.compile("VERSION{.*?}VERSION", re.MULTILINE | re.IGNORECASE | re.DOTALL)
rxbuild = re.compile("BUILD{.*?}BUILD", re.MULTILINE | re.IGNORECASE | re.DOTALL)
rxversionhtml = re.compile("\<\!--VERSION--\>.*?\<\!--VERSION--\>", re.MULTILINE | re.IGNORECASE | re.DOTALL)
rxhelphtml = re.compile("\<\!--HELP--\>.*?\<\!--HELP--\>", re.MULTILINE | re.IGNORECASE | re.DOTALL)

for fname in FILES:
    data = open(fname, "rb").read()
    data = rxversion.sub("VERSION{" + VERSION + "}VERSION", data)
    data = rxversionhtml.sub("<!--VERSION-->" + VERSION + "<!--VERSION-->", data)
    data = rxbuild.sub("BUILD{" + BUILD + "}BUILD", data)
    open(fname, "wb").write(data)
print "Done."
