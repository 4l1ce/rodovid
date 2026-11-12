---
name: familysearch-tree-sync
description: "This skill should be used when adding or changing people, relationships or sources in the person's FamilySearch family tree based on research findings. Trigger on \"додай у дерево\", \"внеси в FamilySearch\", \"прикріпи джерело\", \"додай дітей / братів / дружину\", \"перевір дублікати в дереві\", \"update my tree\", \"attach this record\", \"перевір джерела\", \"дивне джерело\", \"прикріпи реальні сторінки\".\n"
metadata:
  version: "0.5.1"
---

# Updating the FamilySearch tree

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


The tree is shared and public-facing; an error there spreads to other
researchers. Treat every change as a release that needs approval.

## Before touching the tree

1. Prepare a change list: each person / relationship / source to add or
   edit, with the ledger ID and level from `evidence-ledger`. Relationships
   at `підтверджено` (verified by a second reader) go in as facts; at
   `ймовірно` or `гіпотеза` only with the level written in the reason text;
   index-only claims are marked "лише індекс".
2. Show the list to the person and wait for an explicit "так"/"yes".
   Approval covers only the listed changes.
3. Search the tree for existing people (name variants, spouse, place,
   dates) to avoid duplicates. FamilySearch "possible matches" often
   suggest unrelated people from other regions — compare before merging,
   and never merge without approval.

## Rules for every change

- **No person without a source.** Attach the record (index link or scan)
  and write a reason: what the record says, and why it is this person.
- **The source link must open the record itself.** For an unindexed page,
  the link is the `…/ark:/61903/3:1:…` of that exact image («Снимок N»),
  taken from the address bar while the image is open — never the film's
  first image or title card, a catalog page, or a link to the whole film.
  Put archive ref, DGS, image number with side (Л/П), entry number and the
  verbatim transcription in the citation.
- **When the index got the roles wrong, attach the image, not the index
  record.** Example: the 1740 marriage indexed with the father Павел as the
  groom instead of his son Михаил. Attaching that index record would make
  FamilySearch link Павел to the bride. Attach the image as a source instead,
  and say in the reason what the index got wrong.
- **One source per record.** Several records (e.g. three baptisms where the
  person is godparent) are separate sources, each with its own image link;
  do not merge them into one source that links to one page.
- Names as written in the source (Russian church spelling, e.g.
  "Николай Прокофьев Шульга"), unless the person prefers otherwise.
- Hypotheses are added only with an explicit note "Гіпотеза: …" in the
  relationship reason, citing the evidence and what would confirm it.
- Dates from ages are "бл. 1836" (about), not exact.
- Living people: do not add.

## Mechanics (browser, logged in as the person)

Load the browser skill first (Claude in Chrome or built-in browser).
Useful paths (details in `source-map-ua/references/familysearch-techniques.md`):
- attach a record: `/search/linker?ark=/ark:/61903/1:1:<RECORD-ID>&id=<PERSON-ID>`
- set the "Русский" name template before typing Cyrillic names;
- when creating a relative from the attach screen, confirm the
  relationship panel shows the expected parent IDs before saving;
- source dates: type the date, then pick the normalised value from the
  dropdown that appears — otherwise FamilySearch may save the field empty;
- read the tree (family members, sources, relationships) from the person,
  family and sources pages with page-text reads, never through the site's
  internal tree endpoints.

## After the change

1. Re-open each new or changed source from the person's Sources page and
   click its link: it must show the record (right image, right entry).
   Check that dates and the reason text were saved.
2. Report person IDs created or changed, sources attached, and update the
   ledger's "У дереві" column. If something failed midway, list exactly
   what was saved and what was not.

## Auditing existing sources

When asked to check a person's sources ("перевір джерела", "дивне
джерело", "прикріпи реальні сторінки"):
1. List every source on the person's Sources page: title, link, citation,
   reason.
2. Open each link and classify it: points to the record ✔ / to the film's
   first image or a title card ✘ / to a catalog or the whole film ✘ / an
   index record whose roles are wrong ✘ / dead link ✘.
3. For each ✘ find the right image (citation numbers, the index, or by
   reading the film) and prepare a change list: what to detach, what to
   attach, with levels.
4. Change nothing until the person approves the list.
