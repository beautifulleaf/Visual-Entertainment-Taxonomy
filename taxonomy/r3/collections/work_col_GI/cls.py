import re
R=[
 ('X', r'石鏃|石斧|石器|石匙|石錘|石棒|砥石|剥片|bijl|werktuig|vuistbijl|vuurst|obsidiaan|awl|perforator|worked (animal )?bone|animal bone|bone\b|antler|plant material|seed|zaad|cordage|cord\b|twine|fiber|fibre|abrader|chisel|beitel|scraper|schraper|krabber|harpoon|arrow point|projectile|spear point|blade tool|flake|\bcore\b|monster|medicijn|touw|rope|木簡|書簡|letter|aandeel|lobby card|playing card|skelet|skull|schedel|corn|nut|hide\b|husk|grass|celt\b|pestle|mortar|mano|grinding|metate|gouge|adze|hammerstone|net sinker|sinker|fish hook|vishaak|hoe\b|shaft straight|drill|needle|toggle|whetstone|gun flint|ball/shot|knife blade|tool|gereedschap|stenen|stone|shell\b|schelp|kalebas|gourd|cocoon|kleurstof|dye|wierook|incense|resin|gum|pitch|food|vrucht|fruit|meat|sorghum|zout|salt|tabak|tobacco|soap|perfume|rind|leaf|leaves|fuel|copal|plastic|拓本|rubbing|coin|munt|currency|money|geld|tegel',),
 ('E', r'土器|坏|坩|壺|甕|鉢|瓦|埴輪|陶|磁|焼|sherd|potwand|pot\b|jar|bowl|vase|vessel|kruik|beker|kom\b|schotel|ceramic|pottery|aardewerk|tile|tegel|cup\b|dish|plate|bord|kan\b|potje|kookpot|canteen|кувшин|горш|керамич|глинян',),
 ('H', r'zijde|katoen|weefsel|doek|kleed|silk|velvet|textile|textiel|cloth|robe|hemd|broek|jurk|mantel|blanket|shawl|sari|sarong|kain|batik|ikat|tas\b|tasje|zak\b|bag|purse|mand|basket|gevlochten|mat\b|mat part|net\b|visnet|hammock|hangmat|vest|coat|jacket|kimono|袈裟|裂|布|帯|小袖|cap\b|hat\b|hoed|muts|sandaal|slof|schoen|laars|moccasin|shoe|boot|legging|dress|skirt|tunic|huipil|poncho|sash|belt|ceintuur|wrapper|kleding|kostuum|costume|lace|kant\b|embroider|borduur|fragment|border|panel|cover|cushion|kussen|rug|tapijt|carpet|kilim|weav|strap|tumpline|burden|feather|veer|beadwork|bandolier|quiver|pijlkoker|parfleche|saddle|zadel|leer|leder|leather|кукла|ткан|рубаш|платье|сапог|туфл',),
 ('D', r'figure|figuur|beeld|statue|statuette|pop\b|doll|pop |poppen|speelgoed|toy|mask|masker|面$|面|puppet|wajang|wayang|schaduwpop|haniwa|idol|carving|amulet|charm|fetish|krachtobject|jizo|bodhisattva|buddha|kannon|игрушк|матреш|свистул|скульпт',),
 ('G', r'鏡|鐸|銅|鉄|金具|金|銀|環|勾玉|管玉|小玉|玉|mirror|spiegel|bell|bel\b|klok|bronze|brons|koper|zilver|silver|gold|goud|iron|ijzer|zwaard|sword|dagger|dolk|mes\b|knife|kris|spear|speer|lans|arrow|pijl|bow\b|boog|shield|schild|club|knots|helm|armor|armour|earring|oorhanger|oorbel|ring\b|ringen|bracelet|armband|armlet|anklet|pendant|hanger|necklace|halssnoer|ketting|kraal|kralen|bead|brooch|button|knoop|ornament|versiering|sieraad|jewel|gorget|ear spool|labret|nose orn|pin\b|buckle|gesp|metal|меч|кинжал|серьг|украшен|брошь',),
 ('I', r'wood|hout|lepel|spoon|ladle|paddle|peddel|roeispaan|canoe|kano|prauw|box|doos|kist|chest|stool|stoel|chair|seat|table|tafel|kast|cabinet|furniture|meubel|lacquer|lak\b|蒔絵|漆|inrô|inro|comb|kam\b|headrest|neck ?rest|neksteun|drum|trom|rattle|rammelaar|flute|fluit|whistle|mondharp|harp|citer|zither|guitar|gitaar|violin|viool|lute|luit|xylofoon|xylophone|sanza|panpipe|musical|muziek|instrument|horn|hoorn|trumpet|staff|staf|stok|cane|cradleboard|cradle|wieg|frame|lijst|ложк|прялк|шкатул|ковш|домр|скрипк',),
 ('C', r'印譜|seal album|印|book|boek|handschrift|manuscript|sutra|経|katagami|sjabloon|stencil|vlieger|kite|扇|fan\b|waaier|papier|paper|papercut|knipsel|calligraph|書|album',),
 ('B', r'prent|print|ukie|図|drawing|tekening|cartoon|pin-up|woodcut|houtsnede|etching|ets\b',),
 ('A', r'painting|schildering|schilderij|绘|画|絵',),
]
RC=[(f,re.compile(p)) for f,p in R]
def cls(t):
    if not t: return None
    for f,p in RC:
        if p.search(t): return f
    return None
