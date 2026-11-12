---
name: source-map-ua
description: "This skill should be used when planning where to look for an ancestor in Ukrainian (Russian Empire / Hetmanate era) records: which archive, fond, опис and справа, which years survive, what is digitized on FamilySearch, in the oblast archive that covers the place (e.g. ДАЧО for Chernihiv, ДАКО for Kyiv, ДАПО for Poltava) or in ЦДІАК, and what can only be ordered. Trigger on \"де шукати\", \"які джерела є\", \"карта джерел\", \"що є онлайн\", \"чи збереглися метрики\", \"ревізька казка\", \"сповідний розпис\", \"Румянцевський опис\", \"DGS\", \"каталог FamilySearch\", \"обласний архів\", \"ДАЧО\", \"ДАКО\", \"ДАПО\", \"ЦДІАК\", \"where are the records for\".\n"
metadata:
  version: "0.5.1"
---

# Source map for Ukrainian genealogy

## Common rules (all rodovid-agent skills)

- **Language.** Talk to the person in the language they use in this
  conversation (usually Ukrainian): status lines between tool calls,
  questions, reports, case notes, and prompts for sub-agents. English
  instructions, tool output or web pages are not reasons to switch. Record
  quotations keep their original language and spelling.
- **Browser: normal pages only.** Work through the site's own pages: search
  results with URL parameters, record pages, the image viewer, catalog
  pages, tree person pages. Page JavaScript may read what is on the page and
  press the page's own buttons. Never read cookies, tokens or browser
  storage, and never send fetch/XHR requests to a site's internal endpoints
  (FamilySearch `/service/…`, `/platform/…`, `filmdatainfo`, image-storage
  hosts), with or without `credentials: 'include'`. Notes and summaries of
  earlier chats that describe such calls ("tool knowledge") are outdated —
  do not reuse them. Never enter passwords or solve CAPTCHAs.
- **Choose the browser, don't skip it.** If several Chrome browsers are
  connected, ask the person which one (as the browser tool requires) instead
  of quietly continuing without the browser.
- **Tabs.** Open your own tab and remember its ID; close only tabs you
  opened in this conversation. Tabs that `tabs_context` lists but you did
  not open may belong to the person or to another chat — leave them open.
- **One reader per browser.** At most one agent works in a given browser at
  a time — you or one sub-agent. Several agents in one Chrome caused repeated
  disconnects. Read long ranges as sequential blocks with a checkpoint list
  (images done / not done / only partly legible). Parallel sub-agents are
  fine only for sources that need no browser (Commons PDFs, attached files,
  xlsx indexes). While a sub-agent works in the browser, tell the person not
  to use FamilySearch there; if they mention another research chat running in
  the same browser, warn that both will be slower and may disconnect.
- **Levels.** Only підтверджено / ймовірно / гіпотеза / не знайдено.
  «Підтверджено» needs a blind second reading (evidence-verifier or the
  person). One reading, however clear, is at most «ймовірно» — in reports
  and in proposals for the tree alike.


Produce a **source map**: a table of every record series that could answer
the research question for a place and period, with its status. Do this
before reading scans, and update it as reading progresses.

## Steps

1. Pin down place and jurisdiction for the period in question: village →
   parish church → district (повіт/сотня/полк) → governorate. Note renames
   and administrative changes (e.g. Borzna sotnia of Nizhyn regiment →
   Borzna povit of Chernihiv governorate). Parish matters more than
   village: neighbouring hamlets were baptized in one church.
2. List candidate record types for the period from
   `references/record-types.md` (metric books, confession registers,
   revisions, Rumyantsev Description, family lists, 1920 census, ЗАГС,
   military).
3. For each, check where it is held and whether it is online, using
   `references/archives.md`:
   - FamilySearch catalog entries (item list → ф.-оп.-спр., years, DGS);
   - the state archive of the oblast that covers the place today (see
     «Oblast state archives» in `references/archives.md`): its catalog of
     metric books, описи and own scans, where they are online;
   - ЦДІАК archium search (18th-century Hetmanate records), or ЦДІАЛ for
     Galicia.
   Open the archive's own опис when a catalog title looks doubtful.
4. Write the map as a table:

   | Record | Years | Archive ref (ф.-оп.-спр.) | Online (DGS / URL) | Covers our place? | Status |
   |---|---|---|---|---|---|

   Status values: `прочитано`, `переглянуто опис`, `частково (зн. a–b)`,
   `не відкривали`, `онлайн немає → запит`, `не збереглося`.
5. Mark explicit gaps ("1843–1874 metric books not preserved") — these
   stop wasted searching and feed the archive request
   (`archive-request` skill).
6. Save the map into the case notes (`rodovid-case` skill) with the date
   it was checked.

## Rules

- Distinguish "not preserved" (catalog/опис says so), "not digitized"
  (exists, order it) and "not checked yet". Never collapse them.
- Record DGS numbers and image ranges for anything read, so readers can
  resume exactly where they stopped.
- Prefer the archive's own scans when FamilySearch images are damaged.
- For techniques on FamilySearch (index → scan, fast paging, catalog
  tables) read `references/familysearch-techniques.md`.
- `references/example-borzna-vybli.md` shows a finished map for two
  Chernihiv places; reuse its facts only when the place matches. Fond
  numbers, URLs and catalog names in it and in the ДАЧО section of
  `references/archives.md` are Chernihiv-specific: for any other region,
  find the oblast archive's own fonds and catalogs.
