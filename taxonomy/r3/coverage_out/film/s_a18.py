W = "https://en.wikipedia.org/wiki/"
BM = ["Angry Young Man Era (1973–1980s)", "Romantic & Family Spectacle (1990s–2000s)", "Star Action Masala (1995–)"]
ROM = {"tt0110076", "tt0112870", "tt0172684", "tt0216817", "tt0213890", "tt0248126", "tt0347304", "tt0254481", "tt1024943", "tt3863552", "tt4535650", "tt2762334"}
NO = ["Home-Video Era (1992–2000s)", "New Nollywood (2009–)"]
YS = ["Yeşilçam Melodrama", "Yeşilçam Comedy (Eğilmez, Sunal)", "Historical Adventure (Malkoçoğlu, Tarkan, Kara Murat)", "Turksploitation Remakes"]
YSMAP = {"tt0200588": YS[3], "tt0252084": YS[0], "tt0392396": YS[2], "tt0267351": YS[1], "tt0252487": YS[1], "tt0252488": YS[1], "tt0252490": YS[1],
         "tt0253779": YS[1], "tt0253828": YS[1], "tt0252489": YS[1], "tt0263975": YS[0], "tt0253997": YS[1], "tt0765833": YS[0]}
RESEC = {
 "A18-1": {"axis": "era (the field's own periodisation of Hindi masala)", "secs": BM,
           "fn": lambda tc, r, i: BM[0] if int(r["year"]) < 1990 else BM[1] if tc in ROM else BM[2]},
 "A18-7": {"axis": "era of the Nigerian industry", "secs": NO, "fn": lambda tc, r, i: NO[0] if int(r["year"]) < 2009 else NO[1]},
 "A18-8": {"axis": "popular genre cycle of the Yeşilçam studio era", "secs": YS, "map": YSMAP},
}
NEW = [
 {"key": "NEW_A18_OZPLOIT", "sub": "A18", "label": "Ozploitation", "breadth": "national cycle",
  "defn": "The Australian low-budget exploitation boom of c. 1971–1990 under the 10BA tax concession: ocker sex comedies, bikie films, outback horror, kung-fu and car-crash action (<i>Stone</i>, <i>Alvin Purple</i>, <i>Patrick</i>, <i>Turkey Shoot</i>, <i>Dead End Drive-In</i>).",
  "aliases": "Australian exploitation film", "see": "A1-23 Australian New Wave; A10-10 Meat Pie Western", "src": [[W + "Ozploitation", "Wikipedia"]]},
]
ITEMS = """
# Masala angry young man
A18-1 | Angry Young Man Era (1973–1980s) | Zanjeer | 1973 | Prakash Mehra | tt0070947
A18-1 | Angry Young Man Era (1973–1980s) | Amar Akbar Anthony | 1977 | Manmohan Desai | tt0075669
A18-1 | Angry Young Man Era (1973–1980s) | Don | 1978 | Chandra Barot | tt0077451
A18-1 | Angry Young Man Era (1973–1980s) | Trishul | 1978 | Yash Chopra | tt0078418
A18-1 | Angry Young Man Era (1973–1980s) | Muqaddar Ka Sikandar | 1978 | Prakash Mehra | tt0079590
A18-1 | Angry Young Man Era (1973–1980s) | Kaala Patthar | 1979 | Yash Chopra | tt0079386
A18-1 | Angry Young Man Era (1973–1980s) | Shakti | 1982 | Ramesh Sippy | tt0084667
A18-1 | Angry Young Man Era (1973–1980s) | Coolie | 1983 | Manmohan Desai | tt0085361
# Nollywood home video
A18-7 | Home-Video Era (1992–2000s) | Living in Bondage | 1992 | Chris Obi Rapu | tt0489511
A18-7 | Home-Video Era (1992–2000s) | Glamour Girls | 1994 | Chika Onukwufor | tt0765064
A18-7 | Home-Video Era (1992–2000s) | Rattlesnake | 1995 | Amaka Igwe | -
A18-7 | Home-Video Era (1992–2000s) | Domitilla | 1996 | Zeb Ejiro | -
A18-7 | Home-Video Era (1992–2000s) | Saworoide | 1999 | Tunde Kelani | -
A18-7 | Home-Video Era (1992–2000s) | Issakaba | 2000 | Lancelot Oduwa Imasuen | -
# Yesilcam
A18-8 | Yeşilçam Melodrama | Oh, Beautiful Istanbul | 1966 | Atıf Yılmaz | tt0062060
A18-8 | Yeşilçam Melodrama | My Black Eyed | 1970 | Orhan Aksoy | tt0263534
A18-8 | Yeşilçam Melodrama | Arım Balım Peteğim | 1970 | Aram Gülyüz | tt0182731
A18-8 | Yeşilçam Melodrama | Sev Kardeşim | 1972 | Ertem Eğilmez | tt0827739
A18-8 | Yeşilçam Melodrama | Smiling Eyes | 1977 | Ertem Eğilmez | tt0289967
A18-8 | Yeşilçam Comedy (Eğilmez, Sunal) | From the Village to the City | 1974 | Ertem Eğilmez | tt0252619
A18-8 | Yeşilçam Comedy (Eğilmez, Sunal) | Salako | 1974 | Ertem Eğilmez | tt0253623
A18-8 | Yeşilçam Comedy (Eğilmez, Sunal) | Our Family | 1975 | Ertem Eğilmez | tt0456047
A18-8 | Yeşilçam Comedy (Eğilmez, Sunal) | King of the Doormen | 1976 | Zeki Ökten | tt0252591
A18-8 | Yeşilçam Comedy (Eğilmez, Sunal) | Şaban, Son of Şaban | 1977 | Ertem Eğilmez | tt0253614
A18-8 | Yeşilçam Comedy (Eğilmez, Sunal) | Shakir the Clumsy | 1977 | Natuk Baytan | tt0253621
A18-8 | Yeşilçam Comedy (Eğilmez, Sunal) | Fearless Coward | 1979 | Natuk Baytan | tt0252611
A18-8 | Historical Adventure (Malkoçoğlu, Tarkan, Kara Murat) | Malkoçoğlu | 1966 | Süreyya Duru | tt0392393
A18-8 | Historical Adventure (Malkoçoğlu, Tarkan, Kara Murat) | Köroğlu | 1968 | Atıf Yılmaz | tt0183368
A18-8 | Historical Adventure (Malkoçoğlu, Tarkan, Kara Murat) | Tarkan | 1969 | Mehmet Aslan | tt0274931
A18-8 | Historical Adventure (Malkoçoğlu, Tarkan, Kara Murat) | Battal Gazi Destanı | 1971 | Atıf Yılmaz | tt0182765
A18-8 | Historical Adventure (Malkoçoğlu, Tarkan, Kara Murat) | Tarkan and the Blood of the Vikings | 1971 | Mehmet Aslan | tt0274932
A18-8 | Historical Adventure (Malkoçoğlu, Tarkan, Kara Murat) | Kara Murat: Fatih'in Fedaisi | 1972 | Natuk Baytan | tt4819648
A18-8 | Historical Adventure (Malkoçoğlu, Tarkan, Kara Murat) | Kılıç Aslan | 1975 | Natuk Baytan | tt0181966
A18-8 | Turksploitation Remakes | Three Giant Men | 1973 | T. Fikret Uçak | tt0181947
A18-8 | Turksploitation Remakes | Turist Ömer Uzay Yolunda | 1973 | Hulki Saner | tt0182503
A18-8 | Turksploitation Remakes | Şeytan | 1974 | Metin Erksan | tt0072148
A18-8 | Turksploitation Remakes | The Return of Superman | 1979 | Kunt Tulgar | tt0392818
A18-8 | Turksploitation Remakes | The Man Who Saved the World | 1982 | Çetin İnanç | tt0182060
# Ozploitation
NEW_A18_OZPLOIT | | The Adventures of Barry McKenzie | 1972 | Bruce Beresford | tt0068173
NEW_A18_OZPLOIT | | Alvin Purple | 1973 | Tim Burstall | tt0069698
NEW_A18_OZPLOIT | | Stone | 1974 | Sandy Harbutt | tt0072209
NEW_A18_OZPLOIT | | The Man from Hong Kong | 1975 | Brian Trenchard-Smith | tt0073343
NEW_A18_OZPLOIT | | Inn of the Damned | 1975 | Terry Bourke | tt0071661
NEW_A18_OZPLOIT | | Patrick | 1978 | Richard Franklin | tt0078067
NEW_A18_OZPLOIT | | Stunt Rock | 1978 | Brian Trenchard-Smith | tt0078335
NEW_A18_OZPLOIT | | Thirst | 1979 | Rod Hardy | tt0080016
NEW_A18_OZPLOIT | | Snapshot | 1979 | Simon Wincer | tt0079917
NEW_A18_OZPLOIT | | Harlequin | 1980 | Simon Wincer | tt0080842
NEW_A18_OZPLOIT | | The Survivor | 1981 | David Hemmings | tt0083144
NEW_A18_OZPLOIT | | Turkey Shoot | 1982 | Brian Trenchard-Smith | tt0082338
NEW_A18_OZPLOIT | | BMX Bandits | 1983 | Brian Trenchard-Smith | tt0085204
NEW_A18_OZPLOIT | | Dead End Drive-In | 1986 | Brian Trenchard-Smith | tt0090915
NEW_A18_OZPLOIT | | Fair Game | 1986 | Mario Andreacchio | tt0089122
"""
