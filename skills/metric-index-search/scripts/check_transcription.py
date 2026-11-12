#!/usr/bin/env python3
"""QA report for a metric-book transcription workbook.

Treats a transcription like any other test artefact: schema, numbering,
dates, sex/counter consistency, plausibility of ages and the share of
uncertain readings per column. Every finding points to sheet + row + scan.

  check_transcription.py "Борзнянський повіт 1890 рік метрики.xlsx"
  check_transcription.py DIR --max-findings 40
"""
from __future__ import annotations

import argparse
import re
import signal
import sys
from collections import Counter, defaultdict

from rodovid_common import expand_paths, iter_records

signal.signal(signal.SIGPIPE, signal.SIG_DFL)

REQUIRED = {
    "birth": ["Церковь", "№ (м)", "№ (ж)", "Дата рождения", "Месяц", "Имя", "Пол",
              "Отец", "Мать", "Восприемники", "Файл"],
    "marriage": ["Церковь", "№", "Дата", "Жених", "Возраст жениха", "Невеста",
                 "Возраст невесты", "Поручители по женихе", "Поручители по невесте", "Файл"],
    "death": ["Церковь", "№ (м)", "№ (ж)", "Дата смерти", "Умерший", "Пол", "Возраст", "Файл"],
}
UNCERTAIN = re.compile(r"\(\?\)|неразборчиво|\[\?\]")


def as_int(v):
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        return None


def check_file(path, max_findings):
    findings = []
    uncertain = defaultdict(Counter)
    totals = Counter()
    numbers = defaultdict(list)
    headers = {}
    index_only = 0

    def add(level, rec, msg):
        findings.append((level, rec.sheet, rec.row, rec.church, rec.image, msg))

    for rec in iter_records([path]):
        if rec.kind == "other":
            continue
        totals[rec.kind] += 1
        if rec.index_only:
            index_only += 1
        headers.setdefault(rec.kind, set(rec.data))
        d = rec.data
        for col, v in d.items():
            if v is not None and UNCERTAIN.search(str(v)):
                uncertain[rec.kind][col] += 1
        if not d.get("Файл"):
            add("помилка", rec, "немає посилання на скан (Файл)")
        # dates
        date = str(d.get("Дата рождения") or d.get("Дата") or d.get("Дата смерти") or "")
        if date and rec.file_year.isdigit() and not date.startswith(rec.file_year):
            add("увага", rec, f"дата {date} не з року файлу {rec.file_year}")
        day = as_int(d.get("День рожд.") or d.get("День") or d.get("День смерти"))
        if date and day and len(date) >= 10 and as_int(date[8:10]) != day:
            add("увага", rec, f"день у даті ({date}) ≠ стовпчик дня ({day})")
        day2 = as_int(d.get("День крещ.") or d.get("День погреб."))
        if day and day2 and day2 < day and str(d.get("Месяц", "")) not in ("",):
            # baptism / burial earlier than event within a month is suspicious
            # unless it crosses month end (day2 small, day large)
            if not (day > 20 and day2 < 10):
                add("увага", rec, f"хрещення/поховання ({day2}) раніше за подію ({day})")
        # numbering and sex
        if rec.kind in ("birth", "death"):
            m, f = as_int(d.get("№ (м)")), as_int(d.get("№ (ж)"))
            sex = str(d.get("Пол") or "").strip().upper()
            if m and sex == "Ж":
                add("увага", rec, f"№ у графі чоловічої статі ({m}), але стать Ж — перевірити (писар чи транскрипція)")
            if f and sex == "М":
                add("увага", rec, f"№ у графі жіночої статі ({f}), але стать М")
            if m:
                numbers[(rec.kind, rec.church, "м")].append((m, rec))
            if f:
                numbers[(rec.kind, rec.church, "ж")].append((f, rec))
        elif rec.kind == "marriage":
            n = as_int(d.get("№"))
            if n:
                numbers[(rec.kind, rec.church, "")].append((n, rec))
            for col in ("Возраст жениха", "Возраст невесты"):
                age = as_int(d.get(col))
                if age is not None and not 15 <= age <= 85:
                    add("увага", rec, f"{col} = {age} — неправдоподібно, перечитати")
        if rec.kind == "death":
            age = d.get("Возраст")
            if age in (None, "", "?"):
                add("інфо", rec, "вік не вказано")

    # numbering gaps / duplicates per church
    for (kind, church, sex), items in numbers.items():
        nums = Counter(n for n, _ in items)
        dup = sorted(n for n, c in nums.items() if c > 1)
        if dup:
            add("увага", items[0][1], f"{kind} {church} {sex}: повтор номерів {dup[:10]}")
        top = max(nums)
        gaps = [n for n in range(1, top + 1) if n not in nums]
        if gaps:
            add("увага", items[0][1], f"{kind} {church} {sex}: пропущені номери {gaps[:15]}"
                f"{' …' if len(gaps) > 15 else ''} з {top} — пропущені записи або нечитабельні аркуші")

    for kind, cols in REQUIRED.items():
        if kind in headers:
            missing = [c for c in cols if c not in headers[kind]]
            if missing:
                findings.insert(0, ("помилка", kind, 1, "", "", f"бракує стовпчиків: {missing}"))

    out = sys.stdout
    out.write(f"## {path.split('/')[-1]}\n\n")
    out.write("Записів: " + ", ".join(f"{k} {v}" for k, v in totals.items()) + "\n")
    if index_only:
        out.write(f"З них лише за індексом (скан не відкривали): {index_only} — "
                  "висновки з них не вище «ймовірно»\n")
    out.write("\n")
    out.write("Частка невпевнених прочитань (позначки (?) / неразборчиво):\n")
    for kind, cnt in uncertain.items():
        top = ", ".join(f"{c} {n} ({n * 100 // max(totals[kind], 1)}%)" for c, n in cnt.most_common(4))
        out.write(f"- {kind}: {top}\n")
    levels = Counter(f[0] for f in findings)
    out.write(f"\nЗнахідки: " + ", ".join(f"{k} {v}" for k, v in levels.items()) + "\n\n")
    if findings:
        out.write("| Рівень | Книга | Рядок | Церква | Скан | Що |\n|---|---|---|---|---|---|\n")
        order = {"помилка": 0, "увага": 1, "інфо": 2}
        for f in sorted(findings, key=lambda f: order[f[0]])[:max_findings]:
            out.write("| " + " | ".join(str(x) for x in f) + " |\n")
        if len(findings) > max_findings:
            out.write(f"\n… ще {len(findings) - max_findings}\n")
    out.write("\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--max-findings", type=int, default=30)
    args = ap.parse_args(argv)
    for p in expand_paths(args.paths):
        check_file(p, args.max_findings)


if __name__ == "__main__":
    main()
