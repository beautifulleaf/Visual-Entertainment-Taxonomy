# wiki titles found missing on en.wikipedia (API check) -> replacement source (verified title or museum search URL), None = drop row
CB = "https://colbase.nich.go.jp/collection_items?locale=en&keyword="
SI = "https://collections.si.edu/search/results.htm?q="
FIX = {
 "Abu Tahir": "Kashan", "Kashan lustreware": "Kashan", "Adrianus Kocx": "Delftware", "Frederik van Frijtom": "Delftware",
 "Alhambra vase": "Lustreware", "Aoki Mokubei": "https://de.wikipedia.org/wiki/Aoki_Mokubei",
 "Eiraku Hozen": CB + "%E6%B0%B8%E6%A5%BD%E4%BF%9D%E5%85%A8", "Nin'ami Dōhachi": CB + "%E4%BB%81%E9%98%BF%E5%BC%A5%E9%81%93%E5%85%AB",
 "Arakawa Toyozō": "Shino ware", "Bakōhan": "Longquan celadon", "Blom Plate": "Maya ceramics", "Vase of the Seven Gods": "Maya ceramics",
 "Boreads Painter": "List of Greek vase painters", "Hunt Painter": "List of Greek vase painters", "Lycurgus Painter": "List of Greek vase painters",
 "Micali Painter": "List of Greek vase painters", "Paris Painter": "List of Greek vase painters", "Eagle Painter": "List of Greek vase painters",
 "Chigi Painter": "List of Greek vase painters", "Timonidas": "List of Greek vase painters", "Corinthian vase painting": "Pottery of ancient Greece",
 "Bàu Trúc": None, "Böttger stoneware": "Johann Friedrich Böttger",
 "Gong Chun": "https://digitalarchive.npm.gov.tw/Collection/Search?Keyword=%E4%BE%9B%E6%98%A5", "Shi Dabin": "https://digitalarchive.npm.gov.tw/Collection/Search?Keyword=%E6%99%82%E5%A4%A7%E5%BD%AC",
 "Greater Nicoya": SI + "Nicoya+polychrome", "Karako-Kagi site": None, "McKeithen Site": None, "Museo Ruiz de Luna": None, "Nanking Cargo": None,
 "Paul Hannong": "Strasbourg", "Quinchamalí": "https://ich.unesco.org/en/USL/quinchamali-and-santa-cruz-de-cuca-pottery-01847", "Stepan Ivanov (Polubes)": None,
 "Fujiwara Kei": CB + "%E8%97%A4%E5%8E%9F%E5%95%93", "Kaneshige Tōyō": CB + "%E9%87%91%E9%87%8D%E9%99%B6%E9%99%BD",
 "Imaizumi Imaemon XIII": CB + "%E4%BB%8A%E6%B3%89%E4%BB%8A%E5%8F%B3%E8%A1%9B%E9%96%80", "Itō Sekisui V": CB + "%E4%BC%8A%E8%97%A4%E8%B5%A4%E6%B0%B4",
 "Miwa Kyūsetsu": CB + "%E4%B8%89%E8%BC%AA%E4%BC%91%E9%9B%AA", "Nakazato Tarōemon": CB + "%E4%B8%AD%E9%87%8C%E5%A4%AA%E9%83%8E%E5%8F%B3%E8%A1%9B%E9%96%80",
 "Tokuda Yasokichi III": CB + "%E5%BE%B3%E7%94%B0%E5%85%AB%E5%8D%81%E5%90%89", "Kutani Shōza": CB + "%E4%B9%9D%E8%B0%B7%E5%BA%84%E4%B8%89",
 "Kinkōzan Sōbei": CB + "%E9%8C%A6%E5%85%89%E5%B1%B1", "William (hippo)": "https://www.metmuseum.org/art/collection/search/544227",
 "Witte Leeuw": None, "Yōhen tenmoku": "Jian ware",
}
