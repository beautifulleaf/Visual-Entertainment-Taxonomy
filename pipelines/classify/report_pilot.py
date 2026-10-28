"""Pilot report (HTML fragment for the page's Pilot report tab).

Numbers are read from the census and audit files at build time; the prose
records the decisions and findings of the pilot (2026-10-28).
"""
import csv
import json
import os
from collections import Counter

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
P = os.path.join(ROOT, "taxonomy", "pilot")
R = os.path.join(P, "review")


def _blind():
    def lc(d):
        t, _, r = d.partition(":")
        return t, r.split("/")[0].strip()
    va = json.load(open(os.path.join(R, "blind_va_key.json")))
    vr = {r["item_id"]: r["disposition"] for r in csv.DictReader(open(os.path.join(R, "blind_va_rater.csv")))}
    va_ok = sum(1 for i, _, d in va if lc(d) == lc(vr[str(i)]))
    ft = json.load(open(os.path.join(R, "blind_ft_key.json")))
    fr = {r["item_id"]: r["leaf"].strip() for r in csv.DictReader(open(os.path.join(R, "blind_ft_rater.csv")))}
    ft_ok = sum(1 for i, _, l in ft if fr[str(i)] == l)
    return va_ok, len(va), ft_ok, len(ft)


def _probes():
    rows = list(csv.DictReader(open(os.path.join(R, "coverage_probes.csv"))))
    c = Counter((r["set"][:1].upper(), r["status"].strip().lower()) for r in rows)
    return rows, c


def build(census):
    va, ft = census["va"], census["ft"]
    vok, vn, fok, fn = _blind()
    probes, pc = _probes()
    nprobe = len(probes)
    ok = sum(v for (s, st), v in pc.items() if st == "ok")
    d = va["dispositions"]
    src = va["by_source"]
    rows = "".join(
        f"<tr><td>{k}</td>" + "".join(f'<td class="num">{v.get(x, 0)}</td>' for x in ("leaf", "kind", "alias", "tag", "route", "exclude")) + "</tr>"
        for k, v in sorted(src.items(), key=lambda kv: -sum(kv[1].values())))
    per = ft["per_leaf"]
    nempty_ft = [k for k, v in per.items() if v == 0]
    return f"""
<h2 id="r-summary">What the pilot built</h2>
<p>Two slices, each placed end to end with the keys, then audited. Codes are provisional until the first full release.</p>
<table><thead><tr><th>Slice</th><th>Candidates</th><th>Leaves</th><th>Placed as nodes</th><th>Outcome</th></tr></thead><tbody>
<tr><td>Visual Art · Islamic world (tradition-led)</td><td class="num">{va['rows']:,}</td><td class="num">{va['leaves']}</td><td class="num">{d.get('leaf',0) + d.get('kind',0):,}</td><td>{d.get('kind',0)} kinds, {d.get('leaf',0)} rows that are leaves, {d.get('alias',0)} aliases, {d.get('tag',0)} period/place tags, {d.get('route',0)} routed, {d.get('exclude',0)} excluded with a reason</td></tr>
<tr><td>Film &amp; Television · Japanese cinema</td><td class="num">{ft['rows']}</td><td class="num">{ft['leaves']}</td><td class="num">{ft['rows'] - 305:,}</td><td>live-action features placed in genre, cycle and movement leaves; 301 animated films routed to Anime, 4 shorts to Short Film; 0 unplaced</td></tr>
</tbody></table>
<p><b>Gap closed on the way:</b> MDBList returns TMDB keywords (append <code>keyword</code>) and the TMDB plot overview in its batch endpoint. They are now fetched for every selected film (18,268 of 18,365 have keywords) and scripted series (6,870 of 7,134), with Wikidata genre, director and movement facts for the pilot titles. The Wikipedia API stays rate-limited from this machine; it was not needed.</p>

<h2 id="r-decisions">Rulings needed from you</h2>
<div class="q"><b class="id">Q1</b> <b>Movement or genre first (film).</b> The key puts a film in a movement leaf before its genre (F1), with membership attested by the movement's reference list. Wikipedia's Japanese New Wave list is broad, so 27 films went to the New Wave leaf, among them <i>Harakiri</i>, <i>Kwaidan</i>, <i>Onibaba</i>, <i>Tokyo Drifter</i>, <i>Branded to Kill</i> and <i>Pale Flower</i> — the classics of chanbara, kaidan and yakuza noir. <b>Recommendation:</b> a named genre cycle wins over a movement (chanbara, kaidan, yakuza, pink film), the movement leaf keeps the films with no strong genre home (<i>Cruel Story of Youth</i>, <i>Death by Hanging</i>, <i>The Insect Woman</i>), and movement membership shows as a tag on every member. The blind rater split the same way on <i>Branded to Kill</i> and <i>Gate of Flesh</i>.</div>
<div class="q"><b class="id">Q2</b> <b>Dynasties and places are filters, not nodes.</b> All 53 dynasties, 43 production centres and 86 Met culture/period labels became period or place tags (P6, P7); the nodes are the traditions in each medium (Mamluk enamelled glass, Mamluk metalwork, Mamluk carpet, Mamluk architecture). A period filter then shows everything Mamluk. Confirm, or ask for dynasty sub-families inside the medium families.</div>
<div class="q"><b class="id">Q3</b> <b>Asian Drama as a family</b> is a regional division, which the conventions otherwise forbid. Keep it (your decision 2), or fold it into Television Series with its named traditions as leaves (K-drama melodrama, Chinese costume drama, asadora, taiga drama)?</div>
<div class="q"><b class="id">Q4</b> <b>Anime sub-families.</b> The plan splits anime by format (TV, film, OVA). That would repeat every genre leaf three times. <b>Recommendation:</b> genre and demographic sub-families (mecha, magical girl, iyashikei, isekai, shōnen battle …) with format as a filter. The 301 Japanese animated films wait in the Anime family for that build.</div>
<div class="q"><b class="id">Q5</b> <b>Painting sub-families by format.</b> Painting divides into manuscript &amp; album, East Asian ink, icon, cloth &amp; scroll, easel, and folk painting, so the Persian, Mughal, Ottoman and Deccan traditions meet in one sub-family with Rajput and Pahari to come. The precedence P1 sends pictures in manuscripts to painting and the book itself (script, illumination, binding) to Book Arts. Confirm the format axis, or prefer tradition sub-families (Islamic painting, Indian painting).</div>
<div class="q"><b class="id">Q6</b> <b>Ornament.</b> Girih, arabesque and muqarnas have no leaf: the probes asked for them. They are proposed as an ornament tag that runs across media rather than a family. Confirm.</div>
<div class="q"><b class="id">Q7</b> <b>Leaf granularity for folk and ware traditions.</b> Each named tradition is its own leaf (Suzani, Kubachi Ware, Tiraz), as in your Khokhloma example. {len(va['empty_leaves'])} of {va['leaves']} Visual Art leaves have no kinds yet, because the sweeps record the tradition but not its sub-types or makers. Kinds for them come next from the object records (centres, phases, sub-types: the Iznik phases, the Kufic forms). The alternative — technique-group leaves with the traditions as kinds — would halve the leaf count but bury named traditions one level down.</div>
<div class="q"><b class="id">Q8</b> <b>Country of origin.</b> 14 films in the Japanese view are foreign films with a Japanese co-producer (<i>Super Mario Bros.</i>, <i>Memoirs of a Geisha</i>, <i>The Dead Don't Die</i>). Country is only a filter, so they sit in their genre leaves either way. Keep Wikidata P495 as the country rule, or require the main production company to be Japanese for the Japan filter?</div>

<h2 id="r-audits">Audits</h2>
<h3>Blind placement test</h3>
<p>A fresh rater saw only the keys and leaf definitions. <b>Visual Art: {vok} of {vn}</b> held-out items got the same home. <b>Film: {fok} of {fn}</b> films got the same leaf. What it showed and what changed:</p>
<ul>
<li>Five Visual Art misses were one naming fault: school kinds carried the sweep's "dynasty + city" labels (Timurid Herat), which the rater took for tags. They now carry the field's names (Herat school, Qazvin school, Baghdad school, Inju school).</li>
<li>Makers active in two media (illuminator or painter, saz designer or painter) and credit lines naming a scribe and an illuminator split between C1, C2 and A1. Rule P9 (most recorded work wins) stands; the credit-line rows need a parser that splits the names.</li>
<li>Film misses sat on four seams: body horror vs cyberpunk (<i>Tetsuo II</i>), manga action vs chanbara (<i>Rurouni Kenshin</i>), psychological horror vs character study (<i>Kotoko</i>, <i>Helter Skelter</i>), crime vs comedy (<i>Why Don't You Play in Hell?</i>), plus Q1.</li>
</ul>
<h3>Seam audit</h3>
<p>Leaf pairs that most often appear as primary and see-also in the film placements: Social Drama / Character Study (8), Coming-of-Age / Romantic Drama (8), Crime Drama / Psychological Thriller (6), Shomingeki / Family Drama (5), Jidaigeki / Social Drama (5), Superhero &amp; Manga Action / Chanbara (5). Fixes made: F9 (a fantastical device that only frames a love or youth story does not make it fantasy), F10 (the key wins over a leaf's own examples), key step 3 now covers art-house erotic dramas, and Historical Drama now takes fictional Meiji–Shōwa stories.</p>
<h3>Coverage probes</h3>
<p>A second rater wrote {nprobe} probes from memory before reading the leaves — core terms a reference must cover and naive phrasings ("Persian rug", "samurai movie"). <b>{ok} found a good home.</b> Added from the misses: Javanese Mosque Architecture, Taiyōzoku Film, Atomic Bomb Film; ornament, setting (jidaigeki/gendaigeki) and release format (V-cinema) became tags. Added from the placement review before that: Persian Metalwork, Islamic Woodwork, ʿAjami, Edirnekâri, Qallaline Tiles, Al-Qatt Al-Asiri, Indo-Saracenic Architecture, Slasher Film, Psychological Horror, Pinky Violence, Animal Film and a Western sub-family.</p>
<p><b>Gathering gap found by the probes:</b> Imamura's <i>Black Rain</i> (1989; 7,233 Letterboxd ratings) is not in the film selection: the 5% top-up for Japan in the 1980s did not reach it. The atomic-bomb leaf is empty for that reason. Japanese 1980s films need a second look in the film top-up.</p>
<h3>Census by source (Visual Art)</h3>
<div class="tw"><table><thead><tr><th>Source</th><th>Leaf</th><th>Kind</th><th>Alias</th><th>Tag</th><th>Route</th><th>Exclude</th></tr></thead><tbody>{rows}</tbody></table></div>
<p>Exclusions carry their reason in <code>taxonomy/pilot/islamic_placements.csv</code>. The largest groups: 82 zero-sitelink "… architecture style" bulk items, 19 garment types (P10), 12 Wikidata-only folk items below the inclusion rule, and catalogue noise among the makers (authors such as Nizami and Jami, publishers, photographers' firms, placeholders such as "Tara 1"). Routed rows go where they belong when that family or slice is built: 73 modern and contemporary makers, 27 photographers, about 60 European artists and firms, 7 Islamic makers with no leaf yet (Zirid and Maghribi metalwork, Omani crafts, Algerian woodwork, Qajar enamel).</p>
<p>Film leaves with no Japanese film yet ({len(nempty_ft)}): {', '.join(nempty_ft)}. They are needed for the full tab.</p>
<h3>Attestation</h3>
<p>Every leaf shows its source on its card: a Wikidata item (QID, sitelinks) and its Wikipedia article where one exists, otherwise a museum or encyclopedia page found by targeted search. Labels were renamed to the attested form where the search found one (Veneto-Saracenic, Kütahya Ceramics, Damascus Tiles, Moʿaraq, Rishton). Leaves whose name is still weakly attested in English carry a yellow note: Fez Pottery, Ottoman Mother-of-Pearl Inlay, Persian Metalwork, Islamic Woodwork, Edirnekâri, Javanese Mosque Architecture. Six false Wikidata matches were caught and blocked (Illumination → a film company, Kashi → an ancient kingdom).</p>

<h2 id="r-method">How the placements were made</h2>
<ul>
<li><b>Rules first.</b> Tradition labels from the sweeps were mapped by hand to leaves, kinds, aliases or tags (<code>pipelines/classify/pilot_islamic.py</code>); 845 of 1,357 rows were placed this way.</li>
<li><b>Makers reviewed one by one.</b> All 668 named makers were reviewed in three batches against the leaf list: spelling variants merged (Basavana → Basawan), regex errors corrected (Bihzad and the Timurid calligraphers had been filed under the Mughal atelier), and non-makers excluded. Kalan/Khord pairs stay separate painters.</li>
<li><b>Films placed with features.</b> Each Japanese film was placed by running the key with its TMDB keywords, overview, Wikidata genre and director, and the film's own history; New Wave membership needed the reference list.</li>
<li><b>Everything is reproducible:</b> <code>python3 pipelines/classify/build_pilot.py</code> merges the rules, the reviewed files in <code>taxonomy/pilot/review/</code> and the overrides in <code>seeds/classify/</code>, and writes the placements, the census and this page's data.</li>
</ul>

<h2 id="r-open">Open items from the brief</h2>
<ul>
<li><b>Aboriginal artists</b> (ethnic group P172 or art-centre links), <b>Kyunki Saas Bhi Kabhi Bahu Thi</b> and the long-running-serial node, <b>Korean anime</b> top-up, <b>Difret</b>: outside the two pilot slices; they are scheduled with the Oceania, serial-drama, anime and African-film builds.</li>
<li><b>Known noise</b> met in this slice and handled: literati and statesmen among pre-1400 "calligraphers" (Raja ibn Haywa, Ibn ʿAttash excluded), Wikidata trades and garment types in the folk sweep, the 260 unmapped in-situ items, fallback "kind – country" mural buckets.</li>
<li><b>Anime-film matching:</b> 203 of the 301 Japanese animated films in the film selection were matched to the anime selection by title and year; the rest differ only in romanisation and are matched in the anime build, so each keeps one home.</li>
</ul>

<h2 id="r-next">Scaling plan after your review</h2>
<ol>
<li>Apply your rulings (Q1–Q8) to the keys; re-run the pilot build and the blind test.</li>
<li>Visual Art, tradition-led cells region by region (South Asia, East Asian ceramics and sculpture, Africa, the Americas, Oceania, the ancient world), with kinds seeded from the object records.</li>
<li>Visual Art, artist-led cells: period styles and movements as leaves (Europe 1400–1900, modern, contemporary); artists with no attested movement need a rule (proposal: the period-style leaf of their medium).</li>
<li>Film &amp; Television: the remaining 17,600 films by the same key (features now carry keywords), then scripted TV, serial traditions, anime, Asian drama and unscripted formats.</li>
<li>Full audit (blind test, seams, probes, census) per tab, then the first full release with frozen codes.</li>
</ol>
"""
