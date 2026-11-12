#!/usr/bin/env python3
"""Create or extend a metric-book index workbook in the standard schema.

  index_writer.py init  "Борзнянський повіт 1893 рік метрики.xlsx"
  index_writer.py add   FILE --sheet birth    --from rows.json
  index_writer.py add   FILE --sheet marriage --json '[{...}, ...]'

Rows are JSON objects keyed by the column names below (Russian, as in the
books). Unknown keys are rejected so a typo cannot silently drop data.
Uncertain readings stay in the text with "(?)"; illegible parts are written
as "[неразборчиво]"; the reasoning goes to «Примечания».
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

SCHEMA = {
    "birth": ("Рождения", ["Город/Село", "Церковь", "№ (м)", "№ (ж)", "Дата рождения", "Месяц",
                           "День рожд.", "День крещ.", "Имя", "Пол", "Звание отца", "Отец", "Мать",
                           "Вероисповедание", "Восприемники", "Файл", "Примечания"]),
    "marriage": ("Браки", ["Город/Село", "Церковь", "№", "Дата", "Месяц", "День", "Звание жениха",
                           "Жених", "Возраст жениха", "Браком (жених)", "Звание невесты", "Невеста",
                           "Возраст невесты", "Браком (невеста)", "Поручители по женихе",
                           "Поручители по невесте", "Файл", "Примечания"]),
    "death": ("Смерти", ["Город/Село", "Церковь", "№ (м)", "№ (ж)", "Дата смерти", "Месяц",
                         "День смерти", "День погреб.", "Умерший", "Пол", "Возраст",
                         "Причина смерти", "Файл", "Примечания"]),
}
UNCERTAIN_FILL = PatternFill("solid", fgColor="FFF2CC")


def init(path):
    wb = Workbook()
    wb.remove(wb.active)
    for _, (title, cols) in SCHEMA.items():
        ws = wb.create_sheet(title)
        ws.append(cols)
        for c in ws[1]:
            c.font = Font(bold=True)
            c.alignment = Alignment(wrap_text=True)
        ws.freeze_panes = "A2"
    wb.save(path)


def add(path, kind, rows):
    if not os.path.exists(path):
        init(path)
    title, cols = SCHEMA[kind]
    wb = load_workbook(path)
    ws = wb[title]
    for r in rows:
        bad = set(r) - set(cols)
        if bad:
            raise SystemExit(f"Невідомі стовпчики {sorted(bad)}; дозволено: {cols}")
        if not r.get("Файл"):
            raise SystemExit(f"Кожен запис має посилатися на знімок («Файл»): {r}")
        ws.append([r.get(c) for c in cols])
        for cell in ws[ws.max_row]:
            if cell.value and ("(?)" in str(cell.value) or "неразборчиво" in str(cell.value)):
                cell.fill = UNCERTAIN_FILL
    wb.save(path)
    print(f"{title}: додано {len(rows)}, усього {ws.max_row - 1}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init"); p.add_argument("file")
    p = sub.add_parser("add"); p.add_argument("file")
    p.add_argument("--sheet", choices=list(SCHEMA), required=True)
    p.add_argument("--json"); p.add_argument("--from", dest="src")
    a = ap.parse_args(argv)
    if a.cmd == "init":
        init(a.file); print(f"Створено {a.file}")
        return
    if a.src:
        with open(a.src, encoding="utf-8") as fh:
            data = json.load(fh)
    elif a.json:
        data = json.loads(a.json)
    else:
        data = json.load(sys.stdin)
    add(a.file, a.sheet, data if isinstance(data, list) else [data])


if __name__ == "__main__":
    main()
