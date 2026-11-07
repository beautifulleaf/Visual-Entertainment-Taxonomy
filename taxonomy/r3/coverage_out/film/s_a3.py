G = ["Mario Bava", "Dario Argento", "Lucio Fulci", "Sergio Martino", "Other Gialli of the Classic Cycle (1968–1982)", "Late Gialli & Neo-Giallo"]
KR = ["Rialto Edgar Wallace Series (1959–1972)", "Dr. Mabuse Revival (1960–1964)", "Bryan Edgar Wallace & Other Krimis"]

def giallo(tc, r, i):
    w = r["who"]
    for k in ("Bava", "Argento", "Fulci", "Martino"):
        if k in w and not ("Lamberto" in w): return [g for g in G if k in g][0]
    return G[4]

RESEC = {
 "A3-5": {"axis": "auteur (the field's own division of the giallo) and late/neo phase", "secs": G, "fn": giallo},
 "A3-4": {"axis": "production series", "secs": KR, "map": {"tt0052829": KR[0]}},
}
SECS = [("A3-21", "Eurospy (1964–1968)")]
ITEMS = """
# ---- Giallo
A3-5 | Mario Bava | Hatchet for the Honeymoon | 1970 | Mario Bava | tt0064904
A3-5 | Mario Bava | Five Dolls for an August Moon | 1970 | Mario Bava | tt0065553
A3-5 | Dario Argento | Sleepless | 2001 | Dario Argento | tt0220827
A3-5 | Dario Argento | The Card Player | 2004 | Dario Argento | tt0330691
A3-5 | Dario Argento | Giallo | 2009 | Dario Argento | tt1107816
A3-5 | Lucio Fulci | Murder-Rock: Dancing Death | 1984 | Lucio Fulci | tt0087759
A3-5 | Lucio Fulci | A Cat in the Brain | 1990 | Lucio Fulci | tt0099637
A3-5 | Sergio Martino | The Case of the Scorpion's Tail | 1971 | Sergio Martino | tt0066924
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | Death Laid an Egg | 1968 | Giulio Questi | tt0061994
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | The Sweet Body of Deborah | 1968 | Romolo Guerrieri | tt0064243
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | Paranoia | 1969 | Umberto Lenzi | tt0063413
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | So Sweet... So Perverse | 1969 | Umberto Lenzi | tt0064186
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | In the Folds of the Flesh | 1970 | Sergio Bergonzelli | tt0065693
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | The Bloodstained Butterfly | 1971 | Duccio Tessari | tt0067084
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | Short Night of Glass Dolls | 1971 | Aldo Lado | tt0067384
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | The Fifth Cord | 1971 | Luigi Bazzoni | tt0067134
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | Black Belly of the Tarantula | 1971 | Paolo Cavara | tt0069343
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | Death Walks on High Heels | 1971 | Luciano Ercoli | tt0067446
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | The Iguana with the Tongue of Fire | 1971 | Riccardo Freda | tt0067236
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | The Night Evelyn Came Out of the Grave | 1971 | Emilio Miraglia | tt0067487
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | Who Saw Her Die? | 1972 | Aldo Lado | tt0068367
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | Seven Blood-Stained Orchids | 1972 | Umberto Lenzi | tt0067696
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | The Case of the Bloody Iris | 1972 | Giuliano Carnimeo | tt0069073
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | Spasmo | 1974 | Umberto Lenzi | tt0072196
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | What Have They Done to Your Daughters? | 1974 | Massimo Dallamano | tt0072007
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | The Perfume of the Lady in Black | 1974 | Francesco Barilli | tt0070565
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | Eyeball | 1975 | Umberto Lenzi | tt0071537
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | Strip Nude for Your Killer | 1975 | Andrea Bianchi | tt0073470
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | Footprints on the Moon | 1975 | Luigi Bazzoni | tt0071950
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | Watch Me When I Kill | 1977 | Antonio Bido | tt0076068
A3-5 | Other Gialli of the Classic Cycle (1968–1982) | The Pyjama Girl Case | 1977 | Flavio Mogherini | tt0075834
A3-5 | Late Gialli & Neo-Giallo | Delirium | 1987 | Lamberto Bava | tt0093043
A3-5 | Late Gialli & Neo-Giallo | Amer | 2009 | Hélène Cattet; Bruno Forzani | tt1426352
A3-5 | Late Gialli & Neo-Giallo | The Strange Color of Your Body's Tears | 2013 | Hélène Cattet; Bruno Forzani | tt2733258
# ---- Krimi
A3-4 | Rialto Edgar Wallace Series (1959–1972) | The Terrible People | 1960 | Harald Reinl | tt0053630
A3-4 | Rialto Edgar Wallace Series (1959–1972) | Dead Eyes of London | 1961 | Alfred Vohrer | tt0054395
A3-4 | Rialto Edgar Wallace Series (1959–1972) | The Strange Countess | 1961 | Josef von Báky | tt0055429
A3-4 | Rialto Edgar Wallace Series (1959–1972) | The Green Archer | 1961 | Jürgen Roland | tt0054947
A3-4 | Rialto Edgar Wallace Series (1959–1972) | The Forger of London | 1961 | Harald Reinl | tt0054906
A3-4 | Rialto Edgar Wallace Series (1959–1972) | The Door with Seven Locks | 1962 | Alfred Vohrer | tt0056630
A3-4 | Rialto Edgar Wallace Series (1959–1972) | The Inn on the River | 1962 | Alfred Vohrer | tt0056012
A3-4 | Rialto Edgar Wallace Series (1959–1972) | Secret of the Red Orchid | 1962 | Helmut Ashley | tt0055391
A3-4 | Rialto Edgar Wallace Series (1959–1972) | The Indian Scarf | 1963 | Alfred Vohrer | tt0057183
A3-4 | Rialto Edgar Wallace Series (1959–1972) | The Squeaker | 1963 | Alfred Vohrer | tt0057718
A3-4 | Rialto Edgar Wallace Series (1959–1972) | The Black Abbot | 1963 | Franz Josef Gottlieb | tt0057476
A3-4 | Rialto Edgar Wallace Series (1959–1972) | The Mysterious Magician | 1964 | Alfred Vohrer | tt0058191
A3-4 | Rialto Edgar Wallace Series (1959–1972) | Room 13 | 1964 | Harald Reinl | tt0058773
A3-4 | Rialto Edgar Wallace Series (1959–1972) | The Sinister Monk | 1965 | Harald Reinl | tt0059846
A3-4 | Rialto Edgar Wallace Series (1959–1972) | The Hunchback of Soho | 1966 | Alfred Vohrer | tt0060192
A3-4 | Rialto Edgar Wallace Series (1959–1972) | Creature with the Blue Hand | 1967 | Alfred Vohrer | tt0061409
A3-4 | Rialto Edgar Wallace Series (1959–1972) | The College Girl Murders | 1967 | Alfred Vohrer | tt0062022
A3-4 | Dr. Mabuse Revival (1960–1964) | The 1,000 Eyes of Dr. Mabuse | 1960 | Fritz Lang | tt0054371
A3-4 | Dr. Mabuse Revival (1960–1964) | The Return of Dr. Mabuse | 1961 | Harald Reinl | tt0055008
A3-4 | Dr. Mabuse Revival (1960–1964) | The Invisible Dr. Mabuse | 1962 | Harald Reinl | tt0056639
A3-4 | Dr. Mabuse Revival (1960–1964) | The Terror of Doctor Mabuse | 1962 | Werner Klingler | tt0056573
A3-4 | Dr. Mabuse Revival (1960–1964) | Dr. Mabuse vs. Scotland Yard | 1963 | Paul May | tt0057479
A3-4 | Dr. Mabuse Revival (1960–1964) | The Death Ray of Dr. Mabuse | 1964 | Hugo Fregonese | tt0058667
A3-4 | Bryan Edgar Wallace & Other Krimis | Das Phantom von Soho | 1964 | Franz Josef Gottlieb | tt0058466
A3-4 | Bryan Edgar Wallace & Other Krimis | Circus of Fear | 1966 | John Llewellyn Moxey | tt0060865
# ---- Eurospy
A3-21 | Eurospy (1964–1968) | OSS 117: Panic in Bangkok | 1964 | André Hunebelle | -
A3-21 | Eurospy (1964–1968) | Mission Bloody Mary | 1965 | Sergio Grieco | -
A3-21 | Eurospy (1964–1968) | Kiss Kiss... Bang Bang | 1966 | Duccio Tessari | -
A3-21 | Eurospy (1964–1968) | Lightning Bolt | 1966 | Antonio Margheriti | -
A3-21 | Eurospy (1964–1968) | Secret Agent Super Dragon | 1966 | Giorgio Ferroni | tt0060956
A3-21 | Eurospy (1964–1968) | Operation Kid Brother | 1967 | Alberto De Martino | tt0062078
A3-21 | Eurospy (1964–1968) | Deadlier Than the Male | 1967 | Ralph Thomas | tt0060288
A3-21 | Cold War Espionage | Funeral in Berlin | 1966 | Guy Hamilton | tt0060437
A3-21 | Cold War Espionage | Billion Dollar Brain | 1967 | Ken Russell | tt0061405
"""
