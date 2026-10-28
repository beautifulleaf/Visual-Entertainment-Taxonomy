"""Film & Television tab: families, sub-families and (pilot) leaves.

Pilot slice: Japanese cinema. Scale-up (2026-10-28): global feature-film and
short-film leaves; leaves added after the pilot are appended inside each
sub-family, so pilot codes keep their meaning. Japanese animated films go to the
Anime family (FT-E). Codes are provisional until the first full release.

Leaf tuple: (code, label, breadth, definition, aliases, see_also, attest)
"""

TAB = "FT"
TAB_NAME = "Film & Television"

FAMILY_KEY = [
    "1. Is it <b>Japanese animation</b> (anime), in any format — TV series, film, OVA, ONA, special? → <b>E Anime</b>; format is a filter (D4). Animation from elsewhere is placed by its form below (a feature → A15 Animated Feature).",
    "2. Is it an <b>unscripted format</b> licensed across countries (talent competition, dating, cooking, game show, docusoap)? → <b>G Unscripted Formats</b>.",
    "3. Is it a <b>long-running serial</b> in a named serial tradition — telenovela, dizi, Indian daily soap, soap opera? → <b>D Serial Drama Traditions</b>.",
    "4. Any other <b>scripted series or miniseries</b>, from anywhere — including the East and Southeast Asian drama traditions (K-drama, Chinese costume drama, asadora, taiga drama, lakorn)? → <b>C Television Series</b> (D3: Asian drama is a filter, not a family).",
    "5. A film of <b>40 minutes or less</b>? → <b>B Short Film</b>. Otherwise → <b>A Feature Film</b> (the Academy's 40-minute line).",
]

PRECEDENCE = [
    ("F1", "Named cycle before movement", "A film with a home in a named genre cycle (chanbara, kaidan, J-horror, yakuza, film noir, pink film, Roman Porno, pinky violence, kaiju, tokusatsu, Taiyōzoku) goes to that cycle, even when a movement's reference sources list it as a member. A movement leaf keeps the attested members with no cycle home; every attested member carries the movement as a tag (D1)."),
    ("F2", "Named cycle before general genre", "A named cycle with its own canon (J-horror, kaiju eiga, yakuza eiga, pink film) beats the general genre leaf (supernatural horror, monster film, gangster film, sexploitation)."),
    ("F3", "Ghosts before period", "A film whose story turns on ghosts or the supernatural is horror (kaidan eiga) even when set in the Edo period; period setting alone does not make jidaigeki win."),
    ("F4", "Swords before period", "A jidaigeki whose drama is carried by sword combat is chanbara; a period film of manners, politics or family is jidaigeki."),
    ("F5", "Giant monsters", "A film built on a giant monster (kaiju) is Kaiju Film whether or not a costumed hero appears; a costumed transforming hero with no giant monster at its centre is Tokusatsu Hero Film."),
    ("F6", "Crime vs thriller", "Criminals or police and their world at the centre → Crime; suspense built on a threat to an ordinary protagonist, a conspiracy or a puzzle → Thriller & Mystery."),
    ("F7", "Drama vs romance vs comedy", "A love story as the main line → Romance; aimed at laughter first → Comedy; otherwise Drama, divided by its subject."),
    ("F9", "Framing devices", "A fantastical or science-fiction device that only frames a love story or a youth drama (a time slip, a letter from the future) does not make the film fantasy or science fiction: it is placed by the story it frames (A9, A14-3)."),
    ("F10", "Leaf examples follow the key", "When a film named as a leaf example would be sent elsewhere by the key, the key wins and the example is replaced; examples never override the key."),
    ("F8", "Anime", "Japanese animation is always E Anime, never an animated-feature leaf, whatever list it was selected from."),
]

MODIFIERS = [
    "<b>Country of origin</b> — a filter (Wikidata P495 first, as in the selection rule; a co-production counts in each of its countries, D8). National cinemas are never divisions; national cycles and movements defined by what the films are (J-horror, Japanese New Wave) are leaves.",
    "<b>Decade and period of release</b> — a filter.",
    "<b>Director, studio, writer</b> — tags; studio-branded cycles are leaves only where the field names them as a genre (Nikkatsu Roman Porno).",
    "<b>Setting</b> — jidaigeki (pre-1868) or gendaigeki (contemporary) as a filter on every Japanese film; a leaf (Jidaigeki) exists only for the period drama genre.",
    "<b>Release format</b> — theatrical, V-cinema (direct-to-video), TV movie, streaming: a filter.",
    "<b>Movement</b> — a tag on every attested member of a named movement (Japanese New Wave), including members placed in a genre cycle (D1).",
    "<b>Format</b> — for anime: TV series, film, OVA, ONA, special (D4). For series: miniseries, limited, ongoing.",
    "<b>Asian drama</b> — the drama database's scope (Korea, China, Japan, Taiwan, Thailand, the Philippines, Hong Kong, Singapore) as a filter on Television Series (D3).",
    "<b>Source material</b> (manga, novel, true story) — a tag.",
    "<b>Language, rating, runtime, platform</b> — tags.",
    "<b>Audience counts</b> (Letterboxd, IMDb, MAL, MDL) — kept internal (licensing); never shown.",
]

FAMILIES = [
    {"code": "A", "label": "Feature Film",
     "test": "a film of more than 40 minutes made as a single work for cinema, festival, television or streaming release; not anime.",
     "key": [
         "1. Non-fiction? → <b>A13 Documentary</b>.",
         "2. Does it belong to a <b>named genre cycle</b> (the narrower leaves of A2–A12: chanbara, kaidan, J-horror, yakuza, noir, pink, Roman Porno, pinky violence, kaiju, tokusatsu, Taiyōzoku)? → skip to that leaf (F1). Otherwise, is it an <b>attested member of a named film movement</b>? → <b>A1 Movements & Schools</b>.",
         "3. Is erotic display or sexual obsession the film's reason to exist — made for the sex-film circuit, or an art-house film built on it? → <b>A12 Erotic Film</b>. A violent exploitation cycle with erotic elements (pinky violence) is not: it goes on.",
         "4. Does it aim first to frighten (ghosts, monsters, killers, gore)? → <b>A4 Horror</b> (F3).",
         "5. Is its premise speculative science — the future, technology, space, giant monsters, transforming heroes? → <b>A5 Science Fiction & Monster</b> (F5). Magic or myth? → <b>A6 Fantasy & Adventure</b>.",
         "6. Is it set in a past era that defines it, or about war? → <b>A7 Historical, Period & War</b> (F4). A frontier western → <b>A17 Western</b>.",
         "7. Criminals or police at the centre? → <b>A2 Crime</b>. Suspense, conspiracy or puzzle? → <b>A3 Thriller & Mystery</b> (F6).",
         "8. Fights, chases and stunts carry it? → <b>A8 Action & Martial Arts</b>.",
         "9. Songs carry the story? → <b>A11 Musical & Music</b>. Laughter first? → <b>A10 Comedy</b>. A love story? → <b>A9 Romance</b>. Otherwise → <b>A14 Drama</b> (F7).",
     ],
     "subs": [
         ("A1", "Movements & Schools", "Axis: the named movement (membership attested in its reference sources)."),
         ("A2", "Crime", "Axis: whose side the story takes and its milieu."),
         ("A3", "Thriller & Mystery", "Axis: the source of suspense."),
         ("A4", "Horror", "Axis: the source of fear."),
         ("A5", "Science Fiction & Monster", "Axis: the speculative premise."),
         ("A6", "Fantasy & Adventure", "Axis: the kind of wonder."),
         ("A7", "Historical, Period & War", "Axis: the era and what the past is used for."),
         ("A8", "Action & Martial Arts", "Axis: the fighting tradition."),
         ("A9", "Romance", "Axis: tone."),
         ("A10", "Comedy", "Axis: comic mode."),
         ("A11", "Musical & Music", "Axis: how music carries the film."),
         ("A12", "Erotic Film", "Axis: the circuit it was made for."),
         ("A13", "Documentary", "Axis: mode and subject."),
         ("A14", "Drama", "Axis: the drama's subject (family, youth, society, the individual)."),
         ("A15", "Animated Feature", "Axis: technique and tradition (non-anime). Built at scale."),
         ("A16", "Experimental & Avant-Garde", "Axis: practice."),
         ("A17", "Western", "Axis: setting (the American frontier and its transpositions)."),
     ]},
    {"code": "B", "label": "Short Film", "test": "a film under 40 minutes.", "key": ["Placed by the Feature Film key; short-film leaves are built at scale."], "subs": []},
    {"code": "C", "label": "Television Series", "test": "a scripted series or miniseries made for television or streaming, anywhere, outside the named long-running serial traditions and anime.", "key": ["Placed by genre and by named drama tradition; built at scale (D3)."],
     "subs": [("C1", "Drama Series", "Axis: subject. Built at scale."),
              ("C2", "East & Southeast Asian Drama Traditions", "Axis: the named tradition — K-drama melodrama, Chinese costume drama (guzhuang), wuxia and xianxia drama, Japanese asadora and taiga drama, Thai lakorn. Built at scale; 'Asian drama' is a filter (D3)."),
              ("C3", "Crime & Thriller Series", "Axis: milieu. Built at scale."),
              ("C4", "Comedy Series", "Axis: comic form (sitcom, single-camera, sketch). Built at scale."),
              ("C5", "Genre Series", "Axis: speculative premise (science fiction, fantasy, horror). Built at scale.")]},
    {"code": "D", "label": "Serial Drama Traditions", "test": "a long-running serial in a named serial tradition: telenovela, dizi, Indian daily soap, soap opera.", "key": [], "subs": []},
    {"code": "E", "label": "Anime", "test": "Japanese animation in any format (TV series, film, OVA, ONA, special); format is a filter, never a division (D4). Donghua and Korean animation selected through the anime database are placed here with their country as a filter.", "key": ["Placed by genre and demographic; built at scale (D4)."],
     "subs": [("E1", "Action & Battle", "Axis: the fighting premise (shōnen battle, martial arts, samurai). Built at scale."),
              ("E2", "Mecha & Science Fiction", "Axis: real-robot, super-robot, cyberpunk, space opera. Built at scale."),
              ("E3", "Fantasy & Isekai", "Axis: the invented world. Built at scale."),
              ("E4", "Magical Girl", "Axis: tradition. Built at scale."),
              ("E5", "Romance & Romantic Comedy", "Axis: tone and demographic (shōjo, josei, harem). Built at scale."),
              ("E6", "Slice of Life & Iyashikei", "Axis: setting. Built at scale."),
              ("E7", "Sports", "Axis: sport. Built at scale."),
              ("E8", "Drama, Psychological & Mystery", "Axis: subject. Built at scale."),
              ("E9", "Horror", "Axis: source of fear. Built at scale."),
              ("E10", "Comedy", "Axis: comic mode. Built at scale."),
              ("E11", "Children's & Family", "Axis: audience. Built at scale.")]},
    {"code": "F", "label": "Asian Drama (retired)", "test": "Retired by ruling D3: East and Southeast Asian drama series are placed in C Television Series (C2) and 'Asian drama' is a filter. The code F is not reused.", "key": [], "subs": []},
    {"code": "G", "label": "Unscripted Formats", "test": "a cross-border unscripted format (≥3 versions in ≥2 countries); its national versions are kinds.", "key": [], "subs": []},
]

LEAVES = {
    "A1": [
        ("A1-1", "Japanese New Wave", "medium",
         "the Nūberu bāgu: films of Ōshima, Imamura, Yoshida, Shinoda, Teshigahara, Hani and their peers (c. 1959–1975) that broke with studio humanism through politics, sexuality and formal rupture (<i>Cruel Story of Youth</i>, <i>Woman in the Dunes</i>, <i>Death by Hanging</i>). Members with a genre-cycle home (<i>Harakiri</i>, <i>Kwaidan</i>, <i>Branded to Kill</i>) sit in that cycle and carry the movement as a tag (D1).",
         "Nūberu bāgu; Shōchiku Nouvelle Vague", "A14 Drama; A12-1 Pink Film.", "Japanese New Wave"),
    ],
    "A2": [
        ("A2-1", "Yakuza Film", "medium",
         "yakuza eiga: films of the Japanese gangster world, from the chivalrous ninkyō films of 1960s Toei to the documentary-style jitsuroku films (<i>Battles Without Honor and Humanity</i>) and the V-cinema and Kitano cycles (<i>Sonatine</i>).",
         "yakuza eiga; ninkyō eiga; jitsuroku eiga", "A2-2 Gangster Film.", "yakuza film"),
        ("A2-2", "Gangster Film", "medium",
         "films centred on organised criminals and their rise and fall outside the named national cycles.",
         "mob film", "A2-1 Yakuza Film.", "gangster film"),
        ("A2-3", "Police & Detective Film", "medium",
         "films centred on police or detectives working a case (<i>Stray Dog</i>, <i>High and Low</i>).",
         "police procedural; detective film", "A3-2 Mystery Film.", "police procedural"),
        ("A2-4", "Crime Drama", "broad",
         "films about crime, its perpetrators and its effects, told as drama rather than suspense or gang epic (<i>Vengeance Is Mine</i>, <i>The Third Murder</i>).",
         "crime film", "A3-1 Psychological Thriller.", "crime film"),
        ("A2-5", "Film Noir & Neo-Noir", "medium",
         "crime films in the noir manner — fatalism, low-key style, corrupt cities — including Japanese noir (<i>Pale Flower</i>, <i>Branded to Kill</i>).",
         "noir; neo-noir", "A2-1 Yakuza Film.", "film noir|neo-noir"),
        ("A2-6", "Pinky Violence", "narrow",
         "Toei's 1970s cycle of women's revenge, delinquent-girl (sukeban) and women-in-prison films, with violence and eroticism (<i>Female Prisoner #701: Scorpion</i>).",
         "sukeban films; women-in-prison film", "A12-1 Pink Film; A2-1 Yakuza Film.", "pinky violence"),
    ],
    "A3": [
        ("A3-1", "Psychological Thriller", "broad",
         "suspense built on disturbed minds, obsession and manipulation (<i>Cure</i>, <i>Confessions</i>).",
         "", "A4 Horror.", "psychological thriller"),
        ("A3-2", "Mystery Film", "medium",
         "whodunits and puzzle films built on detection, including honkaku adaptations (<i>The Inugamis</i>).",
         "whodunit; detective mystery", "A2-3 Police & Detective Film.", "mystery film"),
        ("A3-3", "Survival & Death-Game Thriller", "medium",
         "films in which characters are forced into a lethal contest or ordeal (<i>Battle Royale</i>, <i>As the Gods Will</i>).",
         "death game; survival thriller", "A4-5 Splatter & Gore Film.", "survival film"),
    ],
    "A4": [
        ("A4-1", "J-Horror", "medium",
         "the Japanese horror cycle of the late 1990s–2000s: vengeful onryō, curses carried by media and technology, slow dread (<i>Ring</i>, <i>Ju-On</i>, <i>Pulse</i>, <i>Dark Water</i>).",
         "Japanese horror; J-horror cycle", "A4-2 Kaidan Film.", "J-horror|Japanese horror"),
        ("A4-2", "Kaidan Film", "narrow",
         "kaidan eiga: ghost-story films drawn from Edo and folk tales (<i>Ugetsu</i>, <i>Kwaidan</i>, <i>Onibaba</i>, <i>Kuroneko</i>).",
         "kaidan eiga; Japanese ghost story film", "A4-1 J-Horror.", "kaidan"),
        ("A4-3", "Supernatural Horror", "broad",
         "horror from ghosts, demons and curses outside the named Japanese cycles (<i>House</i>, <i>Noroi</i>).",
         "", "A4-1 J-Horror; A4-2 Kaidan Film.", "supernatural horror film"),
        ("A4-4", "Body Horror", "narrow",
         "horror of the body transformed, invaded or fused with machines (<i>Tetsuo: The Iron Man</i>).",
         "biological horror", "A5-4 Cyberpunk.", "body horror"),
        ("A4-5", "Splatter & Gore Film", "medium",
         "horror built on graphic violence, mutilation and torture (<i>Audition</i>, <i>Ichi the Killer</i>, <i>Tokyo Gore Police</i>).",
         "splatter film; ero guro; extreme cinema", "A3-3 Survival & Death-Game Thriller.", "splatter film"),
        ("A4-6", "Zombie Film", "narrow",
         "horror of the walking dead (<i>One Cut of the Dead</i>, <i>Versus</i>).",
         "", "", "zombie film"),
        ("A4-7", "Found-Footage Horror", "narrow",
         "horror presented as recovered amateur or documentary footage (<i>Noroi: The Curse</i>).",
         "found footage", "", "found footage film"),
        ("A4-8", "Slasher Film", "narrow",
         "horror built on a killer stalking and murdering victims one by one (<i>Evil Dead Trap</i>).",
         "slasher", "A4-5 Splatter & Gore Film.", "slasher film"),
        ("A4-9", "Psychological Horror", "medium",
         "horror whose dread comes from disturbed minds, unreality and inescapable spaces rather than monsters or gore (<i>Strange Circus</i>, <i>Haze</i>, <i>Exit 8</i>).",
         "", "A3-1 Psychological Thriller.", "psychological horror"),
    ],
    "A5": [
        ("A5-1", "Kaiju Film", "medium",
         "kaiju eiga: films built on giant monsters — Godzilla, Mothra, Rodan, Gamera — and their destruction of cities (<i>Godzilla</i> 1954, <i>Shin Godzilla</i>).",
         "kaiju eiga; giant monster film", "A5-2 Tokusatsu Hero Film.", "kaiju"),
        ("A5-2", "Tokusatsu Hero Film", "medium",
         "live-action special-effects films of costumed transforming heroes (Ultraman, Kamen Rider, Super Sentai).",
         "tokusatsu; henshin hero", "A5-1 Kaiju Film.", "tokusatsu"),
        ("A5-3", "Science Fiction Film", "broad",
         "speculative films of the future, technology, space and alien contact outside the narrower leaves (<i>Virus</i>, <i>Summer Time Machine Blues</i>).",
         "sci-fi", "A5-4 Cyberpunk.", "science fiction film"),
        ("A5-4", "Cyberpunk", "narrow",
         "high-tech, low-life science fiction of cybernetic bodies and urban decay, with its Japanese punk-industrial strand (<i>Tetsuo</i>, <i>Burst City</i>).",
         "Japanese cyberpunk", "A4-4 Body Horror.", "cyberpunk"),
        ("A5-5", "Disaster & Post-Apocalyptic Film", "medium",
         "films of catastrophe — natural, technological or speculative — and of collapse and survival after it (<i>Airport</i>, <i>The Poseidon Adventure</i>, <i>Japan Sinks</i>, <i>Mad Max: Fury Road</i>) (F26).",
         "disaster film; post-apocalyptic film", "A5-3 Science Fiction Film.", "disaster film|post-apocalyptic film"),
    ],
    "A6": [
        ("A6-1", "Fantasy Film", "broad",
         "live-action films of magic, myth and invented worlds (<i>The Great Yokai War</i>).",
         "", "A4-3 Supernatural Horror.", "fantasy film"),
        ("A6-2", "Adventure Film", "medium",
         "journeys and quests in exotic or perilous settings.",
         "", "A6-1 Fantasy Film.", "adventure film"),
        ("A6-3", "Superhero & Manga Action Adaptation", "medium",
         "live-action adaptations of superhero and battle manga whose premise is extraordinary powers (<i>Gantz</i>, <i>Death Note</i>).",
         "superhero film; live-action manga adaptation", "A5-2 Tokusatsu Hero Film.", "superhero film"),
    ],
    "A7": [
        ("A7-1", "Jidaigeki", "broad",
         "period drama set before the Meiji Restoration in which the past is the subject — manners, politics, family and fate rather than swordplay (<i>Sansho the Bailiff</i>, <i>The Life of Oharu</i>, <i>Twilight Samurai</i>).",
         "period drama (Japanese); historical drama", "A7-2 Chanbara.", "Jidaigeki"),
        ("A7-2", "Chanbara", "medium",
         "samurai swordplay films in which sword combat carries the drama (<i>Seven Samurai</i>, <i>Yojimbo</i>, <i>Zatoichi</i>, <i>13 Assassins</i>).",
         "samurai film; swordplay film; chambara", "A7-1 Jidaigeki.", "samurai cinema|chambara"),
        ("A7-3", "War Film", "broad",
         "films about war and soldiers' experience of it (<i>Fires on the Plain</i>, <i>The Burmese Harp</i>, <i>The Human Condition</i>).",
         "anti-war film", "A7-4 Historical Drama.", "war film"),
        ("A7-4", "Historical Drama", "medium",
         "films whose past era defines them outside jidaigeki and war: Meiji, Taishō and Shōwa stories, real events and biopics (<i>The Story of the Last Chrysanthemum</i>, <i>Sanshiro Sugata</i> excepted as martial arts).",
         "biopic; historical film", "A7-3 War Film.", "historical drama film|biographical film"),
        ("A7-5", "Atomic Bomb Film", "narrow",
         "genbaku eiga: films about the bombings of Hiroshima and Nagasaki and the hibakusha (<i>Children of Hiroshima</i>, <i>Black Rain</i>).",
         "genbaku eiga; hibakusha cinema", "A7-3 War Film.", "hibakusha"),
    ],
    "A8": [
        ("A8-1", "Martial Arts Film", "medium",
         "films built on unarmed or weapons combat in modern or timeless settings (<i>The Street Fighter</i>), outside chanbara.",
         "karate film", "A7-2 Chanbara.", "martial arts film"),
        ("A8-2", "Action Film", "broad",
         "films carried by fights, chases, gunplay and stunts outside the narrower leaves (<i>Shinobi</i>, <i>Alive</i>).",
         "action thriller", "A8-1 Martial Arts Film.", "action film"),
    ],
    "A9": [
        ("A9-1", "Romantic Drama", "broad",
         "love stories told as drama (<i>Love Letter</i>, <i>Norwegian Wood</i>).",
         "melodrama of love", "A9-2 Romantic Comedy.", "romance film"),
        ("A9-2", "Romantic Comedy", "medium",
         "love stories told for laughter.",
         "romcom", "A10-1 Comedy Film.", "romantic comedy"),
    ],
    "A10": [
        ("A10-1", "Comedy Film", "broad",
         "films aimed first at laughter (<i>Tampopo</i>, <i>Swing Girls</i>).",
         "", "A10-2 Comedy-Drama.", "comedy film"),
        ("A10-2", "Comedy-Drama", "broad",
         "films that balance comedy with serious drama (<i>Tokyo Sonata</i>).",
         "dramedy", "A14 Drama.", "comedy drama"),
        ("A10-3", "Black Comedy & Satire", "medium",
         "comedy of death, taboo and social satire (<i>The Funeral</i>, <i>The Taste of Tea</i>).",
         "dark comedy; satire", "A10-1 Comedy Film.", "black comedy"),
    ],
    "A11": [
        ("A11-1", "Musical & Music Film", "medium",
         "films carried by song and music, including band and idol films (<i>Linda Linda Linda</i>, <i>The Happiness of the Katakuris</i>).",
         "musical film; music film", "", "musical film"),
    ],
    "A12": [
        ("A12-1", "Pink Film", "medium",
         "pinku eiga: independent Japanese softcore features made from the 1960s for the pink-film circuit, a training ground for directors (<i>Daydream</i>).",
         "pinku eiga", "A12-2 Roman Porno.", "pink film"),
        ("A12-2", "Roman Porno", "narrow",
         "Nikkatsu's studio line of erotic features (1971–1988) under which Kumashiro, Tanaka and Sone made auteur films (<i>Flower and Snake</i>, <i>A Woman Called Sada Abe</i>).",
         "Nikkatsu Roman Porno; romanporno", "A12-1 Pink Film.", "Roman Porno|Nikkatsu Roman Porno"),
        ("A12-3", "Erotic Drama", "narrow",
         "art-house and mainstream films whose subject is sexual obsession (<i>In the Realm of the Senses</i>, <i>The Housemaid</i>).",
         "erotic film", "A12-1 Pink Film.", "erotic film"),
    ],
    "A13": [
        ("A13-1", "Documentary Film", "broad",
         "non-fiction films (<i>The Emperor's Naked Army Marches On</i>, <i>Minamata</i> series).",
         "", "", "documentary film"),
    ],
    "A14": [
        ("A14-1", "Shomingeki", "medium",
         "shomin-geki: dramas of ordinary lower-middle-class urban life, centred on the family and the workplace, the home genre of Ozu, Naruse and Kinoshita (<i>Tokyo Story</i>, <i>Floating Clouds</i>).",
         "shomin-geki; home drama", "A14-2 Family Drama.", "shomingeki|Shomin-geki"),
        ("A14-2", "Family Drama", "broad",
         "dramas of families, parents and children outside the classic shomingeki (<i>Shoplifters</i>, <i>Nobody Knows</i>, <i>Like Father, Like Son</i>).",
         "family film (drama)", "A14-1 Shomingeki.", "family drama"),
        ("A14-3", "Coming-of-Age Film", "broad",
         "seishun eiga: youth and school films about growing up (<i>All About Lily Chou-Chou</i>, <i>Kids Return</i>).",
         "seishun eiga; youth film; teen film", "A14-2 Family Drama.", "coming-of-age film|teen film"),
        ("A14-4", "Social Drama", "broad",
         "dramas of social conditions, poverty, work, institutions and injustice (<i>Ikiru</i>, <i>The Ballad of Narayama</i>, <i>Departures</i>).",
         "social problem film; social realism", "A14-5 Character Study.", "social drama|social problem film"),
        ("A14-5", "Character Study", "broad",
         "dramas centred on one person's inner life, grief, solitude or change (<i>Drive My Car</i>, <i>Perfect Days</i>).",
         "psychological drama; art-house drama", "A14-4 Social Drama.", "psychological drama|drama film"),
        ("A14-6", "Melodrama", "medium",
         "emotionally heightened dramas of suffering and sacrifice, especially women's films (haha-mono mother films, <i>The Life of Oharu</i>).",
         "haha-mono; women's film", "A9-1 Romantic Drama.", "melodrama"),
        ("A14-7", "Sports Film", "narrow",
         "dramas built on a sport and its competition.",
         "", "", "sports film"),
        ("A14-8", "Animal Film", "narrow",
         "live-action films centred on an animal and its bond with people (<i>The Story of Hachikō</i>, <i>The Adventures of Milo and Otis</i>).",
         "dog film; animal story", "A14-2 Family Drama.", "animal film"),
        ("A14-9", "Taiyōzoku Film", "narrow",
         "the 'Sun Tribe' youth films of 1956 adapted from Ishihara Shintarō — affluent, amoral postwar youth (<i>Season of the Sun</i>, <i>Crazed Fruit</i>).",
         "Sun Tribe films; taiyōzoku eiga", "A14-3 Coming-of-Age Film; A1-1 Japanese New Wave.", "Taiyōzoku"),
    ],
    "A17": [
        ("A17-1", "Western", "medium",
         "films of the frontier gunfighter, including spaghetti and transposed westerns (<i>Sukiyaki Western Django</i>).",
         "spaghetti western; eastern western", "A7-2 Chanbara.", "Western film"),
    ],
    "A16": [
        ("A16-1", "Experimental Film", "medium",
         "avant-garde and underground films that work outside narrative convention (Terayama's <i>Emperor Tomato Ketchup</i>, Matsumoto's shorts).",
         "avant-garde film; underground film", "A1-1 Japanese New Wave.", "experimental film"),
    ],
}


# --------------------------------------------------------------------------
# Scale-up (2026-10-28): global feature-film leaves, short-film leaves, and the
# precedence sentences accepted for the scale-up (F11, F12) or found in it.
# New leaves are appended to their sub-family; pilot codes keep their meaning.

PRECEDENCE += [
    ("F11", "Pre-modern wars in Japan", "A war fought in Japan's pre-1868 past is jidaigeki or chanbara, not War Film (<i>Ran</i>, <i>Kagemusha</i>)."),
    ("F12", "Cycle before comedy", "A genre cycle wins over Comedy when the cycle's premise drives the plot (<i>Zom 100</i> → Zombie Film; <i>Shaun of the Dead</i> → Zombie Film). Comedy keeps films whose premise is only a backdrop for gags; a horror film played mainly for laughs with no cycle home is Comedy Horror."),
    ("F13", "Popular-cinema modes", "A South Asian popular star vehicle that mixes an action strand with romance, comedy, melodrama and song-and-dance is Masala Film, before the general crime, action, fantasy and historical leaves (<i>Sholay</i>, <i>Baahubali</i>, <i>Pushpa</i>). Without an action strand, a family or romance musical goes by its main line with Masala Film as see-also (<i>Dilwale Dulhania Le Jayenge</i> → Romantic Drama). A film built on one narrow premise keeps that leaf with Masala Film as see-also (heist, spy, superhero, sport, revenge: <i>Dhoom</i>, <i>Pathaan</i>, <i>Krrish</i>, <i>Dangal</i>). A Nigerian film made in the Nollywood mode is Nollywood Film unless a named genre cycle claims it. Films outside those modes (parallel cinema, art-house, realist thrillers) are placed by genre like any other film."),
    ("F14", "Biopics", "A film that tells a real person's life or career is Biographical Film whatever the person's field (musicians, athletes, criminals), unless it is mainly a war film, a sports contest or a named cycle; a dramatised single real event is placed by its genre (a heist → Heist Film; a battle → War Film)."),
    ("F15", "Superheroes", "A film whose protagonist has a costumed or super-powered heroic identity is Superhero Film, before Action, Science Fiction and Fantasy; a superhero parody stays there too. Japanese transforming heroes are Tokusatsu (F5)."),
    ("F16", "Spies", "Espionage as the plot's engine makes a Spy Film, before Action and Political Thriller (James Bond, <i>Tinker Tailor Soldier Spy</i>)."),
    ("F17", "Animation", "Every animated feature that is not Japanese animation is Animated Feature (A15), placed by technique, whatever its genre; animated documentaries are Documentary (key step 1). Genre is a see-also."),
    ("F18", "Children's and Christmas films", "A live-action film made first for children (not a family-friendly fantasy or adventure, which keep their genre) is Children's Film; a film built on Christmas is Christmas Film, before Comedy, Romance and Drama."),
    ("F19", "Road, sport and court", "A film whose structure is a journey is Road Movie, a film built on a sport and its competition is Sports Film, and a film built on a trial is Legal Drama, whether comic or dramatic, unless a named cycle claims it."),
    ("F21", "Genre films in wartime", "A war film is about the war and the soldiers' experience of it; a horror, action or thriller film that merely uses a war as its setting goes by its own genre (<i>Sisu</i> → Action Film; <i>Overlord</i> → Science Fiction Horror)."),
    ("F22", "Narrow before broad", "When a film's defining trait is named by a narrow leaf that the key reaches only later (Crime Comedy, Action Comedy, Parody & Spoof, Black Comedy & Satire, Sports Film, Dance Film, Spy Film, Road Movie), that leaf wins over the broader sub-family reached first: <i>The Olsen Gang</i> → Crime Comedy, a Karl May spoof → Parody & Spoof, a fencing biopic → Sports Film; a war satire (<i>The Great Dictator</i>, <i>Jojo Rabbit</i>) → Black Comedy & Satire; a spy comedy → Parody & Spoof when it mocks the genre (<i>Johnny English</i>, <i>Spy</i>), otherwise Action Comedy."),
    ("F23", "Subgenres are not cycles", "Subgenre leaves (vampire, zombie, slasher, haunted house, creature feature, found footage) are not named cycles for F1/D1: an attested movement member that is also a vampire film stays in the movement (<i>Nosferatu</i> → German Expressionism). Named cycles are the period- and industry-bound leaves (giallo, J-horror, poliziottesco, spaghetti western, Ostern, blaxploitation, erotic thriller ...); revisionist and neo-Western are subgenres; a later foreign remake or homage of a cycle film goes by its own genre, with the cycle as see-also (<i>The Grudge</i> 2019)."),
    ("F24", "Romance or costume", "An original love story in a period setting is Romantic Drama (<i>The English Patient</i>, <i>Portrait of a Lady on Fire</i>); Costume Drama takes the drama of manners and society, above all literary adaptations (Austen, James, Wharton, Forster: <i>A Room with a View</i>, <i>The Age of Innocence</i>). A period comedy goes by its comic mode."),
    ("F25", "Gimmick comedies", "A comedy whose fantastical or speculative premise only carries the gags is Comedy (<i>Groundhog Day</i>, <i>Multiplicity</i>, <i>Bedazzled</i>, <i>Ivan Vasilyevich Changes His Profession</i>), with the genre as see-also; a science-fiction action comedy is Action Comedy (<i>Men in Black</i>). A live-action/animation hybrid is Animated Feature only when animation carries most of the film (<i>Who Framed Roger Rabbit</i> yes, <i>Space Jam</i> yes, <i>Enchanted</i> no)."),
    ("F26", "Action vehicles", "A star vehicle carried by fights, chases and stunts is Action even when its hero is a cop or a criminal (<i>Die Hard</i>, <i>Speed</i>, <i>Cobra</i>); Crime takes films whose subject is the crime, its world or its investigation. Disaster films are A5-5 whether the catastrophe is speculative or real (<i>Airport</i>, <i>The Towering Inferno</i>, <i>Titanic</i> excepted as romance)."),
    ("F27", "Made-for-TV children's films and compilations", "A children's television film (Disney Channel and Nickelodeon originals, <i>Halloweentown</i>) is Children's Film whatever its premise; theatrical family fantasy and science fiction keep their genre (F18). A feature assembled from television episodes is excluded as a compilation (the episodes belong to their series); an animated television special under 40 minutes is B1-5."),
    ("F20", "Westerns", "A film set on the American frontier (or a transposition of its codes to another frontier — the Australian bushranger film, <i>Aferim!</i>) is a Western leaf before Action, Historical Drama and Comedy; a contemporary crime film in the West is Neo-Western only when the frontier code carries it (<i>Hell or High Water</i>, <i>No Country for Old Men</i>)."),
]

MODIFIERS += [
    "<b>Theme</b> — LGBTQ+, disability, faith, sport fandom and similar subjects are tags on any film; they become leaves only as named genres or movements (New Queer Cinema, Christian Film).",
    "<b>Era of production</b> — silent era, pre-Code Hollywood, the studio era, the Golden Age of a national cinema: filters, not leaves.",
]

_FAM_A = next(f for f in FAMILIES if f["code"] == "A")
_FAM_A["key"] = [
    "1. Non-fiction (documentary, concert film, nature film, essay film)? → <b>A13 Documentary</b>.",
    "2. Animated, and not Japanese animation? → <b>A15 Animated Feature</b> (F17).",
    "3. Does it belong to a <b>named genre cycle</b> — a narrow leaf of A2–A12, A17 or A18 (chanbara, kaidan, J-horror, yakuza, film noir, giallo, poliziottesco, blaxploitation, heroic bloodshed, wuxia, spaghetti western, pink film, kaiju, masala film ...)? → that leaf (F1, F2, F13). Otherwise, is it an <b>attested member of a named film movement</b> (Italian neorealism, the French New Wave, New Hollywood ...)? → <b>A1 Movements & Schools</b>.",
    "4. Avant-garde, working outside narrative convention (abstract, structural, surrealist)? → <b>A16 Experimental & Avant-Garde</b>.",
    "5. Is erotic display or sexual obsession the film's reason to exist? → <b>A12 Erotic Film</b>. A violent exploitation cycle with erotic elements is not: it goes on.",
    "6. Does it aim first to frighten (ghosts, monsters, killers, gore)? → <b>A4 Horror</b> (F3).",
    "7. Superheroes? → <b>A6-3</b> (F15). Speculative science — the future, technology, space, aliens, giant monsters? → <b>A5 Science Fiction & Monster</b> (F5). Magic, myth, fairy tale or a quest in perilous places? → <b>A6 Fantasy & Adventure</b>.",
    "8. The American frontier? → <b>A17 Western</b> (F20). Set in a past era that defines it, a real life, or about war? → <b>A7 Historical, Period & War</b> (F4, F11, F14).",
    "9. Made first for children, or built on Christmas? → <b>A19 Children's & Family</b> (F18).",
    "10. Espionage? → <b>A3-7 Spy Film</b> (F16). Criminals or police at the centre? → <b>A2 Crime</b>. Suspense, conspiracy or puzzle? → <b>A3 Thriller & Mystery</b> (F6).",
    "11. Fights, chases and stunts carry it? → <b>A8 Action & Martial Arts</b>.",
    "12. Songs or dance carry the story? → <b>A11 Musical & Music</b>. Laughter first? → <b>A10 Comedy</b>. A love story? → <b>A9 Romance</b>. Otherwise → <b>A14 Drama</b> (F7, F19).",
]
_FAM_A["subs"] += [
    ("A18", "Popular Cinema Modes", "Axis: the named popular-cinema mode — a production culture the field names as a genre of its own (F13)."),
    ("A19", "Children's & Family", "Axis: occasion and audience (live action)."),
]

_FAM_B = next(f for f in FAMILIES if f["code"] == "B")
_FAM_B["test"] = "a film of 40 minutes or less (the Academy's line), fiction, animation, documentary or experimental; Japanese animated shorts go to E Anime."
_FAM_B["key"] = [
    "1. Animated? → <b>B1 Animated Short</b>, by tradition and technique.",
    "2. Non-fiction (actualities, documentary shorts)? → <b>B3 Documentary & Actuality Short</b>.",
    "3. Avant-garde, outside narrative convention? → <b>B4 Experimental Short</b>.",
    "4. Otherwise live-action fiction → <b>B2 Live-Action Short</b>.",
]
_FAM_B["subs"] = [
    ("B1", "Animated Short", "Axis: tradition and technique."),
    ("B2", "Live-Action Short", "Axis: mode (trick film, silent comedy, narrative short)."),
    ("B3", "Documentary & Actuality Short", "Axis: mode."),
    ("B4", "Experimental Short", "Axis: practice."),
]


def _add(sub, rows):
    LEAVES.setdefault(sub, []).extend(rows)


# Pilot leaves whose wording was Japan-only, generalised for the global tab.
def _redef(code, **kw):
    for sub, rows in LEAVES.items():
        for i, l in enumerate(rows):
            if l[0] == code:
                f = dict(zip(("code", "label", "breadth", "defn", "aliases", "see", "attest"), l))
                f.update(kw)
                rows[i] = tuple(f[k] for k in ("code", "label", "breadth", "defn", "aliases", "see", "attest"))


_redef("A2-3", defn="films centred on police or detectives working a case (<i>Stray Dog</i>, <i>The French Connection</i>, <i>Memories of Murder</i>); buddy-cop films are A8-7.")
_redef("A2-4", defn="films about crime, its perpetrators and its effects, told as drama rather than suspense or gang epic (<i>Vengeance Is Mine</i>, <i>Dog Day Afternoon</i>, <i>City of God</i>).")
_redef("A2-5", defn="crime films in the noir manner — fatalism, low-key style, corrupt cities, the femme fatale: the American cycle of the 1940s–50s (<i>Double Indemnity</i>, <i>The Big Sleep</i>) and its later neo-noir and national forms (<i>Chinatown</i>, <i>Pale Flower</i>, <i>Branded to Kill</i>).")
_redef("A3-1", defn="suspense built on disturbed minds, obsession and manipulation (<i>Cure</i>, <i>Gone Girl</i>, <i>Black Swan</i>).")
_redef("A3-2", defn="whodunits and puzzle films built on detection, including honkaku adaptations and Agatha Christie films (<i>The Inugamis</i>, <i>Knives Out</i>).")
_redef("A3-3", defn="films in which characters are forced into a lethal contest or a fight to survive an ordeal (<i>Battle Royale</i>, <i>The Hunger Games</i>, <i>127 Hours</i>, <i>Cast Away</i>).")
_redef("A4-3", defn="horror from ghosts, demons, possession and curses outside the named cycles (<i>The Exorcist</i>, <i>Hereditary</i>, <i>House</i>).")
_redef("A5-1", defn="kaiju eiga and giant-monster films: Godzilla, Mothra, Gamera and their Hollywood and Korean kin (<i>Godzilla</i> 1954, <i>King Kong</i>, <i>The Host</i>, <i>Pacific Rim</i>).")
_redef("A5-3", defn="speculative films of the future, technology, artificial minds and alien contact outside the narrower leaves (<i>2001: A Space Odyssey</i>, <i>Arrival</i>, <i>Summer Time Machine Blues</i>).")
_redef("A6-1", defn="live-action films of magic, myth and invented worlds outside the narrower leaves (<i>Harry Potter</i>, <i>Pan's Labyrinth</i>, <i>The Great Yokai War</i>).")
_redef("A6-2", defn="journeys, quests and treasure hunts in exotic or perilous settings (<i>Raiders of the Lost Ark</i>, <i>The Mummy</i> 1999).")
_redef("A6-3", label="Superhero Film", defn="films of costumed or super-powered heroes — the Marvel and DC cycles and their kin — and live-action adaptations of power-based manga (<i>Superman</i>, <i>The Dark Knight</i>, <i>Gantz</i>, <i>Death Note</i>) (F15).",
       aliases="superhero film; comic-book film; live-action manga adaptation")
_redef("A7-4", defn="films whose past era defines them outside the narrower leaves: dramas of real events and of fictional lives in a recorded past, from the Meiji era to the twentieth century (<i>The Story of the Last Chrysanthemum</i>, <i>Titanic</i>, <i>The Last Emperor</i>); lives of real people are A7-8.",
       aliases="historical film; period film", attest="historical drama film|historical film")
_redef("A8-1", defn="films built on unarmed or weapons combat in modern or timeless settings outside chanbara, kung fu and wuxia (<i>The Street Fighter</i>, <i>The Raid</i>, <i>Ong-Bak</i>).")
_redef("A8-2", defn="films carried by fights, chases, gunplay and stunts outside the narrower leaves (<i>Die Hard</i>, <i>Mad Max: Fury Road</i>, <i>John Wick</i>).")
_redef("A9-1", defn="love stories told as drama (<i>Casablanca</i>, <i>In the Mood for Love</i>, <i>Love Letter</i>).")
_redef("A9-2", defn="love stories told for laughter (<i>When Harry Met Sally...</i>, <i>Notting Hill</i>).")
_redef("A10-1", defn="films aimed first at laughter outside the narrower leaves (<i>Groundhog Day</i>, <i>Tampopo</i>).")
_redef("A10-3", defn="comedy of death, taboo and social satire (<i>Dr. Strangelove</i>, <i>The Funeral</i>, <i>The Taste of Tea</i>).")
_redef("A11-1", label="Musical & Music Film", defn="films carried by song and music: stage and screen musicals and films about musicians and bands (<i>Singin' in the Rain</i>, <i>La La Land</i>, <i>Linda Linda Linda</i>).")
_redef("A12-3", defn="art-house and mainstream films whose subject is sexual obsession (<i>In the Realm of the Senses</i>, <i>Last Tango in Paris</i>, <i>The Housemaid</i>).")
_redef("A13-1", label="Documentary Film", defn="non-fiction films outside the narrower leaves: social, political, historical and portrait documentaries (<i>Shoah</i>, <i>Hoop Dreams</i>, <i>The Act of Killing</i>).")
_redef("A14-2", defn="dramas of families, parents and children outside the classic shomingeki (<i>Kramer vs. Kramer</i>, <i>Shoplifters</i>, <i>A Separation</i>).")
_redef("A14-3", defn="youth, school and teen films about growing up (<i>The 400 Blows</i> excepted as New Wave; <i>Stand by Me</i>, <i>Lady Bird</i>, <i>Kids Return</i>).")
_redef("A14-4", defn="dramas of social conditions, poverty, work, institutions and injustice (<i>Ikiru</i>, <i>Parasite</i>, <i>I, Daniel Blake</i>).")
_redef("A14-5", defn="dramas centred on one person's inner life, grief, solitude or change (<i>Taxi Driver</i>, <i>Drive My Car</i>, <i>Perfect Days</i>).")
_redef("A14-6", defn="emotionally heightened dramas of suffering and sacrifice, especially the women's film (Sirk, haha-mono mother films, <i>Imitation of Life</i>, <i>The Life of Oharu</i>).",
       aliases="haha-mono; women's film; weepie")
_redef("A14-7", defn="films built on a sport and its competition, comic or dramatic (<i>Rocky</i>, <i>Raging Bull</i>, <i>Moneyball</i>) (F19).")
_redef("A16-1", defn="avant-garde and underground films that work outside narrative convention (<i>Dog Star Man</i>, <i>Wavelength</i>, Terayama's <i>Emperor Tomato Ketchup</i>).")
_redef("A17-1", label="Western", defn="the classical western of the American frontier: gunfighters, cavalry, cattle drives and settlers (<i>Stagecoach</i>, <i>The Searchers</i>, <i>Rio Bravo</i>).",
       aliases="cowboy film; horse opera")

_add("A1", [
    ("A1-2", "German Expressionism", "medium",
     "the Weimar film movement of distorted sets, chiaroscuro and haunted protagonists, c. 1919–1931 (<i>The Cabinet of Dr. Caligari</i>, <i>Nosferatu</i>, <i>Metropolis</i>, <i>M</i>).",
     "Expressionist film; Weimar cinema", "A4-13 Gothic Horror; A2-5 Film Noir & Neo-Noir.", "German Expressionism"),
    ("A1-3", "Soviet Montage", "narrow",
     "the Soviet cinema of the 1920s built on montage theory — Eisenstein, Pudovkin, Vertov, Dovzhenko (<i>Battleship Potemkin</i>, <i>Strike</i>, <i>Mother</i>, <i>Earth</i>).",
     "Soviet montage cinema; montage school", "A13-7 City Symphony.", "Soviet montage theory"),
    ("A1-4", "French Impressionist Cinema", "narrow",
     "the French avant-garde narrative cinema of the 1920s — Gance, L'Herbier, Epstein, Dulac — built on subjective camera and rhythmic cutting (<i>La Roue</i>, <i>Coeur fidèle</i>, <i>The Fall of the House of Usher</i>).",
     "première vague; first French avant-garde", "A16-2 Surrealist Film.", "French Impressionist Cinema"),
    ("A1-5", "Poetic Realism", "narrow",
     "French films of the 1930s of doomed working-class lovers in fog-bound ports and back streets — Carné, Prévert, Renoir, Duvivier, Vigo (<i>Port of Shadows</i>, <i>Le jour se lève</i>, <i>L'Atalante</i>).",
     "réalisme poétique", "A2-5 Film Noir & Neo-Noir.", "poetic realism"),
    ("A1-6", "Italian Neorealism", "medium",
     "Italian films of 1943–1952 shot on location with non-professional actors about the poor and the war's aftermath — Rossellini, De Sica, Visconti, early Fellini (<i>Rome, Open City</i>, <i>Bicycle Thieves</i>, <i>La terra trema</i>, <i>Umberto D.</i>).",
     "neorealismo; Italian neo-realism", "A14-4 Social Drama.", "Italian neorealism"),
    ("A1-7", "French New Wave", "medium",
     "the Nouvelle Vague of 1958–1968: Cahiers critics turned directors — Godard, Truffaut, Chabrol, Rohmer, Rivette, Varda — with location shooting, jump cuts and personal subjects (<i>The 400 Blows</i>, <i>Breathless</i>, <i>Jules and Jim</i>, <i>Cléo from 5 to 7</i>).",
     "Nouvelle Vague", "A1-8 Left Bank.", "French New Wave"),
    ("A1-8", "Left Bank", "narrow",
     "the Rive Gauche group beside the New Wave — Resnais, Marker, Varda, Robbe-Grillet, Duras — literary, political and formally experimental (<i>Hiroshima mon amour</i>, <i>Last Year at Marienbad</i>).",
     "Rive Gauche", "A1-7 French New Wave.", "Left Bank (film)"),
    ("A1-9", "British New Wave", "narrow",
     "British films of 1959–1963 of working-class life in the industrial North, from the Angry Young Men and kitchen-sink writers (<i>Saturday Night and Sunday Morning</i>, <i>A Taste of Honey</i>, <i>This Sporting Life</i>).",
     "kitchen sink realism; British social realism", "A14-4 Social Drama.", "British New Wave|kitchen sink realism"),
    ("A1-10", "Czechoslovak New Wave", "medium",
     "Czech and Slovak films of 1963–1969 — Forman, Chytilová, Menzel, Němec, Jireš — absurdist, satirical and humane (<i>Daisies</i>, <i>Closely Watched Trains</i>, <i>The Firemen's Ball</i>, <i>Marketa Lazarová</i>).",
     "Czech New Wave; Československá nová vlna", "A10-3 Black Comedy & Satire.", "Czechoslovak New Wave"),
    ("A1-11", "Polish Film School", "narrow",
     "Polish films of 1956–1963 about the war and its moral wreckage — Wajda, Munk, Kawalerowicz, Has (<i>Kanał</i>, <i>Ashes and Diamonds</i>, <i>Eroica</i>).",
     "Polska Szkoła Filmowa", "A7-3 War Film.", "Polish Film School"),
    ("A1-12", "Yugoslav Black Wave", "narrow",
     "the critical, dark and sexually frank Yugoslav films of 1963–1972 — Makavejev, Petrović, Žilnik, Pavlović (<i>WR: Mysteries of the Organism</i>, <i>I Even Met Happy Gypsies</i>).",
     "Crni talas", "A1-10 Czechoslovak New Wave.", "Yugoslav Black Wave"),
    ("A1-13", "Cinema Novo", "medium",
     "the Brazilian movement of the 1960s–70s — Glauber Rocha, Nelson Pereira dos Santos, Joaquim Pedro de Andrade — 'an idea in the head and a camera in the hand' (<i>Black God, White Devil</i>, <i>Vidas Secas</i>, <i>Entranced Earth</i>, <i>Macunaíma</i>).",
     "Cinema Novo", "A1-14 Third Cinema.", "Cinema Novo"),
    ("A1-14", "Third Cinema", "narrow",
     "the Latin American and Third World militant cinema of the late 1960s–70s set against Hollywood and auteur cinema (<i>The Hour of the Furnaces</i>, <i>Memories of Underdevelopment</i>, <i>The Battle of Algiers</i>).",
     "Tercer Cine; Third World cinema", "A1-13 Cinema Novo.", "Third Cinema"),
    ("A1-15", "New Hollywood", "broad",
     "the American director-driven cinema of c. 1967–1980 — Penn, Altman, Coppola, Scorsese, Ashby, Malick — in the wake of the studio system (<i>Bonnie and Clyde</i>, <i>Easy Rider</i>, <i>Five Easy Pieces</i>, <i>Nashville</i>).",
     "American New Wave; Hollywood Renaissance", "A2-5 Film Noir & Neo-Noir.", "New Hollywood"),
    ("A1-16", "New German Cinema", "medium",
     "West German auteur cinema of 1962–1982 after the Oberhausen Manifesto — Fassbinder, Herzog, Wenders, Schlöndorff, von Trotta, Kluge (<i>Aguirre, the Wrath of God</i>, <i>Ali: Fear Eats the Soul</i>, <i>Kings of the Road</i>).",
     "Neuer Deutscher Film; Young German Cinema", "A1-2 German Expressionism.", "New German Cinema"),
    ("A1-17", "Parallel Cinema", "medium",
     "Indian art cinema from the 1950s — Satyajit Ray, Ritwik Ghatak, Mrinal Sen, Adoor Gopalakrishnan, Shyam Benegal — realist and outside the song-and-dance mainstream (<i>Pather Panchali</i>, <i>The Cloud-Capped Star</i>, <i>Ankur</i>).",
     "Indian New Wave; art cinema (India)", "A18-1 Masala Film.", "Parallel cinema"),
    ("A1-18", "Iranian New Wave", "medium",
     "Iranian art cinema from the late 1960s and its post-revolutionary flowering — Kiarostami, Makhmalbaf, Panahi, Majidi — with child protagonists, non-actors and fiction-documentary blends (<i>The Cow</i>, <i>Close-Up</i>, <i>Taste of Cherry</i>, <i>Children of Heaven</i>).",
     "Iranian New Wave cinema; Moj-e No", "A14-5 Character Study.", "Iranian New Wave"),
    ("A1-19", "Taiwan New Cinema", "narrow",
     "the Taiwanese New Wave of 1982–1990 — Hou Hsiao-hsien, Edward Yang — long takes and everyday history (<i>A City of Sadness</i>, <i>A Brighter Summer Day</i>, <i>The Time to Live and the Time to Die</i>).",
     "Taiwanese New Wave", "A1-20 Hong Kong New Wave.", "Taiwan New Cinema"),
    ("A1-20", "Hong Kong New Wave", "narrow",
     "the Hong Kong directors of 1979–1990 trained in television — Tsui Hark, Ann Hui, Patrick Tam, Allen Fong — and the 'second wave' of Wong Kar-wai and Stanley Kwan (<i>Boat People</i>, <i>Days of Being Wild</i>, <i>Rouge</i>).",
     "HK New Wave; Hong Kong second wave", "A8-6 Hong Kong Action Cinema.", "Hong Kong New Wave"),
    ("A1-21", "Fifth Generation", "narrow",
     "the first class after the Cultural Revolution at the Beijing Film Academy — Chen Kaige, Zhang Yimou, Tian Zhuangzhuang — allegorical rural epics of the 1980s–90s (<i>Yellow Earth</i>, <i>Red Sorghum</i>, <i>Raise the Red Lantern</i>, <i>Farewell My Concubine</i>).",
     "Chinese Fifth Generation", "A1-22 Sixth Generation.", "Fifth Generation (Chinese cinema)|Fifth Generation"),
    ("A1-22", "Sixth Generation", "narrow",
     "Chinese independent urban realism of the 1990s–2000s — Jia Zhangke, Wang Xiaoshuai, Lou Ye, Zhang Yuan (<i>Platform</i>, <i>Beijing Bicycle</i>, <i>Suzhou River</i>, <i>Still Life</i>).",
     "Urban Generation", "A1-21 Fifth Generation.", "Sixth Generation (Chinese cinema)|Sixth Generation"),
    ("A1-23", "Dogme 95", "narrow",
     "the Danish manifesto films made under the 'Vow of Chastity' — hand-held, location sound, no effects (<i>The Celebration</i>, <i>The Idiots</i>, <i>Italian for Beginners</i>).",
     "Dogma 95", "A1-27 Mumblecore.", "Dogme 95"),
    ("A1-24", "Romanian New Wave", "narrow",
     "Romanian minimalist realism from the 2000s — Puiu, Mungiu, Porumboiu, Muntean — long takes of bureaucracy and the moral afterlife of communism (<i>The Death of Mr. Lazarescu</i>, <i>4 Months, 3 Weeks and 2 Days</i>, <i>12:08 East of Bucharest</i>).",
     "Noul val românesc", "A14-4 Social Drama.", "Romanian New Wave"),
    ("A1-25", "Berlin School", "narrow",
     "the German art cinema from the late 1990s — Petzold, Arslan, Schanelec, Ade, Köhler — detached, precise and observational (<i>Barbara</i>, <i>Toni Erdmann</i>, <i>Phoenix</i>).",
     "Berliner Schule", "A1-16 New German Cinema.", "Berlin School (film)"),
    ("A1-26", "New Queer Cinema", "narrow",
     "the independent queer films of the early 1990s named by B. Ruby Rich — Haynes, Araki, Van Sant, Kalin, Jarman (<i>Poison</i>, <i>My Own Private Idaho</i>, <i>The Living End</i>, <i>Paris Is Burning</i> as documentary).",
     "Queer New Wave", "", "New Queer Cinema"),
    ("A1-27", "Mumblecore", "narrow",
     "American micro-budget films of the 2000s with naturalistic acting and improvised dialogue about twenty-somethings — the Duplass brothers, Swanberg, Bujalski, early Gerwig (<i>Funny Ha Ha</i>, <i>Hannah Takes the Stairs</i>, <i>The Puffy Chair</i>).",
     "bedhead cinema", "A1-23 Dogme 95.", "Mumblecore"),
    ("A1-28", "L.A. Rebellion", "narrow",
     "the Black filmmakers of UCLA, late 1960s–1980s — Charles Burnett, Haile Gerima, Julie Dash, Billy Woodberry (<i>Killer of Sheep</i>, <i>Bush Mama</i>, <i>Daughters of the Dust</i>).",
     "Los Angeles School of Black Filmmakers", "A1-14 Third Cinema.", "L.A. Rebellion"),
    ("A1-29", "Australian New Wave", "narrow",
     "the revival of Australian feature production c. 1970–1985 — Weir, Armstrong, Beresford, Schepisi (<i>Picnic at Hanging Rock</i>, <i>Walkabout</i>, <i>Breaker Morant</i>, <i>My Brilliant Career</i>).",
     "Australian film revival", "", "Australian New Wave"),
    ("A1-30", "Greek Weird Wave", "narrow",
     "Greek films of the late 2000s–2010s — Lanthimos, Tsangari, Avranas — deadpan, absurd and alienated (<i>Dogtooth</i>, <i>Attenberg</i>, <i>Alps</i>).",
     "Greek New Wave", "A10-3 Black Comedy & Satire.", "Greek Weird Wave"),
    ("A1-31", "New Argentine Cinema", "narrow",
     "Argentine independent cinema from the mid-1990s — Martel, Trapero, Caetano, Alonso (<i>Pizza, Beer, and Cigarettes</i>, <i>La Ciénaga</i>, <i>Nine Queens</i> excepted as heist).",
     "Nuevo cine argentino", "A1-24 Romanian New Wave.", "New Argentine Cinema"),
    ("A1-32", "Cinéma du look", "narrow",
     "French films of the 1980s with a glossy, youthful style from advertising and music video — Beineix, Besson, Carax (<i>Diva</i>, <i>Subway</i>, <i>The Lovers on the Bridge</i>, <i>Betty Blue</i>).",
     "", "A1-7 French New Wave.", "Cinéma du look"),
    ("A1-33", "Slow Cinema", "medium",
     "contemplative art cinema of long takes, minimal story and observed duration, as named by critics from the 2000s: films of its core practitioners in that mode — Tarr, Tsai Ming-liang, Lav Diaz, Weerasethakul, Alonso, Reygadas, Costa, Ceylan, Angelopoulos — and <i>Jeanne Dielman</i> (<i>Sátántangó</i>, <i>Uncle Boonmee Who Can Recall His Past Lives</i>). Precursors (Tarkovsky, Bresson, Ozu, Antonioni) carry it as see-also only; a film of a core director whose own genre is clear goes there.",
     "contemplative cinema; cinema of slowness", "A14-5 Character Study.", "slow cinema"),
    ("A1-35", "Cinema Marginal", "narrow",
     "the Brazilian underground of 1968–1973 that broke with Cinema Novo — Sganzerla, Bressane, Reichenbach (<i>The Red Light Bandit</i>, <i>Killed the Family and Went to the Movies</i>).",
     "Cinema de Boca do Lixo; Udigrudi", "A1-13 Cinema Novo.", "Cinema Marginal"),
    ("A1-34", "Korean New Wave", "narrow",
     "the socially critical South Korean films of the 1980s–90s after the end of military censorship — Park Kwang-su, Jang Sun-woo, Lee Chang-dong's debut (<i>Chilsu and Mansu</i>, <i>A Single Spark</i>, <i>Green Fish</i>).",
     "Korean New Cinema", "", "Korean New Wave"),
])

_add("A2", [
    ("A2-7", "Heist Film", "medium",
     "films built on planning and pulling off a robbery, and on its unravelling (<i>The Italian Job</i>, <i>Heat</i>, <i>Ocean's Eleven</i>, <i>Reservoir Dogs</i>; noir heists such as <i>The Asphalt Jungle</i> and <i>Rififi</i> are Film Noir by F1).",
     "caper film; heist movie", "A10-10 Crime Comedy.", "heist film"),
    ("A2-8", "Prison Film", "medium",
     "films set inside prisons and built on incarceration, its society and escape (<i>A Man Escaped</i>, <i>Escape from Alcatraz</i>, <i>The Shawshank Redemption</i>, <i>A Prophet</i>).",
     "prison drama; escape film", "A2-6 Pinky Violence.", "prison film"),
    ("A2-9", "Poliziottesco", "narrow",
     "the Italian crime cycle of the 1970s — vigilante police, kidnapping and urban violence (<i>Almost Human</i>, <i>The Big Racket</i>, <i>Rome Armed to the Teeth</i>).",
     "poliziotteschi; Euro-crime", "A3-8 Giallo.", "poliziottesco"),
    ("A2-10", "Blaxploitation", "narrow",
     "the American cycle of 1970s films with Black heroes for Black urban audiences, mostly crime and action (<i>Shaft</i>, <i>Super Fly</i>, <i>Coffy</i>, <i>Foxy Brown</i>).",
     "blaxploitation film", "A2-11 Hood Film.", "blaxploitation"),
    ("A2-12", "Cine Quinqui", "narrow",
     "the Spanish cycle of 1977–1985 about juvenile delinquents of the urban periphery, often played by non-actors (<i>Deprisa, deprisa</i>, <i>Navajeros</i>, <i>El Pico</i>).",
     "cinema quinqui", "A2-11 Hood Film.", "Cine quinqui"),
    ("A2-11", "Hood Film", "narrow",
     "American films of the 1990s and after about young Black and Latino life in inner-city neighbourhoods, gangs and violence (<i>Boyz n the Hood</i>, <i>Menace II Society</i>, <i>Juice</i>).",
     "'hood film; ghetto film", "A2-10 Blaxploitation.", "hood film"),
])

_add("A3", [
    ("A3-4", "Erotic Thriller", "narrow",
     "suspense driven by sexual desire, seduction and danger, the Hollywood cycle of the 1980s–90s and its heirs (<i>Fatal Attraction</i>, <i>Basic Instinct</i>, <i>Body Heat</i>, <i>Decision to Leave</i>).",
     "", "A12-3 Erotic Drama.", "erotic thriller"),
    ("A3-5", "Revenge Thriller", "medium",
     "suspense built on a protagonist's revenge, including rape-and-revenge and the Korean revenge cycle (<i>Oldboy</i>, <i>Sympathy for Mr. Vengeance</i>, <i>I Saw the Devil</i>, <i>Ms .45</i>).",
     "revenge film; rape and revenge", "A8-2 Action Film.", "revenge film"),
    ("A3-6", "Political & Conspiracy Thriller", "medium",
     "suspense built on state power, political violence, cover-ups and paranoia (<i>Z</i>, <i>The Parallax View</i>, <i>All the President's Men</i>, <i>The Lives of Others</i>).",
     "political thriller; paranoid thriller; conspiracy film", "A3-7 Spy Film.", "political thriller"),
    ("A3-7", "Spy Film", "medium",
     "films whose plot is driven by espionage, from the Bond cycle to Cold War realism (<i>Dr. No</i>, <i>The Spy Who Came in from the Cold</i>, <i>Tinker Tailor Soldier Spy</i>, <i>Mission: Impossible</i>) (F16).",
     "espionage film; spy thriller", "A3-6 Political & Conspiracy Thriller.", "spy film"),
    ("A3-8", "Giallo", "narrow",
     "the Italian thriller-horror cycle of the 1960s–70s: black-gloved killers, stylised murders and amateur sleuths (<i>Blood and Black Lace</i>, <i>The Bird with the Crystal Plumage</i>, <i>Deep Red</i>).",
     "gialli; giallo film", "A4-8 Slasher Film.", "giallo"),
    ("A3-9", "Suspense Thriller", "broad",
     "thrillers of an ordinary protagonist in danger — the wrong man, the stalker, the hostage, the trap — outside the narrower leaves (<i>Rear Window</i>, <i>North by Northwest</i>, <i>Duel</i>, <i>Panic Room</i>).",
     "thriller film; Hitchcockian thriller", "A3-1 Psychological Thriller.", "thriller film"),
])

_add("A4", [
    ("A4-10", "Folk Horror", "narrow",
     "horror rooted in rural isolation, pagan ritual and folklore (<i>Witchfinder General</i>, <i>The Wicker Man</i>, <i>The Witch</i>, <i>Midsommar</i>).",
     "", "A4-3 Supernatural Horror.", "folk horror"),
    ("A4-11", "Vampire Film", "narrow",
     "horror and its offshoots built on vampires (<i>Dracula</i> 1931, <i>Let the Right One In</i>, <i>Thirst</i>, <i>Near Dark</i>).",
     "vampire movie", "A4-13 Gothic Horror.", "vampire film"),
    ("A4-12", "Haunted House Film", "narrow",
     "horror of a haunted dwelling and its ghosts (<i>The Haunting</i>, <i>The Innocents</i>, <i>The Shining</i>, <i>The Conjuring</i>).",
     "haunted house movie", "A4-3 Supernatural Horror.", "haunted house film"),
    ("A4-13", "Gothic Horror", "medium",
     "horror of castles, curses and the literary monsters of the Gothic tradition: the Universal monster cycle, Hammer, the Corman–Poe cycle and Italian Gothic (<i>Frankenstein</i>, <i>The Curse of Frankenstein</i>, <i>Black Sunday</i>, <i>Crimson Peak</i>; Dracula films are A4-11).",
     "Hammer horror; Universal monsters; Italian gothic", "A4-11 Vampire Film.", "gothic horror film|Gothic film"),
    ("A4-14", "Creature Feature & Natural Horror", "medium",
     "horror of monsters, mutated beasts and nature turned killer, outside the giant kaiju (<i>Jaws</i>, <i>The Birds</i>, <i>Tremors</i>, <i>Gremlins</i>, <i>An American Werewolf in London</i>).",
     "monster movie; natural horror; werewolf film; eco-horror", "A5-1 Kaiju Film; A4-15 Science Fiction Horror.", "creature feature|natural horror film"),
    ("A4-15", "Science Fiction Horror", "medium",
     "horror whose threat comes from science, space or aliens (<i>Alien</i>, <i>The Thing</i>, <i>Invasion of the Body Snatchers</i>, <i>Event Horizon</i>, <i>The Fly</i>).",
     "sci-fi horror", "A5-8 Alien Invasion & First Contact.", "science fiction horror film|science fiction horror"),
    ("A4-16", "Comedy Horror", "medium",
     "horror played mainly for laughs, outside a named cycle (<i>The Evil Dead II</i>, <i>What We Do in the Shadows</i>, <i>Tucker & Dale vs. Evil</i>) (F12).",
     "horror comedy", "A4-6 Zombie Film.", "comedy horror"),
    ("A4-19", "Jiangshi Film", "narrow",
     "the Hong Kong cycle of hopping-corpse films, horror played with kung fu and comedy (<i>Mr. Vampire</i>, <i>Encounters of the Spooky Kind</i>, <i>Rigor Mortis</i>).",
     "hopping vampire film; geungsi film", "A4-16 Comedy Horror; A8-4 Kung Fu Film.", "Jiangshi fiction|jiangshi"),
    ("A4-20", "Home Invasion Film", "narrow",
     "horror and thrillers of a household besieged by intruders (<i>The Strangers</i>, <i>Funny Games</i>, <i>Don't Breathe</i>, <i>You're Next</i>).",
     "home invasion thriller; siege horror", "A3-9 Suspense Thriller.", "home invasion"),
    ("A4-17", "Cannibal Film", "narrow",
     "the Italian exploitation cycle of the late 1970s–early 80s set among jungle cannibals (<i>Cannibal Holocaust</i>, <i>Cannibal Ferox</i>).",
     "cannibal boom; Italian cannibal film", "A13-8 Mondo Film.", "cannibal film"),
    ("A4-18", "Asian Horror", "narrow",
     "the East and Southeast Asian supernatural horror cycles that followed J-horror — Thai, Korean, Indonesian, Malaysian, Taiwanese and Hong Kong ghost, possession and shamanic horror; as a named cycle it wins over the subgenre leaves (F2) (<i>Shutter</i>, <i>A Tale of Two Sisters</i>, <i>Satan's Slaves</i>, <i>The Eye</i>).",
     "Asian horror; K-horror; Thai horror", "A4-1 J-Horror.", "Asian horror"),
])

_add("A5", [
    ("A5-6", "Space Opera & Space Adventure", "medium",
     "adventure on an interplanetary scale: starships, galactic empires and space westerns (<i>Star Wars</i>, <i>Guardians of the Galaxy</i>, <i>Dune</i>).",
     "space opera; space western", "A6-4 High Fantasy.", "space opera"),
    ("A5-7", "Dystopian Film", "medium",
     "films of oppressive future societies (<i>Metropolis</i> excepted as Expressionism; <i>Brazil</i>, <i>Children of Men</i>, <i>Snowpiercer</i>, <i>The Hunger Games</i> excepted as survival).",
     "dystopia", "A5-5 Disaster & Post-Apocalyptic Film.", "dystopian film"),
    ("A5-8", "Alien Invasion & First Contact", "medium",
     "films of extraterrestrial invasion or contact (<i>The War of the Worlds</i>, <i>Close Encounters of the Third Kind</i>, <i>Independence Day</i>, <i>District 9</i>).",
     "alien invasion film", "A4-15 Science Fiction Horror.", "alien invasion"),
    ("A5-9", "Time Travel Film", "narrow",
     "films whose plot is built on travel in time or time loops (<i>Back to the Future</i>, <i>12 Monkeys</i>, <i>Primer</i>, <i>Groundhog Day</i> excepted as comedy).",
     "time loop film", "A5-3 Science Fiction Film.", "time travel film|time travel in fiction"),
])

_add("A6", [
    ("A6-4", "High Fantasy", "medium",
     "epic fantasy of invented worlds, quests and sword-and-sorcery (<i>The Lord of the Rings</i>, <i>Conan the Barbarian</i>, <i>The NeverEnding Story</i>).",
     "epic fantasy; sword and sorcery", "A6-1 Fantasy Film.", "high fantasy"),
    ("A6-5", "Fairy-Tale Film", "narrow",
     "live-action films of fairy tales and their retellings (<i>Beauty and the Beast</i> 1946, <i>The Princess Bride</i>, <i>Three Wishes for Cinderella</i>).",
     "fairy tale film", "A15 Animated Feature.", "fairy tale film"),
    ("A6-6", "Swashbuckler", "medium",
     "adventure of sword-fighting heroes — pirates, musketeers, outlaws (<i>The Adventures of Robin Hood</i>, <i>The Three Musketeers</i>, <i>Pirates of the Caribbean</i>).",
     "swashbuckler film; cloak-and-dagger; pirate film", "A7-6 Sword-and-Sandal Film.", "swashbuckler film"),
])

_add("A7", [
    ("A7-6", "Sword-and-Sandal Film", "medium",
     "epics of the ancient and biblical world, including the Italian peplum (<i>Ben-Hur</i>, <i>Spartacus</i>, <i>The Ten Commandments</i>, <i>Hercules</i> 1958, <i>Gladiator</i>).",
     "peplum; biblical epic", "A6-6 Swashbuckler.", "sword-and-sandal"),
    ("A7-7", "Costume Drama", "medium",
     "dramas of manners in a period setting, often literary adaptations and heritage films (<i>Barry Lyndon</i>, <i>The Age of Innocence</i>, <i>Pride & Prejudice</i>, <i>The Leopard</i>).",
     "period drama; heritage film", "A9-1 Romantic Drama.", "costume drama"),
    ("A7-8", "Biographical Film", "broad",
     "films that tell a real person's life or career (<i>Lawrence of Arabia</i>, <i>Gandhi</i>, <i>Amadeus</i>, <i>The Social Network</i>) (F14).",
     "biopic; biographical drama", "A7-4 Historical Drama.", "biographical film"),
    ("A7-9", "Holocaust Film", "narrow",
     "fiction films about the Nazi persecution and murder of the Jews (<i>Schindler's List</i>, <i>The Pianist</i>, <i>Son of Saul</i>, <i>The Zone of Interest</i>).",
     "", "A7-3 War Film; A13-1 Documentary Film.", "Holocaust film"),
    ("A7-10", "Partisan Film", "narrow",
     "Yugoslav, Albanian and other Eastern-bloc films of the Second World War partisan resistance (<i>The Battle of Neretva</i>, <i>Walter Defends Sarajevo</i>, <i>Red Poppies on the Wall</i>; <i>Come and See</i> excepted as war).",
     "partizanski film", "A7-3 War Film.", "partisan film"),
])

_add("A8", [
    ("A8-3", "Wuxia", "medium",
     "Chinese films of martial-arts chivalry: wandering swordsmen and women of the jianghu with gravity-defying combat (<i>Come Drink with Me</i>, <i>A Touch of Zen</i>, <i>Crouching Tiger, Hidden Dragon</i>, <i>Hero</i>).",
     "wuxia pian; swordplay film", "A8-4 Kung Fu Film; A7-2 Chanbara.", "wuxia"),
    ("A8-4", "Kung Fu Film", "medium",
     "Hong Kong and Chinese unarmed martial-arts films, from Shaw Brothers and Bruce Lee to Jackie Chan and Ip Man (<i>Enter the Dragon</i>, <i>The 36th Chamber of Shaolin</i>, <i>Drunken Master</i>, <i>Ip Man</i>).",
     "kung fu movie; chopsocky", "A8-3 Wuxia; A8-1 Martial Arts Film.", "kung fu film"),
    ("A8-5", "Heroic Bloodshed", "narrow",
     "the Hong Kong gunplay cycle of the late 1980s–90s: brotherhood, honour and balletic shoot-outs (<i>A Better Tomorrow</i>, <i>The Killer</i>, <i>Hard Boiled</i>).",
     "gun fu", "A8-6 Hong Kong Action Cinema.", "heroic bloodshed"),
    ("A8-6", "Hong Kong Action Cinema", "medium",
     "Hong Kong stunt-driven action outside kung fu, wuxia and heroic bloodshed: police action, girls-with-guns and the Milkyway crime-action films (<i>Police Story</i>, <i>Project A</i>, <i>Exiled</i>).",
     "Hong Kong action film", "A8-5 Heroic Bloodshed.", "Hong Kong action cinema"),
    ("A8-7", "Buddy Cop Film", "narrow",
     "action films of two mismatched police partners (<i>48 Hrs.</i>, <i>Lethal Weapon</i>, <i>Rush Hour</i>, <i>Hot Fuzz</i>).",
     "buddy cop", "A2-3 Police & Detective Film.", "buddy cop film"),
])

_add("A10", [
    ("A10-4", "Screwball Comedy", "narrow",
     "the fast-talking romantic comedies of the 1930s–40s, American above all, and their European kin, battle of the sexes and comedy of remarriage (<i>It Happened One Night</i>, <i>Bringing Up Baby</i>, <i>His Girl Friday</i>).",
     "comedy of remarriage", "A9-2 Romantic Comedy.", "screwball comedy"),
    ("A10-5", "Slapstick Comedy", "medium",
     "physical comedy of pratfalls, chases and sight gags, from the silent clowns to Tati and Mr. Bean (<i>The General</i>, <i>City Lights</i>, <i>Duck Soup</i>, <i>Playtime</i>).",
     "silent comedy; physical comedy", "A10-1 Comedy Film.", "slapstick"),
    ("A10-6", "Parody & Spoof", "medium",
     "comedy that mocks a genre or a famous work (<i>Airplane!</i>, <i>Young Frankenstein</i>, <i>Monty Python and the Holy Grail</i>, <i>Scary Movie</i>).",
     "spoof film; parody film", "A10-11 Mockumentary.", "parody film"),
    ("A10-7", "Teen & Sex Comedy", "medium",
     "comedy of adolescence, parties and sexual initiation (<i>Animal House</i>, <i>Fast Times at Ridgemont High</i>, <i>American Pie</i>, <i>Superbad</i>).",
     "teen comedy; sex comedy; gross-out comedy", "A14-3 Coming-of-Age Film.", "teen comedy|sex comedy"),
    ("A10-8", "Commedia all'italiana", "narrow",
     "Italian comedy of 1958–1980 that satirised postwar society — Monicelli, Risi, Germi, Scola (<i>Big Deal on Madonna Street</i>, <i>Divorce Italian Style</i>, <i>Il Sorpasso</i>).",
     "Italian-style comedy", "A10-3 Black Comedy & Satire.", "Commedia all'italiana"),
    ("A10-9", "Action Comedy", "medium",
     "comedy carried by action set pieces outside the buddy-cop cycle (<i>Beverly Hills Cop</i>, <i>The Nice Guys</i>, <i>Kung Fu Hustle</i>).",
     "", "A8-7 Buddy Cop Film.", "action comedy film"),
    ("A10-10", "Crime Comedy", "medium",
     "comedy of criminals, capers and botched crimes (<i>The Ladykillers</i>, <i>A Fish Called Wanda</i>, <i>Snatch</i>, <i>The Big Lebowski</i>).",
     "caper comedy", "A2-7 Heist Film.", "crime comedy film|crime comedy"),
    ("A10-11", "Mockumentary", "narrow",
     "fiction comedy in the form of a documentary (<i>This Is Spinal Tap</i>, <i>Best in Show</i>, <i>Borat</i>).",
     "mock documentary", "A10-6 Parody & Spoof.", "mockumentary"),
    ("A10-13", "Bourekas Film", "narrow",
     "the Israeli comedy and melodrama cycle of the 1960s–70s built on Mizrahi–Ashkenazi ethnic stereotypes (<i>Sallah Shabati</i>, <i>Snooker</i>, <i>Charlie and a Half</i>).",
     "bourekas", "A10-1 Comedy Film.", "Bourekas film"),
    ("A10-12", "Stand-Up Comedy Film", "narrow",
     "recorded stand-up comedy performances released as films or specials (<i>Richard Pryor: Live in Concert</i>, <i>Eddie Murphy Raw</i>, <i>Nanette</i>).",
     "stand-up special; comedy special", "A13-2 Concert & Music Documentary.", "stand-up comedy"),
])

_add("A11", [
    ("A11-2", "Dance Film", "narrow",
     "films built on dance and dancers, competitions and the dance floor (<i>The Red Shoes</i>, <i>Saturday Night Fever</i>, <i>Dirty Dancing</i>, <i>Step Up</i>).",
     "dance movie", "A11-1 Musical & Music Film.", "dance film"),
])

_add("A12", [
    ("A12-4", "Sexploitation", "narrow",
     "low-budget softcore features made for sex appeal outside Japan — nudie-cuties, Russ Meyer, Euro-softcore (<i>Faster, Pussycat! Kill! Kill!</i>, <i>Emmanuelle</i>, <i>Vixen!</i>).",
     "softcore film; sexploitation film", "A12-1 Pink Film.", "sexploitation film"),
    ("A12-5", "Pornographic Film", "narrow",
     "hardcore features, chiefly of the Golden Age of Porn (1969–1984) that reached mainstream cinemas (<i>Deep Throat</i>, <i>Behind the Green Door</i>, <i>The Devil in Miss Jones</i>).",
     "Golden Age of Porn; porno chic", "A12-4 Sexploitation.", "pornographic film"),
])

_add("A13", [
    ("A13-2", "Concert & Music Documentary", "medium",
     "documentaries of musicians, concerts and festivals (<i>Woodstock</i>, <i>Stop Making Sense</i>, <i>The Last Waltz</i>, <i>Summer of Soul</i>).",
     "concert film; rockumentary", "A11-1 Musical & Music Film.", "concert film"),
    ("A13-3", "Nature Documentary", "narrow",
     "documentaries of wildlife and the natural world (<i>Microcosmos</i>, <i>March of the Penguins</i>, <i>My Octopus Teacher</i>).",
     "wildlife documentary", "", "nature documentary"),
    ("A13-4", "Direct Cinema & Cinéma Vérité", "narrow",
     "observational documentaries of the 1960s–70s with light cameras and synchronous sound (<i>Primary</i>, <i>Salesman</i>, <i>Grey Gardens</i>, <i>Chronicle of a Summer</i>).",
     "cinéma vérité; observational documentary; direct cinema", "A13-1 Documentary Film.", "direct cinema|cinéma vérité"),
    ("A13-5", "True Crime Documentary", "narrow",
     "documentaries investigating real crimes and miscarriages of justice (<i>The Thin Blue Line</i>, <i>Paradise Lost</i>, <i>Capturing the Friedmans</i>).",
     "true crime", "A2-4 Crime Drama.", "true crime"),
    ("A13-6", "Essay Film", "narrow",
     "personal, reflective non-fiction that argues and wanders (<i>Night and Fog</i>, <i>Sans Soleil</i>, <i>F for Fake</i>, <i>The Gleaners and I</i>).",
     "film essay", "A16-1 Experimental Film.", "essay film"),
    ("A13-7", "City Symphony", "narrow",
     "1920s–30s documentaries that render a city's day as visual rhythm (<i>Berlin: Symphony of a Metropolis</i>, <i>Man with a Movie Camera</i>, <i>Manhatta</i>).",
     "city symphony film", "A1-3 Soviet Montage.", "city symphony"),
    ("A13-8", "Mondo Film", "narrow",
     "Italian-born shockumentaries of bizarre customs and violence, 1962 onward (<i>Mondo Cane</i>, <i>Africa Addio</i>, <i>Faces of Death</i>).",
     "shockumentary", "A4-17 Cannibal Film.", "mondo film"),
    ("A13-9", "Ethnographic Film", "narrow",
     "documentaries of peoples and cultures made from fieldwork (<i>Nanook of the North</i>, <i>Moi, un noir</i>, <i>Dead Birds</i>).",
     "visual anthropology", "A13-4 Direct Cinema & Cinéma Vérité.", "ethnographic film"),
])

_add("A14", [
    ("A14-10", "Legal Drama", "medium",
     "dramas built on a trial, a lawyer's case or a jury (<i>12 Angry Men</i>, <i>To Kill a Mockingbird</i>, <i>Anatomy of a Murder</i>, <i>Anatomy of a Fall</i>) (F19).",
     "courtroom drama; legal film", "A13-5 True Crime Documentary.", "legal drama|courtroom drama"),
    ("A14-11", "Road Movie", "medium",
     "films whose structure is a journey on the road, comic or dramatic (<i>Easy Rider</i> excepted as New Hollywood; <i>Thelma & Louise</i>, <i>Paris, Texas</i>, <i>Wild Strawberries</i>, <i>Y tu mamá también</i>) (F19).",
     "road film", "A14-3 Coming-of-Age Film.", "road movie"),
    ("A14-14", "Banlieue Film", "narrow",
     "French films of the multi-ethnic housing estates on the cities' edge, their youth, police and violence (<i>La Haine</i>, <i>Girlhood</i>, <i>Divines</i>, <i>Les Misérables</i> 2019).",
     "cinéma de banlieue", "A2-11 Hood Film; A14-4 Social Drama.", "Banlieue film|cinéma de banlieue"),
    ("A14-12", "Christian Film", "narrow",
     "films made by and for Christian audiences, of conversion and faith (<i>The Passion of the Christ</i> excepted as biblical epic; <i>God's Not Dead</i>, <i>Fireproof</i>).",
     "faith-based film", "A7-6 Sword-and-Sandal Film.", "Christian film"),
    ("A14-13", "Political Drama", "medium",
     "dramas of politics and power, of leaders, campaigns and activists, outside the thriller (<i>Mr. Smith Goes to Washington</i>, <i>The Candidate</i>, <i>Milk</i> excepted as biopic, <i>Battle of Algiers</i> excepted as Third Cinema).",
     "political film", "A3-6 Political & Conspiracy Thriller.", "political drama|political film"),
])

_add("A15", [
    ("A15-1", "Hand-Drawn Animated Feature", "broad",
     "two-dimensional features animated by hand on cels or paper, or drawn digitally in 2D (Flash, Toon Boom, digital cut-out silhouettes), the Disney tradition and its rivals and the European, Soviet and Chinese studios (<i>Snow White and the Seven Dwarfs</i>, <i>The Lion King</i>, <i>The Snow Queen</i>, <i>The Triplets of Belleville</i>).",
     "traditional animation; cel animation", "A15-2 Computer-Animated Feature.", "traditional animation"),
    ("A15-2", "Computer-Animated Feature", "broad",
     "features made with 3D computer animation, from <i>Toy Story</i> (1995) on: Pixar, DreamWorks, Disney and their peers (<i>Shrek</i>, <i>Spider-Man: Into the Spider-Verse</i>, <i>Ne Zha</i>).",
     "CGI animation; 3D animation", "A15-1 Hand-Drawn Animated Feature.", "computer animation"),
    ("A15-3", "Stop-Motion Feature", "medium",
     "features animated frame by frame with puppets, clay or cut-outs (<i>The Nightmare Before Christmas</i>, <i>Coraline</i>, <i>Chicken Run</i>, <i>Fantastic Mr. Fox</i>).",
     "stop-motion animation; claymation; puppet animation", "B1-3 Stop-Motion & Puppet Short.", "stop-motion animation|stop motion"),
    ("A15-4", "Adult Animated Feature", "medium",
     "animated features made for adults — satire, sex, politics, memoir — whatever the technique (<i>Fritz the Cat</i>, <i>Persepolis</i>, <i>Anomalisa</i>, <i>Flee</i> excepted as documentary).",
     "adult animation", "A15-1 Hand-Drawn Animated Feature.", "adult animation"),
])

_add("A16", [
    ("A16-2", "Surrealist Film", "narrow",
     "films of the surrealist movement and its heirs, dream logic and provocation (<i>L'Âge d'Or</i>, <i>The Discreet Charm of the Bourgeoisie</i>, <i>Eraserhead</i>, <i>The Holy Mountain</i>).",
     "surrealist cinema", "A16-1 Experimental Film.", "surrealist film|surrealist cinema"),
])

_add("A17", [
    ("A17-2", "Spaghetti Western", "medium",
     "Italian westerns of 1964–1978 — Leone, Corbucci, Sollima — with mercenary heroes, operatic violence and Morricone scores (<i>A Fistful of Dollars</i>, <i>The Good, the Bad and the Ugly</i>, <i>Django</i>, <i>Once Upon a Time in the West</i>).",
     "Italian western; macaroni western", "A17-3 Revisionist Western.", "spaghetti western"),
    ("A17-3", "Revisionist Western", "medium",
     "westerns that question the genre's myths — violence, race, the frontier (<i>The Wild Bunch</i>, <i>McCabe & Mrs. Miller</i>, <i>Little Big Man</i>, <i>Unforgiven</i>).",
     "anti-western; acid western", "A17-1 Western.", "revisionist Western"),
    ("A17-4", "Neo-Western", "medium",
     "films set in the modern American West that carry the western's codes (<i>Lonely Are the Brave</i>, <i>No Country for Old Men</i>, <i>Hell or High Water</i>, <i>Brokeback Mountain</i> excepted as romance) (F20).",
     "contemporary western; modern western", "A2-5 Film Noir & Neo-Noir.", "neo-Western"),
    ("A17-5", "Ostern", "narrow",
     "Soviet and East German westerns and 'Eastern' adventures (<i>White Sun of the Desert</i>, <i>The Sons of Great Bear</i>).",
     "Red western; Indianerfilm; Eastern", "A17-2 Spaghetti Western.", "Ostern"),
])

_add("A18", [
    ("A18-1", "Masala Film", "medium",
     "South Asian popular cinema that mixes action, romance, comedy, melodrama and song-and-dance in one star vehicle — the Hindi, Telugu, Tamil and other Indian industries, and the same mode in Bangladesh (Dhallywood) and Pakistan (Lollywood) (<i>Sholay</i>, <i>Amar Akbar Anthony</i>, <i>Baahubali</i>, <i>RRR</i>, <i>Pushpa</i>) (F13).",
     "masala movie; Bollywood masala; mass film", "A1-17 Parallel Cinema; A11-1 Musical & Music Film.", "masala film"),
    ("A18-2", "Nollywood Film", "narrow",
     "Nigerian popular film made in the Nollywood mode: the home-video melodramas of family, wealth, the occult and the city from <i>Living in Bondage</i> (1992), and the 'New Nollywood' cinema releases that grew from them (<i>The Wedding Party</i>, <i>King of Boys</i>) (F13).",
     "Nigerian video film; New Nollywood", "A18-1 Masala Film.", "Nollywood|Cinema of Nigeria"),
])

_add("A18", [
    ("A18-3", "Yeşilçam Film", "medium",
     "Turkish popular cinema of the Istanbul studios, c. 1950–1990: star melodramas, comedies and adventure films made fast for a mass audience (<i>Hababam Sınıfı</i>, <i>Selvi Boylum Al Yazmalım</i>, <i>Tosun Paşa</i>).",
     "Yeşilçam", "A18-1 Masala Film.", "Yeşilçam"),
])
_add("A11", [
    ("A11-3", "Rumberas Film", "narrow",
     "the Mexican cabaret melodrama of the 1940s–50s built on rumba dancers and the nightclub (<i>Aventurera</i>, <i>Victims of Sin</i>).",
     "cabaretera film; cine de rumberas", "A14-6 Melodrama; A11-2 Dance Film.", "Rumberas film"),
])
_add("A1", [
    ("A1-40", "No Wave Cinema", "narrow",
     "the underground film scene of downtown New York, c. 1976–1985, beside No Wave music — Amos Poe, Beth B, Vivienne Dick, early Jarmusch (<i>Smithereens</i>, <i>Born in Flames</i>, <i>Stranger Than Paradise</i>, <i>Permanent Vacation</i>).",
     "No Wave film", "A1-36 New American Cinema; A16-1 Experimental Film.", "No Wave Cinema"),
    ("A1-37", "Cinema of Moral Anxiety", "narrow",
     "Polish films of 1976–1981 on moral compromise under late communism — Kieślowski, Zanussi, Holland, Wajda (<i>Camera Buff</i>, <i>Man of Marble</i>, <i>Camouflage</i>).",
     "Kino moralnego niepokoju", "A1-11 Polish Film School.", "Cinema of moral anxiety"),
    ("A1-38", "Portuguese New Cinema", "narrow",
     "the Novo Cinema of the 1960s–70s that broke with the Estado Novo's studio films — Paulo Rocha, Fernando Lopes, António de Macedo (<i>The Green Years</i>, <i>Change of Life</i>, <i>Belarmino</i>).",
     "Novo Cinema; Cinema Novo (Portugal)", "A1-13 Cinema Novo.", "Novo Cinema"),
    ("A1-39", "Second Golden Age of Philippine Cinema", "narrow",
     "the Filipino auteur cinema of the 1970s–early 80s under martial law — Lino Brocka, Ishmael Bernal, Mike de Leon (<i>Manila in the Claws of Light</i>, <i>Insiang</i>, <i>Himala</i>).",
     "Philippine New Wave (1970s)", "A14-4 Social Drama.", "Second golden age of Philippine cinema"),
    ("A1-36", "New American Cinema", "narrow",
     "the American independent and underground film movement of the late 1950s–60s around the New American Cinema Group and the Film-Makers' Cooperative — Cassavetes, Frank, Mekas, Clarke (<i>Shadows</i>, <i>Pull My Daisy</i>, <i>The Connection</i>).",
     "New American Cinema Group; American underground film", "A1-15 New Hollywood; A16-1 Experimental Film.", "New American Cinema"),
])
_add("A19", [
    ("A19-1", "Children's Film", "medium",
     "live-action films made first for children (<i>The Wizard of Oz</i> excepted as fantasy; <i>Mary Poppins</i> excepted as musical; <i>Matilda</i>, <i>Paddington</i>, <i>Kes</i> excepted as drama).",
     "family film; kids' film", "A6-1 Fantasy Film; A14-8 Animal Film.", "children's film"),
    ("A19-2", "Christmas Film", "medium",
     "films built on Christmas, comic, romantic or dramatic (<i>It's a Wonderful Life</i>, <i>Miracle on 34th Street</i>, <i>Home Alone</i>, <i>Elf</i>) (F18).",
     "holiday film", "A19-1 Children's Film.", "Christmas film"),
])

_add("B1", [
    ("B1-1", "Theatrical Cartoon", "medium",
     "studio cartoon shorts made for cinema programmes, the golden age of American animation and its kin (Disney's <i>Silly Symphonies</i>, Looney Tunes, <i>Tom and Jerry</i>, Fleischer's <i>Betty Boop</i>).",
     "cartoon short; animated short subject", "A15-1 Hand-Drawn Animated Feature.", "animated cartoon|animated short film"),
    ("B1-2", "Auteur Animated Short", "medium",
     "independent and art animation shorts by individual animators and national studios — NFB, Soyuzmultfilm, Zagreb School (<i>Neighbours</i>, <i>Hedgehog in the Fog</i>, <i>The Man Who Planted Trees</i>).",
     "independent animation; art animation", "B4-1 Avant-Garde Short.", "independent animation"),
    ("B1-3", "Stop-Motion & Puppet Short", "narrow",
     "shorts animated with puppets, clay or objects (<i>A Grand Day Out</i>, <i>The Wrong Trousers</i>, <i>Dimensions of Dialogue</i>).",
     "claymation short", "A15-3 Stop-Motion Feature.", "stop-motion animation"),
    ("B1-4", "Computer-Animated Short", "narrow",
     "shorts made with 3D computer animation (<i>Luxo Jr.</i>, <i>Geri's Game</i>, <i>Bao</i>).",
     "CGI short; Pixar short", "A15-2 Computer-Animated Feature.", "computer animation"),
])

_add("B1", [
    ("B1-5", "Animated Television Special", "narrow",
     "animated specials made for television broadcast, chiefly holiday specials (<i>A Charlie Brown Christmas</i>, <i>How the Grinch Stole Christmas!</i>, <i>Rudolph the Red-Nosed Reindeer</i>).",
     "TV special (animated); holiday special", "B1-1 Theatrical Cartoon.", "television special"),
])
_add("B2", [
    ("B2-1", "Trick Film", "narrow",
     "early fantasy shorts built on camera tricks and stage illusion, Méliès and his rivals (<i>A Trip to the Moon</i>, <i>The Haunted Castle</i>).",
     "féerie; trick film", "B3-1 Actuality Film.", "trick film"),
    ("B2-2", "Silent Comedy Short", "medium",
     "one- and two-reel comedies of the silent clowns and the early sound comedy teams (<i>One Week</i>, <i>The Immigrant</i>, Laurel and Hardy's <i>The Music Box</i>).",
     "slapstick short; comedy short", "A10-5 Slapstick Comedy.", "comedy short"),
    ("B2-3", "Narrative Short Film", "broad",
     "live-action fiction shorts of every genre (<i>La Jetée</i>, <i>The Red Balloon</i>, <i>Six Shooter</i>).",
     "short film; short subject", "", "short film"),
])

_add("B3", [
    ("B3-1", "Actuality Film", "narrow",
     "the non-fiction views of early cinema, 1890s–1900s (<i>Workers Leaving the Lumière Factory</i>, <i>The Arrival of a Train</i>, <i>Carmencita</i>).",
     "actualité; actuality", "B2-1 Trick Film.", "actuality film"),
    ("B3-2", "Documentary Short", "medium",
     "documentaries under 40 minutes (<i>Night and Fog</i>, <i>Glass</i>, <i>The Silent World</i> excepted as feature).",
     "short documentary", "A13-1 Documentary Film.", "short documentary film|documentary film"),
])

_add("B4", [
    ("B4-1", "Avant-Garde Short", "medium",
     "experimental and avant-garde shorts — surrealist, abstract, structural and underground (<i>Un Chien Andalou</i>, <i>Meshes of the Afternoon</i>, <i>Scorpio Rising</i>, <i>Window Water Baby Moving</i>).",
     "experimental short film", "A16-1 Experimental Film.", "experimental film|avant-garde film"),
])


# Attestation for leaves: English Wikipedia article titles (resolved to their
# Wikidata item by build), then a QID where the article is a redirect, then a
# source page. A leaf with none of these carries a weak-attestation note.
ATTEST_WIKI = {
"A1-1":"Japanese New Wave","A1-2":"German expressionist cinema","A1-3":"Soviet montage theory","A1-4":"French impressionist cinema",
"A1-5":"Poetic realism","A1-6":"Italian neorealism","A1-7":"French New Wave","A1-8":"Left Bank (film)|Left Bank (film movement)|Rive Gauche (film)",
"A1-9":"British New Wave","A1-10":"Czechoslovak New Wave","A1-11":"Polish Film School","A1-12":"Yugoslav Black Wave","A1-13":"Cinema Novo",
"A1-14":"Third Cinema","A1-15":"New Hollywood","A1-16":"New German Cinema","A1-17":"Parallel cinema","A1-18":"Iranian New Wave",
"A1-19":"Taiwanese New Wave|Taiwan New Cinema","A1-20":"Hong Kong New Wave","A1-21":"Fifth Generation (Chinese cinema)|Fifth generation of Chinese filmmakers",
"A1-22":"Sixth Generation (Chinese cinema)|Sixth generation of Chinese filmmakers","A1-23":"Dogme 95","A1-24":"Romanian New Wave",
"A1-25":"Berlin School (filmmaking)|Berlin School (film)","A1-26":"New Queer Cinema","A1-27":"Mumblecore","A1-28":"L.A. Rebellion",
"A1-29":"Australian New Wave","A1-30":"Greek Weird Wave","A1-31":"New Argentine Cinema|Nuevo cine argentino","A1-32":"Cinéma du look",
"A1-33":"Slow cinema","A1-34":"Korean New Wave","A1-35":"Cinema Marginal|Brazilian marginal cinema","A1-36":"New American Cinema Group|New American Cinema","A1-37":"Cinema of moral anxiety","A1-40":"No Wave Cinema|No wave","A1-38":"Novo Cinema","A1-39":"Philippine cinema|Cinema of the Philippines","A18-3":"Yeşilçam","A11-3":"Rumberas film","A2-12":"Cine quinqui",
"A2-1":"Yakuza film","A2-2":"Gangster film","A2-3":"Police procedural","A2-4":"Crime film","A2-5":"Film noir","A2-6":"Pinky violence",
"A2-7":"Heist film","A2-8":"Prison film","A2-9":"Poliziotteschi","A2-10":"Blaxploitation","A2-11":"Hood film",
"A3-1":"Psychological thriller","A3-2":"Mystery film","A3-3":"Survival film","A3-4":"Erotic thriller","A3-5":"Revenge film|Rape and revenge film",
"A3-6":"Political thriller","A3-7":"Spy film","A3-8":"Giallo","A3-9":"Thriller film",
"A4-1":"Japanese horror","A4-2":"Kaidan","A4-3":"Supernatural horror film","A4-4":"Body horror","A4-5":"Splatter film","A4-6":"Zombie film",
"A4-7":"Found footage (film technique)|Found footage film","A4-8":"Slasher film","A4-9":"Psychological horror","A4-10":"Folk horror",
"A4-11":"Vampire film","A4-12":"Haunted house film|Haunted house","A4-13":"Gothic film|Gothic horror","A4-14":"Monster movie|Natural horror film|Creature feature",
"A4-15":"Science fiction horror film|Science fiction horror","A4-16":"Comedy horror","A4-17":"Cannibal film","A4-20":"Home invasion","A4-19":"Jiangshi fiction|Jiangshi","A4-18":"Asian horror|Korean horror|Thai horror",
"A5-1":"Kaiju","A5-2":"Tokusatsu","A5-3":"Science fiction film","A5-4":"Cyberpunk","A5-5":"Disaster film","A5-6":"Space opera",
"A5-7":"Dystopian film|Utopian and dystopian fiction","A5-8":"Alien invasion","A5-9":"Time travel in fiction",
"A6-1":"Fantasy film","A6-2":"Adventure film","A6-3":"Superhero film","A6-4":"High fantasy","A6-5":"Fairy tale film|Fairy-tale fantasy","A6-6":"Swashbuckler film",
"A7-1":"Jidaigeki","A7-2":"Samurai cinema","A7-3":"War film","A7-4":"Historical drama","A7-5":"Hibakusha cinema|Hibakusha","A7-6":"Sword-and-sandal",
"A7-7":"Costume drama","A7-8":"Biographical film","A7-9":"Holocaust film|The Holocaust in film|Holocaust films","A7-10":"Partisan film",
"A8-1":"Martial arts film","A8-2":"Action film","A8-3":"Wuxia","A8-4":"Kung fu film","A8-5":"Heroic bloodshed","A8-6":"Hong Kong action cinema","A8-7":"Buddy cop",
"A9-1":"Romance film","A9-2":"Romantic comedy",
"A10-1":"Comedy film","A10-2":"Comedy drama","A10-3":"Black comedy","A10-4":"Screwball comedy","A10-5":"Slapstick","A10-6":"Parody film",
"A10-7":"Teen film|Sex comedy","A10-8":"Commedia all'italiana","A10-9":"Action comedy","A10-10":"Crime comedy","A10-11":"Mockumentary","A10-12":"Stand-up comedy",
"A11-1":"Musical film","A11-2":"Dance film",
"A12-1":"Pink film","A12-2":"Roman Porno|Nikkatsu Roman Porno","A12-3":"Erotic film","A12-4":"Sexploitation film","A12-5":"Golden Age of Porn|Pornographic film",
"A13-1":"Documentary film","A13-2":"Concert film","A13-3":"Nature documentary","A13-4":"Direct cinema","A13-5":"True crime","A13-6":"Essay film|Film essay",
"A13-7":"City symphony","A13-8":"Mondo film","A13-9":"Ethnographic film",
"A14-1":"Shomin-geki|Shoshimin-eiga","A14-2":"Family film|Domestic drama","A14-3":"Coming-of-age story|Coming-of-age film","A14-4":"Social problem film",
"A14-5":"Character study|Psychological drama","A14-6":"Melodrama","A14-7":"Sports film","A14-8":"Animal film|List of films about animals",
"A14-9":"Taiyozoku|Taiyōzoku","A14-10":"Legal drama","A14-11":"Road movie","A14-12":"Christian film","A14-14":"Banlieue film|Cinéma de banlieue","A10-13":"Bourekas film","A14-13":"Political drama|Political film",
"A15-1":"Traditional animation","A15-2":"Computer animation","A15-3":"Stop motion","A15-4":"Adult animation",
"A16-1":"Experimental film","A16-2":"Surrealist cinema",
"A17-1":"Western film","A17-2":"Spaghetti Western","A17-3":"Revisionist Western","A17-4":"Contemporary Western|Neo-Western","A17-5":"Ostern",
"A18-1":"Masala film","A18-2":"Nollywood","A19-1":"Children's film","A19-2":"Christmas film|Christmas movie",
"B1-1":"Animated cartoon","B1-2":"Independent animation","B1-3":"Stop motion","B1-4":"Computer animation","B1-5":"Television special","B2-1":"Trick film",
"B2-2":"Silent comedy|Slapstick film|Comedy short","B2-3":"Short film","B3-1":"Actuality film","B3-2":"Short documentary film|Documentary film","B4-1":"Experimental film",
}
ATTEST_QID = {"A1-30": "Q62086465", "A1-31": "Q2843729", "A10-10": "Q1788980", "A12-2": "Q11237516", "A3-5": "Q2254193"}
ATTEST_URLS = {
    "A1-21": "https://en.wikipedia.org/wiki/Cinema_of_China#The_fifth_generation",
    "A1-22": "https://en.wikipedia.org/wiki/Cinema_of_China#The_sixth_generation",
    "A1-34": "https://harvardfilmarchive.org/programs/park-kwang",
    "A4-15": "https://en.wikipedia.org/wiki/List_of_science_fiction_horror_films",
    "A7-9": "https://en.wikipedia.org/wiki/List_of_Holocaust_films",
    "A10-3": "https://en.wikipedia.org/wiki/Black_comedy",
}
WEAK = {
    "A2-6": "no Wikidata item; attested in Toei's own cycle name and the pink-film literature",
    "A3-5": "attested as 'rape and revenge' (Wikidata) and as a Korean cycle in criticism; no item for 'revenge thriller'",
    "A4-18": "attested through Korean horror and Thai horror; no item for the umbrella term",
    "A6-5": "attested as a film form in the fairy-tale literature (Zipes); no item for 'fairy-tale film'",
    "A14-9": "no Wikidata item; attested in Japanese film histories (taiyōzoku eiga)",
}


# --------------------------------------------------------------------------
# Anime leaves (D4: genre and demographic; format — TV, film, OVA, ONA,
# special — is a filter). Kinds are titles; seasons and films of one franchise
# share their franchise's leaf.

_FAM_E = next(f for f in FAMILIES if f["code"] == "E")
_FAM_E["key"] = [
    "1. Explicit sexual content made for the adult market (hentai)? → <b>E12 Adult Anime</b>.",
    "2. Made first for young children (kodomo-muke), or a family literary adaptation? → <b>E11 Children's & Family</b>.",
    "3. A magical girl who transforms to fight or to help? → <b>E4 Magical Girl</b>.",
    "4. Giant robots, or speculative science (space, cyborgs, the future) that carries the story — not a device that only frames a school comedy, romance or idol show? → <b>E2 Mecha & Science Fiction</b>.",
    "5. A sport or a competitive game carries it? → <b>E7 Sports</b>.",
    "6. Aims first to frighten? → <b>E9 Horror</b>.",
    "7. Transported or reborn into another world, or an invented fantasy world or yōkai spirit world at its centre? → <b>E3 Fantasy & Isekai</b> (a battle series in a fantasy world with a shōnen battle structure is E1, AN1).",
    "8. Fights and powers carry it? → <b>E1 Action & Battle</b>.",
    "9. A love story first? → <b>E5 Romance & Romantic Comedy</b>. Everyday life, healing calm, cute-girls, idols and bands? → <b>E6 Slice of Life & Iyashikei</b>.",
    "10. Laughter first? → <b>E10 Comedy</b>. Otherwise → <b>E8 Drama, Psychological & Mystery</b>.",
]
_FAM_E["subs"].append(("E12", "Adult Anime", "Axis: none (one leaf); is_adult titles of the anime database."))

PRECEDENCE += [
    ("AN1", "Battle before world", "A series whose episodes are built on escalating fights, rivals and power systems (shōnen battle) is E1 even when set in a fantasy world (<i>Fullmetal Alchemist</i>, <i>Demon Slayer</i>, <i>Jujutsu Kaisen</i>); an isekai or a fantasy whose world and journey carry it stays E3 (<i>Re:Zero</i>, <i>Frieren</i>)."),
    ("AN2", "Franchise unity", "All seasons, films, OVAs and specials of one franchise share the leaf of its main series, unless a spin-off belongs to another genre outright (a gag spin-off → E10)."),
    ("AN3", "Demographic", "Shōnen, seinen, shōjo and josei are tags on every title (MAL/AniList demographic); they divide leaves only where the field names a demographic genre (shōjo romance, josei)."),
    ("AN5", "Comedy first", "A series whose premise is a pretext for gags or parody (gag manga, a genre parody) is E10 whatever its setting or club (<i>Detroit Metal City</i>, <i>Dragon Half</i>, <i>KonoSuba</i> excepted as isekai, since its world carries the story)."),
    ("AN6", "Children's franchises", "A children's franchise (Pokémon, Digimon, Doraemon) stays in E11 across its entries (AN2), including films made for its grown-up fans."),
    ("AN7", "What carries the story", "A setting, sport, band or speculative frame that is only a backdrop does not decide the leaf: the sport must drive the plot for E7 (<i>Blue Box</i> → romance), a fantasy world must carry the story for E3 (a villainess romance in a fantasy court → romance). Toy-line battle shows for children (<i>Beyblade</i>, <i>Bakugan</i>) are E11; one-off comedy specials and chibi extras of a franchise are E10."),
    ("AN8", "Adult flag", "E12 holds explicit hentai only; an adult-flagged art film or erotic drama (<i>Cleopatra</i> 1970, <i>Shoujo Tsubaki</i>) is placed by its genre with E12-1 as see-also. A gag series about everyday life is E10 (comedy first, AN5); a gentle everyday series without gag structure is E6."),
    ("AN9", "Battle structure in any setting", "AN1 holds for science-fiction and samurai settings too: a series built on escalating fights and power systems is E1 (<i>Kaiju No. 8</i>, <i>Jigokuraku</i>); a death game or gambling series whose engine is the game, not the fights, is E8-6 (<i>Kakegurui</i>, <i>Juuni Taisen</i> excepted as battle). Ecchi series whose fan service carries them stay E10-2 even with fights (<i>High School DxD</i>)."),
    ("AN10", "Frames and parodies", "A magical-girl or robot frame on a romance or comedy does not make E4 or E2 (AN7); a magical-girl parody is E10. A historical war epic whose era and campaigns are the subject is E8-4 even with constant battles (<i>Kingdom</i>, <i>Vinland Saga</i>). Comedy shorts, bloopers and chibi extras of a franchise are E10; side stories in the franchise's own genre stay with it (AN2)."),
    ("AN4", "Non-Japanese animation in the anime database", "Donghua and Korean animation selected through the anime database are placed by the same key, with country as a filter; animation from elsewhere selected as film is A15."),
]

_add("E1", [
    ("E1-1", "Shōnen Battle", "broad",
     "long-running action series of escalating fights, rivals, training arcs and power systems, the core of Weekly Shōnen Jump adaptations (<i>Dragon Ball Z</i>, <i>Naruto</i>, <i>One Piece</i>, <i>Bleach</i>, <i>Jujutsu Kaisen</i>, <i>Demon Slayer</i>).",
     "battle shōnen; nekketsu", "E3-2 Fantasy Adventure.", "Shōnen manga|battle shōnen"),
    ("E1-2", "Seinen Action", "medium",
     "violent action for adult audiences — mercenaries, hunters, gunfights, dark warriors (<i>Hellsing</i>, <i>Black Lagoon</i>, <i>Gantz</i>, <i>Golgo 13</i>; <i>Berserk</i> excepted as dark fantasy).",
     "seinen action", "E8-5 Crime & Gangster Anime.", "seinen"),
    ("E1-3", "Samurai & Ninja Anime", "medium",
     "action in Japan's samurai and ninja past, including chanbara anime (<i>Rurouni Kenshin</i>, <i>Samurai Champloo</i>, <i>Ninja Scroll</i>, <i>Sword of the Stranger</i>).",
     "chanbara anime; jidaigeki anime", "A7-2 Chanbara.", "Samurai cinema"),
    ("E1-4", "Superhero Anime", "medium",
     "anime of costumed heroes and hero societies (<i>My Hero Academia</i>, <i>One-Punch Man</i>, <i>Tiger & Bunny</i>).",
     "hero anime", "A6-3 Superhero Film.", "superhero fiction"),
    ("E1-6", "Action Anime", "broad",
     "action series and films outside shōnen battle, seinen action and the narrower leaves — light-novel and game-based action, school battle series (<i>Absolute Duo</i>, <i>Akame ga Kill!</i> excepted as dark fantasy).",
     "", "E1-1 Shōnen Battle.", "action anime"),
    ("E1-7", "Wuxia & Xianxia Animation", "narrow",
     "animation of martial heroes and of immortal cultivation, Chinese (donghua) above all, and Japanese works in the same genre, (<i>Soul Land</i>, <i>Battle Through the Heavens</i>, <i>Link Click</i> excepted as drama).",
     "cultivation donghua; xianxia animation", "C2-5 Wuxia & Xianxia Drama.", "Xianxia"),
    ("E1-8", "Delinquent Anime", "narrow",
     "anime of yankī delinquents and gang fights (<i>Tokyo Revengers</i>, <i>Great Teacher Onizuka</i> excepted as comedy-drama, <i>Crows</i>-type brawlers).",
     "yankī anime; furyō anime", "E1-5 Martial Arts Anime.", "Yankī"),
    ("E1-5", "Martial Arts Anime", "narrow",
     "anime built on hand-to-hand fighting and tournaments outside shōnen battle power systems (<i>Baki</i>, <i>Kengan Ashura</i>, <i>Fist of the North Star</i>).",
     "", "E7-1 Sports Anime.", "martial arts film"),
])
_add("E2", [
    ("E2-1", "Super Robot", "medium",
     "giant robots as invincible heroes with signature attacks (<i>Mazinger Z</i>, <i>Getter Robo</i>, <i>Gurren Lagann</i>).",
     "super robot anime", "E2-2 Real Robot.", "Super robot"),
    ("E2-2", "Real Robot", "medium",
     "mecha as mass-produced military machines in realistic wars (<i>Mobile Suit Gundam</i>, <i>Macross</i>, <i>Code Geass</i>, <i>Neon Genesis Evangelion</i>).",
     "real robot anime", "E2-1 Super Robot.", "Real robot"),
    ("E2-3", "Cyberpunk Anime", "medium",
     "high-tech, low-life futures of cyborgs, networks and megacities (<i>Akira</i>, <i>Ghost in the Shell</i>, <i>Serial Experiments Lain</i>, <i>Psycho-Pass</i>).",
     "", "A5-4 Cyberpunk.", "Cyberpunk"),
    ("E2-4", "Space Opera Anime", "medium",
     "adventure and war among the stars (<i>Space Battleship Yamato</i>, <i>Legend of the Galactic Heroes</i>, <i>Cowboy Bebop</i>, <i>Space Brothers</i> excepted as drama).",
     "", "A5-6 Space Opera & Space Adventure.", "Space opera"),
    ("E2-6", "Tokusatsu & Kaiju Anime", "narrow",
     "anime of giant monsters and of the tokusatsu hero franchises (<i>Godzilla: Planet of the Monsters</i>, <i>SSSS.Gridman</i>, <i>Godzilla Singular Point</i>).",
     "kaiju anime", "A5-1 Kaiju Film; A5-2 Tokusatsu Hero Film.", "Kaiju"),
    ("E2-5", "Science Fiction Anime", "broad",
     "speculative anime outside mecha, cyberpunk and space opera: time travel, post-apocalypse, aliens, technology (<i>Steins;Gate</i>, <i>Dr. Stone</i>, <i>Planetes</i>, <i>Attack on Titan</i> excepted as dark fantasy).",
     "SF anime", "E2-3 Cyberpunk Anime.", "Science fiction"),
])
_add("E3", [
    ("E3-1", "Isekai", "medium",
     "stories of people transported to or reborn in another world (<i>Re:Zero</i>, <i>Mushoku Tensei</i>, <i>KonoSuba</i>, <i>That Time I Got Reincarnated as a Slime</i>, <i>Sword Art Online</i>).",
     "isekai; another-world anime", "E3-2 Fantasy Adventure.", "Isekai"),
    ("E3-2", "Fantasy Adventure", "broad",
     "quests and journeys through invented worlds and magic (<i>Spirited Away</i>, <i>Frieren</i>, <i>Made in Abyss</i>, <i>Magi</i>).",
     "high fantasy anime", "E3-1 Isekai; E1-1 Shōnen Battle.", "Fantasy"),
    ("E3-3", "Dark Fantasy", "medium",
     "grim fantasy of monsters, war and cruelty (<i>Attack on Titan</i>, <i>Claymore</i>, <i>Devilman Crybaby</i>, <i>Vinland Saga</i> excepted as historical).",
     "", "E9-1 Horror Anime.", "Dark fantasy"),
    ("E3-6", "Shenmo Animation", "narrow",
     "Chinese animation of gods and demons from the classical shenmo novels and myth (<i>Ne Zha</i>, <i>Monkey King: Hero Is Back</i>, <i>Havoc in Heaven</i>).",
     "gods and demons fiction; Chinese mythological animation", "E1-7 Wuxia & Xianxia Animation.", "Shenmo"),
    ("E3-4", "Supernatural & Yōkai Anime", "medium",
     "the spirit world among us — yōkai, gods, exorcists, ghosts — told as adventure or quiet wonder (<i>Natsume's Book of Friends</i>, <i>Mushishi</i>, <i>Noragami</i>, <i>Mononoke</i>).",
     "yōkai anime; urban fantasy", "E9-1 Horror Anime; E6-1 Iyashikei.", "Yōkai"),
])
_add("E4", [
    ("E4-1", "Magical Girl", "medium",
     "mahō shōjo: girls who gain magic to help others, from <i>Sally the Witch</i> and <i>Minky Momo</i> to <i>Cardcaptor Sakura</i>.",
     "mahō shōjo; majokko", "E4-2 Magical Girl Warrior.", "Magical girl"),
    ("E4-2", "Magical Girl Warrior", "medium",
     "magical girls who transform to fight evil in teams, and their dark deconstructions (<i>Sailor Moon</i>, <i>Pretty Cure</i>, <i>Puella Magi Madoka Magica</i>).",
     "sentai magical girl; dark magical girl", "E4-1 Magical Girl.", "Magical girl"),
])
_add("E5", [
    ("E5-1", "Shōjo Romance", "medium",
     "romance written for girls, of first love and feelings (<i>Fruits Basket</i>, <i>Kimi ni Todoke</i>, <i>Ouran High School Host Club</i>, <i>Nana</i> excepted as josei).",
     "shōjo manga romance", "E5-6 Josei.", "Shōjo manga"),
    ("E5-2", "Romantic Comedy Anime", "broad",
     "love stories told for laughter, often school rom-coms (<i>Toradora!</i>, <i>Kaguya-sama: Love Is War</i>, <i>Horimiya</i>).",
     "rom-com", "E5-3 Harem.", "Romantic comedy"),
    ("E5-3", "Harem", "medium",
     "one protagonist surrounded by several romantic interests (<i>Love Hina</i>, <i>The Quintessential Quintuplets</i>, <i>Tenchi Muyo!</i>).",
     "harem anime; reverse harem", "E10-2 Ecchi.", "Harem (genre)"),
    ("E5-4", "Boys' Love", "narrow",
     "romance between men (BL, yaoi) (<i>Given</i>, <i>Sasaki and Miyano</i>, <i>Doukyuusei</i>).",
     "BL; yaoi; shōnen-ai", "E5-5 Yuri.", "Yaoi"),
    ("E5-5", "Yuri", "narrow",
     "romance between women (<i>Bloom Into You</i>, <i>Citrus</i>, <i>Revolutionary Girl Utena</i> excepted as drama).",
     "shōjo-ai; girls' love", "E5-4 Boys' Love.", "Yuri (genre)"),
    ("E5-6", "Romantic Drama Anime", "broad",
     "love stories told as drama, including josei romance (<i>Your Name</i> excepted as fantasy; <i>Nana</i>, <i>Honey and Clover</i>, <i>Clannad</i>, <i>The Garden of Words</i>).",
     "josei romance", "E8-3 Drama Anime.", "Josei manga|romance anime"),
])
_add("E6", [
    ("E6-1", "Iyashikei", "medium",
     "'healing' anime of calm, beauty and small pleasures (<i>Aria</i>, <i>Yuru Camp</i>, <i>Non Non Biyori</i>, <i>Barakamon</i>).",
     "healing anime", "E6-2 Cute Girls Doing Cute Things.", "Iyashikei"),
    ("E6-2", "Cute Girls Doing Cute Things", "medium",
     "moe slice-of-life of girls' clubs and daily routines (<i>K-On!</i>, <i>Lucky Star</i>, <i>Azumanga Daioh</i>, <i>Nichijou</i> excepted as gag).",
     "CGDCT; moe slice of life", "E6-1 Iyashikei.", "Cute girls doing cute things"),
    ("E6-3", "Slice of Life Anime", "broad",
     "everyday school, work and family life outside the narrower leaves (<i>Shirobako</i>, <i>Silver Spoon</i>, <i>Spy × Family</i> excepted as comedy).",
     "nichijō-kei", "E8-3 Drama Anime.", "Slice of life"),
    ("E6-4", "Idol Anime", "narrow",
     "anime of idol groups and their rise (<i>Love Live!</i>, <i>The Idolmaster</i>, <i>Uta no Prince-sama</i>, <i>Oshi no Ko</i> excepted as drama).",
     "idol anime", "E6-5 Music Anime.", "Japanese idol|idol anime"),
    ("E6-5", "Music Anime", "narrow",
     "anime of musicians, bands and performance (<i>Your Lie in April</i>, <i>Bocchi the Rock!</i>, <i>Beck</i>, <i>Nodame Cantabile</i>).",
     "band anime", "E6-4 Idol Anime.", "music anime"),
    ("E6-7", "Performing Arts Anime", "narrow",
     "anime of theatre, revue, rakugo, recitation and circus (<i>Kageki Shoujo!!</i>, <i>Kaleido Star</i>, <i>Akane-banashi</i>, <i>Revue Starlight</i>).",
     "stage anime", "E6-4 Idol Anime; E6-5 Music Anime.", "https://myanimelist.net/anime/genre/70/Performing_Arts"),
    ("E6-6", "Cooking & Gourmet Anime", "narrow",
     "anime built on food, cooking and eating (<i>Food Wars!</i>, <i>Sweetness and Lightning</i>, <i>Restaurant to Another World</i>).",
     "gourmet anime", "E6-1 Iyashikei.", "Cooking manga|Gourmet manga"),
])
_add("E7", [
    ("E7-1", "Sports Anime", "medium",
     "spokon: anime of a sport, a team and its competitions — volleyball, basketball, baseball, football, boxing, cycling, swimming (<i>Slam Dunk</i>, <i>Haikyu!!</i>, <i>Hajime no Ippo</i>, <i>Ashita no Joe</i>, <i>Blue Lock</i>).",
     "spokon; supokon", "A14-7 Sports Film.", "Sports anime and manga|Spokon"),
    ("E7-2", "Game Anime", "narrow",
     "anime of competitive games — go, shogi, karuta, mahjong, card battles (<i>Hikaru no Go</i>, <i>Chihayafuru</i>, <i>March Comes in Like a Lion</i> excepted as drama, <i>Yu-Gi-Oh!</i>).",
     "card battle anime; board game anime", "E7-1 Sports Anime.", "Card game anime|Hikaru no Go"),
])
_add("E8", [
    ("E8-1", "Psychological Thriller Anime", "medium",
     "suspense of minds in conflict, manipulation and identity (<i>Death Note</i>, <i>Monster</i>, <i>Perfect Blue</i>, <i>Paranoia Agent</i>, <i>The Promised Neverland</i>).",
     "psychological anime", "E9-1 Horror Anime.", "Psychological thriller"),
    ("E8-2", "Mystery & Detective Anime", "medium",
     "anime of detection and puzzles (<i>Case Closed</i>, <i>Hyouka</i>, <i>Odd Taxi</i>, <i>Erased</i>).",
     "detective anime", "E8-1 Psychological Thriller Anime.", "Detective fiction|mystery anime"),
    ("E8-3", "Drama Anime", "broad",
     "dramas of grief, growing up, family and society (<i>Anohana</i>, <i>Violet Evergarden</i>, <i>A Silent Voice</i>, <i>March Comes in Like a Lion</i>, <i>Wolf Children</i>).",
     "", "E5-6 Romantic Drama Anime; E6-3 Slice of Life Anime.", "drama anime"),
    ("E8-4", "Historical & War Anime", "medium",
     "anime in which a historical era or a war is the subject (<i>Grave of the Fireflies</i>, <i>In This Corner of the World</i>, <i>The Rose of Versailles</i>, <i>Vinland Saga</i>).",
     "historical anime; war anime", "E1-3 Samurai & Ninja Anime.", "Historical fiction"),
    ("E8-6", "Death Game & Survival Anime", "medium",
     "anime of lethal games and forced survival contests (<i>Danganronpa</i>, <i>Darwin's Game</i>, <i>Kaiji</i>, <i>Btooom!</i>, <i>Future Diary</i>).",
     "death game anime; desu gēmu", "A3-3 Survival & Death-Game Thriller.", "death game"),
    ("E8-7", "Art & Experimental Anime", "narrow",
     "independent and avant-garde Japanese animation made outside genre — Kuri, Yamamura, Furukawa, Aihara (<i>Cat Soup</i>, <i>Mt. Head</i>, <i>Belladonna of Sadness</i> excepted as drama).",
     "independent anime; art animation", "B1-2 Auteur Animated Short.", "Independent animation"),
    ("E8-5", "Crime & Gangster Anime", "medium",
     "anime of thieves, gangsters and the underworld (<i>Lupin III</i>, <i>Baccano!</i>, <i>91 Days</i>, <i>Great Pretender</i>).",
     "crime anime", "E1-2 Seinen Action.", "crime fiction"),
])
_add("E9", [
    ("E9-1", "Horror Anime", "medium",
     "anime that aims first to frighten — curses, ghosts, killers, cosmic dread (<i>Another</i>, <i>Higurashi: When They Cry</i>, <i>Shiki</i>, <i>Junji Ito Collection</i>).",
     "", "E3-3 Dark Fantasy; E8-1 Psychological Thriller Anime.", "horror anime"),
])
_add("E10", [
    ("E10-1", "Gag & Parody Anime", "medium",
     "comedy first: gags, absurdity, parody and surreal humour (<i>Gintama</i>, <i>Nichijou</i>, <i>The Disastrous Life of Saiki K.</i>, <i>Pop Team Epic</i>).",
     "gag anime; owarai", "E5-2 Romantic Comedy Anime.", "gag manga"),
    ("E10-2", "Ecchi", "medium",
     "comedy and fan service built on sexual innuendo without explicit content (<i>High School DxD</i>, <i>Prison School</i>, <i>Kill la Kill</i> excepted as battle).",
     "fan service comedy", "E5-3 Harem; E12-1 Hentai.", "Ecchi"),
    ("E10-3", "Comedy Anime", "broad",
     "situation and character comedy outside gag and ecchi (<i>Spy × Family</i>, <i>Grand Blue</i>, <i>The Devil Is a Part-Timer!</i>).",
     "", "E6-3 Slice of Life Anime.", "comedy anime"),
])
_add("E11", [
    ("E11-1", "Kodomo-muke", "medium",
     "anime made for young children, including the long family series (<i>Doraemon</i>, <i>Anpanman</i>, <i>Crayon Shin-chan</i>, <i>Pokémon</i>, <i>Chibi Maruko-chan</i>).",
     "kodomo anime; children's anime", "A19-1 Children's Film.", "Kodomo manga|Kodomo"),
    ("E11-3", "Early Japanese Animation", "narrow",
     "Japanese animation before the television era (to 1962): the silent and early sound shorts of Shimokawa, Kitayama, Kōuchi, Ōfuji and Masaoka the wartime features and the first postwar shorts (<i>Namakura Gatana</i>, <i>Momotaro's Divine Sea Warriors</i>, <i>Kumo no Ito</i>); Toei's feature films from <i>Hakujaden</i> (1958) go by genre.",
     "senzen anime; prewar anime", "E11-1 Kodomo-muke.", "History of anime"),
    ("E11-2", "World Masterpiece Theater", "narrow",
     "Nippon Animation's series of family adaptations of Western classics and their kin (<i>Heidi, Girl of the Alps</i>, <i>Anne of Green Gables</i>, <i>A Dog of Flanders</i>).",
     "Sekai Meisaku Gekijō", "E11-1 Kodomo-muke.", "World Masterpiece Theater"),
])
_add("E12", [
    ("E12-1", "Hentai", "narrow",
     "explicit adult anime, mostly OVAs (flagged is_adult in the anime database).",
     "adult anime", "E10-2 Ecchi.", "Hentai"),
])
ATTEST_WIKI.update({
    "E1-1": "Shōnen manga", "E1-2": "Seinen manga", "E1-3": "Samurai cinema", "E1-4": "Superhero fiction", "E1-5": "Martial arts film", "E1-6": "Action fiction", "E1-7": "Xianxia", "E1-8": "Yankī|Yankii",
    "E2-1": "Super robot", "E2-2": "Real robot", "E2-3": "Cyberpunk", "E2-4": "Space opera", "E2-5": "Science fiction",
    "E3-1": "Isekai", "E3-2": "Fantasy", "E3-3": "Dark fantasy", "E3-4": "Yōkai", "E4-1": "Magical girl", "E4-2": "Magical girl",
    "E5-1": "Shōjo manga", "E5-2": "Romantic comedy", "E5-3": "Harem (genre)", "E5-4": "Yaoi", "E5-5": "Yuri (genre)", "E5-6": "Josei manga",
    "E6-1": "Iyashikei", "E6-2": "Cute girls doing cute things", "E6-3": "Slice of life", "E6-4": "Japanese idol", "E6-5": "Music anime|Music in anime",
    "E6-6": "Cooking manga|Gourmet manga", "E7-1": "Sports anime and manga|Spokon", "E7-2": "Hikaru no Go",
    "E8-1": "Psychological thriller", "E8-2": "Detective fiction", "E8-3": "Drama", "E8-4": "Historical fiction", "E8-5": "Crime fiction", "E8-7": "Independent animation", "E3-6": "Shenmo|Gods and demons fiction", "E8-6": "Death game|Battle royale (genre)",
    "E9-1": "Horror fiction", "E10-1": "Gag manga", "E10-2": "Ecchi", "E10-3": "Comedy", "E11-1": "Kodomo manga",
    "E11-2": "World Masterpiece Theater", "E11-3": "History of anime", "E2-6": "Kaiju", "E6-7": "Performing arts", "E12-1": "Hentai",
})


# --------------------------------------------------------------------------
# Television: scripted series (C), serial traditions (D), unscripted formats (G).

_FAM_C = next(f for f in FAMILIES if f["code"] == "C")
_FAM_C["key"] = [
    "1. Animated, and not anime? → <b>C6 Animated Series</b> (TV1).",
    "2. Made first for children or tweens (live action)? → <b>C7 Children's Series</b>.",
    "3. An East or Southeast Asian drama in a <b>named tradition</b> — K-drama romance, sageuk, makjang, Chinese costume drama, wuxia/xianxia drama, idol drama, asadora, taiga drama, Japanese trendy drama, lakorn, BL drama? → <b>C2</b> (D3). Asian dramas outside those traditions (thrillers, medical, fantasy) go by genre below with 'Asian drama' as a filter.",
    "4. Science fiction, fantasy, horror, the supernatural or superheroes? → <b>C5 Genre Series</b>.",
    "5. Criminals, police, detectives, spies or a thriller plot? → <b>C3 Crime & Thriller Series</b>.",
    "6. Laughter first? → <b>C4 Comedy Series</b>. Otherwise → <b>C1 Drama Series</b>, by subject.",
]
_FAM_C["test"] = "a series made for television or streaming — scripted series and miniseries, and documentary series — anywhere, outside the named long-running serial traditions, anime and unscripted entertainment."
_FAM_C["key"].insert(0, "0. Non-fiction (a documentary series)? → <b>C8 Documentary Series</b> (TV7).")
_FAM_C["subs"] = [
    ("C1", "Drama Series", "Axis: subject (family, medicine, law, politics, the past, youth)."),
    ("C2", "East & Southeast Asian Drama Traditions", "Axis: the named tradition (D3: 'Asian drama' is a filter; Asian dramas outside these traditions are placed by genre)."),
    ("C3", "Crime & Thriller Series", "Axis: milieu and source of suspense."),
    ("C4", "Comedy Series", "Axis: comic form (multi-camera sitcom, single-camera, sketch, mockumentary)."),
    ("C5", "Genre Series", "Axis: speculative premise (science fiction, fantasy, horror, superheroes)."),
    ("C6", "Animated Series", "Axis: audience and form (non-anime animation)."),
    ("C7", "Children's Series", "Axis: age of audience (live action)."),
    ("C8", "Documentary Series", "Axis: subject."),
]
PRECEDENCE += [
    ("TV1", "Animation", "Every animated series that is not anime is C6, whatever its genre (<i>The Simpsons</i> → Animated Sitcom; <i>Arcane</i> → Animated Action-Adventure)."),
    ("TV2", "Serial or series", "A long-running serial in a named serial tradition (telenovela, dizi, daily soap, soap opera, teleserye, musalsal) is D, not C, even when it is also a crime or historical story; a limited or seasonal series with a closed arc is C."),
    ("TV3", "Named Asian tradition before genre", "An Asian drama in a named tradition of C2 stays there whatever its genre mix (a sageuk with zombies, <i>Kingdom</i>, is Sageuk; a xianxia romance is Wuxia & Xianxia Drama); a Korean thriller or a Japanese medical drama with no tradition home goes by genre."),
    ("TV4", "Crime before drama", "A series centred on crime, police, lawyers defending criminals or spies is C3, even when its prestige makes it 'drama' (<i>The Sopranos</i>, <i>The Wire</i>, <i>Breaking Bad</i>); a legal series about the law firm's own life is Legal Drama."),
    ("TV6", "Daily comedies, crime comedies and true events", "A daily or long-running comedy is a sitcom (C4), not a serial tradition, even with thousands of episodes (<i>Taarak Mehta Ka Ooltah Chashmah</i>). A comedy about criminals goes by laughter first (C4). A dramatised real crime is True Crime Drama (C3-7); a dramatised real event that is not a crime is Docudrama Series (C1-9)."),
    ("TV7", "Non-fiction", "A documentary series is C8; a talk, chat or variety programme that is not a cross-border format goes to G3 (variety and talk) as a programme of its own."),
    ("TV8", "What carries the story", "A comedy whose fantastical premise only carries the gags is Comedy (C4), not Genre Series (<i>The Addams Family</i>, <i>Wonderfalls</i>); a supernatural or speculative frame on a medical, crime or family series does not make it C5 unless the frame carries the plot. A children's cartoon with an adult following stays Children's Animated Series. News magazines and current-affairs programmes are not series of this tab: exclude them."),
    ("TV9", "Comedy first; thrillers; long-running continuing dramas", "A sitcom with a science-fiction, fantasy or horror premise is Comedy (C4) when laughter comes first (<i>Red Dwarf</i>, <i>The League of Gentlemen</i>); comic detectives stay in C3 with C4-5 as see-also. A domestic or psychological thriller miniseries is C3-8. A long-running continuing drama of a workplace (<i>Casualty</i>, <i>Holby City</i>, <i>The Bill</i>) goes by genre (C1-2, C3-1), not D. An Arab 30-episode Ramadan series is D5-1 whatever its genre."),
    ("TV5", "Franchise unity", "Spin-offs and revivals share their parent's leaf unless they change genre outright."),
]
MODIFIERS += [
    "<b>Series format</b> — miniseries, limited, anthology, ongoing, web series: a filter on Television Series.",
    "<b>Network and platform</b> — HBO, BBC, Netflix, TVB, Globo: tags.",
]

_add("C1", [
    ("C1-1", "Family Drama Series", "broad", "series about families and their generations (<i>Six Feet Under</i>, <i>This Is Us</i>, <i>Succession</i>, <i>Reply 1988</i>).", "family saga", "D2-5 Prime-Time Soap Opera.", "family drama"),
    ("C1-2", "Medical Drama", "medium", "series set in hospitals and medical practice (<i>ER</i>, <i>Grey's Anatomy</i>, <i>House</i>, <i>Hospital Playlist</i>).", "hospital drama", "C1-3 Legal Drama Series.", "medical drama"),
    ("C1-3", "Legal Drama Series", "medium", "series about lawyers and the law's own world (<i>L.A. Law</i>, <i>The Good Wife</i>, <i>Extraordinary Attorney Woo</i>) (TV4).", "courtroom series", "C3-3 Crime Drama Series.", "legal drama"),
    ("C1-4", "Political Drama Series", "medium", "series of government, elections and power (<i>The West Wing</i>, <i>House of Cards</i>, <i>Borgen</i>).", "", "C3-5 Spy & Espionage Series.", "political drama"),
    ("C1-5", "Teen Drama", "medium", "series about adolescents and high school (<i>Beverly Hills, 90210</i>, <i>Skins</i>, <i>Euphoria</i>, <i>Sex Education</i> excepted as comedy).", "teen series", "C7-2 Children's & Tween Series.", "teen drama"),
    ("C1-6", "Period Drama Series", "broad", "series set in a defining past, costume and historical drama (<i>Downton Abbey</i>, <i>The Crown</i>, <i>Mad Men</i>, <i>Rome</i>).", "costume drama; historical drama series", "C2-2 Sageuk; C2-5 Chinese Costume Drama.", "costume drama|historical drama"),
    ("C1-7", "War Drama Series", "medium", "series about war and soldiers (<i>Band of Brothers</i>, <i>The Pacific</i>, <i>Generation Kill</i>).", "military drama", "C1-6 Period Drama Series.", "war drama"),
    ("C1-8", "Western Series", "narrow", "series of the American frontier (<i>Gunsmoke</i>, <i>Bonanza</i>, <i>Deadwood</i>, <i>Yellowstone</i> as neo-western).", "TV western", "A17-1 Western.", "Western (genre)"),
    ("C1-9", "Docudrama Series", "medium", "dramatisations of real events and lives (<i>Chernobyl</i>, <i>When They See Us</i>, <i>The People v. O. J. Simpson</i>).", "biographical series; true-story drama", "C3-3 Crime Drama Series.", "docudrama"),
    ("C1-10", "Workplace & Professional Drama", "medium", "series built on a profession or workplace outside medicine and law (<i>The Newsroom</i>, <i>Mad Men</i> excepted as period, <i>The Bear</i>, <i>Misaeng</i>).", "workplace drama", "C1-2 Medical Drama.", "workplace drama"),
    ("C1-11", "Sports Drama Series", "narrow", "series built on a sport and its teams (<i>Friday Night Lights</i>, <i>Ted Lasso</i> excepted as comedy).", "", "A14-7 Sports Film.", "sports drama"),
    ("C1-12", "Drama Series", "broad", "dramas of character and society outside the narrower leaves (<i>The Leftovers</i>, <i>Normal People</i>, <i>The Crown</i> excepted as period).", "serial drama", "C1-1 Family Drama Series.", "drama television series|television drama"),
    ("C1-16", "Anthology Drama Series", "medium", "series of self-contained plays or stories with changing casts (<i>Play for Today</i>, <i>Armchair Theatre</i>, <i>Inside No. 9</i> excepted as comedy, <i>The Twilight Zone</i> excepted as SF).", "single play; anthology series", "C5-1 Science Fiction Series.", "anthology series"),
    ("C1-15", "Action & Adventure Series", "medium", "series carried by action, voyages, quests and treasure hunts, from literary adaptations to stunt-driven adventure (<i>Relic Hunter</i>, <i>Knight Rider</i>, <i>MacGyver</i>) (<i>Treasure Island</i> serials, <i>Around the World in 80 Days</i>, <i>The Adventures of Robin Hood</i>, <i>Sharpe</i> excepted as war).", "adventure serial", "A6-2 Adventure Film; A6-6 Swashbuckler.", "adventure fiction"),
    ("C1-13", "Romantic Drama Series", "medium", "series whose main line is a love story, outside the Asian drama traditions (<i>Outlander</i> excepted as fantasy, <i>Bridgerton</i>, <i>Normal People</i>).", "romance series", "C2-1 K-Drama.", "romance television"),
])
_add("C2", [
    ("C2-1", "K-Drama", "broad", "the Korean miniseries tradition of romance and melodrama — trendy, fated and rom-com love stories in 16–20 episodes (<i>Winter Sonata</i>, <i>Guardian: The Lonely and Great God</i>, <i>Crash Landing on You</i>, <i>Coffee Prince</i>).", "Korean drama; Korean miniseries; K-drama romance", "C2-3 Makjang.", "Korean drama"),
    ("C2-2", "Sageuk", "medium", "Korean historical drama of the Joseon, Goryeo and Three Kingdoms courts (<i>Dae Jang Geum</i>, <i>Moon Embracing the Sun</i>, <i>Mr. Sunshine</i>, <i>Kingdom</i>).", "Korean historical drama; fusion sageuk", "C1-6 Period Drama Series.", "Sageuk"),
    ("C2-3", "Makjang", "medium", "Korean melodrama of outrageous twists — birth secrets, revenge, chaebol families, affairs — often in daily and weekend slots (<i>The Penthouse</i>, <i>Temptation of Wife</i>, <i>The World of the Married</i>).", "makjang drama; Korean family melodrama", "C2-1 K-Drama.", "Makjang"),
    ("C2-4", "Chinese Costume Drama", "broad", "guzhuang: Chinese historical and palace drama of the imperial past (<i>Story of Yanxi Palace</i>, <i>Nirvana in Fire</i>, <i>Empresses in the Palace</i>, <i>Meteor Garden</i> excepted as idol drama).", "guzhuang; palace drama; gongdou", "C2-5 Wuxia & Xianxia Drama.", "Chinese historical drama|Guzhuang"),
    ("C2-5", "Wuxia & Xianxia Drama", "medium", "Chinese drama of martial heroes (wuxia) and of immortal cultivation and celestial romance (xianxia) (<i>The Legend of the Condor Heroes</i>, <i>The Untamed</i>, <i>Eternal Love</i>, <i>Love Between Fairy and Devil</i>).", "wuxia drama; xianxia drama; xuanhuan", "A8-3 Wuxia.", "Xianxia|Wuxia"),
    ("C2-6", "Idol Drama", "medium", "Taiwanese and Chinese youth romance with pop-idol casts, from <i>Meteor Garden</i> (2001) to the modern Chinese campus and urban romances (<i>It Started with a Kiss</i>, <i>Go Go Squid!</i>, <i>A Love So Beautiful</i>).", "ouxiang ju; Taiwanese drama; C-drama romance", "C2-1 K-Drama.", "Idol drama|Taiwanese drama"),
    ("C2-7", "Asadora", "narrow", "NHK's morning serial (renzoku terebi shōsetsu) of a woman's life across decades (<i>Oshin</i>, <i>Amachan</i>, <i>Carnation</i>).", "renzoku terebi shōsetsu", "C2-8 Taiga Drama.", "Asadora"),
    ("C2-8", "Taiga Drama", "narrow", "NHK's year-long historical drama of a figure of Japanese history (<i>Sanada Maru</i>, <i>Ryōmaden</i>, <i>The 13 Lords of the Shogun</i>).", "taiga dorama", "C2-7 Asadora; C1-6 Period Drama Series.", "Taiga drama"),
    ("C2-9", "Japanese Trendy Drama", "medium", "the Japanese prime-time drama (dorama) of urban romance and work in one-cour seasons, from the trendy dramas of Fuji TV's Monday 9 pm slot (<i>Tokyo Love Story</i>, <i>Long Vacation</i>, <i>Nodame Cantabile</i>, <i>We Married as a Job!</i>).", "dorama; getsuku; J-drama", "C2-1 K-Drama.", "Trendy drama|Japanese television drama"),
    ("C2-10", "Lakorn", "medium", "Thai television drama (lakhon), with its romance, revenge and slap-kiss conventions (<i>Love Destiny</i>, <i>The Crown Princess</i>, <i>Girl from Nowhere</i> excepted as thriller).", "lakhon; Thai drama", "C2-11 Boys' Love Drama.", "Lakorn|Thai television soap opera"),
    ("C2-11", "Boys' Love Drama", "medium", "BL series — romance between young men — from Thailand, Taiwan, Japan, Korea and China (<i>SOTUS</i>, <i>2gether</i>, <i>Bad Buddy</i>, <i>Cherry Magic!</i>, <i>Word of Honor</i>).", "BL drama; Y series; danmei drama", "C2-10 Lakorn; E5-4 Boys' Love.", "Boys' love|Thai boys' love"),
])
_add("C3", [
    ("C3-1", "Police Procedural Series", "medium", "series of police investigations case by case (<i>Hill Street Blues</i>, <i>NYPD Blue</i>, <i>Law & Order</i>, <i>Line of Duty</i>, <i>Signal</i>).", "cop show", "C3-2 Detective Series.", "police procedural"),
    ("C3-2", "Detective Series", "medium", "series of a detective solving mysteries, whodunits and cosy crime (<i>Columbo</i>, <i>Poirot</i>, <i>Sherlock</i>, <i>Midsomer Murders</i>).", "whodunit series; cosy mystery", "C3-1 Police Procedural Series.", "detective fiction"),
    ("C3-3", "Crime Drama Series", "broad", "series of criminals and their world (<i>The Sopranos</i>, <i>The Wire</i>, <i>Breaking Bad</i>, <i>Peaky Blinders</i>, <i>Narcos</i>) (TV4).", "crime series; gangster series", "C3-1 Police Procedural Series.", "crime drama"),
    ("C3-4", "Nordic Noir", "narrow", "Scandinavian crime series of bleak landscapes and slow investigations (<i>The Killing</i>, <i>The Bridge</i>, <i>Wallander</i>, <i>Trapped</i>).", "Scandinavian noir; Scandi noir", "C3-1 Police Procedural Series.", "Nordic noir"),
    ("C3-5", "Spy & Espionage Series", "medium", "series of intelligence agents (<i>Mission: Impossible</i>, <i>The Americans</i>, <i>Homeland</i>, <i>Slow Horses</i>, <i>The Bureau</i>).", "spy series", "C1-4 Political Drama Series.", "spy fiction"),
    ("C3-6", "Thriller Series", "broad", "suspense series of conspiracy, survival, revenge and psychological danger (<i>24</i>, <i>Mr. Robot</i>, <i>Squid Game</i>, <i>Money Heist</i> excepted as crime).", "conspiracy thriller series", "C3-3 Crime Drama Series.", "thriller television series|thriller (genre)"),
    ("C3-8", "Psychological & Domestic Thriller Series", "medium", "suspense miniseries of secrets, marriages and threats at home (<i>Doctor Foster</i>, <i>Liar</i>, <i>Fool Me Once</i>, <i>Big Little Lies</i>).", "domestic thriller; domestic noir", "C3-6 Thriller Series.", "domestic noir|psychological thriller"),
    ("C3-7", "True Crime Drama", "narrow", "dramatised series of real criminal cases (<i>Mindhunter</i>, <i>Dahmer</i>, <i>The Serpent</i>).", "", "C1-9 Docudrama Series.", "true crime"),
])
_add("C4", [
    ("C4-1", "Multi-Camera Sitcom", "broad", "studio sitcoms shot before an audience or laugh track (<i>I Love Lucy</i>, <i>Cheers</i>, <i>Seinfeld</i>, <i>Friends</i>, <i>The Big Bang Theory</i>).", "sitcom; situation comedy", "C4-2 Single-Camera Comedy.", "sitcom"),
    ("C4-2", "Single-Camera Comedy", "broad", "film-style comedy series without laugh track (<i>Curb Your Enthusiasm</i>, <i>Arrested Development</i>, <i>Fleabag</i>, <i>Atlanta</i>).", "single-camera sitcom", "C4-1 Multi-Camera Sitcom.", "single-camera setup"),
    ("C4-3", "Mockumentary Sitcom", "medium", "comedy in documentary form (<i>The Office</i>, <i>Parks and Recreation</i>, <i>What We Do in the Shadows</i>, <i>Abbott Elementary</i>).", "mockumentary series", "A10-11 Mockumentary.", "mockumentary"),
    ("C4-4", "Sketch Comedy", "medium", "series of comic sketches (<i>Monty Python's Flying Circus</i>, <i>Saturday Night Live</i>, <i>Key & Peele</i>).", "sketch show", "", "sketch comedy"),
    ("C4-5", "Comedy-Drama Series", "broad", "series balancing comedy and drama (<i>M*A*S*H</i>, <i>Gilmore Girls</i>, <i>Ted Lasso</i>, <i>The Bear</i> excepted as workplace).", "dramedy", "C1-12 Drama Series.", "comedy drama"),
    ("C4-7", "Stand-Up Comedy Special", "narrow", "recorded stand-up shows and series of them (<i>James Acaster: Repertoire</i>, <i>Nanette</i> as special).", "comedy special", "A10-12 Stand-Up Comedy Film.", "stand-up comedy"),
    ("C4-6", "Satire & Political Comedy", "narrow", "comedy that satirises politics and institutions (<i>Yes Minister</i>, <i>The Thick of It</i>, <i>Veep</i>).", "political satire", "C1-4 Political Drama Series.", "political satire"),
])
_add("C5", [
    ("C5-1", "Science Fiction Series", "broad", "series of the future, space and technology (<i>Star Trek</i>, <i>Doctor Who</i>, <i>The Expanse</i>, <i>Black Mirror</i>, <i>Severance</i>).", "SF series; space opera series", "C5-2 Fantasy Series.", "science fiction television"),
    ("C5-2", "Fantasy Series", "broad", "series of magic and invented worlds (<i>Game of Thrones</i>, <i>The Witcher</i>, <i>Outlander</i>, <i>Alchemy of Souls</i>).", "", "C2-5 Wuxia & Xianxia Drama.", "fantasy television"),
    ("C5-3", "Horror Series", "medium", "series that aim first to frighten (<i>The Walking Dead</i>, <i>American Horror Story</i>, <i>The Haunting of Hill House</i>, <i>Sweet Home</i>).", "", "C5-4 Supernatural Drama.", "horror television"),
    ("C5-4", "Supernatural Drama", "medium", "series of ghosts, vampires, witches and the uncanny told as drama or adventure (<i>Buffy the Vampire Slayer</i>, <i>Supernatural</i>, <i>Twin Peaks</i>, <i>Stranger Things</i>).", "supernatural series; paranormal drama", "C5-3 Horror Series.", "supernatural fiction"),
    ("C5-5", "Superhero Series", "medium", "series of costumed or super-powered heroes (<i>Smallville</i>, <i>Daredevil</i>, <i>The Boys</i>, <i>WandaVision</i>).", "", "A6-3 Superhero Film.", "superhero fiction"),
])
_add("C6", [
    ("C6-1", "Animated Sitcom", "medium", "animated comedy series for adults and families (<i>The Flintstones</i>, <i>The Simpsons</i>, <i>South Park</i>, <i>BoJack Horseman</i>, <i>Rick and Morty</i>).", "adult animated sitcom", "C6-2 Adult Animated Series.", "animated sitcom"),
    ("C6-2", "Adult Animated Series", "medium", "non-comedy animation for adults (<i>Arcane</i>, <i>Invincible</i>, <i>Primal</i>, <i>Love, Death & Robots</i>).", "adult animation", "C6-3 Animated Action-Adventure.", "adult animation"),
    ("C6-3", "Animated Action-Adventure", "medium", "animated adventure series for all ages (<i>Batman: The Animated Series</i>, <i>Avatar: The Last Airbender</i>, <i>Gravity Falls</i>, <i>The Legend of Vox Machina</i>).", "action cartoon", "C6-4 Children's Animated Series.", "action-adventure animation|animated series"),
    ("C6-4", "Children's Animated Series", "broad", "cartoon series made first for children (<i>Looney Tunes</i>, <i>SpongeBob SquarePants</i>, <i>Bluey</i>, <i>Peppa Pig</i>).", "Saturday-morning cartoon; kids' cartoon", "E11-1 Kodomo-muke.", "children's television series|Saturday-morning cartoon"),
])
_add("C8", [
    ("C8-1", "Documentary Series", "broad", "non-fiction series of history, society, culture and science (<i>The World at War</i>, <i>Cosmos</i>, <i>The Last Dance</i>, <i>Wild Wild Country</i>).", "docuseries; documentary miniseries", "A13-1 Documentary Film.", "documentary television series|docuseries"),
    ("C8-2", "True Crime Docuseries", "medium", "documentary series investigating real crimes (<i>The Jinx</i>, <i>Making a Murderer</i>, <i>The Staircase</i>, <i>The Devil Next Door</i>).", "true crime series", "C3-7 True Crime Drama.", "true crime"),
    ("C8-3", "Nature Documentary Series", "medium", "series of wildlife and the natural world (<i>Life on Earth</i>, <i>Planet Earth</i>, <i>Blue Planet II</i>).", "natural history series; wildlife series", "A13-3 Nature Documentary.", "nature documentary"),
])
_add("C1", [
    ("C1-14", "Erotic Drama Series", "narrow", "series whose subject is sexual desire and display, including the Indian erotic web series of the streaming platforms (<i>Gandii Baat</i>, <i>Mastram</i>; <i>Spartacus</i> excepted as period).", "erotic web series", "A12-3 Erotic Drama.", "erotic film"),
])
_add("C7", [
    ("C7-1", "Preschool Series", "narrow", "live-action and puppet series for young children (<i>Sesame Street</i>, <i>Mister Rogers' Neighborhood</i>, <i>Teletubbies</i>).", "preschool television", "C6-4 Children's Animated Series.", "preschool television"),
    ("C7-2", "Children's & Tween Series", "medium", "live-action series for children and tweens (<i>Lizzie McGuire</i>, <i>Hannah Montana</i>, <i>iCarly</i>, <i>Goosebumps</i>).", "teen sitcom; tween series", "C1-5 Teen Drama.", "children's television series"),
])

_FAM_D = next(f for f in FAMILIES if f["code"] == "D")
_FAM_D["test"] = "a long-running serial in a named serial tradition, with continuing storylines broadcast daily or weekly for years or hundreds of episodes: soap opera, telenovela, dizi, Indian daily soap, teleserye, musalsal (TV2)."
_FAM_D["key"] = ["1. Latin American or Iberian telenovela? → <b>D1</b>. 2. Anglophone soap opera? → <b>D2</b>. 3. Turkish dizi? → <b>D3</b>. 4. South Asian serial? → <b>D4</b>. 5. Arab musalsal? → <b>D5</b>. 6. Philippine teleserye? → <b>D6</b>."]
_FAM_D["subs"] = [
    ("D1", "Telenovela", "Axis: sub-genre and industry tradition."),
    ("D2", "Soap Opera", "Axis: daypart and national industry (the field's own division)."),
    ("D3", "Dizi", "Axis: setting."),
    ("D4", "South Asian Serials", "Axis: serial genre."),
    ("D5", "Musalsal", "Axis: serial genre."),
    ("D6", "Teleserye", "Axis: none (one leaf)."),
]
_add("D1", [
    ("D1-1", "Telenovela", "broad", "the Latin American serial of a single romance resolved in one run of 100–200 episodes, Mexican, Venezuelan and Colombian (<i>Los ricos también lloran</i>, <i>Yo soy Betty, la fea</i>, <i>Café con aroma de mujer</i>).", "novela; culebrón", "D1-2 Brazilian Novela.", "Telenovela"),
    ("D1-2", "Brazilian Novela", "medium", "the Brazilian telenovela, above all TV Globo's prime-time novelas das nove (<i>Roque Santeiro</i>, <i>Avenida Brasil</i>, <i>Escrava Isaura</i>).", "novela das nove; telenovela brasileira", "D1-1 Telenovela.", "Brazilian telenovela|Telenovelas of Brazil"),
    ("D1-3", "Narconovela", "narrow", "the Colombian and Mexican telenovela of drug traffickers (<i>El Patrón del Mal</i>, <i>La Reina del Sur</i>, <i>Sin senos no hay paraíso</i>).", "narco-telenovela", "C3-3 Crime Drama Series.", "Narconovela"),
    ("D1-4", "Youth Telenovela", "narrow", "telenovelas for children and teens (<i>Chiquititas</i>, <i>Rebelde Way</i>, <i>Rebelde</i>, <i>Violetta</i>).", "juvenile telenovela", "C1-5 Teen Drama.", "Telenovela"),
])
_add("D2", [
    ("D2-1", "American Daytime Soap Opera", "medium", "US daytime serials sponsored for the home audience (<i>Guiding Light</i>, <i>General Hospital</i>, <i>Days of Our Lives</i>, <i>The Young and the Restless</i>).", "daytime soap", "D2-4 Prime-Time Soap Opera.", "Soap opera|American daytime soap opera"),
    ("D2-2", "British & Irish Soap Opera", "medium", "British and Irish continuing dramas of a community (<i>Coronation Street</i>, <i>EastEnders</i>, <i>Emmerdale</i>, <i>Fair City</i>).", "continuing drama", "D2-3 Australian Soap Opera.", "British soap opera"),
    ("D2-3", "Australian Soap Opera", "narrow", "Australian serials (<i>Neighbours</i>, <i>Home and Away</i>, <i>Prisoner</i>).", "Aussie soap", "D2-2 British Soap Opera.", "Australian soap opera"),
    ("D2-4", "Prime-Time Soap Opera", "medium", "evening serials of wealthy families, intrigue and cliffhangers (<i>Peyton Place</i>, <i>Dallas</i>, <i>Dynasty</i>, <i>Melrose Place</i>, <i>Desperate Housewives</i>).", "prime-time serial", "C1-1 Family Drama Series.", "Prime time soap opera"),
    ("D2-5", "European Soap Opera", "narrow", "the continental European daily and weekly soaps (<i>Lindenstraße</i>, <i>Gute Zeiten, schlechte Zeiten</i>, <i>Un posto al sole</i>, <i>Goede tijden, slechte tijden</i>).", "", "D2-2 British Soap Opera.", "Soap opera"),
])
_add("D3", [
    ("D3-1", "Dizi", "broad", "the Turkish weekly serial of 120–150-minute episodes, romance, family honour and class (<i>Aşk-ı Memnu</i>, <i>Fatmagül'ün Suçu Ne?</i>, <i>Kara Sevda</i>).", "Turkish drama; Turkish television drama", "D3-2 Historical Dizi.", "Turkish television drama|Dizi"),
    ("D3-2", "Historical Dizi", "medium", "Turkish serials of the Ottoman and Seljuk past (<i>Muhteşem Yüzyıl</i>, <i>Diriliş: Ertuğrul</i>, <i>Kuruluş: Osman</i>).", "Ottoman dizi", "C1-6 Period Drama Series.", "Turkish television drama"),
])
_add("D4", [
    ("D4-1", "Indian Daily Soap", "broad", "the Hindi and regional daily serial of the joint family, above all the saas-bahu (mother-in-law and daughter-in-law) serial of the 2000s (<i>Kyunki Saas Bhi Kabhi Bahu Thi</i>, <i>Kahaani Ghar Ghar Kii</i>, <i>Balika Vadhu</i>, <i>Anupamaa</i>).", "saas-bahu serial; Indian soap opera", "D4-2 Indian Mythological Serial.", "Indian soap opera"),
    ("D4-2", "Indian Mythological Serial", "medium", "serials of the epics and the gods (<i>Ramayan</i>, <i>Mahabharat</i>, <i>Devon Ke Dev...Mahadev</i>).", "mythological serial", "D4-1 Indian Daily Soap.", "Ramayan (1987 TV series)|Indian television series"),
    ("D4-3", "Pakistani Drama Serial", "medium", "the Urdu prime-time drama serial of family and romance (<i>Humsafar</i>, <i>Zindagi Gulzar Hai</i>, <i>Mere Paas Tum Ho</i>).", "Pakistani drama", "D4-1 Indian Daily Soap.", "Pakistani drama|Pakistani television dramas"),
])
_add("D5", [
    ("D5-1", "Ramadan Musalsal", "medium", "the Arab serial made for the Ramadan season, Syrian, Egyptian and Gulf (<i>Bab al-Hara</i>, <i>Al-Taghriba al-Filistiniya</i>, <i>Omar</i>).", "musalsal; Ramadan series", "C1-6 Period Drama Series.", "Ramadan series|Musalsal"),
])
_add("D6", [
    ("D6-1", "Teleserye", "medium", "the Philippine prime-time serial (<i>Pangako Sa 'Yo</i>, <i>Ang Probinsyano</i>, <i>Encantadia</i>).", "teledrama; Filipino soap opera", "C2-10 Lakorn.", "Teleserye"),
])

_FAM_G = next(f for f in FAMILIES if f["code"] == "G")
_FAM_G["test"] = "an unscripted entertainment format licensed across borders (≥3 versions in ≥2 countries), with its national versions as variants; and the East Asian variety shows of the drama database."
_FAM_G["key"] = ["1. Contestants compete for a prize or title? → <b>G1 Competition Formats</b>.",
                 "2. Real people filmed in arranged situations (dating, makeover, swaps, docusoap)? → <b>G2 Factual Entertainment Formats</b>.",
                 "3. Hosts, guests, games and talk in a studio or on location? → <b>G3 Variety & Talk</b>."]
_FAM_G["subs"] = [
    ("G1", "Competition Formats", "Axis: what is contested."),
    ("G2", "Factual Entertainment Formats", "Axis: the arranged situation."),
    ("G3", "Variety & Talk", "Axis: form."),
]
_add("G1", [
    ("G1-1", "Talent Show", "medium", "singing, dancing and variety talent contests judged by panel and public (<i>Idols</i>, <i>Got Talent</i>, <i>The Voice</i>, <i>The X Factor</i>, <i>Dancing with the Stars</i>).", "talent competition", "G3-1 Variety Show.", "talent show"),
    ("G1-2", "Reality Competition", "medium", "contestants live together or travel and are eliminated (<i>Survivor</i>, <i>Big Brother</i>, <i>The Amazing Race</i>, <i>Fort Boyard</i>).", "reality game show", "G2-1 Dating Show.", "reality competition|reality television"),
    ("G1-3", "Cooking Competition", "medium", "contests of cooks and bakers (<i>MasterChef</i>, <i>Hell's Kitchen</i>, <i>The Great British Bake Off</i>, <i>Top Chef</i>).", "cooking show", "G2-3 Makeover Show.", "cooking show"),
    ("G1-4", "Game Show", "broad", "quiz and game formats played in a studio (<i>Who Wants to Be a Millionaire?</i>, <i>Wheel of Fortune</i>, <i>The Price Is Right</i>, <i>The Chase</i>).", "quiz show", "G1-2 Reality Competition.", "game show"),
    ("G1-5", "Business Pitch Show", "narrow", "entrepreneurs pitch to investors (<i>Dragons' Den</i>, <i>Shark Tank</i>, <i>The Apprentice</i>).", "", "G1-2 Reality Competition.", "Dragons' Den|business reality television"),
])
_add("G2", [
    ("G2-1", "Dating Show", "medium", "formats of courtship and matchmaking (<i>The Dating Game</i>, <i>The Bachelor</i>, <i>Love Island</i>, <i>Married at First Sight</i>).", "dating game show", "G1-2 Reality Competition.", "dating game show|dating show"),
    ("G2-2", "Docusoap & Social Experiment", "medium", "real people followed or placed in arranged situations (<i>Wife Swap</i>, <i>The Real Housewives</i>, <i>Undercover Boss</i>, <i>Gogglebox</i>).", "docusoap; social experiment", "G2-1 Dating Show.", "docusoap"),
    ("G2-3", "Makeover Show", "medium", "transformations of people, homes and businesses (<i>Extreme Makeover</i>, <i>Queer Eye</i>, <i>Kitchen Nightmares</i>, <i>Grand Designs</i>).", "makeover television; lifestyle show", "G2-2 Docusoap & Social Experiment.", "makeover show|makeover television"),
])
_add("G3", [
    ("G3-1", "Variety Show", "medium", "entertainment programmes of games, missions, music and comedy led by a fixed cast — including the Korean and Japanese real-variety shows (<i>Running Man</i>, <i>Infinite Challenge</i>, <i>2 Days & 1 Night</i>, <i>Gaki no Tsukai</i>).", "real variety; Korean variety show", "G1-1 Talent Show.", "variety show"),
    ("G3-3", "Panel Show", "medium", "comedy panel games of a host, team captains and guests (<i>QI</i>, <i>Have I Got News for You</i>, <i>Would I Lie to You?</i>, <i>Never Mind the Buzzcocks</i>).", "panel game", "G1-4 Game Show.", "panel game"),
    ("G3-2", "Talk Show", "medium", "host-led conversation formats (<i>The Tonight Show</i> as a type, <i>Wetten, dass..?</i>, <i>Late Night</i> franchises).", "chat show", "G3-1 Variety Show.", "talk show"),
])
ATTEST_WIKI.update({
    "C1-1": "Family saga|Family drama", "C1-2": "Medical drama", "C1-3": "Legal drama", "C1-4": "Political drama", "C1-5": "Teen drama",
    "C1-6": "Costume drama", "C1-7": "War film", "C1-8": "Western (genre)", "C1-9": "Docudrama", "C1-10": "Workplace comedy",
    "C1-11": "Sports film", "C1-12": "Drama (film and television)", "C1-13": "Romance film", "C1-15": "Adventure fiction",
    "C2-1": "Korean drama", "C2-2": "Sageuk", "C2-3": "Makjang", "C2-4": "Chinese historical drama|Guzhuang", "C2-5": "Xianxia|Wuxia",
    "C2-6": "Taiwanese drama|Idol drama", "C2-7": "Asadora", "C2-8": "Taiga drama", "C2-9": "Trendy drama|Japanese television drama",
    "C2-10": "Lakorn|Thai television soap opera", "C2-11": "Boys' love in Thailand|Thai boys' love", "C3-1": "Police procedural",
    "C3-2": "Detective fiction", "C3-3": "Crime drama", "C3-4": "Nordic noir", "C3-5": "Spy fiction", "C3-6": "Thriller (genre)",
    "C3-7": "True crime", "C4-1": "Sitcom", "C4-2": "Single-camera setup", "C4-3": "Mockumentary", "C4-4": "Sketch comedy",
    "C4-5": "Comedy drama", "C4-6": "Political satire", "C5-1": "Science fiction on television", "C5-2": "Fantasy television",
    "C5-3": "Horror television", "C5-4": "Supernatural fiction", "C5-5": "Superhero fiction", "C6-1": "Animated sitcom",
    "C6-2": "Adult animation", "C6-3": "Animated series", "C6-4": "Saturday-morning cartoon", "C7-1": "Preschool television",
    "C7-2": "Children's television series", "C8-1": "Documentary television series|Docuseries", "C8-2": "True crime", "C8-3": "Nature documentary", "C1-14": "Erotic film", "D1-1": "Telenovela", "D1-2": "Brazilian telenovela|Telenovelas of Brazil",
    "D1-3": "Narconovela", "D1-4": "Telenovela", "D2-1": "American daytime soap opera|Soap opera", "D2-2": "British soap opera",
    "D2-3": "Australian soap opera", "D2-4": "Prime time soap opera", "D2-5": "Soap opera", "D3-1": "Turkish television drama",
    "D3-2": "Turkish television drama", "D4-1": "Indian soap opera", "D4-2": "Ramayan (1987 TV series)", "D4-3": "Pakistani drama",
    "D5-1": "Ramadan series|Musalsal", "D6-1": "Teleserye", "G1-1": "Talent show", "G1-2": "Reality competition|Reality television",
    "G1-3": "Cooking show", "G1-4": "Game show", "G1-5": "Dragons' Den", "G2-1": "Dating game show|Dating show", "G2-2": "Docusoap",
    "G2-3": "Makeover show|Makeover television", "G3-1": "Variety show", "G3-2": "Talk show", "G3-3": "Panel game", "C1-16": "Anthology series", "C3-8": "Domestic noir|Psychological thriller", "C4-7": "Stand-up comedy",
})

# Scale-up, round 3: seams from TV batches 11–14 and film batches 65–74.
_redef("D2-3", label="Australian & New Zealand Soap Opera", defn="Australian and New Zealand serials (<i>Neighbours</i>, <i>Home and Away</i>, <i>Prisoner</i>, <i>Shortland Street</i>).")
_redef("D2-5", defn="the continental European daily and weekly soaps and the European telenovelas outside Iberia (<i>Lindenstraße</i>, <i>Gute Zeiten, schlechte Zeiten</i>, <i>Un posto al sole</i>, <i>Inimă de țigan</i>).")
_redef("D3-2", defn="Turkish serials set before the founding of the Republic (1923), from the Seljuk and Ottoman court epics to late-Ottoman romances (<i>Muhteşem Yüzyıl</i>, <i>Diriliş: Ertuğrul</i>, <i>Kurt Seyit ve Şura</i>).")
_redef("D5-1", defn="the Arab serial made for the Ramadan season, Syrian, Egyptian, Gulf and North African (<i>Bab al-Hara</i>, <i>Al-Taghriba al-Filistiniya</i>, <i>Omar</i>, <i>Awled Moufida</i>).")
_add("D4", [
    ("D4-4", "Sri Lankan Teledrama", "narrow", "the Sinhala television serial (teledrama), from the long-running family serials to the literary adaptations (<i>Deweni Inima</i>, <i>Kopi Kade</i>).", "teledrama", "D4-1 Indian Daily Soap.", "Teledrama"),
])
_add("D5", [
    ("D5-2", "Arab Drama Serial", "narrow", "Arab serials made outside the Ramadan season, including the long pan-Arab adaptations of Turkish dizi (<i>Bride of Beirut</i>, <i>Al Hayba</i> excepted as Ramadan).", "Arab television drama", "D5-1 Ramadan Musalsal; D3-1 Dizi.", "Arab television drama"),
])
_add("C7", [
    ("C7-3", "Nordic Christmas Calendar", "narrow", "the Scandinavian Advent serial of 24 daily episodes broadcast 1–24 December, whatever its genre (<i>Jul i Skomakergata</i>, <i>The Julekalender</i>, <i>Sunes jul</i>, <i>Jul på Månetoppen</i>).", "julekalender; julkalender; Christmas calendar", "C7-2 Children's & Tween Series.", "Nordic Christmas calendar"),
])
PRECEDENCE += [
    ("TV10", "Ramadan comedies, dizi genres, Arab serials", "TV6 wins over TV9 for Ramadan comedies: a Ramadan sitcom or sketch show is C4; only Ramadan drama is D5-1. A Turkish weekly serial in the dizi format stays D3 whatever its genre (crime, action, romantic comedy); only a case-of-the-week police show is C3-1. D3-2 is any dizi set before 1923."),
    ("TV11", "Biography, youth and remakes", "A biographical or religious series of a pre-modern life (prophets, saints, Leonardo) is Period Drama (C1-6); a modern life is Docudrama (C1-9). Series about young adults past school age (college, aspirants, first jobs) go by genre (C1-12, C4-5), not Teen Drama. A remake of a series shares its original's leaf unless it changes genre (TV5)."),
    ("TV12", "Streaming serials, Christmas calendars", "A streaming serial of 60 or more episodes in a named serial tradition is D; a short web series of the same subject is C. A Nordic Advent serial is C7-3 whatever its genre. A short mythological web series is C5-2 with D4-2 as see-also."),
]
ATTEST_WIKI.update({"C7-3": "Nordic Christmas calendar", "D4-4": "Teledrama", "D5-2": "Arab television drama", "D2-3": "Australian soap opera|Shortland Street"})
PRECEDENCE += [
    ("F28", "Stage recordings, specials and visual albums", "A filmed stage production goes by its stage genre (a musical → A11-1, a stand-up show → A10-12, a play → its genre). A special of a television series that is not a compilation (the <i>South Park</i> streaming specials) is placed with its series → route:FT-C; a music or variety television special is excluded as television. A visual album or long-form music video is Musical Film (A11-1) as a feature, Live-Action Short (B2-3) at 40 minutes or less."),
    ("F29", "Creatures, homages and revenge", "Dinosaurs, giant sharks and other natural monsters are Creature Feature (A4-14) when the film aims to frighten, Science Fiction (A5-3) when it is adventure; only giant monsters of the kaiju tradition are A5-1. A recent homage to a cycle (<i>Malignant</i>, <i>MaXXXine</i>) goes by its own genre with the cycle as see-also (F23). Revenge horror stays horror (A4) when it aims to frighten; a revenge story without horror is A3-5."),
]

# Scale-up, round 4: seams from TV batches 15–21 (unscripted programmes that are not cross-border formats).
_FAM_G["test"] = "unscripted entertainment television: the formats licensed across borders (≥3 versions in ≥2 countries, national versions as variants), the East Asian variety shows of the drama database, and the domestic unscripted programmes of the series selection (talk, variety, reality, court and instructional shows)."
_redef("G2-2", defn="real people followed or placed in arranged situations, including occupational and paranormal-investigation reality (<i>Wife Swap</i>, <i>The Real Housewives</i>, <i>Deadliest Catch</i>, <i>Dirty Jobs</i>, <i>Ghost Hunters</i>, <i>Jackass</i>).")
_redef("G3-1", defn="entertainment programmes of games, missions, music and comedy led by a fixed cast or host, and broadcasts of concerts and stage performances — including the Korean and Japanese real-variety shows (<i>Running Man</i>, <i>Infinite Challenge</i>, <i>2 Days & 1 Night</i>, <i>The Ed Sullivan Show</i>, <i>Austin City Limits</i>).")
_redef("G3-2", defn="host-led conversation programmes, late-night and daytime (<i>The Tonight Show</i>, <i>Late Show with David Letterman</i>, <i>The Daily Show</i>, <i>Wetten, dass..?</i>).")
_add("G3", [
    ("G3-4", "Court Show", "narrow", "arbitration of real small-claims disputes before a television judge (<i>The People's Court</i>, <i>Judge Judy</i>, <i>Judge Rinder</i>).", "judge show", "C1-3 Legal Drama Series.", "Court show"),
    ("G3-5", "Instructional & Lifestyle Show", "medium", "programmes that teach a craft, cooking, painting or home skill (<i>The French Chef</i>, <i>The Joy of Painting</i>, <i>Good Eats</i>, <i>This Old House</i>).", "how-to show; cooking show", "G1-3 Cooking Competition; G2-3 Makeover Show.", "Instructional television|Cooking show"),
    ("G3-6", "Web Show", "medium", "unscripted online video series of a host or channel (<i>Good Mythical Morning</i>, <i>Hot Ones</i>, <i>Everything Wrong With</i>, PewDiePie); scripted web series go by genre in C.", "YouTube show; online show", "G3-2 Talk Show.", "Web series"),
])
PRECEDENCE += [
    ("TV13", "Unscripted programmes and edge genres", "A talk, variety, reality, court, instructional or web show is placed in G directly, whether or not it is a licensed format (G2-2 for occupational and paranormal reality, G3-4 for court shows, G3-5 for how-to shows); professional wrestling is G3-1. A documentary series with reenactments is C8 when talking heads and archive carry it, C1-9 when dramatised scenes do. A disaster miniseries is Action & Adventure (C1-15). A US re-edit or dub of an anime is anime (route:FT-E). A defence-lawyer series is Legal Drama (C1-3) when the cases change each week, Crime Drama (C3-3) when a season follows one crime; a lawyer dramedy stays C1-3 with C4-5 as see-also. A 2000s–2010s network serial of secrets among the rich (<i>Revenge</i>, <i>Gossip Girl</i>) is Prime-Time Soap Opera (D2-4); a teen mystery (<i>Pretty Little Liars</i>) is Thriller (C3-6)."),
]
ATTEST_WIKI.update({"G3-4": "Court show", "G3-5": "Instructional television|Cooking show", "G3-6": "Web series"})
PRECEDENCE += [
    ("TV14", "Streaming originals in a serial tradition; sports", "A streaming original of a closed season (8–20 episodes) from a serial-tradition country (a Netflix or BluTV Turkish series, a streaming telenovela) goes by genre in C; the broadcast weekly or daily serial is D. A remake that leaves its original's tradition goes by its own form (a 60-episode Turkish broadcast remake of <i>Doctor Foster</i> is D3-1). An anthology of crime or suspense stories is C1-16 Anthology with the genre as see-also. Live sports coverage is not a series of this tab: exclude it."),
]

# Scale-up, round 5: seams from TV batches 23–31 and drama batches 01–04.
_redef("C2-6", label="Idol & Modern Romance Drama", defn="Taiwanese and Chinese drama of modern romance: the idol drama of pop-idol casts from <i>Meteor Garden</i> (2001), and the modern Chinese campus, urban, workplace and fantasy romances that followed (<i>It Started with a Kiss</i>, <i>Go Go Squid!</i>, <i>Hidden Love</i>).")
_redef("C2-5", defn="Chinese drama of martial heroes (wuxia), of immortal cultivation and celestial romance (xianxia), and of gods and demons (shenmo) (<i>The Legend of the Condor Heroes</i>, <i>The Untamed</i>, <i>Eternal Love</i>, <i>Journey to the West</i>).", aliases="wuxia drama; xianxia drama; shenmo drama")
_redef("C2-11", label="Boys' Love & Girls' Love Drama", defn="BL and GL series — romance between young men or between young women — from Thailand, Taiwan, Japan, Korea and China (<i>SOTUS</i>, <i>2gether</i>, <i>Bad Buddy</i>, <i>Cherry Magic!</i>, <i>GAP</i>).")
_redef("C6-2", defn="non-comedy animation for adults (<i>Invincible</i>, <i>Primal</i>, <i>Love, Death & Robots</i>, <i>Blue Eye Samurai</i>).")
_redef("C3-3", defn="series of fictional criminals and their world (<i>The Sopranos</i>, <i>The Wire</i>, <i>Breaking Bad</i>, <i>Peaky Blinders</i>) (TV4).")
_redef("C1-9", defn="dramatisations of real events and lives that are not crimes (<i>Chernobyl</i>, <i>The Crown</i> excepted as period, <i>The Dropout</i>, <i>WeCrashed</i>).")
_add("C2", [
    ("C2-12", "Main-Melody Drama", "medium", "the Chinese state-endorsed drama of revolutionary history, Party leaders and national achievement (<i>The Age of Awakening</i>, <i>Minning Town</i>, <i>Medal of the Republic</i>, <i>Mao Zedong</i>).", "zhuxuanlü; red drama", "C1-9 Docudrama Series; C1-7 War Drama Series.", "Main-melody film"),
    ("C2-13", "Republican-Era Drama", "narrow", "Chinese drama set in the Republic of China (1912–1949): romance, spy and family sagas of Shanghai and the warlord years (<i>Winter Begonia</i>, <i>Siege in Fog</i>, <i>Romance in the Rain</i>, <i>The Disguiser</i>).", "minguo drama", "C2-4 Chinese Costume Drama; C3-5 Spy & Espionage Series.", ""),
])
_add("C1", [
    ("C1-17", "Vertical Short Drama", "narrow", "serials of one- to two-minute vertical episodes made for short-drama apps, mostly melodramatic romance and revenge (ReelShort, DramaBox).", "micro-drama; vertical drama; short drama", "C1-13 Romantic Drama Series.", "Vertical drama|Microdrama"),
])
ATTEST_WIKI.update({"C2-12": "Main-melody film", "C2-13": "", "C1-17": "Vertical drama|Microdrama", "C2-11": "Boys' love|Yuri (genre)"})
ATTEST_URLS["C2-13"] = "https://en.wikipedia.org/wiki/Chinese_television_drama"
WEAK["C2-13"] = "no article under this label; attested through the Chinese television drama article"
PRECEDENCE += [
    ("TV15", "C-drama traditions", "A Chinese drama of the Party, the revolution or national achievement is Main-Melody Drama (C2-12) whatever its genre; one set in 1912–1949 is Republican-Era Drama (C2-13); a modern Chinese romance of any kind is C2-6. A censored danmei adaptation goes by its setting (<i>The Untamed</i> → C2-5) with C2-11 as see-also; a modern-day one is C2-11. A costume drama goes to C2-5 when martial heroes or a fantasy world carry the story, otherwise C2-4."),
    ("TV16", "Remakes, spin-offs, rich-family serials", "A foreign remake keeps its original's leaf only when it keeps its form; it goes by its own setting when moved (a US remake of a Nordic series is C3-1, not C3-4). A spin-off that moves to another workplace goes by its own profession. A streaming or 2020s series of rich-family secrets with a closed season is C (C1-1 or C3-8) with D2-4 as see-also; the D2-4 rule of TV13 holds only for network serials of 2000–2019 and long-running streaming serials (TV12)."),
]

# Scale-up, round 6: seams from drama batches 05–11.
_redef("C2-9", label="Japanese Television Drama", defn="the Japanese drama series (dorama) of romance, school, work and everyday life in one-cour seasons, from the trendy dramas of Fuji TV's Monday 9 pm slot to the late-night and streaming manga adaptations (<i>Tokyo Love Story</i>, <i>Long Vacation</i>, <i>Hana Yori Dango</i>, <i>Nigeru wa Haji da ga Yaku ni Tatsu</i>).", aliases="dorama; J-drama; trendy drama; getsuku")
_add("C2", [
    ("C2-14", "TVB Drama", "medium", "the Hong Kong television drama of TVB and its rivals, modern and costume, in 20–40-episode serials (<i>The Greed of Man</i>, <i>War and Beauty</i>, <i>Triumph in the Skies</i>, <i>Line Walker</i>).", "Hong Kong television drama; TVB series", "C2-4 Chinese Costume Drama; C2-5 Wuxia & Xianxia Drama.", "TVB drama|Hong Kong television drama"),
])
_add("C5", [
    ("C5-6", "Tokusatsu Series", "medium", "the Japanese live-action special-effects hero series and their adaptations, for children and adults alike (<i>Ultraman</i>, <i>Kamen Rider</i>, <i>Super Sentai</i>, <i>Power Rangers</i>, <i>Garo</i>).", "tokusatsu; henshin hero series", "E2-6 Mecha & Tokusatsu Anime; C5-5 Superhero Series.", "Tokusatsu"),
])
ATTEST_WIKI.update({"C2-14": "TVB drama|Hong Kong television drama", "C5-6": "Tokusatsu", "C2-9": "Japanese television drama|Trendy drama"})
PRECEDENCE += [
    ("TV17", "Japanese and Hong Kong drama; tokusatsu", "Every Japanese drama of romance, school, work, family or everyday life is C2-9; Japanese crime, mystery, medical, legal and speculative dramas go by genre with C2-9 as see-also. A Hong Kong drama is C2-14 unless it is wuxia (C2-5); Hong Kong BL is C2-11. A tokusatsu series is C5-6 whatever its audience (Power Rangers included); a tokusatsu parody comedy is C4. A foreign remake of an Asian drama made inside another tradition goes to the remaking tradition (a Japanese remake of a K-drama is C2-9) with the original's leaf as see-also. A New Year or one-off special is route:FT-A; a re-edit or complete edition of a series is excluded as a duplicate."),
]
