#!/usr/bin/env python
import sitecustomize
import sys
from reportlab.pdfbase.pdfutils import preProcessImages

for spec in sys.argv[1:]:
	preProcessImages(spec)
