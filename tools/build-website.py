"""Build the Maurizio Dècina website from the captured source pages.

Outputs (all under public/):
  index.html                       English home page assembled from tools/home-main.html
  teaching.html                    the complete original Italian homepage (teaching archive)
  stuff/decinabiography.htm        English CV, complete, with page header and contents rail
  stuff/decinabiografia.htm        Italian CV, complete, with page header and contents rail
  stuff/decinapublications.htm     complete publication list with category anchors
  sitemap.xml

The audit at the end compares the text and link order of every generated
source page with the captured original and writes content-audit.json.
"""
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote, quote
from xml.sax.saxutils import escape as xml_escape
from lxml import html
from datetime import date
import json, re, difflib
from html import entities as html_entities

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
SOURCE = ROOT / 'design' / 'source-content'
TOOLS = ROOT / 'tools'
SITE_URL = 'https://mauriziodecina.it/'

asset_manifest = json.loads((ROOT / 'asset-manifest.json').read_text(encoding='utf-8'))
assets = {unquote(urlsplit(x['url']).path).lstrip('/'): x for x in asset_manifest['assets']}
records = json.loads((SOURCE / 'content-manifest.json').read_text(encoding='utf-8'))

FONTS = ('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400'
         '&family=Literata:ital,opsz,wght@0,7..72,300..900;1,7..72,300..900&display=swap')
BLOCK_TAGS = {'p', 'blockquote', 'div', 'ul', 'ol', 'table', 'li', 'h1', 'h2', 'h3', 'h4', 'tr', 'td'}


def normalize(value):
    return ' '.join(value.split())


def source_document(key):
    raw = (SOURCE / (key + '.html')).read_bytes().decode('cp1252')
    # Legacy entities without semicolons are resolved the way browsers resolve them.
    raw = re.sub(r'&([A-Za-z][A-Za-z0-9]*)(?![A-Za-z0-9;])',
                 lambda m: '&' + m[1] + ';' if m[1] + ';' in html_entities.html5 else m[0], raw)
    return html.document_fromstring(raw)


def clean(body, key, prefix):
    for node in body.xpath('.//font'):
        if node.get('size') == '1':
            node.tag = 'span'
            node.attrib.clear()
            node.set('class', 'file-meta')
        else:
            node.drop_tag()
    for node in body.iter():
        if not isinstance(node.tag, str):
            continue
        for name in ('align', 'width', 'height', 'border', 'cellpadding', 'cellspacing',
                     'bgcolor', 'style', 'face', 'size', 'color'):
            node.attrib.pop(name, None)
    for anchor in body.xpath('.//a[@href]'):
        original = anchor.get('href')
        absolute = urljoin(records[key]['source_url'], original)
        parts = urlsplit(absolute)
        path = unquote(parts.path).lstrip('/')
        anchor.set('data-original-href', original)
        anchor.set('data-source-url', absolute)
        if parts.hostname in ('mauriziodecina.it', 'www.mauriziodecina.it'):
            entry = assets.get(path)
            if path.endswith(('.htm', '.html')) or (entry and entry['status'] == 'downloaded'):
                anchor.set('href', prefix + quote(path, safe="/!$&'()*+,;=@-._~"))
            else:
                anchor.set('href', absolute)
        if anchor.get('target') == '_blank':
            anchor.set('rel', 'noopener')
        if re.search(r'\.(zip|rar|pdf)$', parts.path, re.I):
            anchor.set('class', 'resource-link')
    return body


def fragment(node):
    return html.tostring(node, encoding='unicode', method='html', with_tail=True)


def bulletize(node):
    """Turn a run of '· item<br>· item' lines into a list. The text is unchanged:
    the dot stays in the document, wrapped in a span so it can be styled as a marker."""
    inner = xml_escape(node.text or '') + ''.join(fragment(child) for child in node)
    items = []
    for chunk in re.split(r'<br\s*/?>', inner):
        if not normalize(re.sub(r'<[^>]+>', '', chunk).replace('&nbsp;', ' ').replace('\xa0', ' ')):
            continue
        m = re.match(r'^(?:\s|&nbsp;|\xa0)*[·•](?=\s|&nbsp;|\xa0|<)', chunk)
        if m:
            chunk = chunk[:m.end() - 1] + '<span class="cv-dot">' + chunk[m.end() - 1] + '</span>' + chunk[m.end():]
            items.append('<li>' + chunk + '</li>')
        elif re.match(r'^(?:\s|&nbsp;|\xa0)*[·•]', chunk):
            # The dot is glued to the first word in the source; keep it in the text node.
            items.append('<li class="cv-dot-attached">' + chunk + '</li>')
        else:
            items.append('<li class="cv-plain">' + chunk + '</li>')
    if not items:
        return
    new = html.fragment_fromstring('<ul class="cv-list">' + ''.join(items) + '</ul>')
    new.tail = node.tail
    node.getparent().replace(node, new)


# ---------------------------------------------------------------------------
# Shared chrome
# ---------------------------------------------------------------------------
def header(prefix):
    return (
        '<a class="skip-link" href="#main">Skip to content</a>'
        '<header class="site-header"><div class="wrap header-inner">'
        '<a class="wordmark" href="' + prefix + 'index.html">Maurizio Dècina</a>'
        '<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Menu">'
        '<span></span><span></span><span></span></button>'
        '<nav id="site-nav" class="site-nav" aria-label="Main">'
        '<ul>'
        '<li><a href="' + prefix + 'index.html#biography">About</a></li>'
        '<li><a href="' + prefix + 'index.html#research">Research</a></li>'
        '<li><a href="' + prefix + 'index.html#career">Career</a></li>'
        '<li><a href="' + prefix + 'index.html#publications">Publications</a></li>'
        '<li><a href="' + prefix + 'index.html#teaching">Teaching</a></li>'
        '<li><a href="' + prefix + 'teaching.html">Archive</a></li>'
        '<li><a href="' + prefix + 'index.html#contact">Contact</a></li>'
        '</ul>'
        '<a class="btn nav-cta" href="' + prefix + 'stuff/decinabiography.htm">View CV</a>'
        '</nav></div></header>'
    )


def icon(paths, viewbox='0 0 24 24'):
    return ('<svg viewBox="' + viewbox + '" width="20" height="20" aria-hidden="true" focusable="false" '
            'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
            + paths + '</svg>')


ICON_MAIL = icon('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 6.5 8.5 6.5 8.5-6.5"/>')
ICON_PIN = icon('<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>')
ICON_UP = icon('<path d="M12 19V5M6 11l6-6 6 6"/>')

# Profile links shown as round icons in the footer. An entry renders only once
# it has a URL; add the confirmed profile address to switch it on.
FOOTER_PROFILES = [
    ('LinkedIn', '', icon('<path d="M7 10v7M7 7v.01M11 17v-7M11 13.5c0-2 1.2-3.5 3-3.5s3 1.2 3 3.5V17"/>')),
    ('Google Scholar', '', icon('<path d="m12 4 9 6-9 6-9-6 9-6z"/><path d="M7 13.5V17c1.4 1.3 3 2 5 2s3.6-.7 5-2v-3.5"/>')),
    ('ORCID', '', icon('<circle cx="12" cy="12" r="9"/><path d="M9 10v6M9 7.5v.01M12 16v-6h2a3 3 0 0 1 0 6h-2z"/>')),
]


def footer(prefix):
    home = prefix + 'index.html'
    explore = [('About', home + '#biography'), ('Career', home + '#career'),
               ('Recognition', home + '#recognition'), ('Publications', home + '#publications'),
               ('Teaching', home + '#teaching'), ('Archive', prefix + 'teaching.html')]
    research = [('Digital Transmission', 'area-transmission'), ('ISDN &amp; Standards', 'area-isdn'),
                ('Packet Switching &amp; ATM', 'area-atm'), ('Internet &amp; Network Security', 'area-internet')]
    profiles = ''.join(
        '<li><a href="' + url + '" aria-label="' + name + '" rel="me noopener" target="_blank">' + svg + '</a></li>'
        for name, url, svg in FOOTER_PROFILES if url)
    links = lambda items: ''.join('<li><a href="' + href + '">' + label + '</a></li>' for label, href in items)
    return (
        '<footer class="site-footer"><div class="wrap footer-grid">'
        '<div class="footer-id"><p class="footer-name">Maurizio Dècina</p>'
        '<p class="footer-role">Professor Emeritus of Telecommunications<br>Politecnico di Milano</p>'
        '<p class="footer-tagline">Five decades of research, teaching and institutional service '
        'dedicated to building a more connected world.</p>'
        '<ul class="footer-social">' + profiles +
        '<li><a href="mailto:maurizio@mauriziodecina.it" aria-label="Email">' + ICON_MAIL + '</a></li></ul></div>'
        '<nav aria-label="Explore"><h2>Explore</h2><ul class="footer-links">' + links(explore) + '</ul></nav>'
        '<nav aria-label="Research"><h2>Research</h2><ul class="footer-links">'
        + links((label, home + '#' + anchor) for label, anchor in research) + '</ul></nav>'
        '<div class="footer-contact"><h2>Contact</h2><ul>'
        '<li>' + ICON_PIN + '<address>Dipartimento di Elettronica, Informazione e Bioingegneria<br>'
        'Politecnico di Milano<br>Piazza Leonardo da Vinci, 32<br>20133 Milano, Italy</address></li>'
        '<li>' + ICON_MAIL + '<a href="mailto:maurizio@mauriziodecina.it">maurizio@mauriziodecina.it</a></li>'
        '</ul></div>'
        '</div><div class="wrap footer-bottom">'
        '<p>© ' + str(date.today().year) + ' Maurizio Dècina. All rights reserved.</p>'
        '<ul class="footer-legal"><li><a href="' + prefix + 'sitemap.xml">Sitemap</a></li></ul>'
        '<a class="back-to-top" href="#top">Back to top<span>' + ICON_UP + '</span></a>'
        '</div></footer>'
    )


def shell(title, main, prefix='./', lang='en', description='', canonical='', extra_head='', body_class=''):
    meta = ''
    if description:
        meta += '<meta name="description" content="' + description.replace('"', '&quot;') + '">'
    if canonical:
        meta += '<link rel="canonical" href="' + canonical + '">'
    return (
        '<!doctype html>\n<html lang="' + lang + '"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta name="theme-color" content="#173352">'
        '<title>' + title + '</title>' + meta +
        '<link rel="icon" href="' + prefix + 'assets/favicon.svg" type="image/svg+xml">'
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link rel="stylesheet" href="' + FONTS + '">'
        '<link rel="stylesheet" href="' + prefix + 'assets/css/site.css">'
        '<script>document.documentElement.className+=" js"</script>'
        '<script src="' + prefix + 'assets/js/site.js" defer></script>' + extra_head +
        '</head><body' + (' class="' + body_class + '"' if body_class else '') + '>' +
        header(prefix) + main + footer(prefix) + '</body></html>'
    )


# ---------------------------------------------------------------------------
# Teaching archive: the complete original homepage, Italian, unchanged text
# ---------------------------------------------------------------------------
doc = source_document('homepage')
body = clean(doc.find('body'), 'homepage', './')
children = list(body)
intro = children[:5]
hero_name = intro[0]
for image in hero_name.xpath('.//img'):
    image.getparent().remove(image)
intro[1].set('class', 'affiliation')
intro[2].set('class', 'email-table')
intro[3].set('class', 'bio-title')
intro[4].set('class', 'bio-links')
masthead = (
    '<div class="wrap archive-masthead"><div class="archive-masthead-id">'
    '<p class="page-kicker" data-chrome>Teaching archive, 2001 to 2012. The original course pages in Italian, complete.</p>'
    '<p class="home-intro">Home Page di</p><h1>Maurizio Dècina</h1>' + fragment(intro[1]) + fragment(intro[2]) +
    '</div><div class="archive-masthead-links">' + fragment(intro[3]) + fragment(intro[4]) + '</div></div>'
)
for node in intro:
    body.remove(node)

featured, sections, current = [], [], None
for node in list(body):
    text = normalize(node.text_content())
    if text.startswith('Attività didattica') and node.tag == 'p':
        current = {'title': text, 'elements': [], 'id': 'attivita-' + re.search(r'\d{4}(?:-\d{4})?', text)[0]}
        node.tag = 'h2'
        node.set('class', 'course-heading')
        sections.append(current)
    if current is None:
        if text:
            node.set('class', 'featured-row')
            featured.append(node)
        elif node.xpath('.//a'):
            featured.append(node)
    else:
        current['elements'].append(node)

year_counts = {}
for section in sections:
    count = 0
    for node in section['elements'][1:]:
        text = normalize(node.text_content())
        if node.tag == 'p' and (text.startswith('Corso di') or text.startswith('Appunti del corso')):
            node.set('class', 'course-subtitle')
        if node.tag == 'a' and 'resource-link' in node.get('class', ''):
            node.set('class', 'resource-link standalone-resource')
        count += len(node.xpath('self::a[contains(@class,"resource-link")]|.//a[contains(@class,"resource-link")]'))
    year_counts[section['id']] = count

year_label = lambda title: title.replace('Attività didattica ', '').rstrip(':')
archive_nav = ('<aside class="archive-aside" data-chrome><nav class="year-nav" data-spy aria-label="Anni accademici">' +
               ''.join('<a href="#' + s['id'] + '">' + year_label(s['title']) + '</a>' for s in sections) +
               '</nav></aside>')
archive = '<div class="archive-layout">' + archive_nav + '<div class="archive-main">'
for s in sections:
    archive += ('<section id="' + s['id'] + '" class="archive-section">' + fragment(s['elements'][0]) +
                '<div class="document-content">' + ''.join(fragment(x) for x in s['elements'][1:]) + '</div></section>')
archive += '</div></div>'
teaching_main = ('<main id="main" class="archive-page" data-source-page="homepage"><span id="top"></span>' + masthead +
                 '<div class="wrap"><div class="featured-resources">' + ''.join(fragment(x) for x in featured) +
                 '</div></div>' + archive + '</main>')
(PUBLIC / 'teaching.html').write_text(shell(
    'Attività didattica 2001–2012 – Maurizio Dècina', teaching_main, './', 'it',
    description='Archivio completo dei corsi di Maurizio Dècina al Politecnico di Milano: lucidi, esercitazioni, prove e risultati dal 2001 al 2012.',
    canonical=SITE_URL + 'teaching.html'), encoding='utf-8')

# ---------------------------------------------------------------------------
# Biographies and publications
# ---------------------------------------------------------------------------
pub_counts = {}
pub_text = records['decinapublications']['body_text']
for letter in 'ABCDEFGH':
    pub_counts[letter] = len(set(re.findall(r'\(%s\.\s?(\d+)\)' % letter, pub_text)))
pub_total = sum(pub_counts.values())
category_labels = {
    'A': 'International journal papers', 'B': 'Guest editorials', 'C': 'International books and chapters',
    'D': 'International conference papers', 'E': 'Tutorial courses', 'F': 'Video tutorial course',
    'G': 'National journal papers', 'H': 'National books and chapters'}

page_meta = {
    'decinabiography': ('Curriculum vitae of Maurizio Dècina: Professor Emeritus of Telecommunications at Politecnico di Milano, IEEE Fellow, former President of the IEEE Communications Society.', 'en'),
    'decinabiografia': ('Curriculum vitae di Maurizio Dècina: professore emerito di telecomunicazioni al Politecnico di Milano, IEEE Fellow, già presidente della IEEE Communications Society.', 'it'),
    'decinapublications': ('List of selected publications by Maurizio Dècina, 1968 to 2003: international journals, guest editorials, books, conference papers and national publications.', 'en'),
}

# Page header copy for the two CV pages (chrome, excluded from the audit).
cv_labels = {
    'en': {
        'kicker': 'Curriculum vitae',
        'role': 'Professor Emeritus of Telecommunications, Politecnico di Milano',
        'intro': 'The complete curriculum vitae as written by Prof. Dècina in April 2012, when he left his chair to join the board of the Italian Communications Authority.',
        'facts': [('Born', '10 January 1943, Pescasseroli, L’Aquila'),
                  ('Degree', 'Electronic Engineering, University of Rome, 1966'),
                  ('Full professor', 'University of Rome La Sapienza, 1980'),
                  ('Politecnico di Milano', 'Professor of Telecommunications 1987 to 2012, Professor Emeritus since 2014'),
                  ('IEEE', 'Fellow, 1986')],
        'contents': 'Contents',
        'other': ('Versione italiana', 'decinabiografia.htm', 'it'),
        'document': 'Original document',
    },
    'it': {
        'kicker': 'Curriculum vitae',
        'role': 'Professore emerito di Telecomunicazioni, Politecnico di Milano',
        'intro': 'Il curriculum vitae completo scritto dal Prof. Dècina nell’aprile 2012, quando ha lasciato la cattedra per entrare nel consiglio dell’Autorità per le Garanzie nelle Comunicazioni.',
        'facts': [('Nato', '10 gennaio 1943, Pescasseroli, L’Aquila'),
                  ('Laurea', 'Ingegneria Elettronica, Università di Roma, 1966'),
                  ('Professore ordinario', 'Università di Roma La Sapienza, 1980'),
                  ('Politecnico di Milano', 'Professore di Telecomunicazioni dal 1987 al 2012, professore emerito dal 2014'),
                  ('IEEE', 'Fellow, 1986')],
        'contents': 'Indice',
        'other': ('English version', 'decinabiography.htm', 'en'),
        'document': 'Documento originale',
    },
}

for key in ('decinabiography', 'decinabiografia', 'decinapublications'):
    doc = source_document(key)
    body = clean(doc.find('body'), key, '../')
    for node in body.xpath('.//script|.//style'):
        node.getparent().remove(node)
    for image in body.xpath('.//img[@src]'):
        image.set('src', '../' + quote(unquote(urlsplit(urljoin(records[key]['source_url'], image.get('src'))).path).lstrip('/'), safe="/!$&'()*+,;=@-._~"))
    if key == 'decinapublications':
        first_heading = next((node for node in body.xpath('.//p') if normalize(node.text_content())), None)
    else:
        first_heading = next((node for node in body if normalize(node.text_content())), None)
    if first_heading is not None:
        first_heading.tag = 'h1'
        first_heading.set('class', 'article-heading')
    aside = ''
    page_head = ''
    description, lang = page_meta[key]
    if key == 'decinapublications':
        # Category headings become anchored h2 elements; the text is unchanged.
        for node in body.xpath('.//p'):
            text = normalize(node.text_content())
            m = re.match(r'^([A-H])\. ', text)
            if m and len(text) < 120:
                node.tag = 'h2'
                node.set('class', 'pub-category')
                node.set('id', 'cat-' + m[1])
        aside = ('<aside class="article-aside" data-chrome><h2>Categories</h2><nav class="category-nav" data-spy aria-label="Publication categories">' +
                 ''.join('<a href="#cat-' + c + '"><span class="cat-letter">' + c + '</span><span class="cat-name">' + category_labels[c] +
                         '</span><span class="cat-count">' + str(pub_counts[c]) + '</span></a>' for c in 'ABCDEFGH') +
                 '</nav></aside>')
    else:
        # Short emphasised lines are the CV's section titles.
        for node in body.xpath('.//p|.//li'):
            text = normalize(node.text_content())
            if not text or len(text) > 70:
                continue
            parent = node.getparent()
            inner = node.xpath('./em|./i|./strong|./b')
            wrapped = parent is not None and parent.tag in ('em', 'i', 'strong', 'b')
            if wrapped or (inner and normalize(' '.join(x.text_content() for x in inner)) == text and not node.xpath('.//a')):
                node.set('class', 'cv-section')
        toc = []
        for index, node in enumerate(body.xpath('.//*[@class="cv-section"]')):
            section_id = 'sec-' + str(index + 1)
            node.set('id', section_id)
            toc.append((section_id, normalize(node.text_content())))
        # Lines that begin with a middle dot become list items; the dot is kept.
        candidates = [n for n in body.iter('p', 'blockquote')
                      if re.search('[·•]', n.text_content())
                      and not any(isinstance(c.tag, str) and c.tag in BLOCK_TAGS for c in n)]
        for node in candidates:
            bulletize(node)
        labels = cv_labels[lang]
        other_text, other_href, other_lang = labels['other']
        page_head = (
            '<section class="cv-head" data-chrome><div class="wrap cv-head-grid">'
            '<div class="cv-head-text">'
            '<p class="page-kicker">' + labels['kicker'] + '</p>'
            '<p class="cv-head-name">Maurizio Dècina</p>'
            '<p class="cv-head-role">' + labels['role'] + '</p>'
            '<p class="cv-head-intro">' + labels['intro'] + '</p>'
            '<dl class="cv-facts">' + ''.join('<div><dt>' + t + '</dt><dd>' + d + '</dd></div>' for t, d in labels['facts']) + '</dl>'
            '<p class="cv-head-links"><a href="' + other_href + '" lang="' + other_lang + '" hreflang="' + other_lang + '">' + other_text + '</a></p>'
            '</div>'
            '<figure class="cv-head-photo"><picture>'
            '<source type="image/webp" srcset="../assets/portrait-2022-480.webp 480w, ../assets/portrait-2022.webp 860w" sizes="(min-width: 1024px) 380px, 60vw">'
            '<img src="../assets/portrait-2022.jpg" srcset="../assets/portrait-2022-480.jpg 480w, ../assets/portrait-2022.jpg 860w" sizes="(min-width: 1024px) 380px, 60vw" width="860" height="860" alt="Maurizio Dècina" decoding="async">'
            '</picture></figure>'
            '</div></section>'
        )
        aside = ('<aside class="article-aside" data-chrome><h2>' + labels['contents'] + '</h2><nav class="toc-nav" data-spy aria-label="' + labels['contents'] + '">' +
                 ''.join('<a href="#' + sid + '">' + text + '</a>' for sid, text in toc) + '</nav></aside>')
    body_content = (body.text or '') + ''.join(fragment(x) for x in body)
    layout_class = 'article-layout has-aside'
    article_class = 'source-article ' + ('publications-article' if key == 'decinapublications' else 'cv-article')
    main = ('<main id="main" data-source-page="' + key + '"><span id="top"></span>' + page_head +
            '<div class="' + layout_class + '">' + aside +
            '<article class="' + article_class + '">' + body_content + '</article></div></main>')
    title = normalize(doc.find('head').find('title').text_content())
    target = PUBLIC / 'stuff' / (key + '.htm')
    target.parent.mkdir(exist_ok=True)
    target.write_text(shell(title + ' – Maurizio Dècina', main, '../', lang, description=description,
                            canonical=SITE_URL + 'stuff/' + key + '.htm',
                            body_class='cv-page' if key != 'decinapublications' else ''), encoding='utf-8')

# ---------------------------------------------------------------------------
# Home page
# ---------------------------------------------------------------------------
home = (TOOLS / 'home-main.html').read_text(encoding='utf-8')
home = home.replace('{{PUB_TOTAL}}', str(pub_total))
for letter, count in pub_counts.items():
    home = home.replace('{{PUB_COUNT:' + letter + '}}', str(count))
for section_id, count in year_counts.items():
    home = home.replace('{{COUNT:' + section_id + '}}', ('%d files' % count) if count != 1 else '1 file')
assert '{{' not in home, 'unfilled placeholder in home-main.html'
home = home.replace('<main id="top">', '<main id="main"><span id="top"></span>', 1)

person = {
    '@context': 'https://schema.org', '@type': 'Person', 'name': 'Maurizio Dècina',
    'givenName': 'Maurizio', 'familyName': 'Dècina', 'jobTitle': 'Professor Emeritus of Telecommunications',
    'url': SITE_URL, 'image': SITE_URL + 'assets/portrait.jpg',
    'email': ['mailto:maurizio@mauriziodecina.it', 'mailto:m.decina@ieee.org'],
    'affiliation': {'@type': 'CollegeOrUniversity', 'name': 'Politecnico di Milano',
                    'address': {'@type': 'PostalAddress', 'streetAddress': 'Piazza Leonardo da Vinci, 32',
                                'postalCode': '20133', 'addressLocality': 'Milano', 'addressCountry': 'IT'}},
    'alumniOf': {'@type': 'CollegeOrUniversity', 'name': 'University of Rome'},
    'award': ['IEEE Fellow, 1986', 'IEEE Award in International Communications, 1997',
              'IEEE Third Millennium Medal, 2000', 'IEEE ComSoc/KICS Exemplary Global Service Award, 2008'],
    'knowsAbout': ['Digital transmission', 'ISDN', 'Packet switching', 'ATM', 'Network security', 'Internet infrastructure'],
}
description = ('Maurizio Dècina, Professor Emeritus of Telecommunications at Politecnico di Milano and IEEE Fellow. '
               'Biography, career, research, publications and the complete teaching archive.')
extra_head = (
    '<meta property="og:type" content="profile">'
    '<meta property="og:title" content="Maurizio Dècina">'
    '<meta property="og:description" content="' + description + '">'
    '<meta property="og:url" content="' + SITE_URL + '">'
    '<meta property="og:image" content="' + SITE_URL + 'assets/og-image.jpg">'
    '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
    '<meta name="twitter:card" content="summary_large_image">'
    '<link rel="preload" as="image" href="./assets/portrait.webp" type="image/webp" fetchpriority="high">'
    '<script type="application/ld+json">' + json.dumps(person, ensure_ascii=False) + '</script>'
)
(PUBLIC / 'index.html').write_text(shell(
    'Maurizio Dècina – Professor Emeritus of Telecommunications, Politecnico di Milano', home, './', 'en',
    description=description, canonical=SITE_URL, extra_head=extra_head, body_class='home'), encoding='utf-8')

# ---------------------------------------------------------------------------
# 404 page (Netlify and GitHub Pages serve 404.html automatically)
# ---------------------------------------------------------------------------
not_found = (
    '<main id="main" class="not-found"><span id="top"></span><div class="wrap not-found-inner">'
    '<p class="page-kicker">Page not found</p>'
    '<h1>This page does not exist on the site.</h1>'
    '<p class="section-lede">The address may be out of date. Everything on the site is reachable from these pages.</p>'
    '<ul class="not-found-links">'
    '<li><a href="/index.html">Home</a></li>'
    '<li><a href="/teaching.html">Teaching archive</a></li>'
    '<li><a href="/stuff/decinabiography.htm">Curriculum vitae</a></li>'
    '<li><a href="/stuff/decinabiografia.htm" lang="it" hreflang="it">Curriculum vitae in italiano</a></li>'
    '<li><a href="/stuff/decinapublications.htm">List of selected publications</a></li>'
    '</ul></div></main>'
)
(PUBLIC / '404.html').write_text(shell('Page not found – Maurizio Dècina', not_found, '/', 'en',
                                       extra_head='<meta name="robots" content="noindex">'), encoding='utf-8')

# ---------------------------------------------------------------------------
# Sitemap
# ---------------------------------------------------------------------------
urls = ['', 'teaching.html', 'stuff/decinabiography.htm', 'stuff/decinabiografia.htm', 'stuff/decinapublications.htm']
(PUBLIC / 'sitemap.xml').write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join('  <url><loc>' + SITE_URL + u + '</loc></url>\n' for u in urls) + '</urlset>\n', encoding='utf-8')

# ---------------------------------------------------------------------------
# Content audit: every source page keeps its words and its original link order.
# ---------------------------------------------------------------------------
audit = {}
targets = [('homepage', PUBLIC / 'teaching.html')] + [(k, PUBLIC / 'stuff' / (k + '.htm')) for k in records if k != 'homepage']
for key, path in targets:
    out = html.document_fromstring(path.read_text(encoding='utf-8'))
    content = out.xpath('//main')[0]
    for chrome in content.xpath('.//*[@data-chrome]'):
        chrome.getparent().remove(chrome)
    actual = normalize(' '.join(content.itertext()))
    expected = records[key]['body_text']
    actual_words, expected_words = actual.split(), expected.split()
    same = actual_words == expected_words
    original_links = [x['href'] for x in records[key]['links']]
    output_links = [x.get('data-original-href') for x in content.xpath('.//a[@data-original-href]')]
    audit[key] = {'output': str(path.relative_to(ROOT)).replace('\\', '/'), 'text_match': same,
                  'original_words': len(expected_words), 'rendered_words': len(actual_words),
                  'link_order_match': original_links == output_links,
                  'original_link_count': len(original_links), 'rendered_link_count': len(output_links)}
    if not same:
        audit[key]['diff'] = list(difflib.unified_diff(expected_words, actual_words, n=2))[:120]
audit['summary'] = {'publication_entries': pub_counts, 'publication_total': pub_total, 'archive_files_by_year': year_counts,
                    'archive_files_total': sum(year_counts.values())}
(ROOT / 'content-audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(audit, ensure_ascii=False, indent=2))
