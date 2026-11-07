import csv,json
csv.field_size_limit(10**9)
R=list(csv.DictReader(open('../../ft_in/animation_non_japanese.csv')))
a=json.load(open('asg.json'))
NOTE={"Who Framed Roger Rabbit":"","Cool World":"Bakshi adult hybrid","Klaus":"Spanish SPA Studios hand-drawn feature","Fantasia 2000":"","The Lion King@2019":"photoreal CG remake","The Jungle Book@2016":"photoreal CG remake","Mufasa: The Lion King":"photoreal CG remake","Charlotte's Web":"Hanna-Barbera feature","The Transformers: The Movie":"","Batman: Death in the Family":"interactive DC feature","Scary Godmother: Halloween Spooktakular":"TV film","The Adventures of Tintin@2011":"Spielberg motion-capture film","Teen Titans: Trouble in Tokyo":"","Seoul Station":"Korean adult zombie feature","Watchmen: Chapter I":"","Mary and Max":"claymation","Memoir of a Snail":"claymation","Anomalisa":"stop-motion","DuckTales@2017–2021":"reboot of the Disney Afternoon series","The Looney Tunes Show":"Looney Tunes revival","Robin Robin":"Aardman TV special","Olaf's Frozen Adventure":"theatrical featurette","Mickey's Christmas Carol":"theatrical featurette","Skibidi Toilet":"YouTube series","Kid vs. Kat":"","Stillwater":"","Tutenstein":""}
SEE={"Cool World":"C12-19","Who Framed Roger Rabbit":"","The Lord of the Rings":"C12-19","Fire and Ice":"C12-19","American Pop":"C12-19","Mad God":"C12-19","Anomalisa":"C12-18","Persepolis":"C12-19","Seoul Station":"C12-18","Watchmen: Chapter I":"C12-19","Watchmen: Chapter II":"C12-19","Injustice":"","The Adventures of Tintin@2011":"C12-13","Smurfs: The Lost Village":"C12-13","Gargoyles":"C13-13","Avatar: The Last Airbender":"C13-7","Teen Titans Go!":"C13-11","Harley Quinn":"C13-11","Steven Universe":"C13-13","Danny Phantom":"C13-7","Robin Robin":"C14-7","Scoob!":"C12-10","Star Wars: The Clone Wars@2008":"C13-13"}
def key(x):
    for k in (x['title']+'@'+x['year'],x['title']): yield k
with open('assign.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['id','leaf','sec','see_also','note','route'])
    for x in R:
        leaf,sec=a[x['id']]
        note=next((NOTE[k] for k in key(x) if NOTE.get(k)),'')
        see=next((SEE[k] for k in key(x) if SEE.get(k)),'')
        if leaf=='ROUTE': w.writerow([x['id'],'','','','Japanese Sanrio series',sec]); continue
        w.writerow([x['id'],leaf,sec,see,note,''])
