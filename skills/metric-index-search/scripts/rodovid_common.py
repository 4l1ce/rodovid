"""Shared helpers for metric-book index scripts (rodovid-agent).

Index workbooks follow one schema: one workbook per year, sheets
«Рождения», «Браки», «Смерти» (see scan-transcribe/references/schema.md).
Older or third-party workbooks may differ slightly; headers are matched
by name, not by column position.
"""
from __future__ import annotations

import difflib
import sys

try:
    sys.stdout.reconfigure(errors='replace')
except Exception:
    pass
import glob
import json
import os
import re
from dataclasses import dataclass, field

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- normalising
_TRANS = str.maketrans({
    "ё": "е", "є": "е", "э": "е", "ѣ": "е",
    "і": "и", "ї": "и", "ы": "и", "ѵ": "и",
    "ґ": "г", "ѳ": "ф", "ѡ": "о",
    "ъ": "", "ь": "", "'": "", "’": "", "ʼ": "", "`": "",
})

def norm(text: str) -> str:
    """Lower-case, fold Ukrainian/Russian/pre-reform letters, drop signs."""
    return str(text).lower().translate(_TRANS)

TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яЁёІіЇїЄєҐґѢѣѲѳѴѵ'’ʼ-]+")

def tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(str(text))

# Endings stripped to get a comparable surname core. Longest first.
_SURNAME_ENDINGS = sorted([
    "ихи", "иха", "ова", "ева", "ина", "ая", "ий", "ой", "ов", "ев", "ин",
    "ого", "ого", "ему", "а", "я", "у",
], key=len, reverse=True)

def surname_core(tok: str) -> str:
    t = norm(tok).strip("-")
    for end in _SURNAME_ENDINGS:
        if t.endswith(end) and len(t) - len(end) >= 3:
            return t[: -len(end)]
    return t

# ---------------------------------------------------------------- given names
def _load_name_groups() -> dict[str, str]:
    path = os.path.join(HERE, "given_names.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        groups = json.load(fh)
    canon = {}
    for group in groups:
        key = norm(group[0])
        for variant in group:
            canon[norm(variant)] = key
    return canon

NAME_CANON = _load_name_groups()

def canon_given(name: str) -> str:
    n = norm(name)
    return NAME_CANON.get(n, n)

def _known(cands):
    for c in cands:
        if norm(c) in NAME_CANON:
            return NAME_CANON[norm(c)]
    return None

def canon_patronymic(patr: str) -> str:
    """'Феодорова' / 'Федоров' / 'Федорович' -> canonical father's name 'феодор'."""
    n = norm(patr)
    root = re.sub(r"(овича|евича|ович|евич|овна|евна|ична|инична|ова|ева|ов|ев|ина|ин|ого|ому)$", "", n)
    found = _known([root, root + "ий", root + "ей", root + "ай", root + "й", root + "а", root + "о",
                    root + "ия", root + "ь"])
    return found or root

def nominative_given(word: str) -> str:
    """Genitive/dative of a given name back to its canonical form: Михаила, Якову -> михаил, иаков."""
    n = norm(word)
    found = _known([n, n[:-1], n[:-1] + "й", n[:-1] + "а", n[:-1] + "я", n[:-2] + "ий",
                    n[:-1] + "ь", n[:-1] + "о"])
    return found or n

def patronymic_prefix(father_name: str) -> str:
    """'Николай' -> 'никола', 'Тихон' -> 'тихон', 'Яков' -> 'яков'."""
    n = norm(father_name)
    n = re.sub(r"(ий|ей|ай|й|я|а|о)$", "", n)
    return n[: max(3, len(n))]

def patronymic_variants(father_name: str) -> set[str]:
    out = set()
    for variant, key in NAME_CANON.items():
        if key == canon_given(father_name):
            out.add(patronymic_prefix(variant))
    out.add(patronymic_prefix(father_name))
    return {p for p in out if len(p) >= 3}

# ---------------------------------------------------------------- matching
@dataclass
class Match:
    token: str
    score: float
    how: str

def match_surname(cell: str, query: str, mode: str = "fuzzy",
                  threshold: float = 0.82, same_start: bool = True) -> Match | None:
    """Best surname match of `query` among tokens of `cell`.

    exact  – same core after normalising (Третьяк = Третяк = Третьякова)
    prefix – core starts with the query core (Бугай -> Бугаенко)
    fuzzy  – exact, prefix, or difflib ratio >= threshold (Грушак ~ Грушач);
             by default the first letter must agree (Грушак !~ Ушакова)
    """
    qcore = surname_core(query)
    best = None
    for tok in tokens(cell):
        if len(tok) < 3:
            continue
        core = surname_core(tok)
        if core == qcore:
            return Match(tok, 1.0, "exact")
        if mode in ("prefix", "fuzzy") and len(qcore) >= 4 and core.startswith(qcore):
            cand = Match(tok, 0.95, "prefix")
        elif mode == "fuzzy" and (not same_start or core[:1] == qcore[:1]):
            ratio = difflib.SequenceMatcher(None, core, qcore).ratio()
            cand = Match(tok, round(ratio, 2), "fuzzy") if ratio >= threshold else None
        else:
            cand = None
        if cand and (best is None or cand.score > best.score):
            best = cand
    return best

def has_given(cell: str, given: str) -> bool:
    key = canon_given(given)
    return any(canon_given(t) == key for t in tokens(cell))

def has_patronymic(cell: str, father_name: str) -> bool:
    prefixes = patronymic_variants(father_name)
    for tok in tokens(cell):
        n = norm(tok)
        if any(n.startswith(p) and len(n) > len(p) for p in prefixes):
            return True
    return False

# ---------------------------------------------------------------- workbooks
SHEET_KIND = {"рождения": "birth", "браки": "marriage", "смерти": "death",
              "народження": "birth", "шлюби": "marriage", "смерть": "death",
              "смерті": "death"}

# header -> role label (Ukrainian, for reports)
ROLE_COLUMNS = {
    "birth": {"Имя": "дитина", "Отец": "батько", "Мать": "мати",
              "Восприемники": "хрещені", "Примечания": "примітка"},
    "marriage": {"Жених": "наречений", "Невеста": "наречена",
                 "Поручители по женихе": "поручителі нареченого",
                 "Поручители по невесте": "поручителі нареченої",
                 "Примечания": "примітка"},
    "death": {"Умерший": "померлий", "Примечания": "примітка"},
}

@dataclass
class Record:
    file: str
    year: str
    sheet: str
    kind: str
    row: int
    data: dict = field(default_factory=dict)
    file_year: str = "?"

    def get(self, *names, default=""):
        for n in names:
            v = self.data.get(n)
            if v not in (None, ""):
                return v
        return default

    @property
    def church(self):
        return str(self.get("Церковь", "Город/Село"))

    @property
    def date(self):
        d = self.get("Дата рождения", "Дата", "Дата смерти")
        if d:
            return str(d)[:10]
        m, dd = self.get("Месяц"), self.get("День рожд.", "День", "День смерти")
        return f"{dd} {m}".strip()

    @property
    def number(self):
        parts = []
        for col, lab in (("№ (м)", "м"), ("№ (ж)", "ж"), ("№", "")):
            v = self.data.get(col)
            if v not in (None, ""):
                parts.append(f"{lab}{v}" if lab else str(v))
        return "/".join(parts)

    @property
    def image(self):
        return str(self.get("Файл"))

    @property
    def index_only(self) -> bool:
        """True when only an online index entry was seen, not the scan.
        Convention: «Файл» = "індекс: <link>" or a FamilySearch 1:1: link."""
        img = self.image.lower()
        return img.startswith(("індекс", "index")) or "/1:1:" in img

    @property
    def image_label(self) -> str:
        return f"{self.image} (лише індекс)" if self.index_only and not self.image.lower().startswith("індекс") else self.image

    def summary(self) -> str:
        d = self.data
        if self.kind == "birth":
            return (f"{d.get('Имя') or '?'} ({d.get('Пол') or '?'}); батько: "
                    f"{d.get('Звание отца') or ''} {d.get('Отец') or '—'}; мати: "
                    f"{d.get('Мать') or '—'}; хрещені: {d.get('Восприемники') or '—'}")
        if self.kind == "marriage":
            return (f"{d.get('Звание жениха') or ''} {d.get('Жених') or '?'} "
                    f"({d.get('Возраст жениха') or '?'}, {d.get('Браком (жених)') or '?'}) × "
                    f"{d.get('Звание невесты') or ''} {d.get('Невеста') or '?'} "
                    f"({d.get('Возраст невесты') or '?'}); поручителі: "
                    f"{d.get('Поручители по женихе') or '—'} | {d.get('Поручители по невесте') or '—'}")
        if self.kind == "death":
            return (f"{d.get('Умерший') or '?'}, {d.get('Возраст') or '?'} р., "
                    f"{d.get('Причина смерти') or ''}")
        return "; ".join(f"{k}: {v}" for k, v in d.items() if v)

YEAR_RE = re.compile(r"(1[6-9]\d\d)")

def year_of(path: str) -> str:
    m = YEAR_RE.findall(os.path.basename(path))
    return m[-1] if m else "?"

def expand_paths(paths: list[str]) -> list[str]:
    out = []
    for p in paths:
        if os.path.isdir(p):
            out += sorted(glob.glob(os.path.join(p, "**", "*.xls*"), recursive=True))
        else:
            out += sorted(glob.glob(p)) or [p]
    return [p for p in out if not os.path.basename(p).startswith("~$")]

def iter_records(paths: list[str], kinds: set[str] | None = None):
    for path in expand_paths(paths):
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        for ws in wb.worksheets:
            kind = SHEET_KIND.get(ws.title.strip().lower(), "other")
            if kinds and kind not in kinds:
                continue
            header = None
            for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
                if header is None:
                    if row and any(row):
                        header = [str(c).strip() if c is not None else f"col{j}"
                                  for j, c in enumerate(row)]
                    continue
                if not row or not any(c not in (None, "") for c in row):
                    continue
                data = {h: v for h, v in zip(header, row)}
                fy = year_of(path)
                # multi-year workbooks (e.g. imported online index) take the year
                # from the record's own date
                d = str(data.get("Дата рождения") or data.get("Дата") or data.get("Дата смерти") or "")
                year = d[:4] if YEAR_RE.fullmatch(d[:4] or "x") else fy
                yield Record(os.path.basename(path), year, ws.title,
                             kind, i, data, file_year=fy)
        wb.close()

def role_cells(rec: Record):
    cols = ROLE_COLUMNS.get(rec.kind)
    if not cols:
        for k, v in rec.data.items():
            if v:
                yield k, k, str(v)
        return
    for col, role in cols.items():
        v = rec.data.get(col)
        if v:
            yield col, role, str(v)
