import string, os, sys
from encoding import char_index
def parseAFM(filename, encoding, info={}):
	"""Returns an array holding the widths of all characters in the font.
	Ultra-crude parser"""
	alllines = open(filename, 'r').readlines()
	# get stuff between StartCharMetrics and EndCharMetrics
	metriclines = []
	between = 0
	for line in alllines:
		lline = string.lower(line)
		i = string.find(lline,'fontname')
		if i>=0:
			fontname = string.strip(line[i+9:])
			info['fontname'] = fontname
		if string.find(lline, 'endcharmetrics') > -1:
			between = 0
			break
		if between:
			metriclines.append(line)
		if string.find(lline, 'startcharmetrics') > -1:
			between = 1
			
	# break up - very shaky assumption about array size
	widths = [0] * 256
	
	for line in metriclines:
		chunks = string.split(line, ';')
		
		(c, cid) = string.split(chunks[0])
		(wx, width) = string.split(chunks[1])
		(n, name) = string.split(chunks[2])
		#(b, x1, y1, x2, y2) = string.split(chunks[3])
		x = char_index(name,encoding)
		width = int(width)
		cid=int(cid)
		widths[x] = width

	# by default, any empties should get the width of a space
	for i in range(len(widths)):
		if widths[i] == 0:
			widths[i] == widths[32]

	return widths

D=sys.argv[1]
f=open(os.path.join(D,'afm_widths_dump.py'),'w')
f.write('widths={\n')
E = ('standard', 'pdfdoc', 'macroman', 'winansi')
E = ('macroman', 'winansi')
F = os.listdir(D)
for e in E:
	f.write("\t'%s': {\n" % e)
	for fn in F:
		fn = os.path.join(D,fn)
		if os.path.isfile(fn) and string.lower(fn[-4:])=='.afm':
			info={}
			w = parseAFM(fn,e,info)
			f.write("\t\t'%s': %s,\n"% (string.lower(info['fontname']), repr(w)))
	f.write('\t\t}')
	if e!=E[-1]: f.write(',')
	f.write('\n')

f.write('\t}\n')
