# Session State: Soulbekbot (Mustaqil ish bot) v6.4 Production

**Sana:** 2026-09-16
**Loyiha papkasi:** `C:\Users\Azizbek\.gemini\antigravity\scratch\soulbekbot`
**Bot:** `@Soulbekbot` (ID: 6998957173)
**Ko'rinadigan Ismi:** `Mustaqil ish bot`
**Token:** `6998957173:AAEeK8KhYGqF9gzDxFuWDL12Zx9nFryxf2c`
**GitHub ombori:** `https://github.com/soulpaupau2ooo-creator/Soul` (Branch: `main`)
**Render xizmati:** `https://soul-0rvl.onrender.com`
**Zaxira kanali:** `@soul_backups`

---

## 🎯 Yakuniy holat (v6.4 OTM Davlat Standartidagi Word .docx Generatsiyasi):
1. **Rasmiy OTM Davlat Standartidagi Word (.docx) Hujjati (`docgen/mustaqil_ish.py`)**:
   - A4 qog'oz, chap 3.0 sm, o'ng 1.5 sm, yuqori 2.0 sm, pastki 2.0 sm.
   - Times New Roman 14 pt, 1.5 qator oralig'i, 1.25 sm abzas chekinishi, ikki tomonlama tekislash (Justified).
   - Rasmiy Titul varaq (Vazirlik, OTM, fakultet, kafedra, fan, mavzu, talaba va o'qituvchi bloki, shahar va yil).
   - Word da avtomatik yangilanuvchi rasmiy Mundarija (TOC field code).
   - Titulda yashirilgan pastki markaziy sahifa raqamlash (`PAGE` field).
2. **Telegram Orqali Haqiqiy Hujjat Yuborish (`sendDocument`)**:
   - `📄 Word (.docx) yuklab olish` tugmasi orqali toza binar `.docx` yuboriladi.
   - Kompyuterda (Word, LibreOffice) va telefonda (Word, WPS Office) 1 bosish bilan ochiladi.
3. **Akademik Profil va Xotira Boshqaruvi (`/malumotlarim`)**:
   - Talaba o'z universiteti, fakulteti, guruhi, F.I.Sh va o'qituvchisini kiritib qo'yishi mumkin.
   - Bot har bir mustaqil ishning titul varag'iga ushbu ma'lumotlarni avtomatik joylaydi.
4. **Microsoft Azure Speech AI Neyron O'zbekcha Ovozlar (`edge-tts`)**:
   - `uz-UZ-MadinaNeural` (Ayol ovozi) va `uz-UZ-SardorNeural` (Erkak ovozi).
5. **7-Bosqichli O'zbek Matn Normalizatsiya Dvigateli (`tts/uzbek_normalizer.py`)**:
   - Raqamlar, yillar, kasrlar, valyuta, akronimlar, kirill-lotin.
6. **Keng Qamrovli Unit Testlar To'plami (64 ta test metodi)**:
   - Ham normalizatsiya, ham Word .docx o'lchamlari va strukturalari 100% yashil (OK).
7. **30 ta OTM Fani, 300 ta Mavzular Kutubxonasi, Slash Buyruqlar va Rasmiy Statistika to'liq faol.**
