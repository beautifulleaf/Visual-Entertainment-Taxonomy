"""Report tab of the first full release: census, audits, owner rulings needed, open items.

Reads the audit files in taxonomy/audit/ (blind tests, coverage probes, seams) so the numbers on the page
are the numbers in the repository.
"""
import csv
import json
import os
from collections import Counter

A = os.path.join(os.path.dirname(__file__), "..", "..", "taxonomy", "audit")


def _rd(name):
    p = os.path.join(A, name)
    return list(csv.DictReader(open(p, encoding="utf-8"))) if os.path.exists(p) else []


def _blind(prefix, keyname="leaf"):
    kp = os.path.join(A, f"{prefix}_key.json")
    if not os.path.exists(kp):
        return None
    key = json.load(open(kp))
    rat = {r["item_id"]: r for r in _rd(f"{prefix}_rater.csv")}
    items = {r["item_id"]: r for r in _rd(f"{prefix}.csv")}
    ok, n = Counter(), Counter()
    for i, _, want in key:
        r = rat.get(str(i))
        if not r:
            continue
        tab = items.get(str(i), {}).get("tab") or items.get(str(i), {}).get("kind", "all")
        got = (r.get(keyname) or r.get("disposition") or "").strip()
        n[tab] += 1
        c = lambda d: (d.partition(":")[2] if d.split(":")[0] in ("leaf", "kind", "alias") else d).split("/")[0].strip()
        ok[tab] += c(got) == c(want)
    return ok, n


def _fmt(b):
    if not b:
        return "not run"
    ok, n = b
    parts = ", ".join(f"{t} {ok[t]}/{n[t]}" for t in n)
    return f"<b>{sum(ok.values())} of {sum(n.values())}</b> ({parts})"


def _probes(name):
    rows = _rd(name)
    c = Counter(r["status"].strip().lower() for r in rows)
    return rows, c


def build(census):
    va, ft = census["va"], census["ft"]
    b1, b2 = _blind("blind_ft"), _blind("blind2_ft")
    bv1, bv2 = _blind("blind_va", "disposition"), _blind("blind2_va", "disposition")
    pf, cf = _probes("coverage_probes_ft.csv")
    pv, cv = _probes("coverage_probes_va.csv")
    seams = json.load(open(os.path.join(A, "seams_ft.json"))) if os.path.exists(os.path.join(A, "seams_ft.json")) else {}
    seam_rows = "".join(f"<tr><td>{t}</td><td>{a} {la} / {b} {lb}</td><td class='num'>{k}</td></tr>"
                        for t, v in seams.items() for a, la, b, lb, k in v["pairs"][:4])
    fd = ft["dispositions"]
    fam = ft["per_family"]
    weak_probes = "".join(f"<li>{r['set']}: <i>{r['probe']}</i> — {r['status']}; {r['comment']}</li>"
                          for r in pf + pv if r["status"].strip().lower() != "ok")
    return f"""
<h2 id="r-summary">What this release holds</h2>
<p>This is the first full release of both tabs, built from the pilot's method after your rulings D1–D8 and the accepted F11–F12. Codes are provisional; they freeze at the first frozen release.</p>
<table><thead><tr><th>Tab</th><th>Leaves</th><th>Placed</th><th>Notes</th></tr></thead><tbody>
<tr><td>Visual Art</td><td class="num">{va['leaves']:,}</td><td class="num">{va['kinds']:,} kinds</td><td>{va['families_built']} of 13 families built; region slices for South Asia, the Himalaya and Central Asia, Southeast Asia, East Asia, Africa, the ancient world, Mesoamerica and South America, Indigenous North America, Oceania and Australia, Europe and European folk (west and east), architecture, plus 31,551 artists under schools, movements and period styles.</td></tr>
<tr><td>Film &amp; Television</td><td class="num">{ft['leaves']}</td><td class="num">{ft['placed']:,} titles</td><td>Feature films {fam.get('A', 0):,} · shorts {fam.get('B', 0):,} · television series {fam.get('C', 0):,} · serial traditions {fam.get('D', 0):,} · anime {fam.get('E', 0):,} · unscripted formats {fam.get('G', 0):,}.</td></tr>
</tbody></table>
<p>Every gathered row has one disposition. Film routes and exclusions: {sum(v for k, v in fd.items() if k.endswith('|route')):,} routed between families (mostly Japanese animation in the film list → Anime, and anime found in the TV list), {sum(v for k, v in fd.items() if k.endswith('|exclude')):,} excluded with a reason (TV specials, compilations, recaps, duplicates and supplements).</p>

<h2 id="r-method">How it was built</h2>
<ol>
<li><b>Leaves first.</b> Global feature-film leaves (movements, genres, cycles, popular modes), the anime leaves by D4, the television leaves with the Asian drama traditions in C2 by D3, the serial traditions, and the unscripted formats; Visual Art leaves region by region from the gathered pool (tradition-led) and from the artists' attested movements and period styles (artist-led).</li>
<li><b>Rules propose, reviewers decide.</b> Each title got a rule proposal from its TMDB keywords, overview and Wikidata genre; fresh reviewers then placed batches of about 220 against the leaf list and the precedence sentences (82 film batches, 32 television, 23 Asian drama, 26 anime, 2 unscripted). Recurring seams became new leaves and sentences (F13–F31, AN1–AN11, TV1–TV20, P11–P13), and sweeps re-placed earlier batches when a leaf arrived late.</li>
<li><b>Hand corrections</b> live in <code>seeds/classify/*_overrides.csv</code>; sweeps in <code>taxonomy/*/review/sweep_*.csv</code>.</li>
</ol>

<h2 id="r-audits">Audits</h2>
<h3>Blind placement test</h3>
<p>A fresh rater saw only the keys and the leaf definitions and placed a held-out sample drawn from every family. <b>Film &amp; Television</b>, round 1: {_fmt(b1)}; after the fixes, on a new sample, round 2: {_fmt(b2)}. <b>Visual Art</b>, round 1: {_fmt(bv1)}; round 2: {_fmt(bv2)}.</p>
<p>The film misses sit on the seams the reviewers also reported: a general's biopic against War Film, comic police films, a period setting that does or does not "define" a family drama, Asian anime comedies against gag anime, and supplements (manner movies, behind-the-scenes cuts). Fixes made: F30, F31, AN11, TV20, Hood Film widened beyond the United States, and overrides for the items where the rater was right.</p>
<h3>Seam audit</h3>
<p>Leaf pairs that most often appear as primary and see-also:</p>
<table><thead><tr><th>List</th><th>Pair</th><th>Rows</th></tr></thead><tbody>{seam_rows}</tbody></table>
<p>These are expected neighbours (comedy-drama against romantic comedy; coming-of-age against romantic drama; Japanese television drama against teen drama). Each pair is settled by a precedence sentence: F9, F22, F24, TV3, TV17, AN7.</p>
<h3>Coverage probes</h3>
<p>A second rater wrote probes from memory before reading the leaves: core terms a serious reference must cover and naive phrasings ("scary movie", "Turkish soap", "Persian rug"). <b>Film &amp; Television: {cf.get('ok', 0)} of {len(pf)} found a clear home</b>, {cf.get('weak', 0)} only a weak one, {cf.get('missing', 0)} none. <b>Visual Art: {cv.get('ok', 0)} of {len(pv)}</b> clear, {cv.get('weak', 0)} weak, {cv.get('missing', 0)} missing. Fixes made from the misses: aliases for naive phrasings, a Hidden Camera &amp; Prank Show leaf, country of origin stated as a filter on every leaf, critical tags (prestige, cult) as tags.</p>
<details class="key"><summary>Probes that are weak or missing</summary><ul>{weak_probes}</ul></details>
<h3>Census</h3>
<p>Film &amp; Television leaves with no title in this release: {', '.join(ft['empty_leaves']) or 'none'} (Pink Film and Roman Porno: the selection has no pink-circuit or Nikkatsu titles; Korean New Wave: its one candidate keeps its neo-noir leaf and carries the movement tag). Visual Art leaves with no kind yet: {len(va['empty_leaves'])} — attested traditions whose sub-types and makers are not in the gathered evidence. Leaves whose attestation is still weak carry a yellow note on their card: {len(va['weak'])} in Visual Art, {len(ft['weak'])} in Film &amp; Television.</p>

<h2 id="r-rulings">Rulings needed</h2>
<div class="q"><b class="id">R1</b> <b>New Hollywood against genre cycles.</b> Under D1 a genre cycle beats a movement. Is the Hollywood blockbuster or horror classic of an attested New Hollywood director (<i>Jaws</i>, <i>The Exorcist</i>) a cycle member or a movement member? The release keeps the genre leaf and tags the movement.</div>
<div class="q"><b class="id">R2</b> <b>The inclusion rule and European folk art.</b> Dala horse, rosemaling, Quimper faience, santons, Erzgebirge carving, Fair Isle and others fall below §2.3 (fewer than 50 objects in the gathered evidence) and have no leaf; the list is in <code>taxonomy/visual_art/review/gapsweep_europe_below_rule.csv</code>. An exception for attested folk traditions, or leave them out?</div>
<div class="q"><b class="id">R3</b> <b>Medieval illumination.</b> Western illumination sits in Book Arts (C2) and partly in the artist cells (Gothic Book Illustration, Ghent-Bruges); Byzantine and Armenian illumination sit in Painting (A1) by P1. One home for medieval illumination?</div>
<div class="q"><b class="id">R4</b> <b>North American settler folk art</b> (Amish quilts, fraktur, decoys, weathervanes, hooked rugs, tramp art) was built in the Europe slice because the pool filed it there. Keep it with European folk, or a North American folk sub-family?</div>
<div class="q"><b class="id">R5</b> <b>Intangible-heritage rows with no objects.</b> Kept as leaves where they name a craft (telepuk, tekat, Daluang), excluded where they name garments, mats or performances. Confirm the line.</div>
<div class="q"><b class="id">R6</b> <b>Artist fallbacks.</b> 26,555 artists are placed by a medium × region × birth-period rule; Modern Art (8,065) and Contemporary Art (3,394) are the largest leaves. Accept period-style leaves as the home for artists with no attested movement, or split modern and contemporary art further (by country or medium)?</div>
<div class="q"><b class="id">R7</b> <b>Movement against medium.</b> About 190 artists of conceptual, Fluxus, mail art, minimal and kinetic movements are placed under their movement (installation, new media, sculpture) rather than their recorded medium. Confirm.</div>
<div class="q"><b class="id">R8</b> <b>Scope edges.</b> Fashion designers (Possession taxonomy?), comics (manga, ligne claire: a comics tab?), filmed stage productions (placed by stage genre, F28), vertical micro-dramas (a leaf, C1-17), BL and GL as one leaf (C2-11).</div>
<div class="q"><b class="id">R9</b> <b>Animated television specials over 40 minutes</b> (<i>Rudolph the Red-Nosed Reindeer</i>, 47 min) stay in Animated Feature; the special leaf (B1-5) takes 40 minutes or less. Keep the 40-minute line for specials?</div>
<div class="q"><b class="id">R10</b> <b>Weak attestations.</b> The yellow notes on the leaf cards list labels resting on a museum page, a blog or a broader article. Accept them for this release, or hold those leaves until a better source is found?</div>

<h2 id="r-open">Your open items</h2>
<ul>
<li><b>Black Rain</b> (Imamura, 1989) is added to the film selection and placed in Atomic Bomb Film. The Japan 1980s top-up took films that were all above the main bar, so it added nothing below it; other near misses there: <i>Godzilla 1985</i>, <i>Sweet Home</i>, <i>Mermaid Legend</i>.</li>
<li><b>Difret</b> was fourth in its Ethiopia 2010s cell (the top-up takes three after <i>Lamb</i>); added by hand.</li>
<li><b>Japanese animated films</b>: matched to the anime list through MAL synonyms and Wikidata MAL IDs; 12 remain unmatched, 5 turned out to be live action and are placed as films.</li>
<li><b>Aboriginal artists</b> are attached to Western Desert Painting (art centres as kinds), Bark Painting, the Hermannsburg School and Contemporary Indigenous Australian Art.</li>
<li><b>Kyunki Saas Bhi Kabhi Bahu Thi</b> was not in the TV selection (2,269 IMDb votes, below the 2,500 bar). It is the defining saas-bahu serial and the example of Indian Daily Soap (D4-1), so it is added by hand and placed there.</li>
<li><b>Korean anime</b>: the country top-up now includes South Korea (+9 titles, <i>Pucca</i> among them).</li>
<li><b>Licensing</b>: audience counts stay in the repository; the page carries titles, years, makers, IDs and notes only.</li>
</ul>

<h2 id="r-next">Next</h2>
<ol>
<li>Your rulings R1–R10, then the sweeps they imply.</li>
<li>Kinds for the Visual Art leaves that have none (sub-types and makers from the object records).</li>
<li>A second artist pass for the low-confidence period placements, by country and medium.</li>
<li>The frozen release: codes fixed, append-only from then on.</li>
</ol>
"""
