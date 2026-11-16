# Archives and online repositories (Ukraine, Russian Empire period)

## FamilySearch (familysearch.org) — the largest body of scans

- Free account required for images; use the person's own browser session
  (Claude in Chrome or the built-in browser). Never type their password.
- **Catalog** (`/search/catalog/<id>`): one entry per archive series. Each
  item lists archive reference (ф.-оп.-спр.), years, places and a **DGS
  number** (digital film). Write DGS numbers into every note.
- **Indexed collections** (searchable by name), e.g. «Украина, Чернигов,
  церковные записи» (collection 3656669), «Украина, Черниговские исповедные
  ведомости, 1620–1933». Indexes are partial and contain misreadings:
  an index hit is a lead, the scan is the evidence.
- **URL forms** (see familysearch-techniques.md):
  - index record `https://www.familysearch.org/ark:/61903/1:1:<ID>`
  - scan image `https://www.familysearch.org/ark:/61903/3:1:<ID>`
  - film viewer `https://www.familysearch.org/search/film/<DGS>?i=<image-1>`
- Most films are **not** indexed; reading them image by image is normal.

## Oblast state archives (ДАО) — choose by the place, not by habit

Parish registers, confession registers and revision lists of a governorate
are usually held by the **state archive of the oblast that covers the place
today**: ДАЧО for Chernihiv, ДАКО for Kyiv, ДАПО for Poltava, ДАХО for
Kharkiv, ДАЖО for Zhytomyr, ДАЛО for Lviv, and so on. Never assume ДАЧО:
it is only the archive of the worked example below.

- **Find the right archive.** Take the archive named in the FamilySearch
  catalog item for the place (the archive reference names it), and the
  list of oblast archives on the State Archival Service site
  (archives.gov.ua). Check border changes: a village of the old Chernihiv
  governorate may now be in Sumy oblast or in Russia; Kyiv governorate
  villages may now be in Cherkasy oblast; Galicia (Austrian until 1918)
  goes to ЦДІАЛ (Lviv) and the western oblast archives, with Greek
  Catholic, Roman Catholic and Jewish registers instead of consistory
  books.
- **What to look for on its website:** a catalog or list of metric books
  by church and year, scanned описи (finding aids), its own digitized
  cases, and its rules for requests and fees.
- **Fond numbers differ between archives.** The consistory, treasury
  chamber and district treasury fonds have different numbers in every
  oblast archive. Read them from that archive's опис or the FamilySearch
  catalog; do not reuse the Chernihiv numbers below for another region.
- If an archive has no online catalog, record that in the source map and
  plan an archive request (`archive-request` skill) rather than guessing.

## Worked example: ДАЧО — State Archive of Chernihiv Oblast

Use these facts only for places of the former Chernihiv governorate.

- Digital repository ("хмара"): `y2lmcmetyxjjaa.cg.gov.ua` — a folder
  listing behind **Cloudflare**: it opens only in the browser; WebFetch and
  shell downloads fail (checked 16.11.2026). Large images take 3–5 s.
  Folders:
  - `!_ОПИСИ` — scanned **описи** (finding aids). Typewritten описи have no
    text layer: search them by paging, not by Ctrl+F.
  - `!_СПРАВИ (оцифровані ДАЧО)` → `1_Давніх актів` (pre-1917 fonds, e.g.
    132, 152, 185, 679, 805) and `2_Нових актів` (Soviet fonds, e.g.
    Р-4609, Р-8840). **The archive's own scans** — many of these cases are
    neither on FamilySearch nor in Duck Inspector, so check this folder
    before writing «онлайн немає». File path pattern:
    `…/Фонд 132/Ф.132 Оп.2 Спр.348/Ф.132 Оп.2 Спр.348_00001.jpg`; some
    cases are named after the FamilySearch film
    (`804-03494474-l-a-w-152-1-154`).
  - `!_СПРАВИ (оцифровані ГТ Family search)` (and `… 2023-2026`) — copies of
    FamilySearch films, sorted by DGS.
  - «Каталог метричних книг» (which church, which year, which справа, and
    whether it survived), «Науково-довідковий апарат», ordering info.
  - The folder name is the only title; open the cover image before relying
    on it (152-1-154 turned out to be Березна, not Борзна).
- Key fonds for the Chernihiv governorate (Chernihiv only):
  - **ф. 679** Chernihiv Spiritual Consistory — metric books (оп. 10 for
    1880s–1910s of many districts; оп. 1, 4, 9, 14 older), confession
    registers (сповідні розписи), 1782 clergy revision (оп. 5).
  - **ф. 132** Treasury Chamber (казенна палата) — revision lists
    (ревізькі казки) 1795–1858 for the governorate, tax books.
  - **ф. 805** Borzna district treasury — revision lists of Borzna
    district 1816–1858; **ф. 805–820** series also includes volost
    administrations (check the опис).
  - **ф. 133** Noble deputies' assembly — noble genealogies only.
  - **ф. 185** — post-1861 lists of former serfs by landowner.
  - **ф. Р-8998** etc. — Soviet civil registry (ЗАГС) 1919–1930s.
  - **ф. Р-8840** (case files of the repressed, оп. 1–3) and **ф. Р-4609**
    (gubernia revolutionary tribunal, 1919–1922) — arrest files with a
    questionnaire that lists the family. Find the case number first in the
    regional volume of «Реабілітовані історією»; only part of the cases is
    in the cloud, the rest are ordered.
- Practical rule: open the **опис** (finding aid) before concluding that
  something is missing — FamilySearch catalog titles are sometimes wrong
  (e.g. Borzna Troitska "1887/1888" were in fact 1877/1878).

## ЦДІАК — Central State Historical Archive, Kyiv

- Online viewer: `archium.cdiak.archives.gov.ua` (search by fond/case or
  keyword; `file-viewer/<case>#file-<image>`). Some cases are digitized,
  many show only «Замовити» (order a copy). Many ЦДІАК cases are also on
  FamilySearch (image numbers usually match archium) and on Wikisource
  (`Архів:ЦДІАК/<fond>/<опис>/<case>`); check Duck Inspector before
  writing «лише в архіві».
- Case numbers with a letter use a **capital Cyrillic «А»** (127-1015-10А,
  127-1013-106А); with a lowercase or Latin letter, catalogs return «не
  знайдено».
- The viewer scales pages down; small 18th-century hands become partly
  illegible. Open the page image itself in its own browser tab and zoom
  regions there. Cite the case's «Зображення N» and the sheet (арк., Л/П).
  Several cases contain duplicate images (e.g. 366 = 367 in 57-1-4); note
  them so they are not counted as new pages.
- Key fonds for the Hetmanate and Left-Bank Ukraine:
  - **ф. 57** Rumyantsev Description of Little Russia 1765–1769
    (household-by-household census of Cossacks, peasants, burghers). Also
    on FamilySearch (e.g. DGS 109554258 for Borzna sotnia).
  - **ф. 127** Kyiv Spiritual Consistory — confession registers of the
    18th century (e.g. 127-1016-23 Borzna protopopia 1763).
  - **ф. 51** General Military Chancellery — petitions, court cases and
    lists of Cossacks by sotnia. **Опис 3 is largely online** (FamilySearch,
    archium, Wikisource): regimental revisions 1732–1755 (e.g. Chernihiv
    regiment 51-3-19364 for 1732 … 51-3-19356 for 1753–1755), the 1740
    compute (51-3-19252, 19253), oaths of 1732, 1741, 1762, money and hay
    registers, and court cases that name ordinary Cossacks. Not everything:
    e.g. 51-3-19328 (Chernihiv regiment 1747) and 51-3-4284 (Nizhyn 1732)
    have no online copy. The опис is on НашіПредки (incomplete list) and
    Wikisource. Revisions are written sotnia by sotnia; find the sotnia's
    heading first (record-types, «Hetmanate Cossack lists»).
  - **ф. 1539** — 1782 revision of Cossacks (published copies on
    Wikimedia Commons / Wikisource for some districts).

## Duck Inspector — where a case is online, by reference code

`inspector.duckarchive.com` is a volunteer index of online copies
(FamilySearch, archium, Wikisource/Commons) by archive reference. It holds
no scans and indexes no people. Run every reference in a source map through
it before marking a case «лише в архіві» — on 15.11.2026 it found online a
case the project had been about to order (ЦДІАК 51-3-2422).

- Case page: `inspector.duckarchive.com/en/archives/<archive>/<fond>/<опис>/<case>`,
  e.g. `/ЦДІАК/51/3/2422`. Search → Reference code (archive, fond, опис,
  case). Archive codes: ЦДІАК, ДАЧгО (Chernihiv), ДАКО, ДАЧкО (Cherkasy),
  ЦДІАЛ, etc.
- Public JSON for batch checks, no login:
  `/api/catalog/<archive>/<fond>/<опис>/<case>` (field `online_copies`).
  It is a public catalog, not a site's internal endpoint — read it with
  WebFetch, never with the person's browser session. Pause ~2 s between
  requests; after ~60 in a row it answers 429.
- Limits — do not draw conclusions from them:
  - **No online copy listed ≠ not online.** Several ДАЧО cases on
    FamilySearch (e.g. 132-2-113, 132-2-60) show no copy there; the ДАЧО
    cloud's own scans are not covered at all.
  - For ДАЧО ф. 679 the case title is only the **first church** of the case
    (679-1-12, «Берестовець», also holds Borzna city 1824). A title that
    names another village does not rule out your parish.
  - Title search is fuzzy; only the case title is searchable.
  - Large описи are served partially (ЦДІАК 51-3: first 5000 cases), so
    paging an опис there is not a complete inventory.

## Printed editions and volunteer transcriptions

Check for a published transcription before reading an early register or
census from the scan. Local historians publish whole metric books and
confession registers with surname indexes (e.g. «Метрична книга села Виблі
1725–1740 роки», упор. С. Горобець, 2017, full text on
siver-litopys-library.cn.ua). Search the village name with «метрична
книга», «сповідні розписи», «ревізія», «присяга», «переписна книга» in
library catalogues (resource.history.org.ua, oblast universal scientific
libraries, er.kai.edu.ua) and booksellers.

- Use an edition as a **finding aid and independent reading**: it gives
  record numbers to open on the scan and a second reading not made by a
  model. A text extracted automatically from a site is not a reading by
  eye — check quotes against the scan before they go into the tree.
- A case number in an edition can differ from the catalogue (the Vybli
  edition gives 127-1012-181, the catalogue 127-1012-85); record both
  until the cover is checked.
- **Forum transcriptions** (genoua.name, forum.vgd.ru — «вичитки»): good
  leads with exact references, but they are one human reading, often
  partial. Treat them like index rows: open the scan for anything a
  conclusion rests on.

## Other online sources

- **Wikimedia Commons / Wikisource (uk)**: scanned revision tales of
  ДАКО (Kyiv oblast archive, ф. 280) and some 1782 Chernihiv revisions;
  Wikisource has tables of contents (villages → page numbers).
- **Інститут історії України** (resource.history.org.ua): published
  sources, e.g. «Генеральне слідство про маєтності Ніжинського полку
  1729–1730» (Василенко, 1901) — estates, not rank-and-file names.
- **ДАКО** (Kyiv oblast) — revision lists for Kyiv governorate villages
  (Cherkasy region before 1932).
- **WWI**: gwar.mil.ru — casualty cards, loss lists (birthplace given).
- **WWII**: pamyat-naroda.ru, obd-memorial.ru, podvignaroda.ru,
  memory-book.com.ua, Arolsen Archives (forced labour).

## Access notes for the agent

- Sandboxed shells usually cannot download from these hosts; read
  scans through the browser (screenshots + zoom) or WebFetch where an
  image URL is public.
- Record every location as: archive, ф.-оп.-спр., арк./image number,
  DGS (if FamilySearch), direct link. A finding without a location is
  not usable.
