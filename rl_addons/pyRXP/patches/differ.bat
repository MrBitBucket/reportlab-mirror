@echo off
rem command used to get patch differences
diff -rc -I"Copyright (c) 1997" -I"$Header: /tmp/reportlab/rl_addons/pyRXP/patches/differ.bat,v 1.2 2003/04/01 08:03:56 rgbecker Exp $Id:" -x"Entries" %1 %2 > %3
