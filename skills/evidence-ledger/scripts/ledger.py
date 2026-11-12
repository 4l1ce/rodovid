#!/usr/bin/env python3
"""Evidence ledger: one row per claim, colour-coded by confidence.

  ledger.py init    ledger.xlsx
  ledger.py add     ledger.xlsx --from claims.json      # list of claim objects
  ledger.py add     ledger.xlsx --json '{"person": "...", "claim": "...", ...}'
  ledger.py set     ledger.xlsx --id E012 --level confirmed --checked-by "evidence-verifier"
  ledger.py summary ledger.xlsx
  ledger.py export-md ledger.xlsx > table.md              # for the case note

Claim keys (Ukrainian or English accepted):
  person / особа, claim / твердження, event / подія, date / дата, place / місце,
  source / джерело (archive, fond-opys-sprava, book), image / зображення,
  link / посилання, transcript / транскрипція (verbatim, original spelling),
  level / рівень, reasoning / обґрунтування,
  read_by / прочитав (who read the scan), checked_by / перевірив (independent
  second reader: evidence-verifier agent or the person), tree / дерево

Only four levels exist: confirmed, probable, hypothesis, not_found
(підтверджено, ймовірно, гіпотеза, не знайдено). "доведено" is accepted as
an alias of confirmed and goes through the same gate.

Gate for `confirmed`:
  * a scan image or a scan link (an index-only FamilySearch link ark:/61903/1:1:
    is not a scan);
  * read_by is filled in;
  * checked_by is filled in and differs from read_by — the person who read the
    scan cannot be the one who confirms it.
If the gate fails, the claim is refused with the reason; record it as
`probable` and run the verifier.

Colours: confirmed E2EFDA, probable FFF2CC, hypothesis FCE4D6, not_found F4CCCC.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from collections import Counter

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

COLUMNS = [
    ("id", "ID", 7), ("person", "Особа", 26), ("claim", "Твердження", 44),
    ("event", "Подія", 12), ("date", "Дата", 12), ("place", "Місце / парафія", 20),
    ("source", "Джерело (архів, ф.-оп.-спр., книга)", 30), ("image", "Зображення / арк.", 14),
    ("link", "Посилання на скан", 30), ("transcript", "Транскрипція (дослівно)", 48),
    ("level", "Рівень", 14), ("reasoning", "Обґрунтування", 44),
    ("read_by", "Прочитав", 16), ("checked_by", "Перевірив (незалежно)", 18),
    ("checked_on", "Дата", 12), ("tree", "У дереві", 14),
]
KEYS = [c[0] for c in COLUMNS]
COL = {k: i + 1 for i, k in enumerate(KEYS)}
UA_KEYS = {"особа": "person", "твердження": "claim", "подія": "event", "дата": "date",
           "місце": "place", "джерело": "source", "зображення": "image", "посилання": "link",
           "транскрипція": "transcript", "рівень": "level", "обґрунтування": "reasoning",
           "прочитав": "read_by", "перевірив": "checked_by", "дерево": "tree"}
LEVELS = {"confirmed": ("підтверджено", "E2EFDA"), "probable": ("ймовірно", "FFF2CC"),
          "hypothesis": ("гіпотеза", "FCE4D6"), "not_found": ("не знайдено", "F4CCCC")}
ALIASES = {"підтверджено": "confirmed", "доведено": "confirmed", "proven": "confirmed",
           "ймовірно": "probable", "likely": "probable",
           "гіпотеза": "hypothesis", "не знайдено": "not_found", "not found": "not_found"}
LABEL_TO_LEVEL = {v[0]: k for k, v in LEVELS.items()}
SHEET = "Докази"
# a check that saw the index or the earlier reading cannot confirm
NOT_BLIND = __import__("re").compile(
    r"не\s*сліп|не\s*слеп|not\s*blind|бачив\s*індекс|бачила\s*індекс|saw\s*the\s*index|"
    r"знав\s*попереднє|знала\s*попереднє", __import__("re").I)


class GateError(SystemExit):
    pass


def canon_level(raw) -> str:
    lvl = str(raw or "").strip().lower()
    lvl = ALIASES.get(lvl, lvl)
    if lvl not in LEVELS:
        raise GateError(
            f"Рівень «{raw}» не існує. Дозволено лише: підтверджено / ймовірно / гіпотеза / "
            "не знайдено (confirmed / probable / hypothesis / not_found). "
            "Для суперечливих записів — «гіпотеза» з поясненням у обґрунтуванні.")
    return lvl


def gate(c: dict):
    """Raise if a claim may not carry its level."""
    lvl = c["level"]
    has_scan = bool(c.get("image")) or ("/3:1:" in str(c.get("link", "")))
    link = str(c.get("link", ""))
    if lvl == "confirmed":
        if not has_scan:
            why = " (посилання веде на індекс 1:1:, а не на скан)" if "/1:1:" in link else ""
            raise GateError(f"«підтверджено» без скану неможливе{why}: {c.get('claim')}")
        if not c.get("read_by"):
            raise GateError(f"«підтверджено» без поля «прочитав»: {c.get('claim')}")
        if not c.get("checked_by"):
            raise GateError(f"«підтверджено» без незалежної перевірки — запишіть «ймовірно» "
                            f"і запустіть evidence-verifier: {c.get('claim')}")
        if str(c["checked_by"]).strip().lower() == str(c["read_by"]).strip().lower():
            raise GateError(f"Перевіряти має не той, хто читав ({c['read_by']}): {c.get('claim')}")
        if NOT_BLIND.search(str(c["checked_by"])):
            raise GateError(f"Перевірка не сліпа («{c['checked_by']}») — максимум «ймовірно»: "
                            f"{c.get('claim')}")
    if lvl in ("probable", "hypothesis", "not_found") and not c.get("source"):
        raise GateError(f"Потрібне джерело (де шукали / на чому тримається): {c.get('claim')}")


def init(path):
    wb = Workbook()
    ws = wb.active
    ws.title = SHEET
    for i, (_, title, width) in enumerate(COLUMNS, start=1):
        c = ws.cell(row=1, column=i, value=title)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="44546A")
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.column_dimensions[c.column_letter].width = width
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = f"A1:{ws.cell(row=1, column=len(COLUMNS)).column_letter}1"
    legend = wb.create_sheet("Легенда")
    legend.append(["Рівень", "Коли ставити"])
    rules = [
        ("підтверджено", "Прочитано на скані першоджерела; прочитання незалежно перевірив "
                         "інший читач (evidence-verifier або людина). Без цього — «ймовірно»."),
        ("ймовірно", "Скан прочитав один читач, або є невпевнене слово (?), або тотожність "
                     "особи спирається на кілька незалежних непрямих збігів. Лише індекс — "
                     "максимум «ймовірно»."),
        ("гіпотеза", "Висновок методом виключення, за одним збігом або коли записи "
                     "суперечать одне одному. У дерево — лише з позначкою «гіпотеза»."),
        ("не знайдено", "Шукали — не знайшли. Записати, де саме і чи джерело повне."),
    ]
    for name, rule in rules:
        legend.append([name, rule])
        legend.cell(row=legend.max_row, column=1).fill = PatternFill(
            "solid", fgColor=LEVELS[LABEL_TO_LEVEL[name]][1])
    legend.column_dimensions["A"].width = 16
    legend.column_dimensions["B"].width = 100
    wb.save(path)


def _norm_claim(obj):
    out = {UA_KEYS.get(k.lower(), k.lower()): v for k, v in obj.items()}
    out["level"] = canon_level(out.get("level", "hypothesis"))
    out.setdefault("checked_on", dt.date.today().isoformat())
    return out


def _paint(ws, row, level):
    label, colour = LEVELS[level]
    fill = PatternFill("solid", fgColor=colour)
    for col in range(1, len(COLUMNS) + 1):
        cell = ws.cell(row=row, column=col)
        cell.fill = fill
        cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws.cell(row=row, column=COL["level"], value=label)


def _row_dict(ws, row):
    return {k: ws.cell(row=row, column=COL[k]).value for k in KEYS}


def add(path, claims):
    if not os.path.exists(path):
        init(path)
    claims = [_norm_claim(c) for c in claims]
    errors = []
    for c in claims:
        if not c.get("claim"):
            errors.append(f"Без тексту твердження: {c}")
            continue
        try:
            gate(c)
        except GateError as e:
            errors.append(str(e))
    if errors:
        raise GateError("Не додано нічого. Виправте:\n- " + "\n- ".join(errors))
    wb = load_workbook(path)
    ws = wb[SHEET]
    next_id = ws.max_row
    added = []
    for c in claims:
        cid = c.get("id") or f"E{next_id:03d}"
        next_id += 1
        row = ws.max_row + 1
        for key in KEYS:
            val = cid if key == "id" else c.get(key, "")
            cell = ws.cell(row=row, column=COL[key], value=val)
            if key == "link" and val:
                cell.hyperlink = str(val)
        _paint(ws, row, c["level"])
        added.append(cid)
    wb.save(path)
    print(f"Додано {len(added)}: {', '.join(added)}")


def set_level(path, cid, level, checked_by):
    wb = load_workbook(path)
    ws = wb[SHEET]
    level = canon_level(level)
    for row in range(2, ws.max_row + 1):
        if ws.cell(row=row, column=1).value == cid:
            c = _row_dict(ws, row)
            c["level"] = level
            if checked_by:
                c["checked_by"] = checked_by
            gate(c)
            ws.cell(row=row, column=COL["checked_by"], value=c.get("checked_by"))
            ws.cell(row=row, column=COL["checked_on"], value=dt.date.today().isoformat())
            _paint(ws, row, level)
            wb.save(path)
            print(f"{cid} → {LEVELS[level][0]}")
            return
    raise GateError(f"{cid} не знайдено")


def _rows(path):
    wb = load_workbook(path, read_only=True)
    ws = wb[SHEET]
    out = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r and r[0]:
            out.append(dict(zip(KEYS, r)))
    return out


def summary(path):
    rows = _rows(path)
    lv = Counter(r["level"] for r in rows)
    print(f"Тверджень: {len(rows)} — " + ", ".join(f"{k}: {v}" for k, v in lv.items()))
    people = Counter(r["person"] for r in rows)
    print("За особами: " + "; ".join(f"{p} ({n})" for p, n in people.most_common(15)))
    waiting = [r for r in rows if r["level"] == "ймовірно" and r.get("read_by") and not r.get("checked_by")
               and (r.get("image") or "/3:1:" in str(r.get("link") or ""))]
    if waiting:
        print("\nЧекають верифікатора (скан прочитав один читач):")
        for r in waiting:
            print(f"  {r['id']} {r['person']}: {r['claim']}  [{r.get('image') or r.get('link')}]")
    weak = [r for r in rows if r["level"] == "гіпотеза" and str(r.get("tree") or "").lower() not in ("", "ні", "no")]
    if weak:
        print("\n⚠ Гіпотези, внесені в дерево — переконатися, що позначені як гіпотеза:")
        for r in weak:
            print(f"  {r['id']} {r['person']}: {r['claim']}")
    noimg = [r for r in rows if r["level"] == "ймовірно" and not (r.get("image") or r.get("link"))]
    if noimg:
        print("\n⚠ «ймовірно» без посилання на скан чи індекс:")
        for r in noimg:
            print(f"  {r['id']} {r['person']}: {r['claim']}")


def export_md(path):
    rows = _rows(path)
    print("| ID | Твердження | Рівень | На чому тримається | Скан | Прочитав / перевірив |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        claim = f"{r['person']}: {r['claim']}" if r.get("person") else r["claim"]
        basis = r.get("reasoning") or r.get("source") or ""
        scan = r.get("link") or r.get("image") or "—"
        if r.get("link"):
            kind = "скан" if "/3:1:" in r["link"] else ("лише індекс" if "/1:1:" in r["link"] else "посилання")
            scan = f"[{r.get('image') or kind}]({r['link']})"
        who = " / ".join(x for x in (r.get("read_by"), r.get("checked_by")) if x) or "—"
        cells = [r["id"], claim, f"**{r['level']}**", basis, scan, who]
        print("| " + " | ".join(str(c).replace("|", "/").replace("\n", " ") for c in cells) + " |")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init"); p.add_argument("file")
    p = sub.add_parser("add"); p.add_argument("file")
    p.add_argument("--json"); p.add_argument("--from", dest="src")
    p = sub.add_parser("set"); p.add_argument("file"); p.add_argument("--id", required=True)
    p.add_argument("--level", required=True); p.add_argument("--checked-by")
    p = sub.add_parser("summary"); p.add_argument("file")
    p = sub.add_parser("export-md"); p.add_argument("file")
    a = ap.parse_args(argv)
    if a.cmd == "init":
        init(a.file); print(f"Створено {a.file}")
    elif a.cmd == "add":
        if a.src:
            with open(a.src, encoding="utf-8") as fh:
                data = json.load(fh)
        elif a.json:
            data = json.loads(a.json)
        else:
            data = json.load(sys.stdin)
        add(a.file, data if isinstance(data, list) else [data])
    elif a.cmd == "set":
        set_level(a.file, a.id, a.level, a.checked_by)
    elif a.cmd == "summary":
        summary(a.file)
    else:
        export_md(a.file)


if __name__ == "__main__":
    main()
