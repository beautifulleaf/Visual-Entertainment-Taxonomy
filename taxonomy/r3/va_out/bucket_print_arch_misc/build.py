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
json.dump(out, open('result.json', 'w'), ensure_ascii=False, indent=0)
