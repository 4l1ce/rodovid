# Index workbook schema

One workbook per district (повіт) and year: `<Повіт> <рік> рік метрики.xlsx`.
Three sheets; one row per record. Column names are fixed (Russian, as in
the books) so that every script can read any year.

## Рождения (births)
Город/Село · Церковь · № (м) · № (ж) · Дата рождения (YYYY-MM-DD) · Месяц ·
День рожд. · День крещ. · Имя · Пол (М/Ж) · Звание отца · Отец · Мать ·
Вероисповедание · Восприемники · Файл · Примечания

- `№ (м)` / `№ (ж)`: the book's own counter, in the column the priest used
  (even if wrong — explain in Примечания).
- `Отец`: "Яков Антониев Третьяк" — given name, patronymic, surname as
  written; estate goes to `Звание отца` ("козак", "мещанин", "запасный
  рядовой", "отставной унтер-офицер", "крестьянин-собственник").
- `Мать`: as written, usually given name + patronymic ("Наталия Данилова").
- `Восприемники`: everyone, with estates, separated by ";" or " и ".

## Браки (marriages)
Город/Село · Церковь · № · Дата · Месяц · День · Звание жениха · Жених ·
Возраст жениха · Браком (жених) · Звание невесты · Невеста ·
Возраст невесты · Браком (невеста) · Поручители по женихе ·
Поручители по невесте · Файл · Примечания

## Смерти (deaths)
Город/Село · Церковь · № (м) · № (ж) · Дата смерти · Месяц · День смерти ·
День погреб. · Умерший · Пол · Возраст · Причина смерти · Файл · Примечания

- `Умерший` as written, including the relation for children:
  "Козака Якова Третяка сын Афанасий".

## Conventions
- `(?)` right after any uncertain word; `[неразборчиво]` for illegible
  parts; never guess silently.
- `Файл`: scan file name or image number (e.g. `020.png`, `зн. 293`); with
  FamilySearch the scan link `…/ark:/61903/3:1:…` (keep the DGS in the
  workbook name or Примечания). For rows taken from an online index
  without opening the scan: the index link `…/ark:/61903/1:1:…` or
  `індекс: <collection>` — the scripts then label the row «лише індекс».
- Online-index workbooks may hold many years in one file; the scripts take
  each record's year from its date column.
- `Примечания`: why a reading was chosen ("фамилия подтверждается
  поручителем Иваном Лукиным Блахой"), scribe errors, duplicates
  ("спред продублирован на 004.png"), later marginal notes
  ("свидетельство выдано 1901 № 1002"), monthly totals check.
