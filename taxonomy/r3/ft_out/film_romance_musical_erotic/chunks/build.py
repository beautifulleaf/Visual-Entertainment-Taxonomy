import csv, json, glob, os
D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(D)
ROOT = os.path.join(OUT, "..", "..", "..", "..")
W = "https://en.wikipedia.org/wiki/"
def w(a): return [W + a, "Wikipedia"]

# key: (label, breadth, defn, aliases, see, src, axis, secs)
SUBS = [
 ("A13", "Romance", "Axis: by the love-story engine, what draws the lovers together or keeps them apart; dramatic engines first (obstacle, suffering, obsession, betrayal, the couple itself, war, period, youth, queer love), then the comic engines of the romantic comedy, the romantic fantasy last.", [
  ("STAR", "Star-Crossed Romance", "medium",
   "A love story whose engine is an outside force forbidding the match: feuding families, class or caste, religion or ethnicity, custom, state or law (<i>Romeo + Juliet</i>, <i>Bombay</i>, <i>Jungle Fever</i>, <i>Cold War</i>). A comic treatment of the same obstacle goes to the romantic-comedy leaves; a wartime separation goes to A13-6.",
   "forbidden love; star-crossed lovers; interracial romance film", "A13-6 Wartime Romance; A13-7 Period Romance",
   [w("Star-crossed"), w("List_of_interracial_romance_films")], "by the force that forbids the match: feuding families, class, faith and ethnicity, custom and state",
   ["Romeo and Juliet Stories", "Class-Crossed Love", "Interfaith, Interethnic & Interracial Love", "Love Against Custom & State"]),
  ("MELO", "Romantic Melodrama & Weepie", "broad",
   "A love story built to move the audience to tears through suffering, sacrifice, illness, death or loss (<i>Now, Voyager</i>, <i>Love Story</i>, <i>The Fault in Our Stars</i>, <i>The Notebook</i>). The tearjerker and the woman's film; an obsessive, self-destroying love goes to A13-3.",
   "tearjerker; weepie; woman's film; sick-lit romance", "A13-3 Amour Fou; A16 Drama",
   [w("Melodrama_(film_genre)"), w("Woman%27s_film"), w("Tearjerker")], "by the source of the tears: sacrifice, illness, grief, lost memory, sentimental small-town romance last",
   ["Woman's Film & Sacrificial Melodrama", "Illness & Dying-Lover Weepies", "Grief & Widowhood Romances", "Amnesia & Memory-Loss Romances", "Sentimental Small-Town Romances"]),
  ("AMOUR", "Amour Fou & Obsessive Love", "medium",
   "A love story whose engine is the lovers' own excessive, possessive or self-destroying passion rather than an outside obstacle (<i>Devdas</i>, <i>Leaving Las Vegas</i>, <i>Loulou</i>, <i>Kabir Singh</i>). Where sex itself is the subject the title goes to A15-1.",
   "amour fou; mad love; obsessive love; toxic romance", "A15-1 Erotic Drama; A3 Thriller & Mystery",
   [w("Obsessive_love"), w("Amour_fou")], "by the form the excess takes: self-destructive devotion, possession and jealousy, lovers outside the law",
   ["Self-Destructive Devotion", "Possessive & Jealous Love", "Outlaw Lovers"]),
  ("ADUL", "Adultery & Love Triangle", "medium",
   "A love story driven by a third party: an affair, a betrayal of marriage, two rivals for one heart, or a temptation resisted (<i>Brief Encounter</i>, <i>In the Mood for Love</i>, <i>Closer</i>, <i>My Night at Maud's</i>). A comic triangle goes to the romantic-comedy leaves.",
   "infidelity drama; love triangle; affair film", "A13-5 Relationship Drama",
   [w("Love_triangle"), w("Infidelity")], "by what the third party does: a brief or unconsummated affair, adultery, the triangle, the temptation tale",
   ["Brief Affairs & Unconsummated Love", "Adultery & Marital Betrayal", "Love Triangles", "Temptation & Fidelity Tales"]),
  ("REL", "Relationship Drama", "broad",
   "A love story with no outside obstacle whose subject is one couple's relationship itself: its chance beginning, its course over years, separation by distance, breakdown, or love late in life (<i>Before Sunrise</i>, <i>Past Lives</i>, <i>Blue Valentine</i>, <i>Like Crazy</i>). An affair or triangle goes to A13-4; a weepie of illness to A13-2.",
   "couple drama; brief encounter; long-distance romance; May-December romance", "A13-4 Adultery & Love Triangle; A16 Drama",
   [w("Romance_film"), w("Long-distance_relationship"), w("Age_disparity_in_sexual_relationships")], "by the span of the relationship shown: one encounter, years, distance, crisis, late life",
   ["Chance Encounters", "A Couple over the Years", "Long-Distance & Epistolary Love", "Breakups & Marital Crisis", "Late-Life & May–December Love"]),
  ("WAR", "Wartime Romance", "narrow",
   "A love story whose engine is war: lovers met, parted or endangered by a war that stays in the background of the romance (<i>Casablanca</i>, <i>Waterloo Bridge</i>, <i>The English Patient</i>, <i>Dear John</i>). A film about the fighting goes to A9.",
   "war romance", "A9 War Film; A13-7 Period Romance",
   [w("War_film"), w("Romance_film")], None, None),
  ("PER", "Period Romance", "medium",
   "A love story set in a reconstructed past, where period manners, dress and social codes shape the courtship: classic novel adaptations and original period love stories (<i>Wuthering Heights</i>, <i>Titanic</i>, <i>Far and Away</i>, <i>Lady Chatterley's Lover</i>). Heritage romance; a wartime love story goes to A13-6.",
   "historical romance; costume romance; heritage romance", "A8 Historical & Period Film; A13-6 Wartime Romance",
   [w("Heritage_film"), w("Romance_novel")], "by source: adaptation of a literary classic, then original period story",
   ["Literary Classic Adaptations", "Original Period Love Stories"]),
  ("TEEN", "Teen Romance", "broad",
   "A love story whose lovers are adolescents or just past adolescence, built on first love, school and youth (<i>Say Anything...</i>, <i>The Spectacular Now</i>, <i>To All the Boys I've Loved Before</i>, <i>After</i>). Queer teen love goes to A13-9; a teen weepie of illness to A13-2.",
   "first love film; high-school romance; new adult romance; teen romantic comedy", "A13-9 LGBTQ+ Romance; A17 Children's & Family Film",
   [w("Teen_film"), w("New_adult_fiction")], "by the youth setting and tone: first love, high-school drama, teen comedy, new-adult bad-boy romance",
   ["First Love & Summer Romance", "High-School Romance", "Teen Romantic Comedy", "New-Adult & Bad-Boy Romance"]),
  ("LGBT", "LGBTQ+ Romance", "broad",
   "A love story between lovers of the same sex or across gender identity, where queer desire is the romance (<i>Brokeback Mountain</i>, <i>Carol</i>, <i>Call Me by Your Name</i>, <i>Fire Island</i>). A queer movement film of the early 1990s goes to A1.",
   "queer romance; gay romance; lesbian romance; sapphic romance", "A1 Movements & Schools (New Queer Cinema); A13-8 Teen Romance",
   [w("List_of_LGBTQ-related_films"), w("New_queer_cinema")], "by the lovers and the tone: gay men, women (incl. trans women), queer first love, queer romantic comedy",
   ["Gay Male Romance", "Lesbian & Sapphic Romance", "Queer First Love & Coming Out", "Queer Romantic Comedy"]),
  ("SCREW", "Screwball Comedy", "narrow",
   "A fast, farcical romantic comedy of verbal sparring, class mix-ups and a dominant heroine, in the 1930s–40s cycle and its later revivals (<i>Vivacious Lady</i>, <i>Woman of the Year</i>, <i>Something Wild</i>, <i>Intolerable Cruelty</i>). A quieter comedy of manners goes to A13-12.",
   "screwball; neo-screwball", "A13-12 Romantic Comedy of Manners; A12 Comedy",
   [w("Screwball_comedy_film")], None, ["Classic Screwball", "Neo-Screwball"]),
  ("PINK", "Pink Neorealism", "narrow",
   "Italian 1950s romantic comedy that keeps neorealism's poor settings and non-star manner but turns them to sentimental courtship (<i>Two Cents Worth of Hope</i>). Neorealismo rosa.",
   "neorealismo rosa", "A1 Movements & Schools (Italian neorealism)",
   [w("Pink_neorealism")], None, None),
  ("MANN", "Romantic Comedy of Manners", "medium",
   "A witty, talk-driven romantic comedy whose engine is the social and sexual manners of a milieu, usually urban, sophisticated or literary (<i>Ninotchka</i>, <i>Smiles of a Summer Night</i>, <i>Annie Hall</i>, <i>Bridget Jones's Diary</i>). A farcical screwball goes to A13-10.",
   "sophisticated comedy; Lubitsch touch; urban romantic comedy", "A13-10 Screwball Comedy; A12 Comedy",
   [w("Comedy_of_manners"), w("Romantic_comedy")], "by milieu and source: continental sophistication, urban neurosis, Shakespeare and Austen, ensemble roundelay",
   ["Continental Sophisticated Comedy", "Urban Neurotic Comedy", "Shakespearean & Austen Comedy", "Ensemble Roundelay"]),
  ("SEX", "Sex Comedy", "medium",
   "A romantic comedy whose engine is sex and the rules of dating: seduction, sexual mores, hook-ups and the failures of the dating market (<i>Pillow Talk</i>, <i>There's Something About Mary</i>, <i>Knocked Up</i>, <i>How to Be Single</i>). A teen sex comedy goes to A12.",
   "sex comedy; gross-out romantic comedy; dating comedy", "A12 Comedy; A13-17 Friends to Lovers",
   [w("Sex_comedy")], "by era and register: Hollywood sex comedy, gross-out romantic comedy, hook-up and dating comedy",
   ["Hollywood Sex Comedy", "Gross-Out Romantic Comedy", "Hook-Up & Dating Comedy"]),
  ("MEET", "Meet-Cute Romantic Comedy", "medium",
   "A romantic comedy whose engine is the contrived or fated first meeting and the near misses that follow, including courtship by letter and the romance of a trip (<i>Sleepless in Seattle</i>, <i>Serendipity</i>, <i>You've Got Mail</i>, <i>French Kiss</i>). The friends who were already there go to A13-17.",
   "meet cute; destiny romcom; epistolary romance; holiday romance", "A13-5 Relationship Drama (Chance Encounters)",
   [w("Meet_cute")], "by how the lovers meet: fate and near misses, letters and screens, a journey abroad",
   ["Destiny & Near-Miss", "Epistolary & Pen-Pal", "Holiday-Abroad Romance"]),
  ("ENEM", "Enemies to Lovers", "medium",
   "A romantic comedy whose couple begins in hostility, rivalry or total mismatch and fights its way to love (<i>The Quiet Man</i>, <i>The Ugly Truth</i>, <i>Hum Tum</i>, <i>Anyone But You</i>). Battle-of-the-sexes and opposites-attract comedy; rivals at work go to A13-19.",
   "battle of the sexes; opposites attract; bickering couple", "A13-10 Screwball Comedy; A13-19 Workplace Romantic Comedy",
   [w("Romance_novel")], None, ["Bickering Rivals", "Opposites Attract"]),
  ("FAKE", "Fake Relationship", "medium",
   "A romantic comedy whose engine is a pretence: a fake engagement or marriage of convenience, a bet, a disguise or mistaken identity, or a matchmaker's scheme (<i>Green Card</i>, <i>The Proposal</i>, <i>How to Lose a Guy in 10 Days</i>, <i>Hitch</i>). A teen bet comedy goes to A13-8.",
   "fake dating; marriage of convenience; romantic deception; Cyrano comedy", "A13-15 Enemies to Lovers; A13-20 Wedding Comedy",
   [w("Romance_novel"), w("Romantic_comedy")], "by the kind of pretence: fake couple, wager, disguise, matchmaking scheme",
   ["Fake Dating & Marriages of Convenience", "Bets & Wagers", "Disguise & Mistaken Identity", "Matchmakers & Cyrano Schemes"]),
  ("FRIEND", "Friends to Lovers", "medium",
   "A romantic comedy whose engine is a friendship that turns, slowly or suddenly, into love, including the friends-with-benefits arrangement (<i>When Harry Met Sally...</i>, <i>Love, Rosie</i>, <i>Jaane Tu... Ya Jaane Na</i>, <i>Friends with Benefits</i>). A dramatic version spanning years goes to A13-5.",
   "friends to lovers; friends with benefits; friend zone", "A13-5 Relationship Drama; A13-13 Sex Comedy",
   [w("Romantic_comedy"), w("Romance_novel")], None, ["Friends Becoming Lovers", "Friends with Benefits"]),
  ("CIND", "Cinderella Story", "medium",
   "A romantic comedy whose engine is a match across wealth or rank in which one lover is raised into the other's world: makeover, royalty, celebrity (<i>Pretty Woman</i>, <i>Roman Holiday</i>, <i>Notting Hill</i>, <i>Maid in Manhattan</i>). A forbidding, tragic class divide goes to A13-1.",
   "Cinderella story; rags to riches romance; royal romance", "A13-1 Star-Crossed Romance",
   [w("Cinderella"), w("Rags_to_riches")], "by the higher world entered: wealth and makeover, royalty and power, celebrity",
   ["Cinderella & Makeover", "Royal & Political Romance", "Celebrity & Commoner Romance"]),
  ("WORK", "Workplace Romantic Comedy", "narrow",
   "A romantic comedy whose couple meets and spars through a shared job, office or profession (<i>Desk Set</i>, <i>Office Romance</i>, <i>Working Girl</i>, <i>Two Weeks Notice</i>). Career-woman comedy; workplace enemies with no job plot go to A13-15.",
   "office romance; career woman comedy", "A13-15 Enemies to Lovers",
   [w("Workplace_romance"), w("Romantic_comedy")], None, None),
  ("WED", "Wedding Comedy", "medium",
   "A romantic comedy organised around a wedding: brides and planners, guests and crashers, or the clash of two families and arranged matches (<i>Four Weddings and a Funeral</i>, <i>My Best Friend's Wedding</i>, <i>My Big Fat Greek Wedding</i>, <i>Band Baaja Baaraat</i>). A wedding as one scene only does not count.",
   "wedding film; meet-the-parents comedy; arranged-marriage comedy", "A13-16 Fake Relationship; A12 Comedy",
   [w("Wedding_film"), w("Arranged_marriage")], "by who drives the comedy: the couple and their wedding, the guests, the families",
   ["Brides, Grooms & Wedding Planning", "Wedding Guests & Crashers", "Meet-the-Family & Arranged Marriage"]),
  ("HOL", "Holiday Romantic Comedy", "narrow",
   "A romantic comedy built on a calendar holiday that sets its deadline and mood: Christmas, New Year, Valentine's Day (<i>The Irony of Fate</i>, <i>Valentine's Day</i>, <i>Holidate</i>). Christmas only as backdrop does not count.",
   "Christmas romcom; New Year comedy", "A13-12 Romantic Comedy of Manners (Ensemble Roundelay)",
   [w("Christmas_film")], None, None),
  ("CDR", "Romantic Comedy-Drama", "medium",
   "A romantic comedy played half-seriously, whose obstacle lies in the lovers' own eccentricity, damage, family burdens or age (<i>Moonstruck</i>, <i>As Good as It Gets</i>, <i>Silver Linings Playbook</i>, <i>Something's Gotta Give</i>). A purely dramatic treatment goes to A13-5.",
   "romantic dramedy; seriocomic romance", "A13-5 Relationship Drama; A16 Drama",
   [w("Comedy-drama"), w("Romantic_comedy")], "by the lovers' burden: eccentricity, damage or illness, children and second chances, age, a homecoming",
   ["Deadpan & Eccentric Lovers", "Damaged & Healing Lovers", "Single Parents & Second Chances", "Age-Gap & Late-Life Love Comedy", "Homecoming & Small-Town Romance"]),
  ("FANT", "Romantic Fantasy", "broad",
   "A love story, dramatic or comic, whose engine is a fantastic or speculative device: ghosts and afterlife, time travel, supernatural creatures, machines, magic or a time loop (<i>Ghost</i>, <i>Somewhere in Time</i>, <i>Twilight</i>, <i>Her</i>, <i>Palm Springs</i>). Where the device dominates and love is secondary the title goes to A5 or A6.",
   "paranormal romance; time-travel romance; supernatural romance; science-fiction romance", "A5 Science Fiction; A6 Fantasy & Adventure",
   [w("Romantic_fantasy"), w("Paranormal_romance"), w("Time-travel_romance")], "by the fantastic device: ghost, time travel, creature, machine, magic, loop or parallel life",
   ["Ghost & Afterlife Romance", "Time-Travel & Time-Slip Romance", "Paranormal & Creature Romance", "Science-Fiction & AI Romance", "Magic, Curse & Body-Switch Romance", "Time-Loop & Parallel-Life Romance"]),
 ]),
 ("A14", "Musical & Dance Film", "Axis: by how music and dance enter the story: integrated song (book musical, operetta), song as performance (revue, backstage), all-sung forms, rock and pop forms, recorded stage shows, dance, and films about musicians without musical numbers last.", [
  ("BOOK", "Book Musical", "broad",
   "A musical film whose songs and dances arise inside the story and carry plot and character, written for the screen or adapted from the stage (<i>Top Hat</i>, <i>Meet Me in St. Louis</i>, <i>West Side Story</i>, <i>La La Land</i>). Numbers staged as performances go to A14-4; an all-sung film to A14-5.",
   "integrated musical; film musical; stage-musical adaptation", "A14-4 Backstage Musical; A14-5 Opera Film",
   [w("Book_musical"), w("Musical_film")], "by origin and audience: Hollywood studio originals, Broadway adaptations, family musicals, teen musicals, later screen originals, other film-musical traditions",
   ["Hollywood Studio Musicals", "Broadway Adaptations", "Family & Fantasy Musicals", "Teen & High-School Musicals", "Contemporary Screen Originals", "European & World Film Musicals"]),
  ("OPER", "Operetta Film", "narrow",
   "A musical film in the operetta tradition, light romantic plots in a mythical Ruritania or old Europe told through sung waltzes and duets (<i>The Love Parade</i>, <i>Love Me Tonight</i>, <i>Naughty Marietta</i>, <i>Ulduz</i>).",
   "film operetta; Operettenfilm", "A14-1 Book Musical; A14-5 Opera Film",
   [w("Operetta_film")], None, None),
  ("REVUE", "Revue Film", "narrow",
   "A plotless or nearly plotless film made of separate musical and comic numbers, the screen form of the stage revue (<i>King of Jazz</i>, <i>Ziegfeld Follies</i>).",
   "film revue", "A14-4 Backstage Musical",
   [w("Revue")], None, None),
  ("BACK", "Backstage Musical", "medium",
   "A musical film about putting on a show, whose numbers are staged as performances within the story (<i>42nd Street</i>, <i>Singin' in the Rain</i>, <i>The Band Wagon</i>, <i>Cabaret</i>). Integrated numbers go to A14-1; a musician's story without numbers goes to A14-13.",
   "backstager; show musical", "A14-1 Book Musical; A14-13 Music Film",
   [w("Backstage_musical")], "by the stage: Broadway and revue, Hollywood and stardom, cabaret and nightclub",
   ["Broadway & Revue Backstage", "Hollywood & Stardom", "Cabaret, Nightclub & Showgirl"]),
  ("OPERA", "Opera Film & Sung-Through Musical", "narrow",
   "A film entirely or almost entirely sung: a filmed or adapted opera, a sung-through screen musical, or a traditional sung music-theatre form (<i>The Tales of Hoffmann</i>, <i>The Umbrellas of Cherbourg</i>, <i>Chunhyang</i>, <i>Annette</i>). A rock opera goes to A14-6.",
   "film-opera; opera film; sung-through musical; pansori film", "A14-6 Rock Opera & Rock Musical",
   [w("Opera_film"), w("Sung-through")], None, ["Filmed & Adapted Opera", "Sung-Through Screen Musicals", "Traditional Music-Theatre Forms"]),
  ("ROCK", "Rock Opera & Rock Musical", "narrow",
   "A musical film set to rock music, a sung rock narrative or stage rock musical (<i>Tommy</i>, <i>Jesus Christ Superstar</i>, <i>The Rocky Horror Picture Show</i>, <i>Hedwig and the Angry Inch</i>). A musical built on existing hits goes to A14-7.",
   "rock opera; rock musical", "A14-7 Jukebox Musical; A14-5 Opera Film",
   [w("Rock_opera"), w("Rock_musical")], None, None),
  ("JUKE", "Jukebox Musical", "narrow",
   "A musical film whose numbers are previously released popular songs, often one artist's catalogue (<i>Mamma Mia!</i>, <i>Across the Universe</i>, <i>Moulin Rouge!</i>, <i>Sunshine on Leith</i>). A biopic of the artist goes to A11.",
   "jukebox musical", "A11 Biographical Film; A14-6 Rock Opera & Rock Musical",
   [w("Jukebox_musical")], None, None),
  ("STARV", "Pop Star Vehicle", "narrow",
   "A fiction film built to showcase a singer or band playing a version of themselves through their songs (<i>Jailhouse Rock</i>, <i>A Hard Day's Night</i>, <i>Purple Rain</i>, <i>Spice World</i>). A concert record goes to A19.",
   "star vehicle; Elvis musical; band film", "A19 Documentary (concert film); A14-10 Visual Album",
   [w("Star_vehicle")], None, None),
  ("STAGE", "Filmed Stage Musical", "narrow",
   "A recording of a stage musical as performed in the theatre, or broadcast live, rather than re-made for the camera (<i>Hamilton</i>, <i>Cats</i> (1998), <i>Grease Live!</i>). Weakly attested label (trade: pro-shot); a screen adaptation goes to A14-1.",
   "pro-shot; filmed theatre; live television musical", "A14-1 Book Musical; B16 Live Event & Sports Television",
   [w("Musical_film"), w("Musical_theatre")], None, ["Pro-Shot Theatre Recordings", "Live Television Musicals"]),
  ("VIS", "Visual Album", "narrow",
   "A feature-length film made to accompany a music album, its songs strung into an impressionistic narrative (<i>Lemonade</i>, <i>Dirty Computer</i>, <i>Black Is King</i>).",
   "visual album", "A14-8 Pop Star Vehicle; A20 Experimental & Avant-Garde",
   [w("Visual_album")], None, None),
  ("DANCE", "Dance Film", "medium",
   "A fiction film whose story is carried by dance and dancers, its climaxes danced performances or competitions (<i>The Red Shoes</i>, <i>Saturday Night Fever</i>, <i>Dirty Dancing</i>, <i>Step Up</i>). A sung musical goes to A14-1.",
   "dance movie; ballet film; street-dance film", "A14-1 Book Musical; A14-4 Backstage Musical",
   [w("Dance_film")], "by the dance form: ballet and concert dance, flamenco, ballroom and social dance, disco and teen dance, street and hip-hop, striptease",
   ["Ballet & Concert Dance", "Flamenco Dance Film", "Ballroom & Social Dance", "Disco & Teen Dance", "Street & Hip-Hop Dance", "Striptease & Burlesque Dance"]),
  ("RUMB", "Rumberas Film", "narrow",
   "Mexican golden-age cabaret melodrama starring a rumba dancer, the rumbera (<i>Victims of Sin</i>).",
   "cine de rumberas", "A14-11 Dance Film",
   [w("Rumberas_film")], None, None),
  ("MUSIC", "Music Film", "broad",
   "A fiction film about musicians and music-making whose music is performed in the story but which is not a musical: bands, singers, players, teachers, contests (<i>Whiplash</i>, <i>Once</i>, <i>8 Mile</i>, <i>Pitch Perfect</i>). A biopic of a real musician goes to A11; a documentary to A19.",
   "film about musicians; band film; music-competition film", "A11 Biographical Film; A14-4 Backstage Musical",
   [w("Musical_film")], "by the music world: jazz and blues, bands and rock, hip-hop and DJ, singers and stardom, choirs and classical, family, contests last",
   ["Jazz & Blues Lives", "Bands & Rock Dreams", "Hip-Hop, DJ & Electronic", "Singers & Stardom", "Choirs, Classical Music & Teachers", "Music & Family", "Competitions & Battles of the Bands"]),
 ]),
 ("A15", "Erotic Film", "Axis: by how sex drives the film and the production tradition: art-house erotic drama first, erotic thriller, then softcore and exploitation traditions, national erotic cycles last.", [
  ("EDR", "Erotic Drama", "medium",
   "A narrative film whose subject is sexual desire, practice or obsession, shown explicitly as the core of the drama (<i>Last Tango in Paris</i>, <i>In the Realm of the Senses</i>, <i>Secretary</i>, <i>Fifty Shades of Grey</i>). A love story with sex scenes goes to A13; a suspense plot to A15-2.",
   "erotic art film; erotic romance", "A13-3 Amour Fou; A15-2 Erotic Thriller",
   [w("Erotica"), w("Unsimulated_sex")], "by the erotic engine: awakening, obsession and transgression, sadomasochism, unsimulated sex, bestseller erotic romance",
   ["Sexual Awakening", "Obsession & Transgression", "Sadomasochism & Power Games", "Unsimulated-Sex Art Film", "Erotic Romance Bestsellers"]),
  ("ETH", "Erotic Thriller", "narrow",
   "A thriller whose suspense is driven by sexual desire, seduction or perversity (<i>The Housemaid</i>, <i>Eyes Wide Shut</i>, <i>A Snake of June</i>). A mainstream erotic thriller led by crime goes to A3.",
   "erotic thriller", "A3 Thriller & Mystery",
   [w("Erotic_thriller")], None, None),
  ("SOFT", "Softcore Film", "narrow",
   "A film of simulated sex made for erotic display, often in the European erotic tradition (<i>Immoral Tales</i>, <i>Vampyros Lesbos</i>, <i>Delta of Venus</i>).",
   "softcore; Euro-erotica", "A15-4 Sexploitation",
   [w("Softcore_pornography")], None, None),
  ("SEXP", "Sexploitation", "narrow",
   "A low-budget independent film made to exploit sex and nudity, from roadshow sex-hygiene films to Russ Meyer and nunsploitation (<i>Mom and Dad</i>, <i>Faster, Pussycat! Kill! Kill!</i>, <i>Ilsa, the Wicked Warden</i>).",
   "sexploitation; nudie-cutie; nunsploitation", "A18 Popular Cinema Modes; A4 Horror",
   [w("Sexploitation_film"), w("Nunsploitation")], None, None),
  ("PINKF", "Pink Film", "narrow",
   "Japanese theatrical softcore cinema (pinku eiga) of the independent studios and Nikkatsu's Roman Porno line. Kept as an attested canon although no title in the present corpus belongs here.",
   "pinku eiga; Roman Porno; Nikkatsu Roman Porno", "A15-3 Softcore Film",
   [w("Pink_film")], None, None),
  ("PORNO", "Pornochanchada", "narrow",
   "Brazilian erotic comedy and drama of the 1970s–80s made around São Paulo's Boca do Lixo (<i>A Dama do Lotação</i>).",
   "pornochanchada", "A15-1 Erotic Drama",
   [w("Pornochanchada")], None, None),
 ]),
]

code = {}; subs_out = []
for sc, sl, sax, leaves in SUBS:
    lo = []
    for i, (k, lab, br, defn, al, see, src, ax, secs) in enumerate(leaves, 1):
        c = f"{sc}-{i}"; code[k] = c
        d = {"code": c, "label": lab, "breadth": br, "defn": defn, "aliases": al, "see": see, "src": src}
        if secs: d["axis"] = ax or "by type"; d["secs"] = secs
        lo.append(d)
    subs_out.append({"code": sc, "label": sl, "axis": sax, "leaves": lo})
json.dump({"subs": subs_out}, open(os.path.join(OUT, "leaves.json"), "w"), indent=1, ensure_ascii=False)
secs_of = {k: (l[8] or []) for _, _, _, ls in SUBS for l in ls for k in [l[0]]}

csv.field_size_limit(10**9)
inp = list(csv.DictReader(open(os.path.join(ROOT, "taxonomy/r3/ft_in/film_romance_musical_erotic.csv"))))
A = {}
for fn in sorted(glob.glob(os.path.join(D, "c0*.txt"))):
    for l in open(fn):
        l = l.rstrip("\n")
        if not l.strip(): continue
        i, rest = l.split(" ", 1)
        p = (rest.split("|") + ["", ""])[:3]
        A[int(i)] = p
rows = []
for i, r in enumerate(inp):
    k, see, note = A[i]
    if not note:
        note = r["note"] if len(r["note"].split()) <= 12 else ""
    if k.startswith("ROUTE:"):
        rows.append([r["id"], "", "", "", note, k[6:]]); continue
    key, _, sec = k.partition(".")
    c = code[key]
    if secs_of[key] and not sec: raise SystemExit(f"{i} {k} needs sec")
    sa = ";".join(code.get(x, x) for x in see.split(";") if x) if see else ""
    rows.append([r["id"], c, sec, sa, note, ""])
with open(os.path.join(OUT, "assign.csv"), "w", newline="") as f:
    wr = csv.writer(f); wr.writerow(["id", "leaf", "sec", "see_also", "note", "route"]); wr.writerows(rows)
print(len(rows))
