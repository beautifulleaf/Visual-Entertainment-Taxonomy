"""Build the anime candidate set from anime-offline-database (sourcing-plan.md §4).

Downloads the weekly minified JSON release of cedya77/anime-offline-database
(ODbL; continuation of manami-project's archived repository), which cross-links
MyAnimeList, AniList, Kitsu, AniDB and others, and flattens it to one row per
entry with its IDs, format, season, episodes, studios and tags.

Output: data/interim/anime_candidates.csv (input for popularity.py)

Usage: python3 pipelines/anime/build_candidates.py
"""
import csv
import json
import os
import re
import urllib.request

URL = "https://github.com/cedya77/anime-offline-database/releases/latest/download/anime-offline-database-minified.json"
UA = "VisualEntertainmentTaxonomy/0.1 (research; contact via repository)"
ID_SITES = {
    "myanimelist.net": "mal_id", "anilist.co": "anilist_id", "kitsu.app": "kitsu_id",
    "anidb.net": "anidb_id", "animenewsnetwork.com": "ann_id", "livechart.me": "livechart_id",
}

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw", "anime", "anime-offline-database-minified.json")
OUT_PATH = os.path.join(ROOT, "data", "interim", "anime_candidates.csv")


def main():
    os.makedirs(os.path.dirname(RAW), exist_ok=True)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    if not os.path.exists(RAW):
        print("downloading anime-offline-database")
        req = urllib.request.Request(URL, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=300) as r, open(RAW, "wb") as f:
            f.write(r.read())
    db = json.load(open(RAW, encoding="utf-8"))
    print(f"anime-offline-database, last update {db.get('lastUpdate')}: {len(db['data'])} entries")

    cols = ["title", "type", "episodes", "status", "season", "year", "duration_min", "aod_score"] + \
        list(ID_SITES.values()) + ["studios", "tags", "synonyms"]
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as out:
        w = csv.DictWriter(out, fieldnames=cols)
        w.writeheader()
        for a in db["data"]:
            row = {
                "title": a["title"], "type": a["type"], "episodes": a.get("episodes"), "status": a.get("status"),
                "season": (a.get("animeSeason") or {}).get("season"), "year": (a.get("animeSeason") or {}).get("year"),
                "duration_min": round(a["duration"]["value"] / 60, 1) if a.get("duration") else None,
                "aod_score": round(a["score"]["median"], 2) if a.get("score") else None,
                "studios": "|".join(a.get("studios") or []), "tags": "|".join(a.get("tags") or []),
                "synonyms": "|".join((a.get("synonyms") or [])[:10]),
            }
            for src in a["sources"]:
                site = src.split("/")[2]
                m = re.search(r"/(\d+)$", src)
                if site in ID_SITES and m:
                    row[ID_SITES[site]] = m.group(1)
            w.writerow(row)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
