# soulbekbot — O'zbekcha TTS ni Eng Yuqori Darajaga Chiqarish

> **Qanday ishlatiladi:** Har bir PROMPT ni Antigravity chatiga ketma-ket qo'ying. Bittasi tugab, siz natijani tasdiqlamaguningizcha keyingisiga o'tmang.
>
> **Muhim:** 2-PROMPT (normalizatsiya) — eng katta ta'sir beradigan qadam. Uni tashlab ketmang. Provayderni almashtirib, normalizatsiyasiz qoldirsangiz, ovoz baribir yomon chiqadi.

---

## PROMPT 1 — Hozirgi holatni to'liq audit qilish

```
Read the ENTIRE soulbekbot codebase before answering. Do not guess — open the files.

I need a complete audit of the text-to-speech pipeline. Trace the full path a
message takes from the moment the user presses the "listen / tinglash" button
until the audio arrives in Telegram.

Report on:

1. ENTRY POINT
   - Which handler catches the listen/TTS button? File and line.
   - What exact text object is passed in? Is it raw model output, markdown,
     HTML, or already cleaned?

2. TEXT PREPARATION
   - List every transformation applied to the text before it reaches the TTS
     call. If there is none, say so explicitly.
   - Is there any handling for: apostrophes, numbers, dates, percentages,
     currency, abbreviations, URLs, emoji, markdown, code blocks, Cyrillic,
     English words? Check each one and mark present/absent.

3. TTS CALL
   - Which library and version? Which voice string? Which rate/pitch/volume
     parameters, if any?
   - Is there any chunking for long text? What is the length limit before it
     breaks or truncates?
   - What happens on network failure or rate limit? Is there a retry or a
     fallback voice?

4. AUDIO HANDLING
   - Output format, sample rate, channels, bitrate.
   - Is ffmpeg or pydub used at all? Any loudness normalization? Any silence
     trimming?
   - Which Telegram method sends it: sendVoice, sendAudio, or sendDocument?

5. PERFORMANCE
   - Is there any caching of generated audio? How long does one 500-character
     request take end to end? Measure it, don't estimate.

6. FAILURE EVIDENCE
   - Generate audio for these three test strings with the CURRENT code and save
     them, so we have a "before" baseline:
     a) "2024-yilda O'zbekiston iqtisodiyoti 6,5% ga o'sdi va YaIM 112,5 mlrd
        dollarni tashkil etdi."
     b) "Salom! Bugun soat 14:30 da uchrashamiz. Manzil: Toshkent sh.,
        Amir Temur ko'chasi, 108-uy."
     c) "Google va YouTube kabi platformalar AQShda, BMT hisobotiga ko'ra,
        eng ko'p ishlatiladi. Narxi 1 500 000 so'm."

Write the audit to docs/TTS_AUDIT.md. Then list the top 5 defects in priority
order, with your estimate of how much each one degrades quality.
```

**Nima uchun:** Avval nima buzilganini bilmasdan tuzatib bo'lmaydi. Bu uchta test jumlasi — O'zbek TTS ni sindiradigan hamma narsani o'z ichiga oladi.

---

## PROMPT 2 — O'zbek matn normalizatsiya dvigateli (ENG MUHIM QADAM)

```
Build a dedicated Uzbek text normalization engine for TTS. Create it as a
standalone, fully tested module: `tts/uzbek_normalizer.py`.

This is the highest-impact component in the pipeline. Treat it as a first-class
module, not a helper function. It must be pure (no I/O), deterministic, and
covered by unit tests.

=== REQUIREMENTS ===

STAGE 1 — Cleanup
- Strip markdown: **bold**, *italic*, `code`, ```code blocks```, # headings,
  > quotes, tables, [text](url) → keep only "text".
- Remove or convert emoji. Default: remove. Make it configurable.
- URLs → replace with the word "havola". Email → "elektron pochta manzili".
- Collapse repeated whitespace and repeated punctuation (!!!, ???, ...).
- Remove zero-width characters, soft hyphens, and other invisible unicode.

STAGE 2 — Apostrophe normalization (CRITICAL for Uzbek)
Uzbek Latin uses two distinct characters that are constantly typed wrong:
- Oʻ / Gʻ use U+02BB (MODIFIER LETTER TURNED COMMA)
- The tutuq belgisi uses U+02BC (MODIFIER LETTER APOSTROPHE)
People type ' (U+0027), ` (U+0060), ' (U+2018), ' (U+2019), ´ (U+00B4) instead.
Wrong characters make the engine mispronounce or spell out the word.

Rules:
- After o/O and g/G → normalize to U+02BB.
- Everywhere else → normalize to U+02BC.
- Test that "O'zbekiston", "O`zbekiston", "O'zbekiston", "Oʻzbekiston" all
  produce identical output.
- IMPORTANT: verify empirically which form the TTS engine actually pronounces
  best. Generate all four variants and compare. If the engine prefers plain
  ASCII, invert the rule. Report what you found — do not assume.

STAGE 3 — Script handling
- Detect Cyrillic Uzbek text. If found, transliterate to Latin using a correct
  Uzbek table (Ў→Oʻ, Ғ→Gʻ, Ҳ→H, Х→X, Қ→Q, Ч→Ch, Ш→Sh, Ё→Yo, Ю→Yu, Я→Ya, Ъ→ʼ).
- Mixed-script sentences must be unified, not left mixed.

STAGE 4 — Numbers → Uzbek words
This is where most of the damage happens. Implement a real number-to-words
converter for Uzbek, not a lookup table.

- Cardinals: 0-999 999 999 999. 
  1→bir, 11→oʻn bir, 25→yigirma besh, 100→yuz, 1000→ming,
  1 000 000→million, 1 000 000 000→milliard.
- Ordinals: the "-inchi" suffix with correct allomorphs.
  1-→birinchi, 2-→ikkinchi, 3-→uchinchi, 4-→toʻrtinchi, 5-→beshinchi,
  6-→oltinchi, 7-→yettinchi, 8-→sakkizinchi, 9-→toʻqqizinchi, 10-→oʻninchi,
  20-→yigirmanchi, 100-→yuzinchi, 1000-→minginchi.
- Years: "2024-yil" → "ikki ming yigirma toʻrtinchi yil".
  "1991-yilda" → "bir ming toʻqqiz yuz toqsan birinchi yilda" (preserve the
  case suffix -da/-dan/-ga).
- Decimals: "6,5" and "6.5" → "olti butun oʻndan besh". Also accept the simpler
  "olti nuqta besh" as a configurable mode.
- Thousands separators: "1 500 000", "1,500,000", "1.500.000" must all parse.
- Percent: "25%" → "yigirma besh foiz".
- Currency: "5000 soʻm" → "besh ming soʻm"; "$100" → "yuz dollar";
  "€50" → "ellik yevro"; "100 000 UZS" → "yuz ming soʻm".
- Time: "14:30" → "oʻn toʻrtinchi yarim" is WRONG. Use "soat oʻn toʻrt nol
  oʻttiz" or "oʻn toʻrtdan oʻttiz daqiqa oʻtdi". Pick one, be consistent.
- Dates: "12.05.2024" and "12/05/2024" → "ikki ming yigirma toʻrtinchi yil
  oʻn ikkinchi may". Handle month names.
- Phone numbers, card numbers, long digit runs → read digit by digit.
- Ranges: "5-10" → "beshdan oʻngacha". Do not read the hyphen as minus.
- Negative numbers: "-5" → "minus besh".

STAGE 5 — Abbreviations and units
- Expand: km→kilometr, m→metr, sm→santimetr, kg→kilogramm, g→gramm,
  l→litr, mlrd→milliard, mln→million, ming→ming, soat→soat, daq→daqiqa,
  sek→sekund, °C→gradus selsiy, ‰→promille.
- Common Uzbek abbreviations: "va h.k."→"va hokazo", "sh."→"shahri",
  "ko'ch."→"koʻchasi", "t."→"tuman", "y."→"yil", "masalan"→leave as is.
- Acronyms read letter by letter using UZBEK letter names, not English:
  BMT, AQSh, MDH, YaIM, OAV, JSSV. Build an explicit map for the common ones
  and a fallback that spells unknown all-caps sequences with Uzbek letter names.
- CRITICAL: an acronym must never be read as English letters. "AQSh" must not
  become "ay-kyu-es-eych".

STAGE 6 — Foreign words
- Build a respelling dictionary for high-frequency foreign words so the Uzbek
  voice pronounces them acceptably:
  Google→Gugl, YouTube→Yutub, Telegram→Telegram, Instagram→Instagram,
  Facebook→Feysbuk, WhatsApp→Votsap, iPhone→Ayfon, Android→Android,
  Windows→Vindovs, Microsoft→Maykrosoft, ChatGPT→Chat Ji-Pi-Ti,
  AI→sunʼiy intellekt, IT→aylti, USD→dollar, email→elektron pochta.
- Make this dictionary a data file (JSON/YAML), not hardcoded, so it can grow.
- Any Latin word with a letter combination impossible in Uzbek orthography
  should be flagged for the dictionary — log these so we can expand the list.

STAGE 7 — Prosody preparation
- Sentence splitting that is abbreviation-aware (do not split on "sh." or "1.").
- Ensure every sentence ends with terminal punctuation so the engine applies
  a falling intonation.
- Insert short pause markers at commas, longer at sentence ends, longest at
  paragraph breaks. Represent them in whatever the chosen engine supports
  (SSML <break>, or a comma/period insertion for engines without SSML).
- Break sentences longer than ~200 characters at natural clause boundaries —
  long sentences are where TTS prosody collapses.

=== TESTING REQUIREMENT ===
Write at least 80 unit tests. Every rule above needs a test. Include these
adversarial cases:
- "2024-yilda 6,5% o'sish, ya'ni 1 500 000 so'm."
- "O`zbekiston Respublikasi Prezidenti 12.05.2024 yilda BMT da so'zladi."
- "Soat 09:05 da 3-uyga boring. Tel: +998901234567"
- "**Muhim:** [havola](https://example.com) — 25 °C, 10-15 km."
- Mixed Cyrillic: "Ўзбекистон 2024-yilda"
- Empty string, only emoji, only numbers, 5000-character text.

Tests must assert exact output strings. Run them. Show me the output of the
three baseline sentences from PROMPT 1, before and after normalization,
side by side.

Do not integrate this into the bot yet. Module + tests only.
```

**Nima uchun:** Bu modul tayyor bo'lsa, siz hech qanday provayderni almashtirmasdan ham ovoz sifatini keskin oshirasiz. Va u provayderdan mustaqil — keyin qaysi dvigatelga o'tsangiz ham ishlaydi.

---

## PROMPT 3 — Provayderlarni real solishtirish (A/B benchmark)

```
Build a benchmark harness that generates the SAME normalized Uzbek text through
every available TTS provider, so I can listen and choose with my own ears.

Create `tools/tts_benchmark.py`.

=== CANDIDATES TO EVALUATE ===
Research each one's CURRENT Uzbek support before coding — availability changes,
so verify against live docs, do not rely on your training data. For each,
report: does it support Uzbek, which voices, what does it cost, what is the
latency, does it support SSML, does it allow a custom pronunciation lexicon.

1. edge-tts (current)      — voices: run `edge-tts --list-voices | grep -i uz`
                             and report ALL Uzbek voices found, not just Madina.
2. Azure Speech Service    — same underlying voices as edge-tts BUT with full
                             SSML, custom lexicons, and prosody control. This is
                             likely the cheapest big win: same voice, far more
                             control. Prioritise checking this.
3. Google Cloud TTS        — check whether uz-UZ voices exist, including any
                             high-fidelity tier.
4. Gemini TTS API          — check current language coverage for Uzbek.
5. ElevenLabs              — check which model tier covers Uzbek, if any.
6. Yandex SpeechKit        — historically has Uzbek voices. Verify.
7. Mohir.ai                — an Uzbekistan-based speech API specialising in
                             Uzbek. Check their TTS offering and quality.
8. Meta MMS-TTS (uzb)      — open source, self-hostable, free. Check quality.
9. Piper / Coqui / XTTS    — check for any Uzbek voice or fine-tune.

=== HARNESS REQUIREMENTS ===
- One config file listing providers and credentials (env vars, never hardcoded).
- A fixed test corpus of 10 Uzbek sentences covering: plain prose, numbers,
  dates, acronyms, foreign words, a long paragraph, a question, an exclamation,
  a list, and a technical passage.
- For each provider × each sentence, generate audio into
  `benchmark_output/<provider>/<voice>/<id>.mp3`.
- Measure and log: generation latency, output size, failure rate over 3 runs.
- Generate `benchmark_output/index.html` — a simple local page with every clip
  playable side by side, grouped by sentence so I can A/B the same sentence
  across providers in one click. Include a scoring form (1-5) per clip.
- Handle missing credentials gracefully: skip that provider, note it in the
  report, do not crash.

=== REPORT ===
Write `docs/TTS_BENCHMARK.md` with a comparison table:
provider | Uzbek voices | SSML | custom lexicon | latency | cost per 1M chars |
free tier | stability | verdict.

Then give me your top 3 recommendations with reasoning, and state clearly what
you could NOT verify. You cannot hear audio — so rank on capability and
measurable metrics, and leave the final quality judgement to me.

Open the HTML page in the browser and screenshot it so I can confirm it works.
```

**Nima uchun:** Men ham, agent ham ovozni eshita olmaydi. Yagona to'g'ri usul — hammasini generatsiya qilib, **siz** eshitib tanlashingiz. Taxmin qilish emas.

---

## PROMPT 4 — Tanlangan provayderni ishlab chiqarish darajasida ulash

> Bu promptni benchmark natijasini eshitib, provayderni tanlaganingizdan **keyin** qo'ying. `<PROVIDER>` va `<VOICE>` joyiga o'zingiz tanlaganini yozing.

```
I chose <PROVIDER> with voice <VOICE>. Build the production TTS service.

Create `tts/service.py` as the single entry point. Nothing else in the codebase
may call a TTS library directly — everything goes through this service.

=== ARCHITECTURE ===
- A provider interface (abstract base) with one method: synthesize(text, opts)
  → audio bytes + metadata.
- Concrete adapters for the primary provider and at least one fallback.
- A fallback CHAIN: primary → secondary → edge-tts as last resort. Each failure
  is logged with the reason. The user must never see a hard error if any
  provider in the chain can serve them.
- Circuit breaker: if the primary fails N times in M minutes, skip straight to
  the fallback for a cooldown period instead of waiting for timeouts.
- Timeouts on every network call. No unbounded waits.

=== PIPELINE ORDER (enforce exactly this) ===
1. Input validation and length limit.
2. uzbek_normalizer (from PROMPT 2).
3. Cache lookup (see below).
4. Chunking if needed.
5. Synthesis per chunk, with retry and exponential backoff.
6. Chunk concatenation with correct pause between chunks.
7. Audio post-processing (see PROMPT 5).
8. Cache store.
9. Return.

=== CHUNKING ===
- Determine the provider's real per-request limit empirically and document it.
- Split at sentence boundaries, never mid-word, never mid-number.
- Keep chunks well under the limit with a safety margin.
- Concatenate with a natural pause, not a hard cut. Verify there is no audible
  click or gap discontinuity at the seams — this is the most common defect in
  chunked TTS.

=== PROSODY TUNING ===
- If the provider supports SSML, use it: sentence-level <break>, <prosody> for
  rate and pitch, <say-as> for numbers and dates that the normalizer chose to
  leave as digits, and <phoneme> or a custom lexicon for words that remain
  mispronounced.
- Build a pronunciation lexicon file for Uzbek words the engine gets wrong.
  Start it with anything the benchmark exposed. Make it easy for me to add
  entries without touching code.
- Default rate: generate the same sentence at -10%, -5%, 0%, +5%, +10% and let
  me pick. Do not hardcode a guess.

=== CACHING ===
- Cache key: hash of (normalized_text + provider + voice + prosody settings).
- Store the final post-processed audio, not the raw response.
- Disk or Redis depending on what this project already uses — check first.
- TTL and a max size with LRU eviction. Log the hit rate.

=== OBSERVABILITY ===
- Structured logs: provider used, cache hit/miss, latency, char count, fallback
  triggered, error reason.
- A /tts_stats admin command showing these for the last 24h.

Write tests with a mocked provider covering: fallback chain, circuit breaker,
chunking boundaries, cache hit/miss, timeout, empty input, 10 000-char input.
```

---

## PROMPT 5 — Audio post-processing (professional tovush)

```
Add an audio post-processing stage using ffmpeg. This is what separates an
amateur-sounding bot from a professional one.

Create `tts/audio_post.py`.

Apply in this order:

1. TRIM SILENCE
   - Remove leading and trailing silence, but leave ~80ms of headroom so the
     start does not sound clipped.
   - ffmpeg silenceremove filter. Tune the threshold on real output.

2. LOUDNESS NORMALIZATION
   - EBU R128 loudnorm, two-pass for accuracy.
   - Target for speech: I=-16 LUFS, LRA=11, TP=-1.5 dBTP.
   - Two-pass means: first pass measures, second pass applies the measured
     values. A single-pass loudnorm is noticeably worse — do it properly.

3. LIGHT DYNAMICS
   - Gentle compression so quiet words are not lost on a phone speaker.
   - Do NOT over-compress — it makes TTS sound robotic and breathy.
   - A/B it: produce one version with and one without, so I can compare.

4. OPTIONAL SPEED
   - If I later ask for speed control, use ffmpeg atempo (pitch-preserving),
     never a sample-rate change.

5. ENCODE FOR TELEGRAM
   - Telegram voice messages: OGG container, OPUS codec, 48 kHz, MONO.
   - Bitrate 32-48 kbps is enough for speech and keeps files small.
   - Command shape: -c:a libopus -b:a 48k -ar 48000 -ac 1 -application voip

Requirements:
- Check ffmpeg is installed at startup and fail loudly with a clear message if
  not, including the install command for this OS.
- Never shell out with string concatenation of user input. Use argument lists.
- Clean up temp files in a finally block, including on exception.
- Measure the added latency of post-processing and log it. If it exceeds 500ms
  for a typical message, optimise.

Produce a before/after pair of the same sentence and put both in the benchmark
HTML page so I can hear the difference.
```

---

## PROMPT 6 — Telegram tomonini to'g'ri qilish

```
Fix the Telegram delivery layer for voice output.

1. CORRECT METHOD
   - Use sendVoice for spoken content, not sendAudio and not sendDocument.
     sendVoice renders the waveform bubble with inline playback and playback
     speed control, which is what users expect. Confirm the current code and
     change it if needed.
   - sendVoice requires OGG/OPUS. If the file is not that format, it will either
     fail or be shown as a file. Verify the actual format being sent.

2. USER FEEDBACK DURING GENERATION
   - Send the "recording voice" chat action immediately and keep it alive while
     generating, so the user sees activity instead of silence.
   - If generation exceeds 3 seconds, send a short status message and edit it
     away when the audio arrives.

3. LONG TEXT POLICY
   - Define a max spoken length. For anything longer, either split into multiple
     voice messages in order, or speak a summary and offer the full version.
     Ask me which I want before implementing.
   - Each voice message must be independently listenable — do not cut mid-sentence.

4. CONTROLS
   - Add an inline keyboard under the voice message: replay, change voice
     (male/female if available), change speed.
   - Store the user's voice and speed preference per user, persistently.
   - Add a /voice command to set the default.

5. ERROR HANDLING
   - If every provider in the chain fails, send a clear Uzbek message explaining
     the problem and offering to retry — never a silent failure, never a raw
     traceback, never an English error string shown to an Uzbek user.

6. RATE LIMITING
   - Per-user limit on TTS requests to prevent one user exhausting the quota.
   - Queue rather than reject when possible, and tell the user their position.

Verify all of this by actually running the bot and sending real messages.
Screenshot the result in the Telegram client and show me.
```

---

## PROMPT 7 — Sifat darvozasi (tugaganini tasdiqlash)

```
Final quality gate. The TTS upgrade is NOT complete until every item below is
demonstrated with evidence. Go through them one by one and show proof.

FUNCTIONAL
[ ] All three baseline sentences from PROMPT 1 regenerated and saved as "after"
    files, next to the "before" files, in the comparison page.
[ ] Every normalizer unit test passes — paste the summary line.
[ ] 5000-character input works end to end without truncation or seam artifacts.
[ ] Primary provider killed (simulate failure) → fallback serves the user
    transparently. Show the log.
[ ] Cache hit returns in under 100ms. Show the measurement.

LINGUISTIC — generate audio for each and confirm by listening
[ ] "2024-yilda" is read as a year, not as digits.
[ ] "6,5%" is read as "olti butun oʻndan besh foiz".
[ ] "AQSh" and "BMT" are read with Uzbek letter names.
[ ] "Oʻzbekiston" is pronounced correctly regardless of which apostrophe
    character was typed.
[ ] "Google" is not pronounced letter by letter.
[ ] A Cyrillic sentence is read correctly.
[ ] Questions have rising intonation; statements fall.
[ ] No audible click or gap at chunk seams in a long text.

AUDIO
[ ] Measured loudness is within 1 LU of -16 LUFS. Show the ffmpeg measurement.
[ ] True peak does not exceed -1.5 dBTP.
[ ] No clipping. No leading/trailing dead air over 150ms.
[ ] File is genuinely OGG/OPUS mono 48kHz — show ffprobe output.

TELEGRAM
[ ] Renders as a voice bubble with waveform, not as a file attachment.
[ ] Recording action visible during generation.
[ ] Inline controls work. Screenshot each.
[ ] Voice preference persists across bot restart.

CODE QUALITY
[ ] No TTS library is imported anywhere except the adapters.
[ ] No secrets in the diff — show the grep.
[ ] No new TODO/FIXME — show the grep.
[ ] Typecheck, lint, and full test suite pass — paste all three outputs.

Any unticked box means BLOCKED, not done. Report honestly.
```

---

## PROMPT 8 — Doimiy yaxshilash tizimi

```
Set up a feedback loop so quality keeps improving after launch.

1. MISPRONUNCIATION REPORTING
   - Add a small "noto'g'ri o'qidi" button under each voice message.
   - When pressed, log the exact normalized text, the chunk, the provider and
     the voice into a review queue file.
   - Add an admin command to list the queue so I can review and add entries to
     the pronunciation lexicon.

2. AUTOMATIC DETECTION
   - Log every token the normalizer could not classify (unknown abbreviation,
     unknown foreign word, unusual character). Surface the top 20 weekly.

3. REGRESSION CORPUS
   - Every fixed mispronunciation becomes a permanent unit test in the
     normalizer test suite. The corpus only grows.

4. DOCUMENTATION
   - Write docs/TTS.md: architecture diagram, how to add a lexicon entry, how
     to add a provider, how to run the benchmark, how to tune prosody, known
     limitations.
   - Write it so that someone who has never seen this code can add a
     pronunciation fix in under 5 minutes.
```

---

## Kutilayotgan natija — bosqichma-bosqich

| Bosqich | Sifatga ta'siri | Vaqt |
|---|---|---|
| PROMPT 2 — normalizatsiya | **Eng katta.** Raqam, sana, qisqartma muammosi yo'qoladi | 1-2 kun |
| PROMPT 3 + 4 — provayder | Ovoz tabiiyligi, SSML nazorati | 1 kun |
| PROMPT 5 — audio post | Professional balandlik va tozalik | Yarim kun |
| PROMPT 6 — Telegram | Foydalanuvchi tajribasi | Yarim kun |

---

## Muhim maslahatlar

**Tartibni buzmang.** Provayderni birinchi almashtirsangiz, normalizatsiya yo'qligi sababli natija baribir yomon chiqadi va siz "bu provayder ham yomon ekan" degan noto'g'ri xulosaga kelasiz.

**Azure Speech ni alohida tekshiring.** U `edge-tts` bilan **bir xil ovozlarni** beradi, lekin SSML, `<phoneme>` va custom lexicon bilan. Ya'ni siz ovozni tuzata olasiz. Ko'p hollarda bu eng arzon va eng tez yechim bo'ladi — ovozni almashtirmasdan sifatni ko'tarasiz.

**Erkak ovozini ham sinang.** `edge-tts --list-voices | grep -i uz` da `uz-UZ-SardorNeural` bo'lishi mumkin. Ba'zan bitta ovoz boshqasidan sezilarli yaxshiroq o'qiydi.

**O'zbekiston provayderlarini tashlab ketmang.** Mohir.ai kabi mahalliy xizmatlar O'zbek tiliga maxsus o'qitilgan bo'lishi mumkin — global provayderlardan yaxshiroq chiqishi ehtimoli bor. Benchmark ro'yxatida bor, tekshirib ko'ring.

**Sifatni faqat siz baholaysiz.** Agent audio eshita olmaydi, men ham. Shuning uchun benchmark HTML sahifasi muhim — har bir jumlani provayderlar bo'ylab yonma-yon eshitib, o'zingiz tanlang.
