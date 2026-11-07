import ex_L1, ex_L2, ex_L3
EXTRA, EXIST = {}, {}
for m in (ex_L1, ex_L2, ex_L3):
    EXTRA.update(m.E); EXIST.update({k: v for k, v in m.X.items() if v is not None})
NEW_LEAVES = []
MOVES = []
