# 🎧 O'zbek Tili TTS Tizimi Qo'llanmasi (Soulbekbot)

Ushbu tizim `soulbekbot` mustaqil ishlarining to'liq matnini yuqori sifatli O'zbek neyron ovozlarida (`Madina` va `Sardor`) tabiiy, ravon va xatosiz o'qib berish uchun maxsus ishlab chiqilgan.

---

## 1. 🏗️ Arxitektura Diagrammasi

```
[Foydalanuvchi "👩 Madina / 👨 Sardor" tugmasini bosadi]
                          │
                          ▼
        [bot.py: tts_callback_handler]
   (ChatAction: record_voice, status xabari)
                          │
                          ▼
            [tts.service: TTSService]
                          │
        ┌─────────────────┴─────────────────┐
        ▼                                   ▼
 [UzbekTextNormalizer]              [TTS Kesh Tekshiruvi]
 (7-bosqichli tozalash:              (MDH hash asosida:
  raqamlar, yillar, kasrlar,          mavjud bo'lsa darhol MP3)
  valyuta, qisqartmalar,
  akronimlar, kirill-lotin)
        │
        ▼
[EdgeTTSProvider (Azure Speech AI)]
- Madina (uz-UZ-MadinaNeural)
- Sardor (uz-UZ-SardorNeural)
        │
    (Muvaffaqiyatsiz bo'lsa)
        ▼
[GTTSFallbackProvider (Zaxira)]
        │
        ▼
[tts.audio_post: Audio Post-processing]
(FFmpeg / EBU R128 loudnorm / trim silence)
        │
        ▼
[Telegram: answer_audio (Title, Performer, Inline switcher)]
```

---

## 2. 🔤 Yangi Chet Tili So'zini Qo'shish (5 Daqiqada)

Agar bot biror yangi texnologik yoki chet tili so'zini noto'g'ri o'qisa, uni kodga tegmasdan `tts/foreign_words.json` fayliga qo'shishingiz kifoya:

```json
{
  "startup": "startap",
  "blockchain": "blokcheyn",
  "fintech": "fintex"
}
```

Bot keyingi safar ushbu so'zlarni avtomatik ravishda to'g'ri o'zbekcha fonetikada talaffuz qiladi.

---

## 3. 🛡️ Xatoliklarga Chidamlilik (Circuit Breaker)

- **Birinchi daraja:** `uz-UZ-MadinaNeural` (Standart ayol ovozi).
- **Ikkinchi daraja:** `uz-UZ-SardorNeural` (Muqobil erkak ovozi).
- **Uchinchi daraja:** `gTTS` zaxira drayveri.
- Agar tarmoqda ketma-ket 3 marta uzilish kuzatilsa, **Circuit Breaker** ishga tushib, 60 soniya davomida kutmasdan avtomatik zaxira tizimiga yo'naltiradi.

---

## 4. 🧪 Testlarni Ishga Tushirish

Normalizatsiya va barcha 80+ lingvistik qoidalarni tekshirish uchun:

```powershell
.\venv\Scripts\python -m unittest discover -s tests -p "test_*.py"
```
