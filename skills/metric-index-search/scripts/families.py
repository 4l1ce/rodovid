#!/usr/bin/env python3
"""Reconstruct families (sibships) for a surname from metric-book indexes.

Births are grouped by father (given name + patronymic + surname, with name
variants folded: Яков = Иаков = Яків). For every family the report lists the
mothers named, all children with dates and scans, child deaths that name the
same father, and godparents who recur across the children — recurring
godparents and wedding witnesses are strong evidence of kinship.

  families.py DIR --surname Третьяк
  families.py DIR --surname Бугай --mode prefix --min-children 1
  families.py DIR --surname Шульга --father Николай
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict

import signal

from rodovid_common import (canon_given, canon_patronymic, iter_records, match_surname,
                            nominative_given, norm, surname_core, tokens)

from rodovid_common import NAME_CANON

signal.signal(signal.SIGPIPE, signal.SIG_DFL)
KNOWN_NAMES = set(NAME_CANON.values())

PLACE_RE = re.compile(r"\b(г\.|гор\.|города|села|с\.|деревни|хутора|из|уезда|губернии)\s+\S+", re.I)
UNCERTAIN_RE = re.compile(r"\(\?\)|\[[^\]]*\]")


def person_parts(cell: str):
    """Return (given, patronymic, surname) from a cell such as
    'козак города Борзны Яков Антониев Третьяк'."""
    text = UNCERTAIN_RE.sub("", PLACE_RE.sub("", str(cell)))
    caps = [t for t in tokens(text) if t[:1].isupper() and len(t) > 1]
    if len(caps) >= 3:
        return caps[-3], caps[-2], caps[-1]
    if len(caps) == 2:
        return caps[0], "", caps[1]
    if len(caps) == 1:
        return caps[0], "", ""
    return "", "", ""


def mother_parts(cell: str):
    text = UNCERTAIN_RE.sub("", str(cell))
    text = re.sub(r"законная жена его|жена его|законная жена", "", text, flags=re.I)
    caps = [t for t in tokens(text) if t[:1].isupper() and len(t) > 1]
    if not caps:
        return "", ""
    return caps[0], caps[1] if len(caps) > 1 else ""


def parse_age_years(age):
    """'4' -> 4; '2 мес.' / '3 нед.' / '5 дн.' -> 0; unknown -> None."""
    a = str(age or "").strip().lower()
    m = re.match(r"(\d+)", a)
    if not m:
        return None
    if re.search(r"мес|нед|дн|час", a):
        return 0
    return int(m.group(1))


def pkey(given, patr):
    return f"{canon_given(given)}|{canon_patronymic(patr) if patr else ''}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--surname", action="append", required=True)
    ap.add_argument("--father", help="only fathers with this given name")
    ap.add_argument("--mode", choices=["exact", "prefix", "fuzzy"], default="exact")
    ap.add_argument("--threshold", type=float, default=0.85)
    ap.add_argument("--min-children", type=int, default=1)
    args = ap.parse_args(argv)

    def hit(cell):
        return any(match_surname(cell, q, args.mode, args.threshold) for q in args.surname)

    fams = defaultdict(lambda: {"names": Counter(), "ranks": Counter(), "mothers": Counter(),
                                "children": [], "deaths": [], "godparents": Counter(),
                                "mother_keys": {}})
    deaths = []
    marriages = []
    born = defaultdict(set)   # (child given, father's given, surname core) -> birth years
    for rec in iter_records(args.paths):
        d = rec.data
        if rec.kind == "birth" and d.get("Отец") and hit(d["Отец"]):
            g, p, s = person_parts(d["Отец"])
            if not g or (args.father and canon_given(g) != canon_given(args.father)):
                continue
            key = (pkey(g, p), surname_core(s))
            if d.get("Имя") and rec.year.isdigit():
                born[(canon_given(str(d["Имя"]).split("(")[0]), canon_given(g), surname_core(s))].add(int(rec.year))
            f = fams[key]
            f["names"][f"{g} {p} {s}".strip()] += 1
            rank = str(d.get("Звание отца") or "").strip()
            if rank:
                f["ranks"][rank] += 1
            mg, mp = mother_parts(d.get("Мать") or "")
            f["mother_keys"].setdefault(pkey(mg, mp), f"{mg} {mp}".strip() or "—")
            f["mothers"][f["mother_keys"][pkey(mg, mp)]] += 1
            gp = str(d.get("Восприемники") or "")
            for part in re.split(r";| и ", gp):
                part = part.strip()
                if part:
                    gg, gpatr, gs = person_parts(part)
                    if gg:
                        f["godparents"][f"{gg} {gpatr} {gs}".strip()] += 1
            f["children"].append((rec.year, rec.date, d.get("Имя"), d.get("Пол"), rec.church,
                                  rec.number, gp, rec.image_label, rec.get("Примечания")))
        elif rec.kind == "death" and d.get("Умерший") and hit(d["Умерший"]):
            deaths.append(rec)
        elif rec.kind == "marriage" and any(hit(d.get(c) or "") for c in ("Жених", "Невеста")):
            marriages.append(rec)

    # attach child deaths: '<rank> <Father> <Surname> сын/дочь <Name>'
    for rec in deaths:
        cell = str(rec.data["Умерший"])
        m = re.search(r"(.*?)\s+(сын|дочь|дочерь|младенец|младенца|дитя|ребенок)\s+(\S+)", cell)
        if not m:
            continue
        father_part, rel, child = m.groups()
        caps = [t for t in tokens(UNCERTAIN_RE.sub("", father_part)) if t[:1].isupper()]
        if len(caps) < 2:
            continue
        surname = surname_core(caps[-1])
        # 'Козака Михаила Спиридонова Третьяка' -> given, patronymic, surname;
        # 'Козака Якова Третяка' -> given, surname (caps[-3] is then a rank word)
        if len(caps) >= 3 and nominative_given(caps[-3]) in KNOWN_NAMES:
            fgiven, fpatr = nominative_given(caps[-3]), canon_patronymic(caps[-2])
        else:
            fgiven, fpatr = nominative_given(caps[-2]), ""
        for key, f in fams.items():
            kgiven, kpatr = key[0].split("|")
            if key[1] != surname or kgiven != fgiven:
                continue
            if fpatr and kpatr and fpatr != kpatr:
                continue
            f["deaths"].append((rec.year, rec.date, child, rec.get("Возраст"), rec.image_label, cell,
                                "" if fpatr else " (по батькові в записі нема — перевірити)"))

    # father's own birth year, when he appears as a child in the same indexes:
    # a father younger than 16 at a child's birth means a misread age, another
    # man of the same name, or a wrong link
    age_flags = []
    for key, f in fams.items():
        kgiven, kpatr = key[0].split("|")
        years = born.get((kgiven, kpatr, key[1])) if kpatr else None
        if not years or len(years) != 1:
            continue
        fb = next(iter(years))
        name = f["names"].most_common(1)[0][0]
        for c in f["children"]:
            if str(c[0]).isdigit() and int(c[0]) - fb < 16:
                age_flags.append(f"{name} (нар. {fb}): дитина {c[2]} нар. {c[0]} — батькові {int(c[0]) - fb}")
        for dd in f["deaths"]:
            age = parse_age_years(dd[3])
            if age is not None and str(dd[0]).isdigit():
                cb = int(dd[0]) - age
                if cb - fb < 16:
                    age_flags.append(f"{name} (нар. {fb}): {dd[2]} помер {dd[0]} у віці {dd[3]} → нар. бл. {cb}, "
                                     f"батькові було б {cb - fb} — помилка у віці, інший {name.split()[0]} "
                                     "чи хибна прив'язка?")

    out = sys.stdout
    q = " / ".join(args.surname)
    shown = [(k, f) for k, f in fams.items() if len(f["children"]) >= args.min_children]
    shown.sort(key=lambda kv: (-len(kv[1]["children"]), kv[0]))
    out.write(f"# Родини: {q}\n\n{len(shown)} батьків з дітьми в індексах. "
              "Групування за іменем+по батькові батька; збіг імен ≠ одна людина — "
              "перевірте матір, стан (звання) і хрещених.\n\n")
    for key, f in shown:
        name = f["names"].most_common(1)[0][0]
        out.write(f"## {name}\n")
        if len(f["names"]) > 1:
            out.write(f"- Написання: {', '.join(n for n, _ in f['names'].most_common())}\n")
        if f["ranks"]:
            out.write(f"- Стан/звання: {', '.join(f'{r} ×{c}' for r, c in f['ranks'].most_common())}\n")
        out.write(f"- Матері: {', '.join(f'{m} ×{c}' for m, c in f['mothers'].most_common())}\n")
        if len(f["mothers"]) > 1:
            out.write("  - ⚠ кілька матерів: або другий шлюб, або це різні батьки з однаковим іменем\n")
        out.write("\n| Рік | Дата | Дитина | Стать | Церква | № | Хрещені | Скан |\n|---|---|---|---|---|---|---|---|\n")
        for c in sorted(f["children"], key=lambda c: (c[0], c[1])):
            out.write(f"| {c[0]} | {c[1]} | {c[2]} | {c[3]} | {c[4]} | {c[5]} | {c[6]} | {c[7]} |\n")
        if f["deaths"]:
            out.write("\nСмерті дітей з тим самим батьком:\n")
            for dd in sorted(f["deaths"]):
                out.write(f"- {dd[0]} {dd[1]}: {dd[2]}, {dd[3]} р. — «{dd[5]}» ({dd[4]}){dd[6]}\n")
        rec_gp = [(g, c) for g, c in f["godparents"].items() if c > 1]
        if rec_gp:
            out.write("\nХрещені, що повторюються: " +
                      "; ".join(f"{g} ×{c}" for g, c in sorted(rec_gp, key=lambda x: -x[1])) + "\n")
        out.write("\n")

    # same mother (given + patronymic) under two different fathers with the same
    # surname usually means one of the fathers' names is misread or written
    # in another form (Григорий / Георгий, Антоний / Андрей)
    by_mother = defaultdict(list)
    for key, f in fams.items():
        for mkey in f["mother_keys"]:
            if mkey.split("|")[1]:
                by_mother[(key[1], mkey)].append(f["names"].most_common(1)[0][0])
    dupes = [(k, v) for k, v in by_mother.items() if len(set(v)) > 1]
    if dupes:
        out.write("## ⚠ Можливо одна родина під різними іменами батька\n\n")
        for (sur, mkey), fathers in dupes:
            out.write(f"- мати «{mkey.replace('|', ' / ')}» у батьків: {', '.join(sorted(set(fathers)))} "
                      "— звірити скани: різні люди чи різне прочитання/форма імені?\n")
        out.write("\n")

    if age_flags:
        out.write("## ⚠ Вік батька не сходиться\n\n")
        for line in age_flags:
            out.write(f"- {line}\n")
        out.write("\n")

    if marriages:
        out.write(f"## Шлюби з прізвищем {q}\n\n| Рік | Дата | Церква | № | Запис | Скан |\n|---|---|---|---|---|---|\n")
        for rec in sorted(marriages, key=lambda r: (r.year, r.date)):
            out.write(f"| {rec.year} | {rec.date} | {rec.church} | {rec.number} | "
                      f"{rec.summary().replace('|', '/')} | {rec.image_label} |\n")


if __name__ == "__main__":
    main()
