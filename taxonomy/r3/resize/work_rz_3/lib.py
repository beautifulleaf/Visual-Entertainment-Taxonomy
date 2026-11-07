import json, os, re
D = os.path.join(os.path.dirname(__file__), "..")
INP = {l["code"]: l for l in json.load(open(os.path.join(D, "in_rz_3.json")))["leaves"]}
def norm(s): return re.sub(r"\s+", " ", s.lower()).strip()
class Leaf:
    def __init__(self, code):
        self.l = INP[code]; self.T = self.l["titles"]; self.A = {}; self.moves = []
    def find(self, name, field="title"):
        ex = name.endswith("$"); n = norm(name.rstrip("$"))
        hits = [t for t in self.T if (norm(t[field]) == n if ex else norm(t[field]).startswith(n))]
        if not hits: print("NO MATCH", self.l["code"], name)
        return hits
    def put(self, names, key, sec, field="title"):
        for nm in names:
            for t in self.find(nm, field): self.A[t["id"]] = [key, sec]
    def who(self, subs, key, sec, maxyear=None):
        for t in self.T:
            if any(s.lower() in (t["who"] or "").lower() for s in subs):
                if maxyear and int(str(t["year"])[:4]) > maxyear: continue
                self.A[t["id"]] = [key, sec]
    def move(self, name, target, why):
        for t in self.find(name):
            self.moves.append([t["id"], target, why]); self.A.pop(t["id"], None)
    def rest(self, fn):
        mv = {m[0] for m in self.moves}
        for t in self.T:
            if t["id"] not in self.A and t["id"] not in mv: self.A[t["id"]] = fn(t)
def yr(t):
    m = re.match(r"\d{4}", str(t["year"])); return int(m.group()) if m else 2000
OUT = {}
def save():
    p = os.path.join(D, "out_rz_3.json")
    old = json.load(open(p)) if os.path.exists(p) else {}
    old.update(OUT); json.dump(old, open(p, "w"), ensure_ascii=False, indent=1)
