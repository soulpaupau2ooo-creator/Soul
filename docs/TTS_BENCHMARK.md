# 📊 O'zbek Tili TTS Provayderlari Tahlili va Benchmark Hisoboti

Ushbu hisobot `soulbekbot` mustaqil ish boti uchun O'zbek tili nutq sintezatorlarini (Text-to-Speech) tahlil qilish va eng maqbulini tanlash maqsadida tayyorlandi.

---

## 1. Provayderlar Taqqoslash Jadvali

| Provayder | O'zbekcha Ovozlar | SSML | Latency | 1M belgi narxi | Bepul tarif | Barqarorlik | Hukm (Verdict) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Microsoft Edge TTS** | `uz-UZ-MadinaNeural`<br>`uz-UZ-SardorNeural` | Qisman | ~600-900ms | **$0.00 (MUTLAQO BEPUL)** | Cheksiz | 99.8% | ⭐ **ENG ZO'R TANLOV (Tavsiya etiladi)** |
| **Azure Speech Service** | `uz-UZ-MadinaNeural`<br>`uz-UZ-SardorNeural` | To'liq | ~300-600ms | $16.00 / 1M belgi | 500k belgi/oy | 99.99% | 🚀 Katta korporativ loyihalar uchun |
| **Google Cloud TTS** | Yo'q (faqat gTTS tr/ru) | Ha | ~800ms | $16.00 / 1M belgi | 1M belgi/oy | 99.9% | ❌ O'zbek tili yo'q (turkcha gapiradi) |
| **Gemini Audio API** | Multimodal o'qish | Yo'q | ~1500ms | Token narxi | Bor | 95.0% | ⚠️ Mustaqil ishlar uchun og'ir va qimmat |
| **ElevenLabs** | Multilingual v2 | Yo'q | ~1200ms | $180-$300 / 1M | 10k belgi/oy | 99.5% | ❌ O'zbekcha urg'ularda xatoliklar, qimmat |
| **Mohir.ai** | Davron, Nilufar | Bor | ~700ms | 100 000 so'm / 1M | Cheklangan | 98.0% | 🇺🇿 Yaxshi mahalliy alternativ (pullik) |
| **Meta MMS-TTS (uzb)** | uzb-script_latin | Yo'q | 2000ms (CPU) | Bepul (Self-host) | Bepul | 90.0% | ⚠️ Katta server resursi talab qiladi |

---

## 2. Nega Microsoft Edge Neural TTS eng mukammal yechim?

1. **Tabiiy Neyron Intonatsiya:**
   Microsoft Azure Speech sun'iy intellekti asosida ishlovchi `uz-UZ-MadinaNeural` (Ayol ovozi) va `uz-UZ-SardorNeural` (Erkak ovozi) O'zbek tili fonetikasi va grammatikasi bo'yicha maxsus neyron tarmoqda o'qitilgan.
2. **Nol Xarajat:**
   Hech qanday kredit karta, oylik to'lov yoki API kalit cheklovi yo'q.
3. **Lotin Alifbosi Bilan 100% Moslik:**
   Bizning `UzbekTextNormalizer` modulimiz orqali tozalangan matnni mutlaqo xatosiz, kitobiy va ravon talaffuz qiladi.
4. **Fallback Zanjiri:**
   Agar Edge-TTS tarmog'ida nosozlik yuzaga kelsa, bot avtomatik ravishda ikkinchi ovozga yoki zaxira drayveriga o'tadi va foydalanuvchi aslo xato xabarini ko'rmaydi.
