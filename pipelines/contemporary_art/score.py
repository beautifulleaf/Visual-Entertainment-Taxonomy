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
  Architects stay in as gathered (§3.1b); whether they stay artists is decided in
  the classifying stage.

Inputs : data/interim/contemporary_pool.csv, contemporary_pageviews.csv,
         contemporary_list_artists.csv and contemporary_pool_additions.csv (optional)
Output : data/interim/contemporary_scores.csv
Usage  : python3 pipelines/contemporary_art/score.py [--target 11000] [--floor 0.25]
             [--weights museum=0.3,market=0.15] [--celeb-share 0.5] [--report]
"""
import argparse
import math
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INTERIM = os.path.join(ROOT, "data", "interim")
POOL = os.path.join(INTERIM, "contemporary_pool.csv")
VIEWS = os.path.join(INTERIM, "contemporary_pageviews.csv")
LIST_ARTISTS = os.path.join(INTERIM, "contemporary_list_artists.csv")
ADDITIONS = os.path.join(INTERIM, "contemporary_pool_additions.csv")
OUT = os.path.join(INTERIM, "contemporary_scores.csv")

WEIGHTS = {"lists": 0.20, "museum": 0.25, "ulan": 0.05, "market": 0.20,
           "pageviews": 0.10, "sitelinks": 0.10, "awards": 0.10}
MARKET_IDS = ["artnet_id", "artsy_id", "artprice_id", "mutualart_id"]
NON_WESTERN = ["Sub-Saharan Africa", "Middle East and North Africa", "South Asia", "Southeast Asia",
               "East Asia", "Latin America and Caribbean", "Central Asia", "Asia (other)"]
UNKNOWN = "Unknown"


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
    out["lists"] = num(df.get("n_list_entries", df.get("n_lists", 0)), df.index)
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
        add["source"] = "addition"
        for q, l in zip(add.qid, add.get("lists", pd.Series("", add.index))):
            auto_reason.setdefault(q, f"lists:{l}" if l else "lists:resolved")
        rows.append(add)
        notes.append(f"pool additions: {len(add):,} resolved list artists outside the pool")
    else:
        notes.append(f"{os.path.basename(ADDITIONS)} not found: no resolved list artists outside the pool")
    df = pd.concat(rows, ignore_index=True)
    df["region"] = df.region.replace("", UNKNOWN).fillna(UNKNOWN)
    df["auto_include"] = df.qid.map(auto_reason).fillna("")
    return df, list_only, notes


def score(df, weights, celeb_share):
    sig = signals(df)
    region = df.region.to_numpy()
    comp = np.zeros(len(df))
    for k, w in weights.items():
        df[f"pct_{k}"] = midrank_pct(sig[k].to_numpy(), region)
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


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--target", type=int, default=11000, help="total selected incl. auto-includes")
    ap.add_argument("--floor", type=float, default=0.25, help="min fraction selected in floor regions")
    ap.add_argument("--floor-regions", default=",".join(NON_WESTERN),
                    help="comma list of regions with the floor, or 'all'")
    ap.add_argument("--weights", default="", help="override weights, e.g. museum=0.3,market=0.15")
    ap.add_argument("--celeb-share", type=float, default=0.5, help="art_occ_share at which factor reaches 1")
    ap.add_argument("--allow-no-pageviews", action="store_true")
    ap.add_argument("--report", action="store_true", help="print top-20 overall and top-10 per non-Western region")
    args = ap.parse_args()
    args.weights = parse_weights(args.weights)

    df, list_only, notes = load_inputs(args)
    for n in notes:
        print(n)
    print("weights: " + ", ".join(f"{k}={v:.3f}" for k, v in args.weights.items()))
    df = score(df, args.weights, args.celeb_share)
    floor_regions = set(df.region) if args.floor_regions == "all" else set(args.floor_regions.split(","))
    Q, A, f = quotas(df, len(list_only), args.target, args.floor, floor_regions)
    cutoffs = select(df, Q, A)

    df["key"] = df.qid
    df["label"] = df.label.fillna("")
    cols = ["key", "qid", "label", "region", "medium", "score", "region_percentile", "celebrity_factor",
            "auto_include", "selected", "source"] + list(signals(df.head(0)).columns)
    out = pd.concat([df, list_only], ignore_index=True)[cols] if len(list_only) else df[cols]
    out = out.sort_values(["selected", "score"], ascending=False, na_position="last")
    out["score"] = out.score.round(5)
    out["region_percentile"] = out.region_percentile.round(5)
    out.to_csv(OUT, index=False)

    print(f"\nselection fraction f = {f:.4f} (floor {args.floor:.0%} in {len(floor_regions)} regions)")
    print(f"\n{'region':30} {'pool':>7} {'auto':>6} {'picked':>7} {'selected':>8} {'sel%':>6} {'cutoff':>7} {'cut pct':>7}")
    lo_by_region = list_only.region.value_counts() if len(list_only) else pd.Series(dtype=int)
    for r in sorted(Q.index, key=lambda r: -Q[r]):
        sel = int(df[df.region == r].selected.sum())
        sc, pc = cutoffs[r]
        print(f"{r:30} {int((df.region == r).sum()):>7} {int(A[r]):>6} {sel - int(A[r]):>7} {sel:>8} "
              f"{sel / (df.region == r).sum():>6.1%} {sc:>7.3f} {pc:>7.3f}"
              + (f"  (+{lo_by_region[r]} list-only)" if r in lo_by_region else ""))
    print(f"\n{'medium':42} {'pool':>7} {'selected':>8}")
    for m, g in df.groupby("medium"):
        print(f"{m:42} {len(g):>7} {int(g.selected.sum()):>8}")
    if len(list_only):
        print(f"{'(list-only, no medium)':42} {'':>7} {len(list_only):>8}")
    n_auto = int((df.auto_include != "").sum()) + len(list_only)
    print(f"\nTOTAL selected {int(out.selected.sum()):,}  (auto-includes {n_auto:,}, "
          f"regional picks {int(out.selected.sum()) - n_auto:,})\nwrote {OUT}")

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
