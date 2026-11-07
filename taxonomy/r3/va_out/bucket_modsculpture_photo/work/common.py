import json, os
ROOT='/home/user/Visual-Entertainment-Taxonomy'
NORM={'Kingdom of Portugal':'Portugal','German Reich':'Germany','East Germany':'Germany','West Germany':'Germany','Nazi Germany':'Germany',
'Kingdom of Prussia':'Germany','Free State of Prussia':'Germany','German Empire':'Germany','Weimar Republic':'Germany','Kingdom of Bavaria':'Germany','Prussia':'Germany','Hamburg':'Germany','Duchy of Anhalt':'Germany','Free State of Anhalt':'Germany','Grand Duchy of Baden':'Germany',
'Empire of Japan':'Japan','Kingdom of the Netherlands':'Netherlands','Russian Empire':'Russia','Russian Socialist Federative Soviet Republic':'Russia','Russian Republic':'Russia',
'Kingdom of Italy':'Italy','Grand Duchy of Finland':'Finland','Austria–Hungary':'Austria','Cisleithania':'Austria','Kingdom of Denmark':'Denmark',
'United Kingdom of Great Britain and Ireland':'United Kingdom','Socialist Federal Republic of Yugoslavia':'Yugoslavia','Kingdom of Yugoslavia':'Yugoslavia','Kingdom of Serbs, Croats and Slovenes':'Yugoslavia',"Federal People's Republic of Yugoslavia":'Yugoslavia','Federal Republic of Yugoslavia':'Yugoslavia','Independent State of Croatia':'Croatia',
'Czechoslovakia':'Czech Republic','Ottoman Empire':'Turkey','British Raj':'India','Dominion of India':'India','Kingdom of Hungary':'Hungary',
'Crown Colony of Malta':'Malta','State of Malta':'Malta','Union of South Africa':'South Africa','Irish Free State':'Ireland','Congress Poland':'Poland','Second Polish Republic':'Poland',
"Ukrainian People's Republic":'Ukraine','Pahlavi Iran':'Iran','Qajar Iran':'Iran','Republic of China':'Taiwan','Taiwan under Japanese rule':'Taiwan',"People's Republic of China":'China','United Principalities of Moldavia and Wallachia':'Romania','French protectorate of Tunisia':'Tunisia','Palestine':'Palestine'}
SPECIAL={'Kingdom of Serbs, Croats and Slovenes'}
def countries(s):
    s=s or ''
    for sp in SPECIAL: s=s.replace(sp,'KSCS')
    out=[]
    for p in s.split(', '):
        p=p.strip()
        if not p: continue
        if p=='KSCS': p='Yugoslavia'
        p=NORM.get(p,p)
        if p=='Soviet Union': p='Soviet Union'
        if p not in out: out.append(p)
    return out
def main_country(s):
    c=countries(s)
    # prefer specific successor over Soviet Union / Yugoslavia when present
    spec=[x for x in c if x not in ('Soviet Union','Yugoslavia')]
    if 'Soviet Union' in c and spec: 
        if 'Russia' in spec: return 'Russia'
        return spec[0]
    if 'Soviet Union' in c: return 'Russia'
    if 'Yugoslavia' in c and spec: return spec[0]
    return c[0] if c else ''
def load():
    return json.load(open(ROOT+'/taxonomy/r3/va_in/bucket_modsculpture_photo.json'))['leaves']
