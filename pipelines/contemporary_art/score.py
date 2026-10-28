"""Contemporary-artist composite score and regional selection (visual-art-plan.md §2.3, §3.5).

Decided rule (2026-10-28): everyone on the 21 canon lists is auto-included; everyone
else is ranked by a composite score WITHIN THEIR REGION, and each region's cutoff is
set so the total lands at about 10-12k.

Signals (one row per artist, all "more is more prominent")
  lists      n_list_entries: canon-list entries (Kunstkompass, Power 100, Artprice,
             biennials, prizes). Every artist with one is auto-included, so for the
             non-auto artists this signal is constant and does not move the cutoff;
             it only orders the auto-includes in the output.
  museum     n_museum_ids: open-data museum collections with an ID for the artist
             (MoMA, Tate, Whitney, AIC, Met, NGA, SFMOMA, Stedelijk, Reina Sofia, ...).
  ulan       has a Getty ULAN ID (institutional cataloguing).
  market     number of market IDs: Artnet, Artsy, Artprice, MutualArt.
  pageviews  mean monthly Wikipedia pageviews over all language editions
             (data/interim/contemporary_pageviews.csv, from pipelines/visual_art/pageviews.py).
  sitelinks  Wikimedia sitelinks.
  awards     n_awards (Wikidata P166, all awards).
Gallery representation (P1875) and exhibition history (P608) are too sparse to use (§3.1b).

Weights (defaults; override with --weights name=value,...; they are renormalised to 1)
  plan §3.5:  Artfacts 0.25, biennial/lists 0.20, museums 0.15, attention 0.20,
              market 0.10, prizes 0.10.
  There is no Artfacts data (no bulk access), so its 0.25 moves to the museum and
  market IDs (§2.3): museums 0.15 -> 0.30 (0.25 museum count + 0.05 ULAN) and
  market 0.10 -> 0.20. Attention 0.20 is split evenly between pageviews and sitelinks.
  => lists 0.20, museum 0.25, ulan 0.05, market 0.20, pageviews 0.10, sitelinks 0.10,
     awards 0.10.

Percentiles: each signal becomes a mid-rank percentile within the artist's region
(ties share a rank, as in pipelines/visual_art/depth_model.py), so an artist is compared
with artists whose Wikipedia and museum coverage is similar. Pool artists with no
region form an "Unknown" region.

Celebrity factor: composite *= min(1, art_occ_share / --celeb-share) (default 0.5), so
people who are mainly musicians, politicians or actors and also paint (Bowie,
George W. Bush, Selena Gomez: art_occ_share ~0.1) keep ~20% of their score, while
anyone with at least half their occupations in art is untouched. Collectives have no
occupations (art_occ_share blank) and get factor 1.
region_percentile is the mid-rank percentile of the final score within the region.

Selection
  auto     every list artist: pool artists with n_lists > 0, plus those
           resolve_list_artists.py matched to a pool QID, plus resolved artists outside
           the pool (contemporary_pool_additions.csv, scored like pool rows), plus
           unresolved list-only names (keyed "list:<norm_name>", no score).
  regional one common selection fraction f is applied to every region: region r gets a
           quota Q_r = max(A_r, round(f * N_r)) where N_r is its scored rows (pool +
           additions) and A_r its auto-includes among them, so each region's share of
           the selection matches its share of the pool and the auto-includes count
           against that share (Europe and North America, which hold most list
           artists, do not get extra slots on top). Regions in --floor-regions
           (default: the non-Western regions, whose Wikidata coverage is thinnest)
           get at least their top --floor (25%). The Q_r - A_r best-scoring non-auto
           artists are selected, and f is found by bisection so that the total
           (all auto-includes, list-only names included, plus regional picks) is
           --target (default 11,000). List-only names are added outside the quotas so
           they do not take slots from resolved artists in the same region.
  The region's cutoff is the score of its last selected non-auto artist.
  Market-record check (§3.4, --market-check, on by default): an Artnet/Artsy/Artprice/
           MutualArt record only counts when the artist also has an independent signal
           (a museum ID, a ULAN/Tate/MoMA ID, a list entry, an award, >= 5 sitelinks or
           a regional pageview percentile >= 0.5). Without one, the artist's market
           percentile is 0 (below artists with no market record, whose tied percentile
           is ~0.3), so vanity and minor-auction listings do not lift a score. Everyone
           else's market percentile is unchanged.
Routes added ON TOP of the regional quotas (the --target total covers auto-includes and
regional picks only, so the final total is larger)
  movement_guarantee  contemporary selection has no movement skeleton, so movements
           whose members are individually modest (Mono-ha, Dansaekhwa, Gutai, Arte
           Povera, Political Pop...) could end up with one or two names. Pool artists'
           P135 (movement) is fetched (cached in data/raw/wikidata/contemporary/) and a
           movement is kept when it is an art movement / style / group (the class list
           of pipelines/visual_art/build_modern_reference.py, direct or one subclass
           step), began in --movement-since (1945) or later (undated: median member
           birth >= --movement-median-birth, 1915), is not an umbrella term (contemporary
           art, modern art, abstract art, postmodernism, avant-garde...) and has >= 3
           scored members. Its top K = max(3, round(0.15 x members)), at most 15,
           members by holdings (n_museum_ids, then ULAN/Tate/MoMA presence, then score)
           are included, provided art_occ_share >= 0.25 (collectives: blank, allowed).
  attention   cult and popular artists the museum signals under-count (lowbrow,
           fantasy illustration, street art, internet-famous): anyone in the top 2% of
           their region by pageviews (--attention-pct 0.98) whose art_occ_share >= 0.5,
           so celebrities who also paint stay out. Two guards, because that alone let in
           mostly celebrities with one art occupation: without an art-world record
           (market/museum/ULAN/Tate/MoMA ID or list) art_occ_share must be >= 0.6
           (--attention-plain-share), and primary medium architecture or design is left
           out (--attention-exclude-media).
Route flags in the output: route_list, route_regional_score, route_movement_guarantee,
route_attention, route_manual (an artist can carry several); `routes` names them and
`guarantee_movements` names the movements an artist is guaranteed for.
  Architects stay in as gathered (§3.1b); whether they stay artists is decided in
  the classifying stage.

Inputs : data/interim/contemporary_pool.csv, contemporary_pageviews.csv,
         contemporary_list_artists.csv and contemporary_pool_additions.csv (optional)
Output : data/interim/contemporary_scores.csv, data/interim/contemporary_movements.csv
Cache  : data/raw/wikidata/contemporary/movements_P135.json, movements_meta.json
Usage  : python3 pipelines/contemporary_art/score.py [--target 11000] [--floor 0.25]
             [--weights museum=0.3,market=0.15] [--celeb-share 0.5] [--report]
             [--no-market-check] [--no-movements] [--no-attention] [--endpoint qlever]
"""
import argparse
import collections
import json
import math
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "visual_art"))
import wikidata  # noqa: E402
from build_modern_reference import MOVEMENT_TYPES, NON_MOVEMENT, ORG_WORDS  # noqa: E402
INTERIM = os.path.join(ROOT, "data", "interim")
POOL = os.path.join(INTERIM, "contemporary_pool.csv")
VIEWS = os.path.join(INTERIM, "contemporary_pageviews.csv")
LIST_ARTISTS = os.path.join(INTERIM, "contemporary_list_artists.csv")
ADDITIONS = os.path.join(INTERIM, "contemporary_pool_additions.csv")
MANUAL = os.path.join(ROOT, "seeds", "visual-art", "contemporary_manual_includes.csv")
MANUAL_EXCLUDES = os.path.join(ROOT, "seeds", "visual-art", "contemporary_manual_excludes.csv")
OUT = os.path.join(INTERIM, "contemporary_scores.csv")
MOVEMENTS_OUT = os.path.join(INTERIM, "contemporary_movements.csv")
RAW = os.path.join(ROOT, "data", "raw", "wikidata", "contemporary")

WEIGHTS = {"lists": 0.20, "museum": 0.25, "ulan": 0.05, "market": 0.20,
           "pageviews": 0.10, "sitelinks": 0.10, "awards": 0.10}
MARKET_IDS = ["artnet_id", "artsy_id", "artprice_id", "mutualart_id"]
NON_WESTERN = ["Sub-Saharan Africa", "Middle East and North Africa", "South Asia", "Southeast Asia",
               "East Asia", "Latin America and Caribbean", "Central Asia", "Asia (other)"]
UNKNOWN = "Unknown"
INDEPENDENT_IDS = ["ulan_id", "tate_id", "moma_id"]
# Umbrella terms: not movements (members span every style). Checked by label on the
# first run; the later entries were found in the pool's P135 values.
UMBRELLA = {
    "Q186030": "contemporary art", "Q38166": "modern art", "Q128115": "abstract art",
    "Q47783": "postmodernism", "Q215592": "avant-garde", "Q102932": "avant-garde",
    "Q1414236": "modernism", "Q878985": "modernism", "Q1640824": "figurative art",
    "Q2111604": "post-war art",
    # Pruned on review of the first run (2026-10-28): broad or pre-war styles and
    # traditions, and items that pass the class filter but are not visual-art movements.
    "Q10857409": "realism (broad style)", "Q147516": "magic realism (broad style)",
    "Q245188": "modern architecture (broad style)", "Q848365": "primitivism (broad style)",
    "Q837024": "social realism (broad style)", "Q273506": "School of Paris (pre-war)",
    "Q85369440": "École flamande (historical school)", "Q7059995": "Northwest Coast art (tradition)",
    "Q213457": "Beat Generation (literary)", "Q643782": "New German Cinema (film)",
    "Q1092461": "Cinema of Transgression (film)", "Q153946": "punk subculture (music)",
    "Q60749920": "Drain Gang (music collective)", "Q81220079": "The Wrecking Crew (session musicians)",
    "Q1371509": "College of 'Pataphysics (literary society)",
    "Q65149655": "comics creators' association against sexism (an association)",
    "Q4797149": "Art Workers' Coalition (activist organisation)",
    "Q1347824": "La Movida Madrileña (counterculture, mostly music and film)",
}
CHUNK = 400
MAX_ASSOCIATION = 40   # P463-only "groups" larger than this are professional associations


def parse_weights(spec):
    w = dict(WEIGHTS)
    for part in filter(None, (spec or "").split(",")):
        k, v = part.split("=")
        if k.strip() not in w:
            sys.exit(f"unknown signal {k!r}; signals: {', '.join(w)}")
        w[k.strip()] = float(v)
    total = sum(w.values())
    return {k: v / total for k, v in w.items()}


def num(s, index=None):
    if not isinstance(s, pd.Series):
        return pd.Series(float(s or 0), index=index)
    return pd.to_numeric(s, errors="coerce").fillna(0.0)


def has(df, col):
    return df[col].notna() & (df[col].astype(str).str.strip() != "") if col in df else pd.Series(False, df.index)


def signals(df):
    """Raw signal columns from pool-shaped rows (pool or additions)."""
    out = pd.DataFrame(index=df.index)
    entries = num(df.get("n_list_entries", 0), df.index)
    out["lists"] = entries.where(entries > 0, num(df.get("n_lists", 0), df.index))  # additions lack entries
    out["museum"] = num(df.get("n_museum_ids", 0), df.index)
    out["ulan"] = has(df, "ulan_id").astype(float)
    out["market"] = sum(has(df, c).astype(float) for c in MARKET_IDS)
    out["pageviews"] = num(df.get("pageviews", 0), df.index)
    out["sitelinks"] = num(df.get("sitelinks", 0), df.index)
    out["awards"] = num(df.get("n_awards", 0), df.index)
    return out


def midrank_pct(values, groups):
    """Mid-rank percentile within each group: (#below + #at-or-below) / 2 / n."""
    s = pd.Series(values)
    r = s.groupby(groups).rank(method="average")
    n = s.groupby(groups).transform("size")
    return ((r - 0.5) / n).to_numpy()


def load_inputs(args):
    pool = pd.read_csv(POOL, dtype=str, keep_default_na=False)
    pool["source"] = "pool"
    notes = []
    if os.path.exists(VIEWS):
        views = pd.read_csv(VIEWS, dtype=str)
        if "pageviews" not in views:
            sys.exit(f"{VIEWS} has no pageviews column yet")
        pool = pool.merge(views[["qid", "pageviews"]], on="qid", how="left")
        notes.append(f"pageviews: {num(pool.pageviews).gt(0).sum():,} of {len(pool):,} pool artists have views")
    elif args.allow_no_pageviews:
        notes.append("pageviews MISSING: its weight is moved to sitelinks")
        args.weights["sitelinks"] += args.weights.pop("pageviews")
    else:
        sys.exit(f"missing {VIEWS}; run pipelines/visual_art/pageviews.py or pass --allow-no-pageviews")

    pool_q = set(pool.qid)
    auto_reason = {q: f"lists:{l}" for q, l in zip(pool.qid, pool.lists) if l}
    rows = [pool]
    list_only = pd.DataFrame()
    if os.path.exists(LIST_ARTISTS):
        la = pd.read_csv(LIST_ARTISTS, dtype=str, keep_default_na=False)
        names = {q: (r["label"] or r["name"]) for q, r in zip(la.qid, la.to_dict("records")) if q}
        blank = pool.label == ""
        pool.loc[blank, "label"] = pool.loc[blank, "qid"].map(names).fillna("")  # pool labels can be blank
        for _, r in la.iterrows():
            reason = f"lists:{r['lists']}"
            qids = [r["qid"]] if r["qid"] else list(filter(None, r.get("member_qids", "").split("|")))
            for q in qids:
                auto_reason.setdefault(q, reason)
        unresolved = la[(la.qid == "") & (la.get("member_qids", "") == "")]
        list_only = pd.DataFrame({
            "key": "list:" + unresolved.norm_name, "qid": "", "label": unresolved.name,
            "region": unresolved.get("region", "").replace("", UNKNOWN), "medium": "",
            "auto_include": "lists:" + unresolved.lists, "source": "list_only", "selected": 1,
        })
        notes.append(f"list artists: {len(la):,} ({(la.status == 'pool').sum():,} in pool, "
                     f"{(la.status == 'resolved_not_in_pool').sum():,} resolved outside it, "
                     f"{len(unresolved):,} list-only)")
    else:
        notes.append(f"{os.path.basename(LIST_ARTISTS)} not found: auto-includes are pool n_lists > 0 only")
    if os.path.exists(ADDITIONS):
        add = pd.read_csv(ADDITIONS, dtype=str, keep_default_na=False)
        add = add[~add.qid.isin(pool_q)].drop_duplicates("qid")
        # Historical artists on contemporary lists (e.g. Venice 2024's historical
        # section: Frida Kahlo, Wifredo Lam) belong to the modern pass (visual-art-plan §2.4).
        born = pd.to_numeric(add.birth.str[:4], errors="coerce")
        historical = add[born < 1920]
        if len(historical):
            for q in historical.qid:
                auto_reason.pop(q, None)
            add = add[~add.qid.isin(historical.qid)]
            notes.append(f"{len(historical):,} resolved list artists born before 1920 left to the modern pass")
        # A list artist resolved to someone with no art occupation (a poet, a researcher,
        # Franz Boas...) is almost certainly the wrong person: keep the list entry as a
        # list-only name instead of the wrong QID.
        wrong = add[pd.to_numeric(add.art_occ_share, errors="coerce").fillna(-1) == 0]
        if len(wrong):
            by_q = la.set_index("qid") if os.path.exists(LIST_ARTISTS) else None
            demoted = pd.DataFrame({
                "key": "list:" + wrong.qid.map(lambda q: by_q.norm_name.get(q, q) if by_q is not None else q),
                "qid": "", "label": wrong.qid.map(lambda q: by_q.name.get(q, "") if by_q is not None else ""),
                "region": wrong.region.replace("", UNKNOWN), "medium": "",
                "auto_include": wrong.qid.map(auto_reason).fillna("lists:resolved"),
                "source": "list_only_wrong_match", "selected": 1,
            })
            list_only = pd.concat([list_only, demoted], ignore_index=True)
            for q in wrong.qid:
                auto_reason.pop(q, None)
            add = add[~add.qid.isin(wrong.qid)]
            notes.append(f"{len(wrong):,} resolved list artists with no art occupation kept as list-only names (likely wrong-person matches)")
        add["source"] = "addition"
        for q, l in zip(add.qid, add.get("lists", pd.Series("", add.index))):
            auto_reason.setdefault(q, f"lists:{l}" if l else "lists:resolved")
        rows.append(add)
        notes.append(f"pool additions: {len(add):,} resolved list artists outside the pool")
    else:
        notes.append(f"{os.path.basename(ADDITIONS)} not found: no resolved list artists outside the pool")
    if os.path.exists(MANUAL):
        # Hand-curated includes for consumer categories the metrics under-count (§3.4).
        for r in pd.read_csv(MANUAL, dtype=str, keep_default_na=False).itertuples():
            auto_reason[r.qid] = f"manual:{r.category}"
        notes.append(f"manual includes: {os.path.basename(MANUAL)}")
    df = pd.concat(rows, ignore_index=True)
    df["region"] = df.region.replace("", UNKNOWN).fillna(UNKNOWN)
    df["auto_include"] = df.qid.map(auto_reason).fillna("")
    return df, list_only, notes


def independent_signal(df, sig, pv_pct):
    """Anything besides a market record that says the artist is established."""
    return ((sig.museum >= 1) | sum(has(df, c) for c in INDEPENDENT_IDS).gt(0)
            | (num(df.get("n_lists", 0), df.index) >= 1) | (sig.awards >= 1)
            | (sig.sitelinks >= 5) | (pd.Series(pv_pct, df.index) >= 0.5))


def score(df, weights, celeb_share, market_check=True):
    sig = signals(df)
    region = df.region.to_numpy()
    df["pv_pct"] = midrank_pct(sig.pageviews.to_numpy(), region)
    df["market_verified"] = independent_signal(df, sig, df.pv_pct).astype(int)
    unverified = (df.market_verified == 0).to_numpy()
    comp = np.zeros(len(df))
    for k, w in weights.items():
        df[f"pct_{k}"] = midrank_pct(sig[k].to_numpy(), region)
        if k == "market" and market_check:
            df.loc[unverified, f"pct_{k}"] = 0.0
        comp += w * df[f"pct_{k}"].to_numpy()
    share = pd.to_numeric(df.art_occ_share, errors="coerce")
    df["celebrity_factor"] = np.minimum(1.0, (share / celeb_share).fillna(1.0)).round(3)
    df["score"] = comp * df.celebrity_factor
    df["region_percentile"] = midrank_pct(df.score.to_numpy(), region)
    for k in sig:
        df[k] = sig[k]
    return df


def quotas(df, n_list_only, target, floor, floor_regions):
    g = df.groupby("region")
    N = g.size()
    A = g.apply(lambda x: (x.auto_include != "").sum())
    fl = pd.Series({r: (math.ceil(floor * N[r]) if r in floor_regions else 0) for r in N.index})

    def q(f):
        return np.minimum(N, np.maximum(np.maximum(A, (f * N).round()), fl)).astype(int)

    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if q(mid).sum() + n_list_only < target:
            lo = mid
        else:
            hi = mid
    return q(hi), A, hi


def select(df, Q, A):
    df["selected"] = (df.auto_include != "").astype(int)
    cutoffs = {}
    for r, idx in df.groupby("region").groups.items():
        sub = df.loc[idx]
        cand = sub[sub.auto_include == ""].sort_values(["score", "sitelinks"], ascending=False)
        take = cand.head(int(Q[r] - A[r]))
        df.loc[take.index, "selected"] = 1
        cutoffs[r] = (take.score.iloc[-1], take.region_percentile.iloc[-1]) if len(take) else (np.nan, np.nan)
    return cutoffs


# ---------------------------------------------------------------- movements

def chunked_cache(name, keys, query_fn):
    """{key: value} filled chunk by chunk and saved after every chunk (resumable)."""
    path = os.path.join(RAW, name)
    data = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    todo = sorted(set(keys) - set(data))
    for i in range(0, len(todo), CHUNK):
        data.update(query_fn(todo[i:i + CHUNK]))
        json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"  {name}: {min(i + CHUNK, len(todo)):,}/{len(todo):,}")
    return data


def fetch_movements(qids, endpoint):
    """P135 per artist, and label / classes / inception per movement (one query at a time)."""
    def members(chunk):
        out = {q: [] for q in chunk}
        values = " ".join("wd:" + q for q in chunk)
        for r in wikidata.sparql(f"SELECT ?a ?m WHERE {{ VALUES ?a {{ {values} }} ?a wdt:P135 ?m }}",
                                 endpoint=endpoint):
            if r["m"].startswith("Q"):
                out[r["a"]].append(r["m"])
        return out

    def meta(chunk):
        out = {m: {"label": "", "types": [], "parents": [], "start": []} for m in chunk}
        values = " ".join("wd:" + m for m in chunk)
        for r in wikidata.sparql(f"""SELECT ?m ?k ?v WHERE {{ VALUES ?m {{ {values} }}
              {{ ?m rdfs:label ?v FILTER(LANG(?v) = "en") BIND("label" AS ?k) }}
              UNION {{ ?m wdt:P31 ?v BIND("types" AS ?k) }}
              UNION {{ ?m wdt:P31/wdt:P279 ?v BIND("parents" AS ?k) }}
              UNION {{ ?m wdt:P279 ?v BIND("parents" AS ?k) }}
              UNION {{ ?m wdt:P571|wdt:P580 ?v BIND("start" AS ?k) }} }}""", endpoint=endpoint):
            rec = out[r["m"]]
            if r["k"] == "label":
                rec["label"] = r["v"]
            elif r["v"] not in rec[r["k"]]:
                rec[r["k"]].append(r["v"])
        return out

    def groups(chunk):
        # P463 (member of) is mostly academies and unions; only movement-class items count.
        out = {q: [] for q in chunk}
        values = " ".join("wd:" + q for q in chunk)
        types = " ".join("wd:" + t for t in MOVEMENT_TYPES)
        for r in wikidata.sparql(f"""SELECT DISTINCT ?a ?m WHERE {{ VALUES ?a {{ {values} }} ?a wdt:P463 ?m .
              VALUES ?t {{ {types} }} ?m wdt:P31/wdt:P279? ?t }}""", endpoint=endpoint):
            out[r["a"]].append(r["m"])
        return out

    os.makedirs(RAW, exist_ok=True)
    qids = [q for q in qids if q]
    p135 = chunked_cache("movements_P135.json", qids, members)
    p463 = chunked_cache("movements_P463.json", qids, groups)
    memberships = {q: {m: "P135" for m in p135.get(q, [])} for q in qids}
    for q in qids:
        for m in p463.get(q, []):
            memberships[q].setdefault(m, "P463")
    movs = sorted({m for q in qids for m in memberships[q]})
    meta_ = chunked_cache("movements_meta.json", movs, meta)

    def any_label(chunk):
        values = " ".join("wd:" + m for m in chunk)
        out = {m: "" for m in chunk}
        for r in wikidata.sparql(f"SELECT ?m ?v WHERE {{ VALUES ?m {{ {values} }} ?m rdfs:label ?v }}",
                                 endpoint=endpoint):
            out[r["m"]] = out[r["m"]] or r["v"]
        return out
    for m, label in chunked_cache("movements_labels_any.json",
                                  [m for m in movs if not meta_[m]["label"]], any_label).items():
        if m in meta_ and not meta_[m]["label"]:
            meta_[m]["label"] = label
    return memberships, meta_


def movement_guarantee(df, args):
    """Top-K members (holdings first) of every post-1945 art movement in the pool."""
    memberships, meta = fetch_movements(df.qid.tolist(), args.endpoint)
    birth = pd.to_numeric(df.birth.str[:4], errors="coerce")
    share = pd.to_numeric(df.art_occ_share, errors="coerce")
    holdings = sum(has(df, c).astype(int) for c in INDEPENDENT_IDS)
    members, via = collections.defaultdict(list), collections.defaultdict(set)
    for i, q in zip(df.index, df.qid):
        for m, prop in memberships.get(q, {}).items():
            members[m].append(i)
            via[m].add(prop)
    rows, guaranteed = [], collections.defaultdict(list)
    for m, idx in members.items():
        md = meta.get(m, {})
        classes = [MOVEMENT_TYPES[t] for t in md.get("types", []) if t in MOVEMENT_TYPES]
        sub = [MOVEMENT_TYPES[t] for t in md.get("parents", []) if t in MOVEMENT_TYPES]
        starts = [y for y in map(wikidata.year_of, md.get("start", [])) if y is not None]
        start = min(starts) if starts else None
        median_birth = birth[idx].median()
        reasons = []
        if m in UMBRELLA:
            reasons.append("umbrella term: " + UMBRELLA[m])
        if not classes and not sub:
            reasons.append("not an art movement/style/group class")
        bad = [NON_MOVEMENT[t] for t in md.get("types", []) if t in NON_MOVEMENT]
        if bad:
            reasons.append("organisation: " + ", ".join(bad))
        if ORG_WORDS.search(md.get("label") or ""):
            reasons.append("organisation (label)")
        if start is not None and start < args.movement_since:
            reasons.append(f"inception {start}")
        if start is None and not (median_birth >= args.movement_median_birth):
            reasons.append(f"undated, median birth {median_birth:.0f}" if median_birth == median_birth
                           else "undated, no member births")
        if via[m] == {"P463"} and len(idx) > MAX_ASSOCIATION:
            reasons.append(f"association (P463 only, {len(idx)} members)")
        if len(idx) < args.movement_min:
            reasons.append(f"<{args.movement_min} pool members")
        k = min(args.movement_max_k, max(args.movement_min_k, round(args.movement_share * len(idx))))
        rec = {"movement_qid": m, "movement": md.get("label") or m,
               "via": "|".join(sorted(via[m])), "classes": "|".join(dict.fromkeys(classes + [c + " (subclass)" for c in sub])),
               "inception": start, "median_birth": median_birth, "members": len(idx),
               "kept": int(not reasons), "excluded_because": "; ".join(reasons), "k": k, "member_idx": idx}
        if not reasons:
            cand = df.loc[idx]
            ok = share[idx].isna() | (share[idx] >= args.movement_min_share)
            cand = cand[ok.to_numpy()].assign(_h=holdings[idx][ok.to_numpy()])
            cand = cand.sort_values(["museum", "_h", "score"], ascending=False).head(k)
            for i in cand.index:
                guaranteed[i].append(rec["movement"])
            rec["eligible"] = int(ok.sum())
            rec["guaranteed_idx"] = list(cand.index)
        rows.append(rec)
    return pd.DataFrame(rows), guaranteed


def attention_route(df, args, guarded=True):
    share = pd.to_numeric(df.art_occ_share, errors="coerce")
    ok = (df.pv_pct >= args.attention_pct) & (df.pageviews > 0) & (share.isna() | (share >= args.attention_min_share))
    if not guarded:
        return ok
    # Guards added on review of the first run, where the plain rule let in mostly
    # celebrities with an art occupation (Frances Bean Cobain, Randy Johnson, Tommy
    # Hilfiger, royal spouses): their pageviews come from fame outside art.
    art_record = (df.market > 0) | (df.museum > 0) | sum(has(df, c) for c in INDEPENDENT_IDS).gt(0) | (df.lists > 0)
    ok &= art_record | share.isna() | (share >= args.attention_plain_share)
    excluded = set(filter(None, args.attention_exclude_media.split(",")))
    return ok & ~df.medium.isin(excluded)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--target", type=int, default=11000, help="total selected incl. auto-includes")
    ap.add_argument("--floor", type=float, default=0.25, help="min fraction selected in floor regions")
    ap.add_argument("--floor-regions", default=",".join(NON_WESTERN),
                    help="comma list of regions with the floor, or 'all'")
    ap.add_argument("--weights", default="", help="override weights, e.g. museum=0.3,market=0.15")
    ap.add_argument("--celeb-share", type=float, default=0.5, help="art_occ_share at which factor reaches 1")
    ap.add_argument("--allow-no-pageviews", action="store_true")
    ap.add_argument("--no-market-check", dest="market_check", action="store_false",
                    help="count market records even without an independent signal")
    ap.add_argument("--no-movements", dest="movements", action="store_false", help="skip the movement guarantee")
    ap.add_argument("--movement-since", type=int, default=1945, help="earliest movement inception")
    ap.add_argument("--movement-median-birth", type=float, default=1915,
                    help="undated movements: minimum median member birth year")
    ap.add_argument("--movement-min", type=int, default=3, help="minimum scored pool members per movement")
    ap.add_argument("--movement-share", type=float, default=0.15, help="share of members guaranteed")
    ap.add_argument("--movement-min-k", type=int, default=3)
    ap.add_argument("--movement-max-k", type=int, default=15)
    ap.add_argument("--movement-min-share", type=float, default=0.25,
                    help="minimum art_occ_share for a guaranteed member")
    ap.add_argument("--no-attention", dest="attention", action="store_false", help="skip the attention route")
    ap.add_argument("--attention-pct", type=float, default=0.98, help="within-region pageview percentile")
    ap.add_argument("--attention-min-share", type=float, default=0.5, help="minimum art_occ_share")
    ap.add_argument("--attention-plain-share", type=float, default=0.6,
                    help="art_occ_share needed when the artist has no art-world record (market, museum, "
                         "ULAN/Tate/MoMA ID or list); 0.5 turns this guard off")
    ap.add_argument("--attention-exclude-media", default="architecture,design and decorative arts",
                    help="primary media left out of the attention route (fashion designers, architect-"
                         "politicians); '' turns this guard off")
    ap.add_argument("--endpoint", choices=["wdqs", "qlever"], default="wdqs",
                    help="SPARQL endpoint for the P135 fetch (cached after the first run)")
    ap.add_argument("--max-total", type=int, default=13000,
                    help="warn when the total exceeds this (the outputs are still written)")
    ap.add_argument("--report", action="store_true", help="print top-20 overall and top-10 per non-Western region")
    args = ap.parse_args()
    args.weights = parse_weights(args.weights)
    args.endpoint = wikidata.QLEVER if args.endpoint == "qlever" else wikidata.SPARQL

    df, list_only, notes = load_inputs(args)
    for n in notes:
        print(n)
    print("weights: " + ", ".join(f"{k}={v:.3f}" for k, v in args.weights.items()))
    df = score(df, args.weights, args.celeb_share, args.market_check)
    if args.market_check:
        unv = (df.market_verified == 0) & (df.market > 0)
        print(f"market check: {int(unv.sum()):,} artists with market IDs but no independent signal "
              f"get market percentile 0")
    floor_regions = set(df.region) if args.floor_regions == "all" else set(args.floor_regions.split(","))
    Q, A, f = quotas(df, len(list_only), args.target, args.floor, floor_regions)
    cutoffs = select(df, Q, A)
    n_base = int(df.selected.sum()) + len(list_only)

    df["route_list"] = df.auto_include.str.startswith("lists:").astype(int)
    df["route_manual"] = df.auto_include.str.startswith("manual:").astype(int)
    df["route_regional_score"] = ((df.selected == 1) & (df.auto_include == "")).astype(int)
    df["route_movement_guarantee"] = 0
    df["guarantee_movements"] = ""
    mov = pd.DataFrame()
    if args.movements:
        print("\nmovement guarantee")
        mov, guaranteed = movement_guarantee(df, args)
        for i, ms in guaranteed.items():
            df.loc[i, "route_movement_guarantee"] = 1
            df.loc[i, "guarantee_movements"] = "|".join(sorted(ms))
    df["route_attention"] = attention_route(df, args).astype(int) if args.attention else 0
    if args.attention:
        plain = attention_route(df, args, guarded=False)
        print(f"attention route: {int(plain.sum()):,} artists pass the plain rule (top pageviews, art_occ_share "
              f">= {args.attention_min_share}); {int(df.route_attention.sum()):,} pass the guards")
    base = df.selected == 1
    df["selected"] = (base | (df.route_movement_guarantee == 1) | (df.route_attention == 1)).astype(int)
    if os.path.exists(MANUAL_EXCLUDES):
        # Reviewed false positives of the automatic routes (celebrities, non-artist collectives).
        drop = set(pd.read_csv(MANUAL_EXCLUDES, dtype=str, keep_default_na=False).qid)
        df.loc[df.qid.isin(drop) & ~df.auto_include.str.startswith("manual:"), "selected"] = 0
    routes = ["route_list", "route_regional_score", "route_movement_guarantee", "route_attention", "route_manual"]
    df["routes"] = df[routes].apply(lambda r: "|".join(c[6:] for c in routes if r[c]), axis=1)

    if len(mov):
        sel_base = set(df.index[base])
        mov["guaranteed"] = mov.pop("guaranteed_idx").map(lambda ix: ix if isinstance(ix, list) else [])
        mov["n_guaranteed"] = mov.guaranteed.map(len)
        mov["n_new"] = mov.guaranteed.map(lambda ix: sum(i not in sel_base for i in ix))
        mov["selected_before"] = mov.member_idx.map(lambda ix: sum(i in sel_base for i in ix))
        mov["selected_after"] = mov.member_idx.map(lambda ix: int(df.selected[ix].sum()))
        mov = mov.drop(columns=["member_idx"])
        mov["new_members"] = mov.guaranteed.map(
            lambda ix: "; ".join(df.label[i] or df.qid[i] for i in ix if i not in sel_base))
        mov["guaranteed_members"] = mov.guaranteed.map(lambda ix: "; ".join(df.label[i] or df.qid[i] for i in ix))
        mov = mov.drop(columns=["guaranteed"])
        mov = mov.sort_values(["kept", "members"], ascending=False)
        mov["median_birth"] = mov.median_birth.round(0)
        mov.to_csv(MOVEMENTS_OUT, index=False)

    df["key"] = df.qid
    df["label"] = df.label.fillna("")
    cols = ["key", "qid", "label", "region", "medium", "score", "region_percentile", "celebrity_factor",
            "auto_include", "selected", "routes"] + routes + ["guarantee_movements", "market_verified", "pv_pct",
            "source"] + list(signals(df.head(0)).columns)
    if len(list_only):
        list_only = list_only.assign(route_list=1, routes="list")
    out = pd.concat([df, list_only], ignore_index=True)[cols] if len(list_only) else df[cols]
    for c in routes + ["market_verified"]:
        out[c] = out[c].fillna(0).astype(int)
    out["routes"] = out.routes.fillna("")
    out["guarantee_movements"] = out.guarantee_movements.fillna("")
    out["pv_pct"] = out.pv_pct.round(5)
    out = out.sort_values(["selected", "score"], ascending=False, na_position="last")
    out["score"] = out.score.round(5)
    out["region_percentile"] = out.region_percentile.round(5)
    out.to_csv(OUT, index=False)

    print(f"\nselection fraction f = {f:.4f} (floor {args.floor:.0%} in {len(floor_regions)} regions)")
    base_sel = df.route_list | df.route_manual | df.route_regional_score
    mov_new = (df.route_movement_guarantee == 1) & (base_sel == 0)
    att_new = (df.route_attention == 1) & (base_sel == 0) & ~mov_new
    print(f"\n{'region':30} {'pool':>7} {'auto':>6} {'picked':>7} {'+mov':>5} {'+attn':>5} {'selected':>8} "
          f"{'sel%':>6} {'cutoff':>7} {'cut pct':>7}")
    lo_by_region = list_only.region.value_counts() if len(list_only) else pd.Series(dtype=int)
    for r in sorted(Q.index, key=lambda r: -Q[r]):
        m = df.region == r
        sel = int(df[m].selected.sum())
        sc, pc = cutoffs[r]
        print(f"{r:30} {int(m.sum()):>7} {int(A[r]):>6} {int(df[m].route_regional_score.sum()):>7} "
              f"{int(mov_new[m].sum()):>5} {int(att_new[m].sum()):>5} {sel:>8} "
              f"{sel / m.sum():>6.1%} {sc:>7.3f} {pc:>7.3f}"
              + (f"  (+{lo_by_region[r]} list-only)" if r in lo_by_region else ""))
    print(f"\n{'medium':42} {'pool':>7} {'selected':>8}")
    for m, g in df.groupby("medium"):
        print(f"{m:42} {len(g):>7} {int(g.selected.sum()):>8}")
    if len(list_only):
        print(f"{'(list-only, no medium)':42} {'':>7} {len(list_only):>8}")
    n_auto = int((df.auto_include != "").sum()) + len(list_only)
    total = int(out.selected.sum())
    print(f"\nauto-includes {n_auto:,} + regional picks {n_base - n_auto:,} = {n_base:,} (--target)")
    if len(mov):
        k = mov[mov.kept == 1]
        print(f"movement guarantee: {len(k):,} movements kept of {len(mov):,}; "
              f"{int(df.route_movement_guarantee.sum()):,} artists guaranteed, {int(mov_new.sum()):,} not otherwise selected")
    print(f"attention route: {int(df.route_attention.sum()):,} artists qualify, {int(att_new.sum()):,} not otherwise selected")
    print(f"TOTAL selected {total:,}\nwrote {OUT}" + (f" and {MOVEMENTS_OUT}" if len(mov) else ""))
    if total > args.max_total:
        print(f"WARNING: total {total:,} exceeds --max-total {args.max_total:,}: review the route composition")

    if args.report:
        df["name"] = df.label.where(df.label != "", df.qid).str.slice(0, 32)
        df["lists_"] = df.auto_include.str.slice(6, 46)
        show = ["name", "region", "medium", "score", "lists_"]
        print("\nTop 20 overall\n" + df.sort_values("score", ascending=False).head(20)[show].to_string(index=False))
        top = df[df.auto_include == ""].sort_values("score", ascending=False)
        print("\nTop 20 overall, not on a list\n" + top.head(20)[show[:4]].to_string(index=False))
        for r in ["Sub-Saharan Africa", "Middle East and North Africa", "South Asia", "Southeast Asia",
                  "East Asia", "Latin America and Caribbean"]:
            sub = df[df.region == r].sort_values("score", ascending=False)
            print(f"\nTop 10 {r}\n" + sub.head(10)[["name", "medium", "score", "lists_"]].to_string(index=False))
            print(f"  top 10 not on a list: " + "; ".join(top[top.region == r].head(10).name))


if __name__ == "__main__":
    main()
