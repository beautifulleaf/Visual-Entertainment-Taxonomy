# Television (B1–B16) coverage pass
Scripts: `find.py` (pool lookup), `build.py` (writes all outputs; checks resections cover every title; adds checked against placed format Q-ids).

## Audit
Checked all 263 B leaves/sections against the List of television genres, Wikipedia "Reality television" subgenres, and TV-relevant IMDb interests (Sitcom, Cozy Mystery, Docusoap, Business/Paranormal/Crime Reality TV, Home Improvement, News, Cooking & Food, Travel, Survival Competition, Court/Talk/Game/Quiz, Soap, Telenovela, Steampunk, Kaiju, Bumbling Detective). No B leaf was empty. Micro-drama/web series excluded.

Missing or thin → done:
- Golden Age of Television anthology drama → NEW_GOLDEN (B1), 9 moved from B1-29 + 14 added; live / filmed sections.
- Business Reality TV → NEW_BIZ (B14): Dragons' Den format (incl. Shark Tank), Kitchen Nightmares format, Undercover Boss moved; 12 added.
- Home Improvement / property TV → NEW_PROP (B14): Grand Designs, Love It or List It moved from B14-4; 21 added. Home/garden makeovers (Changing Rooms, Trading Spaces, DIY SOS, Ground Force) added to B14-4 sec 2.
- Crime Reality TV → NEW_CRIME (B14): Cops (series+format), Poliisit, Dog the Bounty Hunter, Missing: Dead or Alive? moved from B14-2; 17 added.
- News → NEW_NEWS (B11), 43 titles in 6 form sections.
- Sinetron (Indonesia) → new leaf B12, 4 titles (pool thin).
- Filled: B14-9 Court Show 2→15; B14-6 Paranormal TV 4→22 (re-sectioned); B12-10 Sri Lankan Teledrama 3→8; B12-3 Narconovela +10; B12-8 Mythological +9; B15-5 Clip Show +5; B7-7 Tartan Noir +2; B10-2 Educational +5; B11-12 +4; B12-1 Telenovela +8.
- Steampunk → new section in B9-17 (2 moved within leaf, 2 added).
- Cooking show → B14-8 re-sectioned (cooking / craft / know-how), +15 cooking shows.
- Outdoor survival → B14-7 re-sectioned (motoring / comic travel / survival), +6.

## Fundamentals
- B1-1 Prestige Drama re-sectioned by era: Third Golden Age cable prestige (1999–2012) / Peak TV (2013–).
- B15-1 Variety re-sectioned by era (Golden Age 1948–60 / network variety hours 1961–79 / post-network & international), +19 classic variety hours.
- Golden Age anthology is now a named era-cycle leaf. Telenovela/soap were already split by national tradition.

## Doubts
- Sitcom eras (British sitcom eras, US network-era/Lear sitcoms) not done: titles are spread over B8-1/3/5/9 by premise, so re-sectioning would re-sort the comedy family. Owner decision; decade/country filters may suffice.
- Canonical prestige dramas stay in their genre leaves; B1-1 is a small residual leaf.
- News is arguably not entertainment; drop NEW_NEWS if out of scope.
- Scare PewDiePie (YouTube Red) in B14-6 is borderline web; left as is.
- IMDb interest sources cited as taxonomy/r3/imdb_interests.tsv (no verified interest-page URLs).
