import json, os
ROOT='/home/user/Visual-Entertainment-Taxonomy'
NORM={'Kingdom of Portugal':'Portugal','German Reich':'Germany','East Germany':'Germany','West Germany':'Germany','Nazi Germany':'Germany',
'Kingdom of Prussia':'Germany','Free State of Prussia':'Germany','German Empire':'Germany','Weimar Republic':'Germany','Kingdom of Bavaria':'Germany','Prussia':'Germany','Hamburg':'Germany','Duchy of Anhalt':'Germany','Free State of Anhalt':'Germany','Grand Duchy of Baden':'Germany',
'Empire of Japan':'Japan','Kingdom of the Netherlands':'Netherlands','Russian Empire':'Russia','Russian Socialist Federative Soviet Republic':'Russia','Russian Republic':'Russia',
'Kingdom of Italy':'Italy','Grand Duchy of Finland':'Finland','Austria–Hungary':'Austria','Cisleithania':'Austria','Kingdom of Denmark':'Denmark',
'United Kingdom of Great Britain and Ireland':'United Kingdom','Socialist Federal Republic of Yugoslavia':'Yugoslavia','Kingdom of Yugoslavia':'Yugoslavia','Kingdom of Serbs, Croats and Slovenes':'Yugoslavia',"Federal People's Republic of Yugoslavia":'Yugoslavia','Federal Republic of Yugoslavia':'Yugoslavia','Independent State of Croatia':'Croatia',
'Czechoslovakia':'Czech Republic','Ottoman Empire':'Turkey','British Raj':'India','Dominion of India':'India','Kingdom of Hungary':'Hungary',
'Crown Colony of Malta':'Malta','State of Malta':'Malta','Union of South Africa':'South Africa','Irish Free State':'Ireland','Congress Poland':'Poland','Second Polish Republic':'Poland',
"Ukrainian People's Republic":'Ukraine','Pahlavi Iran':'Iran','Qajar Iran':'Iran','Republic of China':'Taiwan','Taiwan under Japanese rule':'Taiwan',"People's Republic of China":'China','United Principalities of Moldavia and Wallachia':'Romania','French protectorate of Tunisia':'Tunisia','Palestine':'Palestine','Kingdom of Great Britain':'United Kingdom','England':'United Kingdom','Kingdom of Scotland':'United Kingdom','Colony of New Zealand':'New Zealand','Qing dynasty':'China','Austrian Empire':'Austria','Kingdom of Saxony':'Germany','Kingdom of Sardinia':'Italy','Papal States':'Italy','Republic of Geneva':'Switzerland','First French Empire':'France','Electorate of Hesse':'Germany','Duchy of Saxe-Weimar-Eisenach':'Germany','Kingdom of Württemberg':'Germany','Kingdom of Lombardy–Venetia':'Italy','Mandatory Palestine':'Israel','Russian Soviet Federative Socialist Republic':'Russia','Duchy of Nassau':'Germany','Dutch East Indies':'Indonesia','State of East Indonesia':'Indonesia','Sierra Leone Colony and Protectorate':'Sierra Leone','Banovina of Croatia':'Croatia','State of Slovenes, Croats and Serbs':'Croatia','French Indochina':'Vietnam','Q965':'Burkina Faso','Q1005':'Gambia','Q1045':'Somalia','Q805':'Yemen','Q878':'United Arab Emirates','Q819':'Laos'}
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
