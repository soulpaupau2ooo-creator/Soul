# soulbekbot — Mustaqil Ishni Haqiqiy .docx Faylga Aylantirish

> **Muammo:** Hozir bot mustaqil ishni chat ichida matn sifatida yozib beryapti — shuning uchun formatlash, chegaralar, titul varaq, mundarija yo'q va natija "g'alati" chiqadi.
>
> **Yechim:** Har bir mustaqil ish so'rovi — universitet standarti bo'yicha to'liq formatlangan, chegaralari santimetrda aniq belgilangan, haqiqiy Microsoft Word (.docx) fayl bo'lib, Telegram orqali fayl sifatida yuborilishi kerak. Kompyuterda Word/LibreOffice, telefonda esa Telegram ichidagi yoki tashqi Word/WPS ilovasi orqali o'zi ochilishi kerak.
>
> **Qanday ishlatiladi:** Promptlarni ketma-ket, natijani tasdiqlab borib qo'ying. PROMPT 2 — asosiy og'irlik markazi.

---

## PROMPT 1 — Hozirgi holatni audit qilish

```
Read the ENTIRE soulbekbot codebase before answering. Find the feature that
generates "mustaqil ish" (academic coursework paper). It may be referenced in
git history as "academic essay" or similar.

Report on:

1. Where is the handler? What triggers it (a command, a button, free text)?
2. What does the user currently receive — raw text in chat, a plain .txt file,
   or something else? Confirm by tracing the actual send call.
3. What input does the bot currently collect from the user before generating
   (topic only? subject, student name, university, group)? List exactly what
   is asked versus what a real mustaqil ish title page requires (see PROMPT 2).
4. Is there ANY document-generation library already imported anywhere in the
   codebase (python-docx, docxtpl, docx2pdf, anything)? List versions.
5. Generate one sample output with the CURRENT code for the topic
   "Raqamli iqtisodiyotning O'zbekistonda rivojlanish istiqbollari" and save it,
   so we have a documented "before" baseline.

Write findings to docs/MUSTAQIL_ISH_AUDIT.md. List exactly what is missing to
turn this into a properly formatted Word document.
```

---

## PROMPT 2 — Docx generatsiya dvigateli (formatlash yadrosi)

```
Build a dedicated Word document generator for Uzbek academic coursework papers
("mustaqil ish"). Create it as a standalone module: `docgen/mustaqil_ish.py`.

Use python-docx as the base library. Research current best practice for
generating a Word document with a Table of Contents field that auto-updates
when opened in Word — python-docx cannot compute page numbers itself, so you
must insert a real TOC field code (the same one Word's Insert > Table of
Contents produces), not a fake static list. Verify this works by opening the
output in a real Word/LibreOffice render, not just by reading the XML.

=== DOCUMENT SPECIFICATION ===
Implement these as named constants in a config section at the top of the file,
NOT hardcoded inline, so a university's specific requirements can be changed
in one place:

PAGE SETUP
- Paper size: A4 (21.0 cm x 29.7 cm)
- Margins (O'zbekiston OTM standart uslubi, sozlanadigan qildiring):
  - Chap chegara (left):   3.0 cm
  - O'ng chegara (right):  1.5 cm
  - Yuqori chegara (top):  2.0 cm
  - Pastki chegara (bottom): 2.0 cm
- Make every value a Cm() constant that can be overridden per-university via
  a config dict, since some universities require 2.5/1.0/2.0/2.0.

TYPOGRAPHY
- Asosiy matn shrifti: Times New Roman, 14 pt
- Sarlavhalar (bob nomlari): Times New Roman, 14-16 pt, Bold, markazda
- Qism sarlavhalari (paragraf/bo'lim): Times New Roman, 14 pt, Bold, chap
  tomonda yoki markazda (universitet talabiga qarab sozlanadigan)
- Qator oralig'i (line spacing): 1.5
- Birinchi qator chekinishi (first-line indent): 1.25 cm on every body
  paragraph
- Matn tekislash: justified (ikki tomonlama tekislash), sarlavhalar bundan
  mustasno
- Paragraflar orasida qo'shimcha bo'sh joy yo'q (space-before/after = 0) —
  ajratish faqat qator oralig'i va chekinish orqali, Word odatidagi kabi

TITLE PAGE (titul varaq) — alohida sahifa, raqamlanmaydi lekin hisoblanadi
Fields, centered, in this vertical order:
1. Universitet nomi (bold, upper case, top)
2. Fakultet nomi
3. Kafedra nomi
(blank space)
4. "MUSTAQIL ISH" (bold, larger size, centered, middle of page)
5. Fan nomi: "___________"
6. Mavzu: "___________"
(blank space, right-aligned block near bottom)
7. Bajardi: talaba F.I.Sh., guruh
8. Tekshirdi: o'qituvchi F.I.Sh., unvon
(bottom, centered)
9. Shahar nomi, yil

All these must be REAL user-provided values, never placeholder text left in
the output. If a value is missing, the bot must ask for it before generating
(see PROMPT 3) — never ship a document with literal "___________" in it.

STRUCTURE AFTER THE TITLE PAGE
1. Mundarija (Table of Contents) — real auto-updating TOC field, own page.
2. Kirish (Introduction) — own page, starts numbering from here or from title
   page per config (make this a toggle: "raqamlash titul varaqdan boshlanadi
   va yashiriladi" is the common convention — verify and implement correctly).
3. Asosiy qism — divided into numbered sections/subsections using Word's
   real Heading 1 / Heading 2 styles (not manually bolded text), so the TOC
   field can actually pick them up automatically.
4. Xulosa (Conclusion) — own page.
5. Foydalanilgan adabiyotlar (References) — own page, numbered list, each
   entry formatted as: "1. Muallif F.I.Sh. Kitob nomi. -- Shahar: Nashriyot,
   yil. -- B. sahifalar." Support books, articles, and websites with distinct
   citation shapes.

PAGE NUMBERS
- Bottom center or bottom right (make configurable), Arial or Times New Roman
  10-12pt.
- Title page: number is suppressed but counted (page 1 exists with no visible
  number; content starts appearing as "2" on the next page). Implement this
  with python-docx section breaks and "different first page" header/footer
  settings — verify it actually renders this way in real Word, not just in
  the XML.

HEADERS/FOOTERS
- No running header unless the university requires one (config flag, off by
  default).

=== VALIDATION ===
After generating, programmatically re-open the produced .docx and assert:
- Section margins equal the configured Cm() values exactly.
- Font name and size on a body paragraph run match spec.
- Line spacing value matches 1.5.
- First-line indent matches 1.25 cm.
- The TOC field code is present (not a static list).
- No placeholder text ("___________", "Lorem ipsum", "TODO") remains anywhere
  in the final document -- grep the extracted text and fail loudly if found.

Write at least 20 unit tests covering: default config, an overridden
university config, a paper with only 2 sections, a paper with 8 sections and
subsections, a references list mixing books/articles/websites, and a missing
required field (must raise a clear error, not silently produce a broken doc).

Generate one real sample with realistic O'zbek content for the topic
"Raqamli iqtisodiyotning O'zbekistonda rivojlanish istiqbollari" and save it
to docs/samples/. Open it yourself (via a Word-compatible viewer / LibreOffice
headless conversion to PDF) and take a screenshot of the title page and one
content page so I can visually confirm the layout before we go further.
```

---

## PROMPT 3 — Foydalanuvchidan ma'lumot yig'ish oqimi

```
Build the conversation flow that collects everything the document needs BEFORE
generation starts, so PROMPT 2's engine never has to guess or leave a blank.

Required fields, collect in this order, one question at a time (or grouped if
the bot's UI supports a form-like multi-step message):

1. Mavzu (topic) -- free text
2. Fan nomi (subject) -- free text
3. Universitet nomi -- free text, but remember the last one used per user so
   returning users are not asked again; offer "oldingi: <name> ishlataman?"
4. Fakultet va kafedra nomi -- free text, same remember-per-user behaviour
5. Talabaning F.I.Sh. va guruhi -- free text, remember per user
6. O'qituvchi F.I.Sh. -- free text, optional, remember per user
7. Shahar va yil -- default to the bot's config city and current year, let the
   user override
8. Taxminiy hajm -- necha bet / necha bo'lim (offer quick-reply buttons: Qisqa
   (5-7 bet), O'rtacha (10-15 bet), Kengaytirilgan (20+ bet))

After collecting, show a short confirmation summary in chat and ask
"Tasdiqlaysizmi?" before spending time generating. Only then call the content
generator and the docx engine from PROMPT 2.

Store the per-user remembered fields (university, faculty, student name,
group, teacher) in whatever persistence this bot already uses, so the next
mustaqil ish for the same user needs only the topic and subject.

Add a way to edit a remembered field: "/malumotlarim" command shows current
saved values with buttons to update each one.
```

---

## PROMPT 4 — Mazmun generatsiyasi (kirish, asosiy qism, xulosa)

```
Build the content generation step that produces the actual academic text
before it is placed into the docx engine from PROMPT 2. Keep this SEPARATE
from the docx formatting module -- content generation and document formatting
must not be entangled in one function.

Requirements:
- Generate real, coherent, on-topic Uzbek academic prose for kirish, 3-5
  bo'lim of the asosiy qism (with meaningful subheadings derived from the
  topic, not generic "1-bo'lim, 2-bo'lim"), and xulosa.
- Length must scale to the "taxminiy hajm" choice from PROMPT 3.
- Kirish must state: mavzuning dolzarbligi, ishning maqsadi, vazifalari.
- Xulosa must summarize findings and never just repeat kirish verbatim.
- Generate a references list of 5-10 plausible academic-style sources
  appropriate to the topic's field. Flag clearly in the code (not to the user)
  that these are model-generated and the user should verify them before
  academic submission -- do not present fabricated sources as verified facts.
- Run the output through the uzbek_normalizer text-cleanup stages if that
  module already exists in this codebase (strip stray markdown, fix
  apostrophes) before it reaches the docx engine, since Word does not want
  markdown syntax appearing as literal characters.
- Return content as a structured object (list of sections, each with a
  heading and paragraphs) -- never as one giant string -- because PROMPT 2's
  engine needs structure to apply Heading 1/2 styles correctly.

Test with three different topics from different fields (iqtisodiyot, tibbiyot,
IT) and confirm the structure object is well-formed for each before it is
ever passed to the docx engine.
```

---

## PROMPT 5 — Telegram orqali fayl sifatida yuborish (kompyuter va telefon)

```
Fix the delivery so the generated mustaqil ish is ALWAYS sent as a real
document, never as chat text, and opens correctly on both desktop Telegram
and mobile Telegram.

Requirements:

1. SEND METHOD
   - Use sendDocument, never send the content as a text message.
   - Set the filename explicitly and meaningfully: sanitize the topic into a
     filesystem-safe name, e.g. "Raqamli_iqtisodiyot_mustaqil_ish.docx".
     Never send as a generic name like "output.docx" or a random UUID.
   - Set the correct MIME type explicitly:
     application/vnd.openxmlformats-officedocument.wordprocessingml.document
   - Verify the library you use for sending actually sets this MIME type --
     some Telegram wrapper libraries infer it from the extension, others need
     it passed explicitly. Check the actual HTTP request if unsure.

2. WHY "IT DOESN'T OPEN ON PHONE" HAPPENS -- verify and fix
   Common causes, check each on THIS codebase:
   - The file bytes are corrupted because it was read/written in text mode
     somewhere in the pipeline instead of binary mode. Grep for any open()
     call touching the docx path and confirm every one uses "rb"/"wb".
   - The file was sent as a base64 string inside a JSON/text response instead
     of as an actual multipart file upload. Confirm the real HTTP request
     Telegram receives is multipart/form-data with the file as bytes.
   - The extension is missing or wrong by the time Telegram names it.
   - A temp file was deleted before the upload finished (race condition) --
     confirm the send call fully completes (await/blocks) before any cleanup.

3. CAPTION
   - Send a short caption with the document: mavzu nomi, fan, va necha bet.
   - Add a message like "Mustaqil ish tayyor. Word faylini oching va
     tekshiring." so the user knows what to expect.

4. FALLBACK
   - If sendDocument fails (file too large, network error), tell the user
     clearly in Uzbek and offer to retry -- never fall back to dumping the
     content as plain chat text, since that defeats the entire point of
     this fix.

5. VERIFY ON BOTH PLATFORMS
   - Send a real test file through the bot to a real Telegram account.
   - Confirm and screenshot: on Telegram Desktop, the file appears as a
     document card and opens in Word/LibreOffice/the OS default app on click.
   - Confirm and screenshot: on Telegram mobile (iOS or Android), tapping the
     file opens it in Telegram's built-in previewer or hands off correctly to
     Word/Google Docs/WPS Office if installed. If the phone has no Word-
     compatible app installed at all, Telegram will offer a "share/open with"
     picker -- this is expected phone behaviour, not a bug in our file; confirm
     the file itself is valid by opening it successfully in at least one app.
   - If a real device is not available in this environment, at minimum
     validate the file with a headless docx-to-pdf conversion (e.g. via
     LibreOffice --headless) to prove the file is not corrupted, and state
     clearly that on-device confirmation still needs to happen.
```

---

## PROMPT 6 — Sifat darvozasi (yakuniy tasdiqlash)

```
Final quality gate for the mustaqil ish feature. Not done until every item
below is demonstrated with evidence.

CONTENT
[ ] Title page has zero placeholder text -- grep confirms it.
[ ] TOC field is a real auto-updating field, verified by opening in a real
    Word-compatible renderer and checking it lists all headings with correct
    page numbers after "update field".
[ ] Kirish, asosiy qism (with real subheadings), xulosa, and references all
    present and on-topic for at least 3 different test topics.

FORMATTING (measure, don't eyeball)
[ ] Margins exactly match config in cm -- paste the measured values.
[ ] Font is Times New Roman 14pt on body text -- paste the measured run
    properties.
[ ] Line spacing is 1.5 -- paste the measured value.
[ ] First-line indent is 1.25cm on body paragraphs -- paste the measured
    value.
[ ] Title page number is suppressed but page count is correct.

DELIVERY
[ ] File arrives via sendDocument, not as chat text -- confirm from the code
    path, not assumption.
[ ] Filename is meaningful and filesystem-safe.
[ ] MIME type is the correct Word MIME type -- show the actual outgoing
    request.
[ ] Opens successfully in at least one real renderer (Word, LibreOffice, or
    headless conversion proving non-corruption).
[ ] Desktop Telegram screenshot showing the document card.
[ ] Mobile Telegram screenshot showing successful open or share-sheet
    handoff.

ROBUSTNESS
[ ] Missing required field during collection produces a clear Uzbek prompt to
    fill it in, never a broken document.
[ ] Returning user's remembered fields (university, student name, etc.)
    persist across a bot restart.
[ ] Full test suite (docgen + content + delivery) passes -- paste the
    summary.

Any unticked box is BLOCKED, not done. Report honestly, with evidence for
every ticked box.
```

---

## Eslatma

- **PROMPT 2 dagi sm qiymatlari** -- bu O'zbekistondagi eng ko'p tarqalgan standart (chap 3sm, o'ng 1.5sm, yuqori-pastki 2sm). Agar sizning universitetingiz boshqacha talab qilsa (masalan chap 2.5sm), config'dagi bitta joyni o'zgartirish kifoya -- kodni qayta yozish shart emas.
- **"Telefonda ochilmaydi" muammosi** ko'pincha formatlashda emas, balki fayl **qanday yuborilishida** bo'ladi (matn sifatida, noto'g'ri MIME bilan, yoki binary/text mode xatosi). PROMPT 5 shu sabablarni birma-bir tekshiradi.
- Agent sizga har bosqichda **skrinshot va o'lchangan qiymatlarni** ko'rsatishi shart -- "should work" emas, isbot bilan.
