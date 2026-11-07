SPEC = {}
def S(code, pat=None, kw=None, prof="islam", excl=None, node=None, src=None, met=(), rows=(), ov=None, zh=None, jp=None, ich=None, defn=None):
    assert code not in SPEC, code
    SPEC[code] = dict(pat=pat or [], kw=kw, prof=prof, excl=excl, node=node, src=src, met=list(met), rows=list(rows), ov=ov or {}, zh=zh, jp=jp, ich=ich, defn=defn)
