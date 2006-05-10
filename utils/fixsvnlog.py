import sys, re
f=open(sys.argv[1],'r')
T = f.read()
f.close()
pat=re.compile('^-+$',re.M)
for l in filter(None,reversed(pat.split(T))):
    l = [l for l in l.split('\n')
        if l.strip() and not l.strip().startswith('Changed')]
    if l:
        l.insert(1,l.pop())
        l[1:] = ['\t'+x.strip() for x in reversed(l[1:])]
    print '\n'.join(l)
