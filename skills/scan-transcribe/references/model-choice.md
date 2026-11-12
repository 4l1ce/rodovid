# Which model reads handwriting

Blind test, 10 Nov 2026: one page of the Rumyantsev Description (ЦДІАК
ф.57 оп.1 спр.4, зобр. 56, right page, двір 43; 18th-century скоропис),
read independently by four Claude models from the same image tiles and
scored against the reading already checked by the person on both copies.

| Item | Checked reading | Haiku | Sonnet | Opus | Fable |
|---|---|---|---|---|---|
| Head | Марія Игнатова Шулжиха, 50 | not read | Шулгиха, 50 | correct | correct |
| Son 1 | Иванъ 20, на праву ногу хромъ | partly | "на сторону ходитъ" | correct | correct |
| His wife | Устинія Матвѣева 20 | not read | Мартынова | Мартынова | correct |
| Son 2 | Григорій 13 | Яхім | "daughter Гриня" | correct | correct |
| Son 3 | Савва 11 | Сапна | "daughter Сапна" | Ганна | correct |
| Worker | Карпо 40 | no name | no name | Марко | correct |
| Worker's wife | Евдокія 24 | — | "his son" | Ѳедорка | correct |
| Pay | 4 руб. 50 коп. | 4 руб. | 4 руб. | correct | 4 руб., kopecks not read |
| Hay | 70 возовъ | — | 40 | 40 | 70 |
| Wood, circumference | 4 четверти, 446 саж. | "46" | 446 | correct | correct |

What follows from it:

- Fable read the household almost completely; Opus got three of seven
  names wrong; Sonnet and Haiku are not usable on this hand.
- Wrong readings look plausible (Мартынова, Ганна, Марко) and came with
  medium confidence. A model's own confidence does not flag them.
- Every place where Opus and Fable disagreed was a truly difficult place;
  where all models agreed there were no errors. Disagreement between two
  different models is the useful signal.

Limits: one page, one run, one hand; the checked reading was itself partly
produced by earlier Claude readings. Re-run the test (same method: same
tiles, blind prompts, a reading checked by the person) on a new kind of
hand before relying on this table for it, and update this file.
