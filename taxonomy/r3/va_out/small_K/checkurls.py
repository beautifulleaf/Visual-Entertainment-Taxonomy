import sys, json, urllib.parse, importlib, subprocess, time
sys.path.insert(0,'.')
def wiki_check(titles):
    T=list(titles); missing=[]; redir={}
    for i in range(0,len(T),20):
        url='https://en.wikipedia.org/w/api.php?'+urllib.parse.urlencode({'action':'query','format':'json','redirects':1,'titles':'|'.join(T[i:i+20])})
        for attempt in range(6):
            out=subprocess.run(['curl','-s','-m','30',url],capture_output=True,text=True).stdout
            try: d=json.loads(out); break
            except Exception: time.sleep(8*(attempt+1))
        else: raise SystemExit('rate limited')
        for p in d['query']['pages'].values():
            if 'missing' in p or 'invalid' in p: missing.append(p.get('title'))
        for r in d['query'].get('redirects',[]): redir[r['from']]=r['to']
        time.sleep(1.5)
    return missing, redir
if __name__=='__main__':
    mod = importlib.import_module(sys.argv[1])
    titles=set()
    for code, rows in mod.R.items():
        for r in rows:
            if r[3].startswith('https://en.wikipedia.org/wiki/'):
                titles.add(urllib.parse.unquote(r[3].split('/wiki/',1)[1]).split('#')[0].replace('_',' '))
    m,rd=wiki_check(titles)
    print('checked',len(titles)); print('MISSING',m); print('REDIRECTS',rd)
