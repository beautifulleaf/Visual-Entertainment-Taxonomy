import json, sys, importlib
sys.path.insert(0, '.')
from common import *
import arch_cfg
out = {"leaves": {}, "new_leaves": [], "moves_out": MOVES, "dropped": DROPPED}
for code, l in LEAVES.items():
    for r in l['rows']:
        if r[1].startswith('Gathered rows'):
            DROPPED.append([code, r[0], "the leaf's own style label restated (evidence row), not a kind"])
for code in arch_cfg.CFG:
    out['leaves'][code] = arch_cfg.build_arch(code)
for mod in ['cfg_modern', 'cfg_print', 'cfg_deco', 'cfg_vase', 'cfg_misc']:
    try:
        m = importlib.import_module(mod)
    except ModuleNotFoundError:
        continue
    m.build(out)
# fall back: untouched leaves pass through
for code, l in LEAVES.items():
    if code not in out['leaves']:
        ks = [[r[0] or '(unnamed)', r[1] or 'Sub-types', '', r[3], r[4]] for r in l['rows'] if not r[1].startswith('Gathered')]
        out['leaves'][code] = {"axis": "provisional", "kinds": ks}
# individual fixes
OVR = {('K4-13', 'Villard de Honnecourt'): ('French cathedral masters', '13th-century Picard master known from his portfolio of drawings (BnF, Paris)'),
       ('K6-22', 'Branko Žeželj'): ('Yugoslav modernism', None), ('K6-26', 'Ilze Wolff'): ('South Africa', None), ('K6-26', 'Jing Liu'): ('United States', 'b. 1980, co-founder of SO-IL, New York'),
       ('I3-16', 'Christofle'): ('Jewellery and silver', 'Paris silversmiths; Art Deco silver for the liner Normandie')}
OUTM = {('K6-21', 'William Lethaby'): 'K6-1', ('K6-21', 'Charles Robert Ashbee'): 'K6-1', ('K5-24', "Émile Prisse d'Avennes"): 'K3-1'}
for code, v in out['leaves'].items():
    keep = []
    for x in v['kinds']:
        if (code, x[0]) in OVR:
            g, gl = OVR[(code, x[0])]; x[1] = g
            if gl: x[2] = gl
        if (code, x[0]) in OUTM and x[4]:
            MOVES.append([x[0], code, OUTM[(code, x[0])]]); continue
        if code == 'K6-21' and x[0] == 'Jacques-Émile Ruhlmann':
            continue
        keep.append(x)
    v['kinds'] = keep
rr = [r for r in LEAVES['K6-21']['rows'] if r[0] == 'Jacques-Émile Ruhlmann'][0]
dk = out['leaves']['I3-16']['kinds']
for x in dk:
    if x[0] == 'Émile-Jacques Ruhlmann':
        x[0] = rr[0]; x[3] = rr[3]
# clean two sub-style glosses, make groups contiguous
FIX = {'Mannerism = Mannerist architecture (alias of that kind)': 'Mannerism as tagged on buildings: Mannerist architecture',
       'Romanticism = Romantic (early Gothic Revival) historicism; the art movement itself is artist-led': 'Romanticism as tagged on buildings: the Romantic, early phase of Gothic Revival historicism'}
def contig(ks):
    first = {}
    for i, x in enumerate(ks):
        first.setdefault(x[1], i)
    return sorted(ks, key=lambda x: first[x[1]])
for v in list(out['leaves'].values()) + out['new_leaves']:
    for x in v['kinds']:
        x[2] = FIX.get(x[2], x[2])
    v['kinds'] = contig(v['kinds'])
json.dump(out, open('result.json', 'w'), ensure_ascii=False, indent=0)
