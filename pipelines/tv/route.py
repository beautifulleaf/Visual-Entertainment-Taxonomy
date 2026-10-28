"""Split enriched series between the four series databases (sourcing-plan.md §3-6).

  anime         has a MAL id (MDBList cross-link), or is animation from JP/CN
                (donghua is in the anime database)
  unscripted    reality, game, talk and news shows; grouped by format later
                (pipelines/unscripted/build_formats.py)
  asian_drama   live-action series from East and Southeast Asia
  scripted_tv   everything else, documentary series included (they use the
                scripted-TV thresholds)

Scripted-TV rows also get `serial_tradition` = 1 for long-running serials in the
telenovela / dizi / Indian-soap / teleserye / Ramadan-series traditions, which
form their own format node and rely on the regional-percentile rule.

Input:  data/interim/tv_ratings.csv
Output: data/interim/tv_routed.csv (tv_ratings + database + serial_tradition)

Usage: python3 pipelines/tv/route.py
"""
import collections
import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IN_PATH = os.path.join(ROOT, "data", "interim", "tv_ratings.csv")
OUT_PATH = os.path.join(ROOT, "data", "interim", "tv_routed.csv")

ASIAN_DRAMA = {"KR", "CN", "JP", "TW", "HK", "TH", "PH", "SG", "MY", "ID", "VN"}
ANIME_ANIMATION = {"JP", "CN"}
UNSCRIPTED_GENRES = {"Reality-TV", "Game-Show", "Talk-Show", "News", "Reality", "Talk"}
# Countries whose long-running serial traditions get their own node (§3 decision).
SERIAL_COUNTRIES = {
    "MX", "BR", "CO", "VE", "AR", "CL", "PE",   # telenovela
    "TR",                                        # dizi
    "IN", "PK", "BD",                            # daily soaps
    "PH",                                        # teleserye (also in the Asian-drama set)
    "EG", "SY", "SA", "AE", "KW", "LB", "JO",    # Ramadan series
    "PT", "ES",
}
# Dizi run ~30-40 long (2h+) episodes a season; telenovelas and daily soaps run 100+.
# A flat 40 caught short prestige series (Money Heist, Elite).
SERIAL_MIN_EPISODES = {"TR": 30}
SERIAL_MIN_EPISODES_DEFAULT = 100


def genres_of(row):
    return set(filter(None, (row.get("imdb_genres") or "").split("|") + (row.get("mdblist_genres") or "").split("|")))


def route(row):
    g, country = genres_of(row), (row.get("country") or "").upper()
    if row.get("mal_id") or ("Animation" in g and country in ANIME_ANIMATION):
        return "anime"
    if g & UNSCRIPTED_GENRES and not g & {"Drama", "Comedy", "Crime", "Thriller"}:
        return "unscripted"
    if country in ASIAN_DRAMA:
        return "asian_drama"
    return "scripted_tv"


def main():
    with open(IN_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    counts, serials = collections.Counter(), 0
    for r in rows:
        r["database"] = route(r)
        eps = int(r.get("episodes") or 0)
        r["serial_tradition"] = int(
            r["database"] == "scripted_tv" and (r.get("country") or "").upper() in SERIAL_COUNTRIES
            and eps >= SERIAL_MIN_EPISODES.get((r.get("country") or "").upper(), SERIAL_MIN_EPISODES_DEFAULT)
            and bool(genres_of(r) & {"Drama", "Romance"}))
        serials += r["serial_tradition"]
        counts[r["database"]] += 1
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} series: {dict(counts)}; serial-tradition flag on {serials} scripted-TV series")
    for db in counts:
        votes = [int(r["imdb_votes"]) for r in rows if r["database"] == db and r.get("imdb_votes")]
        print(f"  {db:12} IMDb >=2.5k votes: {sum(v >= 2500 for v in votes):>6}   >=500: {sum(v >= 500 for v in votes):>6}")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
