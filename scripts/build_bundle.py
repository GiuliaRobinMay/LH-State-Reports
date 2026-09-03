#!/usr/bin/env python3
"""Inline data/summary.json + data/states/*.json into app/index.html -> dist/index.html.

The result is one self-contained file (no fetches) that can be dropped into any host,
embedded in the community platform, or published as a Claude Artifact.
Artifacts wrap the page in their own <html>/<head>/<body>, so --artifact strips those tags.
"""
import json, os, sys, glob, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html = open(os.path.join(ROOT, 'app', 'index.html'), encoding='utf-8').read()
summary = json.load(open(os.path.join(ROOT, 'data', 'summary.json'), encoding='utf-8'))
states = {}
for p in glob.glob(os.path.join(ROOT, 'data', 'states', '*.json')):
    s = json.load(open(p, encoding='utf-8'))
    states[s['slug']] = s
payload = json.dumps({'summary': summary, 'states': states}, ensure_ascii=False, separators=(',', ':'))
payload = payload.replace('</', '<\\/')
out = html.replace('<script id="app-data" type="application/json"></script>',
                   '<script id="app-data" type="application/json">' + payload + '</script>')
os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
open(os.path.join(ROOT, 'dist', 'index.html'), 'w', encoding='utf-8').write(out)
if '--artifact' in sys.argv:
    body = out
    body = re.sub(r'^<!doctype html>\s*<html[^>]*>\s*<head>\s*<meta charset="utf-8">\s*<meta name="viewport"[^>]*>\s*', '', body, flags=re.I)
    body = re.sub(r'</head>\s*<body>', '', body, count=1)
    body = re.sub(r'</body>\s*</html>\s*$', '', body)
    open(os.path.join(ROOT, 'dist', 'artifact.html'), 'w', encoding='utf-8').write(body)
print('dist/index.html', round(len(out.encode('utf-8'))/1e6, 2), 'MB;', len(states), 'states inlined')
