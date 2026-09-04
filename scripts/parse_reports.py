#!/usr/bin/env python3
"""Parse the harvested Lesko state-report documents into structured JSON.

Input:  raw/master-index.json   (state -> category -> source doc link, from the master Google Doc)
        raw/docs/<fileId>.md    (verbatim text of each linked sub-document)
        raw/docs/<fileId>.meta.json
Output: data/states.json        (everything, one file)
        data/states/<slug>.json (one file per state, used by the app)
        data/summary.json       (counts for the README / app home screen)
"""
import json, re, os, sys, glob, hashlib
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'raw')
OUT = os.path.join(ROOT, 'data')

ABBR = {"Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA","Colorado":"CO","Connecticut":"CT","Delaware":"DE","District of Columbia":"DC","Florida":"FL","Georgia":"GA","Hawaii":"HI","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS","Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD","Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS","Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV","New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM","New York":"NY","North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK","Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC","South Dakota":"SD","Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA","Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY","Puerto Rico":"PR"}

# Canonical category keys. The master doc spells the headings slightly differently per state.
CATEGORIES = [
    ("financial", "Financial Assistance", "Personal bills, debt, rent, utilities and emergency money", "💵"),
    ("business",  "Business", "Start or grow a business, nonprofit or invention", "🏢"),
    ("jobs",      "Jobs, Education & Training", "Training for a better job, degrees and government jobs", "🎓"),
    ("health",    "Health, Dental & Pet Care", "Free and low-cost health care, prescriptions, dental and pet care", "🩺"),
    ("mentoring", "Free Local Mentoring & Research Help", "Local experts, libraries, 211 and counselors who help for free", "🧭"),
    ("housing",   "Real Estate & Housing", "Grants, cheap loans and counselors for buying or keeping a home", "🏠"),
    ("other",     "Other Resources", "Extra links listed for this state", "🔗"),
]
CAT_BY_KEY = {c[0]: c for c in CATEGORIES}

def category_key(label):
    l = label.lower()
    if 'financial' in l: return 'financial'
    if 'business' in l: return 'business'
    if 'jobs' in l or 'education' in l: return 'jobs'
    if 'health' in l or 'dental' in l: return 'health'
    if 'mentoring' in l or 'research' in l: return 'mentoring'
    if 'housing' in l or 'real estate' in l: return 'housing'
    return 'other'

# ---------------------------------------------------------------- text cleanup
BOLD = re.compile(r'(?<!\\)\*\*')
def unescape(s):
    s = BOLD.sub('', s)                      # drop bold markers first (escaped \* survive)
    s = re.sub(r'\\([\\`*_{}\[\]()#+\-.!~>&|"\'])', r'\1', s)
    s = s.replace(' ', ' ')
    return s

URL_MD   = re.compile(r'\[([^\]]*)\]\((https?://[^)\s]+)\)')
URL_AUTO = re.compile(r'<(https?://[^>\s]+)>')
URL_BARE = re.compile(r'(?<![\(<\w/])(https?://[^\s<>\)\]]+)')
URL_WWW  = re.compile(r'(?<![\w/@.])(www\.[a-z0-9.-]+\.[a-z]{2,}[^\s<>\)\]]*)', re.I)

def clean_url(u):
    u = u.rstrip('.,;:)>*')
    u = u.replace('\\_', '_').replace('\\&', '&').replace('\\#', '#').replace('\\~', '~')
    return u

# A label lifted out of a URL fragment ("&text=The%20tax...", "referrer=", "?") tells
# a reader nothing. Drop it so the app falls back to a plain-words verb plus the host.
URLISH = re.compile(r'[?&=]|https?:|%[0-9A-Fa-f]{2}|\bfbclid\b|\butm_')
def usable_label(lab):
    lab = (lab or '').strip()
    if not lab: return ''
    if URLISH.search(lab): return ''
    if re.fullmatch(r'[A-Za-z0-9_\-]{22,}', lab): return ''
    return lab

def link_type(u):
    ul = u.lower()
    if 'youtube.com' in ul or 'youtu.be' in ul: return 'video'
    if 'vimeo.com' in ul: return 'video'
    if 'docs.google.com' in ul or 'drive.google.com' in ul: return 'document'
    if ul.endswith('.pdf'): return 'pdf'
    return 'web'

def host(u):
    m = re.match(r'https?://([^/]+)', u)
    return m.group(1).lower().replace('www.', '') if m else u

def extract_links(line):
    """Return (text_without_urls, [links]) for one line."""
    links = []
    def md(m):
        label, url = m.group(1).strip(), clean_url(m.group(2))
        if label and not re.match(r'^https?://|^www\.', label.strip('* ')):
            links.append({'url': url, 'label': label.strip('* ')})
            return ' ' + label + ' '
        links.append({'url': url, 'label': ''})
        return ' '
    text = URL_MD.sub(md, line)
    def auto(m):
        links.append({'url': clean_url(m.group(1)), 'label': ''}); return ' '
    text = URL_AUTO.sub(auto, text)
    def bare(m):
        links.append({'url': clean_url(m.group(1)), 'label': ''}); return ' '
    text = URL_BARE.sub(bare, text)
    def www(m):
        links.append({'url': 'http://' + clean_url(m.group(1)), 'label': ''}); return ' '
    text = URL_WWW.sub(www, text)
    return text, links

PROGRAM_RE = re.compile(r'^\s*(?:#{1,6}\s*)?\*{3}\s*(.+?)\s*$')
GROUP_RE   = re.compile(r'^\s*(?:#{1,6}\s*)?(\d{1,2})\s*(?:…|\.\.\.|\.{1,3}|:|\))\s*([A-Z].{4,})$')
HEADING_RE = re.compile(r'^\s*#{1,6}\s*(.+?)\s*$')
NOISE_LINE = re.compile(r'^\s*(?:\||:-+:|-{3,}|Tab \d+|\\\\|pp?|[A-Za-z]{1,2})\s*$')
TRAILER_RE = re.compile(r'(Join Lesko ?Help|LeskoHelp\.com|© ?20\d\d|Matthew Lesko\.|leskohelp@gmail|Thanks for downloading|Download Free Report|Want Free Money to End Financial Stress)', re.I)
VIDEO_LABEL = re.compile(r'^(watch|intro|see)\b.*(video|this)s?:?\s*$', re.I)

STRAY_URL = re.compile(r'\(?(?:https?://|www\.)\S+\)?')
def clean_text(t):
    t = STRAY_URL.sub(' ', t)
    t = re.sub(r'(?m)^\s*[`~\'"*.\u2026\\-]{1,4}\s*$', '', t)
    t = re.sub(r'\\([#&_~*])', r'\1', t)
    t = re.sub(r'\s+([,.;:?!])', r'\1', t)
    return re.sub(r'\s{2,}', ' ', t).strip(' *:-')

def norm_title(t):
    t = re.sub(r'\\([#&_~*])', r'\1', t)
    t = re.sub(r'\s+', ' ', t).strip(' *:.-')
    return t

TITLE_MAX = 108
def split_title(t):
    """Lesko's headings are sometimes whole paragraphs. Keep a readable headline and
    return the remainder so the caller can push it into the body text."""
    t = norm_title(t)
    if len(t) <= TITLE_MAX:
        return t, ''
    for m in re.finditer(r'(?<=[a-z0-9\)\"”])\s*(?:[.?!]|…|\.\.\.)\s+', t):
        if 40 <= m.start() <= 150 and len(t) - m.end() >= 25:
            return t[:m.start()].strip(' .'), t[m.end():].strip()
    cut = t.rfind(' ', 40, TITLE_MAX + 20)
    if cut > 40 and len(t) - cut >= 25:
        return t[:cut].rstrip(' ,;:-'), t[cut:].strip()
    return t, ''

def parse_doc(text, state):
    """Split one sub-document into intro + groups of programs.

    Two layouts exist in the source documents:
      * '***Title' lines mark a program; optional 'N… Heading' lines group them.
      * 'N… Heading' lines ARE the programs (Financial Assistance docs), with bullets under them.
    Both are handled: a numbered heading opens a group, and any content that appears under it before
    the first '***' program becomes an implicit program carrying the heading's title.
    """
    raw_lines = [l for l in text.replace('\r', '').split('\n') if l.strip()]
    # Detect a table of contents: 2+ consecutive numbered headings near the top of the doc.
    toc = set()
    run = []
    for i, raw in enumerate(raw_lines[:25]):
        line = unescape(raw.rstrip())
        g = GROUP_RE.match(line)
        if g and len(norm_title(g.group(2))) <= 170:
            run.append(norm_title(g.group(2)).lower())
        else:
            if len(run) >= 2: toc.update(run)
            run = []
    if len(run) >= 2: toc.update(run)
    toc_consumed = set()

    intro = []
    groups = []
    cur_group = {'title': '', 'programs': [], 'intro': None}
    cur = None
    pending = None          # short text line waiting to become the label of the next link

    def flush_group():
        nonlocal cur_group
        if cur_group['programs'] or cur_group['title']:
            groups.append(cur_group)
        cur_group = {'title': '', 'programs': [], 'intro': None}

    def flush_pending(target):
        nonlocal pending
        if pending and target is not None:
            target['text'].append(pending)
        pending = None

    for raw in raw_lines:
        line = unescape(raw.rstrip())
        stripped = line.strip()
        if not stripped or NOISE_LINE.match(stripped):
            continue
        if TRAILER_RE.search(stripped) and not re.search(r'https?://(?!www\.free\.lesko|www\.leskohelp|leskohelp)', stripped):
            continue
        m = PROGRAM_RE.match(line)
        if m and len(norm_title(m.group(1))) > 3:
            flush_pending(cur)
            title, tlinks = extract_links(m.group(1))
            title, rest = split_title(title)
            cur = {'title': title, 'text': [rest] if rest else [], 'links': list(tlinks), 'implicit': False}
            cur_group['programs'].append(cur)
            continue
        g = GROUP_RE.match(line)
        if g and len(norm_title(g.group(2))) <= 170:
            gtitle, grest = split_title(g.group(2))
            key = gtitle.lower()
            if key in toc and key not in toc_consumed and cur is None and not groups and not cur_group['programs']:
                # This is the table-of-contents entry itself; the real heading comes later.
                toc_consumed.add(key)
                # If the same heading never re-appears it will be re-added as a group below.
                continue
            flush_pending(cur)
            flush_group(); cur_group['title'] = gtitle; cur = None
            if grest:
                cur = {'title': gtitle, 'text': [grest], 'links': [], 'implicit': True}
                cur_group['programs'].append(cur)
            continue
        h = HEADING_RE.match(line)
        if h: line = h.group(1)
        text, links = extract_links(line)
        text = re.sub(r'\s+', ' ', text).strip(' *')
        text = re.sub(r'^[-••]\s*', '', text).strip()
        if cur is None and cur_group['title'] and (text or links):
            # Content directly under a numbered heading -> implicit program named after the heading.
            cur = {'title': cur_group['title'], 'text': [], 'links': [], 'implicit': True}
            cur_group['programs'].append(cur)
        if cur is None:
            if links:
                for l in links:
                    if not l['label'] and pending: l['label'] = pending
                    elif not l['label'] and text and len(text) < 120 and not re.search(r'https?://', text): l['label'] = text
                pending = None
                intro.append({'text': text if len(text) >= 120 else '', 'links': links})
            elif text:
                if len(text) < 90: pending = text
                else:
                    pending = None; intro.append({'text': text, 'links': []})
            continue
        if links:
            for l in links:
                if l['label']: continue
                if text and len(text) < 120 and not re.search(r'https?://', text) and not VIDEO_LABEL.match(text):
                    l['label'] = text
                elif pending and len(pending) < 120:
                    l['label'] = pending
                elif text and VIDEO_LABEL.match(text):
                    l['label'] = text
            pending = None
            cur['links'].extend(links)
            if text and len(text) >= 120:
                cur['text'].append(text)
        elif text:
            if VIDEO_LABEL.match(text):
                pending = text
            elif len(text) < 90 and (text.endswith(':') or len(text) < 60):
                flush_pending(cur); pending = text
            else:
                flush_pending(cur); cur['text'].append(text)
    flush_pending(cur)
    flush_group()

    for g in groups:
        out = []; seen_prog = set()
        for p in g['programs']:
            links, seen = [], set()
            for l in p['links']:
                u = l['url']
                if u in seen:
                    for e in links:
                        if e['url'] == u and not e['label'] and l['label']: e['label'] = l['label']
                    continue
                seen.add(u)
                l['type'] = link_type(u); l['host'] = host(u)
                l['label'] = usable_label(norm_title(l['label'])) if l['label'] else ''
                if not l['label'] or l['label'].lower() in ('website', 'website:', 'here', 'click here', 'link'):
                    l['label'] = ('Watch video' if l['type'] == 'video' else l['host']) if not l['label'] else l['label'].rstrip(':') + ' (' + l['host'] + ')'
                links.append(l)
            p['links'] = links
            p['text'] = '\n'.join(x for x in (clean_text(t) for t in p['text']) if x).strip()
            sig = (p['title'].lower(), tuple(sorted(x['url'] for x in links)), p['text'][:80].lower())
            if sig in seen_prog: continue
            seen_prog.add(sig)
            if p['title'] and (links or p['text']):
                out.append(p)
        g['programs'] = out
        # A group whose only program is the implicit heading program is really just a program: drop the group title.
        if len(g['programs']) == 1 and g['programs'][0].get('implicit'):
            g['title'] = ''
        # Otherwise an implicit lead program repeats the heading: fold it into the group as its intro.
        elif g['programs'] and g['programs'][0].get('implicit') and g['programs'][0]['title'] == g['title']:
            lead = g['programs'].pop(0)
            g['intro'] = {'text': lead['text'], 'links': lead['links']}
        for p in g['programs']: p.pop('implicit', None)
    groups = [g for g in groups if g['programs']]
    # Merge consecutive untitled groups.
    merged = []
    for g in groups:
        if merged and not g['title'] and not merged[-1]['title'] and not g.get('intro'):
            merged[-1]['programs'].extend(g['programs'])
        else:
            merged.append(g)
    groups = merged
    intro_text = clean_text(' '.join(i['text'] for i in intro if i['text']))
    intro_links = []; seen = set()
    for i in intro:
        for l in i['links']:
            if l['url'] in seen: continue
            seen.add(l['url'])
            l['type'] = link_type(l['url']); l['host'] = host(l['url'])
            l['label'] = usable_label(norm_title(l['label'])) or ('Watch video' if l['type'] == 'video' else l['host'])
            intro_links.append(l)
    return {'intro': intro_text[:1200], 'introLinks': intro_links[:16], 'groups': groups}

def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def main():
    index = json.load(open(os.path.join(RAW, 'master-index.json')))
    states = []
    total_programs = 0; total_links = 0; missing = []
    for st in index:
        name = st['state']
        entry = {'name': name, 'abbr': ABBR.get(name, ''), 'slug': slug(name), 'categories': []}
        by_key = OrderedDict()
        for sec in st['sections']:
            key = category_key(sec['category'])
            fid = sec.get('fileId')
            doc = None; meta = {}
            if fid:
                p = os.path.join(RAW, 'docs', fid + '.md')
                mp = os.path.join(RAW, 'docs', fid + '.meta.json')
                if os.path.exists(p):
                    doc = open(p, encoding='utf-8').read()
                if os.path.exists(mp):
                    meta = json.load(open(mp))
                if doc is None:
                    missing.append((name, sec['category'], fid))
            cat = by_key.get(key)
            if cat is None:
                c = CAT_BY_KEY[key]
                cat = {'key': key, 'name': c[1], 'tagline': c[2], 'icon': c[3], 'blurb': sec.get('blurb', ''),
                       'sources': [], 'intro': '', 'introLinks': [], 'groups': []}
                by_key[key] = cat
            src = {'url': sec['url'], 'title': meta.get('title', ''), 'modified': meta.get('modifiedTime', '')[:10], 'label': sec['category']}
            cat['sources'].append(src)
            if doc is not None:
                parsed = parse_doc(doc, name)
                if not cat['intro']: cat['intro'] = parsed['intro']
                cat['introLinks'].extend(parsed['introLinks'])
                cat['groups'].extend(parsed['groups'])
            elif not fid:
                # external (non-Drive) link, e.g. NYC free financial counseling
                cat['groups'].append({'title': '', 'programs': [{'title': sec['category'], 'text': sec.get('blurb',''),
                    'links': [{'url': sec['url'], 'label': host(sec['url']), 'type': link_type(sec['url']), 'host': host(sec['url'])}]}]})
        for key, cat in by_key.items():
            # Some states link two overlapping versions of the same report (Puerto Rico's two
            # Jobs documents, the duplicated Delaware and Virginia blocks). Dedupe across the
            # whole category so a member doesn't scroll the same program twice.
            fingerprints = set()
            for g in cat['groups']:
                kept = []
                for p in g['programs']:
                    fp = (p['title'].lower(), tuple(sorted(l['url'] for l in p['links'])))
                    if fp in fingerprints:
                        continue
                    fingerprints.add(fp)
                    kept.append(p)
                g['programs'] = kept
            cat['groups'] = [g for g in cat['groups'] if g['programs'] or (g.get('intro') and g['intro']['links'])]
            n = sum(len(g['programs']) for g in cat['groups'])
            cat['programCount'] = n
            cat['linkCount'] = sum(len(p['links']) for g in cat['groups'] for p in g['programs'])
            total_programs += n; total_links += cat['linkCount']
            entry['categories'].append(cat)
        # keep canonical order
        order = [c[0] for c in CATEGORIES]
        entry['categories'].sort(key=lambda c: order.index(c['key']))
        entry['programCount'] = sum(c['programCount'] for c in entry['categories'])
        states.append(entry)
    states.sort(key=lambda s: s['name'])
    os.makedirs(os.path.join(OUT, 'states'), exist_ok=True)
    import datetime
    gen = datetime.date.today().isoformat()
    json.dump({'generated': gen, 'states': states}, open(os.path.join(OUT, 'states.json'), 'w'), ensure_ascii=False)
    for s in states:
        json.dump(s, open(os.path.join(OUT, 'states', s['slug'] + '.json'), 'w'), ensure_ascii=False)
    summary = {'states': [{'name': s['name'], 'abbr': s['abbr'], 'slug': s['slug'], 'programCount': s['programCount'],
                           'categories': [{'key': c['key'], 'programCount': c['programCount']} for c in s['categories']]} for s in states],
               'categories': [{'key': c[0], 'name': c[1], 'tagline': c[2], 'icon': c[3]} for c in CATEGORIES],
               'totals': {'states': len(states), 'programs': total_programs, 'links': total_links}, 'generated': gen}
    json.dump(summary, open(os.path.join(OUT, 'summary.json'), 'w'), ensure_ascii=False, indent=1)
    print(f"states={len(states)} programs={total_programs} links={total_links} missing_docs={len(missing)}")
    for m in missing: print('  MISSING', m)

if __name__ == '__main__':
    main()
