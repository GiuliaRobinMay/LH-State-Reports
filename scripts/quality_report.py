#!/usr/bin/env python3
"""Write data/QUALITY.md: what the harvest could not get, and known defects in the source docs."""
import json, os, re, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW, OUT = os.path.join(ROOT, 'raw'), os.path.join(ROOT, 'data')
index = json.load(open(os.path.join(RAW, 'master-index.json')))
summary = json.load(open(os.path.join(OUT, 'summary.json')))

missing, empty, tiny = [], [], []
for st in index:
    for sec in st['sections']:
        fid = sec.get('fileId')
        if not fid:
            continue
        md = os.path.join(RAW, 'docs', fid + '.md')
        if not os.path.exists(md):
            missing.append((st['state'], sec['category'], sec['url']))
        elif os.path.getsize(md) < 400:
            tiny.append((st['state'], sec['category'], sec['url'], os.path.getsize(md)))
for s in summary['states']:
    for c in s['categories']:
        if c['programCount'] == 0:
            empty.append((s['name'], c['key']))

lines = ["# Source data quality", "",
         f"Harvested from {len(index)} states/territories and "
         f"{sum(1 for st in index for x in st['sections'] if x.get('fileId'))} linked documents in the master Google Doc.",
         f"Parsed into **{summary['totals']['programs']:,} programs** and **{summary['totals']['links']:,} links**.", "",
         "Everything below is a defect in the original Drive folder, not in the extraction. "
         "The app still shows the original Google Doc link for every report, so nothing is lost to the reader.", ""]

lines += ["## Documents that could not be fetched", ""]
if missing:
    lines += ["The linked file returns *\"Requested entity was not found\"* — it has been deleted, "
              "or it is not shared with the account that ran the harvest. These categories appear in the app "
              "with the original link and no programs.", "",
              "| State | Report | Link |", "|---|---|---|"]
    lines += [f"| {s} | {c} | [source]({u}) |" for s, c, u in missing]
else:
    lines.append("None — every linked document was fetched.")
lines.append("")

if tiny:
    lines += ["## Documents that are effectively empty", "",
              "The document exists and was fetched, but the source itself has almost no content.", "",
              "| State | Report | Characters | Link |", "|---|---|---|---|"]
    lines += [f"| {s} | {c} | {n} | [source]({u}) |" for s, c, u, n in tiny]
    lines.append("")

lines += ["## Known defects inside the source documents", "",
          "Found while parsing. All content is preserved verbatim in `raw/docs/`; none of these were \"fixed\", "
          "because guessing at the author's intent would be worse than showing what he wrote.", "",
          "- **Copy-paste headings from the wrong state.** Michigan and New Jersey housing reports carry the heading "
          "*\"HUD Identified Programs for Homeownership In Alaska\"*, though the link underneath is correct for the state. "
          "California's dental section is headed *\"Free and Low-Cost Dental Clinics in New Jersey\"*. Arizona's financial "
          "report links `211connectsalabama.org` beside the correct `211arizona.org`. North Carolina's jobs report opens "
          "with the heading *\"Arizona\"*. Several \"Biz Done\" reports (Tennessee, Utah, Virginia, Wyoming) open with "
          "*\"Why does Indiana want to help you…\"*.",
          "- **One misassigned link.** The master document's North Carolina *Financial Assistance* link points at a Google "
          "Doc titled \"Book notes\" — a short personal outline, not a Lesko report.",
          "- **Editing debris.** A few documents contain stray characters left over from editing (a run of backslashes in "
          "Oregon, `Aa as à AA qàáà see em` in Virginia, empty \"Tab 2/3/4\" sections in several). The parser drops "
          "single-character and separator-only lines, so most of this never reaches the app.",
          "- **Duplicated sections.** Delaware and Virginia are listed twice in the master document with two different sets "
          "of six links; both sets are merged into one entry per state. Puerto Rico is listed with two *Jobs, Education, "
          "Training* links and no *Financial Assistance* or *Health* report.",
          "- **Dead external links.** Many programs point at pages that have moved since the reports were written "
          "(`youcaring.com` shut down, several `hud.gov` and `portal.hud.gov` paths now redirect). Link-checking is a "
          "separate pass and has not been run.", ""]

if empty:
    lines += ["## Categories with no programs in the app", "",
              "These are the consequence of the two lists above.", "",
              ", ".join(f"{s} ({c})" for s, c in empty), ""]

open(os.path.join(OUT, 'QUALITY.md'), 'w').write('\n'.join(lines))
print('wrote data/QUALITY.md —', len(missing), 'missing,', len(tiny), 'empty,', len(empty), 'categories with no programs')
