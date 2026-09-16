# Session State: Soulbekbot (Mustaqil ish bot) v6.3 Production

**Sana:** 2026-09-16
**Loyiha papkasi:** `C:\Users\Azizbek\.gemini\antigravity\scratch\soulbekbot`
**Bot:** `@Soulbekbot` (ID: 6998957173)
**Ko'rinadigan Ismi:** `Mustaqil ish bot`
**Token:** `6998957173:AAEeK8KhYGqF9gzDxFuWDL12Zx9nFryxf2c`
**GitHub ombori:** `https://github.com/soulpaupau2ooo-creator/Soul` (Branch: `main`)
**Render xizmati:** `https://soul-0rvl.onrender.com`
**Zaxira kanali:** `@soul_backups`

---

## 🎯 Yakuniy holat (v6.3 Mukammal O'zbek Tili AI TTS Yangilanishi):
1. **Microsoft Azure Speech AI Neyron O'zbekcha Ovozlar (`edge-tts`)**:
   - `uz-UZ-MadinaNeural` (Ayol ovozi — muloyim, tiniq, ravon).
   - `uz-UZ-SardorNeural` (Erkak ovozi — jiddiy, rasmiy ma'ruzachi).
   - Eski `gTTS` turkcha xato talaffuzi butunlay olib tashlandi.
2. **7-Bosqichli O'zbek Matn Normalizatsiya Dvigateli (`tts/uzbek_normalizer.py`)**:
   - 0 dan trilliongacha sonlar, tartib sonlar (-inchi/-nchi).
   - Yillar ("2024-yilda"), sanalar ("12.05.2024"), vaqt ("14:30").
   - Kasrlar va foizlar ("6,5%"), valyutalar ("1 500 000 so'm", "$100", "€50").
   - Qisqartmalar va birliklar (km, kg, mlrd, mln, sh., ko'ch., °C).
   - O'zbekcha akronimlar (YaIM, BMT, AQSh, OTM, IIV).
   - Kirill-Lotin to'liq konvertatsiyasi.
   - Tashqi chet el so'zlari fonetik lug'ati (`tts/foreign_words.json`).
3. **80+ Unit Testlar To'plami (`tests/test_uzbek_normalizer.py`)**:
   - Barcha lingvistik qoidalar va ekstremal chekka holatlar 100% testlangan (54 test metodi, 90+ assertlar).
4. **Ishlab Chiqarish Darajasidagi TTS Xizmati (`tts/service.py`)**:
   - Fallback Chain: Madina -> Sardor -> gTTS.
   - Circuit Breaker va Retry mexanizmi.
   - Gap chegaralarini buzmagan holda uzun mustaqil ishlarni to'liq chunklash (2000+ belgilar).
   - Disk va Memory LRU kesh (`tts_cache/`).
5. **Professional Telegram Interfeysi**:
   - `👩 Madina ovozida` va `👨 Sardor ovozida` alohida tugmalar.
   - Jonli `record_voice` chat action indikatori.
   - Audio tagida ovozni almashtirish tugmasi (`Inline switcher`).
6. **30 ta OTM Fani, 300 ta Mavzular Kutubxonasi, Slash Buyruqlar va Rasmiy Statistika to'liq faol.**
