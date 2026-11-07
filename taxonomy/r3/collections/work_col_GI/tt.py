import pickle,csv,sys,re
T=pickle.load(open('work_col_GI/titles.pkl','rb'))
r=list(csv.DictReader(open('in_col_GI.csv')))
fpat=sys.argv[1]; lpat=re.compile(sys.argv[2]); fams=sys.argv[3]; mn=int(sys.argv[4]) if len(sys.argv)>4 else 0; k_=int(sys.argv[5]) if len(sys.argv)>5 else 8
for x in r:
  if x['file'].startswith(fpat) and lpat.search(x['label']) and x['family'] in fams and int(x['objects'])>=mn:
    k=(x['file'],x['label'],x['family'])
    print(x['label'][:40],x['family'],x['objects'],'|',' ; '.join(f'{t[:28]}:{n}' for t,n in T.get(k,{}).most_common(k_)))
