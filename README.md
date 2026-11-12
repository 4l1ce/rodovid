# rodovid-agent — AI-асистент для пошуку предків в українських архівах

Плагін для Claude, який перетворює генеалогічне дослідження на керований
процес: від «де це взагалі може бути» до запису в дереві з джерелом і
рівнем достовірності. Зібраний із реальної роботи над родоводом Борзни і
Вибель (Чернігівщина): метрики 1880–1890-х, сповідні розписи 1763–1846,
ревізії 1850–1858, Румянцевський опис 1766–1767.

## Принципи

1. **Кожне твердження — до зображення.** Архів, ф.-оп.-спр., знімок, посилання.
2. **Індекс — це зачіпка, скан — це доказ.**
3. **Незалежна перевірка.** Ключові прочитання перечитує агент, який їх не робив.
4. **Рівні достовірності:** підтверджено / ймовірно / гіпотеза / не знайдено.
5. **Відсутність ≠ доказ відсутності,** доки не перевірено повноту джерела.
6. **Людина затверджує** кожну зміну в дереві й кожен запит до архіву.

## Склад

| Компонент | Що робить |
|---|---|
| skill `rodovid-case` | Оркеструє дослідження: питання → карта джерел → пошук → читання → перевірка → реєстр доказів → нотатка → дерево / архів. Містить 12 перевірених шаблонів міркувань |
| skill `source-map-ua` | Карта джерел: обласний архів за місцем пошуку (ДАЧО, ДАКО, ДАПО…), ЦДІАК, FamilySearch (DGS), що збереглося і що лише в архіві; прийоми роботи з FamilySearch |
| skill `metric-index-search` | Python-скрипти для xlsx-індексів метрик: пошук з варіантами прізвищ та імен, реконструкція родин, покриття, QA транскрипцій |
| skill `scan-transcribe` | Читання сканів (дореформена орфографія, кирилічні числа, стани), схема індексу, запис у xlsx |
| skill `evidence-ledger` | Реєстр доказів у xlsx з кольорами рівнів і перевірками |
| skill `familysearch-tree-sync` | Зміни в дереві FamilySearch лише з джерелом і за згодою |
| skill `archive-request` | Чернетка запиту до обласного архіву за місцем пошуку або до ЦДІАК |
| agent `source-scout` | Складає карту джерел по каталогах і описах |
| agent `scan-reader` | Читає блок зображень паралельно з іншими читачами |
| agent `evidence-verifier` | Сліпе перечитування і рев'ю висновків |

## Скрипти (Python 3 + openpyxl)

```
search_index.py   DIR --surname Третьяк [--mode exact|prefix|fuzzy] [--given] [--patronymic] [--role]
families.py       DIR --surname Бугай --mode prefix
coverage.py       DIR --kind birth
check_transcription.py "Борзнянський повіт 1890 рік метрики.xlsx"
index_writer.py   init|add FILE --sheet birth --from rows.json
ledger.py         init|add|set|summary FILE
```

Приклад: `families.py` по Третяках Борзни 1887–1892 за секунду збирає
20 родин із дітьми, смертями й хрещеними і сам підсвічує, що «Григорий» і
«Георгий Афанасьев Бугай» мають одну дружину — тобто, ймовірно, це одна
людина, записана двома формами імені.

## Встановлення

У Claude Code:

```
/plugin marketplace add 4l1ce/rodovid
/plugin install rodovid-agent@rodovid
```

Або завантажте файл `.plugin` у Claude і натисніть «Install». Для роботи з
FamilySearch потрібен ваш акаунт і браузер (Claude in Chrome або вбудований
браузер Claude). Паролі агент не вводить.

## Обмеження

- Читання рукописів AI помиляється — тому верифікатор і рівні достовірності.
- Багато фондів онлайн немає; плагін допомагає швидко це встановити і
  скласти точний запит до архіву.
- Живих людей не досліджуємо й не публікуємо.
- Детальні довідки про фонди (номери, каталоги, хмара) поки є лише для
  Чернігівщини (ДАЧО). Для інших областей агент сам визначає потрібний
  обласний архів і шукає його фонди й описи.

## Data handling

The plugin has no server of its own and sends nothing to the publisher.

**Personal data it reads and stores.** Names, dates, places and family
relationships of (overwhelmingly deceased) people from archival records;
for archive-request drafts, the user's own name and contact details. All
of it is stored only in files on the user's machine or project: xlsx
indexes and the evidence ledger, markdown case notes, and request drafts.
Living people are not researched or added to shared trees.

**External services it uses**, always through the user's own browser
(Claude in Chrome or Claude's built-in browser) and the sites' normal
pages. It never reads cookies or tokens, never calls internal APIs and
never enters passwords:

| Service | What is sent | When |
|---|---|---|
| FamilySearch (familysearch.org) | Search terms (names, places, years); page views of catalog items and images | Searching records and reading scans |
| FamilySearch Family Tree | People, relationships and source citations | Only after the user explicitly approves each change |
| Archive websites (the oblast state archive for the place, e.g. ДАЧО, ДАКО; ЦДІАК, ЦДІАЛ), Wikisource, Wikimedia Commons | Search terms and page views | Building the source inventory |

Archive requests are drafted only; the user sends them themselves.

Privacy: [PRIVACY.md](PRIVACY.md)

## Версії

Поточна версія — **0.5.1**: пошук в обласному архіві за місцем (не лише
ДАЧО), політика конфіденційності, встановлення з GitHub.

Повна історія змін — у [CHANGELOG.md](CHANGELOG.md).
