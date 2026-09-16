# 🎧 soulbekbot TTS Pipeline Auditi (Texnik Tekshiruv)

## 1. Kirish Nuqtasi (Entry Point)
- **Fayl va qator:** `bot.py:608-632` (`tts_callback_handler`), inline tugma: `bot.py:169` (`InlineKeyboardButton(text="🎧 Ovozli tinglash (Audio)", callback_data=f"tts_play_{user_id}")`).
- **Uzatiladigan matn:** `last_generated_essays.get(uid)`. Bu to'g'ridan-to'g'ri Gemini AI tomonidan yaratilgan xom matn (Markdown belgilari, `#` sarlavhalar, `**` qalin shrift, jadvallar va statistik raqamlar bilan to'la).
- **Hozirgi holat:** Matn deyarli tozalanmagan, faqat 800 ta belgiga kesib olinadi (`text[:800]`).

## 2. Matnni Tayyorlash (Text Preparation)
- **Transformatsiyalar:** `multimodal_handler.py:195`:
  `clean_text = text[:800].replace("*", "").replace("_", "").replace("#", "")`
- **Mavjud bo'lmagan (Absent) muhim qismlar:**
  - ❌ Apostroflar (Oʻ / Gʻ va tutuq belgisi) normalizatsiyasi: **YO'Q**.
  - ❌ Raqamlar (sonlar, kardinal va tartib sonlar): **YO'Q** (dvigatel raqamlarni noto'g'ri talaffuz qiladi yoki inglizcha/turkcha o'qiydi).
  - ❌ Yillar va sanalar ("2024-yilda", "12.05.2024"): **YO'Q**.
  - ❌ Kasr va foizlar ("6,5%", "112,5"): **YO'Q**.
  - ❌ Valyutalar ("1 500 000 so'm", "$100"): **YO'Q**.
  - ❌ Qisqartmalar (km, kg, mlrd, mln, va h.k., sh., ko'ch.): **YO'Q**.
  - ❌ O'zbekcha akronimlar (YaIM, BMT, AQSh): **YO'Q** (inglizcha yoki xato o'qiladi).
  - ❌ Chet tili so'zlari (Google, YouTube, Telegram): **YO'Q**.
  - ❌ Kirill-Lotin konvertatsiyasi: **YO'Q**.
  - ❌ Jadvallar va URL manzillarni tozalash: **YO'Q**.

## 3. TTS Chaqiruvi (TTS Call)
- **Kutubxona:** `gTTS` (Google Translate TTS).
- **Ovoz / Til kodi:** `tts_lang = 'tr'` (TURKCHA!). Sababi: gTTS da o'zbek tili (`uz`) yo'q. Natijada o'zbekcha matn turk tili fonetikasi bilan o'qiladi va mutlaqo beo'xshov, buzilgan talaffuz yuzaga keladi.
- **Chunking va hajm chegarasi:** Chunking yo'q. `[:800]` bilan kesib tashlanadi (butun mustaqil ishning faqat 20-25% qismi o'qiladi).
- **Tarmoq xatolari va Fallback:** Faqat umumiy `try-except`, hech qanday zaxira ovoz yoki qayta urinish (retry) yo'q.

## 4. Audio Boshqaruvi (Audio Handling)
- **Format:** MP3 (gTTS standart oqimi).
- **Loudness / EBU R128:** Qo'llanilmagan.
- **Silence Trimming:** Yo'q.
- **Telegram usuli:** `callback.message.answer_audio` (`sendAudio`) orqali musiqiy fayl shaklida yuboriladi. To'lqinli (waveform) ovozli xabar (`sendVoice`) emas.

## 5. Kesh va Unumdorlik (Performance)
- **Kesh:** Hech qanday audio keshlash yo'q. Bir xil matn har safar noldan yuklanadi.

---

## 💥 Eng Katta 5 Ta Kamchilik (Prioritet Tartibida)

1. **Provayder tilining turkcha (`tr`) ekanligi (Buzilish darajasi: 95%):**
   O'zbek tili tovushlari (o', g', q, h, x) turkcha harflar kabi talaffuz qilinadi, so'zlar umuman boshqacha eshitiladi.
2. **Matn normalizatsiyasining yo'qligi (Buzilish darajasi: 85%):**
   "2024-yilda", "6,5%", "YaIM", "1 500 000 so'm" kabi akademik iqtisodiy tushunchalar o'qilmaydi yoki buziladi.
3. **800 belgilik qattiq cheklov (Buzilish darajasi: 80%):**
   Talabaning mustaqil ishi odatda 2500-4000 belgidan iborat bo'ladi. Hozirgi tizim faqat kirish qismining yarmini o'qib to'xtab qoladi.
4. **Markdown va jadval axlatlari (Buzilish darajasi: 60%):**
   Tizim jadvallardagi `|` (chiziq), `---`, havolalarni nutq ichida tartibsiz shovqin qilib yuboradi.
5. **sendAudio vs sendVoice (Buzilish darajasi: 40%):**
   Foydalanuvchilar Telegramda tezlikni o'zgartirish (1.5x, 2x) va to'lqin shaklini ko'rishni xohlashadi, fayl ko'rinishida yuklab olish noqulay.
