---
name: scan-transcribe
description: "This skill should be used when reading or transcribing scans of Ukrainian and Russian-Empire church records and censuses — metric books (метричні книги), confession registers (сповідні розписи), revision lists (ревізькі казки), the Rumyantsev Description — from photos, PDFs, FamilySearch, ДАЧО or ЦДІАК images, and when building an index workbook from them. Trigger on \"прочитай скан\", \"розшифруй запис\", \"транскрибуй\", \"що написано на зображенні\", \"перепиши двір\", \"зроби індекс метрик\", \"прочитай сторінки 120–140\", or when scan images are attached.\n"
metadata:
  version: "0.5.0"
---

# Transcribing record scans

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


Read `references/reading-guide.md` before the first scan of a session,
and `references/schema.md` when writing an index workbook.

## Which model reads

Handwriting accuracy differs sharply between models (test and table:
`references/model-choice.md`). Apply this to every reading of a
handwritten scan, by you or by a sub-agent:

- **First reading: Fable.** Start `scan-reader` with `model: "fable"`. If
  this conversation runs on another model, say so to the person before
  reading and still start the readers on Fable.
- **Blind second reading: Opus.** For every entry a conclusion depends on,
  and for whole pages when the person asks for a full transcription, start
  a second reader with `model: "opus"` on the same images, without the
  first reading. A second reading by the same model as the first does not
  count as independent.
- **Never Sonnet or Haiku for handwriting.**
- **Text that is already typed needs no strong reader.** Searching and
  summarising xlsx indexes, online index records (FamilySearch `1:1:`),
  printed books and catalog pages can run on Sonnet (`model: "sonnet"` for
  the sub-agent); the index scripts need no model at all. Haiku only for
  mechanical filtering of rows. Conclusions drawn from index rows
  (who is whose father, which of two namesakes) stay with the main
  conversation's model.
- **Compare field by field** (names, patronymics, surnames, ages, sums,
  land and hay figures). Where the two readings agree, record the reading
  as usual. Where they differ, do not pick one silently and do not go by
  the models' own confidence: show the person a short table «Розбіжності»
  — field, Fable, Opus, zoomed crop or image reference — and mark the
  field `(?)` until the person or a zoomed re-reading settles it.
- **Say which model read.** Start every transcription report with two
  lines: «Перше читання: <модель>» and «Друге читання: <модель>» or
  «Друге читання: не робилось». Take the model from what you passed when
  starting the reader, not from the reader's own words. If both lines name
  the same model, add «не незалежне». When no second reading was done for
  an entry a conclusion depends on, offer it as the next step.
- **The main conversation is not switched.** Only sub-agents get another
  model. When you read a handwritten scan yourself and this conversation
  is not on Fable, tell the person once and hand the reading to a
  `scan-reader` started on Fable.
- A field both models read the same way is still one line of evidence from
  one source: the level rules above are unchanged.

## Reading a scan

1. Identify the document first: archive reference, book, year, church,
   page/image number, which part (births / marriages / deaths /
   household list). Write it at the top of the output.
2. Read the whole row across both pages of the spread. Transcribe in the
   original language and word order; do not translate names.
3. Mark every uncertain word with `(?)` and illegible parts with
   `[неразборчиво]`. When a reading is chosen because of context (a
   guarantor with the same surname, a monthly total), say so in the note.
4. Zoom until letters are distinct before deciding any name, patronymic
   or number that a conclusion will rest on. If the image is too poor,
   say so and name a better copy (ДАЧО own scans, another filming).
5. Check against the monthly totals ("Итого в … месяце") and the
   numbering; report missing or duplicated numbers.
6. For a person-search task, return only the relevant records in full
   plus a line per neighbouring record that could be family (same
   surname, same godparents).

## Building or extending an index workbook

Use `scripts/index_writer.py` (next to this file; locate it with
`find / -name index_writer.py 2>/dev/null | head -1`):

```
python3 index_writer.py init "<Повіт> <рік> рік метрики.xlsx"
python3 index_writer.py add  "<file>" --sheet birth    --from rows.json
python3 index_writer.py add  "<file>" --sheet marriage --from rows.json
python3 index_writer.py add  "<file>" --sheet death    --from rows.json
```

Rows are JSON objects with the schema's column names; the writer rejects
unknown columns and rows without `Файл`, and highlights cells with (?).
After each book, run the QA check from the `metric-index-search` skill
(`check_transcription.py`) and fix numbering, date and sex/counter
issues by re-reading the scans, not by editing data to fit.

The same writer is used for rows copied from an online index (FamilySearch
search results): `Файл` = scan link `3:1:` if the scan was opened, else the
index link `1:1:` or `індекс: <collection>`. When a scan is later opened,
update the row's `Файл` and fix the transcription from the scan.

## Reading economy

Lessons from a real case (Borzna, revisions of 1737–1738, 10 Nov 2026),
where most of the cost went into reading that could not change the answer.

- **Find the section by structure, not by sweep.** Large composite cases
  (regiment revisions, oath books, Rumyantsev volumes) have cover pages per
  sotnia, a summary table («табель») listing the sotnias in order, and the
  same order of sections from year to year. Check the neighbouring year's
  map first: in the Nizhyn regiment revisions Borzna follows Konotop in
  both 1737 and 1738. Then probe: every 10th image reading only the heading,
  and bisect between the two probes that bracket the target. Do not read
  ranges «суцільно» to find a section — in the Borzna case about 160 images
  were read that way in the wrong parts of the film.
- **A mapping reader reads headings only.** Its report is a table
  image → heading. It does not transcribe entries, and it does not get a
  «part 2, if resources remain».
- **Surname pass.** When the question is whether a surname occurs, the
  reader lists name and surname per line with the image and line number.
  Numeric columns, ages and remarks are read only for lines with a target
  surname. A full line-by-line transcription of a list is done only when
  the person asks for the whole list.
- **Targeted second reading.** The blind second reader gets the image and
  the line numbers (or «all surnames beginning with Т, Б, С on this
  page»), not «transcribe the page again».
- **One block, one agent.** 10–20 images per agent for entry reading, up
  to 50 for heading-only mapping. Every zoomed image stays in the agent's
  context and makes each later step dearer, so a fresh agent per block with
  a notes file is cheaper than one long agent. One task per agent.
- **Running text last.** Deeds, wills and court extracts cost the most per
  image and rarely name a father. Look for the case's own register of
  documents first; read continuously only with the person's approval.
- **The 30-image rule** from `rodovid-case` step 3 applies to every run
  started from this skill as well.

## Long ranges

Read long ranges (dozens to hundreds of images) as **sequential blocks** of
10–20 images (up to 50 for heading-only mapping), one reader at a time in the browser: you, or one `scan-reader`
agent in the background (or a general-purpose agent with the instructions
from the plugin's `agents/scan-reader.md`). Do not run several readers in the
same Chrome — in practice that caused disconnects and lost tabs. After each
block, record the checkpoint: images read, records found, images only
partly legible. A dropped connection then costs one block, not the whole
range. Readers may run in parallel only on sources that need no browser
(attached files, Commons PDFs, saved tiles). Send every finding a conclusion depends on
to the `evidence-verifier` for an independent second reading.

## Getting enough resolution

- FamilySearch viewer: close the index panel at the bottom, use the
  viewer's own zoom (double-click or «+») until the line fills the screen,
  then screenshot/zoom that region. Small 18th-century hands need two zoom
  steps.
- ЦДІАК archium: open the page image itself in its own tab (the image file
  behind the viewer) instead of reading the scaled viewer, then zoom
  regions.
- To let several readers work on one page without the browser, save the
  page as overlapping full-resolution tiles once (show the image at its
  natural size, shift it by about 600 px per step, save each screenshot),
  then give all readers the same tile files. Readers of saved tiles may run
  in parallel; the one-reader-per-browser rule applies only to capturing.
- If letters still merge, mark the page «частково читається» in the
  checkpoint list and the case note, and do not draw conclusions from it;
  the verifier or the person can re-read it later.

## Copying citations

Take DGS, image number («Снимок N»), page side (Л/П) and entry number from
the viewer while the image is open, and the scan link from the address bar
(`…/ark:/61903/3:1:…`). Do not reuse numbers from older notes without
opening the image — older notes have contained wrong image numbers.
