# LeskoHelp State Reports

A digital, searchable version of Matthew Lesko's **50-state "Money & Help" reports** for the LeskoHelp.com community.

The original material is one master Google Doc that links to six sub-reports per state (about 310 Word/Google documents in total). This repo harvests those documents, parses them into structured data, and ships a small app where a member picks their state and browses every program by category, or searches across all 52 states and territories.

## What is in here

| Path | What it is |
|---|---|
| `raw/master-index.json` | The master doc, parsed: every state, its six report headings, blurbs and source links |
| `raw/docs/<fileId>.md` | Verbatim text of each linked sub-document, plus a `.meta.json` with the Drive title and last-modified date |
| `scripts/parse_reports.py` | Turns the raw text into structured JSON (state → category → group → program → links) |
| `data/summary.json` | Counts per state and category, used for the home screen |
| `data/states/<state>.json` | One file per state with every program, description and link |
| `data/states.json` | Everything in one file |
| `app/index.html` | The app. Loads the JSON files next to it, no build step, no framework |
| `scripts/build_bundle.py` | Inlines all data into `dist/index.html`, a single self-contained file for hosting or embedding |

## Categories

Each state has the same six reports, which become the six tabs in the app:

1. Financial Assistance (bills, debt, rent, utilities, emergency money)
2. Business (start or grow a business, nonprofit or invention)
3. Jobs, Education & Training
4. Health, Dental & Pet Care
5. Free Local Mentoring & Research Help
6. Real Estate & Housing

## Running it

```bash
# serve the repo root, then open /app/
python3 -m http.server 8000
# or build the single-file version
python3 scripts/parse_reports.py      # raw/ -> data/
python3 scripts/build_bundle.py       # data/ + app/ -> dist/index.html
```

`dist/index.html` works from a plain `file://` open, an `<iframe>` in the community platform, or any static host.

## Refreshing the data

Re-harvest the Google Docs into `raw/docs/` (the file IDs are in `raw/master-index.json`), then run the two scripts above. The parser is deliberately tolerant of the formatting differences between documents, and any document that fails to parse still shows its original Google Doc link in the app.

## Known gaps in the source material

See `data/QUALITY.md` for documents that were missing, empty, or mislabelled in the original Drive folder.
