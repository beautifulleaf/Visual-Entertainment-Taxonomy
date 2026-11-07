W = "https://en.wikipedia.org/wiki/"
SP = ["Sergio Leone", "Sergio Corbucci", "Zapata Westerns (Sollima, Damiani & the political spaghetti)", "Other Spaghetti Westerns", "Comic Spaghetti & the Trinity Cycle"]
SPMAP = {"tt0058461": SP[0], "tt0059578": SP[0], "tt0060196": SP[0], "tt0064116": SP[0], "tt0067140": SP[0], "tt0060315": SP[1], "tt0063032": SP[1],
         "tt0064208": SP[3], "tt0063501": SP[2], "tt0067355": SP[4], "tt0068154": SP[4], "tt0070215": SP[4], "tt0067770": SP[3], "tt0074575": SP[3]}
OS = ["DEFA Indianerfilme (1966–1985)", "Soviet Red Westerns (Easterns)"]
RESEC = {
 "A10-8": {"axis": "auteur and named sub-cycle", "secs": SP, "map": SPMAP},
 "A10-9": {"axis": "national production tradition", "secs": OS, "map": {"tt0151750": OS[1], "tt0061057": OS[0], "tt0069725": OS[0]}},
}
NEW = [
 {"key": "NEW_A10_KARLMAY", "sub": "A10", "label": "Karl May Western", "breadth": "national cycle",
  "defn": "The West German (Rialto/CCC) cycle of 1962–1968 adapting Karl May's Winnetou and Old Shatterhand novels, shot in Yugoslavia: noble Apache chief, German blood-brother hero, Martin Böttcher scores (<i>Treasure of Silver Lake</i>, <i>Apache Gold</i>). It preceded and fed the Spaghetti Western boom.",
  "aliases": "Winnetou films; Karl May films", "see": "A10-8 Spaghetti Western; A10-9 Ostern", "src": [[W + "Karl_May_film_adaptations", "Wikipedia"]]},
]
ITEMS = """
# Spaghetti
A10-8 | Sergio Corbucci | Minnesota Clay | 1964 | Sergio Corbucci | tt0058202
A10-8 | Sergio Corbucci | Navajo Joe | 1966 | Sergio Corbucci | tt0061587
A10-8 | Sergio Corbucci | The Hellbenders | 1967 | Sergio Corbucci | tt0060261
A10-8 | Sergio Corbucci | The Mercenary | 1968 | Sergio Corbucci | tt0063293
A10-8 | Sergio Corbucci | Compañeros | 1970 | Sergio Corbucci | tt0066612
A10-8 | Zapata Westerns (Sollima, Damiani & the political spaghetti) | A Bullet for the General | 1967 | Damiano Damiani | tt0061429
A10-8 | Zapata Westerns (Sollima, Damiani & the political spaghetti) | Face to Face | 1967 | Sergio Sollima | tt0061636
A10-8 | Zapata Westerns (Sollima, Damiani & the political spaghetti) | Requiescant | 1967 | Carlo Lizzani | tt0063500
A10-8 | Zapata Westerns (Sollima, Damiani & the political spaghetti) | Run, Man, Run | 1968 | Sergio Sollima | tt0062825
A10-8 | Zapata Westerns (Sollima, Damiani & the political spaghetti) | Tepepa | 1968 | Giulio Petroni | tt0063679
A10-8 | Other Spaghetti Westerns | A Pistol for Ringo | 1965 | Duccio Tessari | tt0059601
A10-8 | Other Spaghetti Westerns | Day of Anger | 1967 | Tonino Valerii | tt0061709
A10-8 | Other Spaghetti Westerns | Django Kill... If You Live, Shoot! | 1967 | Giulio Questi | tt0062082
A10-8 | Other Spaghetti Westerns | If You Meet Sartana Pray for Your Death | 1968 | Gianfranco Parolini | tt0063568
A10-8 | Other Spaghetti Westerns | Cemetery Without Crosses | 1969 | Robert Hossein | tt0063740
A10-8 | Other Spaghetti Westerns | Sabata | 1969 | Gianfranco Parolini | tt0064916
A10-8 | Other Spaghetti Westerns | The Price of Power | 1969 | Tonino Valerii | tt0066105
A10-8 | Other Spaghetti Westerns | Django the Bastard | 1969 | Sergio Garrone | tt0064240
A10-8 | Other Spaghetti Westerns | Blindman | 1971 | Ferdinando Baldi | tt0066844
A10-8 | Other Spaghetti Westerns | Four of the Apocalypse | 1975 | Lucio Fulci | tt0073594
A10-8 | Other Spaghetti Westerns | Keoma | 1976 | Enzo G. Castellari | tt0074740
# Ostern
A10-9 | DEFA Indianerfilme (1966–1985) | Chingachgook: The Great Serpent | 1967 | Richard Groschopp | tt0202832
A10-9 | DEFA Indianerfilme (1966–1985) | White Wolves | 1969 | Konrad Petzold | tt0063798
A10-9 | DEFA Indianerfilme (1966–1985) | Tecumseh | 1972 | Hans Kratzert | tt0069353
A10-9 | DEFA Indianerfilme (1966–1985) | Ulzana | 1974 | Gottfried Kolditz | tt0072336
A10-9 | DEFA Indianerfilme (1966–1985) | Blood Brothers | 1975 | Werner W. Wallroth | tt0072717
A10-9 | DEFA Indianerfilme (1966–1985) | Severino | 1978 | Claus Dobberke | tt0078237
A10-9 | Soviet Red Westerns (Easterns) | The Elusive Avengers | 1966 | Edmond Keosayan | tt0060747
A10-9 | Soviet Red Westerns (Easterns) | White Sun of the Desert | 1970 | Vladimir Motyl | tt0066565
A10-9 | Soviet Red Westerns (Easterns) | At Home Among Strangers | 1974 | Nikita Mikhalkov | -
# Karl May
NEW_A10_KARLMAY | | Treasure of Silver Lake | 1962 | Harald Reinl | tt0056452
NEW_A10_KARLMAY | | Apache Gold | 1963 | Harald Reinl | tt0057687
NEW_A10_KARLMAY | | Old Shatterhand | 1964 | Hugo Fregonese | tt0057380
NEW_A10_KARLMAY | | Last of the Renegades | 1964 | Harald Reinl | tt0058751
NEW_A10_KARLMAY | | Amongst Vultures | 1964 | Alfred Vohrer | tt0058709
NEW_A10_KARLMAY | | The Desperado Trail | 1965 | Harald Reinl | tt0059915
NEW_A10_KARLMAY | | The Oil Prince | 1965 | Harald Philipp | tt0059958
NEW_A10_KARLMAY | | Flaming Frontier | 1965 | Alfred Vohrer | tt0059538
NEW_A10_KARLMAY | | Winnetou and the Crossbreed | 1966 | Alfred Vohrer | tt0061197
NEW_A10_KARLMAY | | Old Firehand | 1966 | Alfred Vohrer | tt0061198
NEW_A10_KARLMAY | | The Valley of Death | 1968 | Harald Reinl | tt0063818
# Acid western
A10-7 | | The Hired Hand | 1971 | Peter Fonda | tt0067204
A10-7 | | The Last Movie | 1971 | Dennis Hopper | tt0067327
A10-7 | | Zachariah | 1971 | George Englund | tt0068011
A10-7 | | Greaser's Palace | 1972 | Robert Downey Sr. | tt0068659
# Musical western
A10-5 | | Whoopee! | 1930 | Thornton Freeland | tt0021549
A10-5 | | The Harvey Girls | 1946 | George Sidney | tt0038589
A10-5 | | Annie Get Your Gun | 1950 | George Sidney | tt0042200
A10-5 | | Red Garters | 1954 | George Marshall | tt0047400
A10-5 | | Lemonade Joe | 1964 | Oldřich Lipský | tt0058275
A10-5 | | Paint Your Wagon | 1969 | Joshua Logan | tt0064782
A10-5 | | Rustlers' Rhapsody | 1985 | Hugh Wilson | tt0089945
# Singing cowboy
A10-3 | | The Phantom Empire | 1935 | Otto Brower; B. Reeves Eason | tt0026867
A10-3 | | Tumbling Tumbleweeds | 1935 | Joseph Kane | -
A10-3 | | The Singing Vagabond | 1935 | Carl Pierson | -
A10-3 | | Song of the Gringo | 1936 | John P. McCarthy | -
A10-3 | | Public Cowboy No. 1 | 1937 | Joseph Kane | -
A10-3 | | Back in the Saddle | 1941 | Lew Landers | -
A10-3 | | My Pal Trigger | 1946 | Frank McDonald | tt0038764
"""
