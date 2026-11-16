# FamilySearch techniques that worked in practice

All of this runs in the person's own browser session (logged in), through
the site's normal pages. Do not read cookies or session tokens, do not
build Authorization headers, and do not call undocumented internal APIs
(`/service/...`, `/platform/...`, `filmdatainfo`, image-storage endpoints) —
not even from the page's JavaScript and not with `credentials: 'include'`.
Such calls are blocked by safety systems and would use the person's
credentials in a way they did not approve. Summaries of chats from
September–October 2026 still describe these calls as "tool knowledge"; they
are outdated and must not be copied.

Allowed page JavaScript: reading what the page shows (tables, links, the
image number field) and pressing the page's own buttons (e.g. «Следующий
снимок»), with waits — the same as a person clicking.

## Searching an indexed collection
- Use the search results page with URL parameters, e.g.
  `https://www.familysearch.org/search/record/results?q.surname=Дубинский&f.collectionId=3656669&count=100&offset=0`
  (add `q.givenName=`, `q.fatherGivenName=`, `q.residencePlace=`,
  `q.birthLikeDate.from=`/`to=`, and page with `offset=100, 200…`).
- Read each page with page-text / accessibility reads; save hits straight
  into an index workbook (`index_writer.py`, `Файл` = `індекс: <1:1: link>`)
  so the scripts can group families.
- Search spelling variants separately (Дубинский / Дубинская / Дубина /
  Дубенко); the index does not fold them.
- If results stop loading or the site limits requests, pause, reduce the
  number of pages, and record which queries were not completed.

## From an index hit to the scan
1. Open `https://www.familysearch.org/ark:/61903/1:1:<INDEX-ID>`.
2. Find the image link on the page (the "image" / «изображение» link,
   a `…/ark:/61903/3:1:…` URL) by reading the page's links.
3. Open that `3:1:` URL; zoom into the entry (double-click to zoom, then
   screenshot/zoom regions). Read the scan; never trust the index alone.

## Paging an unindexed film
- Film viewer: `https://www.familysearch.org/search/film/<DGS>?i=<n-1>`;
  the image-number field accepts a number + Enter; next/previous buttons
  step through images. Zoom with the viewer and screenshot regions.
- Split long ranges across several reader agents (e.g. 121–220, 221–320)
  and record exactly which images each one finished; browser
  connections drop.

## Catalog work
- `https://www.familysearch.org/search/catalog/<ID>` → list every item
  with ф.-оп.-спр., years, DGS. Make a table; mark each row
  "прочитано / переглянуто опис / не відкривали".
- Catalog titles can be wrong; check the first images (title page,
  internal опис) before relying on a title.
- The film's title card and even the archive's cover can carry the wrong
  year: 679-1-18 is labelled «1839» on both, but its first book is Borzna
  Troitska 1834. Trust the year written in the book's own headings and
  annual totals.
- A volume of metric books often holds several churches one after another;
  the archive cover may name only the first. Map the volume by the
  headings («Часть первая о родившихся…» and the church name) before
  concluding that a church is missing.
- A consistory volume of confession registers is ordered by protopopia,
  each parish starting with «Роспись…» at the top of a right-hand page;
  read the heading of every parish rather than guessing it from a
  neighbouring year (1763 «село C» was Стрільники).
- Many spreads are filmed twice; note duplicate image numbers so totals
  are not inflated.

## Attaching sources to the tree (only after the person approves)
- Attach an index record to a person:
  `https://www.familysearch.org/search/linker?ark=/ark:/61903/1:1:<RECORD-ID>&id=<PERSON-ID>`
- When adding a new relative from the attach screen, verify the
  relationship panel shows the expected parent IDs before saving.
- Name entry in Cyrillic: set the "Русский" name template first.
- FamilySearch "possible matches" often propose unrelated people from
  another region — compare place, spouse and dates before merging.
- Each attachment gets a reason text: what the record says and why it is
  this person (citing godparents/witnesses/household when used).

## Reading the tree without internal endpoints
- Person: `https://www.familysearch.org/tree/person/details/<PID>`;
  sources: `/tree/person/sources/<PID>`; family members are on the details
  page. Read them with page-text reads; expand a source to see its link,
  citation and reason.
- Sources whose link is the film's first image (the microfilm title card),
  a catalog page or the whole film are faulty — they look valid but do not
  show the record. Fix them by attaching the exact `3:1:` image.

## Index pages vs. images
- On the image viewer the index panel at the bottom lists indexed entries
  for that image; many 18th-century pages have no index or a partial one,
  and the index can mis-assign roles (a father indexed as the groom).
  Always read the image for the role of each person.
