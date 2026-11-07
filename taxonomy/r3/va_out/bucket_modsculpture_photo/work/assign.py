A={}
for line in open('assign.txt'):
    line=line.strip()
    if not line or line.startswith('#'): continue
    head,rest=line.split(': ',1)
    code,grp=head.split('|')
    for n in [x.strip() for x in rest.split(';') if x.strip()]:
        if n in A: continue
        A[n]=code if grp=='x' else (code,grp)
A['']='A5-111'
