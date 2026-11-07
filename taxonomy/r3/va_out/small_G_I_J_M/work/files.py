import csv, os
csv.field_size_limit(10**9)
R = os.path.join(os.path.dirname(__file__), '../../../../../data/interim/regional')
# file -> (culture columns, type columns, title col, date cols, inst col, url col)
SPEC = {
 'africa': (['culture','culture_group','labels_recorded'], ['object_group','object_type','materials'], 'title', ('date_text','date_begin'), 'institution', 'url', 'place'),
 'africa_oceania_targeted': (['culture','culture_group','labels_recorded'], ['object_group','object_type','materials'], 'title', ('date_text','date_begin'), 'institution', 'url', 'place'),
 'americas_oceania': (['culture','culture_group','labels_recorded'], ['object_group','object_type','materials'], 'title', ('date_text','date_begin'), 'institution', 'url', 'place'),
 'south_southeast_asia': (['culture','culture_group','labels_recorded','place'], ['object_group','object_type','materials'], 'title', ('date_text','date_begin'), 'institution', 'url', 'place'),
 'east_asia': (['period_en','country','designation_en'], ['object_type','object_subtype'], 'title_en', ('date','date_begin'), 'holder', 'url', 'country'),
 'europe_folk': (['node_key','culture'], ['medium'], 'title', ('date',None), 'institution', 'url', 'culture'),
 'gap_sweep': (['node_label','labels','place'], ['object_group'], 'title', ('date_text','date_begin'), 'institution', 'url', 'place'),
 'himalaya_central_asia': (['tradition','traditions_all','place_recorded','tradition_recorded'], ['object_type','medium','materials'], 'title', ('date_text','date_begin'), 'institution', 'url', 'place_recorded'),
 'islamic': (['dynasty','dynasty_recorded','culture_place','production_centre','school_workshop'], ['object_type','materials_technique','techniques'], 'title', ('date_text','date_begin'), 'institution', 'url', 'culture_place'),
 'smithsonian': (['culture','culture_indexed','nmai_culture_area','nmai_archeol_1','nmai_archeol_2','nmai_archeol_3','school_style','period','place'], ['object_type','object_name','object_type_indexed','medium'], 'title', ('date','begin_year'), 'unit', 'record_link', 'place'),
 'world_extra': (['culture_label','culture_keys','culture_path','place'], ['object_type','object_group','materials'], 'title', ('period','date_begin'), 'institution', 'url', 'place'),
 'world_folk': (['node_label','culture'], ['medium'], 'title', ('date',None), 'institution', 'url', 'culture'),
}
def rows(name):
    s = SPEC[name]
    with open(os.path.join(R, name + '_objects.csv'), newline='') as f:
        for r in csv.DictReader(f):
            cult = ' | '.join(r.get(c) or '' for c in s[0])
            typ = ' | '.join(r.get(c) or '' for c in s[1])
            yield r, cult, typ
