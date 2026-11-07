"""Lookup helper: python3 q.py 'regex' [more regexes]  -> placed titles + pool matches"""
import csv, re, sys, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..")
csv.field_size_limit(10**9)
P = list(csv.DictReader(open(f"{R}/taxonomy/r3/ft_title_index.tsv"), delimiter="\t"))
placed = {r["id"] for r in P}
AN = {r["mal_id"]: r for r in csv.DictReader(open(f"{R}/data/interim/anime_popularity.csv"))}
AC = list(csv.DictReader(open(f"{R}/data/interim/anime_candidates.csv")))
FR = {r["tconst"]: r for r in csv.DictReader(open(f"{R}/data/interim/film_ratings.csv"))}
FC = list(csv.DictReader(open(f"{R}/data/interim/film_candidates.csv")))
TV = list(csv.DictReader(open(f"{R}/data/interim/tv_candidates.csv")))
for pat in sys.argv[1:]:
    rx = re.compile(pat, re.I)
    print("=====", pat)
    for r in P:
        if rx.search(r["title"]): print("  PLACED", r["id"], r["title"], r["year"], r["who"], r["leaf"])
    for r in AC:
        if rx.search(r["title"]) or rx.search(r["synonyms"][:300]):
            if r["mal_id"] in placed: continue
            a = AN.get(r["mal_id"], {})
            print("  ANIME", r["mal_id"], r["title"], r["type"], r["year"], a.get("mal_members"), r["studios"][:30])
    for r in FC:
        if (rx.search(r["title"]) or rx.search(r["original_title"])) and r["tconst"] not in placed:
            f = FR.get(r["tconst"], {})
            print("  FILM", r["tconst"], r["title"], r["year"], r["title_type"], r["genres"], r["imdb_votes"], f.get("letterboxd_votes"), f.get("country"))
    for r in TV:
        if rx.search(r["title"]) and r["tconst"] not in placed:
            print("  TV", r["tconst"], r["title"], r["start_year"], r["genres"], r["imdb_votes"])
