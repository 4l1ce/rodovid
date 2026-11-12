---
name: rodovid-case
description: "This skill should be used for any multi-step family-history research in Ukrainian / Russian-Empire records: tracing an ancestor, a surname line or a village, answering \"who was the father of …\", or continuing a research case from earlier notes. It orchestrates the source map, index search, scan reading, verification, evidence ledger, case notes, tree updates and archive requests. Trigger on \"досліди рід\", \"досліди гілку\", \"знайди батька\", \"хто батьки\", \"продовжимо дослідження\", \"родовід\", \"генеалогія\", \"шукаю предків\", \"простеж лінію\", \"research my ancestor\", \"trace the family\".\n"
metadata:
  version: "0.5.1"
---

# Running a genealogy research case

Work like a careful archivist with a QA mindset: every claim traceable to
an image, every gap explained, every reading that matters checked by a
second reader, every change to the tree approved.

A case is **not done** until the checklist at the end passes. If a step
cannot be done in this session, the report says which one and why, and the
affected claims stay at a lower level.

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

## 0. Load the case
- Read existing case notes (project docs, memory, attached files) and
  list what is already established, what was rejected, and decisions the
  person made (e.g. "закрито: не шукати жіночі лінії"). Do not re-open
  closed questions unless asked.
- Restate the research question in one line: who, what link, which
  place and period. If two readings are possible, ask once.
- Create the task list with these stages: source map → search → read →
  **verify** → ledger → note.

## 1. Plan with a source map
Use the `source-map-ua` skill: list record series that could answer the
question, their years, archive refs, DGS numbers and status. Pick the
cheapest decisive source first (indexed > unindexed but small >
large unindexed > archive request).

## 2. Search indexes — into files, not into the conversation
- Transcribed xlsx indexes: use `metric-index-search` (`search_index.py`,
  `families.py`, and `coverage.py` before any "not found").
- Online indexes (FamilySearch search results): when a family or surname
  has **10 or more** index records, or you are reconstructing sibships, save
  the hits as rows with `scan-transcribe/scripts/index_writer.py` (schema in
  `scan-transcribe/references/schema.md`; `Файл` = the scan link `…/3:1:…`,
  or `індекс: <…/1:1:… link>` when only the index was seen) and run
  `families.py` on them — it catches the anomalies a manual reading misses
  (one mother under two fathers' names, a father too young for a child).
  Fewer records can stay in the case note's table.

## 3. Read scans — cheapest step that can answer first
Reading images is the expensive part of a case. Go down this ladder and
stop at the first step that answers the question (details in
`scan-transcribe`, «Reading economy»):

1. **Titles before images.** Identify a case from the archive опис,
   catalog titles and finding aids (`source-scout`, typed text). Do not
   open a film just to learn which regiment or parish it is.
2. **Map before reading.** In a large unindexed case, find the section
   first: cover pages, the summary table of sotnias or parishes, and the
   order of sections in the same series for a neighbouring year. Read
   headings only.
3. **Names before details.** On the pages that matter, the first pass
   takes name and surname per line (plus estate or «вдова»). No numeric
   columns, no household detail.
4. **Second reading of target lines only**, not of the whole page.
5. **Disagreements to the person at once**, before starting further
   reading that depends on them.
6. **Full transcription only of the households found.**
7. **Continuous reading of running text** (deeds, court records, whole
   villages «на всяк випадок») is the last resort and needs approval.

**Say the size before spending it.** Before any run of more than 30 images
(one agent or several), tell the person: how many images, which step of the
ladder, what it can answer, and what the cheaper alternative is; then wait
for a yes. A «так, починай» for a plan covers the steps named in it, not
follow-up ranges the agents discover later. When a run ends without an
answer, report it and propose the next step; do not chain a new range
automatically.

Use `scan-transcribe`. Open the scan for every record a conclusion rests
on. Long ranges are read as **sequential blocks** by one reader at a time
(you, or one `scan-reader` agent in the background) — never several agents
in the same browser. Keep a checkpoint list: images done, not done, and
only partly legible (those go to «Що лишилося» for a re-read). Copy the DGS,
image number and entry number from the viewer at the moment of reading —
never from memory or an older note; earlier notes have contained wrong image
numbers.

## 4. Verify — mandatory
For every claim the answer depends on, and every claim proposed for the
tree, run the `evidence-verifier` agent (if the named agent is not
available, start a general-purpose agent with the instructions from the
plugin's `agents/evidence-verifier.md`). Give it only: the **scan** link
(`…/ark:/61903/3:1:…`) or the film-viewer link
(`/search/film/<DGS>?i=<n-1>`), the entry number, and which fields to read.
Never give it a `1:1:` index link — the index page shows a reading, so the
check stops being blind — and never the earlier reading or the expected
answer. Ask it also to confirm that DGS, image and entry number match.
Give it the target lines only (the entries the claim rests on, plus «are
there other surnames beginning with the same letter on this page»), not
the whole page or range. Run it in the background when the person is waiting, and say roughly how
long it takes (about 2–3 minutes per scan).
- Agreement → the ledger can record `confirmed` with
  `checked_by: evidence-verifier`.
- Disagreement → keep `probable` or `hypothesis`, show both readings to the
  person.
- Verifier saw the index or the earlier reading → its check is not blind;
  the claim stays `probable`.
- Verifier could not run (no browser, agent tool unavailable, the person
  stopped it) → say so in the report; those claims stay `probable` at most.

## 5. Reason and grade
Apply `references/reasoning-patterns.md`. Record each claim in the ledger
with `evidence-ledger` (`ledger.py`, an xlsx file). Use only the four
levels: підтверджено / ймовірно / гіпотеза / не знайдено. Contradictory
records are `гіпотеза` with both readings; index-only claims are at most
`ймовірно`.

## 6. Report and save
- Answer the question first, with the level, then the evidence table
  (`ledger.py export-md`), what was verified and by whom, rejected
  candidates, anomalies, and what is left (online vs. archive).
- Save a case note in the format of `references/case-notes-format.md` to
  the person's project (or as a file), plus the ledger xlsx. Write a
  project document once per finished step, not after every agent report:
  each rewrite re-sends the whole document. Interim progress goes into the
  conversation and the agents' note files.
- If some decisive readings were not verified, the **first** next step you
  offer is the verification itself, with the number of records ("Запустити
  сліпу перевірку 4 записів?") — before any new search.
- Offer, do not perform: tree changes (`familysearch-tree-sync`, needs
  approval and only for verified or clearly labelled claims) and archive
  requests (`archive-request`).

## Guardrails
- No speculation presented as fact; hypotheses are labelled.
- Living people are not researched or published without the person's
  explicit wish; do not put them in shared trees.
- Do not reproduce copyrighted publications; cite and summarise.

## Definition of done (check before the final message)
- [ ] Every claim in the answer has a ledger row with one of the four levels.
- [ ] Every `підтверджено` was re-read by the verifier (or the person);
      nothing was upgraded on a single reading.
- [ ] Families reconstructed from 10+ index records went through
      `families.py`.
- [ ] Every scan citation (DGS, image, entry) was copied from the viewer in
      this session or checked by the verifier.
- [ ] Only your own browser tabs were closed; no two agents shared the
      browser.
- [ ] "Not found" statements name where it was searched and whether that
      source is complete (coverage).
- [ ] Case note and ledger xlsx saved; tree untouched unless approved.
- [ ] Steps that could not be done are listed in the report.
