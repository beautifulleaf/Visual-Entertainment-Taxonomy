import json
W = "https://en.wikipedia.org/wiki/"
def src(*a): return [[W + x, "Wikipedia"] for x in a]
L = []
def leaf(label, breadth, defn, aliases, see, s, axis=None, secs=None):
    d = {"label": label, "breadth": breadth, "defn": defn, "aliases": aliases, "see": see, "src": s}
    if secs: d["axis"] = axis; d["secs"] = secs
    L.append(d)

SPORT_TEST = "A broadcast of competitive {x} played as it happens (or as its recording), together with the named broadcast strands, studio and highlights programmes built around that sport"
leaf("Association Football Broadcasts", "broad",
     SPORT_TEST.format(x="association football") + " (<i>FIFA World Cup</i>, <i>UEFA Champions League</i>, <i>Match of the Day</i>, <i>Sportschau</i>). A multi-sport Saturday programme that merely carries football goes to B16-17.",
     "soccer on television; Fußball im Fernsehen", "B16-17 Sports Anthology & Magazine Shows; B16-16 Multi-Sport Event Coverage",
     src("Sports_broadcasting", "Match_of_the_Day", "FIFA_World_Cup"),
     "by competition level, highlights apart: international tournaments, continental club competitions, domestic league and cup coverage; highlights and magazine programmes last",
     ["International Tournaments", "Continental Club Competitions", "Domestic League & Cup Coverage", "Football Highlights & Magazine Programmes"])
leaf("American Football Broadcasts", "medium",
     SPORT_TEST.format(x="American (gridiron) or Canadian football") + " (<i>Super Bowl</i>, <i>Monday Night Football</i>, <i>The NFL Today</i>, <i>Grey Cup</i>). The Super Bowl halftime show as a concert goes to B16-25.",
     "gridiron football on television; NFL on television", "B16-25 Concert Broadcasts & Specials",
     src("Monday_Night_Football", "Super_Bowl"))
leaf("Basketball Broadcasts", "medium",
     SPORT_TEST.format(x="basketball") + " (<i>NBA Finals</i>, <i>Inside the NBA</i>, <i>NCAA March Madness</i>).",
     "NBA on television", "B16-2 American Football Broadcasts; B16-4 Baseball Broadcasts",
     src("NBA_Finals", "Inside_the_NBA"))
leaf("Baseball Broadcasts", "medium",
     SPORT_TEST.format(x="baseball") + " (<i>World Series</i>, <i>Sunday Night Baseball</i>, <i>Japan Series</i>, <i>Little League World Series</i>).",
     "MLB on television; yakyū chūkei", "B16-3 Basketball Broadcasts",
     src("World_Series", "Sunday_Night_Baseball"))
leaf("Ice Hockey Broadcasts", "medium",
     SPORT_TEST.format(x="ice hockey") + " (<i>Hockey Night in Canada</i>, <i>Stanley Cup Final</i>, <i>Summit Series</i>). Olympic hockey games famous in their own right stay here with see_also B16-16.",
     "NHL on television", "B16-16 Multi-Sport Event Coverage",
     src("Hockey_Night_in_Canada", "Stanley_Cup_Final"))
leaf("Cricket Broadcasts", "medium",
     SPORT_TEST.format(x="cricket") + " (<i>Cricket World Cup</i>, <i>The Ashes</i>, <i>Indian Premier League</i>, <i>World Series Cricket</i>).",
     "cricket on television", "B16-7 Rugby Broadcasts",
     src("Cricket_World_Cup", "World_Series_Cricket", "Indian_Premier_League"))
leaf("Rugby Broadcasts", "medium",
     SPORT_TEST.format(x="rugby union or rugby league") + " (<i>Rugby World Cup</i>, <i>Six Nations Championship</i>, <i>State of Origin series</i>, <i>Rugby Special</i>).",
     "rugby on television", "B16-6 Cricket Broadcasts; B16-1 Association Football Broadcasts",
     src("Rugby_World_Cup", "Six_Nations_Championship", "Rugby_Special"))
leaf("Tennis Broadcasts", "medium",
     SPORT_TEST.format(x="tennis") + " (<i>Wimbledon</i>, <i>Breakfast at Wimbledon</i>, <i>Battle of the Sexes</i>).",
     "tennis on television", "B16-9 Golf Broadcasts",
     src("Wimbledon_Championships", "Battle_of_the_Sexes_(tennis)"))
leaf("Golf Broadcasts", "medium",
     SPORT_TEST.format(x="golf") + " (<i>Masters Tournament</i>, <i>The Open Championship</i>, <i>Ryder Cup</i>, <i>Shell's Wonderful World of Golf</i>).",
     "golf on television", "B16-8 Tennis Broadcasts",
     src("Masters_Tournament", "Shell's_Wonderful_World_of_Golf"))
leaf("Motorsport Broadcasts", "medium",
     SPORT_TEST.format(x="motor racing on cars or motorcycles") + " (<i>Formula One World Championship</i>, <i>Indianapolis 500</i>, <i>Daytona 500</i>, <i>24 Hours of Le Mans</i>). A motoring magazine such as <i>Top Gear</i> is factual entertainment (B14).",
     "motor racing on television", "B14 Factual Entertainment Formats; B16-11 Cycling Broadcasts",
     src("Formula_One", "Indianapolis_500", "Daytona_500"))
leaf("Cycling Broadcasts", "narrow",
     SPORT_TEST.format(x="road or track cycling") + " (<i>Tour de France</i>, <i>Giro d'Italia</i>, <i>Paris–Roubaix</i>).",
     "cycle racing on television", "B16-10 Motorsport Broadcasts; B16-12 Athletics Broadcasts",
     src("Tour_de_France", "Grand_Tour_(cycling)"))
leaf("Athletics Broadcasts", "narrow",
     SPORT_TEST.format(x="track-and-field athletics or road running") + " (<i>World Athletics Championships</i>, <i>London Marathon</i>, <i>Diamond League</i>). Athletics inside the Olympics goes to B16-16.",
     "track and field on television; marathon coverage", "B16-16 Multi-Sport Event Coverage",
     src("World_Athletics_Championships", "London_Marathon"))
leaf("Snooker & Darts Broadcasts", "narrow",
     SPORT_TEST.format(x="snooker, pool or darts") + ", the indoor sports that became mass television in Britain (<i>Pot Black</i>, <i>World Snooker Championship</i>, <i>PDC World Darts Championship</i>). A darts game show such as <i>Bullseye</i> is a competition format (B13).",
     "cue sports on television", "B13 Competition Formats",
     src("Pot_Black", "World_Snooker_Championship", "PDC_World_Darts_Championship"))
leaf("Combat Sports Broadcasts", "medium",
     SPORT_TEST.format(x="boxing, mixed martial arts, kickboxing or sumo") + ", including named landmark bouts sold as pay-per-view events (<i>Rumble in the Jungle</i>, <i>HBO World Championship Boxing</i>, <i>UFC 1</i>, NHK <i>Ōzumō</i>). Professional wrestling, whose outcomes are scripted, goes to B16-18.",
     "fight broadcasts; pay-per-view boxing", "B16-18 Professional Wrestling Television",
     src("Combat_sport", "Pay-per-view", "Ultimate_Fighting_Championship"))
leaf("Horse Racing Broadcasts", "medium",
     SPORT_TEST.format(x="horse racing") + " (<i>Kentucky Derby</i>, <i>Grand National</i>, <i>Melbourne Cup</i>, <i>Channel 4 Racing</i>).",
     "racing on television", "B16-12 Athletics Broadcasts; B16-23 State & Royal Occasions",
     src("Kentucky_Derby", "Grand_National"))
leaf("Multi-Sport Event Coverage", "medium",
     "The broadcast of a multi-sport games as one event, including its opening and closing ceremonies as landmark broadcasts (<i>Olympic Games</i>, <i>2012 Summer Olympics opening ceremony</i>, <i>Commonwealth Games</i>, <i>X Games</i>). A single-sport championship goes to its sport leaf.",
     "Olympics on television; Olympic broadcasting", "B16-1 to B16-15 single-sport leaves; B16-23 State & Royal Occasions",
     src("Olympic_Games", "Olympic_Broadcasting_Services", "Commonwealth_Games"))
leaf("Sports Anthology & Magazine Shows", "medium",
     "A recurring studio-based programme that covers many sports, by live inserts, highlights, results, features or debate, rather than one sport (<i>ABC's Wide World of Sports</i>, <i>Grandstand</i>, <i>SportsCenter</i>, <i>Das aktuelle Sportstudio</i>). A highlights show for one sport goes to that sport's leaf; a sports quiz is a competition format (B13).",
     "sports anthology series; sports magazine programme; sports talk show", "B16-1 Association Football Broadcasts; B13 Competition Formats; B11 Documentary Series",
     src("ABC's_Wide_World_of_Sports", "Grandstand_(TV_programme)", "SportsCenter"))
leaf("Professional Wrestling Television", "broad",
     "A programme or event of professional wrestling: athletic performance with scripted outcomes and serial storylines, broadcast as live or live-to-tape matches (<i>WWE Raw</i>, <i>WCW Monday Nitro</i>, <i>WrestleMania</i>, <i>Wrestle Kingdom</i>). Unscripted combat sports go to B16-14.",
     "sports entertainment; puroresu; lucha libre", "B16-14 Combat Sports Broadcasts; B15 Variety & Talk Formats",
     src("Professional_wrestling", "WWE_Raw", "WrestleMania"),
     "by broadcast form, foreign traditions apart: weekly episodic shows, pay-per-view and premium live events; puroresu and lucha libre programmes last",
     ["Weekly Wrestling Programmes", "Pay-Per-View & Premium Live Events", "Puroresu & Lucha Libre Programmes"])
leaf("Award Ceremonies", "broad",
     "The televised ceremony at which an academy, industry body or publication presents its annual awards, hosted and staged as a show (<i>Academy Awards</i>, <i>Primetime Emmy Awards</i>, <i>Grammy Awards</i>, <i>Tony Awards</i>). A song contest whose prize is decided on the night goes to B16-20.",
     "awards show; awards ceremony", "B16-20 Song Contests & Music Festival Broadcasts",
     src("Academy_Awards", "Primetime_Emmy_Awards", "Grammy_Awards"),
     "by the field honoured: film, television, music; theatre, sports and multi-field awards last",
     ["Film Award Ceremonies", "Television Award Ceremonies", "Music Award Ceremonies", "Theatre, Sports & Multi-Field Award Ceremonies"])
leaf("Song Contests & Music Festival Broadcasts", "medium",
     "The broadcast of a song contest, in which new songs or national entries compete live for a prize, or of a named music festival as a televised event (<i>Eurovision Song Contest</i>, <i>NHK Kōhaku Uta Gassen</i>, <i>Sanremo Music Festival</i>, <i>Melodifestivalen</i>). A talent-search series with weekly eliminations (<i>The X Factor</i>) is a competition format (B13).",
     "song festival; national selection; kayō festival", "B13 Competition Formats; B16-19 Award Ceremonies; B16-25 Concert Broadcasts & Specials",
     src("Eurovision_Song_Contest", "Song_contest", "Sanremo_Music_Festival", "Kōhaku_Uta_Gassen"))
leaf("Beauty Pageants", "narrow",
     "The televised final of a beauty pageant, in which contestants are judged on stage for a title (<i>Miss Universe</i>, <i>Miss World</i>, <i>Miss America</i>). A reality series about pageant children (<i>Toddlers & Tiaras</i>) is factual entertainment (B14).",
     "beauty contest; pageant telecast", "B14 Factual Entertainment Formats",
     src("Beauty_pageant", "Miss_Universe", "Miss_World"))
leaf("Parades & New Year's Eve Broadcasts", "medium",
     "Annual live coverage of a civic parade, carnival or calendar festivity, above all New Year's Eve countdown shows (<i>Macy's Thanksgiving Day Parade</i>, <i>Dick Clark's New Year's Rockin' Eve</i>, <i>CCTV New Year's Gala</i>, <i>Jools' Annual Hootenanny</i>). Military and state parades go to B16-23.",
     "holiday specials; New Year's Eve special; Chunwan", "B16-23 State & Royal Occasions; B15 Variety & Talk Formats",
     src("Macy's_Thanksgiving_Day_Parade", "Dick_Clark's_New_Year's_Rockin'_Eve", "CCTV_New_Year's_Gala"))
leaf("State & Royal Occasions", "medium",
     "Live coverage of a ceremony of state: coronations, royal weddings, state funerals, inaugurations, national-day and military parades (<i>Coronation of Elizabeth II</i>, <i>Wedding of Prince Charles and Lady Diana Spencer</i>, <i>Trooping the Colour</i>). Political news coverage is out of scope.",
     "royal broadcast; national ceremony; outside broadcast", "B16-22 Parades & New Year's Eve Broadcasts; B16-16 Multi-Sport Event Coverage",
     src("Coronation_of_Elizabeth_II", "State_funeral", "Trooping_the_Colour"))
leaf("Telethons & Benefit Concerts", "medium",
     "A broadcast staged to raise money for a cause, either a long-form appeal telethon or a benefit concert broadcast live (<i>Live Aid</i>, <i>Jerry Lewis MDA Labor Day Telethon</i>, <i>Comic Relief</i>, <i>24-Hour Television</i>). A concert without a fund-raising purpose goes to B16-25.",
     "telethon; charity appeal; benefit concert", "B16-25 Concert Broadcasts & Specials",
     src("Telethon", "Benefit_concert", "Live_Aid"))
leaf("Concert Broadcasts & Specials", "medium",
     "A musical performance before an audience broadcast as a programme, as a one-off concert special or a recurring concert strand (<i>Elvis: Aloha from Hawaii</i>, <i>Vienna New Year's Concert</i>, <i>MTV Unplugged</i>, <i>Austin City Limits</i>). Studio chart and music-variety shows go to B15; benefit concerts to B16-24; opera and ballet to B16-26.",
     "concert special; television special; music special", "B15 Variety & Talk Formats; B16-24 Telethons & Benefit Concerts; B16-26 Theatre, Opera & Ballet Broadcasts",
     src("Television_special", "Elvis:_Aloha_from_Hawaii", "MTV_Unplugged"))
leaf("Theatre, Opera & Ballet Broadcasts", "medium",
     "A staged theatrical work (play, musical, opera, ballet) broadcast live or relayed from the stage, including the live television musical (<i>Great Performances</i>, <i>Live from Lincoln Center</i>, <i>The Metropolitan Opera: Live in HD</i>, <i>The Sound of Music Live!</i>). A drama written for television (anthology drama) goes to B1.",
     "live theatre broadcast; event cinema; live television musical", "B1 Drama Series; B16-25 Concert Broadcasts & Specials",
     src("Great_Performances", "Live_from_Lincoln_Center", "The_Metropolitan_Opera_Live_in_HD", "National_Theatre_Live"))
leaf("Circus & Spectacle Broadcasts", "narrow",
     "A broadcast of a circus show or of a live stunt or feat staged as a television event outside organized sport (<i>Circus of the Stars</i>, <i>International Circus Festival of Monte-Carlo</i>, <i>Evel Knievel's Snake River Canyon jump</i>, <i>Skywire</i>).",
     "circus special; stunt special", "B16-26 Theatre, Opera & Ballet Broadcasts; B14 Factual Entertainment Formats",
     src("Circus", "Cirque_du_Soleil", "Circus_of_the_Stars"))
leaf("Stand-Up Comedy Specials", "broad",
     "A recorded stand-up (or live improvised) comedy performance before an audience broadcast or streamed as a special, or a showcase series of such sets (<i>Eddie Murphy: Delirious</i>, <i>Chris Rock: Bring the Pain</i>, <i>Nanette</i>, <i>Live at the Apollo</i>). A theatrically released concert film goes to A12; sketch shows go to B8 or B15.",
     "comedy special; stand-up special", "A12 Comedy; B8 Comedy Series; B15 Variety & Talk Formats",
     src("Stand-up_comedy", "Comedy_Central_Presents", "Live_at_the_Apollo_(TV_series)"),
     "by outlet and form: premium-cable and broadcast specials, streaming-era specials, showcase series; musical and improvised comedy specials last",
     ["Premium Cable & Broadcast Specials", "Streaming-Era Specials", "Stand-Up Showcase Series", "Musical & Improvised Comedy Specials"])

for i, l in enumerate(L, 1): l["code"] = f"B16-{i}"
out = {"subs": [{"code": "B16", "label": "Live Event & Sports Television",
    "axis": "Axis: by the kind of live event the broadcast carries: sporting competition (by sport, then multi-sport and anthology), professional wrestling, then ceremonies, contests and pageants, civic and state occasions, fund-raising broadcasts, and stage performances (concert, theatre, circus, stand-up)",
    "leaves": [dict(code=l.pop("code"), **l) for l in L]}]}
json.dump(out, open("/home/user/Visual-Entertainment-Taxonomy/taxonomy/r3/ft_out/tv_live_sports/leaves.json", "w"), ensure_ascii=False, indent=1)
print(len(L))
