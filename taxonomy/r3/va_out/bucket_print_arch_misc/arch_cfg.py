from common import *
from arch import works, architect_group, architect_info, arch_gloss
import re

def clean_sub(g):
    g = re.sub(r';?\s*(the )?(art movement|painting leaf|decorative arts leaf|decorative leaf)[^;)]*(artists:T\d+)', '', g)
    g = re.sub(r'\s*\((decorative leaf )?artists:T\d+\)', '', g)
    g = re.sub(r'\s*\(T\d+ note: a kind\)', '', g)
    g = re.sub(r';?\s*non-Western slice routed it west', '', g)
    g = re.sub(r'\s*(as )?tagged on buildings = ', ' = ', g)
    return g.strip(' ;')

def substyles(leaf, groupmap, order):
    """Keep the leaf's sub-style rows (non-maker, architecture_west), ordered by `order` (list of names)."""
    rows = []
    for r in leaf['rows']:
        if is_maker(r) or r[1].startswith('Gathered'):
            continue
        g = groupmap.get(r[1], r[1])
        rows.append([r[0], g, clean_sub(r[2]), r[3], 0])
    idx = {n: i for i, n in enumerate(order)}
    gi = {}
    for k in rows:
        gi.setdefault(k[1], len(gi))
    rows.sort(key=lambda k: (gi[k[1]], idx.get(k[0], 999)))
    return rows

def architects(leaf, regmap, cutoff, revival, regorder, moves=None):
    moves = moves or {}
    rows = []
    for r in leaf['rows']:
        if not is_maker(r):
            continue
        if not r[0].strip():
            MOVES.append([r[0], leaf['code'], 'A5-111']); continue
        if r[0] in moves:
            MOVES.append([r[0], leaf['code'], moves[r[0]]]); continue
        info = architect_info(r)
        g = architect_group(r, regmap, cutoff, revival)
        b = 9999
        if info and re.match(r'^-?\d+$', info['birth'] or ''):
            b = int(info['birth'])
        rows.append((g, b, [r[0], g, arch_gloss(r, info), r[3], 1]))
    oi = {g: i for i, g in enumerate(regorder)}
    cnt = collections.Counter(g for g, _, _ in rows)
    rows.sort(key=lambda x: (oi.get(x[0], 500 - cnt[x[0]] if cnt[x[0]] > 1 else 900), x[0], x[1]))
    return [k for _, _, k in rows]

UNESCO = ['https://whc.unesco.org/en/list/', 'UNESCO World Heritage List', 'every inscribed World Heritage site, searchable by country and keyword']
POP = ['https://pop.culture.gouv.fr/', 'POP: Mérimée (French heritage register)', 'all protected monuments historiques of France, searchable by period and style']
NHLE = ['https://historicengland.org.uk/listing/the-list/', 'National Heritage List for England', 'every listed building and scheduled monument in England']
NRHP = ['https://www.nps.gov/subjects/nationalregister/database-research.htm', 'US National Register of Historic Places', 'database of all NRHP-listed buildings, searchable by architectural style']
def cat(title, what):
    return [wp('Category:' + title), 'Wikipedia: Category:' + title, what]

CFG = {}

CFG['K4-13'] = dict(
    axis='Sub-styles and phases first, then regional schools; works: every gathered exemplar building (architecture_exemplars.csv) tagged with the style or one of its sub-styles that has a Wikipedia article or a heritage/UNESCO listing, built before 1700, by phase/sub-style then building type, dated order; architects by the region of their buildings, medieval masters first, later restorers last',
    sections=[('Early Gothic buildings', ['early gothic architecture']), ('Romano-Gothic (transitional) buildings', ['romano-gothic']),
              ('High Gothic buildings', ['classic gothic']), ('Rayonnant buildings', ['rayonnant']), ('Late Gothic buildings', ['late gothic', 'sondergotik']),
              ('Flamboyant buildings', ['flamboyant']), ('International Gothic buildings', ['international gothic']),
              ('Early English Gothic buildings', ['early english gothic']), ('Decorated Gothic buildings', ['decorated gothic']), ('Perpendicular Gothic buildings', ['perpendicular gothic']),
              ('English Gothic buildings', ['english gothic architecture']), ('French Gothic buildings', ['french gothic architecture']),
              ('Plantagenet (Angevin) Gothic buildings', ['plantagenet style']), ('Meridional Gothic buildings', ['meridional gothic']),
              ('Brabantine Gothic buildings', ['brabantine gothic', 'demer gothic', 'mosan gothic']), ('Scheldt Gothic buildings', ['scheldt gothic architecture']), ('Holland Gothic buildings', ['holland gothic']),
              ('Brick Gothic buildings', ['brick gothic']), ('Czech (Bohemian) Gothic buildings', ['czech gothic architecture']), ('Belarusian Gothic buildings', ['belarusian gothic']),
              ('Italian Gothic buildings', ['italian gothic architecture']), ('Venetian Gothic buildings', ['venetian gothic architecture']),
              ('Spanish Gothic buildings', ['spanish gothic architecture']), ('Catalan Gothic buildings', ['catalan gothic']), ('Valencian Gothic buildings', ['valencian gothic']),
              ('Mallorcan repopulation churches', ['esglésies de repoblament de mallorca']), ('Isabelline Gothic buildings', ['isabelline']),
              ('Gothic Survival buildings', ['gothic survival architecture'])],
    generic=['gothic architecture', 'gothic art', 'gothic style'], prefix='Gothic', hi=1700,
    groupmap={'Phases': 'Sub-styles and phases', 'Sub-styles': 'Sub-styles and phases'},
    suborder=['Early Gothic architecture', 'Romano-Gothic', 'classic gothic', 'Rayonnant', 'Late Gothic', 'Sondergotik', 'Flamboyant', 'International Gothic', 'Gothic Survival architecture',
              'French Gothic architecture', 'Plantagenet style', 'Meridional Gothic', 'English Gothic architecture', 'Early English Gothic', 'Decorated Gothic', 'Perpendicular Gothic',
              'Brabantine Gothic', 'Scheldt Gothic architecture', 'Demer Gothic', 'Mosan gothic', 'Holland gothic', 'Brick Gothic', 'Czech Gothic architecture', 'Belarusian Gothic',
              'Italian Gothic architecture', 'Venetian Gothic architecture', 'Spanish Gothic architecture', 'Catalan Gothic', 'Valencian Gothic', 'Esglésies de repoblament de Mallorca', 'Isabelline'],
    regmap={'France': 'French cathedral masters', 'Belgium': 'Brabantine and Netherlandish masters (Keldermans, Van Ruysbroeck)', 'Netherlands': 'Brabantine and Netherlandish masters (Keldermans, Van Ruysbroeck)',
            'Germany': 'German and Central European masters (Cologne, Parler)', 'Czech Republic': 'German and Central European masters (Cologne, Parler)', 'Hungary': 'German and Central European masters (Cologne, Parler)', 'Denmark': 'German and Central European masters (Cologne, Parler)',
            'Spain': 'Spanish, Catalan and Valencian masters', 'Italy': 'Italian Gothic masters', 'United Kingdom': 'English master masons'},
    cutoff=1700, revival='Restorers, completers and revival architects',
    regorder=['French cathedral masters', 'English master masons', 'German and Central European masters (Cologne, Parler)', 'Brabantine and Netherlandish masters (Keldermans, Van Ruysbroeck)',
              'Italian Gothic masters', 'Spanish, Catalan and Valencian masters', 'Restorers, completers and revival architects'],
    catalogues=[[wp('List of Gothic cathedrals in Europe'), 'Wikipedia: List of Gothic cathedrals in Europe', 'the Gothic cathedrals of Europe by country'],
                cat('Gothic architecture by country', 'all Wikipedia articles on Gothic buildings, by country'), POP, NHLE, UNESCO],
)

CFG['K5-23'] = dict(
    axis='Phases and sub-styles, then regional schools; works: every gathered exemplar building tagged with the style or a sub-style/regional Baroque with a Wikipedia article or heritage/UNESCO listing, built before 1800, by school then building type; architects by the region of their buildings',
    sections=[('Proto- and Early Baroque buildings', ['proto-baroque', 'early baroque']), ('High Baroque buildings', ['high baroque']), ('Late Baroque buildings', ['late baroque']),
              ('Baroque Gothic buildings (Santini)', ['baroque gothic']), ('Classicist Baroque buildings', ['classicist baroque']), ('Country Baroque buildings', ['country baroque architecture']),
              ('Italian Baroque buildings', ['italian baroque architecture', 'italian baroque']), ('Milanese Baroque buildings', ['milanese baroque']), ('Neapolitan Baroque buildings', ['neapolitan baroque art']),
              ('Lecce Baroque buildings', ['barocco leccese']), ('Sicilian Baroque buildings', ['sicilian baroque']), ('Maltese Baroque buildings', ['maltese baroque architecture']),
              ('Louis XIII style buildings', ['louis xiii style']), ('Louis XIV style buildings', ['louis xiv style']), ('French Baroque buildings', ['french baroque architecture']),
              ('English Baroque buildings', ['english baroque', 'restoration style', 'william and mary style']), ('Dutch Baroque buildings', ['dutch baroque architecture']),
              ('Czech (Bohemian) Baroque buildings', ['czech baroque architecture']), ('Vilnian Baroque buildings', ['vilnian baroque']), ('Belarusian Baroque buildings', ['belarusian baroque']),
              ('Ukrainian (Cossack) Baroque buildings', ['ukrainian baroque']), ('Naryshkin (Moscow) Baroque buildings', ['naryshkin baroque', 'moscow baroque', 'golitsyn baroque']),
              ('Petrine Baroque buildings', ['petrine baroque']), ('Elizabethan Baroque buildings', ['elizabethan baroque']), ('Russian Baroque buildings', ['russian baroque']), ('Siberian Baroque buildings', ['siberian baroque']),
              ('Spanish Baroque buildings', ['spanish baroque architecture']), ('Portuguese Baroque buildings', ['portuguese baroque'])],
    generic=['baroque architecture', 'baroque', 'baroque art'], prefix='Baroque', hi=1800,
    groupmap={'Phases': 'Sub-styles and phases', 'Sub-styles': 'Sub-styles and phases'},
    suborder=['Proto-Baroque', 'Early Baroque', 'High Baroque', 'Late Baroque', 'classicist baroque', 'baroque gothic', 'country baroque architecture', 'Louis XIII style', 'Louis XIV style'],
    regmap={'Italy': 'Italian Baroque architects', 'Malta': 'Italian Baroque architects', 'France': 'French Baroque architects', 'Russia': 'Russian Baroque architects (Petrine and Elizabethan)',
            'Ukraine': 'Russian Baroque architects (Petrine and Elizabethan)', 'Netherlands': 'Dutch Baroque architects', 'United Kingdom': 'English Baroque architects (Wren circle)',
            'Czech Republic': 'Central European Baroque architects', 'Slovakia': 'Central European Baroque architects', 'Austria': 'Central European Baroque architects', 'Germany': 'Central European Baroque architects',
            'Slovenia': 'Central European Baroque architects', 'Croatia': 'Central European Baroque architects', 'Switzerland': 'Central European Baroque architects', 'Belarus': 'Vilnian and Belarusian Baroque architects'},
    cutoff=1760, revival='Later architects of buildings tagged Baroque',
    regorder=['Italian Baroque architects', 'French Baroque architects', 'Central European Baroque architects', 'English Baroque architects (Wren circle)', 'Dutch Baroque architects',
              'Russian Baroque architects (Petrine and Elizabethan)', 'Vilnian and Belarusian Baroque architects', 'Later architects of buildings tagged Baroque'],
    catalogues=[cat('Baroque architecture by country', 'all Wikipedia articles on Baroque buildings, by country'), POP, NHLE, UNESCO,
                ['https://www.pamatkovykatalog.cz/', 'Památkový katalog (Czech heritage catalogue)', 'every listed monument of the Czech Republic, including the Bohemian Baroque']],
)

CFG['K5-22'] = dict(
    axis='Phases first (Early, High, Mannerist), then regional Renaissances; works: every gathered exemplar building tagged with the style or a sub-style with a Wikipedia article or heritage/UNESCO listing, built before 1700, by phase/region then building type; architects by the region of their buildings',
    sections=[('Early Renaissance buildings', ['early renaissance']), ('High Renaissance buildings', ['high renaissance']), ('Mannerist buildings', ['mannerist architecture', 'mannerism', 'northern mannerism']),
              ('Italian Renaissance buildings', ['italian renaissance architecture']), ('Venetian Renaissance buildings', ['venetian renaissance architecture']),
              ('French Renaissance buildings', ['french renaissance architecture', 'french renaissance', 'louis xii style', 'henry ii style', 'henry iv style']),
              ('Spanish Renaissance buildings', ['spanish renaissance architecture', 'spanish renaissance']), ('Portuguese Plain Style buildings', ['chão style']),
              ('Northern Renaissance buildings', ['northern renaissance']), ('German Renaissance buildings', ['german renaissance']), ('Weser Renaissance buildings', ['weser renaissance']),
              ('Saxon Renaissance buildings', ['saxon renaissance']), ('Brick Renaissance buildings', ['brick renaissance style', 'list of brick renaissance buildings']),
              ('Mosan Renaissance buildings', ['mosan renaissance style']), ('Jacobean buildings', ['jacobean architecture']), ('Lublin Renaissance buildings', ['lublin renaissance'])],
    generic=['renaissance architecture', 'renaissance', 'renaissance art', 'ренессанс'], prefix='Renaissance', hi=1700,
    groupmap={'Phases': 'Sub-styles and phases', 'Sub-styles': 'Sub-styles and phases'},
    suborder=['Early Renaissance', 'High Renaissance', 'Mannerist architecture', 'Mannerism', 'Northern Mannerism', 'Louis XII style', 'Henry II style', 'Henry IV style'],
    regmap={'Italy': 'Italian Renaissance architects', 'France': 'French Renaissance architects', 'Germany': 'German and Northern Renaissance architects', 'Netherlands': 'German and Northern Renaissance architects',
            'Denmark': 'German and Northern Renaissance architects', 'Sweden': 'German and Northern Renaissance architects', 'Czech Republic': 'German and Northern Renaissance architects', 'Poland': 'German and Northern Renaissance architects',
            'Spain': 'Spanish and Portuguese Renaissance architects', 'Portugal': 'Spanish and Portuguese Renaissance architects', 'United Kingdom': 'English Renaissance architects'},
    cutoff=1650, revival='Later architects of buildings tagged Renaissance',
    regorder=['Italian Renaissance architects', 'French Renaissance architects', 'Spanish and Portuguese Renaissance architects', 'German and Northern Renaissance architects', 'English Renaissance architects', 'Later architects of buildings tagged Renaissance'],
    catalogues=[cat('Renaissance architecture by country', 'all Wikipedia articles on Renaissance buildings, by country'), [wp('List of Renaissance architects'), 'Wikipedia: List of Renaissance architects', 'Renaissance architects and their works'], POP, NHLE, UNESCO],
)

CFG['K6-21'] = dict(
    axis='Regional schools (national names of the style); works: every gathered exemplar building tagged with the style or a regional school with a Wikipedia article or heritage/UNESCO listing, by school then building type; architects by the country of their buildings',
    sections=[('Vienna Secession buildings', ['vienna secession']), ('Geometric Art Nouveau buildings', ['geometric art nouveau']), ('Jugendstil buildings', ['jugendstil']),
              ('Catalan modernisme buildings', ['catalan modernism']), ('Valencian Art Nouveau buildings', ['valencian art nouveau']), ('Stile Liberty buildings', ['stile liberty']),
              ('École de Nancy buildings', ['école de nancy']), ('Hungarian Secession buildings', ['secessionist architecture in hungary']), ('Riga Art Nouveau buildings', ['art nouveau architecture in riga']),
              ('Ukrainian modern buildings', ['ukrainian modern', 'hutsul secession']), ('Sapin style buildings', ['sapin style']), ('Dutch transitional architecture', ['transitional architecture'])],
    generic=['art nouveau architecture', 'art nouveau'], prefix='Art Nouveau', hi=1930,
    groupmap={'Regional schools': 'Regional schools'},
    suborder=['Art Nouveau architecture in Riga', 'École de Nancy', 'Vienna Secession', 'Jugendstil', 'Geometric Art Nouveau', 'secessionist architecture in Hungary', 'Catalan modernism', 'Valencian Art Nouveau', 'Stile Liberty'],
    regmap={'Spain': 'Catalan modernisme and Spanish architects', 'Netherlands': 'Dutch Nieuwe Kunst architects', 'France': 'French Art Nouveau architects (Paris, Nancy)', 'Belgium': 'Belgian Art Nouveau architects',
            'Germany': 'Jugendstil architects', 'Switzerland': 'Jugendstil architects', 'Austria': 'Vienna Secession and Central European architects', 'Czech Republic': 'Vienna Secession and Central European architects',
            'Hungary': 'Hungarian Secession architects', 'Romania': 'Hungarian Secession architects', 'Italy': 'Stile Liberty architects', 'Latvia': 'Riga and Baltic Art Nouveau architects', 'Ukraine': 'Ukrainian modern architects'},
    cutoff=None, revival='',
    regorder=['Belgian Art Nouveau architects', 'French Art Nouveau architects (Paris, Nancy)', 'Catalan modernisme and Spanish architects', 'Vienna Secession and Central European architects', 'Jugendstil architects',
              'Hungarian Secession architects', 'Stile Liberty architects', 'Dutch Nieuwe Kunst architects', 'Riga and Baltic Art Nouveau architects', 'Ukrainian modern architects'],
    catalogues=[['https://www.artnouveau.eu/', 'Réseau Art Nouveau Network', 'the Art Nouveau heritage of its member cities across Europe'], cat('Art Nouveau architecture by country', 'all Wikipedia articles on Art Nouveau buildings, by country'),
                [wp('List of Art Nouveau architects'), 'Wikipedia: List of Art Nouveau architects', 'Art Nouveau architects by country'], POP, UNESCO],
)

CFG['K2-17'] = dict(
    axis='Sub-styles, then regionalisms; works: every gathered exemplar building tagged eclectic or with a listed sub-style with a Wikipedia article or heritage listing, by sub-style then building type; architects by the country of their buildings',
    sections=[('Stile Umbertino buildings', ['stile umbertino']), ('Resort architecture (Bäderarchitektur)', ['resort architecture']), ('Regionalist buildings', ['regionalism', 'regionalist architecture in spain']),
              ('Neo-Basque buildings', ['neo-basque style']), ('Português Suave buildings', ['soft portuguese style']), ('French provincial buildings', ['french provincial architecture'])],
    generic=['eclectic architecture', 'eclecticism', 'eclecticism in art'], prefix='Eclectic', hi=1950,
    groupmap={'Sub-styles': 'Sub-styles', 'Regionalism': 'Regionalisms'},
    suborder=['Stile umbertino', 'Resort architecture', 'Regionalism', 'regionalist architecture in Spain', 'Neo-Basque style', 'Soft Portuguese style', 'French provincial architecture'],
    regmap={'Spain': 'Spain', 'France': 'France', 'Italy': 'Italy', 'Portugal': 'Portugal'},
    cutoff=None, revival='', regorder=['France', 'Spain', 'Italy', 'Portugal'],
    catalogues=[[wp('Eclecticism in architecture'), 'Wikipedia: Eclecticism in architecture', 'overview with the main buildings by country'], POP,
                ['https://www.culturaydeporte.gob.es/cultura/patrimonio/bienes-culturales-protegidos.html', 'Spain: Bienes culturales protegidos', 'the Spanish register of protected cultural property'], UNESCO],
)

CFG['K2-6'] = dict(
    axis='Phases and sub-styles (Romantic and Picturesque first, then High Victorian, Collegiate, Carpenter and national variants); works: every gathered exemplar building tagged with the style or a sub-style with a Wikipedia article or heritage listing, by sub-style then building type; architects by the country of their buildings',
    sections=[('Romantic (early Gothic Revival) buildings', ['romanticism', 'romantic architecture']), ('Cottages ornés', ['cottage orné']), ('Castellated Gothic buildings', ['castellated gothic']),
              ('Scottish baronial buildings', ['scottish baronial architecture']), ('High Victorian Gothic buildings', ['high victorian gothic']), ('Collegiate Gothic buildings', ['collegiate gothic', 'collegiate gothic in north america']),
              ('Carpenter Gothic buildings', ['carpenter gothic']), ('Maximilianstil buildings', ['maximilianstil']), ('Brick Gothic Revival buildings', ['märkische backsteingotik']),
              ('Willem II Gothic buildings', ['willem ii gotiek']), ('Russian pseudo-Gothic buildings', ['russian pseudo-gothic'])],
    generic=['gothic revival'], prefix='Gothic Revival', hi=None,
    groupmap={'Romantic historicism': 'Sub-styles', 'Sub-styles': 'Sub-styles', 'Picturesque': 'Sub-styles', 'Regional schools': 'Sub-styles'},
    suborder=['Romanticism', 'Romantic architecture', 'cottage orné', 'Castellated Gothic', 'Scottish baronial architecture', 'High Victorian Gothic', 'Collegiate Gothic', 'Carpenter Gothic', 'Maximilianstil', 'märkische Backsteingotik', 'Willem II Gotiek', 'Russian pseudo-gothic'],
    regmap={'United Kingdom': 'British Gothic Revival architects', 'United States': 'American Gothic Revival architects', 'Germany': 'German Gothic Revival architects (Cologne, Hanover school)', 'Netherlands': 'Dutch and Belgian Gothic Revival architects',
            'Russia': 'Russian Gothic Revival architects', 'Spain': 'Spanish neo-Gothic architects'},
    cutoff=None, revival='', regorder=['British Gothic Revival architects', 'American Gothic Revival architects', 'German Gothic Revival architects (Cologne, Hanover school)', 'Dutch and Belgian Gothic Revival architects', 'Russian Gothic Revival architects', 'Spanish neo-Gothic architects'],
    catalogues=[[wp('List of Gothic Revival architecture'), 'Wikipedia: List of Gothic Revival architecture', 'Gothic Revival buildings worldwide by country'], cat('Gothic Revival architecture by country', 'all Wikipedia articles on Gothic Revival buildings, by country'), NHLE, NRHP],
)

CFG['K2-10'] = dict(
    axis='Sub-styles; works: every gathered exemplar building tagged with the style or a sub-style with a Wikipedia article or heritage listing, by sub-style then building type; architects by the country of their buildings',
    sections=[('Palazzo style buildings', ['palazzo style architecture']), ('Semper–Nicolai school buildings', ['semper nicolai school']), ('Châteauesque buildings', ['châteauesque']),
              ('Neo-Louis XIII buildings', ['neo-louis xiii style']), ('Flemish Renaissance Revival buildings', ['flemish renaissance revival architecture']), ('Nordic Neo-Renaissance buildings', ['severská neorenesance']),
              ('Neo-Plateresque buildings', ['neo-plateresque architecture'])],
    generic=['renaissance revival architecture'], prefix='Renaissance Revival', hi=None,
    groupmap={'Sub-styles': 'Sub-styles'},
    suborder=['Palazzo style architecture', 'Semper Nicolai school', 'châteauesque', 'Neo-Louis XIII style', 'Flemish Renaissance Revival architecture', 'severská neorenesance', 'Neo-Plateresque architecture'],
    regmap={}, cutoff=None, revival='', regorder=['France', 'Germany', 'Belgium', 'United Kingdom', 'United States', 'Canada'],
    catalogues=[cat('Renaissance Revival architecture by country', 'all Wikipedia articles on Renaissance Revival buildings, by country'), POP, NHLE, NRHP],
)

CFG['K6-15'] = dict(
    axis='Phases (Postconstructivism, then Stalinist Empire style) and national variants; works: every gathered exemplar building tagged with the style or a sub-style with a Wikipedia article or heritage listing, by phase then building type; architects by the country of their buildings',
    sections=[('Postconstructivist buildings', ['postconstructivism']), ('Stalinist Empire style buildings', ['stalinist empire style', 'soviet classicism']), ('Socialist realist buildings in Poland', ['socialist architecture in poland'])],
    generic=['stalinist architecture'], prefix='Stalinist', hi=1965,
    groupmap={'Phases': 'Sub-styles and phases', 'Sub-styles': 'Sub-styles and phases'},
    suborder=['Postconstructivism', 'Stalinist Empire style'],
    regmap={'Russia': 'Russia', 'Belarus': 'Belarus (Minsk rebuilding)', 'Ukraine': 'Ukraine', 'Poland': 'Poland', 'Georgia': 'Caucasus', 'Armenia': 'Caucasus', 'Latvia': 'Baltic republics'},
    cutoff=None, revival='', regorder=['Russia', 'Belarus (Minsk rebuilding)', 'Ukraine', 'Caucasus', 'Baltic republics', 'Poland'],
    catalogues=[cat('Stalinist architecture', 'Wikipedia articles on Stalinist buildings'), ['https://opendata.mkrf.ru/opendata/7705851331-egrkn', 'EGROKN: Russian unified register of cultural heritage', 'all protected monuments of the Russian Federation (open data)'],
                [wp('Seven Sisters (Moscow)'), 'Wikipedia: Seven Sisters (Moscow)', 'the seven Stalinist high-rises of Moscow']],
)

CFG['K5-24'] = dict(
    axis='Phases and sub-styles (Louis XVI, Adam, Directoire, Zopf, Biedermeier), then regional schools; works: every gathered exemplar building tagged with the style or a sub-style with a Wikipedia article or heritage listing, built before 1900, by sub-style then building type; architects by the country of their buildings',
    sections=[('Louis XVI style buildings', ['louis xvi style']), ('Adam style buildings', ['adam style']), ('Zopf style buildings', ['zopf style']), ('Gustavian buildings', ['gustavian style']),
              ('Directoire buildings', ['directoire style']), ('Biedermeier buildings', ['biedermeier']), ('Louis-Philippe buildings', ['louis-philippe style']),
              ('Italian Neoclassical buildings', ['italian neoclassical architecture']), ('Russian Neoclassical buildings', ['neoclassical architecture in russia']), ('Waterstaat style churches', ['waterstaatsstijl'])],
    generic=['neoclassical architecture', 'neoclassicism', 'classicism', 'neoclassical'], prefix='Neoclassical', hi=1900,
    groupmap={'Phases': 'Sub-styles', 'Sub-styles': 'Sub-styles', 'Regional schools': 'Regional schools'},
    suborder=['Louis XVI style', 'Adam style', 'Zopf style', 'Directoire style', 'Biedermeier', 'Louis-Philippe style'],
    regmap={'Russia': 'Russian Neoclassical architects', 'Italy': 'Italian Neoclassical architects', 'Malta': 'Italian Neoclassical architects', 'Sweden': 'Nordic Neoclassical architects', 'Finland': 'Nordic Neoclassical architects',
            'Norway': 'Nordic Neoclassical architects', 'Germany': 'German Neoclassical architects', 'Netherlands': 'Dutch and Belgian Neoclassical architects', 'Belgium': 'Dutch and Belgian Neoclassical architects', 'France': 'French Neoclassical architects'},
    cutoff=None, revival='', regorder=['French Neoclassical architects', 'Italian Neoclassical architects', 'German Neoclassical architects', 'Russian Neoclassical architects', 'Nordic Neoclassical architects', 'Dutch and Belgian Neoclassical architects'],
    catalogues=[cat('Neoclassical architecture by country', 'all Wikipedia articles on Neoclassical buildings, by country'), POP, NHLE, NRHP, UNESCO],
)

def build_arch(code, extra_rows=None, moves=None):
    c = CFG[code]
    leaf = LEAVES[code]
    kinds = substyles(leaf, c['groupmap'], c['suborder'])
    kinds += extra_rows or []
    kinds += works(c['sections'], c['generic'], c['prefix'], hi=c['hi'])
    kinds += architects(leaf, c['regmap'], c['cutoff'], c['revival'], c['regorder'], moves)
    alias = list(leaf['alias_rows'])
    return dict(axis=c['axis'], catalogues=c['catalogues'], kinds=kinds, alias_rows=alias)
