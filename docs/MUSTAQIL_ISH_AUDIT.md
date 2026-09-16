# 📑 Soulbekbot Mustaqil Ish Generatsiyasi Auditi

## 1. Kirish Nuqtasi (Entry Points)
- **Mavzular bo'yicha generatsiya:** `bot.py` da mavzu tugmasi bosilganda (`F.data.startswith("gen_subj_")` yoki `topic_select_`).
- **Erkin mavzu yozilganda:** `EssayStates.waiting_for_custom_topic` FSM holati orqali.
- **Rasmdan mavzu olinganda:** `extract_topic_from_photo` orqali.
- **Hozirgi uzatish usuli:** Mustaqil ish matni sun'iy intellekt (Gemini) orqali olinadi va Telegram chatiga oddiy matn (`message.answer(part)`) sifatida yuboriladi.

## 2. Foydalanuvchidan Yig'iladigan Ma'lumotlar
- **Hozir yig'ilayotgan:** Faqat fan nomi va mustaqil ish mavzusi.
- **Yetishmayotgan (Titul varag'i uchun shart bo'lgan):**
  - Universitet nomi (masalan: Toshkent davlat iqtisodiyot universiteti)
  - Fakultet nomi
  - Kafedra nomi
  - Talabaning F.I.Sh. va guruhi
  - O'qituvchi / Ilmiy rahbar F.I.Sh. (ixtiyoriy)
  - Shahar va yil (standart Toshkent, 2026)

## 3. Mavjud Kutubxonalar
- Hozirga qadar `python-docx` yoki boshqa Word generator kutubxonalari loyihaga ulanmagan edi.
- Loyihaga `python-docx>=1.1.0` o'rnatildi va `requirements.txt` ga qo'shildi.

## 4. Standart Word Hujjatiga Aylantirish Uchun Nimalar Kerak?
1. **`docgen/mustaqil_ish.py`** — O'zbekiston OTM standartlari bo'yicha formatlangan (A4, 3.0/1.5/2.0/2.0 sm chegaralar, Times New Roman 14pt, 1.5 interval, 1.25 sm abzas) rasmiy hujjat generatori.
2. **Haqiqiy Titul Varag'i** — markazlashgan bosh qism, fan va mavzu, o'ng tomonda talaba va o'qituvchi bloki, pastda shahar va yil.
3. **Avtomatik Mundarija (TOC field code)** — Word da yangilanadigan rasmiy mundarija maydoni.
4. **Strukturalangan Bo'limlar** — Kirish, Heading 1/2 asosiy boblar, Xulosa, Foydalanilgan adabiyotlar.
5. **Telegram Delivery** — `sendDocument` orqali toza binar `.docx` fayl yuborish, to'g'ri MIME type, chiroyli fayl nomi.
6. **Foydalanuvchi profili xotirasi** — universitet, fakultet, guruh, ismni eslab qolish (`/malumotlarim`).
