@echo off
rem command used to get patch differences
diff -rc -I"Copyright (c) 1997" -I"$Header: /tmp/reportlab/rl_addons/pyRXP/patches/differ.bat,v 1.1 2002/03/22 11:07:52 rgbecker Exp $Id:" %1 %2 > %3
