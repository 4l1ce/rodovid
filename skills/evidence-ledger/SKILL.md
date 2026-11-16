---
name: evidence-ledger
description: "This skill should be used whenever a genealogical finding is recorded, graded or reviewed: deciding whether a parent–child link is confirmed, probable or a hypothesis, keeping a colour-coded evidence table, or checking what a family-tree claim rests on. Trigger on \"наскільки це певно\", \"це доведено?\", \"рівень достовірності\", \"запиши знахідку\", \"таблиця доказів\", \"реєстр доказів\", \"на чому це тримається\", \"evidence\", \"confidence level\", \"is this proven\".\n"
metadata:
  version: "0.6.0"
---

# Evidence ledger

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


Every claim about a person ("X is the son of Y", "born ~1821", "died
before 1920") is one row with its source, who read it, who checked it, and
a confidence level. The ledger is what lets a human audit the agent's work.
Every research report ships with a ledger file — a markdown table alone is
not enough.

## The four levels — no others

| Level | Colour | Use when |
|---|---|---|
| `confirmed` · підтверджено | green E2EFDA | Read on the original scan **and** independently re-read by someone other than the first reader (evidence-verifier agent or the person) |
| `probable` · ймовірно | yellow FFF2CC | Scan read by one reader; or a key word is uncertain (?); or identity rests on several independent indirect matches; or **index only** (ceiling for index-only claims) |
| `hypothesis` · гіпотеза | orange FCE4D6 | Inference by elimination or from a single match; **records that contradict each other** (state both in the reasoning) |
| `not_found` · не знайдено | red F4CCCC | Searched and not found — state where, and whether that source is complete |

Do not invent other labels ("доведено", "невідомо", "суперечить",
"не підтверджено"). "доведено" is read as `confirmed` and must pass the
same gate; contradictions are `hypothesis` with both readings in the
reasoning; an unknown with no record is `not_found` with the list of places
searched.

A claim read on a scan by one agent stays `probable` until the verifier
re-reads it blind. If the verifier cannot run in this session, say so in
the report and leave the claim at `probable` — never upgrade on a single
reading, however clear the scan looks.

## Using the script

`scripts/ledger.py` next to this file (locate with
`find / -name ledger.py -path "*evidence-ledger*" 2>/dev/null | head -1`):

```
python3 ledger.py init  <case>-докази.xlsx
python3 ledger.py add   <file> --from claims.json        # list of claims
python3 ledger.py set   <file> --id E007 --level confirmed --checked-by "evidence-verifier"
python3 ledger.py summary <file>                           # what still waits for the verifier
python3 ledger.py export-md <file>                         # table for the case note
```

Claim fields: person, claim, event, date, place, source (archive +
ф.-оп.-спр. + book), image, link, transcript (verbatim), level,
reasoning, read_by, checked_by, tree.

The script enforces the gate and refuses the whole batch when any claim
breaks it:
- `confirmed` needs a scan (image, or a FamilySearch `3:1:` link — a `1:1:`
  index link is not a scan), `read_by`, and `checked_by` different from
  `read_by`;
- unknown level names are rejected;
- every non-confirmed claim needs a source.

`summary` lists claims waiting for the verifier, hypotheses already in the
tree, and probable claims with no link. Put the `export-md` table into the
case note and attach or save the xlsx next to it.

## Writing reasoning

State the chain, not the conclusion: "Діомид Прокофьев Шульга —
поручитель на шлюбі Тихона 1888 (скан, зн. 293) і на шлюбі Анни
Николаевни 1895 → Діомид, ймовірно, дядько обох → батько Тихона —
Николай Прокофьевич (єдиний вибельський Николай потрібного віку)". Name
what would confirm or refute it (a family list, a confession register).
