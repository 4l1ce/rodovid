#!/usr/bin/env python3
"""Search metric-book index workbooks for a person or a surname.

Examples
  search_index.py DIR --surname Третьяк
  search_index.py DIR --surname Грушак --mode fuzzy --threshold 0.78
  search_index.py DIR --surname Бугай --given Петр --kind birth --years 1884-1890
  search_index.py DIR --surname Шульга --patronymic Николай --role батько
  search_index.py DIR --surname Саенко --format csv > saenko.csv

Each hit shows year, sheet, church, record number, date, the role in which
the surname appears (батько, мати, хрещені, поручителі, ...), the matched
spelling with its score, the image file and the transcriber's note.
Fuzzy hits (score < 1) are leads, not identifications: verify on the scan.
"""
from __future__ import annotations

import argparse
import csv
import json
import signal
import sys

from rodovid_common import (has_given, has_patronymic, iter_records,
                            match_surname, role_cells)

signal.signal(signal.SIGPIPE, signal.SIG_DFL)

KIND_ALIASES = {"birth": "birth", "births": "birth", "народження": "birth",
                "marriage": "marriage", "шлюби": "marriage", "шлюб": "marriage",
                "death": "death", "смерті": "death", "смерть": "death"}


def parse_years(spec: str | None):
    if not spec:
        return None
    a, _, b = spec.partition("-")
    return int(a), int(b or a)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="xlsx files, globs or folders")
    ap.add_argument("--surname", action="append", required=True,
                    help="surname to look for; repeat for spelling variants")
    ap.add_argument("--given", help="given name in the same cell (variants folded: Иван=Іван=Иоанн)")
    ap.add_argument("--patronymic", help="father's given name, e.g. Николай -> Николаев/Николаевна")
    ap.add_argument("--role", action="append",
                    help="limit to role(s): дитина, батько, мати, хрещені, наречений, наречена, "
                         "поручителі нареченого, поручителі нареченої, померлий, примітка")
    ap.add_argument("--kind", action="append", help="birth / marriage / death")
    ap.add_argument("--years", help="e.g. 1885-1890")
    ap.add_argument("--church", help="substring of church name")
    ap.add_argument("--mode", choices=["exact", "prefix", "fuzzy"], default="fuzzy")
    ap.add_argument("--threshold", type=float, default=0.82)
    ap.add_argument("--any-start", action="store_true",
                    help="fuzzy: allow a different first letter (Гоменко ~ Хоменко)")
    ap.add_argument("--no-notes", action="store_true", help="ignore matches found only in notes")
    ap.add_argument("--format", choices=["md", "csv", "json"], default="md")
    args = ap.parse_args(argv)

    kinds = {KIND_ALIASES[k.lower()] for k in args.kind} if args.kind else None
    years = parse_years(args.years)
    roles = {r.lower() for r in args.role} if args.role else None

    hits = []
    for rec in iter_records(args.paths, kinds):
        if years and rec.year.isdigit() and not (years[0] <= int(rec.year) <= years[1]):
            continue
        if args.church and args.church.lower() not in rec.church.lower():
            continue
        for col, role, cell in role_cells(rec):
            if roles and role not in roles:
                continue
            if args.no_notes and role == "примітка":
                continue
            best = None
            for q in args.surname:
                m = match_surname(cell, q, args.mode, args.threshold, not args.any_start)
                if m and (best is None or m.score > best.score):
                    best = m
            if not best:
                continue
            # a child's own cell holds only the given name: check given/patronymic
            # against the father's cell in that case
            context = cell
            if role == "дитина":
                continue  # child cell has no surname; surname is on the father
            if role == "батько" and rec.data.get("Имя"):
                # --given may name the child: «Петр» born to «Спиридон ... Бугай»
                context = f"{cell} {rec.data['Имя']}"
            if args.given and not has_given(context, args.given):
                continue
            if args.patronymic and not has_patronymic(context, args.patronymic):
                continue
            hits.append({
                "year": rec.year, "sheet": rec.sheet, "church": rec.church,
                "no": rec.number, "date": rec.date, "role": role,
                "matched": best.token, "score": best.score, "how": best.how,
                "cell": cell, "summary": rec.summary(), "image": rec.image_label,
                "note": str(rec.get("Примечания")), "file": rec.file, "row": rec.row,
            })

    # one line per record: merge roles when the surname appears twice
    merged = {}
    for h in hits:
        key = (h["file"], h["sheet"], h["row"])
        if key in merged:
            m = merged[key]
            if h["role"] not in m["role"]:
                m["role"] += ", " + h["role"]
            if h["score"] > m["score"]:
                m.update(matched=h["matched"], score=h["score"], how=h["how"])
        else:
            merged[key] = dict(h)
    hits = sorted(merged.values(), key=lambda h: (h["year"], h["date"], h["sheet"], h["row"]))
    out = sys.stdout
    if args.format == "json":
        json.dump(hits, out, ensure_ascii=False, indent=1)
        return
    if args.format == "csv":
        w = csv.DictWriter(out, fieldnames=list(hits[0].keys()) if hits else ["year"])
        w.writeheader()
        w.writerows(hits)
        return

    q = " / ".join(args.surname)
    out.write(f"## Пошук: {q} — {len(hits)} збігів\n\n")
    if not hits:
        out.write("Нічого не знайдено. Відсутність у індексі ≠ відсутність у книзі: "
                  "перевірте повноту року (coverage.py) і нечитабельні записи.\n")
        return
    out.write("| Рік | Книга | Церква | № | Дата | Роль | Написання (оцінка) | Запис | Скан | Примітка |\n")
    out.write("|---|---|---|---|---|---|---|---|---|---|\n")
    for h in hits:
        mark = "" if h["how"] == "exact" else f" ({h['how']} {h['score']})"
        note = (h["note"] if h["note"] not in ("None", "") else "").replace("|", "/")
        out.write(f"| {h['year']} | {h['sheet']} | {h['church']} | {h['no']} | {h['date']} | "
                  f"{h['role']} | {h['matched']}{mark} | {h['summary'].replace('|', '/')} | "
                  f"{h['image']} | {note[:160]} |\n")
    fuzzy = sum(1 for h in hits if h["how"] != "exact")
    if fuzzy:
        out.write(f"\n{fuzzy} збіг(ів) не точні — це зачіпки, їх треба звірити зі сканом.\n")


if __name__ == "__main__":
    main()
