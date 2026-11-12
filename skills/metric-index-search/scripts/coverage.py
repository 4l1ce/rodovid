#!/usr/bin/env python3
"""Which church / book / month is actually covered by the indexes?

Run before concluding that a person is "not there": a missing month or a
missing church means the index cannot answer the question.

  coverage.py DIR
  coverage.py DIR --kind birth --church Троиц
"""
from __future__ import annotations

import argparse
import signal
import sys
from collections import defaultdict

from rodovid_common import iter_records, norm

signal.signal(signal.SIGPIPE, signal.SIG_DFL)

MONTHS = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август",
          "сентябрь", "октябрь", "ноябрь", "декабрь"]
MONTH_ALIASES = {"генварь": "январь", "майя": "май"}
KIND_UA = {"birth": "народження", "marriage": "шлюби", "death": "смерті"}


def month_of(rec):
    m = norm(rec.get("Месяц") or "").strip()
    m = MONTH_ALIASES.get(m, m)
    if m in MONTHS:
        return MONTHS.index(m) + 1
    d = str(rec.get("Дата рождения", "Дата", "Дата смерти") or "")
    if len(d) >= 7 and d[5:7].isdigit():
        return int(d[5:7])
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--kind", action="append", choices=["birth", "marriage", "death"])
    ap.add_argument("--church")
    args = ap.parse_args(argv)

    counts = defaultdict(lambda: defaultdict(int))
    unknown = defaultdict(int)
    for rec in iter_records(args.paths, set(args.kind) if args.kind else None):
        if rec.kind == "other":
            continue
        church = rec.church or "?"
        if args.church and args.church.lower() not in church.lower():
            continue
        key = (rec.year, KIND_UA[rec.kind], church)
        m = month_of(rec)
        if m:
            counts[key][m] += 1
        else:
            unknown[key] += 1

    out = sys.stdout
    out.write("# Покриття індексів (записів за місяць)\n\n")
    out.write("| Рік | Книга | Церква | " + " | ".join(str(i) for i in range(1, 13)) +
              " | без міс. | Пропущені місяці |\n|" + "---|" * 17 + "\n")
    for key in sorted(set(counts) | set(unknown)):
        row = counts[key]
        cells = [str(row.get(i, "·")) for i in range(1, 13)]
        missing = [str(i) for i in range(1, 13) if i not in row]
        miss = ", ".join(missing) if missing else "—"
        if args.kind == ["marriage"] or key[1] == "шлюби":
            miss += " (у шлюбах пропуски в піст — норма)" if missing else ""
        out.write(f"| {key[0]} | {key[1]} | {key[2]} | " + " | ".join(cells) +
                  f" | {unknown.get(key, 0) or '·'} | {miss} |\n")
    out.write("\nЦерква без місяців народжень/смертей — найчастіше втрачені аркуші або "
              "непрочитані знімки, а не відсутність подій. Шлюби не вінчали у пости "
              "(березень, грудень часто порожні).\n")


if __name__ == "__main__":
    main()
