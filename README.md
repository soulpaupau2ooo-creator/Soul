# 🎓 Soulbekbot - O'zbekiston OTMlari Iqtisodiyot Talabalari Uchun AI Yordamchi

Ushbu Telegram bot O'zbekistondagi barcha nufuzli oliy ta'lim muassasalari (TDIU, TMI, NamDU, NamDTU va boshqalar) talabalari uchun iqtisodiyot fanlaridan mukammal va akademik talablarga javob beradigan mustaqil ishlar (referat/insho) tayyorlab beruvchi aqlli sun'iy intellekt tizimidir.

## 🚀 Texnologiyalar va Arxitektura (Father Mode v6.0)
- **Asosiy freymvork:** Python 3.12 + `aiogram 3.x`
- **Sun'iy Intellekt:** Google Gemini API (`gemini-flash-latest`)
- **Yuklamani taqsimlash (Load Balancing):** Ko'p bosqichli API Key Rotation & avtomatik zaxira serverlar tizimi
- **Ma'lumotlar bazasi:** MongoDB Atlas (Cloud) + Mahalliy xavfsiz JSON zaxira
- **24/7 Cloud Hosting:** Render.com Web Service
- **Keep-Alive Uptime:** `aiohttp.web` server (`/health` va `/` yo'nalishlari) + cron-job.org ping monitoring

## 📚 Qamrab olingan fanlar
- **Nazariy iqtisodiyot:** Makroiqtisodiyot, Mikroiqtisodiyot, Iqtisodiy ta'limotlar
- **Moliya va Hisob:** Moliya, Buxgalteriya hisobi, Soliq va soliqqa tortish
- **Tadbirkorlik va Boshqaruv:** Marketing, Menejment, Kichik biznes va tadbirkorlik
- **Mintaqaviy va Tarmoq (NamDU):** Mintaqaviy iqtisodiyot, Qishloq xo'jaligi iqtisodiyoti, Turizm iqtisodiyoti
- **Sanoat va Muhandislik (NamDTU):** Sanoat iqtisodiyoti, Muhandislik iqtisodiyoti, Logistika, Innovatsion iqtisodiyot
- **Xalqaro:** Xalqaro iqtisodiy munosabatlar

## 🛠️ O'rnatish va Ishga tushirish
```bash
git clone https://github.com/soulpaupau2ooo-creator/Soul.git
cd Soul
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python bot.py
```

## 🌐 Server Health Check
Keep-alive holatini tekshirish:
```
GET /health
```
Qaytariladigan javob:
```json
{
  "status": "ok",
  "service": "Soulbekbot 24/7 Hosting",
  "database": "MongoDB Atlas"
}
```
