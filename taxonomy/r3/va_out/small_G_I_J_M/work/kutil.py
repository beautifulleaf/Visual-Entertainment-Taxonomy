from urllib.parse import quote
WP = 'https://en.wikipedia.org/wiki/'
def U(x): return x if x.startswith('http') else WP + x
def met(q): return ['https://www.metmuseum.org/art/collection/search?q=' + quote(q), 'The Met collection search: ' + q, 'objects in the Metropolitan Museum of Art matching “%s”' % q]
def vam(q): return ['https://collections.vam.ac.uk/search/?q=' + quote(q), 'V&A collections search: ' + q, 'objects in the Victoria and Albert Museum matching “%s”' % q]
def bm(q): return ['https://www.britishmuseum.org/collection/search?keyword=' + quote(q), 'British Museum collection search: ' + q, 'objects in the British Museum matching “%s”' % q]
def si(q): return ['https://collections.si.edu/search/results.htm?q=' + quote(q), 'Smithsonian collections search: ' + q, 'Smithsonian objects incl. the National Museum of the American Indian']
def ch(q): return ['https://collection.cooperhewitt.org/search/collection/?query=' + quote(q), 'Cooper Hewitt collection search: ' + q, 'objects in Cooper Hewitt, Smithsonian Design Museum']
def moma(q): return ['https://www.moma.org/collection/?q=' + quote(q), 'MoMA collection search: ' + q, 'works in the Museum of Modern Art, New York']
def tate(q): return ['https://www.tate.org.uk/search?q=' + quote(q), 'Tate search: ' + q, 'works and artists in the Tate collection']
def wpl(a, label, what): return [U(a), label, what]
