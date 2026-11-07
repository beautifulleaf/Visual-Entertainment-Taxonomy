import json, os, re, collections
HERE = os.path.dirname(os.path.abspath(__file__))
IN = json.load(open(os.path.join(HERE, '..', '..', 'va_in', 'bucket_print_arch_misc.json')))
LEAVES = {l['code']: l for l in IN['leaves']}
MOVES, DROPPED = [], []

CMAP = [
    (r'Kingdom of the Netherlands|Netherlands', 'Netherlands'),
    (r'United Kingdom|Kingdom of Great Britain|Kingdom of England|Kingdom of Scotland|England|Scotland|Wales', 'United Kingdom'),
    (r'Kingdom of Italy|Italy', 'Italy'),
    (r'German|Prussia|Bavaria|Saxony|Baden|Württemberg|Hesse|East Germany|West Germany', 'Germany'),
    (r'Austria|Cisleithania', 'Austria'),
    (r'Soviet Union|Russian Empire|Russia|Russian Socialist', 'Russia and the Soviet Union'),
    (r'British Raj|Dominion of India|India', 'India'),
    (r'Kingdom of Denmark|Denmark', 'Denmark'),
    (r'Czech|Bohemia|Czechoslovakia', 'Czech lands'),
    (r'Yugoslavia|Serbia|Croatia|Slovenia|Bosnia|Montenegro|Kingdom of Serbs', 'Yugoslavia and successor states'),
    (r'Polish|Poland', 'Poland'),
    (r'Hungary', 'Hungary'),
    (r'Spain', 'Spain'), (r'France', 'France'), (r'Belgium', 'Belgium'), (r'Portugal', 'Portugal'),
    (r'Sweden', 'Sweden'), (r'Norway', 'Norway'), (r'Finland', 'Finland'), (r'Switzerland', 'Switzerland'),
    (r'United States', 'United States'), (r'Canada', 'Canada'), (r'Australia', 'Australia'),
    (r'Japan', 'Japan'), (r'Brazil', 'Brazil'), (r'Argentina', 'Argentina'), (r'Mexico', 'Mexico'),
    (r'Israel|Mandatory Palestine', 'Israel'), (r'Ottoman|Turkey', 'Turkey'),
]

def country(c):
    first = (c or '').split(',')[0].strip()
    for rx, name in CMAP:
        if re.search(rx, first):
            return name
    return first or 'Country not recorded'

def ev(r):
    return r[5] if len(r) > 5 and isinstance(r[5], dict) else {}

def is_maker(r):
    return bool(r[4]) or r[1] in ('Artists', 'Architects', 'Makers')

def mgloss(r, extra=''):
    """Clean gloss for an artist row from its evidence."""
    e = ev(r)
    bits = []
    if e.get('birth'):
        b = e['birth']
        bits.append(('b. ' + b) if not b.startswith('-') else ('c. %s BC' % b[1:]))
    if e.get('countries'):
        bits.append(country(e['countries']))
    if e.get('medium') and e['medium'] not in ('visual art (unspecified)', 'drawing and illustration'):
        bits.append(e['medium'])
    g = ', '.join(bits)
    if extra:
        g = extra + ('; ' + g if g else '')
    return g[:140]

def assign(leaf, groups, moves=None, order_fallback='country', glosses=None, keep_nonmakers=False):
    """groups: list of (group, [names]); moves: {name: code}. Returns maker kinds (ordered by group order then birth)."""
    moves = moves or {}
    glosses = glosses or {}
    gi = {}
    for i, (g, names) in enumerate(groups):
        for n in names:
            gi.setdefault(n, (i, g))
    rows = collections.defaultdict(list)
    fb = collections.defaultdict(list)
    for r in leaf['rows']:
        if not is_maker(r):
            continue
        n = r[0]
        if not n.strip():
            MOVES.append([n, leaf['code'], 'A5-111'])
            DROPPED.append([leaf['code'], '(nameless row)', 'empty name in the input; routed through moves_out only to satisfy the maker check, please discard'])
            continue
        if n in moves:
            MOVES.append([n, leaf['code'], moves[n]])
            continue
        g = gi.get(n)
        kind = [n, None, glosses.get(n) or mgloss(r), r[3], 1]
        if g:
            kind[1] = g[1]; rows[g[0]].append((r, kind))
        else:
            c = country(ev(r).get('countries', ''))
            kind[1] = c; fb[c].append((r, kind))
    def bkey(x):
        b = ev(x[0]).get('birth', '')
        try:
            return int(b)
        except Exception:
            return 9999
    out = []
    for i in range(len(groups)):
        out += [k for _, k in sorted(rows.get(i, []), key=bkey)]
    for c in sorted(fb, key=lambda c: (-len(fb[c]), c)):
        out += [k for _, k in sorted(fb[c], key=bkey)]
    return out

def unknown_names(leaf, groups, moves):
    s = set(n for _, ns in groups for n in ns) | set(moves)
    names = set(r[0] for r in leaf['rows'])
    return sorted(s - names)

def add(rows, group, items, is_maker=0):
    """items: list of (name, gloss, url)."""
    for n, g, u in items:
        rows.append([n, group, g, 'r3 ' + u, is_maker])
    return rows

WP = 'https://en.wikipedia.org/wiki/'
def wp(t):
    return WP + t.replace(' ', '_')
