import pandas as pd, sys
R='/home/user/Visual-Entertainment-Taxonomy/data/interim/regional/'
spec={
 'africa':('africa_objects.csv',['culture','culture_group','labels_recorded','place'],['object_group','object_type'],'materials','institution','url','title','date_begin'),
 'aot':('africa_oceania_targeted_objects.csv',['culture','culture_group','labels_recorded','place'],['object_group','object_type'],'materials','institution','url','title','date_begin'),
 'amoc':('americas_oceania_objects.csv',['culture','culture_group','labels_recorded','place'],['object_group','object_type'],'materials','institution','url','title','date_begin'),
 'ssea':('south_southeast_asia_objects.csv',['culture','culture_group','labels_recorded','place'],['object_group','object_type'],'materials','institution','url','title','date_begin'),
 'east':('east_asia_objects.csv',['country','period_en','object_subtype'],['object_type'],'designation_en','holder','url','title_en','date_begin'),
 'efolk':('europe_folk_objects.csv',['culture','node_key'],['medium'],'medium','institution','url','title',None),
 'gap':('gap_sweep_objects.csv',['node_label','labels','place'],['object_group'],'flag','institution','url','title','date_begin'),
 'him':('himalaya_central_asia_objects.csv',['tradition','traditions_all','place_recorded','country','period'],['object_type'],'materials','institution','url','title','date_begin'),
 'isl':('islamic_objects.csv',['dynasty','culture_place','production_centre','school_workshop'],['object_type'],'materials_technique','institution','url','title','date_begin'),
 'smith':('smithsonian_objects.csv',['culture','culture_indexed','nmai_culture_area','nmai_archeol_1','place','school_style','period'],['object_type','object_name'],'medium','unit','record_link','title','begin_year'),
 'wx':('world_extra_objects.csv',['culture_label','culture_keys','place','country','period'],['object_type','object_group'],'materials','institution','url','title','date_begin'),
 'wfolk':('world_folk_objects.csv',['node_label','culture'],['medium'],'medium','institution','url','title',None),
}
out=[]
for k,(f,cc,tc,mc,ic,uc,tt,dc) in spec.items():
    df=pd.read_csv(R+f,dtype=str,keep_default_na=False,on_bad_lines='skip')
    o=pd.DataFrame({'f':k,
      'ck':df[cc].agg(' | '.join,axis=1),
      'ot':df[tc].agg(' | '.join,axis=1),
      'mat':df[mc],'inst':df[ic],'url':df[uc],'title':df[tt],
      'date':df[dc] if dc else ''})
    if k=='east':
        o['title']=[t or o2 for t,o2 in zip(df['title_en'],df['title'])]
    out.append(o); print(k,len(o),file=sys.stderr)
A=pd.concat(out,ignore_index=True)
A.to_pickle('/home/user/Visual-Entertainment-Taxonomy/taxonomy/r3/va_out/small_D_F/work/all.pkl')
print(len(A))
